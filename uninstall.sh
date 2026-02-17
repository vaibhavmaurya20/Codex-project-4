#!/usr/bin/env bash
set -euo pipefail

TARGET="${HOME}/.aegis-omega"
if [[ -d "$TARGET" ]]; then
  rm -rf "$TARGET"
  echo "[OK] Removed $TARGET"
else
  echo "[INFO] Nothing to remove"
fi
