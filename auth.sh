#!/bin/bash
# Run ADC login with the scopes /pdf-extract needs for Drive PDFs.
# Usage:
#   bash ./auth.sh
#   bash ./auth.sh <account-email>
set -euo pipefail

SCOPES="https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform"

ACCOUNT="${1:-}"

if [[ -n "$ACCOUNT" ]]; then
  echo "==> Launching gcloud ADC login as ${ACCOUNT}"
  exec gcloud auth application-default login \
    --account="$ACCOUNT" \
    --scopes="$SCOPES"
else
  echo "==> Launching gcloud ADC login (active account)"
  exec gcloud auth application-default login --scopes="$SCOPES"
fi
