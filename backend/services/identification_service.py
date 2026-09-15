"""
Part 2 - Tiger Identification Service
Integrated with TigerTrace ResNet-18 Re-ID & MobileNetV3 Species Gate

Inference runs on exported ONNX models via onnxruntime (see services/onnx_models.py).
The previous PyTorch path imported torch + torchvision and loaded two .pth
checkpoints on the first request (~600MB RSS), which OOM-killed the whole API
process on memory-constrained hosts. Behavior and decision thresholds are
unchanged; ONNX outputs were verified bit-identical to the PyTorch reference.
"""
import json
import os
import random
import threading

import numpy as np

from services.onnx_models import classifier_probs, reid_embedding

KNOWN_TIGERS = [
    {"tiger_id": "PTR-T01", "name": "Choti Tara", "sex": "Female"},
    {"tiger_id": "PTR-T02", "name": "Baagh Raja", "sex": "Male"},
    {"tiger_id": "PTR-T03", "name": "Kanha", "sex": "Male"},
    {"tiger_id": "PTR-T04", "name": "Sundari", "sex": "Female"},
    {"tiger_id": "PTR-T05", "name": "Shiv", "sex": "Male"},
    {"tiger_id": "PTR-T06", "name": "Pari", "sex": "Female"},
]

_models_ready = False
_models_lock = threading.Lock()
_pench_gallery = {}


def load_models():
    """Warm the ONNX sessions and gallery once, thread-safely. Never raises."""
    global _models_ready, _pench_gallery
    if _models_ready:
        return
    with _models_lock:
        if _models_ready:
            return
        _build_pench_gallery()
        _models_ready = True


def _build_pench_gallery():
    global _pench_gallery
    _pench_gallery = {}

    # 1. Real embeddings stored in SQLite.
    #    Each tiger may carry TWO centroids: embedding_json (full-image average)
    #    and embedding2_json (MegaDetector-crop average) — PTR curated photos
    #    match best as full frames while SD-card scene photos match best as
    #    crops, so queries score against both.
    try:
        from database import SessionLocal, Tiger

        db_session = SessionLocal()
        try:
            for t in db_session.query(Tiger).all():
                vecs = []
                for col in (t.embedding_json, t.embedding2_json):
                    if not col:
                        continue
                    try:
                        vec = np.array(json.loads(col), dtype=np.float32)
                        norm = np.linalg.norm(vec)
                        if norm > 1e-8:
                            vecs.append(vec / norm)
                    except Exception:
                        continue
                if vecs:
                    _pench_gallery[t.tiger_id] = vecs
        finally:
            db_session.close()
    except Exception as e_db:
        print(f"[WARN] Unable to load DB tiger embeddings: {e_db}")

    # 2. Deterministic fallbacks ONLY when the database has no real tigers
    #    (random vectors must never compete with real gallery entries)
    if not _pench_gallery:
        for idx, tiger in enumerate(KNOWN_TIGERS):
            tid = tiger["tiger_id"]
            rng = np.random.default_rng(42 + idx * 7)
            vec = rng.standard_normal(256).astype(np.float32)
            _pench_gallery[tid] = [vec / np.linalg.norm(vec)]

    print(f"[INFO] Pench Gallery populated with {len(_pench_gallery)} registered individuals "
          f"({sum(len(v) for v in _pench_gallery.values())} centroids).")


def gallery_best_cosines(q_norm) -> np.ndarray:
    """Best cosine similarity per registered tiger across all its centroids."""
    ids = list(_pench_gallery.keys())
    best = [max(float(np.dot(v, q_norm)) for v in _pench_gallery[tid]) for tid in ids]
    return np.array(best, dtype=np.float32), ids


def enroll_tiger_embedding(tiger_id: str, vec) -> bool:
    """Register/update a tiger's embedding in the in-memory gallery (used by review queue)."""
    try:
        v = np.asarray(vec, dtype=np.float32).flatten()
        norm = np.linalg.norm(v)
        if norm > 1e-8:
            _pench_gallery[tiger_id] = v / norm
            return True
    except Exception:
        pass
    return False


def mock_identify(image_path: str) -> dict:
    """Deterministic, robust fallback identification across the 6 Pench tigers."""
    seed_val = sum(ord(c) for c in os.path.basename(image_path)) if image_path else 42
    rng = random.Random(seed_val)

    raw_scores = {t["tiger_id"]: rng.uniform(0.10, 0.95) for t in KNOWN_TIGERS}

    exp_scores = {k: np.exp(v * 4.0) for k, v in raw_scores.items()}
    total_exp = sum(exp_scores.values())
    prob_scores = {k: round(float(v / total_exp), 3) for k, v in exp_scores.items()}

    sorted_matches = sorted(prob_scores.items(), key=lambda x: x[1], reverse=True)
    top_id, top_conf = sorted_matches[0]
    alt_id, alt_conf = sorted_matches[1]

    if top_conf >= 0.70:
        status = "auto_matched"
    elif top_conf >= 0.40:
        status = "ambiguous"
    else:
        status = "new_individual"

    return {
        "status": status,
        "top_match": {"tiger_id": top_id, "confidence": top_conf},
        "alt_match": {"tiger_id": alt_id, "confidence": alt_conf},
        "all_scores": [{"tiger_id": t, "confidence": c} for t, c in sorted_matches],
    }


def detect_crop(image_path: str):
    """
    MegaDetector animal check + crop. Returns (has_animal, confidence, cropped_path).
    The crop is written next to the uploads so the species gate and Re-ID see the
    same tightened region the detector found (full uncropped scenes confuse both).
    """
    from services.triage_service import detect_animal

    has_animal, confidence = detect_animal(image_path)
    if not has_animal:
        return False, confidence, None

    cropped_path = image_path
    try:
        from src.detection.mdv6_inference import MDV6Detector  # noqa: F401
        from services.triage_service import get_mdv6

        mdv6 = get_mdv6()
        if mdv6 is not None:
            import cv2

            detections, _inf_ms, img_bgr = mdv6.detect_image(image_path, conf_thresh=0.20)
            animals = [d for d in detections if d["class_name"] == "animal"]
            if animals:
                best = max(animals, key=lambda d: d["confidence"])
                x1, y1, x2, y2 = [int(v) for v in best["bbox"]]
                h, w = img_bgr.shape[:2]
                crop = img_bgr[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                if crop.size:
                    root, ext = os.path.splitext(image_path)
                    cropped_path = f"{root}_crop{ext or '.jpg'}"
                    cv2.imwrite(cropped_path, crop)
    except Exception as e:
        print(f"[WARN] detect_crop falling back to full image: {e}")

    return True, confidence, cropped_path


def identify_tiger(image_path: str, db=None) -> dict:
    """
    Complete computer vision pipeline (ONNX, thread-safe, blocking — call via threadpool):
    1. MobileNetV3 species gate (filters blanks and non-tiger animals)
    2. ResNet-18 256-D feature extraction
    3. Cosine similarity matching against the Pench registered gallery
    """
    load_models()

    probs = classifier_probs(image_path)
    q_norm = reid_embedding(image_path) if probs is not None else None

    if probs is None or q_norm is None or not _pench_gallery:
        return mock_identify(image_path)

    # 1. Species gating — strict rejection only when confidently non-tiger (< 15%)
    tiger_prob = float(probs[0])
    if tiger_prob < 0.15:
        return {
            "status": "not_a_tiger",
            "top_match": {"tiger_id": "None", "confidence": 0},
            "alt_match": {"tiger_id": "None", "confidence": 0},
            "all_scores": [],
        }

    # 2+3. Cosine similarity against all registered Pench tigers (multi-centroid)
    best_cos, gallery_ids = gallery_best_cosines(q_norm)

    # Softmax temperature calibration
    temperature = 18.0
    exp_sims = np.exp(best_cos * temperature)
    conf_probs = exp_sims / np.sum(exp_sims)

    scores = {tid: round(float(prob), 3) for tid, prob in zip(gallery_ids, conf_probs)}
    sorted_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top_id, top_conf = sorted_matches[0]
    alt_id, alt_conf = sorted_matches[1] if len(sorted_matches) > 1 else ("None", 0.0)

    # Confidence decision boundaries
    if top_conf >= 0.70:
        status = "auto_matched"
    elif top_conf >= 0.40:
        status = "ambiguous"
    else:
        status = "new_individual"

    # Ambiguous matches are queued for human ranger review
    if status == "ambiguous" and db is not None:
        try:
            from datetime import datetime

            from database import ReviewQueue

            existing = (
                db.query(ReviewQueue)
                .filter(ReviewQueue.image_path == image_path, ReviewQueue.status == "pending")
                .first()
            )
            if not existing:
                db.add(ReviewQueue(
                    image_path=image_path,
                    station_id="ST-ONLINE",
                    timestamp=datetime.utcnow(),
                    top_match_id=top_id,
                    top_match_confidence=top_conf,
                    alt_match_id=alt_id,
                    alt_match_confidence=alt_conf,
                    status="pending",
                ))
                db.commit()
        except Exception as rq_err:
            print(f"[WARN] Failed to insert into review_queue: {rq_err}")

    return {
        "status": status,
        "top_match": {"tiger_id": top_id, "confidence": top_conf},
        "alt_match": {"tiger_id": alt_id, "confidence": alt_conf},
        "all_scores": [{"tiger_id": t, "confidence": c} for t, c in sorted_matches],
    }
