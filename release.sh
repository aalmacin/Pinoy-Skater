#!/bin/bash
# Release script for Pinoy Skater
# Usage: bash release.sh <version>
# Example: bash release.sh 1.0.0

# Check if version number is provided
if [ -z "$1" ]; then
    echo "Error: Version number is required"
    echo "Usage: bash release.sh <version>"
    echo "Example: bash release.sh 1.0.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"

echo "Creating release for version ${VERSION}..."
echo "Tag: ${TAG}"

# Create the git tag
echo "Creating git tag..."
git tag "${TAG}"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create git tag"
    exit 1
fi

echo "Tag created successfully!"

# Push the tag to origin
echo "Pushing tag to origin..."
git push origin "${TAG}"

if [ $? -ne 0 ]; then
    echo "Error: Failed to push tag to origin"
    echo "You may need to delete the local tag: git tag -d ${TAG}"
    exit 1
fi

echo ""
echo "✓ Release ${TAG} created successfully!"
echo ""
echo "GitHub Actions will now:"
echo "  1. Build executables for Windows and Linux"
echo "  2. Create a GitHub Release"
echo "  3. Upload the executables as release assets"
echo ""
echo "Check the progress at:"
echo "  https://github.com/aalmacin/Pinoy-Skater/actions"
echo ""
echo "Once complete, the release will be available at:"
echo "  https://github.com/aalmacin/Pinoy-Skater/releases/tag/${TAG}"
