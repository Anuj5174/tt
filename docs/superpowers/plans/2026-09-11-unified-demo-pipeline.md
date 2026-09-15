# Unified Demo Pipeline + Complete Language Switching Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One-page photo-to-answer demo flow (upload → confirm → automatic detect/classify/identify) with the SD-card import on the same page, video upload removed, and complete EN/हिंदी/मराठी switching across every page including chatbot backend responses.

**Architecture:** Add a `POST /api/pipeline/analyze` backend endpoint that runs the whole chain on one uploaded image and returns every stage's result in a single response. Rebuild `/identification` as the unified demo page with an auto-advancing pipeline stepper; move the SD-card import panel there as a shared component. Remove video upload everywhere. For language: extend `ChatRequest` with an optional `language` field and thread it through `generate_response` via a translation lookup; on the frontend, replace every hardcoded string with keys in `translations.ts` (already the i18n system) and pass the selected language with each chat request.

**Tech Stack:** FastAPI, ONNX Runtime (existing services), Next.js 16 App Router, existing homemade i18n (`src/lib/i18n/`), TypeScript.

**Spec:** This plan (user request, 2026-09-11 session).

## Global Constraints

- Never break the 6 existing pages' API contracts (`/api/summary`, `/api/tigers`, etc. stay unchanged).
- Existing ONNX models are used as-is; no new models.
- All new user-visible strings must exist in all three languages (en/hi/mr) in `translations.ts`.
- Chatbot intent/entity classification keeps working on English queries regardless of `language` param (responses localize, routing stays keyword-based).
- The dev servers run on ports 3000/8000 and must keep working after every task.

---

### Task 1: Backend — unified `POST /api/pipeline/analyze` endpoint

**Files:**
- Modify: `backend/main.py` (add endpoint after `/api/identify`)
- Modify: `backend/services/identification_service.py` (export a `detect_crop` helper using MDV6)

**Interfaces:**
- Produces: `analyze_image(file, station_id: str = "ST-01") -> dict` returning
  `{ filename, preview_url, stages: { blank_filter: {...}, species_gate: {...}, stripe_reid: {...}, classification: {...} }, final: { outcome, tiger_id, name, confidence, review_item_id } }`

- [x] **Step 1: Add `detect_crop` helper** in `identification_service.py`:

```python
def detect_crop(image_path: str) -> tuple[bool, float, str | None]:
    """MegaDetector blank check + animal crop. Returns (has_animal, confidence, cropped_path)."""
    from services.triage_service import detect_animal  # MDV6-backed
    # crop when detected, save to data/images/uploads/crops/, return path
```

- [x] **Step 2: Add `/api/pipeline/analyze` in `main.py`** — accepts `file` + `station_id`, runs:
  1. `detect_animal` (blank filter)
  2. If animal: MDV6 crop → `classifier_probs` (species gate)
  3. If tiger: `identify_tiger` on the crop (stripe Re-ID + category match)
  4. Build the staged response dict; store under `data/images/uploads/` and serve via `/images` static mount
  Runs in threadpool (blocking ONNX calls), same as `/api/identify`.

- [x] **Step 3: Test** — `curl -F file=@data/images/temp_test_tiger.jpg -F station_id=ST-14 http://localhost:8000/api/pipeline/analyze` returns all 4 stages with real confidences; blank image returns `blank_quarantined` outcome without later stages.

### Task 2: Frontend — unified demo page (`/identification` rebuild)

**Files:**
- Create: `frontend/src/components/SdCardImportPanel.tsx` (moved from triage page)
- Modify: `frontend/src/app/identification/page.tsx` (complete rebuild: tabs → single flow)
- Modify: `frontend/src/lib/api.ts` (add `analyzePipeline(file, stationId)`, remove `uploadVideo`)
- Delete from identification page: video tab + all video state/handlers/upload UI

**Interfaces:**
- Consumes: `POST /api/pipeline/analyze` response shape from Task 1.
- Produces: `<SdCardImportPanel />` component for reuse.

- [x] **Step 1: Extract SD panel** from `triage/page.tsx` into `components/SdCardImportPanel.tsx` (verbatim move, import path updates only).
- [x] **Step 2: Rebuild identification page** as: upload dropzone (single photo) → "Analyze" confirm button → auto-advancing 4-step stepper (Checking for animals → Is this a tiger? → Reading stripe pattern → Final answer) → result card (tiger name/photo/confidence or quarantine message) → "Analyze another photo" reset. Below: registered tigers strip + review queue (collapsed sections) + `<SdCardImportPanel />`.
- [x] **Step 3: TypeScript check** — `npx tsc --noEmit` passes.
- [x] **Step 4: Browser test** — upload tiger photo via UI, stepper advances, correct result shows; upload blank photo → quarantine outcome.

### Task 3: Video upload removal

**Files:**
- Modify: `frontend/src/lib/api.ts` (delete `uploadVideo`)
- Modify: `backend/main.py` (delete `/api/upload-video` endpoint)

- [x] **Step 1: Remove** both (video tab UI already gone with the page rebuild in Task 2).
- [x] **Step 2: Verify** `grep -ri "uploadVideo\|upload-video" frontend/src backend/main.py` returns nothing user-facing.

### Task 4: Navigation simplification

**Files:**
- Modify: `frontend/src/components/LewaNav.tsx` (remove TRIAGE link)
- Modify: `frontend/src/app/triage/page.tsx` (redirect to `/identification`)

- [x] **Step 1:** Remove the `/triage` nav link; keep the page as a small redirect component so old links/chatbot action links land on the unified page.
- [x] **Step 2:** Update chatbot `ActionLink` routes `/triage` → `/identification` in `response_generator.py`.

### Task 5: Complete frontend translation — all hardcoded strings

**Files:**
- Modify: `frontend/src/lib/i18n/translations.ts` (add ~120 keys × 3 languages)
- Modify: every page: `identification`, `map`, `patrol`, `chat`, `alerts`, `triage`(redirect only), `page.tsx` (home) — replace inline English with `t.key` lookups

**Interfaces:**
- Consumes: existing `useLanguage()` / `t` pattern.
- Produces: complete TranslationDict with zero English-only strings left in page bodies.

- [x] **Step 1: Inventory** every hardcoded string via grep per page.
- [x] **Step 2: Add keys** in en/hi/mr blocks.
- [x] **Step 3: Replace** all page strings with `t.*` references (language ternaries removed).
- [x] **Step 4: Verify** each page in browser in all 3 languages.

### Task 6: Chatbot trilingual backend

**Files:**
- Modify: `backend/services/chatbot/schemas.py` (`ChatRequest.language: Optional[str] = "en"`)
- Modify: `backend/services/chatbot/chatbot_service.py` (pass language through)
- Create: `backend/services/chatbot/response_translations.py` (per-language label packs)
- Modify: `backend/services/chatbot/response_generator.py` (wrap all handlers' strings with `T(lang, key)`)

- [x] **Step 1: Add `language` field** to `ChatRequest`; validate `{"en","hi","mr"}`.
- [x] **Step 2: Create label pack** with the ~60 recurring response strings (headers, "captures", "stations", "View on Map", etc.) × 3 languages.
- [x] **Step 3: Wrap every handler** to format through the pack (data values like names/numbers stay as-is).
- [x] **Step 5: Frontend** sends `language` from `LanguageContext` with each `/api/chat` POST.
- [x] **Step 6: Test** — "Show all tigers" in each language mode returns localized answer.

### Task 7: End-to-end verification + plan doc

- [x] Browser-verify: unified flow (upload → auto pipeline → result), SD panel on same page, chat in हिंदी + मराठी, every page translated, `/triage` redirects.
- [x] `tsc --noEmit` + backend syntax checks pass; servers restarted cleanly.

---

## Deferred (existing todo list, unchanged)
- Dashboard landing page (slideshow kept at separate route)
- Plain-language jargon rewrite (identification/patrol/chat pages)
- Capacitor APK packaging
