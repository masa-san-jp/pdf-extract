#!/bin/bash
# Setup for /pdf-extract
#
# Installs Python dependencies. Drive access additionally needs ADC
# (verified below); local-PDF extraction works without credentials.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Python dependencies"
python3 -m pip install -q -r "$SCRIPT_DIR/requirements.txt"

echo "==> Verifying Application Default Credentials (for Drive inputs)"
if ! python3 - <<'PY' 2>/dev/null
from google.auth import default
creds, _ = default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
PY
then
    echo ""
    echo "NOTE: Application Default Credentials missing or insufficient scopes."
    echo "      Local PDF extraction still works without this."
    echo "      For Google Drive PDFs, run:"
    echo "          bash $SCRIPT_DIR/auth.sh                  # active account"
    echo "          bash $SCRIPT_DIR/auth.sh <email>          # specific account"
fi

echo "==> OK. Try:"
echo "    $SCRIPT_DIR/pdf_extract.py /path/to/file.pdf"
echo "    $SCRIPT_DIR/pdf_extract.py <drive-id-or-url>"
