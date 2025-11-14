#!/bin/bash
# Build script for Pinoy Skater executable

echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo "Building executable for Pinoy Skater (Arcade version)..."
pyinstaller pinoy-skater_4.spec

echo "Build complete! Executable is in the 'dist/PinoySkater' folder"
