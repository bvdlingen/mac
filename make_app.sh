#!/usr/bin/env bash
# Build hello_gui in release mode and package it as a double-clickable .app bundle.
# Usage: ./make_app.sh  (from anywhere — it finds its own folder)
set -euo pipefail
cd "$(dirname "$0")"

APP_NAME="Hello World"
APP="../${APP_NAME}.app"

echo "==> cargo build --release"
cargo build --release

echo "==> assembling ${APP_NAME}.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

cp target/release/hello_gui "$APP/Contents/MacOS/hello-gui"
[ -f resources/AppIcon.icns ] && cp resources/AppIcon.icns "$APP/Contents/Resources/AppIcon.icns"

cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>              <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>       <string>${APP_NAME}</string>
    <key>CFBundleExecutable</key>        <string>hello-gui</string>
    <key>CFBundleIdentifier</key>        <string>com.example.hello-world</string>
    <key>CFBundleIconFile</key>          <string>AppIcon</string>
    <key>CFBundlePackageType</key>       <string>APPL</string>
    <key>CFBundleShortVersionString</key><string>0.1.0</string>
    <key>CFBundleVersion</key>           <string>1</string>
    <key>LSMinimumSystemVersion</key>    <string>11.0</string>
    <key>NSHighResolutionCapable</key>   <true/>
</dict>
</plist>
EOF

printf 'APPL????' > "$APP/Contents/PkgInfo"

echo "==> ad-hoc code signing"
codesign --force --sign - "$APP"

echo "==> done: $APP"
echo
echo "GUI:      open \"../${APP_NAME}.app\""
echo "GUI + text: open \"../${APP_NAME}.app\" --args -m \"your extra text\""
echo "CLI:      \"${APP}/Contents/MacOS/hello-gui\" cli \"your extra text\""
