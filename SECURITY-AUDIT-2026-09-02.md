# WORLDLINE aggressive security audit — 2026-09-02

Method: four parallel adversarial static auditors (injection, TOCTOU/atomicity, containment,
ledger/ABI) + independent reading of the crown-jewel code + isolated dynamic PoCs (throwaway
daemon, private HOME/XDG, fixture adapters, zero model quota, real daemon untouched). Every
load-bearing finding below was verified against the code or demonstrated live, not taken on a
subagent's word. SPARK proof reproduced 130/130; project test suite 44 pass; skill health check
26/26; installed .so == manifest hash.

## Verdict

WORLDLINE splits into two halves with very different security postures.

- **Containment + atomic collapse + crash-recovery core: excellent and lives up to its claims.**
  Verified strong (see "Holds"). This is the hard part and it is done well.
- **The evidence/proof layer oversells against a determined same-uid adversary,** and there was
  **one confirmed host-level RCE** reachable by the tool's own normal use. The RCE is now fixed
  and the fix is verified. The evidence-layer gaps are calibration + hardening, detailed below.

---

## CONFIRMED — reachable by WORLDLINE's real adversary (an untrusted repo / agent)

### C1 [CRITICAL, FIXED] Host RCE via a hostile repo's `.git/config`
`linux/git.py:_run` ran `git` host-side (no sandbox) with the operator's real `$HOME`, and
`roots.py:176` calls `validate()`→`git.capture()` **before** the `CONFIRMATION_REQUIRED` raise
at :178. `git status`/`diff` execute commands named in the repo's own `.git/config`.
**Dynamically confirmed on git 2.55.0** by driving the *exact* commands `GitAdapter.capture`
runs: `core.fsmonitor` fires on `status --porcelain=v2` and executes a planted script — i.e.
`worldline init ~/some-cloned-repo` runs attacker code as the operator at the preview, before
you approve anything. (`diff.external` did NOT fire: `capture` already passes `--no-ext-diff`,
which blocks that one vector — so `core.fsmonitor` via status is the reachable path, with hooks
and textconv/filter drivers as adjacent theoretical vectors.) The same host-side sink re-fires
on every fork/collapse/return via checkpoint.freeze/finalize/transaction._capture.
**Fix applied (verified):** `git.py` now injects highest-precedence `-c` overrides
(core.fsmonitor=, core.hooksPath=/dev/null, diff.external=, core.sshCommand=, pager/editor/
askPass/credential.helper/uploadpack.packObjectsHook blanked, protocol.ext=never) and a
hardened env (GIT_CONFIG_GLOBAL/SYSTEM=/dev/null, GIT_TERMINAL_PROMPT=0, GIT_OPTIONAL_LOCKS=0,
GIT_ALLOW_PROTOCOL=file, GIT_ATTR_NOSYSTEM=1). Re-test: 3 hardened calls fire nothing; an
unhardened git on the same repo still pops — test is live. Suite still 44 pass.
**Residual / recommended:** attribute-driven textconv/filter drivers via repo-local config are
narrower (need a matching .gitattributes) but not fully closable by `-c` name overrides; the
belt-and-suspenders fix is to run git.capture inside the existing bwrap sandbox (no net, tmpfs
home, repo mounted) like checks already do.

### C2 [HIGH] Sandbox shares host network + mounts real credentials → agent exfil channel
`linux/namespaces.py:156-158` `--unshare-all` then `--share-net` (host network, no egress
filter, no seccomp), and `:203` `--ro-bind`s the real credential file (agents/claude.py:26 →
`~/.claude/.credentials.json`; codex/pi/omp similar). Agents launch with approval gates OFF
(`--dangerously-skip-permissions` etc.). A prompt-injected mission or hostile repo content can
make the credentialed agent read the mounted key and POST it out, and reach host `127.0.0.1`
services. This is inherent tension — a coding agent needs network to reach its model API — so
the fix is a **design decision**, not a one-liner: egress-restrict to the model endpoint(s),
or deliver the credential through a broker instead of a file bind, or disclose explicitly.
Auto-ghost worlds (unattended, default OFF) amplify it.

### C3 [MEDIUM] "simulate … nothing on the host changes" is filesystem-only
`simulate` correctly makes system roots writable overlays (no persistent FS damage), but the
same builder gives it `--share-net`. `simulate curl …` / hitting a real API / deleting cloud
resources are not counterfactual. Scope the claim, or drop net for simulate.

## CONFIRMED but require same-uid code OUTSIDE the sandbox (claim-calibration, NOT agent-reachable)

The sandboxed agent CANNOT reach the store (verified: tmpfs over store, daemon socket absent
in-world), so these are not reachable by the untrusted agent. They matter only against an
attacker who already runs as the user outside the sandbox — who can also just replace the
binary. Still, they mean specific written claims are stronger than the cryptography supports.

- **E1 [HIGH-as-claim] Evidence chain is hash-only — no signature, no external anchor.** Verified:
  zero ed25519/hmac/signature anywhere in runtime. `log --verify` recomputes hashes over a
  fully user-writable SQLite store rooted at a constant zero-hash; a same-uid process can
  truncate or rewrite history and it re-verifies clean. The user already ships Ed25519 +
  hash-chain ledgers in ATTEST/ANUBIS and SIA — anchoring WORLDLINE's chain head into one of
  those (or signing receipts) would make "chains replay through the proved kernel" true against
  same-uid tampering. Today it means "self-consistent recomputation," which is less than the
  wording implies.
- **E2 [HIGH-as-claim] "SPARK-proved kernel authorizes the collapse" oversells.** The kernel is a
  proved hash-and-compare library (SHA-256 math, link hashes, an equality predicate). Verified:
  the C API exports only 7 hash/compare functions; the transaction state machine actually
  enforced at runtime is a Python dict + a SQLite CHECK, not the proved `Transitions` unit.
  Several `expected_*`/`candidate_*` pairs fed to `collapse_decide` are the *same Python
  variable* passed twice (owner/parent/staged in prepare — I read them directly), so those
  comparisons are tautological. The `renameat2` that mutates PRIME is a separate Python call not
  structurally forced to follow the verdict; two PRIME-writing paths (checkpoint publish, root
  register/remove) never consult the kernel at all. Accurate wording: "a proved-correct hash
  kernel supplies the equality checks; Python decides what is compared and enforces the
  lifecycle."
- **E3 [MEDIUM] `invariantPreservation: PROVED` is forgeable.** Verified: `core.py:89` selects the
  library from `WORLDLINE_CORE_LIB` first; the manifest is an unauthenticated JSON next to it;
  substitute both and every receipt says PROVED. Also a load-vs-hash TOCTOU (dlopen at start,
  file hashed at receipt time). Pin an expected hash in code or sign the manifest.

## REAL BUGS (integrity/robustness; bounded impact; worth fixing)

- **B1 [MEDIUM] inotify watcher not rebuilt after collapse/return** (controller: `_refresh_watcher`
  only at init/register/remove). After the first collapse it watches swapped-away inodes, so the
  `PRIME_CHANGED_DURING_CAPTURE` generation guard and dirty/reconcile tracking go stale.
  **Downgraded from the auditor's CRITICAL:** the authoritative guard is the commit-time content
  re-hash `_capture_current_roots()` vs `beforeRoot` (transaction.py:284), which is
  watcher-independent and still works — PRIME integrity is preserved; only defense-in-depth
  degrades. Fix: call `_refresh_watcher()` at the end of collapse/return commit.
- **B2 [MEDIUM] Crash windows in root register/remove** (roots.py:199-208, 388-432). SIGKILL mid-
  `os.rename` during registration can leave the user's directory inside the store under a UUID
  with no `roots`/transaction row and no recovery scan → user must hand-locate it. SIGKILL mid-
  removal can leave a registered root that no longer routes through `live`, so later collapses
  "commit" without touching the user's real files. Add a generations/ orphan scan on startup and
  a symlink-chain invariant check per registered root.
- **B3 [MEDIUM] Recovery dual-write can wedge startup.** `_set_state` writes JSON then the DB row;
  a crash between them makes `_load_record` raise on every boot (fail-closed but
  unrecoverable-by-design). Same for a non-idempotent `publish_checkpoint`/`set_prime` window.
- **B4 [MEDIUM] No cross-process daemon mutex** (grep: no flock/pidfile). A second `worldlined`
  unlinks the live socket and binds its own; two daemons over one WAL DB can interleave
  collapses, each self-consistent, violating "exactly one world commits." Add an flock/pidfile.
- **B5 [LOW] Power-loss torn PRIME:** staged payload subtree dirents are never fsynced before the
  exchange (only file contents + parent dirs), and recovery re-hashes survivors without
  comparing to `stagedRoot`. **B6 [LOW]** crash between COMMITTED and receipt-append loses the
  receipt permanently (recovery only replays PREPARED/AUTHORIZED). **B7 [LOW]** DENIED/ABORTED
  staging dirs never cleaned → store grows by a full PRIME copy per conflicted attempt.
  **B8 [LOW]** `validate_alias` permits `.`/`..`/`PRIME`/control chars (harmless: UUID-keyed
  paths, parameterized SQL, argv-not-shell, PRIME short-circuits — cosmetic/log-spoof only).
  **B9 [LOW]** `scripts/pick_candidate.py` crashes to exit 1 (not the documented 3) on NaN in a
  hostile race.json. **B10 [LOW]** worldline `install.sh` non-atomic `mv` swap leaves a window
  with no binary; verify→install gap on the .so.

## HOLDS — verified strong (the claims that are true)

- **Filesystem containment of agents.** Real files are the RO lower (agent runs get a materialized
  *copy*, not the live inode); writes land in the overlay upper; PRIME lives behind a symlink
  chain in managed storage, never bind-mounted into a world. `$HOME` masked by tmpfs; `~/.ssh`,
  `~/.config`, Wayland/DBus/ydotool/XDG sockets all absent; the **daemon socket is unreachable
  from inside a world** (so an agent can't drive a collapse or fork-bomb the daemon); namespace-
  root neutered (`--cap-drop ALL`, `--disable-userns`, `--uid 0` mapping to the real uid
  outside the namespace, `NoNewPrivileges` set by bwrap itself and again on the transient unit
  — verified in-world: uid=0, CapEff=0, NoNewPrivs=1).
- **Symlink / hardlink / traversal escape is blocked.** `_safe_symlink_target` (manifest.py:76-87)
  rejects NUL/absolute/`..`-escaping targets at capture AND materialize AND the mandatory staged
  recapture; a payload `evil -> ~/.ssh` is caught (`EXTERNAL_SYMLINK`). Hardlinks outside the
  root rejected; walks never follow symlinks; cross-device/special files rejected.
- **Atomic collapse is genuinely one syscall for all roots.** Roots are symlinks in one `live`
  dir swapped by a single `renameat2(RENAME_EXCHANGE)`; no per-file window. Payload is re-hashed
  vs `stagedRoot` and PRIME re-hashed vs `beforeRoot` immediately before the exchange; a
  DB/world tamper between prepare and commit is denied. Marker-based recovery deterministically
  distinguishes committed from aborted and fails closed on ambiguity.
- **Daemon access control.** Socket 0600 + `SO_PEERCRED` uid check per connection + 16 MB NDJSON
  cap + strict request envelope. **Global config owner-only is enforced at startup** (verified:
  a world-writable config makes the daemon refuse to boot, socket never published).
- **No shell anywhere** (no shell=True/eval/exec/os.system); **SQL fully parameterized**; QML and
  CLI build argv arrays. Docker path is host-side and label+mount scoped; docker socket absent
  from worlds. Checks run with no creds and no `~/.local/bin` (confirmed).
- Kernel proof reproduces 130/130 (0 unproved, 0 pragma Assume); installed library == manifest
  hash; ctypes ABI has real bounds checks (NUL/len/2^61 cap, 32-byte digest validation).

## Status (fixed in 1.0.1 — see CHANGELOG.md)
- **C1 [FIXED]** git RCE — `-c` hardening + hardened env in `GitAdapter._run`; verified the exact
  `capture()` argv fires nothing while an unhardened control still pops.
- **B1 [FIXED]** watcher rebuilt after collapse/return.
- **B4 [FIXED]** daemon singleton `flock` (`DAEMON_ALREADY_RUNNING`); verified a second daemon is refused.
- **B7 [FIXED]** denied/aborted staging reclaimed.
- **B8 [FIXED]** operator alias validation (`validate_user_alias`): control chars, length,
  reserved `PRIME`/`prime-*` rejected.

## Remaining (deliberately not code-changed)
1. **C1 residual** — sandbox the git inspection for the narrow textconv/filter-via-repo-config
   vector (the `-c` set closes the confirmed and common vectors).
2. **C2 / C3** — network-egress policy for agent/simulate worlds (design call; documented in SECURITY.md).
3. **E1** — anchor the chain head into ATTEST/SIA (you own the signing primitives); **E2/E3**
   wording is now corrected in SECURITY.md; a library hash-pin would further harden E3.
4. **B2** — register/remove SIGKILL crash-recovery (startup orphan scan + symlink-chain invariant).
5. **B3, B5, B6, B9, B10** — remaining LOW robustness items as cleanup.
