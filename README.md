# AEGIS-Ω v2.1 (Production-Practical Edition)

AEGIS-Ω is a real Linux-first autonomous engineering runtime designed for continuous 24×7 execution with strict architectural separation:

1. **Control Plane** → orchestration only
2. **Autonomy Engine** → cognition/planning only
3. **Execution Layer** → isolated execution only

## Major upgrades in this revision

- Per-task **virtual Linux-like environments** in `~/.aegis-omega/sandboxes/<task-id>`.
- Parallel multi-agent action execution with configurable concurrency.
- Multi-provider LLM router abstraction for simultaneous planning fan-out.
- Retry, scheduled recovery, and dead-letter handling in control plane.
- Persistent pending task snapshots to survive reboot/crash and auto-resume.
- Expanded installer resource detection and lightweight defaults for lower-end laptops.

## Architecture

### 1) Control Plane (`aegis_omega/control_plane/orchestrator.py`)

- Task queue, scheduling, retries, dead-letter queue.
- No cognition logic.
- No command execution.

### 2) Autonomy Engine (`aegis_omega/autonomy_engine/*`)

- Goal decomposition into workflow steps.
- Domain-specific strategy scaffolds (software/linux/cyber/research/devops).
- Multi-provider planning hints via `MultiLLMRouter` (offline-safe default behavior).

### 3) Execution Layer (`aegis_omega/execution_layer/*`)

- Isolated command execution in per-task sandbox workspaces.
- Safety policy denylist for destructive host operations.
- Virtualenv-backed task environment creation.

## Governance model

Implemented root governor plus long-lived domain directors:

- `software_architect_director`
- `linux_os_director`
- `cybersecurity_director`
- `research_simulation_director`
- `devops_ci_director`

Directors spawn short-lived worker tasks and route goals by domain.

## Persistent memory

- `short_term`
- `long_term`
- `failures`
- `tool_effectiveness`

All memory is versioned and persisted to disk (`~/.aegis-omega/memory/memory.json`) with append-only audit logs.

## Install (Linux)

```bash
./install.sh
```

Optional extras:

```bash
AEGIS_ENABLE_CLOUD=1 AEGIS_ENABLE_VECTOR=1 ./install.sh
```

Optional provider list for planning fan-out:

```bash
AEGIS_LLM_PROVIDERS="openai,anthropic,local_fallback" ./install.sh
```

## Run

```bash
~/.aegis-omega/run-aegis.sh --goal "build and test a python web service"
~/.aegis-omega/run-aegis.sh --goal "analyze linux kernel config for embedded target"
~/.aegis-omega/run-aegis.sh --goal "perform authorized vulnerability analysis and mitigation plan"
```

## 24×7 operation (systemd user mode)

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

## Security and policy

This implementation supports **authorized defensive cybersecurity and engineering automation only**.

- No blind exploit spraying.
- No destructive host/system commands (denylist enforced).
- Audit logs are immutable append-only lines.

## Current boundaries

- External cloud API invocation is intentionally plugin-style (router exists; API calls remain opt-in integration work).
- Heavy backends (Docker/QEMU/KVM orchestration) are staged as modular adapters, keeping default install light for low-resource hardware.
