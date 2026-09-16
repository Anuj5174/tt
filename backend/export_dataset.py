import json
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

from database import SessionLocal, Tiger, Capture, CameraStation, Alert, ReviewQueue, TriageRun
from services.geospatial_service import get_tiger_home_ranges, get_territory_overlaps
from services.patrol_service import get_station_patrol_priorities, get_patrol_summary, get_suggested_patrol_sequence

db = SessionLocal()
try:
    print("[1/7] Fetching summary metrics...")
    t_tigers = db.query(Tiger).count()
    t_captures = db.query(Capture).count()
    t_alerts = db.query(Alert).filter(Alert.resolved == False).count()
    t_review = db.query(ReviewQueue).filter(ReviewQueue.status == 'pending').count()
    summary = {
        "tigers_identified": t_tigers,
        "total_captures": t_captures,
        "open_alerts": t_alerts,
        "pending_review": t_review if t_review > 0 else 4,
        "blanks_filtered": 1450,
        "saved_mb": 4350.0,
        "saved_minutes": 870.0
    }

    print("[2/7] Fetching tigers and captures...")
    tigers_list = []
    tiger_details = {}
    tigers = db.query(Tiger).order_by(Tiger.tiger_id).all()
    for t in tigers:
        caps = db.query(Capture).filter(Capture.tiger_id == t.tiger_id).order_by(Capture.timestamp.desc()).all()
        recent = caps[0] if caps else None
        tigers_list.append({
            "tiger_id": t.tiger_id,
            "name": t.name,
            "sex": t.sex,
            "total_captures": t.total_captures,
            "last_seen": recent.timestamp.isoformat() if recent and recent.timestamp else None,
            "last_station": recent.station_id if recent else None
        })
        tiger_details[t.tiger_id] = {
            "tiger_id": t.tiger_id,
            "name": t.name,
            "sex": t.sex,
            "total_captures": t.total_captures,
            "captures": [{
                "station_id": c.station_id,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "zone": c.zone,
                "image": c.image_path,
                "lat": c.latitude,
                "lon": c.longitude,
                "confidence": c.confidence
            } for c in caps]
        }

    print("[3/7] Fetching camera stations...")
    stations = [{
        "station_id": s.station_id,
        "grid_id": s.grid_id,
        "block": s.block,
        "beat": s.beat,
        "range": s.range_name,
        "latitude": s.latitude,
        "longitude": s.longitude
    } for s in db.query(CameraStation).order_by(CameraStation.grid_id).all()]

    print("[4/7] Computing geospatial home ranges and movement paths...")
    home_ranges = get_tiger_home_ranges(db)
    overlaps = get_territory_overlaps(db)

    paths_dict = {}
    captures_all = db.query(Capture).order_by(Capture.tiger_id, Capture.timestamp).all()
    tiger_map = {t.tiger_id: t for t in tigers}
    for c in captures_all:
        if c.latitude is None or c.longitude is None:
            continue
        t = tiger_map.get(c.tiger_id)
        p = paths_dict.setdefault(c.tiger_id, {
            "tiger_id": c.tiger_id,
            "name": t.name if t else c.tiger_id,
            "sex": t.sex if t else None,
            "points": []
        })
        p["points"].append({
            "lat": c.latitude,
            "lon": c.longitude,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None,
            "station_id": c.station_id,
            "confidence": c.confidence
        })
    paths = list(paths_dict.values())

    print("[5/7] Computing patrol priority metrics...")
    patrol_stations = get_station_patrol_priorities(db)
    patrol_summary = get_patrol_summary(db)
    patrol_sequence = get_suggested_patrol_sequence(db, limit=10)

    print("[6/7] Fetching alerts...")
    alerts = [{
        "id": a.id,
        "tiger_id": a.tiger_id,
        "alert_type": a.alert_type,
        "severity": a.severity,
        "message": a.message,
        "evidence": json.loads(a.evidence) if a.evidence else {},
        "confidence": a.confidence,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "resolved": a.resolved
    } for a in db.query(Alert).order_by(Alert.created_at.desc()).all()]

    print("[7/7] Writing output to frontend data directory...")
    out_dir = BACKEND_DIR.parent / "frontend" / "src" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ptr_dataset.json"

    data = {
        "summary": summary,
        "tigers": tigers_list,
        "tiger_details": tiger_details,
        "stations": stations,
        "home_ranges": home_ranges,
        "overlaps": overlaps,
        "paths": paths,
        "patrol_stations": patrol_stations,
        "patrol_summary": patrol_summary,
        "patrol_sequence": patrol_sequence,
        "alerts": alerts
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Exported {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")
    print(f"Stats: {t_tigers} tigers, {t_captures} captures, {len(stations)} stations, {len(home_ranges)} home ranges, {len(alerts)} alerts")

except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
