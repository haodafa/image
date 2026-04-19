#!/usr/bin/env bash
# Check runtime dependencies for text-card-generator.
# Usage: bash check_env.sh
# Exit 0 = ready, Exit 1 = missing dependencies.
set -e

missing=0

check() {
    local label="$1"
    local cmd="$2"
    local hint="$3"
    if eval "$cmd" >/dev/null 2>&1; then
        echo "[OK] $label"
    else
        echo "[MISSING] $label — $hint"
        missing=1
    fi
}

check "uv" "command -v uv" "curl -LsSf https://astral.sh/uv/install.sh | sh"
check "python3" "command -v python3" "install Python 3.10+"

# Check venv with Pillow
if [[ -f "/tmp/card-gen-venv/bin/python" ]]; then
    if /tmp/card-gen-venv/bin/python -c "from PIL import Image" 2>/dev/null; then
        echo "[OK] /tmp/card-gen-venv (Pillow installed)"
    else
        echo "[MISSING] Pillow in venv — run setup_env.sh"
        missing=1
    fi
else
    echo "[MISSING] /tmp/card-gen-venv — run setup_env.sh"
    missing=1
fi

# Check font cache
font_dir="/tmp/card-gen-fonts"
if [[ -f "$font_dir/NotoSansCJKsc-Regular.otf" && -f "$font_dir/NotoSansCJKsc-Bold.otf" ]]; then
    echo "[OK] CJK fonts cached"
else
    echo "[MISSING] CJK fonts — run setup_env.sh"
    missing=1
fi

if [[ "$missing" -eq 0 ]]; then
    echo
    echo "[OK] All dependencies ready."
    exit 0
fi

echo
echo "Run scripts/setup_env.sh to install missing deps."
exit 1
