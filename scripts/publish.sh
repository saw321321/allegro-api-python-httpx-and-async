#!/bin/bash

# Script to publish package to PyPI
# Usage: ./scripts/publish.sh [--test]

set -e

echo "🚀 Allegro API Python - Publishing Script"
echo "========================================"

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run from project root."
    exit 1
fi

# Parse arguments
TEST_MODE=false
if [ "$1" == "--test" ]; then
    TEST_MODE=true
    echo "📦 Running in TEST mode (will upload to TestPyPI)"
else
    echo "📦 Running in PRODUCTION mode (will upload to PyPI)"
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Check if all changes are committed
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run tests
echo "🧪 Running tests..."
pytest tests/ || {
    echo "❌ Tests failed! Fix them before publishing."
    exit 1
}

# Run linting
echo "🔍 Running linting..."
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 || {
    echo "❌ Linting failed! Fix issues before publishing."
    exit 1
}

# Run type checking
echo "🔍 Running type checking..."
mypy src/ || {
    echo "❌ Type checking failed! Fix issues before publishing."
    exit 1
}

# Build the package
echo "📦 Building package..."
python -m build || {
    echo "❌ Build failed!"
    exit 1
}

# Check the package
echo "🔍 Checking package with twine..."
python -m twine check dist/* || {
    echo "❌ Package check failed!"
    exit 1
}

# Show package contents
echo "📋 Package contents:"
ls -la dist/

# Get version from pyproject.toml
VERSION=$(grep "^version" pyproject.toml | cut -d'"' -f2)
echo "📌 Version to publish: $VERSION"

# Confirm before upload
if [ "$TEST_MODE" = true ]; then
    REPO_URL="https://test.pypi.org/project/allegro-api/$VERSION/"
    echo "📤 Ready to upload to TestPyPI"
else
    REPO_URL="https://pypi.org/project/allegro-api/$VERSION/"
    echo "📤 Ready to upload to PyPI"
    echo "⚠️  This is PRODUCTION - package will be publicly available!"
fi

read -p "Continue with upload? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Upload cancelled"
    exit 1
fi

# Upload
if [ "$TEST_MODE" = true ]; then
    echo "📤 Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/* || {
        echo "❌ Upload to TestPyPI failed!"
        exit 1
    }
    echo "✅ Successfully uploaded to TestPyPI!"
    echo "🔗 View at: $REPO_URL"
    echo ""
    echo "📥 To install from TestPyPI:"
    echo "pip install --index-url https://test.pypi.org/simple/ allegro-api"
else
    echo "📤 Uploading to PyPI..."
    python -m twine upload dist/* || {
        echo "❌ Upload to PyPI failed!"
        exit 1
    }
    echo "✅ Successfully uploaded to PyPI!"
    echo "🔗 View at: $REPO_URL"
    echo ""
    echo "📥 To install:"
    echo "pip install allegro-api"
fi

# Tag the release
echo ""
read -p "Create git tag for v$VERSION? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git tag -a "v$VERSION" -m "Release version $VERSION"
    echo "✅ Tagged as v$VERSION"
    echo "📤 Don't forget to push tags: git push origin v$VERSION"
fi

echo ""
echo "🎉 Publishing complete!"