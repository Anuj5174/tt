# TigerTrace Android APK — Build Guide

The repo ships a ready-to-open **Android Studio project** at `frontend/android/`.
No web code needs to be written on the Android side — the app is the TigerTrace
web interface packaged with Capacitor, talking to the FastAPI backend over your
reserve's local network.

## One-time setup (already done in this repo)

- `next.config.ts` → `output: "export"` (static site build)
- `capacitor.config.ts` → appId `org.pench.tigertrace`, cleartext HTTP allowed
- `frontend/android/` → generated Gradle project (Android Studio-ready)
- App icons + splash generated into `android/app/src/main/res/`

## Build the APK (your part — Android Studio)

1. Open Android Studio → **File ▸ Open** → select the folder
   `TigerTrace-main/frontend/android`
2. Let Gradle sync finish (first time downloads dependencies).
3. Menu: **Build ▸ Build App Bundle(s) / APK(s) ▸ Build APK(s)**
4. The APK appears at
   `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
5. Copy it to a phone (USB/ShareApp) and enable *Install unknown apps* once.

## Point the app at the main machine

The app ships pointing at `http://localhost:8000` (wrong for a phone). On first
launch:

1. Open the app → dashboard → **Server Settings** (bottom of the page)
2. Enter the deployed machine's LAN address, e.g. `http://192.168.1.50:8000`
3. Tap **Save** — the app reloads and remembers it.

The phone and the machine must be on the same Wi-Fi/hotspot. If the machine's IP
changes later, just update it here — no rebuild needed.

## After changing the web app

Whenever you edit the frontend and want a fresh APK:

```bash
cd frontend
npm run build        # static export into out/
npx cap sync android # copies out/ into the Android project
```

Then rebuild in Android Studio.

## Backend note

Start the backend so it accepts LAN connections (not only localhost):

```bash
cd backend
.venv/Scripts/python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

CORS is already open (`allow_origins=["*"]`), so no backend change is needed.

## Troubleshooting

- **Blank map in the field**: map tiles come from OpenStreetMap and need
  internet; tiger territories/stations still draw from the local backend.
- **"Connection Error" in chat**: wrong server address, or backend not running
  with `--host 0.0.0.0`.
- **Upload button does nothing in some WebViews**: use the file picker that
  opens; if a browser on the phone is preferable for a demo, open
  `http://<machine-ip>:3000` in Chrome instead.
