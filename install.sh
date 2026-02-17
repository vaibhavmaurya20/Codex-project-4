#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${HOME}/.aegis-omega/venv"
RUNTIME_HOME="${HOME}/.aegis-omega"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "[ERR] Missing dependency: $1"; exit 1; }
}

detect_resources() {
  MEM_MB=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo 2>/dev/null || echo 0)
  CORES=$(nproc 2>/dev/null || echo 1)
  echo "[INFO] Detected ${CORES} CPU cores and ~${MEM_MB}MB RAM"
  if [[ "$MEM_MB" -lt 6000 ]]; then
    echo "[WARN] Low RAM detected; enforcing lightweight defaults"
    export AEGIS_LIGHTWEIGHT=1
  fi
}

select_optional_components() {
  ENABLE_CLOUD=${AEGIS_ENABLE_CLOUD:-0}
  ENABLE_VECTOR=${AEGIS_ENABLE_VECTOR:-0}
}

write_default_config() {
  mkdir -p "$RUNTIME_HOME"/{runtime,logs,memory,sandboxes}
  cat > "$RUNTIME_HOME/config.json" <<JSON
{
  "loop_interval_s": 5,
  "max_workers": 4,
  "max_parallel_agents": 3,
  "enable_cloud_models": ${AEGIS_ENABLE_CLOUD:-false},
  "enable_docker_execution": false,
  "enable_virtual_linux_env": true,
  "lightweight_mode": ${AEGIS_LIGHTWEIGHT:-true},
  "llm_providers": ["${AEGIS_LLM_PROVIDERS:-local_fallback}"]
}
JSON
}

main() {
  require_cmd python3
  require_cmd bash

  detect_resources

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

  cp "$ROOT_DIR/scripts/run-aegis.sh" "$RUNTIME_HOME/run-aegis.sh"
  chmod +x "$RUNTIME_HOME/run-aegis.sh"
  write_default_config

  echo "[OK] Installed AEGIS-Ω into $RUNTIME_HOME"
  echo "Run: $RUNTIME_HOME/run-aegis.sh --goal 'build project skeleton'"
}

main "$@"
