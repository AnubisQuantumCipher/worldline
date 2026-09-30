# WORLDLINE security model

This document states plainly what WORLDLINE defends against, what it does not, and where its
claims end. It is deliberately conservative: a guarantee is listed under "Holds" only if it was
verified in code or demonstrated, and everything else is named as a limit rather than left
implied. Last reviewed 2026-09-30, against release 1.9.1. Every review of WORLDLINE,
including `SECURITY-AUDIT-2026-09-02.md`, was carried out by AI agents and checked against
mechanical evidence (proofs, contract pins, reproductions, exact-commit assurance); no human
security audit is claimed. The reviews since 2026-09-02 are summarized, release by release, in
`CHANGELOG.md`.

## The adversary WORLDLINE is built for

The primary adversary is **the coding agent running inside a world** — possibly prompt-injected
by a hostile mission or by content in the repository it reads. WORLDLINE's job is to let that
agent work without being able to touch the operator's real files or commit anything without an
authorized, atomic collapse.

Since 1.5.0 there is a second one: **the candidate's code while it is being examined.** A check
declared with the `private-evaluator-v1` profile treats candidate bytes as data: its examiner is
staged from PRIME, and the candidate programs it starts run under identities that cannot reach
the report it writes. Ordinary (`legacy`) checks run the examiner and the candidate code it
starts under one identity; their verdict is the supervisor-observed exit status, and their
report files are never admissible.

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
  capture, materialize, and the mandatory staged recapture (`EXTERNAL_SYMLINK`). Since 1.6.0
  this includes any target whose `..` follows a name: after `x -> .`, the kernel resolves
  `x/../..` above where lexical normalization places it. Before 1.6.0, such a target could
  normalize inside a root and resolve outside it. Hardlinks
  outside a root are rejected; walks never follow symlinks; special/cross-device files are
  rejected. Agent worlds, checks, and shells run as the real uid inside the user namespace
  (the only uid mapped either way); `simulate` futures keep namespace root, and either identity
  is neutered (`--cap-drop ALL`, `--disable-userns`, `--unshare-user`, `NoNewPrivileges`). The
  private evaluator (below) is the one exception: it maps two subordinate identities besides the
  operator's, and it neuters them differently.
- **Network containment (1.2.0, opt-in).** `network.policy: allowlist` gives each agent's world
  an empty network namespace whose only exit is a daemon-side proxy that connects to the
  adapter's provider hosts and `network.allow`, and records every refusal on the world's
  evidence. This closes the egress gap for everything that speaks HTTP through the proxy
  environment; it does not stop a process that ignores those variables from *trying* (it simply
  has no route), and it does not inspect the traffic it does allow. `none` removes the door
  entirely. `shared` (the default) keeps the historical behaviour and the historical caveat. The
  policy governs the agent's own sandbox only (limit 1); private-evaluator roles get their own
  empty network namespace under every policy.
- **Anchored receipts (1.2.0).** The receipt chain is additionally written as an Ed25519-signed
  Custos-format ledger and mirrored to `anchor.exportPath`. This does not defend against an
  attacker who holds the signing key (a `0600` file in WORLDLINE's config directory) and can
  reach the export location; it raises the cost from "rewrite one SQLite file" to "rewrite it,
  re-sign every entry, and rewrite the external copy", and `attest verify-custos` checks the
  chain with proved code independent of this runtime.
- **Credential projection.** Each builtin adapter binds its credential file read-only at its
  home path; apart from the `readonlyHomePaths` above, nothing else of `$HOME` is visible. omp
  is the one exception: it opens its whole state database read-write at startup, so the world
  gets a per-world private copy (SQLite backup, `0600`, under the world's runtime) and the host
  database is never mounted. Claude Code's hooks are disabled inside a world
  (`--settings '{"disableAllHooks":true}'`): they are host desktop integrations, and a hook that
  exits 2 silently blocks the mission.
- **Atomic, crash-consistent collapse.** All roots swap in a single `renameat2(RENAME_EXCHANGE)`
  of the `live` mapping; PRIME is re-hashed against `beforeRoot` and the staged payload against
  `stagedRoot` immediately before the exchange; a generation marker inside the swapped directory
  makes crash recovery deterministic and fail-closed. A second daemon is refused
  (`DAEMON_ALREADY_RUNNING`).
- **Daemon access control.** Socket is `0600` with an `SO_PEERCRED` uid check per connection and
  a bounded request envelope. The global config is rejected unless it is a regular, owner-owned,
  non-group/other-accessible file — the daemon refuses to start otherwise.
- **Managed roots resolve through the store (1.7.0).** Capture, validation, policy loading,
  prune and `why` read a root's content through the store's own `live/<root key>` mapping,
  never through the registered path. That path is a link in a directory the operator owns.
  The link must route through the mapping and the mapping must resolve inside the store, or the
  root is refused (`LIVE_MAPPING_BROKEN`).
- **Dedicated-account client mode (1.7.0).** Opt-in only, through the daemon's environment:
  exactly one `WORLDLINE_CLIENT_GID` and at least one `WORLDLINE_CLIENT_UIDS` (distinct ASCII
  decimal uids, never 0). Anything else refuses at startup with `INVALID_CLIENT_MODE`, and so
  do a runtime directory that overlaps the store and a group the daemon is not in.
  - The runtime directory is `0750`, the socket `0660` and `status.json` `0640`, all with that
    group.
  - The daemon serves its own uid and the listed ones and refuses every other peer with
    `PEER_UID_MISMATCH`.
  - Clients can traverse to PRIME's content, but cannot list any store directory: the path to it
    is `0710` with the group, and everything else stays `0700`. The data directory is the gate:
    it opens only at daemon start after the content check, and closes if content turns out unsafe
    while the daemon runs. Since 1.7.1 `worldlined` takes a lock in the store's state directory
    before it validates or builds anything and closes the gate once it is the store's only daemon,
    so a second start neither writes a running daemon's store nor touches its gate, as long as the
    lock file is in place (removing it, which only the daemon account or root can, lets a second
    daemon with another runtime directory start) and no daemon starts at the same moment (the
    check and the close are two steps). Whether the lock is held is read from the
    kernel's lock table, which counts a lock its owner made unreadable, and a lock the start cannot
    observe (not in the table as it sees it and unreadable to it, or behind a state directory it
    cannot search) is taken as held. The gate is left closed by a start or configuration that
    refuses after that lock, by a lock that cannot be taken or written while the start can see
    that no process holds it (a lock path that is not a regular file, a state path that is not a
    real directory of the daemon's, a full disk), and by a daemon that fails in Python. It is left
    as it was by a daemon that stops cleanly or is
    killed outright, until the next start, which closes it and checks again before opening it; by a
    configuration whose store directories cannot be named (a relative XDG path), which refuses
    before the lock; by a start that cannot observe the lock, whether or not a process holds it,
    which logs that it left the gate; and by a start refused on a lock file hard-linked to another
    store's held lock, which cannot be told from this store's own.
  - Content they can reach must be owned by the daemon and carry no other-write bit, no
    group-write bit outside the daemon's own group, no extended ACL (any `system.*acl*` xattr), no
    file capability (`security.capability`), and no setuid, setgid or sticky bit
    (`CLIENT_MODE_UNSAFE_CONTENT`; the group, ACL and capability rules are 1.7.1). An entry whose
    xattrs cannot be read refuses. This is checked at collapse and return prepare, when a
    generation is published, and at daemon start. A client group equal to the daemon's primary
    group is refused, and so is a named member of the client group who is in the daemon's group.
  - `live` may hold only mapping links (and its marker), each a link into a generation or
    transaction payload; the routing check compares the live directory by device and inode,
    resolved in the daemon's own namespace (1.7.1).
  - A refused registration moves the operator's directory back; only reconcile and remove, which
    publish copies, discard a refused generation (1.7.1).
  - `init`, `root add`, `root remove` and `switch` refuse clients
    (`OPERATION_NEEDS_DAEMON_ACCOUNT`).
  - The client checks the socket's `SO_PEERCRED` against `WORLDLINE_DAEMON_UID`, or its own
    uid, before sending anything.
  - Without the environment, the daemon is owner-only as before.
- **The daemon's HOME and store are masked in every ordinary sandbox (1.7.0).**
  - Agents, checks, services, `simulate`, `shell` and the materializers all see the daemon's
    HOME as an empty tmpfs.
  - A data, state, config or runtime directory under a system path (bound, or overlaid by
    `simulate`) and outside that HOME is covered by its own tmpfs, mounted after the system
    overlays.
  - The private evaluator binds only `/usr`, `/etc` and the library directories.
- **No shell, parameterized SQL.** No `shell=True`/`eval`/`exec`; every subprocess is an argv
  list; every SQL statement that carries data uses placeholders (the only interpolated SQL sets
  `PRAGMA user_version` from the runtime's own integer schema constants).
- **Evidence freshness (1.3.0; executed-verifier identity, 1.5.0).** A candidate's acceptance
  evidence is bound to the policy, checks, verifier bytes, engine and execution configuration it
  was evaluated under (`validationContext` inside the hashed evidence manifest). Promotion
  compares that requirement identity with the one the CURRENT PRIME imposes, at prepare and again
  at the serialized commit boundary, and the proved kernel refuses a mismatching pair
  (`EVIDENCE_STALE`, kernel decision `VALIDATION_CONTEXT_MISMATCH`). Evidence from another world,
  a corrupted or missing context, or a candidate that rewrote/redirected/shadowed a verifier its
  evidence ran is refused by name (`EVIDENCE_CONTEXT_INVALID`, `EVIDENCE_CONTEXT_MISSING`,
  `VERIFIER_MODIFIED_BY_CANDIDATE`) — for the verifiers the engine binds: the files a check's
  argv names, their directory, or the declared `verifiers` globs. A check that names no existing
  file (`make test`, `-m pytest`, `sh -c …`) or whose argv path lies inside its own `covers`
  binds no verifier; the engine WARNS (`doctor.policy.warnings`) and does not refuse — declare
  `verifiers` for such checks (a `private-evaluator-v1` check without them is refused when the
  policy loads). Staged bytes that differ from the tested candidate are refused
  (`STAGED_UNTESTED`) unless the current checks pass over the staged result itself. Checkpoint
  returns need no candidate evidence; re-application of a candidate obeys the collapse rules.
  Legacy candidates are revalidated explicitly (`worldline revalidate`), never accepted silently.
  A verifier's directory (or the declared `verifiers` globs), declared services and the
  forwarded check environment are part of the identity; a top-level verifier without a
  declaration binds only itself and is warned about. Since 1.5.0 bound verifiers execute from a
  staging copy taken out of PRIME, not from the candidate's overlay, and the kernel also refuses
  unless every required check has an execution record whose provenance is established and the
  verifier identity that executed equals the one the policy authorizes
  (`EXECUTION_EVIDENCE_INCOMPLETE`, `VERIFIER_EXECUTION_IDENTITY_MISMATCH`); the two identities
  come from different producers (the policy's resolved verifier list and the check runner's
  execution record). Retained reproducers: `tests/test_freshness.py` (classes A–L).
- **Resource admission (1.4.0).** Every path that starts supervised work — the agent world, each
  check (the private evaluator's unit included), a declared service and its health probe, and
  `simulate` — asks one admission authority first and holds a reservation while it runs.
  Admission is `observe → lock → account → reserve → authorize` under one exclusive lock, and its
  refusals are named (`RESOURCES_UNAVAILABLE`, `RESOURCE_STATE_UNKNOWN`,
  `RESOURCE_POLICY_INVALID`, `RESOURCE_LIMIT_EXCEEDED`); a state that could not be measured is
  never reported as insufficient. Ceilings go on the unit and are read back from the kernel's
  own cgroup files. The enforced policy is part of `requirementHash`; admission state and
  telemetry are never hashed. It does not guarantee completion, does not police processes
  WORLDLINE did not start, and does not make evidence correct because it was produced under a
  satisfied budget. The cgroup is a budget for a workload that is not trying to leave it: a
  same-uid workload can create a sibling cgroup and leave both the ceiling and the accounting,
  and it is the sandbox that stops one that tries. That escape was shown to fail inside the
  ordinary world/check sandbox, where user namespaces are disabled; this document does not
  extend the claim to the private evaluator's roles (limit 5).
- **Repository inspection runs in a sandbox (1.7.0, tightened in 1.7.1; hardened since
  1.0.1).** Registered repos and world repos are untrusted. Every host-side `git` process runs in
  its own bubblewrap sandbox: no network, no capabilities, no nested user namespace, read-only
  system directories, a bounded tmpfs, a task limit, and nothing of the host except the
  inspected root (read-only) and a private scratch directory. Only a repository's top-level
  directory, with `.git` a real directory inside it, is inspected; a linked worktree, a `.git`
  link or a subdirectory refuses by name, because git would need directories that content inside
  the root names (1.7.0 bound them, and a `.git` file naming another repository put its content
  into a world's facts). The index is read on the host at `<root>/.git/index` through one
  descriptor that refuses links, and the bytes hashed are the bytes copied. A sandbox that does
  not start refuses (`GIT_SANDBOX_UNAVAILABLE`) instead of being read as a repository fact; only
  bubblewrap's own status report decides that, not git's stderr, which a repository's filter can
  write. git must resolve inside the bound system directories. Anything a repository's
  configuration makes git run, such as a filter driver, reaches nothing.
  Before 1.7.0 a `-c` denylist was the only defence, and it could not name filter drivers; that
  list remains as a second layer. Memory and tasks used inside the sandbox are charged to the
  daemon's cgroup: the shipped unit's `MemoryMax=4G`, `MemorySwapMax=0` and `TasksMax=4096` bound
  them, inspection runs with OOM score 1000 (code a repository makes git run can lower it toward
  the unit's floor), and `OOMPolicy=continue` keeps an OOM kill in the cgroup from stopping the
  daemon. A git killed by any signal, or reporting that a process it started was killed (`died of
  signal`, or a filter that failed with a status above 128), refuses the inspection instead of
  becoming a fact; a helper other than a filter killed by SIGPIPE, SIGINT or SIGQUIT leaves no
  report and cannot be told apart.
- **Release assurance of an exact commit (1.3.0; private host roster, 1.5.0).** A version is
  published only after `scripts/release_gate.py` accepts the full assurance report of the tagged
  commit, produced in the same workflow run (`docs/release-process.md`). One roster
  (`scripts/assurance_contract.py`) defines the required steps: checkout identity, a clean build
  tree, build, Ada tests, Ada fuzz, the Python suite with the private host integration cases
  enabled, a named private-host subset that must run with zero skips (`PRIVATE_HOST_CASES` in
  `scripts/assurance.py`: role separation, worker timeout and output limits, report forgery,
  revalidation and promotion, and both case-lease cases), the two-arm evaluation-domain gate, the
  SPARK proof gate and the proof-manifest check. The evaluation-domain gate passes only if the
  candidate build holds and a pinned, deliberately unreleased counterexample build still
  exhibits its known defect, so an instrument that stopped working cannot pass as a fix. A
  missing or failing step fails the run.

### Private evaluation (`private-evaluator-v1`, 1.5.0; candidate principal and case leases, 1.6.0)

- **Declaring it.** A `private-evaluator-v1` check must use a report format (`junit`,
  `gnatprove`, `worldline-benchmark-v1`), declare its trusted verifier files in `verifiers`, and
  name no candidate `result` path. Private checks must follow every ordinary check
  (`CHECK_PROFILE_ORDER_INVALID`), and the profile and the check order are part of the policy
  identity. The examiner must be `/usr/bin/python3` running a script inside the read-only
  verifier mount (`/run/worldline-verifiers`).
- **Trusted bytes from PRIME; candidate input frozen.** The examiner's verifier files are staged
  from PRIME — the checkpoint the world was forked from, or the current PRIME for a
  revalidation — never from the candidate's overlay. Before any examiner can write, the daemon
  copies the candidate into daemon-owned storage (the *candidate snapshot*, re-verified before
  use), and the backend copies that snapshot again, with change detection, into a *frozen* tree
  that accepts only ordinary directories and singly linked regular files (links, special files,
  xattrs, special permission bits, mounts and entries that change during the copy are refused).
  The examiner sees the frozen tree read-only; every worker or candidate run gets a disposable
  copy whose identity must equal the frozen one. Private-evaluator writes are never promoted:
  the pre-check snapshot becomes the payload.
- **Three principals in one mapped user namespace.** The daemon launches only its own
  bootstrap, whose bytes must equal the installed engine's, as a transient unit under
  `unshare --user --map-auto --map-root-user`. It is the one unit that runs with
  `NoNewPrivileges=no`, so that `newuidmap`/`newgidmap` can install the operator's subordinate
  ID ranges; the daemon reads that property back from the service manager and records it before
  the bootstrap may continue. Inside, the examiner is namespace uid/gid 0 (mapped to the
  operator's own identity), the worker 1 and the candidate 2. The bootstrap refuses unless 0
  maps to the operator and 1 and 2 map to two different host identities that are neither host
  root nor the operator. Every role is started through bubblewrap without a new user namespace
  (all three share the bootstrap's) and through `setpriv` with no new privileges, its own uid
  and gid, cleared supplementary groups, and cleared bounding, inheritable and ambient
  capability sets.
- **Every role is observed before it runs anything.** A fixed helper in each role first reports
  its uid and gid, `/proc/self/status` (`Uid`, `Gid`, `Groups`, `NoNewPrivs` and the effective,
  permitted, bounding and ambient capability sets), its uid/gid maps and namespace identities,
  and whether the report, examiner-broker and worker-broker paths exist. The supervisor
  validates that frame before acknowledging it; no workload code runs first, and later output
  is data, never observation. A role is refused unless it has exactly its own uid and gid in all
  four positions, `NoNewPrivs` is 1, all four capability sets are empty, it has no supplementary
  groups, the report and examiner-broker paths exist only for the examiner, and the
  worker-broker path only for the worker. After the examiner exits, the run is refused unless
  every role's maps equal the bootstrap's and every worker's and candidate's PID and mount
  namespaces differ from the examiner's.
- **The examiner alone writes the report.** For each invocation the daemon creates a new
  owner-only report directory holding a binding marker (run, check, candidate identity, verifier
  identity) and binds it only into the examiner, at `/run/worldline-report`, next to the
  examiner broker socket (`0600`; any peer but namespace uid/gid 0 is refused) and the optional
  GNAT toolchain. Workers and candidates get none of the three. When the supervised run has
  returned, the daemon collects a fixed-name, singly linked regular file of bounded size,
  refusing one whose binding does not match or that changed while being read, and retains the
  bytes and their digest with the result.
- **Report admission.** A JUnit, GNATprove or benchmark report counts only when finalization
  verifies, from the recorded facts: the `private-evaluator-v1` profile and a result produced by
  the daemon outside the sandbox; a supervised, started unit that the manager did not stop and
  whose exit status agrees with the examiner's and the bootstrap's; the recorded
  `NoNewPrivileges=no` bootstrap property; a boundary record with no error and with
  `rolesCompleted` and `reportMountExclusive`; a report bound to this run, check, candidate
  snapshot and executed verifier set, whose retained bytes match the collected size and digest;
  an intact executed verifier set; an examiner observation and every worker and candidate
  observation passing the per-role pins above; every worker and candidate in the examiner's user
  namespace, with the examiner's maps, in different PID and mount namespaces; and no candidate
  observation sharing a worker's UID or GID. Anything else makes the report `UNTRUSTED`, and an
  `UNTRUSTED` report cannot make its check admissible. A boundary error refuses the whole run
  (`PRIVATE_EVALUATOR_BOUNDARY_FAILED`); the check then records a refused result channel, which
  is never a completed evaluation. A required check that is not admissible leaves the world
  `DEGRADED`. When a promotion is prepared the classification is recomputed from the raw result,
  and an `UNTRUSTED` report makes the execution evidence incomplete, which the kernel refuses.
  Legacy report files, which live in the candidate-writable overlay, are never admissible.
- **Candidate principal (1.6.0).** `candidate.run` still starts its process as the worker. An
  examiner can instead start candidate processes as the candidate principal
  (`candidate.run_isolated`, `start_isolated`, `stream_isolated`, `wait_isolated`,
  `signal_isolated`, `teardown_isolated`); every such session must be torn down before the run
  ends, or the run is refused. Finalization accepts a `candidate` observation only with the
  candidate's identity, and refuses any report in which a candidate observation shares a
  worker's UID or GID.
- **Worker broker and scoped case leases (1.6.0).** A worker gets its own broker socket at
  `/run/worldline-worker-broker.sock`, bound into no other role, served only while a worker is
  active, and checked on every connection with `SO_PEERCRED`: any peer other than the worker's
  uid and gid 1 is refused. A harness in the worker can use it to open a *case lease* on a real
  directory (not a symlink) strictly inside — not equal to — its copy of the candidate roots,
  not overlapping another open lease, up to `MAX_CASE_LEASES` (256) leases per run. The backend
  copies the case into a separate *candidate view* owned by the candidate principal, mounts it
  at the same logical path in the candidate's own mount namespace, and starts candidate commands
  there. A start takes the ordinary argv, cwd and timeout validation, at most 2048 bytes of
  stdin, and no environment beyond `PYTHONHASHSEED` (decimal digits) and
  `PYTHONDONTWRITEBYTECODE=1`; a wait blocks for at most 2000 ms; the only signals are `SIGTERM`
  and `SIGKILL` to the candidate's process group; teardown kills that group and waits for it.
  Starting a candidate, copying out and closing all require that the worker's view still matches
  the last copied generation. Worker edits reach the candidate view only through an explicit
  copy-in that names the current generation while no candidate handle is live and no output is
  uncopied; candidate output is copied back only after every candidate handle of the case has
  been torn down. Case copies accept only ordinary files, directories and symlinks whose target
  stays in the case with no `..` after a name, and refuse hardlinks, special files, xattrs,
  special permission bits, nested mounts (same-device bind mounts included) and observed
  mutation. **Any protocol
  violation stops the broker and refuses the whole run** — a malformed request, a refused peer,
  a lease outside the worker copy or over the cap, a variable outside the allowlist, a link that
  escapes, a copy that changes, a worker view that moved, or a session or lease still open at the
  end — whatever the examiner does with the error; worker timeouts and output overruns refuse
  it the same way. Every candidate start is recorded in the boundary evidence with its role
  observation and lease handle, and every lease with its open, copy, start, teardown and close
  events. Two retained adversarial campaigns, both required with zero skips by the private-host
  roster, attack this protocol:
  - `tests/test_private_lease_protocol_campaign.py` covers overlap, ordering, stale-generation
    replay, handle reuse, output limits and request fuzzing;
  - `tests/test_private_lease_fault_campaign.py` covers role deaths, copy-out failures, extreme
    trees, nested namespaces and `/proc`.

  Each scenario must end as a clean, complete run or a whole-run refusal. A worker's case
  directory must be left exactly as it was before the operation or exactly fully copied.
- **What a candidate process cannot reach.** A candidate process gets no report,
  examiner-broker, worker-broker, verifier or toolchain mount (the first three are checked in its
  role observation). It runs as its own uid and gid with no capabilities and no supplementary
  groups, in its own PID, IPC, UTS, network and mount namespaces (only the user namespace is
  shared by the three roles), with a private `/tmp` and `/run` and a cleared environment. It
  sees `/usr`, `/etc` and the top-level system directories read-only, its own copy of the
  candidate input — fresh per call, or kept for the life of its lease — and, for a lease, the
  case view. The 1.6.0 claim is exactly this: the candidate principal protects the examiner and
  worker processes and their mounts from candidate code.

## Limits — known, and where the claims end

These are not defended, by design or by current architecture. Treat them as the boundary of the
trust you place in WORLDLINE.

1. **The network is contained only for the agent, only under a restrictive policy, and agent
   worlds mount real credentials.** Under the default `network.policy: shared` an agent's world
   uses the host network, and under every policy each builtin agent's world read-only-binds the
   agent's real credential file (e.g. `~/.claude/.credentials.json`; omp gets a private
   per-world copy). A prompt-injected agent under `shared` can therefore exfiltrate that
   credential or reach host-local and LAN services; under `allowlist` it can still send
   anything, the credential included, to every allowed host, and the proxy does not inspect the
   traffic it allows. If you run agents on untrusted missions or untrusted repository content,
   assume the mounted credential and anything the world can reach are exposed. The policy is
   applied to the agent's own sandbox only: legacy checks, declared services and their health
   probes, and `simulate` run with the host network under every policy, so candidate code that a
   legacy check executes has the host network even under `allowlist` or `none`.
   Private-evaluator roles have no network. `simulate` contains filesystem effects only; its
   network side effects are real.

2. **The evidence chain is tamper-evident against the agent, not against you.** Receipts and the
   causal/receipt chains in the store are SHA-256 hash chains. The sandboxed agent cannot reach
   the store, so it cannot forge them — that is the property that matters for WORLDLINE's
   adversary. But any process running as your uid *outside* the sandbox can rewrite the store and
   the chain re-verifies clean, exactly as it can replace the binary or delete your files.
   `worldline log --verify` proves internal self-consistency, not authenticity against a same-uid
   attacker. Since 1.2.0 every committed receipt (not the causal chain) is also appended to the
   Ed25519-signed anchor ledger, which raises the cost of a rewrite without removing it: the
   signing key is a `0600` file of that same uid under WORLDLINE's config directory, so the
   attacker can re-sign, and a rewrite is detectable only against a copy at `anchor.exportPath`
   that the attacker cannot write. `anchor.exportPath` is unset by default.

3. **"Proved" describes the kernel, not an attestation of the running system.** The SPARK proof
   (`proof-manifest.json`: 251 checks, 0 unproved, 0 justified, 0 `pragma Assume`) covers the
   kernel library: hashing, identity and link functions, the world, evaluation and transaction
   state machines, the collapse decision, and (1.9.0) the decoding and validation of the collapse
   request as it arrives over the C ABI. `Decide`'s postcondition makes `Authorized` exactly
   equivalent to `All_Hold`: a `VALID` candidate; conflicts and foreign managed writes both
   measured and none found; the PRIME watcher's generation unchanged across the decision and
   every registered root watched; every identity pair present and equal — parent, evidence
   subject, base, delta, root set, and at commit the staged root; and the evidence obligation of
   the mode (a candidate evaluation against the current requirement, with a complete roster and
   equal declared and executed verifier identities, or for a checkpoint return a witness equal
   to the checkpoint), in both modes by evidence that examined exactly the bytes that would go
   live. Since 1.9.0 each identity has its own type and explicit presence: two absent values are
   never equal, and nothing absent or unmeasured is ever `Authorized`. The manifest's own
   boundary lists the C entry points (pointer dereference, exception handlers, hashing
   marshalling, and the decoding and validation of evaluation observations), the Python/QML
   boundary, and OS syscalls and filesystem behaviour as not proved. Because GNATprove counts a
   whole postcondition as one check, the contracts are also pinned by digest in
   `verify_proof_manifest.py`, so a weakened contract is refused rather than counted. Everything that decides *what* is hashed,
   compared and enforced is Python, covered by tests rather than proof: manifests, requirement
   and content identities, what enters the execution-identity comparison, report collection and
   admission, resource admission, the sandbox, and the whole private evaluator — its namespace
   setup through `unshare`, `newuidmap`/`newgidmap`, bubblewrap and `setpriv` under systemd, the
   role observations, both brokers, the lease protocol and both copy protocols. The kernel proves
   only that unequal or absent identities are never `Authorized`; which values reach it is the
   runtime's choice. 1.9.0 retired the owner pair, which was one computed value passed on both
   sides and so constrained nothing; each remaining pair is produced from two different records,
   named in the kernel's request comments, but a runtime that passed one value to both sides
   would still satisfy the proof. Foreign managed writes are measured (1.9.0) by comparing a
   capture of live PRIME with the components the PRIME record states: a write nothing reported is
   refused, and marks PRIME for reconciliation. A write the watcher reported becomes a PRIME
   generation rather than a foreign write, a write made and undone between two captures is not
   seen, and ownership (uid/gid) is not part of a manifest, so a `chown` or `chgrp` is not
   measured at all. Freshness is identity comparison, not re-execution — a `PASS`
   revalidation or staged validation is evidence about the bytes it names at the time it ran, in
   the same sandbox finalization uses, and stored contexts live in the same same-uid-writable
   store as everything else. Since 1.1.0 the transaction lifecycle (PREPARED → AUTHORIZED →
   COMMITTED, DENIED sticky) is consulted from the proved unit on every state change, and the
   kernel's parent comparison receives the store's parent identity rather than the candidate's
   own claim on both sides. `invariantPreservation: PROVED` in a receipt means the on-disk proof
   manifest matched the library at receipt time; the library is selected by
   `WORLDLINE_CORE_LIB`/package path and the manifest is unauthenticated, so a same-uid attacker
   can make it report `PROVED` for a substituted library. Read it as "the proved hash kernel is
   in use per its unsigned manifest," not "the running system is proved correct."

4. **Private evaluation separates processes; it does not make the verdict independent of the
   candidate.** The candidate principal protects the examiner and worker processes and their
   mounts from candidate code. It does not make an examiner's or harness's judgment independent
   of the candidate outputs it chooses to read: the verdict is whatever trusted examiner logic
   concludes from candidate exit statuses, streams and files, and an examiner that copies
   candidate-written XML or JSON into its report hands the verdict back to the candidate. Role
   isolation does not establish that examiner logic is correct, and it does not make candidate
   imports into the examiner safe: code the examiner imports from the candidate tree runs inside
   the examiner, with the report and the broker in reach (the examiner starts with only the
   standard library and the verifier mount on `sys.path`). A worker is trusted only as far as the
   code it is told to run: its executable must be a system binary or a file in its copy of the
   frozen candidate input, so what a worker runs from that copy is the candidate snapshot's
   bytes, not the staged verifier's, and it runs with the worker's identity and broker. The
   examiner's stdout and stderr are recorded as candidate-reachable data.

5. **What the private backend does not isolate, freeze or keep to itself.**
   - Nested user-namespace creation is not disabled for the examiner, the worker or the
     candidate — every boundary record says so — whereas ordinary worlds and checks run with
     `--disable-userns`. The fault campaign attacks this. On the reference host (Linux 7.2):
     - a candidate can create a nested user namespace, map itself to root inside it, create a
       mount namespace and mount tmpfs over its own view;
     - mounting `/proc` is refused.

     The campaign asserts that nesting reaches no broker socket, report directory, verifier or
     toolchain mount, or worker process, and that a mount made inside the nested namespace does
     not change what copy-out collects. A host whose kernel refuses the nested namespace
     records the refusal and is held to the same assertions. This document therefore does not
     extend 1.4.0's finding that a workload cannot leave its cgroup budget from inside the
     sandbox to the private roles.
   - A candidate sees only its own PID namespace, whose PID 1 is bubblewrap's init. That
     process runs with the bootstrap's identity (namespace UID 0). The fault campaign asserts
     that a candidate cannot read that process's environment or signal it, and cannot read the
     environment of any process outside its own UID. No worker process is visible to it.
   - A case copy is not an atomic snapshot: its metadata comparisons detect changes during a
     copy, but cannot replace a filesystem snapshot against a writer that deliberately races the
     copy and restores metadata. The frozen-tree copy likewise assumes a quiescent source; its
     source is the daemon's candidate snapshot, not a live overlay.
   - `candidate.run_isolated` returns `examinerPeerPid` to the examiner: the examiner's PID as
     the bootstrap sees it through `SO_PEERCRED`, outside every role's PID namespace (the
     bootstrap is started with `unshare --user` only, so this is the service manager's PID
     namespace). It exists for signal probes, is not recorded in the boundary evidence and is
     given to no other role; an examiner that forwards it — in candidate argv, or in its
     report — discloses a PID from outside the sandbox.

6. **The trust base, and accounts with administrative access.** The private boundary relies on,
   and does not attest: the host kernel; the installed isolation binaries — bubblewrap
   (resolved, digest-pinned in the run plan and re-checked by the bootstrap before any role
   runs), `unshare`, `newuidmap`/`newgidmap` and `setpriv`; the systemd user manager that runs
   and reports on the units; `/usr/bin/python3` and the other `/usr` tools; the operator's
   subordinate ID configuration; and, when the optional toolchain is mounted, the listed GNAT
   executables, whose bytes are hashed without attesting the installation. The bootstrap checks
   that the three identities are distinct and that neither subordinate identity is host root or
   the operator; it does not check that no other host account uses those IDs. An operator or
   orchestrator account with administrative access (for example `sudo`) is outside the model,
   and WORLDLINE makes no claim against it. The same holds, as limit 2 says, for any process
   running as your uid outside the sandbox.

7. **Client mode separates the store from its clients; it does not authorize their requests.**
   - A listed client has every operation except the root-set changes and `switch`. That includes
     `collapse`, `return` and `transaction commit`. The confirmation screen is a CLI prompt,
     not a daemon-side authorization. Receipts do not record which uid asked; the daemon's log
     does.
   - The boundary is only as strong as the daemon's environment and account. Whoever can edit
     the service unit can add a client uid, and the daemon account can do anything the store
     can. The deployment must keep the unit, the install and the account out of the clients'
     reach.
   - Clients can stat names they already know along the path to PRIME, since the chain is
     group-searchable. Through each entry's recorded other-read bit, they can read:
     - PRIME's content;
     - fork checkpoints;
     - the staged payloads of open transactions, whose ids `transaction list` gives them.

     The content's group is the daemon's primary group, and a client in that group is refused, so
     a `0600` or `0640` file stays unreadable to them directly. Through daemon requests (`why`,
     `show`, `inspect`) they see PRIME content whatever its modes. Earlier PRIMEs' committed
     payloads stay readable by id until `prune`. They cannot list any store directory, and
     reachable content refuses other-write, a group-write bit outside the daemon's own group, an
     extended ACL, a file capability, and special bits.
   - The routing check reads the registered root links. The daemon account therefore needs
     search permission on the directories above them, for example the operator's HOME. Without
     it every capture refuses, which fails closed. It runs on the daemon's event loop: a
     registered path under a mount that stops answering (a FUSE mount whose device went away)
     blocks the daemon until it answers. A unit with `ProtectHome=tmpfs` and a read-only bind of
     the project directory keeps the home directory's other mounts out of the daemon's view.
   - `worldline shell` (`SHELL_UNAVAILABLE_TO_CLIENT`) and `switch`
     (`OPERATION_NEEDS_DAEMON_ACCOUNT`) need the daemon's own account, and refuse from clients.
     Agent adapters mount the credential files of the account the daemon runs as, so a
     dedicated account has no agent credentials until the deployment provides them. Job
     supervision needs that account's systemd user manager (lingering).
   - `worldline-relocate` proves a relocated copy's recorded locations, chains and mappings, and
     that its account owns every entry.
     - It does not prove the copy is complete. The copy step (as root, for overlay work
       directories) and its comparison belong to the migration.
     - Its check for a process holding the database open sees only processes of its own uid (in
       any mount namespace), matched by the device and inode their own mount tables and fdinfo
       give, which the copy's identity is read the same way as (on btrfs `stat` alone never
       matched). A real run also holds the copy's store lock, the one `worldlined` takes before it
       opens anything, so no daemon can start on the copy meanwhile; both runs first check,
       reading only, that it is free, before anything is written into the copy.
     - A copy root on FUSE, a network filesystem or an idmapped mount, or one that is the old
       store's location on the same device as far as the mount table can relate them, refuses,
       judged from the mount table before anything is written, whether or not the old store is
       visible to the relocating account; the old store's paths are resolved as far as that
       account can see first (a symlinked home), and when they run through a directory it cannot
       search, a copy root on a bind mount of a directory refuses too (a btrfs subvolume mounted
       whole is not a bind). Where the account can neither see nor locate the old store (its path
       unsearchable, or missing as behind a tmpfs over the home), a copy named by the old store's
       own real path, or a view of it the mount table cannot relate, is left to the ownership
       checks.
       On btrfs a held file with the same inode number in another subvolume of the same
       filesystem reads as a holder and refuses the relocation.
     - Every retained world's payload that is in the copy before relocation must be there after
       it. A payload absent from the copy is exempt only on positive evidence that the old store
       lacks it too: seen absent there, when the old store is present at its recorded path, is
       this store (generations, its roots' live links, at least one recorded payload seen
       present) and records the world at that path, walked without following links; or
       attested absent by a caller who can see the old store (`--absent-in-old-store`). Each
       basis is reported (`payloadsAbsentBeforeRelocation`, 1.7.2). Any other missing payload
       refuses before anything is written (`payloadsMissingFromCopy`), and a rerun on a
       rewritten copy exempts nothing. An attestation is trusted as given. The old store is read,
       never written.
     - It keeps each world's evidence byte for byte (it is hashed into the world's identity, and
       nothing reads a path back out of it) and counts it; a mention of the old store in any
       other database column refuses.
     - Directories it cannot read refuse, except overlayfs work directories (`0000` by design,
       holding only the kernel's transient state), which are checked for ownership but not
       descended; the report counts them.
     - It refuses a mount inside the copy and a file hard-linked outside it, and reports PRIME
       content a client-mode daemon would refuse as it is in the copy.
   - Deployment requirements that WORLDLINE does not enforce (`worldline doctor` reports the
     ones it can observe under `clientMode.deployment`, each `OK`, `MISSING` or `UNKNOWN`):
     - no `RestrictSUIDSGID=` on the unit or on the account's user manager (jobs run there): its
       seccomp filter answers `openat2` with ENOSYS, and bubblewrap (0.13) then cannot build any
       sandbox, so repository inspection, `simulate`, agents and checks all refuse (1.7.3; 1.7.0
       to 1.7.2 recommended it). Setuid content is covered by the content check, which refuses
       setuid and setgid bits in anything a client can reach, and by the `nosuid` store mount;
     - `MemoryMax=`, `MemorySwapMax=` and `TasksMax=` on the unit, which bound repository
       inspection (reported), and `OOMPolicy=continue`, so an OOM kill of inspection does not stop
       the daemon;
     - a `nosuid` store mount on the host, where clients reach PRIME (reported from PID 1's mount
       table; the daemon's own namespace can show `nosuid` over a mount that is not), placed
       outside the system roots `simulate` overlays (`/usr`, `/etc`, `/var`, `/opt`, `/boot`),
       for example `/srv/<account>`: the kernel refuses an unprivileged overlay layer with a
       mount beneath it, so a store mounted under `/var/lib` makes `simulate` fail for every
       account on the host (1.7.3);
     - a client group disjoint from the daemon's group (named members are checked; accounts whose
       primary group is the client group are not listed anywhere the daemon can check);
     - `fs.protected_hardlinks=1` (reported). Without it a client can hard-link a PRIME file it
       can read into a directory of its own, and every capture of PRIME then refuses
       `EXTERNAL_HARDLINK` until the link is found: a denial of service;
     - a regular (non-system) uid for the account, so journald keeps its user journal, which job
       supervision reads;
     - search permission for clients above the data and runtime directories.
   - `simulate` runs a client's argv as the daemon account, in a sandbox that masks the store and
     HOME but shares the host network under `network.policy: shared`.

     There is no supported way to add a root in the dedicated layout.

8. **Python chooses which evaluation speaks for a world, and a later failure does not revoke
   an earlier pass.**
   - `validation.effective_evidence` takes the newest PASS for the world's bytes. A revalidation
     that fails never speaks.
   - While an earlier PASS for the same bytes, from finalization or from a revalidation, is
     still fresh, it keeps speaking.
   - So a candidate whose checks pass once and fail on a later run can still be promoted on the
     earlier PASS until the requirement changes.
   - Planned: Phase 1 item 5, one effective evaluation. A newer evaluation supersedes, and a
     superseded one never regains authority.

## Reporting

This is a personal project on a single-user machine. Security notes and audit findings live
alongside the code in `SECURITY-AUDIT-*.md`.
