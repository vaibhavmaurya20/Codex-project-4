#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${HOME}/.aegis-omega/venv"
RUNTIME_HOME="${HOME}/.aegis-omega"
CONFIG_FILE="${RUNTIME_HOME}/config.json"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "[ERR] Missing dependency: $1"; exit 1; }
}

select_optional_components() {
  ENABLE_CLOUD=0
  ENABLE_VECTOR=0
  if [[ "${AEGIS_ENABLE_CLOUD:-0}" == "1" ]]; then ENABLE_CLOUD=1; fi
  if [[ "${AEGIS_ENABLE_VECTOR:-0}" == "1" ]]; then ENABLE_VECTOR=1; fi
}

write_default_config() {
  local scope_json="[]"
  if [[ -n "${AEGIS_AUTH_SCOPE:-}" ]]; then
    scope_json="[\"${AEGIS_AUTH_SCOPE}\"]"
  fi

  cat > "$CONFIG_FILE" <<JSON
{
  "loop_interval_s": 5,
  "max_workers": 4,
  "enable_cloud_models": ${ENABLE_CLOUD},
  "enable_docker_execution": false,
  "lightweight_mode": true,
  "allow_live_terminal": false,
  "authorized_security_scopes": ${scope_json},
  "auto_recovery": true
}
JSON
}

main() {
  require_cmd python3
  require_cmd bash

  python3 -m venv "$VENV_DIR"
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"

  python -m pip install --upgrade pip
  select_optional_components

  extras=""
  [[ "$ENABLE_CLOUD" == "1" ]] && extras="${extras},cloud"
  [[ "$ENABLE_VECTOR" == "1" ]] && extras="${extras},vector"
  extras="${extras#,}"

  if [[ -n "$extras" ]]; then
    pip install -e "$ROOT_DIR[$extras]"
  else
    pip install -e "$ROOT_DIR"
  fi

  mkdir -p "$RUNTIME_HOME"/{runtime,logs,memory,sandboxes}
  cp "$ROOT_DIR/scripts/run-aegis.sh" "$RUNTIME_HOME/run-aegis.sh"
  chmod +x "$RUNTIME_HOME/run-aegis.sh"
  write_default_config

  echo "[OK] Installed AEGIS-Ω into $RUNTIME_HOME"
  echo "Run: $RUNTIME_HOME/run-aegis.sh --goal 'build project skeleton'"
}

main "$@"
