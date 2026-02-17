# AEGIS-Ω v2.1 (Production-Practical Edition)

AEGIS-Ω is a Linux-first autonomous engineering runtime designed for continuous 24×7 operation with strict separation of concerns:

- **Control Plane** = orchestration only
- **Autonomy Engine** = cognition and planning only
- **Execution Layer** = isolated execution only

## Production improvements in this revision

- Per-task **virtual Linux workspace** under `~/.aegis-omega/sandboxes/<task-id>` with isolated working directory and environment variables.
- Parallel multi-agent style execution using worker pools for action requests.
- Goal decomposition with domain-aware plans (software, Linux OS, cybersecurity, research, DevOps).
- Parallel model-advisory router scaffold for multiple providers (OpenAI/Anthropic/Groq/local fallback).
- Recovery loop that can create automatic recovery tasks on failure.
- Authorization enforcement for security-domain actions.

## Architecture

### 1) Control Plane (`aegis_omega/control_plane`)
- Poll events
- Run schedules
- Submit and dispatch tasks

### 2) Autonomy Engine (`aegis_omega/autonomy_engine`)
- Decomposes goals into executable steps
- Generates action requests without touching shell/OS directly
- Uses a parallel provider router scaffold to aggregate plan fragments

### 3) Execution Layer (`aegis_omega/execution_layer`)
- Executes in sandboxed task workspaces
- Applies denylist safety filters
- Enforces configured authorization for cybersecurity scope

## Safety / governance constraints

This project supports **authorized defensive security workflows only**.

- Security tasks require explicit configured scope (`authorized_security_scopes`) in config.
- Dangerous destructive command patterns are blocked.
- Audit logs are append-only in `~/.aegis-omega/memory/audit.log`.

## Installation (Linux)

```bash
./install.sh
~/.aegis-omega/run-aegis.sh --goal "build a Python service with tests"
```

Optional components:

```bash
AEGIS_ENABLE_CLOUD=1 AEGIS_ENABLE_VECTOR=1 ./install.sh
```

## 24×7 runtime (systemd user service)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/aegis-omega.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now aegis-omega.service
```

## Uninstall

```bash
./uninstall.sh
```

## Important note on autonomy

AEGIS-Ω can automate large engineering workflows, but intentionally keeps legal/safety constraints active. It does not disable guardrails or run unrestricted offensive operations.
