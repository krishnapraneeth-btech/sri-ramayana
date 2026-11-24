# Sri Ramayana — The Eternal Epic (Android App & Web Cinema)

An offline-first **Android application** (`Ramayana_Epic.apk`, SDK 24–34) and interactive **HTML5 Cinema Player** telling the complete **Valmiki Ramayana** across **14 cinematic 15-minute episodes** (168 scenes total) spanning all **7 Kandas**, with live **5-language switching** (**Telugu, Hindi, English, Tamil, Malayalam**), Sanskrit shlokas, devotional Indian raga background music, and real-time HTML5 Canvas VFX.

## Download & Install (Android)
- Download **`Ramayana_Epic.apk`** directly from the repository root (or from **Releases**) and install it on Android 7.0+ (API 24+).
- If a regional voice pack (Telugu, Hindi, Tamil, or Malayalam) is not yet installed on your phone, tap **Voice Pack Help → Open Device Voice Settings** inside the app to download Google Speech Services voice data for offline narration.

## Features
- **14 Complete 15-Minute Episodes (3.5 Hours Total):**
  - **Bala Kanda** (Episodes 1–2): Putrakameshti Yagna to Sita Swayamvaram & Parashurama
  - **Ayodhya Kanda** (Episodes 3–4): Vanavasa Departure, Guha & Bharata's Paduka Rajya
  - **Aranya Kanda** (Episodes 5–6): Panchavati, Golden Deer, Jatayu & Shabari/Hanuman
  - **Kishkindha Kanda** (Episodes 7–8): Kishkindha Alliance, Vali Moksha & Four-Direction Search
  - **Sundara Kanda** (Episodes 9–10): Samudra Langhana, Ashoka Vatika, Lanka Dahan & Chudamani
  - **Yuddha Kanda & Coronation** (Episodes 11–13): Rama Setu, Sanjeevani, Ravana Samhara, Agni Pariksha & Pattabhishekam
  - **Uttara Kanda** (Episode 14): Ashwamedha, Valmiki Ashram, Lava–Kusha's Song & Sarayu Vaikuntha
- **5-Language Live Switching:** Telugu (`te-IN`), Hindi (`hi-IN`), English (`en-IN`), Tamil (`ta-IN`), and Malayalam (`ml-IN`).
- **Native Android Bridge (`RamayanaBridge.java`):**
  - Uses Android `TextToSpeech` + `UtteranceProgressListener` for sentence-synchronized narration & subtitle highlighting.
  - Uses native `MediaPlayer` for seamless looping raga MP3 background music (`bgm_divine_dawn`, `bgm_royal_court`, `bgm_sorrow_exile`, `bgm_forest_mystic`, `bgm_heroic_ocean`, `bgm_epic_war`) with automatic volume ducking during speech.
- **Real-Time Visuals (`visualizer.js` & `styles.css`):** 20 scene artworks (`1280×720`) paired with Ken Burns camera choreography and 15 custom particle/light Canvas VFX modes.

## Project Layout
```
├── Ramayana_Epic.apk                # Prebuilt signed Android APK (v2 + v3)
├── android/
│   ├── AndroidManifest.xml
│   ├── res/                         # App launcher icons & dark theme
│   ├── src/com/sriramayana/epic/    # MainActivity.java & RamayanaBridge.java
│   └── assets/www/                  # WebView UI, i18n, 14 episodes, 20 images, 6 BGM tracks
├── scripts/
│   ├── build_apk.sh                 # Zero-dependency SDK 34 APK builder (aapt2 + javac + d8 + apksigner)
│   ├── generate_bgm.py              # Indian raga synthesizer
│   ├── generate_scenes_svg.py       # SVG/PIL canvas renderer for scenes 10–20
│   ├── optimize_art.py              # Image optimizer & mipmap generator
│   └── preview_server.py            # Local HTTP server for browser testing
└── .github/workflows/
    └── build-apk.yml                # Automated CI APK build on push
```

## Building from Source
Requires **JDK 11+** and **Android SDK Platform 34 + Build-Tools 34.0.0** (`aapt2`, `d8`, `zipalign`, `apksigner`):

```bash
bash scripts/build_apk.sh build/Ramayana_Epic.apk
```

## Running the Browser Preview
```bash
python3 scripts/preview_server.py
# Open http://localhost:8080
```
