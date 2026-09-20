# WORLDLINE security model

This document states plainly what WORLDLINE defends against, what it does not, and where its
claims end. It is deliberately conservative: a guarantee is listed under "Holds" only if it was
verified in code or demonstrated, and everything else is named as a limit rather than left
implied. Last reviewed 2026-09-02 (see `SECURITY-AUDIT-2026-09-02.md`).

## The adversary WORLDLINE is built for

The primary adversary is **the coding agent running inside a world** — possibly prompt-injected
by a hostile mission or by content in the repository it reads. WORLDLINE's job is to let that
agent work without being able to touch the operator's real files or commit anything without an
authorized, atomic collapse.

## Holds (verified)

- **Filesystem containment of agents.** An agent's overlay lower layer is a materialized *copy*
  of the roots, not the live inode; writes land in the overlay upper; the real roots live behind
  a symlink chain in managed storage and are never bind-mounted into a world. `$HOME` is masked
  by tmpfs, so nothing under the real home is visible except what is explicitly projected: the
  adapter's credential file and the operator-configured `readonlyHomePaths` (by default
  `~/.local/bin`, `~/.local/share/mise`, `~/.config/mise`, `~/opt/gnat`). `~/.ssh`, the rest of
  `~/.config`, Wayland/D-Bus/ydotool/XDG session sockets, and **the worldline daemon socket
  itself** are absent from a world, so an agent cannot drive the daemon.
- **Escape resistance.** Absolute, `..`-escaping, and NUL symlink targets are rejected at
  capture, materialize, and the mandatory staged recapture (`EXTERNAL_SYMLINK`); hardlinks
  outside a root are rejected; walks never follow symlinks; special/cross-device files are
  rejected. Agent worlds, checks, and shells run as the real uid inside the user namespace
  (the only uid mapped either way); `simulate` futures keep namespace root, and either identity
  is neutered (`--cap-drop ALL`, `--disable-userns`, `--unshare-user`, `NoNewPrivileges`).
- **Credential projection.** Each builtin adapter binds its credential file read-only at its
  home path; nothing else of `$HOME` is visible. omp is the one exception: it opens its whole
  state database read-write at startup, so the world gets a per-world private copy (SQLite
  backup, `0600`, under the world's runtime) and the host database is never mounted. Claude
  Code's hooks are disabled inside a world (`--settings '{"disableAllHooks":true}'`): they are
  host desktop integrations, and a hook that exits 2 silently blocks the mission.
- **Atomic, crash-consistent collapse.** All roots swap in a single `renameat2(RENAME_EXCHANGE)`
  of the `live` mapping; PRIME is re-hashed against `beforeRoot` and the staged payload against
  `stagedRoot` immediately before the exchange; a generation marker inside the swapped directory
  makes crash recovery deterministic and fail-closed. A second daemon is refused
  (`DAEMON_ALREADY_RUNNING`).
- **Daemon access control.** Socket is `0600` with an `SO_PEERCRED` uid check per connection and
  a bounded request envelope. The global config is rejected unless it is a regular, owner-owned,
  non-group/other-accessible file — the daemon refuses to start otherwise.
- **No shell, parameterized SQL.** No `shell=True`/`eval`/`exec`; every subprocess is an argv
  list; all SQL uses placeholders.
- **Host-side git inspection is hardened (1.0.1).** Registered repos are untrusted; git's
  config-driven command execution is neutralized before inspection (see CHANGELOG 1.0.1).

## Limits — known, and where the claims end

These are not defended, by design or by current architecture. Treat them as the boundary of the
trust you place in WORLDLINE.

1. **A world has host network access, and agent worlds mount real credentials.** A coding agent
   must reach its model API, so the sandbox keeps host networking and read-only-binds the
   agent's real credential file (e.g. `~/.claude/.credentials.json`). A prompt-injected agent
   can therefore exfiltrate those credentials or reach host-local/LAN services. There is no
   egress filter today. If you run agents on untrusted missions or untrusted repository content,
   assume the mounted credential and any network-reachable host service are exposed. A future
   egress policy (allowlist the model endpoint, or broker the credential) is the intended fix;
   until then this is a deliberate, disclosed limit. `simulate` likewise contains filesystem
   effects only — its network side effects are real.

2. **The evidence chain is tamper-evident against the agent, not against you.** Receipts and the
   causal/receipt chains are SHA-256 hash chains with **no asymmetric signature and no external
   anchor**. The sandboxed agent cannot reach the store, so it cannot forge them — that is the
   property that matters for WORLDLINE's adversary. But any process running as your uid *outside*
   the sandbox can rewrite the store and the chain re-verifies clean, exactly as it can replace
   the binary or delete your files. `worldline log --verify` proves internal self-consistency,
   not authenticity against a same-uid attacker. Anchoring the chain head into a signed external
   ledger would close this; it is not done today.

3. **"Proved" describes the kernel, not an attestation of the running system.** The 130-check
   SPARK proof covers the hash/link/decision/lifecycle *library*. The authority — what is
   hashed and whether the decision gates the exchange — is enforced in Python. Since 1.1.0 the
   transaction lifecycle (PREPARED → AUTHORIZED → COMMITTED, DENIED sticky) is consulted from
   the proved unit on every state change, and the kernel's parent comparison receives the
   store's parent identity rather than the candidate's own claim on both sides.
   `invariantPreservation: PROVED` in a receipt means the on-disk proof manifest matched the
   library at receipt time; the library is selected by `WORLDLINE_CORE_LIB`/package path and the
   manifest is unauthenticated, so a same-uid attacker can make it report `PROVED` for a
   substituted library. Read it as "the proved hash kernel is in use per its unsigned manifest,"
   not "the running system is proved correct."

## Reporting

This is a personal project on a single-user machine. Security notes and audit findings live
alongside the code in `SECURITY-AUDIT-*.md`.
