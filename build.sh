#!/bin/bash
# Build script for Pinoy Skater executable

echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo "Building executable..."
pyinstaller pinoy-skater.spec

echo "Build complete! Executable is in the 'dist/PinoySkater' folder"
