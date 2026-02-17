#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${HOME}/.aegis-omega/venv"
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Install first: ./install.sh"
  exit 1
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
exec aegis-omega "$@"
