#!/usr/bin/env bash
# Install runtime dependencies for text-card-generator.
# Usage: bash setup_env.sh
set -e

# 1. Create venv and install Pillow
VENV="/tmp/card-gen-venv"
if [[ ! -f "$VENV/bin/python" ]]; then
    echo "[INSTALL] Creating venv at $VENV"
    uv venv "$VENV"
fi

if ! "$VENV/bin/python" -c "from PIL import Image" 2>/dev/null; then
    echo "[INSTALL] Pillow"
    UV_CACHE_DIR=/tmp/uv-cache uv pip install --python "$VENV/bin/python" Pillow
else
    echo "[SKIP] Pillow already installed"
fi

# 2. Download CJK fonts
FONT_DIR="/tmp/card-gen-fonts"
mkdir -p "$FONT_DIR"

BASE_URL="https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese"

if [[ ! -f "$FONT_DIR/NotoSansCJKsc-Regular.otf" ]]; then
    echo "[INSTALL] NotoSansCJKsc-Regular.otf"
    curl -sL "$BASE_URL/NotoSansCJKsc-Regular.otf" -o "$FONT_DIR/NotoSansCJKsc-Regular.otf"
else
    echo "[SKIP] NotoSansCJKsc-Regular.otf exists"
fi

if [[ ! -f "$FONT_DIR/NotoSansCJKsc-Bold.otf" ]]; then
    echo "[INSTALL] NotoSansCJKsc-Bold.otf"
    curl -sL "$BASE_URL/NotoSansCJKsc-Bold.otf" -o "$FONT_DIR/NotoSansCJKsc-Bold.otf"
else
    echo "[SKIP] NotoSansCJKsc-Bold.otf exists"
fi

echo
echo "[DONE] Re-run scripts/check_env.sh to verify."
