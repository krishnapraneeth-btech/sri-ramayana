#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ANDROID_SDK="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-/opt/android-sdk}}"
if [[ -d "$ANDROID_SDK/build-tools/34.0.0" ]]; then
  BUILD_TOOLS="$ANDROID_SDK/build-tools/34.0.0"
else
  BUILD_TOOLS="$(ls -1d "$ANDROID_SDK"/build-tools/* 2>/dev/null | sort -V | tail -n 1)"
fi

if [[ -f "$ANDROID_SDK/platforms/android-34/android.jar" ]]; then
  PLATFORM_JAR="$ANDROID_SDK/platforms/android-34/android.jar"
else
  PLATFORM_JAR="$(ls -1 "$ANDROID_SDK"/platforms/android-*/android.jar 2>/dev/null | sort -V | tail -n 1)"
fi

PROJ_DIR="$APP_DIR/android"
OUT_APK="${1:-$APP_DIR/build/Ramayana_Epic.apk}"
WORK="$(mktemp -d /tmp/ramayana_build.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/gen" "$WORK/classes" "$WORK/dex" "$(dirname "$OUT_APK")"

echo "Using ANDROID_SDK=$ANDROID_SDK"
echo "Using BUILD_TOOLS=$BUILD_TOOLS"
echo "Using PLATFORM_JAR=$PLATFORM_JAR"

echo "1. Compiling Android resources with aapt2..."
"$BUILD_TOOLS/aapt2" compile --dir "$PROJ_DIR/res" -o "$WORK/res.zip"

echo "2. Linking resources, manifest, and assets..."
"$BUILD_TOOLS/aapt2" link \
  -I "$PLATFORM_JAR" \
  --manifest "$PROJ_DIR/AndroidManifest.xml" \
  -A "$PROJ_DIR/assets" \
  -0 .mp3 -0 mp3 \
  --min-sdk-version 24 \
  --target-sdk-version 34 \
  --version-code 1 \
  --version-name 1.0.0 \
  --java "$WORK/gen" \
  -o "$WORK/base.apk" \
  "$WORK/res.zip"

echo "3. Compiling Java sources..."
javac --release 11 \
  -classpath "$PLATFORM_JAR" \
  -d "$WORK/classes" \
  "$WORK/gen/com/sriramayana/epic/R.java" \
  "$PROJ_DIR/src/com/sriramayana/epic/RamayanaBridge.java" \
  "$PROJ_DIR/src/com/sriramayana/epic/MainActivity.java"

echo "4. Dexing classes with d8..."
mapfile -t CLASS_FILES < <(find "$WORK/classes" -name "*.class")
"$BUILD_TOOLS/d8" \
  --min-api 24 \
  --release \
  --lib "$PLATFORM_JAR" \
  --output "$WORK/dex" \
  "${CLASS_FILES[@]}"

echo "5. Packaging classes.dex into APK..."
(cd "$WORK/dex" && zip -q -u "$WORK/base.apk" classes.dex)

echo "6. Zipaligning APK..."
"$BUILD_TOOLS/zipalign" -p -f 4 "$WORK/base.apk" "$WORK/aligned.apk"

echo "7. Generating signing key & signing APK (v1+v2+v3)..."
keytool -genkeypair -noprompt \
  -keystore "$WORK/ramayana.jks" \
  -alias ramayana \
  -keyalg RSA -keysize 2048 \
  -validity 10000 \
  -storepass ramayana108 \
  -keypass ramayana108 \
  -dname "CN=Sri Ramayana App, O=Eternal Epic, L=Ayodhya, C=IN" >/dev/null 2>&1

"$BUILD_TOOLS/apksigner" sign \
  --ks "$WORK/ramayana.jks" \
  --ks-key-alias ramayana \
  --ks-pass pass:ramayana108 \
  --key-pass pass:ramayana108 \
  --v1-signing-enabled true \
  --v2-signing-enabled true \
  --v3-signing-enabled true \
  --v4-signing-enabled false \
  --out "$OUT_APK" \
  "$WORK/aligned.apk"

echo "8. Verifying signed APK..."
"$BUILD_TOOLS/apksigner" verify --verbose "$OUT_APK"
ls -lh "$OUT_APK"
