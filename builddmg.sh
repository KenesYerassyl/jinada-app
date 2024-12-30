#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/Jinada.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/Jinada.dmg" && rm "dist/Jinada.dmg"
create-dmg \
  --volname "Jinada" \
  --volicon "resources/icon_macosx.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Jinada.app" 175 120 \
  --hide-extension "Jinada.app" \
  --app-drop-link 425 120 \
  "dist/Jinada.dmg" \
  "dist/dmg/"