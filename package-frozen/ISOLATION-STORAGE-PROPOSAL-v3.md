# Isolation and storage proposal W-1, v3: protected writer, gated target account, committed records (specification)

**Status.** Drafting author's design specification, written 2026-10-04/05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame.
- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, mount, linger, unit, probe, selftest, vault or window action has been performed for v3.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED).
- v1 (`ISOLATION-STORAGE-PROPOSAL.md`, sha256 `a27d3e74305b5edd47acd31a7c881d7147cfecdaa0935195e2b0acea1dc70442`) and
  v2 (`ISOLATION-STORAGE-PROPOSAL-v2.md`, sha256 `1c116f27bd11bcd3e2fae0d00792b27c2e598928bb9ccc97f1db418102232cf6`)
  are preserved unchanged.
- v3 is written against the sealed actual gpt-6.1-sol re-review `wt-1/package-review/gpt61-v2` (verdict NOT_READY;
  freeze verified by hash: REVIEW.md `dc0127eb4c55b1913a6ea3e2c72b316aa9f4c57292bb3e5b00a430f4e059a226`, review.json
  `85fc67aea96975a9c8cf6f25d2fe000ab953247dfc5d3c8ebff6f8c962af7e6b`, checks.json
  `154ff442e61078f135cae9015b5ed4cbfa9984ac560a49a65dc8e0489cacf9a8`). Its four NOT_CLOSED W-1 corrections
  (W1-CUSTODY, W1-SETUP, W1-RESOURCES, W1-LIFETIME-ROLLBACK), its twelve section-3 gaps and every original W-1 subgap
  are mapped in §18. **§18 gives the author's own assessment (CLOSED-AT-SPEC-LEVEL or OPEN) for an independent actual
  gpt-6.1-sol reviewer to judge. It is not closure, and no row says a section "answers" a finding.**
- Authority. Design and frame code are routine reversible engineering under the human's preserved authorization; no
  in-principle approval is needed for them. Reserved to the operator: actual privileged setup (accounts, groups, ACLs,
  sudo, sshd configuration, installation, mounts, linger, rollback) on a concrete reviewed inventory; material
  API/ABI/owner-policy changes; toolchain/deployment architecture; merge, release, install, sudo, production and real
  PRIME. v3 adds no other approval gate.
- Every "verify", "check", "probe", "selftest" or "observe" below names future work. Design text is not executed
  evidence.

**Inputs read for v3** (sha256, read-only): frame v5 sealed review `REVIEW.md` `2c414c694ed75d72cffae2172bef967bdcf63d73cc0a3764f96762a59d49ec71`
(freeze `48539bdf…4ef7`); frame v5 `scratch.py` `f9f6596d…be86`; frame v6 working copy `scratch.py`
`2255d6e1…4c84`; `frame-v6-PLAN.md` `9a07534b…d1e9`; runbook v4.3 `d7db4439…7201` (v4.2 preserved as
`runbook-history/v4.2-SUPERSEDED.md` `612f110f…10f5`, the version the re-review read; v4.3 changes only O1's provenance
wording); earlier package review `gpt61-v1/REVIEW.md` `824c95c3…44c7`; HANDOFF.md `2f3a0b4b…8237`;
START-CLAUDE.txt `004c71a8…187e`; `complete-phase1-prompt.txt` `1b228f4b…b327`; `frame-v6-selfcheck/RESULTS.md`
`74230e85…8292`; `frame-v6w1-proto/RESULTS.md` `1651ddbd…66eb`; `w1proto.py` `2c7d6100…19dd`.

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, Gate 0 and every original
Phase One obligation stay OPEN with their original owners, releases and dependencies. A kernel-enforced writer boundary
is not proof of the frame code, not lead authentication, not target confinement and not capacity.

---

## 0. Reading guide and what changed from v2

The design keeps v2's direction (separate writer account, separate target account, streamed pinned inputs, exclusive
writer lease, front-side storage and vault) and makes it a complete, internally consistent specification:

1. **Generation order (§4).** The initial generation record binds only what exists when it is written. Inputs,
   reservation, admission and launch intent are separate create-only records with exact schemas, anchors and joins.
   The immutable admitted generation partition is distinct from the attempt bookkeeping partition and the export
   partition, so "final pass after the last frame mutation" has an exact meaning (§4.5).
2. **Lease (§5).** `writer.lock` is created at setup, owned by root, mode 0440, and only `flock`ed through an
   `O_RDONLY` descriptor: there is no runtime byte write. Its owner, group, mode, type, link count, size, name,
   parent and inode identity are checked at every invocation. The entrypoint closure for both accounts and for the new
   gate group is enumerated route by route.
3. **Modes and ACLs (§6).** No ACL is set on any recipe object, frame record, snapshot entry or stream, so every v5
   mode is preserved exactly. No default ACL exists anywhere. Access is shaped only on frame-created ancestors
   (`runs/`, the generation root) and on the four writer-created output partition roots. The target reads source
   through the recipe's own others-bits. The writer never opens a target-owned object. The lead reads writer-produced
   export copies.
4. **A dedicated gate group (§3, §5, §6, §9).** The target runs as `wlscratch-run` with the primary group
   `wlscratch-gate`, which only the reviewed launcher path can confer. Background processes of the target account's
   own user manager lack it and cannot reach the generation.
5. **Channels (§7).** Exact framing, canonical bytes, chain initialization, rejection rules and in-memory
   expectations. Integrity is stated as integrity, not authentication; the lead-authentication ceiling is the
   original v5 ceiling. Dumpability is set and read back through `prctl(PR_GET_DUMPABLE)` and the ownership of
   `/proc/self/fd`, with the exact point in each process's start.
6. **Identities (§8).** Fresh per-invocation identities for every role; the real non-isolated lead invocation and the
   original target path and caps are kept; an explicit relocation table yields the new target-context baselines; the
   vault pins the export partition only.
7. **Participants (§9).** Complete participant, wait and scope schemas; launch gating that makes a late launch after
   writer death impossible except through an already-issued, recorded permission; known-terminal ownership defined
   from protocol invariants and complete process-table scans; reboot interpretation bound to boot identity.
8. **Commits (§10).** A record counts only through a separate committed-record marker (N11). Retries, a
   pre-established preallocated fallback journal inside the generation, and an explicit durability-UNKNOWN state.
9. **Setup (§11), exposure (§12), probes (§13), resources (§14), rollback and evidence (§15)**: exact, staged and
   fail-closed.

**Author corrections carried from v2's lifetime** (recorded earlier in `STATUS.md`, `frame-v6-selfcheck/RESULTS.md`
and `frame-v6w1-proto/RESULTS.md`; v2 itself is not edited):
- v2 §4.5 said the excluded-leaf final pass was "required and not yet written". The v6 working copy already records
  excluded generated leaves (`scratch.py:554`) and re-stats them in the final pass (`:569-573`); an ENGINEERING_ONLY
  self-check exercised it (14/14 as required). That is not review, admission or acceptance evidence.
- The subordinate-UID prototype showed that UIDs delegated to `sicarii` in `/etc/subuid`/`/etc/subgid` are no boundary
  against `sicarii`. v3 makes exclusion from every delegated range a setup requirement (§11.2).
- v2 named a `/proc/self/status` "Dumpable" readback; that field does not exist on this host. v3 uses
  `prctl(PR_GET_DUMPABLE)` and `/proc/self/fd` ownership (§7.7).
- v2 §5.2 cited a nonexistent §8.5. Every cross-reference in v3 resolves to a section of this document.

## 1. Criteria (verbatim, unchanged)

Source: frame v5's sealed actual gpt-6.1-sol review, `work/claude-scratch-frame-v5/review/gpt61-v1/REVIEW.md`
(sha256 above). Lines 76 and 82 are quoted here; lines 76, 82 and 84-123 are reproduced byte-exactly in Appendix A.

**V5-B01 (REVIEW.md:76):**

> Retain file observation identities through the complete walk and revalidate every encountered leaf, including
> excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission
> boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted
> generation from changing before use. Directory-only revalidation or after-run detection must not substitute for
> pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates.

**V5-B02 (REVIEW.md:82):**

> Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff,
> rather than observer-only checks before and after it. Use an independently protected writer/location boundary or
> an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch
> are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed
> preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the
> original guarantee; retain this blocker if custody cannot yet be established.

**Residual rulings, N-items and terminal semantics (REVIEW.md:84-123)** are carried unchanged (Appendix A). In
particular: residuals (a)-(d) are ACCEPTABLE_AS_DOCUMENTED only within their stated limits and none authorizes
frame-owned outside-tree mutation or an unsafe alias present at final launch admission; N01, N03, N04, N07, N08,
N09 remain engineering ceilings; N11-N14 are required corrections (§10); "SIGKILL/dead launching parent has no late
collector and leaves manual reservation resolution" stays in force (§9.4).

**WORLDLINE monitor rulings (unchanged; as carried by `frame-v6-PLAN.md:5-13,33-39` and v2 §1):**
- An own-inode "detected and refused" residual does not satisfy V5-B02.
- A root-made filesystem, and W-1 itself, are candidates, not established designs or approved actions.
- Storage (two separate exact excerpts, joined here by an ellipsis): "live preflight that budgets measured run growth
  AND temporary full-restore space above the unchanged reserve … If safe capacity cannot be established, keep dispatch
  deferred."
- "periodic storage sampling plus a factor on the maximum observed write rate does not establish a maximum future
  write rate or stop latency".

**Ineligibility.** No W-1 setting closes an unchanged obligation by lowering it: a lowered reserve, a narrowed
confinement scope, a frame write relabelled as target residual, a waived warning, a narrowed accepted case, control,
fixture, allowlist, cap or gate, a finite cap, a new size refusal, catch-and-refuse, or image ENOSPC presented as an
accepted refusal or success. Any of these leaves the original obligation OPEN.

## 2. Threat model, trusted base, preconditions and residuals

### 2.1 Adversaries

- **A1, concurrent `sicarii` processes** (other agents and sessions; uid 1000). They may run arbitrary code as
  `sicarii`, including user namespaces over `sicarii`'s delegated subordinate range 100000-165535 (start 100000, count
  65536; last id JACKAL exact, parsed `100000+65536-1`), FUSE mounts,
  reads of every dumpable `sicarii` process's `/proc` entries, signals to `sicarii` processes and to processes whose
  real uid is `sicarii`, writes to every `sicarii`-writable file (including the shared window file, the lead inbox and
  every frozen input under `/home/sicarii`), and invocations of the reviewed `sicarii`→`wlscratch` sudo rule with
  arbitrary arguments. They must not be able to create, rename, substitute, modify or delete any frame-owned location
  or the admitted generation, or cause the frame to mutate outside its tree.
- **A2, the running target** (`wlscratch-run` with group `wlscratch-gate`, and everything it starts). It may do
  anything those credentials allow, including starting units in its account's user manager, moving itself between
  cgroups of that manager's delegated subtree, passing descriptors to other processes, and writing everywhere its
  credentials permit outside the generation. It must not be able to mutate frame records, the admitted recipe, the
  frame's location chain or another attempt's evidence, and its leftovers must not change an admitted generation
  between a later final pass and spawn.
- **A3, background processes of the target account's user manager** (uid `wlscratch-run` without `wlscratch-gate`).
  They are root-configured services, not adversaries by assumption, but the design does not let them reach the
  generation and treats any of them holding a generation reference as an unknown participant (§9.4).

### 2.2 Trusted base (outside the threat model)

Root and everything running as root (sudo, systemd and logind, PAM, sshd, the kernel, the root launcher of Option B);
root-owned installed files (`/usr`, `/etc`, the installed frame under `/opt/wlscratch`); the Python 3.14.7 runtime
under `/usr/lib/python3.14` (interpreter `/usr/bin/python3.14`, sha256 observed by v2 as
`c6bc1ef497b896b7575c546b13f9bafe52e2066f184fdd3fec6af4b5b6349947`); the operator's credential. The design gives no
protection against root, against kernel defects or against a compromised operator credential.

### 2.3 Preconditions (checked at setup, §11.3; their failure refuses setup)

- **No privilege route for `sicarii`.** Apart from the reviewed frame rule, no route lets a `sicarii` process run as
  root, `wlscratch`, `wlscratch-run` or with `wlscratch-gate` without the operator's interactive credential: no
  `NOPASSWD` sudo rule yielding root or those identities, no polkit rule granting `sicarii` (or a group it is in) a
  passwordless `YES`, the `empower` group empty, no membership in `docker` in any running session, no file capability
  or setuid/setgid binary owned by the new identities. An unprivileged process cannot read `/etc/sudoers` (0440),
  `/etc/sudoers.d` (not listable) or `/etc/polkit-1/rules.d` (not listable); the drafting author observed those
  refusals on 2026-10-04, so this inventory is operator-produced. Observed by the drafting author on 2026-10-04:
  `/etc/group` lists no member of `docker` or `empower`, and the drafting session's own process had supplementary
  groups 954, 955, 956, 982, 983, 992, 995, 998, 1000 (no `docker`).
- **Kernel settings** as observed: `fs.protected_hardlinks=1`, `fs.protected_symlinks=1`, `fs.protected_regular=1`,
  `kernel.yama.ptrace_scope=1`, `/proc` mounted without `hidepid`, cgroup2 with `nsdelegate`. Observed too:
  `fs.suid_dumpable=2`.
- **One local filesystem.** Observed: `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp` and `/home` are all on `/dev/vda`
  ext4; `/dev/shm` and `/run/user/*` are tmpfs. No EXDEV boundary is relied on anywhere.

### 2.4 Residuals (stated exactly; none is a new accepted exception)

- **R1, the lead's own processes.** W-1 does not protect `sicarii` processes from other `sicarii` processes. Yama
  `ptrace_scope=1` stops non-ancestor attach; read-mode `/proc` access is not covered by Yama, so each frame process
  sets itself non-dumpable as its first effective act (§7.7). Before that call there is a pre-first-call window. This
  is an explicit inability carried from frame v5, where the whole frame ran as `sicarii`; it grants no acceptance.
- **R2, lead authentication.** The frame authenticates the lead only through the reviewed v5 admission protocol:
  frame review and adoption joins, the fresh lead observation, the actual-MCP JACKAL challenge and receipt (N01: a
  lead obligation), and window ownership. Private pipes, the channel chain and the sudo rule add integrity and
  ordering, not sender authentication (§7.6). This is the original v5 engineering ceiling, carried exactly, not a new
  accepted residual. All original joins are implemented.
- **R3, the running target.** No confinement of the running target outside the generation: the ruled
  `no-target-confinement` residual (ACCEPTABLE_AS_DOCUMENTED at the reference ceiling). It covers target writes only,
  never a frame write and never an unsafe alias at final admission. W-1 narrows where the target can write but the
  inventory of target-writable places is incomplete and stated as UNKNOWN beyond the listed places (§12.3).
- **R4, the toolchain.** The target executable is identity-checked and then executed by path (ruled
  ACCEPTABLE_AS_DOCUMENTED). The toolchain under `/home/sicarii/opt/gnat` stays `sicarii`-owned and `sicarii`-writable;
  its closure is observed before and after. W-1 claims no custody of it.
- **R5, exposure.** Option A's read exposure is known only for named places and UNKNOWN elsewhere (§12.1). Option B
  adds privileged code (§12.2).
- **R6, availability.** A `sicarii` process can stop an attempt: it can kill the front, signal processes whose real
  uid is `sicarii` (which may include the sudo front-ends, so a signal may be relayed to a frame helper), or modify
  the cooperating window file (N07). The result is an interrupted, non-success attempt or a held window, never a
  custody change. Whether sudo relays such signals is a probe item (§13, P-SIG).
- **R7, `(sd-pam)`.** The target account's user-manager PAM helper may have root-owned `/proc` entries, so its
  descriptor table may be unreadable to the observer. §9.4 accepts it as a baseline process only under the identity
  conditions stated there; this is a stated limit, verified by probe P-MGR.
- **R8, root and the kernel** (§2.2).
- **R9, descriptors in transit.** `SCAN-REFS` (§9.4) sees descriptors installed in a process's table, its file
  mappings, cwd and root. It cannot see a descriptor sitting unreceived in a socket queue. A target could pass a
  generation descriptor towards a baseline service of its account; such services are root-configured (A3) and are
  reduced by the setup masks to the manager, `(sd-pam)` and the user-bus broker. This is a stated limit of the scan,
  not an accepted exception; a received descriptor becomes visible and holds the window.

## 3. Principals, accounts and layout

### 3.1 Accounts and groups (three new identities)

| Identity | Kind | Purpose | Members |
|---|---|---|---|
| `wlscratch`, uid = gid = W | user + user-private group | The only writer of generation trees | none besides the user |
| `wlscratch-run`, uid = gid = R | user + user-private group | Runs the launcher, observer, in-scope child and target; owns a lingering user manager | none besides the user |
| `wlscratch-gate`, gid = GATE | group only | Granted to processes started through the reviewed launcher rule; the only non-writer, non-lead key to the generation | none in `/etc/group` |

Candidate numbers: W = 950, R = 951, GATE = 952. As observed on 2026-10-04 they are unused by every passwd and group
entry (the lowest used system uid is 957 and the lowest used gid at or above 900 is 954), inside `SYS_UID_MIN`-`SYS_UID_MAX`
500-999 of `/etc/login.defs`, and outside every range in `/etc/subuid` and `/etc/subgid`. They are candidates; §11.2
fixes the policy and the prestate re-verifies them. Counts: new users 2 (JACKAL exact, parsed `1+1`); new groups 3
(JACKAL exact, parsed `1+1+1`: the two user-private groups and `wlscratch-gate`).

The v1 `wlscratch-clients` group is not used. `sicarii` gets no new group membership and no new login.

### 3.2 Roles (processes)

| Role | Process and credentials | Started by | Code |
|---|---|---|---|
| F, front | the lead's real outer invocation `/usr/bin/python3 -B /opt/wlscratch/frame-v6w1/front.py <verb> …`, uid 1000 | the lead | installed, root-owned |
| S1 | `sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py <verb> …` | F | `/usr/bin/sudo` |
| W, writer | `writer.py`, uid/gid W | S1 | installed |
| S2, S_O | `sudo -n -u wlscratch-run -g wlscratch-gate -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py <verb> …` (Option A) | W | `/usr/bin/sudo` |
| L, launcher | `launch_target.py launch …`, uid R, egid GATE | S2 | installed |
| SR/C, scope launcher then in-scope child | `systemd-run --user --scope …` which, being a scope, `exec`s `launch_target.py child …` in the same process inside the scope | L | systemd, installed |
| U, scope | transient `claude-worldline-scratch-<g12>-<A>.scope` in R's user manager | SR | systemd |
| T, target | the exact allowlisted command, uid R, egid GATE | C | toolchain |
| O, observer | `launch_target.py observe …`, uid R, egid GATE | S_O | installed |
| W2, seal-front | a second, short `writer.py seal-front …` invocation that commits the front's terminal record | F, via S3 (same rule as S1) | installed |
| RL (Option B only) | root launcher `sandbox_launch.py`, replacing S2's direct `-g` start | W, via Option B's rule, which replaces the launcher rule | installed, privileged |

`<g12>` is the first 12 hex digits of the generation id; `<A>` is the v5 attempt stamp (`STAMP_RE`).

### 3.3 Layout

```
/var/lib/wlscratch                    root:W        writer home (setup)
  lease/                              root:W        setup; writer-only traverse
    writer.lock                       root:W 0440   setup; flock-only
  runs/                               W:W           setup; generation roots live here
    <g>/                              W:W           generation root G (writer-created), g = 32 lowercase hex
      generation.json                 initial generation record                        [P_adm]
      commits/                        generation-level commit markers                  [P_adm]
      inputs/                         streamed input records + manifest.json           [P_adm]
      overlay-snapshot/               v5 overlay snapshot (0700 dirs, 0600 files)      [P_adm]
      source/                         admitted recipe (exact recipe modes)              [P_adm]
        obj/ lib/ resource-tests/obj/ resource-tests/bin/   output partition roots     [P_adm roots; contents target-owned]
      materialization.json            v5 schema plus §4.3 fields                       [P_adm]
      attempts/<A>/                   attempt bookkeeping partition                    [P_att(A)]
        attempt.json, commits/, fallback.journal, front/, streams, all v5 attempt records
      export/                         export partition (writer-produced read-only copies) [P_exp]
        generation/   <A>/
/var/lib/wlscratch-run                root:root     target account home (setup; not writable by R)
  tmp/                                R:R 0700      the target's TMPDIR (setup)
  .config/systemd/user/               root:root     masks for the target account's user manager (setup)
/opt/wlscratch/frame-v6w1/            root:root     installed frame (member-exact)
/opt/wlscratch/setup-identities.json  root:root 0644 setup identity record (§11.5, script S-H)
```

Exact modes and ACLs are in §6.3. If optional images are chosen (§14.5), `runs/` is the work image's mount point and
the attempt and export partitions move to a records image; §14.5 states the conditional layout.

## 4. Generation order and record partitions [gap: generation-order]

### 4.1 Three partitions

- **P_adm(g), the admitted generation partition.** `generation.json`, `commits/` (generation-level markers),
  `inputs/**`, `overlay-snapshot/**`, every recipe object under `source/` (files, directories, their modes and
  contents), the four output partition root directories (their identity, mode and ACL) and `materialization.json`.
  P_adm is written only by the `materialize` invocation that creates g. After that invocation's final verification
  and the materialization marker (§4.2, M8), no writer verb has any path that mutates P_adm: no verb rewrites,
  renames, deletes, chmods or re-ACLs an existing P_adm object. Only W can write there at all (§6.3), and W writes
  P_adm only in `materialize`.
- **Partition contents.** Entries below the four partition roots are written only by targets of launched attempts
  (through the gate group, §6.3). They are not frame writes. They are part of what each later attempt admits, so every
  attempt re-observes them in full (§4.5).
- **P_att(g, A), the attempt bookkeeping partition** `attempts/<A>/**`. Every writer invocation that touches g has
  one: the creating `materialize` invocation (kind `materialize`) and every `dispatch` invocation (kind `dispatch`).
  It is created by that W, written by that W and, for `front/` records only, by the capability-checked W2 (§5.2).
  Create-only. The target never reads it: launch records reach the in-scope child over its channel (§7.1), and target
  streams are passed as open descriptors (§6.4).
- **P_exp(g), the export partition** `export/**`. Writer-produced read-only copies of committed records, for the
  lead. Create-only. Never read by the target, never an admission input.

The partitions are disjoint. Every frame mutation after a generation's creation lands in a P_att or P_exp, never in
P_adm.

### 4.2 Exact order

**Generation creation (`front.py materialize <label> <overlay-dir>`; v5 `materialize`).**

- M1. F starts (§7.7 first act), records its identity (§8.1), validates its argv grammar (`label` matches v5
  `NAME_RE`; `overlay-dir` absolute).
- M2. F reads, through the v5 anchored readers, the base descriptors (`source-binding.json`,
  `source-inventory.json`, `source-directory-modes.json`), observes `BASE/source` against the pinned inventory
  (`observe_tree`, as v5 `base_tree`), and observes and reads the overlay directory (`observe_tree` + `read_files`,
  as v5 `materialize`). F writes nothing.
- M3. F creates its two channel pipes after its first act and starts S1 → W (`writer.py materialize <N_F> <label>`,
  `N_F` = 32 random bytes as 64 hex, §7.3).
- M4. W starts (§7.7), records its identity, takes the lease (§5.1), anchors `/var/lib/wlscratch/runs` from `/`,
  creates `g` (v5 `Dir.child(create=True)`: mode 0700, owner W, link count 2, same device, empty, not an ancestor),
  sets g's access ACL by `fsetxattr` on the held descriptor and reads it back (§6.3), creates `commits/` (0700,
  authenticated) and writes **`generation.json`** (§4.3) with its marker (§10.1). It then creates `attempts/` and
  `attempts/<A0>/` (0700, authenticated) and writes there **`attempt.json`** (kind `materialize`; its only generation
  pin is `generation.json`) and the preallocated `fallback.journal` (§10.3), each with its marker. It then sends
  `W_HELLO`.
- M5. F answers `HELLO_ACK` (it echoes `N_W` and carries F's identity). W records F's identity in
  `attempts/<A0>/front/front-identity.json`.
- M6. Inputs are streamed in three requested phases (§7.2): (i) the three base descriptors, the lead module and F's
  base-tree observation; (ii) the overlay files and `DELETE.list`; (iii) exactly the base files the recipe needs (base
  inventory minus deletions minus overlay-replaced paths), in sorted path order. W verifies every pinned input before
  it uses or writes it (§8.6, pinned versus observation inputs). Descriptor bytes, the lead module and the observation
  go to `inputs/` as create-only input records. Overlay bytes go only to `overlay-snapshot/` and base-file bytes go only
  to their recipe path under `source/`; the message log records their headers and a reference to the place their bytes
  were written, so no bulk payload is retained twice (§7.3).
- M7. W materializes exactly as v5 `materialize` (S:959-1049), with streamed verified bytes in place of anchored
  reads of `BASE` and the overlay directory: `overlay_rules`; `expected_source`; snapshot files written by
  `write_bytes` with the default 0600 into snapshot directories created 0700; every recipe directory created 0700 and
  authenticated; every expected file written with its row mode (base mode, or 0644 for a new overlay unit); then the
  four partition roots created (0700, authenticated) with their ACLs set and read back (§6.3); then the recipe directory
  modes applied deepest first, the recipe root last (`set_mode`); then `source.sync()`.
- M8. W verifies with a full walk of `source/` (all partition roots are empty and writer-owned at this point, so W
  can walk them) and of the snapshot: recipe content and modes equal the recipe; the partition roots are exactly the
  four, empty, with their exact mode and ACL. W then writes **`materialization.json`** (§4.3) and its marker, runs
  `verify_materialization` against the committed record, and re-verifies the location of every held handle. **This is
  the last mutation of P_adm(g), ever.**
- M9. W writes the generation export (`export/generation/`, §15.3) and sends `MATERIALIZED`. F runs
  `project-vault pin <g>/export` and `project-vault status` (§8.5) and streams the results; W records them in
  `attempts/<A0>/front/`. F sends `BYE`; W closes and exits; F waits for S1; F commits its terminal record through W2
  (§9.2); F exits (§10.6).

**Dispatch attempt (`front.py dispatch <inbox> <g> <action> [args]`; v5 `dispatch` + `run` + `child`).**

- D1. F starts, records its identity, validates `action`/`args` against v5 `ACTIONS`/`command()` grammar and anchors
  the lead-created inbox (`sicarii`-owned, mode 0700, empty).
- D2. F performs its parent-stage half (§8.1): fresh lead observation (`claude_lead.observe('scratch-run', …)`),
  the front part of frame admission (installed-inventory pin versus review and adoption, rollout join, adoption
  observation and transcript prefix), base-tree re-observation and its own runtime identity. Results stay in memory.
- D3. F starts S1 → W (`writer.py dispatch <N_F> <g> <action> [args]`).
- D4. W starts, takes the lease, opens g by the anchored chain, requires committed markers for `generation.json` and
  `materialization.json` and equality of P_adm identities with them, creates `attempts/<A>/` (0700, authenticated),
  writes **`attempt.json`** (§4.3) with its marker, preallocates `fallback.journal` (§10.3) with its marker, and sends
  `W_HELLO`.
- D5. F sends `HELLO_ACK` and its D2 results; W records them under `front/` with markers.
- D6. Parent stage, in v5's order: the writer half (writer-owned recipe walk, snapshot, record pins, location), the
  observer O for the parent stage (scans, full walk, target-context identities `parent`; §9.1), the `preflight`
  sample (front half: sibling units in `sicarii`'s manager and `storage_status.py`; helper half: heavy-process and
  meminfo; §8.1), then `project-vault pin <g>/export` and `status` by F.
- D7. Frame-enforced Gate 0 receipt for the dispatch stage (§14.3).
- D8. W writes **`launch.json`** (§4.3) with its marker.
- D9. Reservation, driven by F under the shared-window lock (§9.4): `reservation-intent.json` is committed by W
  before F's window commit; `reservation.json` after it.
- D10. v5 memory gate: W issues each challenge; F prints it and forwards the lead's answer line and receipt bytes
  from the inbox; W verifies exactly as v5 (`memory_gate`, `receipt_line` deadlines 300 s and 30 s).
- D11. W writes **`admission.json`** and then **`launcher-intent.json`** (§4.3), each with its marker, and sends
  `LAUNCH_INTENT_COMMITTED`.
- D12. F sends `PROCEED_LAUNCH` only after D11's acknowledgement and only while it still owns the window. Only then
  does W create the stream files and the launcher socket and start S2 → L (§9.3).
- D13. Launch, child stage, final pass, spawn and run (§9.3).
- D14. Conclusion, release, export, final status, W's exit, F's wait, W2, F's exit (§9.4, §10.6, §15.3).

### 4.3 The records that order the generation (complete field lists in Appendix B)

- **`generation.json` (initial generation record).** It binds only facts that exist when it is written: generation
  id, creation time, boot id, W's identity and invocation (argv, `SUDO_USER`/`SUDO_UID`/`SUDO_COMMAND`), the `N_F`
  nonce from W's argv, the front-process triple `(pid, start_time_ticks, boot_id)` that W reads from `/proc` (F is the
  parent of S1, which is W's parent), the lease identity, the location chain from `/` to g (device, inode, owner, mode,
  ACL digest for each component), the installed frame inventory pin, the setup identity record pin, the channel
  genesis heads, the verb and label. It binds **no** input digest, recipe, reservation or launch fact, because none
  exists yet. F's self-reported identity arrives later (`HELLO_ACK`) and is recorded in P_att(A0), not here.
- **`inputs/<seq>-<name>` and `inputs/manifest.json`.** One create-only record per descriptor, lead module and
  observation input (bytes plus `{path, size, mode, sha256, class, pin_source, verdict}`), and a manifest written after
  the last input: every input header including overlay and base files, the place each payload was written, the channel
  heads after the last input.
- **`materialization.json`.** The v5 schema (`claude-scratch-materialization-v5` fields: base pins, overlay snapshot
  and identities, overlays, deletions, `source`, `source_directory_identities`) plus `generation` (pin of
  `generation.json`), `inputs_manifest` (pin), `partition_roots` (path, `[dev, ino]`, mode, exact ACL text),
  `recipe_mode_property` (§6.1), `channel_heads`. Its schema name becomes `wlscratch-materialization-v1`; the v5
  `run` field becomes the generation root path.
- **`attempts/<A>/attempt.json` (initial attempt record).** Kind, attempt stamp, generation pins
  (`generation.json`, `materialization.json`, their markers), W's identity and invocation, the lease identity, the
  channel genesis for this invocation, the front-process triple `(pid, start_time_ticks, boot_id)` read by W from
  `/proc` as the grandparent of W through S1 (§9.2, used by W2), the boot id and the verb and arguments. Like
  `generation.json`, it binds nothing that does not yet exist.
- **`launch.json`** (v5 schema plus): `generation`/`attempt` pins; the parent-stage full-walk observation digest
  from O (files, directories, identities and every excluded generated leaf's `stat_key`, §4.5); the relocated target
  environment (§8.4); the exact L, systemd-run and C argv templates; the stream-file names; the unit name; the front
  stage-record pins. v5 fields kept unchanged in meaning: `action`, `args`, `child_argv`, `cwd`,
  `directory_identities` (run, attempt, source, snapshot, `source_tree`), `unit`, `scope_argv_template`,
  `scope_argv_tail`, `environment`, `frame_inventory`, `review`, `adoption`, `materialization`,
  `storage_reserve_bound`, `holder`.
- **`reservation-intent.json`, `reservation.json`** (v5 fields: `at`, `token`, `launch`, `prior`, `holder_task`,
  `candidate`; `current`) plus the window-lock identity F observed under the lock and the F request message digest.
- **`admission.json`** (v5: `memory_gate`, `reservation`, `launch`) plus the Gate 0 receipt pin (D7), the front
  stage-record pins, the O parent-stage record pin and the writer-half pins. It is the complete create-only
  admission/launch record: written after every input, the reservation and the memory gate.
- **`launcher-intent.json`** (v5: `scope_argv`) plus the L argv (with `launch.json` and `admission.json` sha256 and the
  W↔L nonce), the stream-file descriptors and the commit-journal head. It is the launch intent: committed before any
  launcher process can exist (§9.3).

No sealed record is ever rewritten. Later facts go into new records (for example the input manifest, the admission
record, `conclude-errors.json`), never into an earlier one.

### 4.4 Anchors and joins

- Channel genesis: `head0(dir) = SHA256("wlscratch-channel-v1" ‖ 0x00 ‖ dir ‖ 0x00 ‖ N_F)` for `dir` ∈ {`F2W`,
  `W2F`}; F knows `N_F` because it chose it; W reads it from its own argv, which `sudo` also reports in
  `SUDO_COMMAND`. `W_HELLO` (the first `W2F` message) carries W's nonce `N_W`, and `HELLO_ACK` (the first `F2W`
  message) echoes it, so both nonces are bound into both chains by their first messages (§7.3). W↔L, L↔C and W↔O
  chains are initialized the same way with their own argv nonces.
- Every record carries `generation`, `attempt` (or `null` for P_adm records), `boot_id`, the current heads of both
  directions of its invocation's channel, a writer-local `record_seq`, and `prev_commit` (the sha256 of the previous
  commit marker of the same journal), so committed records form hash-linked journals: one per generation for P_adm
  (`g/commits/`), and one per invocation for its P_att records and its P_exp copies (`attempts/<A>/commits/`) (§10.1;
  the frame plan's H-M4 journal).
- Joins required before launch: `attempt.json` → generation pins equal the committed `generation.json` and
  `materialization.json` markers; `launch.json` → `attempt.json` pin and the O parent-stage observation pin;
  `reservation-intent.json` → `launch.json` pin (v5); `admission.json` → launch and both reservation pins (v5) plus
  the Gate 0 and stage pins; `launcher-intent.json` → launch and admission pins; L's and C's argv → the sha256 of
  `launch.json` and `admission.json` (v5 V4-B03 seal); C → the bytes it received over its channel hash to those values.
- F's expectations join W's records through the channel: every `*_COMMITTED` message carries the record descriptor
  `{name, sha256, bytes, mode}` and the marker digest, which F keeps in memory (§7.5).

### 4.5 Where the final pass is, exactly

The **final admission boundary** is C's last full walk, inside the scope, immediately before the spawn:

1. C performs v5 `verify_materialization` over `g/source` with the v6 final pass: every encountered leaf, recorded or
   excluded generated, is re-stat'ed by name without following and must keep its complete `stat_key`, and every
   directory is re-reached with unchanged metadata (`scratch.py` v6 :554, :569-573). C walks as `wlscratch-run`
   with `wlscratch-gate`, so it can read recipe files (others-readable recipe modes) and every target-owned partition
   entry (owner).
2. The observation (files, directory modes, identities and every excluded generated leaf's `stat_key`) must equal the
   O parent-stage observation sealed in `launch.json` exactly. A difference in any recorded or excluded leaf refuses
   the launch. (v5 compared directory identities only; the excluded-leaf comparison is added and is an engine change
   to `observe_tree`, which must return the excluded leaves' keys it already computes.)
3. Then C re-verifies the location of its held handles, reaches the interruption point (pending-signal check) and
   spawns with `fchdir` on the held `source` descriptor (v5 `spawn`).

This pass follows (a) the last mutation of P_adm(g) (M8, at generation creation), (b) the commit and delivery of
every record C's admission depends on (`launch.json`, `admission.json`, `launcher-intent.json`) and (c) the
`SPAWN_OK` of §9.3. Every frame write after it goes to P_att(g, A) or P_exp(g): `child-start.json`, waits, the
conclusion. Those partitions are disjoint from P_adm and the target never reads them. **So "the final pass runs after
the last frame mutation of the admitted generation" is exact, and the remaining frame writes are bookkeeping by
construction, not exceptions.**

Custody from the final pass to `exec` (V5-B01, second sentence) rests on five facts, each with its own section:
(i) no `sicarii` process has write access to any P_adm object or to partition contents (§6.3, §6.5); (ii) W does not
mutate P_adm after M8, and any other writer instance refuses before its first mutation while W holds the lease
(§5.1); (iii) GATE can be held only by
processes started through the reviewed launcher rule, and earlier targets could not mint a GATE-conferring
set-group-ID file because their whole process tree ran under `no_new_privs` and the anti-setid filter (§9.3, step
C9); (iv) the scans in C's child stage (§9.4) refuse unless L and C are the only GATE holders, no unknown process
holds R, and no baseline process of the target account holds a reference into g; (v) background processes of the
target account cannot reach g by path (§6.4). Root is outside the threat model. This is an argument for review, not
evidence.

## 5. Lease, writer authority and entrypoint closure [gap: lease-and-writer-authority]

### 5.1 `writer.lock`: creation, checks, use

**Creation (setup script S-B, §11.5).** As root, in a freshly created root-owned directory:
`install -d -o root -g <W> -m 0750 /var/lib/wlscratch/lease`, then
`touch /var/lib/wlscratch/lease/writer.lock && chown root:<W> … && chmod 0440 …`, then a check that
`stat -c '%F %h %s %u %g %a'` prints exactly `regular empty file 1 0 0 <W> 440`. Only root can create, replace,
rename or chmod either object, because the directory is root-owned and not writable by its group, and the file is
root-owned.

**Checks at every writer invocation, before any mutation** (all through descriptors, no pathname re-resolution):
1. Anchor `/var/lib/wlscratch/lease` from `/` component by component with `O_DIRECTORY|O_NOFOLLOW` (v5 `Dir.anchor`);
   each ancestor's `[dev, ino]`, owner and mode must equal `setup-identities.json` (`/` and `/var` and `/var/lib`
   root:root 0755; `/var/lib/wlscratch` root:<W> with the ACL of §6.3; `lease` root:<W> 0750 with no ACL xattr).
2. `openat(lease_fd, "writer.lock", O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK)`; `fstat` must show `S_ISREG`,
   `st_nlink == 1`, `st_uid == 0`, `st_gid == W`, mode 0440, `st_size == 0`; `fgetxattr(…, "system.posix_acl_access")`
   must fail with `ENODATA`; `fstatat(lease_fd, "writer.lock", AT_SYMLINK_NOFOLLOW)` must name the same `[dev, ino]`;
   and `[dev, ino]` must equal the value in `setup-identities.json`.
3. `flock(fd, LOCK_EX|LOCK_NB)`. `EWOULDBLOCK` → refuse before any mutation (W writes nothing, reports on its stderr
   to F, exits non-zero). Any other error → refuse the same way.
4. The descriptor stays open for W's whole life and is never passed on (`O_CLOEXEC`; every child is spawned with
   close-on-exec descriptors only). The lock is released when W exits.

**No byte write.** `flock` needs no write access and changes neither content nor metadata, the descriptor is
read-only, and the file is root-owned 0440. The lease therefore causes no frame mutation outside g, so no
outside-tree classification is needed. Because the lock inode is root-owned in a root-owned directory, the frame
plan's N07 "stable cooperating lock inode" ceiling does not apply to the writer lease. It still applies to the shared
window lock, which is unchanged (§9.4).

### 5.2 What the writer may mutate (the complete list)

| Mutation | Where | When | Parent writable by |
|---|---|---|---|
| create g, its ACL, `commits/`, `attempts/<A0>/`, `generation.json` | `runs/` and g | `materialize` M4 | `runs/`: W only; g: W only |
| inputs, snapshot, recipe files/directories/modes, partition roots and their ACLs, `materialization.json` | g (P_adm) | `materialize` M6-M8 | W only (recipe directories are 0755 owned by W) |
| `attempts/<A>/**` records, markers, fallback-journal slots, stream files (create only) | P_att | `materialize`, `dispatch` | W only |
| `attempts/<A>/front/**` front records | P_att | `seal-front` (W2) | W only |
| `export/**` copies, manifest, freeze record, their ACLs | P_exp | `materialize` M9, `dispatch` D14 | W only |
| sacrificial `runs/selftest-<hex>/**` | own sacrificial g | `selftest` | W only |

Nothing else. In particular W writes nothing in `lease/` (§5.1), nothing in partition contents, nothing outside
`runs/`, and creates no temporary file anywhere. Post-run work (conclusion, exports, the front's terminal record) is
in the table: every one of those writes goes through a W-exclusive parent.

**W2 (`writer.py seal-front <N_F> <g> <A>`).** It takes the lease like any writer and may only create new records in
`attempts/<A>/front/`. It verifies its capability before writing: W2 reads `/proc/<W2's parent>/stat` (the S3 sudo
process) and `/proc/<S3's parent>/stat`, and the latter's `(pid, start_time_ticks)` together with the current boot id
must equal the front-process triple committed in `attempt.json`. A different `sicarii` process cannot satisfy that,
because the kernel assigns pids and start times. W2 never modifies an existing record.

### 5.3 Entrypoint closure

A process can carry a given uid or gid only through: inheritance from a process that already has it; a privileged
credential change by root or by a holder of `CAP_SETUID`/`CAP_SETGID`; executing a set-user-ID or set-group-ID file;
executing a file with file capabilities; or user-namespace mapping, which `newuidmap`/`newgidmap` permit only within
`/etc/subuid`/`/etc/subgid`. The table closes each route for each new identity. "Check" means a setup prestate or
verification item (§11.3, §11.6) and, where marked, a per-invocation check by the frame.

| Route | `wlscratch` (W) | `wlscratch-run` (R) | `wlscratch-gate` (GATE) |
|---|---|---|---|
| sudo | only rule naming W: `sicarii ALL=(wlscratch) NOPASSWD: <writer entry> *`; no other sudoers rule lists W in a Runas or user list, and no `sicarii` rule has Runas `ALL` without a password (operator inventory) | only rule: `wlscratch ALL=(wlscratch-run : wlscratch-gate) NOPASSWD: <launcher entry> *`, usable only by W | conferred only by that rule's `-g` (Option A) or by RL (Option B) |
| user manager | no linger; `sudo`'s PAM session uses `pam_systemd.so class=none` (observed in `/etc/pam.d/sudo`); probe P-MGR verifies that no `user@W.service` and no `/run/user/W` appear | linger (needed for the scope); its manager can start only units that are not masked (§11.5 S-F) or that R's own processes create; per-user masks are root-owned under a root-owned home, so they cannot be removed by R | the manager's units run with R's default credentials, without GATE |
| sshd (active: observed `ActiveState=active`) | `DenyUsers wlscratch wlscratch-run` drop-in (§11.5 S-E); home root-owned, so no `authorized_keys` can be planted; no userdb record with keys (`userdbctl`) | same drop-in; home root-owned | not a login identity |
| login, getty, display manager | shell `/usr/bin/nologin`, password locked | same | n/a |
| PAM account controls | `sudo` uses `system-auth` (`pam_unix` account, `pam_time`) for the invoking user and opens its session with `pam_systemd.so class=none` (that no user manager results for W is probe P-MGR); login services (`system-login`) add `pam_access`, `pam_nologin` and `pam_shells`; the locked password makes every password authentication fail; account expiry (`usermod -e 1`) is applied only at rollback, because sudo must still reach the accounts while they are installed (observed stacks, P10) | same | n/a |
| `su`, `runuser` | `su` needs the target's password (locked); `runuser` is root-only (`pam_rootok`) | same | `newgrp`/`sg` need a group password: none is set (`gshadow` entry locked) |
| polkit, `pkexec`, `run0`, `machinectl` | require admin authentication (`unix-group:wheel`, interactive); no rules.d grant (operator inventory); `empower` empty | same | same |
| cron, at | not installed: `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch` absent, cronie and atd not found, no spool directories (observed 2026-10-04); re-checked at setup and by W at every invocation (absence of those paths) | same | n/a |
| system units, D-Bus system services | no unit or D-Bus service file references W (operator `grep -r` inventory of `/etc/systemd`, `/usr/lib/systemd`, `/usr/share/dbus-1`, `/etc/dbus-1`) | same, except the user@R.service instance created by linger | none references GATE |
| setuid/setgid files and file capabilities | none owned by W (operator `find / -xdev \( -uid W -o -gid W \)` empty before and, apart from setup objects, after); no untrusted code ever runs as W | none owned by R at setup. A target could otherwise mint a set-user-ID-R file anywhere it can write (`/tmp` and the other places of §12.3 are on the `suid`-enabled root filesystem). That would confer only R, which reaches nothing in g (g's ACLs name GATE, §6.3), and any process holding R is an unknown participant (§9.4) | the decisive route: a target holding GATE could chgrp a file to GATE and set the set-group-ID bit, and anyone executing it would gain GATE. C therefore sets `no_new_privs` and installs the anti-setid seccomp filter of §9.3 (step C9) before `exec` of T; the filter is inherited by every descendant. Processes outside T's tree that lack GATE cannot create GATE-group setid files (not members). The frame also refuses any set-user-ID or set-group-ID leaf it meets in g (§6.5), and every admission stage and the terminal check refuse any unknown GATE holder (§9.4) |
| user namespaces | W is outside every subordinate range; no range is allocated to W | same for R | GATE outside every subordinate gid range |
| existing processes | none at setup; afterwards only W instances (S1/S3 children) | the manager and its unmasked baseline, and L/C/T/O | only L/C/T/O and their descendants |

### 5.4 Subordinate-ID exclusion

Observed `/etc/subuid` and `/etc/subgid` (identical): `sicarii:100000:65536`, `cosmov1lab:165536:65536`,
`wlrehearsal:231072:65536`, `wldrill:362144:65536`, `worldline:296608:65536`. Every new uid and gid must lie outside
every listed range and no range may be allocated to a new identity. That keeps `sicarii` (and every other user) from
mapping them through `newuidmap`/`newgidmap`. Policy, checks and the post-setup re-check are in §11.2.

## 6. Modes, ACLs and access paths [gap: per-entry-modes-acls]

### 6.1 The v5 recipe and record modes are preserved exactly

v5 semantics (S:308-327, 913, 995-1026, 1992): the process umask is 077; `write_bytes` creates with 0600 and then
`fchmod`s to the requested mode (default 0600, so every JSON record and stream is 0600); created directories are
authenticated at 0700; the overlay snapshot keeps 0600 files in 0700 directories; recipe directories are created 0700
and then set to their base directory mode, deepest first, the root last; recipe files are written with their row's
mode (the base inventory mode, or 0644 for a new overlay unit).

W-1 keeps every one of these. **No ACL is set on any recipe object, frame record, snapshot entry, stream file,
marker or journal, and no default ACL exists anywhere in the design**, so the umask 077 semantics apply exactly as in
v5 to everything W and the target create.

Recipe-mode property, observed on the pinned base (inventory `943ea95e…3bf`, directory modes `1049c831…bde`): 635
files, 617 with mode 0644 and 18 with mode 0755 (617 + 18 = 635, JACKAL exact, parsed `617+18`); 55 directories, all
0755. Overlay units take a base mode or 0644. Every recipe file is therefore others-readable and every recipe
directory others-readable and others-searchable. W records this as `recipe_mode_property` at M7. It is not a new
refusal of an accepted case: for the pinned base it holds row by row, and a base with other modes would be a
different pinned base, which is itself a reviewed change.

### 6.2 Why ACLs never touch a mode that is recorded

POSIX ACL semantics (acl(5)): a named-user or named-group entry requires a mask entry; `stat` reports the mask in
the group bits of `st_mode`; `chmod` rewrites the mask. A named entry on a 0600 file therefore shows as 0640 or 0620
and changes the observed mode. A default ACL on a directory replaces the umask for new entries (their ACL is derived
from the default ACL and the creating mode), so a default ACL inherited "under 0600" does not give the promised read
access and silently changes creation semantics. v3 therefore puts ACLs only on objects whose modes are not part of
the recipe or of any v5 record, and puts no default ACL anywhere:
- setup objects `/var/lib/wlscratch` and `runs/`;
- the generation root g (created 0700, authenticated at 0700 by `Dir.child(create=True)`, then given its ACL; v5
  records no mode for its run directory);
- the four partition roots (v5 records partition identities but never partition directory modes, S:502-503);
- export directories and export files, which are new writer-produced copies with their own declared modes;
- Option A only: `/home/sicarii` (operator-captured before and after, §11.5 S-G).

### 6.3 Per-object owners, modes and ACLs

ACLs are written by W through `fsetxattr(fd, "system.posix_acl_access", …)` on the held descriptor (POSIX ACL xattr
version 2 encoding; entries sorted by tag then id) and read back with `fgetxattr` plus `fstat`; a mismatch refuses.
Setup ACLs are written by `setfacl` as root and read back with `getfacl -n`. "GATE" and "W", "R" are numeric ids;
`1000` is `sicarii`.

| Object | Owner:group | Base mode | Access ACL (`getfacl -n` order) | `st_mode` shown | Default ACL |
|---|---|---|---|---|---|
| `/var/lib/wlscratch` | root:W | 0750 | `user::rwx user:1000:--x group::r-x group:GATE:--x mask::r-x other::---` | 0750 | none |
| `lease/` | root:W | 0750 | none | 0750 | none |
| `lease/writer.lock` | root:W | 0440 | none | 0440 | n/a |
| `runs/` | W:W | 0700 | `user::rwx user:1000:--x group::--- group:GATE:--x mask::--x other::---` | 0710 | none |
| g | W:W | 0700 | same text as `runs/` | 0710 | none |
| `generation.json`, `materialization.json`, `inputs/**`, `commits/**` | W:W | 0600 files, 0700 dirs | none | same | none |
| `overlay-snapshot/**` | W:W | 0600 files, 0700 dirs (v5) | none | same | none |
| `source/` and every recipe directory | W:W | recipe mode (0755 for all 55 observed) | none | same | none |
| recipe files | W:W | recipe mode (0644 or 0755 observed) | none | same | n/a |
| `obj/`, `lib/`, `resource-tests/obj/`, `resource-tests/bin/` roots | W:W | 0700 | `user::rwx group::--- group:GATE:rwx mask::rwx other::---` | 0770 | none |
| partition contents | created by T: uid R, group GATE | as created under umask 077 | none set by the frame | as created | none |
| `attempts/**` records, markers, `fallback.journal`, stream files | W:W | 0600 files, 0700 dirs | none | same | none |
| `export/` and every directory below it | W:W | 0700 | `user::rwx user:1000:r-x group::--- mask::r-x other::---` | 0750 | none |
| export files | W:W | 0600 | `user::rw- user:1000:r-- group::--- mask::r-- other::---` | 0640 | n/a |
| `/var/lib/wlscratch-run` | root:root | 0755 | none | 0755 | none |
| `/var/lib/wlscratch-run/tmp` | R:R | 0700 | none | 0700 | none |
| `/var/lib/wlscratch-run/.config`, `…/systemd`, `…/systemd/user` | root:root | 0755 | none | 0755 | none |
| mask links in `…/systemd/user` | root:root symlink → `/dev/null` | n/a | n/a | n/a | n/a |
| `/opt/wlscratch`, `/opt/wlscratch/frame-v6w1/**` | root:root | 0755 dirs, 0644 files | none | same | none |
| `/opt/wlscratch/setup-identities.json` | root:root | 0644 | none | 0644 | n/a |

### 6.4 Access paths

- **The target reads admitted source** through `/var/lib/wlscratch` (GATE `--x`), `runs/` (GATE `--x`) and g (GATE
  `--x`), then through the recipe's own others bits (0755 directories, 0644/0755 files). It writes only partition
  contents, through the roots' GATE `rwx` and its own ownership of what it created, and its stream files, through
  descriptors it was given. It never needs write access to a recipe directory, because the partition roots exist
  before it runs.
- **C and O** use the same path as the target. They read partition contents as their owner (uid R). As in v5, where
  the frame ran as the target's owner, a target-created object without owner read permission yields an observation
  failure and a non-success outcome.
- **The writer never opens a target-owned object.** Its own walks treat the four roots as opaque (root identity,
  mode and ACL only). It receives partition observations and the report bytes (`obj/core/gnatprove/gnatprove.out`) from
  O over the channel and writes its own copy, as v5 copied the report (S:1696-1708).
- **The lead reads evidence only from P_exp**, through `user:1000` entries on `/var/lib/wlscratch`, `runs/` and g
  (`--x`) and on the export directories and files (`r-x`, `r--`). The lead could also read the recipe, which is its own
  base content; nothing else in g has an entry for it.
- **Background processes of the target account** (uid R without GATE) have no entry on `/var/lib/wlscratch` and fall
  to `other::---`, so they cannot reach g by path at all.
- **Pre-created partition roots.** v5's target created `obj/` and the other partition directories itself, inside a
  source tree it owned. Under W-1 the writer creates the four roots at M7 (empty, writer-owned, GATE `rwx`), so the
  target never needs write access to a recipe directory. The partition paths, their exclusion rules and the
  allowlisted commands are unchanged; v5's "no generated output at materialization" check becomes "exactly the four
  empty writer-created roots at materialization", which is stricter for everything else. The only behaviour the
  target loses is removing or renaming a partition root itself. No allowlisted action (gnatprove proof actions,
  `gprbuild -p -c`) is known to do that; this is a compatibility hypothesis that the first engineering run's evidence
  must confirm. If it is false, W-1 must be redesigned; the accepted case is not narrowed.

### 6.5 Denial matrix (each cell is a probe in §13)

| Object | `sicarii` (A1) | T, C, O (R + GATE) | background R (no GATE) | W |
|---|---|---|---|---|
| `/var/lib/wlscratch` | search only | search only | none | read, search |
| `lease/`, `writer.lock` | none | none | none | search; open read-only and `flock` |
| `runs/`, g | search only | search only | none | full (owner) |
| P_adm records, `inputs/`, snapshot, `commits/` | none | none | none | full (owner); code writes create-only |
| recipe directories | read, search | read, search | none | full (owner); code does not mutate after M8 |
| recipe files | read | read | none | owner; code does not mutate |
| partition roots | none | create, rename and unlink entries | none | owner; code never uses |
| partition contents | none | owner of what T created | none | none |
| P_att | none | none (stream bytes only through passed descriptors) | none | full (owner) |
| P_exp | read | none | none | full (owner) |
| `/var/lib/wlscratch-run/tmp` | none | owner | owner | none |

In every cell marked "none" or "read"/"search", every mutation (create, `mkdir`, `unlink`, `rmdir`, `rename` in or
out, `link`, `symlink`, `open` for write, `truncate`, `chmod`, `chown`, `setfacl`, `utimes` with explicit times) must
fail with `EACCES` or `EPERM`. `fs.protected_hardlinks=1` refuses hard links of another owner's files. The frame's
walks additionally refuse any symlink, special file, multiply linked regular file, and (new in W-1) any set-user-ID or
set-group-ID leaf in g.

## 7. Channels, expectations and dumpability [gap: channel-and-dumpability]

### 7.1 Channels and transports

| Channel | Transport | Created by | Carries |
|---|---|---|---|
| F↔W (and F↔W2) | three pipes: F→W on W's fd 0, W→F framed messages on W's fd 1, W→F diagnostics on W's fd 2 | F, after its first act; F's ends close-on-exec | inputs, observations, requests, answers, record descriptors |
| W↔L | `AF_UNIX`/`SOCK_STREAM` socketpair on L's fd 0; L's fd 1 and fd 2 are `launcher.stdout`/`launcher.stderr` in P_att, opened create-only by W | W | `GO` with record bytes, stream descriptors by `SCM_RIGHTS`, relayed C messages, `STOP` |
| L↔C | socketpair on C's fd 0 (systemd-run's stdin, kept by the scope `exec`); C's fd 1 and fd 2 are `scope.stdout`/`scope.stderr` (W-created, passed through L) | L | child stage, `SPAWN_REQUEST`/`SPAWN_OK`, `child.stdout`/`child.stderr` descriptors for T, waits |
| W↔O | socketpair on O's fd 0; O's fd 1 and fd 2 are `observer-<n>.stdout`/`.stderr` | W | observation requests and results, report bytes |

`sudo` passes only fds 0-2 (its default `closefrom` is 3), so every helper gets exactly one bidirectional socket on
fd 0 and two W-created files on fd 1 and fd 2; further descriptors travel only by `SCM_RIGHTS`. Under Option B, RL
sits between S2 and L and passes L's fds through unchanged (§12.2).

### 7.2 Canonical encoding and framing

- **Frame**: an 8-byte unsigned big-endian length `n`, then `n` payload bytes, `1 ≤ n ≤ MAX_FRAME`,
  `MAX_FRAME = 67108864` (JACKAL exact, parsed `64*2^20`).
- **Payload**: the canonical JSON of an object with exactly the keys `body`, `kind`, `prev`, `seq`:
  `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)`, encoded as ASCII.
- **Strict decoding**: ASCII only; `json.loads` with hooks that reject floating-point numbers (`parse_float`),
  `NaN`/`Infinity` (`parse_constant`) and duplicate keys (`object_pairs_hook`); nesting depth at most 32; every number an
  integer with absolute value below 2^63; and the payload must equal its canonical re-encoding byte for byte.
- `seq` counts from 0 per direction; `prev` is 64 lowercase hex; `kind` must be allowed in the current protocol state;
  `body` must have exactly the key set and types of the kind's schema (Appendix B.4).
- **Bulk bytes** (input files, record bytes delivered to C, report bytes from O) travel as `BEGIN {name, size, mode,
  sha256, chunks}`, then `chunks` × `CHUNK {index, data_b64}` of at most `CHUNK = 4194304` raw bytes each (JACKAL
  exact, parsed `4*2^20`), then `END {sha256}`. The receiver checks index order, count, size and sha256. Base64 of a
  full chunk is at most 4·(CHUNK+2)/3 bytes, leaving 61516456 bytes of `MAX_FRAME` for the envelope (JACKAL exact,
  parsed `67108864-4*(4194304+2)/3`). Inputs of any size are streamed in chunks and never refused for size. An
  over-length header can only come from a non-conforming sender and is a protocol violation, not an input-size refusal.
- **Observation results and record bytes are bulk bytes.** Front stage results, observer results, relayed child
  records and receipts travel as `BEGIN`/`CHUNK`/`END` carrying their own JSON encoding (v5 `write_json` form), so the
  strict envelope rules (for example, no floating-point number) constrain only control bodies and never the content of
  a v5 observation (v5 observations contain floating-point fields such as `transcriptSilenceSeconds`). The receiver
  parses bulk JSON with the v5 readers after the digest check.

### 7.3 Chain initialization, validation and retained form

- `head0(dir)` is defined in §4.4. The receiver of message k of a direction requires `seq == k` and
  `prev == head_k`, then sets `head_{k+1} = SHA256(bytes.fromhex(head_k) ‖ payload_k)`. The prototype implements the
  same recurrence (ENGINEERING_ONLY).
- `W_HELLO` (first `W2F` message) carries W's nonce `N_W` and W's identity; `HELLO_ACK` (first `F2W` message) echoes
  `N_W` and carries F's identity. Each side refuses a hello whose identity fails §8.1's joins.
- W retains the channel as create-only segment records `attempts/<A>/channel/<first-seq>-<last-seq>.json`, written at
  every phase boundary and at conclusion, each with a marker. A segment holds, per message, `{dir, seq, prev, kind,
  length, payload_sha256}` and the payload, except that bulk chunk data is replaced by a reference `{record, offset,
  length, sha256}` to the committed bytes it became. A verifier reconstructs every payload and recomputes both chains.
  If W dies, messages after the last committed segment are durability-UNKNOWN (§10.4); records still carry the heads.
- F writes nothing; it keeps both heads in memory and its terminal record (committed through W2) carries them.

### 7.4 Rejection rules

- EOF at a frame boundary in a state that permits it (after `BYE`, or the states so marked in Appendix B.4) is a clean
  end.
- Everything else is a **channel failure**: EOF inside a frame or in any other state; `n == 0` or `n > MAX_FRAME`;
  non-ASCII, non-canonical, duplicate-key, floating-point or non-finite payload; wrong key set; `seq` out of order;
  `prev` not the current head; a kind not allowed in the state; a body schema mismatch; a chunk index, count, size or
  sha256 error; an expired deadline. The receiver stops reading that channel, retains the raw bytes of the failing
  frame (if any) as a raw record, never acts on a later message and proceeds by §9.5.
- Deadlines (judgments, not bounds): v5's 300 s first byte and 30 s completion for an answer line, unchanged; v5's
  30 s per subprocess observation, unchanged; 600 s for a front stage-observation set; 60 s for a control reply
  (acknowledgement, `GO`, `SPAWN_OK`). Before launch an expired deadline refuses (nothing reserved or launched, as
  applicable). After launch it is recorded and never stops the wait for participants.

### 7.5 In-memory expectations (the v5 admission protocol's, carried)

| Expectation | Held by | Compared with |
|---|---|---|
| challenge (each memory challenge, and the Gate 0 receipt challenge of §14.3) | W: the pin of the `challenge.json` it committed and the expression it issued | the answer's `challenge_sha256`; the receipt row's `parsed`, `status`, `formal`, `exact`; no receipt hash reused within the attempt (v5 S:1195-1248) |
| lead | F and W: `claude_lead.LEAD_ID` (W from the verified lead-module bytes) | every front observation's `leadId`, the window `holder_task`, `launch.json` `holder` (v5) |
| window | F: token, holder, candidate path, the reservation record descriptors W returned | `owns_window` under the window lock; W's conclusion message; release (v5) |
| argv | F: W's exact argv; W: S2/L, S_O/O and W2 argv, the scope and C templates; C: its own sealed command line | `/proc/<pid>/cmdline` read by the parent role, `SUDO_COMMAND`, C's `/proc/self/cmdline` (v5 S:1786-1791) |
| records | W: every marker it wrote (journal); F: every descriptor it was sent | conclusion re-reads every journaled record (v5 re-read seven); drift is an error |
| exports | W: the export manifest; F: the manifest digest in `FINAL` | F re-reads every export file through its ACL and compares |
| participants | W: S2, L, SR/C, T, O, W2 identities (§9.1); F: S1, W, W2 and those relayed | the terminal scans (§9.4) |

No re-read local record defines its own expectation (v5 V4-B03 rule).

### 7.6 Integrity is not sender authentication

The chain shows that the receiver saw exactly the ordered bytes written by whoever holds the other end, with no loss,
reordering or alteration in transit. It does not show who that is. For F, the other end of the W pipes is the process
F started: F created the pipes after becoming non-dumpable, kept its own ends close-on-exec, and requires W's reported
`fstat` of fds 0-2 (`S_ISFIFO`, `[dev, ino]`) to equal its pipe inodes. For W, the other end is "the `sicarii`
process that invoked `sudo` and kept the pipe", which W cannot distinguish from any other `sicarii` process. The lead
is therefore authenticated only by the original v5 joins (§2.4 R2). W-1 makes them neither weaker nor stronger, and
this is the original v5 engineering ceiling, not a newly accepted residual.

### 7.7 Dumpability: set, read back, when

- **First act.** Each entry script (`front.py`, `writer.py`, `launch_target.py`, `sandbox_launch.py`) begins, before
  importing anything but `sys` and `ctypes`: `libc = ctypes.CDLL(None, use_errno=True)`;
  `libc.prctl(4, 0, 0, 0, 0)` (`PR_SET_DUMPABLE`, 0) must return 0; `libc.prctl(3, 0, 0, 0, 0)` (`PR_GET_DUMPABLE`) must
  return 0; `os.stat('/proc/self/fd').st_uid` must be 0 (the kernel makes a non-dumpable process's `/proc/<pid>`
  entries root-owned; `os` is already loaded by interpreter start-up, so binding it loads nothing new). On any failure the process writes one line to stderr and exits 125 with no other action. Both
  readbacks go into its role identity (§8.1). `/proc/self/status` has no `Dumpable` field on this host and is not used.
- **Relative to start-up.** Before the first act come: the dynamic loader, `libpython` initialization, the encodings
  import, `site` (for F including the user site directory and its `.pth` processing; for the `-I` helpers only the
  system site), and `import ctypes` with its own imports. Only then the two `prctl` calls, then the `sys.flags` checks
  of §8.2, then every other import.
- **Each invocation.** `execve` resets the attribute (to 1 when the credentials do not change in the exec), so every
  process sets it itself: F, W, W2, L, C (after systemd-run's `exec` into it), O and RL. T does not (R3).
- **Pre-first-call residual, per role.** F (uid 1000) is readable by every `sicarii` process until the call: its
  environment, command line and inherited descriptors (Yama still blocks attach). Its channel pipes are created after
  the call and are never exposed. W and W2 are readable only by other `wlscratch` processes (frame writer instances)
  and root. L, C and O are readable by other `wlscratch-run` processes (the manager baseline) until the call; their
  channel sockets cannot be reopened through `/proc` and their stream files are W-owned 0600. The window's duration is
  not measured; probe P-DUMP timestamps it. This residual is stated, not accepted as a new guarantee.

## 8. Fresh identities, the real outer invocation, context relocation and the vault [gap: fresh-identities-and-vault]

### 8.1 Per-invocation role identity

Every process of every invocation records a fresh `wlscratch-role-identity-v1` (Appendix B.1) immediately after its
first act (§7.7). It contains: role; boot id; pid, ppid, `start_time_ticks` (field 22 of `/proc/self/stat`); comm;
argv (`/proc/self/cmdline`); exe (`readlink /proc/self/exe`, `[dev, ino]`, sha256); all four uids and gids and the
supplementary groups (`/proc/self/status`); capability sets, `NoNewPrivs` and `Seccomp`; both dumpability readbacks;
umask; resource limits; cgroup (`/proc/self/cgroup`); mount, pid and user namespace inodes; cwd `[dev, ino]`; for fds
0-2 the file type, `[dev, ino]`, mode and open flags, and the full list of open fds; the environment as sorted names
plus the sha256 of every value, with clear values only for the non-secret keys `HOME USER LOGNAME LANG PATH SHELL PWD
TMPDIR XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS INVOCATION_ID SUDO_USER SUDO_UID SUDO_GID SUDO_COMMAND` and every
`PYTHON*` key; Python `sys.version`, `sys.executable`, prefixes, every `sys.flags` field and `sys.path`; and the loaded
module closure (every `sys.modules` entry with a file: name, path, size, sha256; builtin names listed). The parent role
independently reads the child's `/proc/<pid>/{stat,status,cmdline,cgroup}` and joins them with the child's
self-report (pid, start time, credentials, command line); a mismatch refuses before launch and is an error after.

Per stage, in addition (each a fresh observation, never reused across stages or attempts):

| Role | Parent stage | Child stage | After (conclusion) |
|---|---|---|---|
| F (real lead context) | fresh lead observation `scratch-run`; frame admission front part; base-tree re-observation; v5 runtime-closure observation with the **original** unrelocated spec against the **original** baseline (compact if equal, v5 item 4); `systemctl --user show-environment` of `sicarii`'s manager against the original `manager_environment` baseline; sibling units and `storage_status.py` | the same set with stage `scratch-child`, and the window ownership check | the same set except the lead observation, as v5 conclusion re-ran frame admission and identities |
| W | own identity against the reviewed writer-context baseline (system standard library only, `-I` flags) | lease, location, snapshot, record-drift writer half | same, plus the conclusion of §9.4 |
| O (target context) | full walk; tool, proof-data, proof-ELF, vendor and runtime-closure observations with the relocated spec; R's manager environment; the scans of §9.4 | n/a | same as parent, plus the report bytes |
| C (target context) | n/a | v5 child admission in full (§9.3 C1-C11), with the same observations as O and the final pass | n/a |

### 8.2 The real non-isolated outer invocation is kept

The front is the lead's real outer invocation and keeps the original shape: `/usr/bin/python3 -B
/opt/wlscratch/frame-v6w1/front.py <verb> …`, with no added `-I` (HANDOFF.md:177: "Retain the real non-isolated outer
invocation (no added -I)"). F requires `sys.flags.isolated == 0`, `ignore_environment == 0`, `no_user_site == 0`,
`safe_path == 0`, `optimize == 0`, `dont_write_bytecode == 1`, and that `sys.executable` resolves to
`/usr/bin/python3.14` with the reviewed digest. F's runtime and manager observations use the original specifications
and baselines, because F runs in the original `sicarii` context. The helpers (W, W2, L, C, O, RL) run with `-I -B` and
require `isolated == 1`, `optimize == 0`, `dont_write_bytecode == 1`. The frame plan's H-M7 ("every verb runs -I") is
applied to helpers only. Helper observations are additional; none replaces F's. The inherited bootstrap ceiling (N08:
`site`, `.pth` and cached state before main) applies to F unchanged.

### 8.3 The original target path and caps are kept

- `child_argv` is exactly v5 `command()`: `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove -P
  core/worldline_core_sources.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on -j2`
  (with `-k` for `prove-all-k`), the `prove-file`/`prove-subp` forms, or the `gprbuild … -p -j2 -c -U` form for
  `compile-all`. The path is executed as written (R4); Options A and B both make that exact path resolvable (§12).
- The scope is `systemd-run --user --scope --unit=<U> -p MemoryMax=8G -p MemorySwapMax=0`; `RLIMIT_CORE` is (0, 0)
  from L's pre-exec of systemd-run and is inherited; C reads back `memory.max == 8589934592`, `memory.swap.max == 0`,
  core `[0, 0]` and its scope membership (v5 S:1828-1838). `-j2` stays in the argv.
- `MIN_MEM_AVAILABLE_KB = 16777217`, `MAX_CHALLENGES = 3`, the 300 s and 30 s receipt deadlines and the 30 s
  observation timeouts are unchanged; the target executable's digest is checked against the baseline before the spawn
  (v5 S:1839-1841).
- W-1 adds two restrictions on T and changes no cap: `no_new_privs`, and the anti-setid seccomp filter (§9.3 C9),
  both needed so that T cannot mint a GATE-conferring file (§5.3). They are reviewed deltas with a compatibility
  hypothesis: no allowlisted action sets set-user-ID or set-group-ID bits or relies on `io_uring` or `openat2`. If
  that is false, W-1 must be redesigned; no accepted case is narrowed.

### 8.4 Context relocation table and the new baselines

The target now runs as R, so the account-bound part of its environment must change. Nothing else may. v5 already
relocated four source-bearing keys and one runtime-closure entry to the run's source (S:1077-1095); W-1 keeps that
rule (with g's source path) and adds exactly these relocations:

| Key or entry | v5 value and source | W-1 value |
|---|---|---|
| `HOME` | `/home/sicarii`, from the run's environment (`KEEP_ENVIRONMENT`) | `/var/lib/wlscratch-run` |
| `USER`, `LOGNAME` | `sicarii`, same | `wlscratch-run` |
| `LANG` | the lead environment's value | the lead environment's value, as observed by F and streamed (unchanged) |
| `XDG_RUNTIME_DIR` | `/run/user/1000` (tool spec) | `/run/user/<R>` |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/run/user/1000/bus` (tool spec) | `unix:path=/run/user/<R>/bus` |
| `TMPDIR` | `/home/sicarii/.cache/workflow-tmp` (runtime spec) | `/var/lib/wlscratch-run/tmp` |
| runtime-closure `mutable_directory_identities` entry for `TMPDIR` | `/home/sicarii/.cache/workflow-tmp` | `/var/lib/wlscratch-run/tmp` |
| runtime-closure tree `/home/sicarii/.local/lib/python3.14/site-packages` | `sicarii`'s user site, observed | `/var/lib/wlscratch-run/.local/lib/python3.14/site-packages`, required absent |
| `PENDING_LIBRARY_DIR`, `PENDING_OBJECT_DIR`, `PYTHONPATH`, `WORLDLINE_CORE_LIB`; runtime entry for the source | F10K source path | g's source path (v5 rule) |
| `PATH`, `GPR_PROJECT_PATH`, `GNAT_ROOT`, `WORLDLINE_BUILD`, `PYTHONDONTWRITEBYTECODE`, every `null` key | spec | unchanged, byte-identical |

`HOME` itself is root-owned and not writable by R (§6.3, S-F), so that no `~/.ssh/authorized_keys` and no persistent
user unit can be planted there; v5's target could write its `HOME`. This is a compatibility hypothesis: the
allowlisted actions write their outputs to the object directories and `TMPDIR`, not to `HOME`. The first engineering
run's evidence must confirm it; if it is false, W-1 must be redesigned and the accepted case is not narrowed.

New baselines, each reviewed installed evidence before adoption (§16): the relocated runtime-closure inventory (the
v5 inventory with the user-site subtree removed and recorded absent, the `TMPDIR` row replaced by R's directory row,
the source row relocated); R's manager environment; the writer-context baseline. The tool, proof-data, proof-ELF and
vendor baselines are expected byte-identical in the target context, because the toolchain files are the same; any
difference keeps the full observation and refuses (v5 `retain_observation`), pending review. Under Option A, `PATH`
entries below `/home/sicarii` that are not others-searchable become unresolvable for T; under Option B every `PATH`
entry below `/home/sicarii` except the bound toolchain is absent (§12.2). The tool-inventory observation records the
effect, and its baseline for the chosen option is part of the reviewed installed evidence.

### 8.5 Vault scope

- **What is pinned:** P_exp(g), the path `g/export`, which `sicarii` can read through the ACLs of §6.3. The originals
  in g are unreadable to `sicarii`; they are neither pinned nor backed up by the vault. Their custody is the protected
  local tree.
- **Who and when:** F, as `sicarii`, runs `project-vault pin <g>/export` and `project-vault status` at M9 and at
  D6, each under the original 30 s observation timeout, keeping the authentic HOME, configuration, user bus, reserve,
  queue and backup state; W records the results (v5 S:1562-1563 did the same for its run directory). Both must succeed
  or the stage refuses, as in v5. `storage_status.py` and `project-vault` are never run as W or R.
- **Unverified:** whether project-vault backs up and restores a path outside `/home` correctly. Sacrificial
  verification V-VAULT (§13) is future evidence; until it passes, vault coverage of exports is not claimed and the
  Gate 0 restore term remains in full (§14).

### 8.6 Input classes (v2 §6.1 carried; the re-review closed W1-READ-ACCESS)

W reads nothing under `/home/sicarii`. F reads every lead-side input with the v5 anchored readers and streams it.
- **Pinned inputs**, verified by W against values compiled into the installed frame before any use: the three base
  descriptors (`BASE_BINDING_SHA256`, `BASE_INVENTORY_SHA256`, `BASE_DIRMODES_SHA256`, unchanged from v5); every base
  file (digest and size from the pinned inventory); the lead module (`LEAD_MODULE_SHA256`; W executes the verified bytes
  with v5 `exec_verified` only to read its constants and never calls `observe`).
- **Joined inputs**, verified structurally exactly as v5 does, because they postdate the frozen frame: the overlay
  (v5 `overlay_rules`: Ada units under `core/` and `DELETE.list` only; retained by digest in the snapshot); the frame
  review roster and the adoption record (v5 `review_profile_problems` and the adoption profile, with the review's and
  the adoption's `frame_inventory_sha256` equal to the sha256 of the installed `frame-inventory.json`).
- **Observations**, recorded with digests at v5's trust (R2): F's lead observation, rollout join and
  adoption-observation/transcript-prefix results, base-tree re-observation, window snapshots, storage readings, vault
  results, sibling units, F's runtime and manager observations, and F's identity.

A concurrent `sicarii` change to a home file between F's read and W's use yields the pinned bytes or a refusal for a
pinned input; for joined inputs and observations the trust is v5's. After materialization the admitted copy exists only
in g. No ACL is added for W anywhere under `/home/sicarii`, and the frozen 0600 review files keep their modes.

## 9. Participants, waits, launch gating, terminal ownership and recovery [gap: participants-and-recovery]

### 9.1 Participant set and schemas

Participants of attempt A: S2, L, SR/C (one pid: systemd-run `exec`s C inside the scope), U, T and all its
descendants, every S_O/O, and S3/W2; under Option B also RL. F and W are the owner processes (as v5's dispatch and
run). Schemas (Appendix B.2): `wlscratch-participant-v1` `{role, pid, start_time_ticks, boot_id, ppid, uids[4],
gids[4], groups, cmdline, cgroup, observed_by, at, state ∈ {alive, absent, reused, unknown}}`; `wlscratch-wait-v1`
`{waiter_role, waited_role, pid, start_time_ticks, boot_id, raw_status, exited, exit_code, signaled, signal,
core_dumped, wait_error, interrupts, unresolved, at, meaning}`; `wlscratch-scope-v1` `{manager_uid, unit,
invocation_id, control_group, properties_at_start, properties_at_end, cgroup_state ∈ {ABSENT, EMPTY, NONEMPTY,
UNAVAILABLE}}`. A process is identified by `(pid, start_time_ticks, boot_id)`: a different start time at the same pid
means the original ended and the pid was reused; a different boot id means the original ended with its boot.

O's jobs per invocation: the scans of §9.4 that need R credentials (`SCAN-UNITS`, `SCAN-REFS`), the full walk of
`g/source` (v5 `verify_materialization` with v6's final pass, returning every excluded leaf's `stat_key`), the
target-context identities (`parent` or `after`), and at `after` the report bytes.

### 9.2 Waits, reaping and relay

| Waiter | Waits for | Mechanism | Retained as |
|---|---|---|---|
| F | S1, and through sudo's relay W | `waitpid` on S1 (F's child) | front terminal record via W2: S1's raw status, W's self-reported final status (from `FINAL`), and W's `(pid, start)` absent or reused afterwards |
| F | S3 (W2) | `waitpid` | console only. It is the last wait, as v5's lead wait of `dispatch` was |
| W | S2 (and L through relay), each S_O (O) | `waitpid` | `sudo-launcher-wait.json`, `observer-wait-<n>.json` |
| L | SR = C | `waitpid` | relayed and committed as `launcher-wait.json` (v5 meaning: the actual wait of the systemd-run scope launcher) |
| C | T | `waitpid` (`wait_blocked`) | relayed and committed as `child-wait.json` (v5) |

Every wait record is committed before any cleanup (v5 V4-B02 rule). Relay evidence: `sudo` reports the command's
status; whether it re-raises a fatal signal is probe P-RELAY. The parent role always keeps both its direct child's raw
status and the grandchild's self-report; disagreement is an error. Each role reaps only its own children. An orphan
(a child whose parent died) is not waited for by the frame; it is observed by the scans until it ends. Handled
signals are blocked at the start of every role and consumed only synchronously (frame plan H-S1, H-M3).
`STOP` messages travel down the channels (F→W→L→C), and C forwards `SIGTERM` to T exactly as v5's `wait_blocked`
did. W cannot signal L or C (different uid) and does not try.

### 9.3 Launch gating

- G1. W commits `launcher-intent.json` and sends `LAUNCH_INTENT_COMMITTED` with its descriptor.
- G2. F sends `PROCEED_LAUNCH` only if it still owns the window and has had no channel failure.
- G3. W creates, create-only and 0600 in P_att, `launcher.stdout`, `launcher.stderr`, `scope.stdout`,
  `scope.stderr`, `child.stdout`, `child.stderr`; creates socketpair SP_L (its own end close-on-exec); starts S2 with
  fd 0 = SP_L's other end and fds 1-2 = the launcher files; commits `launcher-start.json` with S2's identity.
- G4. L: first act, identity, argv grammar; requires ruid = euid = suid = fsuid = R and rgid = egid = sgid = fsgid =
  GATE (under either option; Option B's RL produces the same credentials, §12.2), fd 0 a socket, fds 1-2 regular files;
  sends `L_HELLO`; waits for `GO` within the control deadline.
  **EOF or deadline before `GO` → L exits 125 having started nothing.**
- G5. W verifies L through `/proc/<L>` (credentials, `PPid == S2`, start time, cmdline) and sends `GO`: the bytes of
  `launch.json`, `admission.json`, `reservation-intent.json`, `reservation.json`, `launcher-intent.json` and
  `materialization.json` (chunked), and by `SCM_RIGHTS` the four scope and child stream descriptors.
- G6. L verifies the two seals (sha256 of the delivered `launch.json` and `admission.json` equal its argv) and that
  `launcher-intent.json`'s scope argv is exactly what it will run; sets umask 077 and `no_new_privs`; creates
  socketpair SP_C; starts SR = `/usr/bin/systemd-run --user --scope --unit=<U> -p MemoryMax=8G -p MemorySwapMax=0
  /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py child <N_C> <g> <A> <launch_sha> <admission_sha>`
  with stdin = SP_C's other end, stdout/stderr = the scope files, the environment of `launch.json`, and a pre-exec
  that sets `RLIMIT_CORE` (0, 0) and unblocks the handled signals (v5 `spawn`); sends `LAUNCHER_START`.
- C1. C (inside the scope after the `exec`): first act, identity; requires its `/proc/self/cmdline` to equal the
  sealed template plus `[N_C, g, A, launch_sha, admission_sha]`, its cgroup to end in `/<U>`, its credentials R/GATE,
  its parent to be L, `INVOCATION_ID` to be 32 hex, its environment minus `INVOCATION_ID` to equal `launch.json`'s,
  fd 0 a socket and fds 1-2 the scope files named in `launcher-intent.json`. (That C's pid equals SR's, because a scope
  `exec`s in place, is verified by probe P-LAUNCH; if systemd-run were to fork instead, C's parent would be SR and both
  identities would be recorded and joined.)
- C2. C receives the record bytes (relayed by L) and the stream descriptors, and verifies every v5 child join
  (S:1782-1817): both seals; `intent.launch` equals the delivered `launch.json` descriptor; `admission.launch` equals
  `intent.launch`; the `reservation.json` token taken from the `admission.json`-pinned record (frame plan H-M6) equals
  the intent's token; `launch.materialization` equals the delivered `materialization.json` descriptor.
- C3. C opens g and `source/` by anchored chains and requires their identities to equal the seal; the attempt and
  snapshot identities are checked by W in C4.
- C4. `CHILD_STAGE_REQUEST`. W performs the writer half (snapshot observation equals the record, attempt-directory
  identity equals the seal, every journaled record unchanged, lease held, location chain unchanged) and obtains F's
  child-stage half (§8.1: fresh lead observation `scratch-child`, `owns_window(LEAD_ID, attempt path, token)`, frame
  admission front part, base-tree re-observation, F's runtime and manager identity, the front half of the `child-final`
  sample with the reserve equal to the bound). W commits both halves and relays them.
- C5. C requires `launch.holder == LEAD_ID == intent.holder_task` and window ownership true (v5 S:1809-1811); runs
  the installed-frame inventory check, the target-context identities `child`, and the admission walk with source-tree
  identities equal to the seal (v5 S:1812-1813).
- C6. v5 S:1814-1841 in order: pins (frame inventory, review, adoption, materialization), environment, parent memory
  gate, the helper half of `child-final` (sibling units of R's manager allowing only U, heavy-process refusal, meminfo
  at or above 16777217 kB), cwd, allowlist re-derivation, limits readback, scope membership, target executable digest.
- C7. Scans (§9.4, child-stage form): GATE holders exactly {L, C}; R-uid processes ⊆ {L, C} ∪ B_mgr; R's manager units
  ⊆ B_mgr ∪ {U}; no B_mgr process holds a reference into g.
- C8. `SPAWN_REQUEST` with the digest of C's admission summary. W answers `SPAWN_OK` only if F answered a `PING`
  within the control deadline, W's error list is empty and the record journal is unchanged, and only after committing
  `spawn-ok.json`. EOF or deadline → C refuses (`child-refusal.json`, v5 meaning "nothing was started").
- C9. C prepares T's pre-exec: `fchdir` to the held `source` descriptor, `RLIMIT_CORE` (0, 0), umask 077,
  `PR_SET_NO_NEW_PRIVS` = 1, then the **anti-setid filter**: a classic seccomp BPF program for `AUDIT_ARCH_AARCH64`
  (any other arch: kill) that returns `EPERM` for `fchmod`, `fchmodat` and `fchmodat2` when the mode argument has any
  of the bits 06000, for `openat` and `mknodat` when the mode argument has any of those bits, returns `ENOSYS` for
  `io_uring_setup` and `openat2` (whose arguments a classic filter cannot inspect), and allows everything else; then
  unblock the handled signals. The filter and `no_new_privs` are inherited by every descendant and cannot be removed.
- C10. **Final pass** (§4.5) and `verify_location` of every held handle.
- C11. Pending-signal check (interruption point); spawn T with stdin `/dev/null`, stdout/stderr the child stream
  descriptors, the sealed environment, `child_argv`.
- C12. `CHILD_START` with T's identity; W commits `child-start.json` (v5) and tells F (`TARGET_STARTED`).
- Then C waits for T, retains `child-wait.json` before cleanup, closes the child streams (failures:
  `child-cleanup.json`) and exits by v5's rule; L retains its wait of SR/C and exits; W retains its wait of S2.

**Why a late launch after writer death is impossible except through an issued, recorded permission.** No L can do
anything without `GO` (G4), which only a live W sends, and only after `PROCEED_LAUNCH` and the committed launch
intent. No T can start without `SPAWN_OK` (C8), which only a live W sends after committing `spawn-ok.json`. A sudo
front-end (S2) that outlives W can only start an L, which then reads EOF and exits. So after W's death the only possible
future target is one whose C already holds `SPAWN_OK`; that C is a GATE holder and visible to every scan until it ends.
A scan that finds no GATE holder, no W-uid process and no process naming the attempt therefore proves that no launch
is pending, and an empty target-account or cgroup snapshot alone is never used for that conclusion.

### 9.4 Scans, known-terminal ownership and the release rule

Scans (all over the whole `/proc` of the initial pid namespace; `/proc` has no `hidepid`):
- `SCAN-GATE`: processes whose `Gid:` line (real, effective, saved, fs) or `Groups:` line contains GATE.
- `SCAN-R`, `SCAN-W`: processes whose `Uid:` line contains R, respectively W, in any position.
- `SCAN-NAME`: processes whose command line contains the attempt path or g (v5 `processes_naming`), excluding F, S1
  and W themselves.
- `SCAN-SCOPE`: U's cgroup below `user@R.service` absent or empty (`cgroup.procs` is world-readable).
- `SCAN-UNITS` (C or O only): R's manager's loaded units, timers, sockets and paths compared with B_mgr ∪ {U} at the
  child stage, with B_mgr elsewhere.
- `SCAN-REFS` (C or O only): for every B_mgr process, `/proc/<pid>/{cwd,root}`, every `/proc/<pid>/fd/<n>` and every
  file mapping in `/proc/<pid>/maps` is stat'ed; a `[dev, ino]` equal to any object observed in g by the same stage's
  walk is a reference into g.
- Recorded participants: each `(pid, start_time_ticks, boot_id)` classified alive, absent, reused or unknown.
Any unreadable entry needed by a scan makes that scan UNKNOWN, with one stated exception (R7): B_mgr's `(sd-pam)`
process may have root-owned `/proc` entries and is accepted with an unreadable descriptor table only if its parent is
R's manager, its start time precedes g's creation, and it is the only such process. **B_mgr** is the reviewed baseline
of R's manager after the setup masks (§11.5 S-F): the manager itself, `(sd-pam)`, and `dbus-broker-launch` and
`dbus-broker` if the inventory keeps `dbus.socket` (the original environment names the user bus), each identified by
uid, parent, cgroup path, comm and executable identity.

**Known-terminal ownership** of attempt A holds when: every recorded launch participant is absent or reused;
`SCAN-GATE` is empty; `SCAN-R` ⊆ B_mgr; `SCAN-W` ⊆ {the serving writer instance}; `SCAN-NAME` is empty; `SCAN-SCOPE` is absent or
empty; and no scan is UNKNOWN. (`SCAN-W` may contain only the writer instance currently serving F: the concluding W,
or the W2 that commits F's release records when W has died.) While W lives, W's conclusion must also report `terminal_ok` from its own scans
including `SCAN-UNITS` and `SCAN-REFS` by O (v5 `owned_terminal` semantics, extended).

**Release rule (only F; v5's "only the launching parent releases" is kept, because F is the reserving process).** F
releases only if (1) `owns_window(holder, candidate, token)` holds under the window lock, (2) known-terminal ownership
holds by F's own scans and, while W lives, by W's `terminal_ok`, and (3) `release-intent.json` has been committed
before F's window commit (by W, or by W2 if W has died). The window protocol itself (`window_locked`, `window_read`,
`window_write`, `reserve`, `owns_window`, `release`, the released-status prerequisite, holder/candidate/token joins,
history fields, the lock file and its single-link check) is v5's, unchanged; N07 stays the inherited ceiling for the
window lock. The attempt-directory records v5 wrote inside `reserve`/`release` are committed by W on F's request, under
F's window lock, in the same order relative to the window commit. A durability-UNKNOWN record withholds success,
never release (re-review clarification). **Hold:** any UNKNOWN, any live participant, `terminal_ok == false`, or no
committable `release-intent.json` keeps the window reserved; F commits `release-withheld.json` if it can and prints the
facts; resolution is explicit and operator-visible; there is no late collector, and no frame verb ever releases a
reservation made by another process.

### 9.5 Failure table

| Event | Behaviour |
|---|---|
| Lease held | W refuses before any mutation, writes only to its stderr, exits non-zero. F has reserved nothing (reservation is D9) |
| sudo refuses, account locked, rule missing (each invoke) | F observes S1's exit before any reservation; nothing to release. A setup selftest never stands in for this |
| Channel failure before D9 | W: `refusal.json` ("refused before reservation and launch; nothing was started"); F: no reservation |
| W dies before D11's acknowledgement | no launch is possible (F has not sent `PROCEED_LAUNCH`); F waits for S1; known-terminal by F's scans; if F holds the window, F commits `release-intent.json` through W2 and releases; success false |
| W dies after `PROCEED_LAUNCH` | a launch may exist; F keeps observing (§9.3 argument) until known-terminal, then releases through W2 as above; any UNKNOWN → hold |
| F dies after D9 | W: before launch, refuses and concludes non-success; after launch, keeps waiting and concludes. W cannot release (F alone can): `release-withheld.json` ("front absent"); manual resolution. A front EOF never implies a refusal after launch |
| L dies before `GO` / after | before: nothing launched; after: C may run; W observes; O's terminal scans decide |
| C refuses or dies before spawn | `child-refusal.json` (relayed) or, if C died silently, W observes no `CHILD_START`, L's wait and SCAN-GATE |
| T exits | C's `child-wait.json`, L's and W's waits, O's after-stage, conclusion |
| O fails | the stage's observation fails: before launch refusal; after, `terminal_ok` cannot be established → hold until a new O run under a live W succeeds; W never releases on its own |
| Records exhaustion | §10.2-10.4; outcome non-success; release by §9.4 |
| R's user manager unavailable | L refuses before systemd-run (C never exists) |
| Window not owned at release | `NotOwner` error, nothing released (v5) |
| `sicarii` or target mutation attempt on frame objects | kernel `EACCES`/`EPERM` (§6.5) — prevention, verified by probes in future |

### 9.6 Reboot

- Every record and participant identity carries the boot id. After a reboot every participant of an earlier boot has
  ended. An attempt of an earlier boot whose `launcher-intent.json` is committed but which has no committed
  `result.json` is "interrupted by reboot: outcome unknown"; it is non-success forever and is never re-entered.
- The window, if still reserved by that attempt, stays reserved: F (the only releaser) is gone, and no frame verb
  collects it. The operator resolves it explicitly, citing the boot ids and the attempt's committed records.
- At its next invocation W re-verifies the protected inventory before any mutation: the ancestor chain, `lease/`,
  `writer.lock`, `runs/`, the wlscratch-run home and masks, the installed frame and, with images, each mount (source,
  filesystem UUID and label, `st_dev` of the mount root, options `nosuid,nodev,noexec` as reviewed) against
  `setup-identities.json`, and refuses otherwise. A missing image mount leaves the bare root-owned mount point
  (§14.5), which W can neither write nor mistake (different `st_dev`).
- There is no implicit new genesis: W never recreates or reinitializes a generation; a new one exists only through
  `materialize`. Stale evidence earns no credit: no record of an earlier attempt is ever an admission input.

## 10. Commits, retries, durable fallback and durability-UNKNOWN [gap: commits-and-durable-channel]

### 10.1 Commit primitive and markers (N11)

`commit(dir, name, value)`:
1. v5 `write_json` bytes (`json.dumps(value, indent=2, sort_keys=True, default=str)` plus a newline, with v5's
   `label`) written by v5 `write_bytes(name, bytes, 0600)`: `O_CREAT|O_EXCL|O_NOFOLLOW`, write, `fchmod`, `fsync` of
   file, `fsync` of directory, entry join (the name names the written single-link inode of the written size),
   `verify_location`. Raw byte records (streams, copies, input bytes) use `write_bytes` directly.
2. Post-validation: re-read through `read_observed` and require equal sha256, size and mode.
3. Marker: the same primitive and post-validation for `commits/<seq:08d>-<pathhash16>.commit` holding
   `wlscratch-commit-v1` `{generation, attempt, seq, record: {path, sha256, bytes, mode}, kind ∈ {primary, retry},
   prev_commit, channel_heads, boot_id, at}` (`pathhash16` = the first 16 hex digits of the sha256 of the record's
   partition-relative path, so marker names are single components).

**A record is committed exactly when its marker is committed.** A record whose bytes exist but whose marker does not
(failed `fsync`, failed post-validation, failed marker) is "written, uncommitted": retained as raw evidence, reported,
and never parsed as valid input (v5 `retain` already never reused a partial primary).

### 10.2 Retries and downgrade

v5 `retain` semantics are kept: on any failure in steps 1-3 of the primary the failure is appended, `downgrade` is
applied if given (a retried `result.json` never claims success), and the record is committed under
`name.retry-<12hex>` with its `record_errors`. If the retry's commit also fails, the record goes to the fallback journal.

### 10.3 The pre-established durable fallback channel

- `attempts/<A>/fallback.journal` is created by W at D4 (and at M4 for the creating invocation), before any
  reservation or launch: create-only, 0600, 16777216 bytes (JACKAL exact, parsed `16*2^20`) written in full with zero
  bytes, `fsync` of file and directory, marker committed. It is inside the attempt partition and W-exclusive, so it is
  a frame write inside the tree, not a new outside-tree write.
- 256 slots of 65536 bytes (JACKAL exact: parsed `16*2^20/(64*2^10)` gives 256, parsed `64*2^10` gives 65536). A slot
  is `"WLFB0001"`, the slot index (u32, big-endian), the payload length (u32, big-endian), sha256 of the payload, the
  payload (canonical JSON), zero padding. A slot is written once, with one `pwrite` of the whole slot followed by
  `fdatasync`, and never rewritten; a slot is valid only if magic, index and digest agree. The payload names the record,
  the stage, the error rows, the sha256 and length of the value, and the value itself if it fits (otherwise
  `value_truncated: true`).
- Why it can work when allocation fails: overwriting blocks that are already allocated and written needs no new data
  block, and the metadata update uses the existing journal. This is a design assumption, verified only by the future
  disk-full fault probe P-ENOSPC; it is not claimed. It does not survive a read-only filesystem or device failure; a
  torn slot after power loss is detectable by its digest.
- The next free slot is the first all-zero slot found by scanning the journal at open. W2 (seal-front) uses the same
  journal's free slots for the front's terminal record if its own commit fails; it runs only after W has exited, so the
  two never write concurrently (the lease also excludes it).

### 10.4 Durability-UNKNOWN

If primary, retry and fallback all fail, the record is **durability-UNKNOWN**: W sends `RECORD_UNKNOWN {name, sha256,
length, errors}` to F, writes the facts to its stderr (v5 `last_resort`), sets the attempt's durability state to
UNKNOWN in every later record it can still commit, and the attempt cannot succeed. F prints every `RECORD_UNKNOWN` to its
console; that output reaches the lead's tool output and transcript, written by the harness, not by the frame, and is
not durable if F dies or the transcript filesystem fills. Effect: no success or acceptance credit; no new approval gate;
the window is released or held by §9.4 only.

### 10.5 Consumer joins

- For every record name N, every consumer (conclusion, terminal classification, export, the lead, reviewers) takes:
  the committed primary; else the committed retry (with its downgrade); else the fallback slots naming N (never success
  credit); else UNKNOWN. A parseable but uncommitted primary is raw evidence only.
- N12: every participant record (`launcher-*`, `child-*`, `observer-*`, scope records, `spawn-ok.json`) is validated
  against its exact schema (Appendix B.2). A record that parses but has a missing or mistyped field is unresolved,
  which makes its participant UNKNOWN and holds the window.
- Error joins: every `record_errors` list, `*-failure.json`, `conclude-errors.json`, channel failures and
  durability-UNKNOWN entries are joined into the conclusion and the front terminal record.

### 10.6 Exit statuses (N13, N14)

- **W (N13).** `success` = v5's conjunction (launched, scope wait 0, child wait 0 and clean, no error, post-identity
  clean, materialization unchanged, owned terminal) ∧ every required record committed ∧ no durability-UNKNOWN ∧ release
  committed. Errors appended after `result.json`, including late handle-close and export errors, force `success =
  false`, are committed as `conclude-errors.json` (or to the journal), and make W exit 1.
- **F (N14).** Exit 0 only if W's `FINAL` reports success and release, F's own error list is empty, no interrupt
  reached F, S1's raw status is 0, the front terminal record was committed through W2 and W2's status is 0, and nothing
  is durability-UNKNOWN. Otherwise 1.
- **C, L, O.** C keeps v5's rule (`code` if it is not `None` and there were no failure, notes or errors, else `code or
  1`); L exits 0 only if its scope wait is 0 and it had no error; O exits 0 only if its observation succeeded.

## 11. Prestate and installation [gap: prestate-and-installation]

### 11.1 Rules used throughout

- **Absence is no-follow.** Every "absent" check uses `lstat` and requires `ENOENT`: in Python `os.lstat` must
  raise `FileNotFoundError`; in operator scripts the `absent` function of §11.5 exits unless both `[ -e "$p" ]` and
  `[ -L "$p" ]` are false. A dangling symlink, any other type or a permission error is "present" and refuses.
  `test ! -e` alone is never used.
- **Regular-file identity:** `S_ISREG`, `st_nlink == 1`, owner, group, mode, size, sha256, no ACL xattr, and the
  named entry naming the same `[dev, ino]`.
- **Directory identity:** `S_ISDIR`, owner, group, mode, the exact entry set, `st_nlink == 2 + (number of immediate
  subdirectories)`, the exact ACL text (or none), `[dev, ino]`, and the same `st_dev` as its parent unless it is a
  declared mount point. The `nlink == 1` rule applies to regular files only.
- **Symlinks:** none anywhere in an installed or setup tree, except the reviewed mask links (root-owned, target
  `/dev/null`, exact names).
- Every capture is retained raw with its sha256.

### 11.2 Numeric identity policy

- W, R and GATE are explicit numbers fixed in the concrete inventory (candidates 950, 951, 952 as observed in §3.1).
- For each number n: `getent passwd n` and `getent group n` exit 2; n lies in 500-999 (`SYS_UID_MIN`-`SYS_UID_MAX`,
  `SYS_GID_MIN`-`SYS_GID_MAX`, the system range used by `useradd --system`, which allocates no subordinate range for
  system accounts); for every line
  `owner:start:count` of `/etc/subuid` and `/etc/subgid`, n < start or n ≥ start + count, each bound computed with
  JACKAL in the concrete inventory (all current ranges start at 100000 or above, observed); no file on any local
  filesystem is owned by uid n or group n (P4).
- After setup: `/etc/subuid` and `/etc/subgid` byte-identical to their prestate; `getent` shows exactly the two new
  users and the three new groups; `/etc/shadow` password fields of W and R begin with `!` (or `*`); the `gshadow`
  entry of GATE has no members and a locked password.
- If probe P-MGR shows that a system-range uid cannot host a lingering manager with cpu, memory and pids delegation,
  the concrete inventory moves R to a regular uid and removes any subordinate range `useradd` allocates
  (`usermod --del-subuids/--del-subgids`), re-reviewed. (The existing lingering accounts here have regular uids 1001,
  1002 and 1004.)

### 11.3 Prestate inventory (read-only; "lead" = unprivileged agent, "operator" = needs root)

| Id | Check | Runner | Required |
|---|---|---|---|
| P1 | `getent passwd wlscratch`, `getent passwd wlscratch-run`, `getent group wlscratch`, `getent group wlscratch-run`, `getent group wlscratch-gate` | lead | each exits 2 |
| P2 | `getent passwd <n>`, `getent group <n>` for every candidate | lead | each exits 2 |
| P3 | contents, digests and `lstat` of `/etc/subuid`, `/etc/subgid` | lead | every candidate outside every range; files root:root 0644 |
| P4 | `find <fs> -xdev \( -uid <n> -o -gid <n> \) -print -quit` for `/` and each other local non-FUSE filesystem (never `~/iPad`, `~/iPadBackup`) | operator | empty |
| P5 | no-follow absence of `/var/lib/wlscratch`, `/var/lib/wlscratch-run`, `/opt/wlscratch`, `/var/lib/systemd/linger/wlscratch`, `/var/lib/systemd/linger/wlscratch-run`, `/etc/ssh/sshd_config.d/30-wlscratch.conf`, and with images `/var/lib/wlscratch-images` and the mount-unit paths | lead | `ENOENT` each |
| P6 | no-follow absence of `/etc/sudoers.d/wlscratch-frame`, `/etc/sudoers.d/wlscratch-run`, `/root/wlscratch-staging` | operator | absent, not a symlink |
| P7 | `lstat` of `/`, `/var`, `/var/lib`, `/opt`, `/var/lib/systemd/linger`, `/etc/ssh/sshd_config.d`; `getfacl -n -c` of `/var/lib` and `/opt` | lead | root-owned, no extended ACL |
| P8 | `protected_hardlinks`, `protected_symlinks`, `protected_regular`, `ptrace_scope`, `suid_dumpable`, `max_user_namespaces` | lead | as in §2.3 |
| P9 | `findmnt` of `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp`, `/dev/shm`, `/run/user`, `/proc`, `/sys/fs/cgroup` | lead | as in §2.3 (`/proc` without `hidepid`) |
| P10 | digests of `/etc/pam.d/{sudo,system-auth,system-login,system-remote-login,sshd,su,su-l,runuser,runuser-l,login,other}` | lead | `sudo` keeps `session optional pam_systemd.so class=none` |
| P11 | digests of `/etc/ssh/sshd_config` and drop-ins; `systemctl show sshd.service -p ActiveState -p UnitFileState`; `sshd -T` | lead; operator for `sshd -T` | recorded; gives the expected `denyusers` line |
| P12 | `sudo --version`; digests of `/etc/sudoers` and every `/etc/sudoers.d` file; `visudo -c`; `sudo -l -U sicarii` | lead for the version; operator | §2.3 privilege-route precondition holds |
| P13 | digests of `/usr/share/polkit-1/rules.d/*`; listing and digests of `/etc/polkit-1/rules.d`; `getent group empower wheel docker` | lead; operator for `/etc` | no rule grants `sicarii` or any of its groups a passwordless `YES` for an action that runs code as another user (for example `org.freedesktop.systemd1.manage-units`, `org.freedesktop.policykit.exec`, machine shell or login actions); `empower` and `docker` without members |
| P14 | no-follow absence of `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch`, `/var/spool/cron`, `/var/spool/at`, `/var/spool/atjobs`; `systemctl show cronie.service atd.service -p LoadState` | lead | absent; `not-found` |
| P15 | listing of `/var/lib/systemd/linger` | lead | observed `cosmov1lab`, `wlrehearsal`, `worldline` |
| P16 | listings of `/etc/systemd/user/**` and `/usr/lib/systemd/user/*.wants/**` | lead | gives the mask list (§11.5 S-F) |
| P17 | `find / -xdev -perm /6000 -type f` with digests; `getcap -r /usr` | operator | baseline for S-I |
| P18 | `readlink -f /usr/bin/python3`; sha256 of `/usr/bin/python3.14` and `/usr/lib/libpython3.14.so`; `sys.version` | lead | observed `/usr/bin/python3.14`, `c6bc1ef4…`; 3.14.7 (the lead's earlier observation, reproduced by the re-review) |
| P19 | `systemctl --version`, `setfacl --version`, presence of `/usr/bin/nologin`, `/usr/bin/visudo` | lead | recorded (systemd 261 and sudo 1.9.17p2 are the lead's earlier observations) |
| P20 | `cgroup.controllers` of an existing lingering manager (`user@1002.service`) | lead | observed `cpu memory pids` |
| P21 | Option A: `getfacl -n -c -p /home/sicarii`, `stat -c '%a %u %g %d %i' /home/sicarii`, `namei -l` of the gnatprove path | operator (agents never list or stat the home directory itself) | recorded; becomes `home-acl.pre.expected` |
| P22 | the frozen v6-W1 inventory digest and the review-freeze digests that the install will use | lead | recorded |

Observed on 2026-10-04 by the drafting author (passive reads): the `/etc/passwd` and `/etc/group` entries at or
above 900 (§3.1, for P1/P2); P3 (§5.4); `/etc/login.defs` ranges; P5 for `/var/lib/wlscratch`,
`/var/lib/wlscratch-run`, `/opt/wlscratch` (absent from the listings of `/var/lib` and `/opt`); P8 (`protected_*` 1,
`ptrace_scope` 1, `suid_dumpable` 2, `max_user_namespaces` 128053); P9; P10 (the `sudo`, `system-auth`,
`system-login`, `system-remote-login`, `sshd`, `su` and `runuser` stacks); P11 (sshd active; drop-ins
`20-systemd-userdb.conf` and `99-archlinux.conf`; `UsePAM yes`; `AuthorizedKeysFile .ssh/authorized_keys`;
`AuthorizedKeysCommand /usr/bin/userdbctl ssh-authorized-keys %u`); P13 (the two `/usr/share` rules files read, the
`/etc` directory unreadable); P14; P15; P16; P18 (path and digest); P20. These are observations only; the concrete
inventory repeats them fresh.

### 11.4 Protected reviewed-byte staging and fail-closed execution

- Every privileged byte is part of the reviewed concrete inventory with its sha256: both sudoers files, the sshd
  drop-in, every expected ACL text, the mask list, the identity-record generator, the scripts S-A to S-I, every frame
  member and the member/directory lists.
- **S-0 (operator, root):** create `/root/wlscratch-staging` (root:root 0700) only if absent (no-follow); copy the
  staging manifest from the lead's frozen inventory directory with `install -m 0600`; verify it as root with
  `echo "<MANIFEST_SHA256>  $st/staging-manifest.sha256" | sha256sum -c --strict -`, where the digest is the one in the
  sealed review record; copy every listed file the same way; verify all as root with `sha256sum -c --strict`. The
  lead-writable source can change after review, which is why only the root-owned copies, checked as root, are ever
  used. v2's predictable lead-owned `/tmp` files are not used.
- Each script runs as `sudo sh -eu /root/wlscratch-staging/S-<x>.sh` from the verified copy, so any failing command
  stops everything after it. Installs read only from the staging copies (`install -o -g -m`); there is no `cp -a` and
  no recursive `chmod`. Where a step can leave a partial change, the script undoes exactly that change before exiting
  non-zero (shown below).

### 11.5 Setup scripts (templates; texts and digests become exact in the concrete inventory)

`<W>`, `<R>`, `<GATE>` are the fixed numbers. Every script begins with the same two lines, so that an absence test
is a single command (a failing left operand of `&&` would not stop a `set -e` script):
```sh
st=/root/wlscratch-staging
absent() { if [ -e "$1" ] || [ -L "$1" ]; then echo "present: $1" >&2; exit 2; fi; }
```

**S-A, accounts and groups.**
```sh
set -eu; umask 077
for n in wlscratch wlscratch-run wlscratch-gate; do
  if getent passwd "$n" >/dev/null || getent group "$n" >/dev/null; then echo "S-A: $n exists" >&2; exit 10; fi
done
for i in <W> <R> <GATE>; do
  if getent passwd "$i" >/dev/null || getent group "$i" >/dev/null; then echo "S-A: id $i used" >&2; exit 11; fi
done
groupadd --system --gid <W> wlscratch
groupadd --system --gid <R> wlscratch-run
groupadd --system --gid <GATE> wlscratch-gate
useradd --system --uid <W> --gid <W> --no-create-home --home-dir /var/lib/wlscratch \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame writer' wlscratch
useradd --system --uid <R> --gid <R> --no-create-home --home-dir /var/lib/wlscratch-run \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame target' wlscratch-run
for u in wlscratch wlscratch-run; do
  case "$(getent shadow "$u" | cut -d: -f2)" in '!'*|'*'*) : ;; *) usermod -L "$u" ;; esac
  case "$(getent shadow "$u" | cut -d: -f2)" in '!'*|'*'*) : ;; *) echo "S-A: $u not locked" >&2; exit 12 ;; esac
done
```

**S-B, writer home, lease, runs.**
```sh
set -eu; umask 077
absent /var/lib/wlscratch; absent /opt/wlscratch
install -d -o root -g <W> -m 0750 /var/lib/wlscratch
install -d -o root -g <W> -m 0750 /var/lib/wlscratch/lease
touch /var/lib/wlscratch/lease/writer.lock
chown root:<W> /var/lib/wlscratch/lease/writer.lock
chmod 0440 /var/lib/wlscratch/lease/writer.lock
[ "$(stat -c '%F %h %s %u %g %a' /var/lib/wlscratch/lease/writer.lock)" = "regular empty file 1 0 0 <W> 440" ]
install -d -o <W> -g <W> -m 0700 /var/lib/wlscratch/runs
setfacl -m u:1000:--x,g:<GATE>:--x /var/lib/wlscratch
setfacl -m u:1000:--x,g:<GATE>:--x /var/lib/wlscratch/runs
getfacl -n -c -p /var/lib/wlscratch      | cmp - "$st/acl/var-lib-wlscratch.expected"
getfacl -n -c -p /var/lib/wlscratch/runs | cmp - "$st/acl/runs.expected"
getfacl -n -c -p /var/lib/wlscratch/lease /var/lib/wlscratch/lease/writer.lock | cmp - "$st/acl/lease.expected"
```
The expected files hold exactly the §6.3 texts (and, for `lease`, only the base entries).

**S-C, frame install** (from the verified staging copy of the frozen v6-W1 tree).
```sh
set -eu; umask 022
absent /opt/wlscratch
install -d -o root -g root -m 0755 /opt/wlscratch /opt/wlscratch/frame-v6w1
while read -r d; do install -d -o root -g root -m 0755 "/opt/wlscratch/frame-v6w1/$d"; done < "$st/frame-dirs.list"
while read -r m; do install -o root -g root -m 0644 "$st/frame/$m" "/opt/wlscratch/frame-v6w1/$m"; done < "$st/frame-members.list"
( cd /opt/wlscratch/frame-v6w1 && sha256sum -c --strict "$st/frame-members.sha256" )
```
The v6-W1 source is frozen with every member at 0644 and every directory at 0755, so installed modes equal frozen
modes; the inventory records `install_root = /opt/wlscratch/frame-v6w1` (v5 checked `inventory['frame'] == FRAME`; the
installed frame checks `install_root` instead).

**S-D, sudo rules** (reviewed bytes, one line each).
- `wlscratch-frame`: `sicarii ALL=(wlscratch) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py *`
- `wlscratch-run` (Option A): `wlscratch ALL=(wlscratch-run : wlscratch-gate) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py *`
- Option B replaces the second file: `wlscratch ALL=(root) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *`
```sh
set -eu; umask 077
for f in wlscratch-frame wlscratch-run; do
  absent "/etc/sudoers.d/$f"
  visudo -cf "$st/sudoers/$f"
done
install -o root -g root -m 0440 "$st/sudoers/wlscratch-frame" /etc/sudoers.d/wlscratch-frame
install -o root -g root -m 0440 "$st/sudoers/wlscratch-run"   /etc/sudoers.d/wlscratch-run
if ! visudo -c; then rm -f /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/wlscratch-run; exit 40; fi
```

**S-E, sshd** (reviewed byte line `DenyUsers wlscratch wlscratch-run`).
```sh
set -eu; umask 022
f=/etc/ssh/sshd_config.d/30-wlscratch.conf
absent "$f"
install -o root -g root -m 0644 "$st/30-wlscratch.conf" "$f"
if ! sshd -t; then rm -f "$f"; exit 50; fi
if ! sshd -T -C user=wlscratch,host=localhost,addr=127.0.0.1 | grep -qixF -f "$st/sshd-denyusers.expected"; then
  rm -f "$f"; exit 51; fi
systemctl reload sshd.service
```

**S-F, target home, masks, linger.** The mask list is derived from P16 at inventory time: every unit enabled for user
managers in `/etc/systemd/user/*.wants` and `/usr/lib/systemd/user/*.wants`, every unit those activate, and the
aliases, minus the keep set (`dbus.socket` and `dbus-broker.service`, kept because the original environment names the
user bus). Observed on 2026-10-04: `/etc/systemd/user` enables `omarchy-native-audio-bridge.service`,
`omarchy-native-camera-bridge.service`, `omarchy-native-mac-share-link.service`, `xdg-user-dirs.service`,
`omarchy-native-clipboard-bridge.service`, `wireplumber.service` (also aliased as `pipewire-session-manager.service`),
`gnome-keyring-daemon.socket`, `p11-kit-server.socket`, `pipewire-pulse.socket`, `pipewire.socket`;
`/usr/lib/systemd/user/sockets.target.wants` enables `dbus.socket`, `dirmngr.socket`, `gpg-agent-browser.socket`,
`gpg-agent-extra.socket`, `gpg-agent-ssh.socket`, `gpg-agent.socket`, `keyboxd.socket`,
`systemd-ask-password.socket`, `systemd-importd.socket`, `systemd-journalctl.socket`, `systemd-machined.socket`,
`systemd-storage-fs.socket`. (Existing lingering accounts run `pipewire`, `wireplumber`, `pipewire-pulse` and
`dbus-broker` processes, observed with `ps`.)
```sh
set -eu; umask 022
h=/var/lib/wlscratch-run
absent "$h"
install -d -o root -g root -m 0755 "$h" "$h/.config" "$h/.config/systemd" "$h/.config/systemd/user"
install -d -o <R> -g <R> -m 0700 "$h/tmp"
while read -r u; do ln -s /dev/null "$h/.config/systemd/user/$u"; done < "$st/masks.list"
absent /var/lib/systemd/linger/wlscratch-run
loginctl enable-linger wlscratch-run
```
`ln -s` without `-f` fails if a name exists; the masks precede linger, so R's manager first starts with them in place.

**S-G, Option A only: home traverse entry** (operator; agents never stat the home directory).
```sh
set -eu
getfacl -n -c -p /home/sicarii | cmp - "$st/home-acl.pre.expected"     # P21 capture; a concurrent change stops here
setfacl -m g:<GATE>:--x /home/sicarii
getfacl -n -c -p /home/sicarii | cmp - "$st/home-acl.post.expected"    # pre + the entry + the recalculated mask
```
If the second comparison fails, the operator runs the S-G part of rollback (§15.1 step 7) at once.
**S-G′, Option B only:** no home ACL; `sandbox_launch.py` is a frame member installed by S-C, and its rule is S-D's
Option B line.

**S-H, setup identity record.** A reviewed generator, run as `/usr/bin/python3 -I -B "$st/make_setup_identities.py"
/opt/wlscratch/setup-identities.json`, creates the file with `O_EXCL`, 0644, root:root, holding: the numbers; for every
setup object its path, type, `[dev, ino]`, owner, group, mode, link count, size and exact ACL text (including
`writer.lock`'s `[dev, ino]`); the `runs/` mount facts (and image facts); the installed frame root identity and member
digests; the sudoers and sshd digests; the mask list digest; the linger file; the digests of `/etc/subuid`,
`/etc/subgid` and of the new `passwd`, `group`, `shadow` and `gshadow` lines. The operator records its sha256.

**S-I, post-setup capture** (operator, read-only): the first character only of each new `shadow` password field;
the `gshadow` line of GATE; sudoers digests and `visudo -c`; `sudo -l -U sicarii` and `sudo -l -U wlscratch`;
`sshd -T -C user=wlscratch,…`; `find / -xdev -perm /6000 -type f` and `getcap -r /usr` compared with P17;
`find / -xdev \( -uid <W> -o -gid <W> -o -uid <R> -o -gid <R> -o -gid <GATE> \)` equal to exactly the setup objects.

### 11.6 Post-setup verification

- Lead (unprivileged): `getent` for the three identities; `lstat` and `getfacl -n -c` of `/var/lib/wlscratch`,
  `runs/`, `/var/lib/wlscratch-run` and its children compared with `setup-identities.json` and §6.3; the installed
  frame listed and hashed member by member against the frozen inventory, with §11.1's regular-file and directory rules,
  no extra entry and no ACL; `/var/lib/systemd/linger` equal to P15 plus `wlscratch-run`; `loginctl show-user` for both
  accounts; `cgroup.controllers` of `user@R.service` containing `cpu memory pids`; R's processes equal to B_mgr;
  `/etc/subuid` and `/etc/subgid` unchanged.
- Through the selftest verbs (W and L/C/O): `lease/` and `writer.lock` identities, role identities and readbacks, R's
  manager units equal to B_mgr, and the probes of §13.
- Operator: S-I.

## 12. Exposure options [gap: exposure-options]

No option is selected or recommended here. Both keep the exact original target command path.

### 12.1 Option A: one traverse entry on `/home/sicarii`

- **Change:** `group:<GATE>:--x` on `/home/sicarii` (S-G). It is a group entry, so only GATE holders (L, C, O, T and
  T's descendants) get it; R's background processes and W do not.
- **Known required:** the toolchain subtree `/home/sicarii/opt/gnat/**`. Every component below `/home/sicarii` must
  be others-searchable and the toolchain files others-readable and, for executables, others-executable; P21's
  `namei -l` capture verifies the components at setup.
- **Known exposed (historical observation, not re-inspected for v3):** during v1's preparation `~/opt`,
  `~/Documents`, `~/.claude` and `~/.codex` were observed 0755. Every others-readable file reachable through
  others-searchable directories below them is readable by T, including lead transcripts under `~/.claude/projects` and
  the WORLDLINE work tree under `~/Documents`.
- **UNKNOWN:** everything else below `/home/sicarii`, explicitly including `~/iPad` and `~/iPadBackup` (FUSE mounts,
  never listed or stat'ed) and `~/.local/share/sia/.gbrain` (never inspected). No exact exposure set is claimed and no
  aggregate count is offered as one. A complete enumeration would require listing the home directory itself, which the
  machine rules forbid to agents; an operator enumeration with the same exclusions would still leave those paths
  UNKNOWN.
- **Write exposure added:** none by the entry itself (search only). T can write any others-writable object below
  `/home/sicarii` that it can reach: part of the UNKNOWN inventory of §12.3.
- **PATH:** original `PATH` entries below `/home/sicarii` resolve for T only where others-searchable; executables
  there are `sicarii`-writable (R4).

### 12.2 Option B: root launcher with a private mount namespace (design level; concrete review in the setup package)

- **Rule:** S-D's Option B line replaces the launcher rule; RL runs as root, then becomes L.
- **RL steps:** first act (§7.7); role identity; argv grammar (verb `launch`, `observe` or `selftest`; g; A; nonce;
  seals); before any namespace change, open the real toolchain directory by an anchored no-follow walk
  (`openat2` with `RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS`) and record its `[dev, ino]`, owner and mode;
  `unshare(CLONE_NEWNS)`; set `MS_REC|MS_PRIVATE` on `/` before any mount (**mount propagation**: nothing propagates
  back to the host and host mount events do not enter); mount a tmpfs on `/home/sicarii` (mode 0755, uid 0, gid 0,
  size 1 MiB, few inodes); create `opt/gnat` in it; bind the held toolchain directory there (`open_tree`/`move_mount`
  from the held descriptor) and remount it `MS_RDONLY|MS_NOSUID|MS_NODEV`; verify inside the namespace that
  `/home/sicarii` lists exactly `opt`, `opt` lists exactly `gnat`, the bound root's `[dev, ino]` equals the held one and
  the mount is read-only.
- **Inherited fds:** only 0-2 (sudo's `closefrom` guarantees it; RL verifies `/proc/self/fd`).
- **Capability, uid, gid and group drop:** drop every bounding-set capability (`PR_CAPBSET_DROP`), clear ambient
  capabilities, `setgroups([R])`, `setresgid(GATE, GATE, GATE)`, `setresuid(R, R, R)`, `PR_SET_NO_NEW_PRIVS` = 1; then
  verify `/proc/self/status`: all uids R, all gids GATE, groups `[R]`, every capability set zero, `NoNewPrivs: 1`.
- **Root-before-drop work** is only validation, identity, the namespace and its mounts, the checks, fd verification,
  the credential drop and `execve`. RL writes no file on any host filesystem; the tmpfs exists only inside the
  namespace.
- **Environment:** RL builds L's exact environment (the relocated environment of §8.4) and `execve`s L.
- **Identity:** RL sends its `root-launcher` role identity (namespace inodes before and after, the relevant
  `mountinfo` lines, credentials and capability sets after the drop) to W over fd 0 before `exec`; W commits it.
- **Reachable paths** for L, C, O and T: the host mount table except `/home/sicarii`, where only the read-only
  toolchain is visible.
- **New trust:** privileged code behind a passwordless rule that any writer instance can call with any arguments, so
  RL must be robust to arbitrary input. Its code, rule, probes (propagation, fds, credentials, capabilities,
  namespace contents) and residuals are reviewed in the concrete setup package before any approval. No implementation
  or sufficiency evidence exists.
- **Exposure:** known required: the toolchain subtree, read-only. Nothing else below `/home/sicarii` is visible to T.

### 12.3 Target-write residual (both options), stated as an inventory

- **Known target-writable places:** partition contents of g; its stream descriptors; `/var/lib/wlscratch-run/tmp`;
  `/tmp` and `/var/tmp` (world-writable, sticky, on the same ext4 as everything else); `/dev/shm`; `/run/user/R`
  (including the manager's transient-unit state); R's user manager (units, through the bus or the private socket).
- **UNKNOWN:** every other location on the host that is others-writable or writable by R or GATE. No complete
  inventory of world-writable objects exists; under Option A this includes anything others-writable below
  `/home/sicarii`.
- The residual covers target writes only and never a frame write (V5-B02).

## 13. Probe specification (future; nothing here has been executed) [gap: denial-probes]

**Fixtures.** The writer selftest creates a sacrificial generation `runs/selftest-<hex>` with §3.3's layout and §6.3's
modes and ACLs, reduced to: a recipe directory `src/` (0755) holding `src/a.adb` (0644); a partition root `src/obj`
(0770 by ACL); a record `rec.json` (0600); `attempts/<A>/` (0700) with a record; `export/` with one export file. The
launcher selftest creates, as T would, `src/obj/t.o` (0600) and `src/obj/d/` (0700). Probes never touch a real
generation, the real window file or anything below `/home/sicarii` other than the lead's own records.

**Actors.** A1: the lead, uid 1000, outside. A2: a launcher-selftest process with T's credentials (R + GATE,
`no_new_privs`, the anti-setid filter). A3: a transient unit started by the launcher selftest through R's manager
(R without GATE). A4: a second writer selftest instance while the first holds the lease. A5: W itself (positive
controls).

**Each probe row records:** the actor's full credentials; the exact syscall and absolute operands; the positive
preconditions observed immediately before (source exists with the expected type, destination absent, destination
parent exists, and whether the actor can search to it); the raw errno number and name; and, on unexpected success, the
whole resulting state, retained and never cleaned. An unexpected success is a setup failure.

| Family | Operations and expected outcome |
|---|---|
| P-MUT | For each actor A1, A2, A3 and each object class where §6.5 denies that actor the operation (and, as positive controls, A2's permitted creates and unlinks inside the partition root): `open(O_WRONLY)`; `open(O_CREAT\|O_EXCL)` of a fresh name; `mkdir`; `unlink`; `rmdir`; `rename` within a directory; `rename` out into an actor-owned directory in `/tmp`, after verifying equal `st_dev` so that `EXDEV` cannot mask the result; `rename` in from it; `link` out and in; `symlink` in; `truncate`; `chmod`; `chown`; `setxattr("system.posix_acl_access")`; `utimensat` with explicit times. Expected `EACCES` (search or write permission) or `EPERM` (ownership, `protected_hardlinks`). For A1 below g the first denial is the path search; the object's own permission is probed again by A2, which can search |
| P-ALIAS | A1 and A2 hard-link a W-owned recipe file and a W-owned record to a fresh `/tmp` name (`EPERM` for A2 by `protected_hardlinks`, `EACCES` for A1 by search); symlink into g (`EACCES`); A1 mounts over g inside its own user namespace and `findmnt` in the host namespace shows no change |
| P-READ | A1 reads an export file (ok) and a record (`EACCES`); A2 reads a recipe file (ok), its own partition file (ok), a record (`EACCES`) and an export file (`EACCES`); A3 searches `/var/lib/wlscratch` (`EACCES`) |
| P-LEASE | A4 gets `LeaseHeld` before any mutation, and A5's listing of `runs/` is identical before and after; as W, `open(writer.lock, O_WRONLY)` → `EACCES`, `chmod` → `EPERM`, `rename`/`unlink` in `lease/` → `EACCES` |
| P-DRIFT | Between the O parent-stage walk and C's final pass of a sacrificial attempt, A2 changes an excluded partition leaf (content, mode, mtime, a second hard link inside the partition, replacement): C refuses with the recorded reason. A control without change is accepted |
| P-LAUNCH | A1 runs `sudo -n -u wlscratch-run …` (refused; exact status and message); a writer selftest starts L and closes SP_L before `GO` (L exits 125, nothing started); C started outside the scope or with a wrong seal refuses; C without `SPAWN_OK` refuses |
| P-SETID | A2: `fchmod`, `fchmodat`, `fchmodat2` with 04755 and 02755, `openat(O_CREAT)` with 06755, `mknodat` with 06755 → `EPERM`; `io_uring_setup`, `openat2` → `ENOSYS`; ordinary `chmod 0755` and `open` 0644 succeed. A3: `chown` to group GATE → `EPERM` |
| P-DUMP | every role's two readbacks; timestamps of `exec` and of the first act (pre-first-call window) |
| P-MGR | `loginctl show-user` for W (no manager, no `/run/user/W`) and R (`Linger=yes`, running); `user@R.service` controllers ⊇ {cpu, memory, pids}; R's processes and units equal B_mgr; whether `(sd-pam)`'s `/proc` entries are readable to R |
| P-RUNTIME | role identities, module closures and runtime-closure observations in each context against their baselines |
| P-SIG, P-RELAY | A1 sends `SIGTERM` to S1 during a writer selftest wait: W's interrupt record, whether `sudo` relayed it, and that W made no mutation outside its sacrificial g |
| P-TERM | terminal-failure controls through test-only switches of the selftest verbs (never of `dispatch`): W death after launch intent; L death after `GO`; C refusal; target non-zero exit (`/usr/bin/false` as the selftest target); commit failures injected into the commit primitive (primary; primary and retry; all → fallback; fallback exhausted → UNKNOWN); F death after a reservation of a sacrificial copy of the window protocol on a sacrificial path. Expected behaviour as §9.5 and §10 |
| P-ENOSPC | optional, on an operator-provided sacrificial small filesystem: fill it, then a fallback-journal slot write must succeed |
| V-VAULT | as `sicarii`: `project-vault pin`, `status` and the project-vault recovery comparison on `runs/selftest-<hex>/export` |

## 14. Resources, staged Gate 0 and images [gap: resources-and-images]

Every derived number below was computed with actual MCP `jackal_exact`. Each result has status `exact`, `formal`
false, lane `rat`, and the non_claims "NOT formal-bounded: this lane carries no Lean-checked certificate", "The
epistemic class above is the STRONGEST claim this result supports", "exact rational arithmetic (not yet
checker-covered)". No consequence ceiling field was returned; the results are informational arithmetic only. Exact is
not formal-bounded. The "approx" figures are the tool's decimal display of the exact value. Full records:
`v3-support/jackal.json` and Appendix C.

### 14.1 Gate 0 of runbook v4.3, unchanged

Allowances (labelled judgments; runbook v4.3 = v4.2 plus O1's corrected provenance, values identical): A_mat 16777216;
A_obj 2242440646; A_rec 545393048; A_ambient 1468268019712/1397; R = A_mat + A_obj + A_rec. Required = A_mat + A_obj
+ A_rec + A_ambient + R = 9304350902252/1397 (reproduced by the re-review, parsed
`2*(16777216+2*1121220323+545393048)+1468268019712/1397`). Reserve 10000000000, unchanged. The allowances are never
lowered because a run used less, and an observation can only raise them.

### 14.2 W-1 allowances (labelled judgments)

| Id | Covers | Bytes | Basis (JACKAL parsed input) |
|---|---|---|---|
| A_idf | F's real-context runtime-closure observations, full form, three stages, × 2 (A_rec's convention) | 152953998 | `2*3*25492333` (O2 runtime-closure size 25492333, observed) |
| A_in | retained inputs and messages: descriptors, lead module, observation inputs, front records, channel segments (headers and references, no bulk duplicate), role identities with module closures, F-captured W diagnostics | 134217728 | `128*2^20`, judgment. Largest comparable observed inputs: the v5 frame-review roster, 979762 bytes (`49133+602614+68556+250916+8543`); the base descriptors, 108768 (`1735+105491+1542`); lead module 8639 and START 2699 bytes (observed) |
| A_exp | export copies, each retained record at most once | 832564774 | `545393048+152953998+134217728` (A_rec + A_idf + A_in) |
| A_retry | partial primaries and retries, each record at most twice | 832564774 | same expression |
| A_fb | the fallback journal | 16777216 | `16*2^20` (fixed by design) |
| X | all W-1 retained additions: A_idf + A_in + A_exp + A_retry + A_fb | 1969078490 | `2*545393048+3*152953998+3*134217728+16777216`; the check, echoed as parsed `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` (the tool flattened the submitted grouping parentheses), gives 0 |
| A_tmp | target temporaries (`TMPDIR`, `/tmp`, `/var/tmp`): not retained, peak use | 268435456 | `256*2^20`, judgment; no observation exists and v4.3 has no such term; the first observation can only raise it |
| A_jrnl | manager, sudo, PAM, journal and unit effects, per stage | 134217728 | `128*2^20`, judgment; the new identities are system ids, whose messages go to the system journal |
| A_install | installed frame: code plus original and relocated baselines | 115303191 | `3*38434397`; the 17 v5 frame members total 38434397 bytes (`13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891`, member sizes observed in `frame-inventory.json`) |
| A_homes | setup directories, lock, masks | 1048576 | `1*2^20`, judgment |
| A_setuprec | setup evidence (prestate, captures, installed listings, identities) | 16777216 | `16*2^20`, judgment |
| A_selftest | sacrificial selftest generations, probe records, sacrificial export | 67108864 | `64*2^20`, judgment |

### 14.3 Stage budgets and the rule

| Stage | Required (exact) | approx | JACKAL parsed input |
|---|---|---|---|
| before setup | 2027732564230/1397 | 1451490740.3221188 | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` (A_install + A_homes + A_setuprec, their full restore, A_jrnl, A_ambient) |
| before selftests | 1843272351744/1397 | 1319450502.3221188 | `2*67108864+134217728+1468268019712/1397` (A_selftest, its restore, A_jrnl, A_ambient) |
| before every `materialize` and every dispatch | 15368462701360/1397 | 11001047030.322119 | `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` |

The dispatch-stage W-1 addition is 4340810164 (parsed `2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728`:
X, its full restore, A_tmp, A_jrnl), and `15368462701360/1397-9304350902252/1397-4340810164` gives 0.

**Rule.** A stage proceeds only if free − reserve − Required(stage) ≥ 0, computed with actual MCP JACKAL from a
fresh `storage_status.py` reading taken by F as `sicarii`, with the configured reserve unchanged. Otherwise the stage is
DEFERRED. The setup and selftest stages are procedural (the lead computes and records the receipt before asking the
operator, and before running any selftest). The dispatch stage is procedural (runbook) **and** frame-enforced: at D7,
W issues the challenge `<free>-<reserve>-(<the reviewed dispatch-stage expression>)` built from F's fresh reading; F
forwards the lead's actual-MCP receipt; W requires `status` exact, `formal` false, `parsed` equal to the challenge,
`exact` ≥ 0, and free and reserve equal to the reading. Raising an allowance is allowed only upward, and changes the
frame's compiled expression, which is a reviewed frame change.

**What these numbers are not.** Satisfying the inequality is not a safe-capacity argument. Periodic sampling plus a
factor is not a bound. Images and ENOSPC never count as capacity or as an accepted refusal.

### 14.4 Historical arithmetic (not capacity and not current)

Against the retained 23:32:06Z reading (free 10460753920; reserve 10000000000; the re-review reproduced
free − reserve = 460753920 with parsed `10460753920-10000000000`):

| Stage | Margin (exact) | approx | parsed |
|---|---|---|---|
| dispatch | −14724789475120/1397 | −10540293110.322119 | `10460753920-10000000000-15368462701360/1397` |
| setup | −1384059337990/1397 | −990736820.3221189 | `10460753920-10000000000-2027732564230/1397` |
| selftest | −1199599125504/1397 | −858696582.3221189 | `10460753920-10000000000-1843272351744/1397` |

All three are negative, so every stage would have been DEFERRED at that reading. No fresh reading was taken for v3.

### 14.5 Images (only if S-1 option 3 is chosen)

Carried unchanged in substance from v2 (re-review: W1-IMAGE-GEOMETRY and W1-IMAGE-COMPATIBILITY CLOSED): payload
allowances, not image sizes (work 2259217862 = A_mat + A_obj; records 545393048 = A_rec for v2's record set);
filesystem metadata, journal, inode tables, reserved blocks, geometry and setup effects to be measured on a sacrificial
image and never assumed; the zero difference is an ideal payload identity, not physical allocation equality or safe
capacity; `fallocate` creates under the umask, so each image needs an explicit `chmod 0600` and `chown root:root`,
verified; `noexec` is compatible with the proof/compile-only allowlist (gnatprove, gprbuild and the provers execute
from the toolchain path) and incompatible with any control that executes built artifacts in the tree, and such
original executable or native-loading controls keep a separate compatible admitted frame and mount and are never
narrowed to suit a mount; images enforce bounded writes only; ENOSPC is a retained failure, never an accepted refusal
and never capacity evidence; images earn no capacity or admission credit without a reviewed preserving argument.

v3 additions. v3's record classes raise the records payload allowance to A_rec + X = 2514471538 (parsed
`545393048+1969078490`). The v3 ideal payload identity (work payload + records payload + full restore + A_ambient +
A_tmp + A_jrnl − Required(dispatch)) is 0; JACKAL returned it with parsed
`16777216+2242440646+545393048+1969078490+16777216+2242440646+545393048+1969078490+1468268019712/1397+268435456+134217728-15368462701360/1397`
(the tool flattened the grouping parentheses of the submitted expression). It is still only an ideal payload identity.
Layout with images: the work image is mounted at `runs/`; a records image at `/var/lib/wlscratch/records`, which then
holds the attempt and export partitions as `records/<g>/attempts/<A>` and `records/<g>/export` (paths change, modes
and ACLs do not); each bare mount point is root-owned 0700, so W cannot write into a missing mount; the mount units
carry `Options=loop,nosuid,nodev,noexec`; there is no automount unit and no fstab line; W checks each mount at every
invocation (§9.6). A_tmp's places are not on the images.

### 14.6 Memory, CPU and caps

Unchanged from v5: `MemoryMax=8G`, `MemorySwapMax=0`, core 0/0, `-j2`, the 16777217 kB gate and the receipt
protocol. The new user manager and helpers use RAM (tmpfs under `/run/user/R`) and processes; this is not disk and is
not budgeted as disk.

## 15. Rollback, freeze/export and evidence [gap: rollback-and-evidence]

### 15.1 Rollback order (operator; every step's before and after state captured raw)

1. **Revoke new launches first.** Preserve the bytes and sha256 of `/etc/sudoers.d/wlscratch-frame` in
   `/root/wlscratch-staging/rollback-<stamp>/`, remove it, run `visudo -c`. No new writer can start.
2. **Wait for and reconcile every pending and running participant before withdrawing anything else:** `SCAN-W` empty
   (including writers started before step 1); no `sudo` process naming a frame entry; `SCAN-GATE` empty; `SCAN-R` ⊆
   B_mgr; R's units ⊆ B_mgr (`systemctl --user -M wlscratch-run@ list-units --all`, as root); no scope cgroup below
   `user@R.service` other than the manager's own. A live participant is waited for; killing one is a separate, recorded,
   explicit operator decision. Any UNKNOWN holds the rollback at this step.
3. **The shared window.** If it is reserved by a W-1 attempt and known-terminal ownership is uncertain, it is a hold:
   never force a release. If ownership is known terminal and the reserving front is gone, the operator resolves it
   explicitly and records the resolution; the frame never does.
4. Preserve and remove `/etc/sudoers.d/wlscratch-run` (or Option B's root rule); `visudo -c`.
5. `loginctl disable-linger wlscratch-run`, only after step 2 holds; verify `user@R.service` stopped and
   `/run/user/R` gone.
6. **Images, if used:** identify every start source first (the mount units, `systemctl list-dependencies --reverse`
   of each, any automount unit, fstab: none expected); `systemctl disable` the units; verify that no process has a file
   open on them and that step 2 still holds; then stop them (unmount); verify that each is unmounted and that the bare
   mount point equals its setup identity; preserve the unit files (bytes and sha256), remove them, `systemctl
   daemon-reload`, verify no remount. Keep the image files and record their sha256.
7. **Restore the exact approved home ACL (Option A):** capture `getfacl -n -c -p /home/sicarii` and `stat`; require
   equality with the post-setup expected capture (a difference is a concurrent change: stop and report, never
   overwrite it blindly); restore exactly, with `setfacl --restore=` from the P21 dump (which restores entries and mask)
   or `setfacl -b` when P21 showed no extended ACL; capture again and require byte equality with P21 and the same
   `st_mode`.
8. Lock and expire both accounts (`usermod -L -e 1`); keep them, so evidence ownership keeps its meaning. Then preserve
   and remove the sshd drop-in, `sshd -t`, reload.
9. Keep as evidence: `/var/lib/wlscratch` (generations and exports), `/var/lib/wlscratch-run` (including masks),
   `/opt/wlscratch`, `/root/wlscratch-staging` and every capture.

### 15.2 What rollback leaves

Remaining: the two locked and expired accounts and the three groups (the two user-private groups and
`wlscratch-gate`), with their numbers; their `passwd`,
`group`, `shadow` and `gshadow` entries; every file under `/var/lib/wlscratch*`, `/opt/wlscratch` and
`/root/wlscratch-staging`; images, if any; journal entries; and, if step 7 stopped on a concurrent change, the home ACL
as found (reported). Removed: both sudoers files, the sshd drop-in, the linger file, the mount units. Not restored: a
pristine pre-setup system.

### 15.3 Freeze and export

- At M9 and D14, W copies into P_exp every committed record, marker, retry, channel segment and stream file of the
  invocation, and the valid slots of the fallback journal as one `fallback-slots.json` (the zero-filled journal itself
  is not copied; a record exported from a slot takes the place of the committed copy it lacks, so A_exp still counts
  each retained record once, §14.2), each copy create-only, 0600, then given the export ACL of §6.3; it then commits
  `export/<A>/manifest.json` (per copy: export path, source path, sha256, size, source marker digest) and
  `export/<A>/freeze.json` (manifest sha256, last marker digest of the attempt journal, channel heads, boot id, time),
  each with a marker. The markers of P_exp objects are kept in the invocation's attempt journal
  (`attempts/<A>/commits/`, or `attempts/<A0>/commits/` for the generation export), so P_exp holds only copies, the
  manifest and the freeze record. F re-reads every copy through its ACL, compares with the manifest and holds the
  manifest digest from `FINAL`.
- **What "frozen" means:** create-only, W-exclusive, no verb that modifies or deletes, digests in a hash-linked
  journal. **Limits:** root, or W running changed code, could still alter them; no immutable attribute is set (that
  needs `CAP_LINUX_IMMUTABLE`).
- Lead copies of exports are mutable evidence records, not authentic producer custody. A project-vault transfer of
  exports (§8.5) is backup, not authenticity.

### 15.4 Evidence classes (all retained raw)

Pre- and post-setup captures with digests; `passwd`, `group`, `shadow` (first character only) and `gshadow` lines;
`getfacl`/`stat` outputs; sudoers and sshd bytes; `findmnt`, kernel settings, linger state; installed-inventory
comparisons; role identities and module closures; selftest and probe records with raw errnos; every committed record,
marker, retry, fallback slot, channel segment, wait, participant and scope record; launch intent, `spawn-ok`, conclusion
and release records (`release-intent`, `window-release`, `release-withheld`, `release-failure`, `conclude-errors`);
front terminal records; F's console output as preserved in the lead transcript (neither durable nor frame custody);
rollback captures. **Limits:** hashes of W-owned files describe files that root or W could change; copies are evidence
records; none of this is producer authenticity, proof or acceptance.

## 16. Setup, verification and adoption order

1. Actual gpt-6.1-sol review of this v3 design.
2. Frame v6-W1 code implemented, frozen (members 0644, directories 0755, `install_root`) and reviewed as code by
   actual gpt-6.1-sol: front, writer, launcher, child, observer, Option B's RL if pursued, the final pass with
   excluded-leaf keys, channels, commits and the fallback journal, scans, exports, selftest verbs and probes.
3. Concrete setup inventory (fixed numbers; filled prestate P1-P22; exact script texts and digests; expected ACL texts;
   mask list; sudoers and sshd bytes; the Option A or B text), reviewed by actual gpt-6.1-sol.
4. Gate 0, setup stage, on a fresh reading.
5. Operator approval of the concrete setup (reserved authority).
6. The operator runs, or explicitly authorizes, S-0 to S-I.
7. Gate 0, selftest stage; lead verification (§11.6), selftests and probes (§13).
8. Installed-identity, baseline and probe evidence reviewed by actual gpt-6.1-sol; lead adoption with a fresh lead
   observation (v5 `adopt` semantics).
9. Gate 0, dispatch stage; only then `materialize` and dispatch, each under fresh original admission.

No step authorizes the next by inference. This refines v2's CLOSED setup order without changing its substance.

## 17. Placement of every v5 mechanism

| v5 mechanism (frozen `scratch.py`) | W-1 placement | Change, and why it preserves the original |
|---|---|---|
| `Dir` anchoring, `verify_location`, `child(create=True)` authentication, `write_bytes`/`write_json`/`open_stream`/`set_mode` (S:144-358) | W for every frame mutation; C and O for anchored reads; F for anchored input and window reads | none in semantics; the location chain is now protected (§4.5) |
| `stat_key`, `observe_tree` (v6 final pass), `read_observed`, `read_prefix`, `read_files` | C and O full walks; W writer-owned walks (partition roots opaque); F base-tree and transcript reads | `observe_tree` also returns excluded-leaf keys (§4.5) |
| `retain`, `guarded`, `read_record`, `last_resort`, `retain_observation` (S:375-436, 1109-1128) | W | commit markers, fallback journal, UNKNOWN (§10); the compact equal-record form unchanged |
| `exec_verified`, frame inventory, `frame_admitted` (S:587-863) | installed members checked by W, L, C, O; review, adoption, rollout and transcript joins by F | `install_root` replaces `frame`; F's joins at v5 trust (R2) |
| `materialize` recipe (S:959-1049), `expected_source`, `overlay_rules` | W `materialize` | streamed verified bytes; partition roots pre-created (§6.4) |
| `command()` allowlist (S:1054-1070) | W, re-derived by C | unchanged |
| `specifications()` (S:1073-1106) | W builds, C verifies | relocation table (§8.4) |
| `identities()` (S:1131-1153) | O (`parent`, `after`), C (`child`) in the target context; F's runtime and manager in the real context | baselines per context (§8.1, §8.4) |
| `sample()` (S:1156-1179) | F half (sibling units in `sicarii`'s manager, `storage_status.py`); helper half (heavy processes, meminfo, R's units) | split by authority; same checks |
| `threshold_receipts`, `receipt_line`, `memory_gate` (S:1186-1248) | W issues and verifies; F forwards from the inbox | unchanged constants and deadlines; "through original stdin" = W's stdin channel |
| `window_locked`, `window_read`, `window_write`, `reserve`, `owns_window`, `release` (S:1253-1341) | F | unchanged protocol; attempt records committed by W under F's lock in the same order |
| `ancestors`, `processes_naming`, `owned_terminal` (S:1346-1415) | O and C scans; F scans | extended scans and schemas (§9.4, N12) |
| `final_stream_sync` (S:1420-1437) | W after terminal | unchanged |
| `admission()` (S:1440-1448) | split per stage among F, W, O and C | the same checks |
| `spawn`, `wait_blocked`, `pending_handled`, `raising_handler` (S:1469-1517) | every waiting role | H-S1/H-M3 synchronous handling; `STOP` down the channels |
| `started_by_dispatch` (S:1520-1527) | W: `SUDO_*` plus `HELLO_ACK` plus stdio inode join; W2: front-process triple | the invoker is bound by kernel identities instead of a parent command line |
| `refusal_record`, `run`, `conclude` (S:1530-1765) | W (`dispatch`), F (release), O (terminal observations) | N13 recomputation |
| `child` (S:1768-1896) | C | §9.3 C1-C12 |
| `dispatch` (S:1899-1988) | F | inbox answers over the channel; S1 wait via W2; N14 exit |
| `verify_materialization` placement: materialize, parent and child admission, immediately before spawn, conclusion | W at M8; O at the parent stage and W's writer half; C at the child stage and as the final pass; O and W at the conclusion | same placements, now split by authority |
| launch seal in argv (S:1570-1594, 1783-1817) | L's and C's argv carry the `launch.json` and `admission.json` sha256; C verifies the bytes delivered over its channel | V4-B03 kept |

## 18. Per-gap status (the author's assessment, for the independent reviewer to judge)

"CLOSED-AT-SPEC-LEVEL" is this author's claim that the specification text now covers what the gap asks for. It is
not closure, not executed evidence and not acceptance. "CLOSED (re-review), carried" marks items the re-review closed;
v3 keeps them unchanged in substance. Every original obligation, V5-B01, V5-B02 and Gate 0 stay OPEN regardless.

### 18.1 The re-review's required corrections

| Correction | Re-review | v3 sections | Author's assessment | Still needed as future evidence |
|---|---|---|---|---|
| W1-CUSTODY | NOT_CLOSED | §4 (stable lock §5.1; initial versus admission/launch records §4.2-§4.3; bound source/output/window/command/record/export/participant expectations §4.4, §7.5; final pass and partitions §4.1, §4.5; per-entry modes §6; lease classified as flock-only §5.1) | CLOSED-AT-SPEC-LEVEL | v6-W1 code and its review; installed setup; probes P-MUT, P-ALIAS, P-LEASE, P-DRIFT, P-LAUNCH, P-SETID |
| W1-SETUP | NOT_CLOSED | §5.1 (`writer.lock`), §11 (no-follow prestate, numeric policy, ACL masks, linger, sudoers, frame, runtime, module and optional image inventories, protected staging, fail-closed scripts), §7.7 (dumpability readback), §11.1 (file versus directory identity), §13 (probe operands), §12 (Option A known/UNKNOWN; Option B design), §8 (real front, per-invocation identity, original path and caps, vault scope) | CLOSED-AT-SPEC-LEVEL; Option B at design level only, its concrete review being deferred to the setup package as the re-review allows | the concrete inventory and its review; operator setup; S-I; probes; V-VAULT |
| W1-RESOURCES | NOT_CLOSED | §14 | CLOSED-AT-SPEC-LEVEL | fresh readings; image geometry measured on a sacrificial image if images are chosen; first observations (A_tmp, A_jrnl, A_in) raise allowances |
| W1-LIFETIME-ROLLBACK | NOT_CLOSED | §10 (markers, joins, fallback, UNKNOWN), §9 (schemas, waits, launch gating, death, EOF, exhaustion, reboot, holds), §15 (rollback order, ACL/mask restoration with concurrency check, start sources before unmount, evidence) | CLOSED-AT-SPEC-LEVEL | code; P-TERM, P-ENOSPC; rollback execution records |

### 18.2 The re-review's section-3 gaps

| Gap | v3 | Author's assessment | What v3 specifies |
|---|---|---|---|
| generation-order | §4 | CLOSED-AT-SPEC-LEVEL | initial `generation.json` and `attempt.json` bind only existing facts; inputs manifest, `launch.json`, reservation records, `admission.json` and `launcher-intent.json` are separate create-only records with exact fields (Appendix B.3), anchors and joins (§4.4); P_adm immutable after M8; P_att and P_exp take every later write; the final pass is defined against P_adm (§4.5) |
| lease-and-writer-authority | §5 | CLOSED-AT-SPEC-LEVEL | `writer.lock` root:W 0440 created by S-B; per-invocation owner/group/mode/type/link/size/ACL/name/parent/inode checks; `flock` on `O_RDONLY`, no byte write; the writer's complete mutation list; the closure of every uid/gid acquisition route for W, R and GATE; subordinate-range exclusion |
| per-entry-modes-acls | §6 | CLOSED-AT-SPEC-LEVEL | v5 modes preserved by never placing an ACL on a recipe object, record, snapshot entry or stream and never using a default ACL; mask semantics stated; per-object owner, mode and exact ACL text; target, C/O, W and lead access paths; denial matrix |
| channel-and-dumpability | §7 | CLOSED-AT-SPEC-LEVEL | transports; canonical encoding; chain genesis and recurrence; retained segment form; rejection rules (EOF, order, size, canonicity, schema, deadlines); in-memory expectations; integrity versus authentication with the original v5 ceiling; `prctl` set and readback and `/proc/self/fd` ownership at an exact point in each start; the pre-first-call residual per role |
| prestate-and-installation | §11 | CLOSED-AT-SPEC-LEVEL | no-follow absence; numeric ids outside every subordinate range; home and ancestor identity; password, keys, jobs, linger, ACL, interpreter, frame, module, sudoers, sshd, polkit and image inventories; root staging with root-side digest checks; fail-closed scripts that install only after validation and undo partial changes; regular-file versus directory identity |
| exposure-options | §12 | CLOSED-AT-SPEC-LEVEL (Option B design level) | Option A: required, historically observed and UNKNOWN exposure, with the excluded FUSE and brain paths never inspected and no exact set claimed; the target-write residual as an inventory with an UNKNOWN remainder; Option B: propagation, reachable paths, inherited fds, capability/uid/gid/group drop, `no_new_privs`, root-before-drop work, environment, identity |
| fresh-identities-and-vault | §8 | CLOSED-AT-SPEC-LEVEL | fresh role identities (runtime, modules, manager, stdio, environment) for every process of every invocation; raw outer waits (§9.2); the real non-isolated front invocation with original baselines; the original target path and caps; the relocation table; the vault pins only P_exp, readable through named ACL entries; V-VAULT is future evidence; the nonexistent cross-reference is gone |
| denial-probes | §13 | CLOSED-AT-SPEC-LEVEL | fixtures, actors, operands, preconditions, recorded fields and every family the gap names (outside alias under both identities, lock concurrency, final-leaf drift including link count, launch custody, dumpability/manager/runtime readback, terminal-failure controls) plus P-SETID and V-VAULT; all future |
| resources-and-images | §14 | CLOSED-AT-SPEC-LEVEL | staged Gate 0 before setup, before selftests and before every materialize and dispatch, with labelled allowances for inputs, messages, duplicates, retries, the failure channel, setup and selftest outputs, manager and journal effects, every retained output, full restore and ambient growth; images as payload allowances only; compatible frames for executable and native controls |
| commits-and-durable-channel | §10 | CLOSED-AT-SPEC-LEVEL | a record counts only through its marker (N11); retry and consumer joins; non-success on every commit, close and dispatch failure (N13, N14); the pre-established preallocated fallback journal inside the tree; durability-UNKNOWN with no new gate and no release effect |
| participants-and-recovery | §9 | CLOSED-AT-SPEC-LEVEL | participant, wait and scope schemas; genuine waits and relay evidence; launch gating that excludes a late launch after writer death except through an issued, recorded permission; scans with UNKNOWN holds; N11-N14 and no late collector kept; reboot with boot-bound interpretation and a protected inventory check; no new genesis; no stale credit |
| rollback-and-evidence | §15 | CLOSED-AT-SPEC-LEVEL | launches revoked first; every participant reconciled before any other withdrawal; an uncertain window is a hold; exact ACL and mask restoration with concurrent-change detection; start sources disabled before unmount; what remains; the freeze/export mechanism and its limits |

### 18.3 The original W-1 subgaps

| Subgap | Re-review | v3 | Author's assessment |
|---|---|---|---|
| W1-CUSTODY | NOT_CLOSED | §4, §5, §6, §9.3 | CLOSED-AT-SPEC-LEVEL |
| W1-FINAL-PASS | CLOSED | §4.5 | CLOSED (re-review), carried; the v6 working copy's excluded-leaf pass is noted as an author correction (ENGINEERING_ONLY self-check) |
| W1-CLOSURE | NOT_CLOSED | §8.1-§8.4, §11.1, §11.6 | CLOSED-AT-SPEC-LEVEL |
| W1-CHANNEL | NOT_CLOSED | §7 | CLOSED-AT-SPEC-LEVEL |
| W1-WRITE-AUTHORITY | NOT_CLOSED | §5.2, §6, §12.3 | CLOSED-AT-SPEC-LEVEL |
| W1-READ-ACCESS | CLOSED | §4.2 (M6), §8.6 | CLOSED (re-review), carried: streamed pinned inputs; the frozen 0600 files keep their modes; no writer ACL under `/home/sicarii` |
| W1-READ-EXPOSURE | NOT_CLOSED | §12 | CLOSED-AT-SPEC-LEVEL |
| W1-PREFLIGHT-IDENTITY | NOT_CLOSED | §8.5, §6.4 | CLOSED-AT-SPEC-LEVEL |
| W1-SETUP-PRESTATE | NOT_CLOSED | §11.1-§11.3 | CLOSED-AT-SPEC-LEVEL |
| W1-SETUP-ORDER | CLOSED | §16 | CLOSED (re-review), carried and refined by staged Gate 0 |
| W1-SETUP-EXACTNESS | NOT_CLOSED | §11.4-§11.5, §6.3 | CLOSED-AT-SPEC-LEVEL (template texts; exact bytes come with the concrete inventory, as the re-review accepted) |
| W1-IMAGE-GEOMETRY | CLOSED | §14.5 | CLOSED (re-review), carried; v3's records payload grows by X |
| W1-IMAGE-COMPATIBILITY | CLOSED | §14.5 | CLOSED (re-review), carried |
| W1-VERIFICATION-PROBES | NOT_CLOSED | §13 | CLOSED-AT-SPEC-LEVEL |
| W1-FAILURE-LEASE | NOT_CLOSED | §9 | CLOSED-AT-SPEC-LEVEL |
| W1-FAILURE-RECORDS | NOT_CLOSED | §10 | CLOSED-AT-SPEC-LEVEL |
| W1-REBOOT-RECOVERY | NOT_CLOSED | §9.6 | CLOSED-AT-SPEC-LEVEL |
| W1-ROLLBACK | NOT_CLOSED | §15.1-§15.2 | CLOSED-AT-SPEC-LEVEL |
| W1-EVIDENCE | NOT_CLOSED | §15.3-§15.4, §10 | CLOSED-AT-SPEC-LEVEL |
| W1-NONCLAIMS | CLOSED | header, §20 | CLOSED (re-review), carried |

### 18.4 The re-review's residual judgments

| Residual | v3 | Status |
|---|---|---|
| lead-process same-user interference | §2.4 R1, §7.7 | carried as an explicit inability with the pre-first-call window; readback corrected; not a new exception |
| lead authentication | §2.4 R2, §7.6 | the original v5 engineering ceiling only; all original joins kept |
| Option A exposure | §12.1 | known and UNKNOWN parts stated; no exact set claimed |
| Option B privilege | §12.2 | candidate with a design-level argument; concrete review before any setup approval |
| running-target and toolchain ceilings | §2.4 R3, R4, §12.3 | reference ceilings only; they cover no frame mutation, no unsafe pre-launch alias and no narrowing |

### 18.5 New design elements in v3 that need the reviewer's attention

1. The gate group GATE as the only non-writer key to the generation (§3.1, §5.3, §6).
2. `no_new_privs` and the anti-setid seccomp filter on T (§9.3 C9), which close the route by which a target could
   mint a GATE-conferring set-group-ID file. Compatibility hypothesis stated in §8.3.
3. Per-user masks and the manager baseline B_mgr, `SCAN-UNITS` and `SCAN-REFS`; the `(sd-pam)` limit R7 and the
   in-transit-descriptor limit R9 (§2.4, §9.4).
4. Pre-created, writer-owned partition roots (§6.4) and a root-owned `HOME` for R (§8.4): two compatibility
   hypotheses for the first engineering run.
5. F as the only releaser: if F dies after reserving, W cannot release, so the window is held for manual resolution
   (§9.5). v5's reserving parent was the `run` verb, which could still release after `dispatch` died; v3's behaviour is
   more conservative, not weaker.
6. The frame-enforced dispatch-stage Gate 0 receipt (§14.3), in addition to the runbook procedure.
7. W2's capability as the kernel-assigned front-process triple (§5.2).
8. The relocation table (§8.4) and the new baselines it implies.

## 19. Future execution and installed evidence (none of it exists)

- Frame v6-W1 code for every role, frozen, with its own actual gpt-6.1-sol review, including the excluded-leaf keys,
  channels, commit markers and fallback journal, scans, exports, the anti-setid filter, selftest verbs and probes.
- The concrete setup inventory (fixed numbers, P1-P22 outputs, script texts and digests, expected ACL texts, mask list,
  sudoers and sshd bytes, the Option A or B text) and its review; JACKAL bounds for the subordinate-range checks.
- Option B's concrete code, rule and probes, if Option B is pursued, and their review.
- Operator approval and execution of S-0 to S-I, with S-I captures.
- Post-setup verification (§11.6); every probe of §13 with raw records; V-VAULT; optionally P-ENOSPC.
- The new baselines (relocated runtime closure, R's manager environment, writer context, tool inventory per option) as
  reviewed installed evidence; installed-identity review and adoption.
- Fresh storage readings and Gate 0 receipts for every stage; measured image geometry if images are chosen.
- First engineering-run evidence for the compatibility hypotheses: no `HOME` writes, no partition-root removal, no
  set-user-ID or set-group-ID mode, no `io_uring` or `openat2` use by the allowlisted actions.
- Rollback execution records, whenever rollback happens.
- Independent actual gpt-6.1-sol review of all of the above. Only then can V5-B01 and V5-B02 be assessed against
  exact successor evidence.

## 20. Non-claims

- No sufficiency is claimed for V5-B01, V5-B02 or any original obligation. All stay OPEN until exact successor
  evidence meets the original required changes, with their original owners, releases and dependencies.
- Nothing here is executed or installed evidence. Design statements, templates and probe specifications are plans.
- The account and gate design gives a kernel-enforced writer and generation boundary under the stated trusted base
  and preconditions. It is not proof of the frame code, not lead authentication (R2), not confinement of the running
  target (R3), not custody of the toolchain (R4), and no protection from root.
- Integrity of the channels is not sender authentication.
- No storage capacity is established. Allowances are labelled judgments, never bounds; the arithmetic is exact
  arithmetic outside the Lean certificate chain (status `exact`, not `formal-bounded`) and is informational only.
- Images enforce write limits only. ENOSPC is never an accepted refusal and never capacity.
- Exports and lead copies are evidence records, not authentic producer custody; a vault transfer is backup.
- No operator choice is made or recommended; no approval is requested; no new approval gate is created.
- Phase One is incomplete.

## Appendix A. Verbatim criteria

Source: `work/claude-scratch-frame-v5/review/gpt61-v1/REVIEW.md`, sha256
`2c414c694ed75d72cffae2172bef967bdcf63d73cc0a3764f96762a59d49ec71` (sealed by `review-freeze.json`
`48539bdf57e11edeabe0844c7860284fa1cde26c1cab58a7b86317ef82a34ef7`). Each block reproduces the named source lines
byte for byte, one source line per line, blank lines included.

**A.1, line 76 (V5-B01 required change):**

```text
Required change: Retain file observation identities through the complete walk and revalidate every encountered leaf, including excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted generation from changing before use. Directory-only revalidation or after-run detection must not substitute for pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates.
```

**A.2, line 82 (V5-B02 required change):**

```text
Required change: Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff, rather than observer-only checks before and after it. Use an independently protected writer/location boundary or an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the original guarantee; retain this blocker if custody cannot yet be established.
```

**A.3, lines 84-123 (boundary assessments, N-items, explicit residual rulings, terminal semantics):**

```text
The source-tree problem does not require unchanged timestamps or undetectable file metadata. The earlier leaf's nlink/ctime/content can actually differ; the final algorithm simply never compares those file fields again. An outside hard link does not add/remove/rename an entry in the walked source directory. The frame-mutation problem likewise does not depend on target behavior: the frame's own fd-relative writes/chmod/mkdir can happen after a location check and before its later refusal. Detection and a non-success result are useful, but they do not undo those specified prohibited outcomes.

| Boundary reviewed | Passive assessment | Evidence |
|---|---|---|
| Reviewed/adopted frame and fresh lead | Full fixed roster/profile/sidecar and actual rollout/final/model/cwd/provider/argv joins remain. fresh_lead runs before parent and child admission. This UNQUALIFIED review must fail the required QUALIFIED profile; no adoption or fresh observation was performed. | S:687-863, 1557-1559, 1809-1815 |
| Launch seal carried in argv | The child hashes launch/admission bytes, joins launch to intent/admission and verifies its own argv. Parent conclusion checks launch/intents/reservation/admission/launcher records against in-memory pins and uses the original seal. No re-read local data substitutes for those expectations. | S:1570-1594, 1662-1694, 1783-1817 |
| Token window and other holder protection | Reservation requires released status; ownership joins holder/candidate/token; only parent conclude calls release and checks those fields under the same flock. No conforming-protocol holder overwrite found. Stable lock replacement remains N07. No live window was read or locked by the reviewer. | S:1253-1341, 1735-1755 |
| Full child admission, allowlisted argv, exact environment and caps | Common admission repeats frame/materialization/tool/data/ELF/vendor/runtime/manager checks. Child compares the complete observed environment minus a validated INVOCATION_ID, parent memory gate, final memory threshold, allowlisted command, cgroup unit and effective memory/swap/core limits. Named gate calls are preserved; V5-B01/B02 prevent treating the directory/leaf observations as sufficient custody. | S:1054-1106, 1131-1179, 1440-1448, 1809-1845 |
| Dir location chains and created-directory authentication | Components use O_DIRECTORY/O_NOFOLLOW; created directories require owner/mode/nlink/device/empty/non-ancestor checks before chmod/write. Residual (a) is narrowly acceptable in item 3. V5-B02 blocks full mutation/launch lifetime reliance. | S:155-237, 308-345 |
| observe_tree and verify_materialization | Exact fixed base descriptors/keyset/modes plus validated Ada snapshot/deletions are reconstructed; non-partition and snapshot directory identities are bound to materialization. Partition identities are sealed. The final pass omits file metadata and remains V5-B01. | S:495-582, 868-956, 1030-1044, 1566-1569, 1842-1845 |
| retain/read_record/refusals | Primary/retry/stderr are create-only attempts; cleanup/parsing errors are aggregated. Parent and child pre-launch refusal records include explicit no-target-started meaning. Unparseable child records remain raw and withhold release. Durability is not established when commit fails; N11/N12 describe remaining consumer/schema hardening. | S:375-436, 1530-1537, 1579-1581, 1848-1858 |
| Owned participants and conclude | Active/unavailable scope/cgroup or present known pid/process marker refuses terminal classification; unreadable/unparseable participant records are unresolved. Wait records precede fallible cleanup. Materialization/seals/report/post-identities/raw child-wait read are guarded. Only terminal ownership permits release; release errors/withholding/conclude errors have separate records. | S:1375-1437, 1611-1765 |
| Signal, interrupt and crash paths: dispatch/parent/child | Handled signals are masked through Popen/handle enrollment and recording, child preexec unblocks, and wait_blocked synchronously forwards SIGTERM until actual exit or explicit unresolved wait. Pending sweeps exist at the requested boundaries. SIGKILL/dead launching parent has no late collector and leaves manual reservation resolution. Surviving parent independently observes child/wrapper/launcher scope/pids and treats partial records conservatively. No new lost-started-wait/unsafe-release path was found under those stated ceilings; V5-B02 still affects record custody and N13/N14 affect final error reporting. | S:1469-1517, 1595-1641, 1848-1896, 1918-1988; F:358-361 |
| Retained evidence and reviewed inputs | Writes use exclusive leaves; the report is copied to a distinct exclusive artifact; snapshots/base/launch pins are rechecked; no prune/standing verify/late collect surface exists. This does not grant same-user protected evidence or immutable source proof. V5-B02 can still place frame writes outside the named tree. | S:308-327, 959-1048, 1662-1717, 1991-2007 |

NON-BLOCKING observations (the source references are part of each finding):

- **N01 — Actual fresh per-challenge MCP origin remains a lead obligation.** Shape, parsed/exact fields and in-attempt hash non-reuse do not authenticate actual MCP origin or cross-attempt freshness. Every live challenge still needs the legitimate lead to call actual MCP. Reviewer fixed-expression responses authorize no challenge or launch. Evidence: S:1182-1248, F:85-90;277-280.
- **N03 — Report mtime and zero exit remain engineering observations.** The old separately reread report mtime is fixed: bytes and st_mtime_ns now come from read_observed on the same descriptor. Incremental output may still be old, and neither mtime nor command-zero establishes report origin, full body/caller coverage, proof or acceptance. Evidence: S:1695-1708, F:281-282;366-367.
- **N04 — Copies and prospective identities transfer no original acceptance.** All original support/native-cost/custody/capacity/backup/body/caller/runtime/fault/Phase One obligations remain OPEN. Passing author cases, copied modules and exact arithmetic supply none of those guarantees. Evidence: F:368-373, /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v5/modules/runtime_inventory.py:1-5.
- **N07 — Shared flock still assumes a stable cooperating protocol inode.** O_NONBLOCK and single-link regular-file hardening are implemented. The name/parent/inode of the cooperating lock still must not be independently replaced while another holder uses it. This is the inherited reference ceiling, not a new conforming-protocol overwrite finding. The exception grants no arbitrary outside-tree write. Evidence: S:1253-1292;1295-1341, F:285-286;356-357.
- **N08 — Verified-byte module execution retains its bootstrap and cached-state ceiling.** Fresh exec_verified hashes the exact bytes it compiles/executes. Its sys.modules branch relies on __verified_sha256__ metadata; outer Python bootstrap and path-launched frame entrypoints are not protected pre-main/provider/cached-code custody attestation. Complete prospective identities remain required and original custody obligations remain OPEN. Evidence: S:52-57;587-614, F:277-280;350-355.
- **N09 — Pending-signal sweeps are observations rather than atomic cancellation.** The requested pre-spawn and post-wait sweeps exist. Signals arriving after a sweep can still be forwarded during waiting or arrive later during final recording; the code does not atomically combine signal arrival with Popen. This alone bypasses no admission/cap or terminal-ownership gate. Evidence: S:1478-1517;1596-1606;1861-1884;1923-1930.
- **N11 — Fully written failed primary commits need explicit archival interpretation.** write_json can finish bytes then fail fsync or post-validation. retain leaves that primary and writes a retry/error record; result retries are downgraded. read_record distinguishes unreadable/unparseable bytes but has no separate committed-primary marker, so a syntactically complete failed primary can still be parsed. Current aggregated errors/nonzero wait outcomes prevent scratch success in the affected paths; archival consumers must join primary, retries and refusal/error records instead of treating any parseable primary as durable success. Add explicit committed-record descriptors/markers for consumers. Evidence: S:308-327;387-436;1731-1759;1880-1896.
- **N12 — Participant-record semantic validation is narrower than parse validation.** read_record requires only a JSON object; owned_terminal extracts whichever integer pid fields are present. A valid JSON object with missing/wrong participant fields is not marked unresolved. Scope/cgroup and in-memory launcher observation still independently prevent a demonstrated live conforming participant release. Validate each participant schema and required pid/wait fields before classifying the record. Evidence: S:418-436;1372-1415.
- **N13 — Late directory-close errors are reported after the success calculation.** conclude checks errors after result/release, then guarded handle closes can append further errors. Its success variable and exit decision are not recomputed after those closes, and no new terminal error record is then attempted. This contradicts the blanket any aggregated error means nonzero prose, but occurs after waits/stream sync/terminal observation and does not establish one of the blocking outcomes. Include late close errors in the terminal disposition. Evidence: S:1756-1765, F:215-216.
- **N14 — Dispatch can exit zero despite its own failure or interrupt record.** dispatch terminal.json records failure/notes, but its exit expression considers only code and errors. If the run returns zero, a dispatch failure or interrupt can still leave dispatch exit zero. The actual run wait and terminal failure remain retained and this is not a target admission bypass. Make dispatch exit reflect failure/interrupts too. Evidence: S:1953-1988.

The author self-check's observed case count and success are author reports only. AUTHOR-SELFCHECK.json explicitly excludes adopt and the real run/child launch/scope path. No candidate code, compiler, prover, build, test, reservation or admission action was executed by this reviewer. The Claude adversarial pre-read was not consulted and supplies no closure weight.

**3. Explicit residual rulings**

| Stated residual | Ruling and exact limit | File:line evidence |
|---|---|---|
| (a) Empty owned 0700 directory between mkdir and open | **Acceptable as documented, narrowly.** The frame requires owner, exact mode, link count, same device, empty contents, named/open inode agreement and non-ancestor identity. Substitution of an indistinguishable empty directory at the intended name does not itself redirect a file write to another location or overwrite prior file contents. POSIX mkdir did not return an inode handle, so no original-mkdir identity is established. This ruling is not a continuing location lease; the separate post-check/pre-mutation detachment in V5-B02 remains BLOCKING. | F:117-135; S:192-223 |
| (b) No confinement of the running target; conclusion detection | **Acceptable as documented at the reference engineering ceiling.** Reference run_checks.py starts the target by path/cwd without a filesystem sandbox; it performs before/after readbacks. v5 similarly cannot prevent an already-running target from resolving absolute paths or writing while another process changes the tree. The resulting attempt must remain non-successful on detected drift. All original confinement/custody obligations remain OPEN. This residual does not authorize frame-owned outside-tree mutation, nor an unsafe alias already present at the final launch admission. | F:69-76, 349; S:1512-1517, 1662-1694; F10K/run_checks.py:42-47, 293-325 |
| (c) Executing the identity-checked target by path | **Acceptable as documented at the reference ceiling.** S:1839-1841 checks the allowlisted executable hash; S:1867 executes the sealed argv by path. Full before/after tool/ELF/data/vendor/runtime identity comparisons remain. F10K run_checks.py:43 and :294 use Popen paths too. This establishes no exec-inode, mapped-library or protected pre-main custody; those original guarantees remain OPEN. | F:354-355; S:1131-1153, 1711-1716, 1839-1867; modules/proof_elf_inventory.py:1-5, 85-89 |
| (d) Metadata/timestamp granularity | **Acceptable as documented for genuinely identical compared fields.** Device/inode/mode/nlink/owner/size/mtime_ns/ctime_ns are compared by stat_key, excluding read-altered atime. No claim is made about the actual kernel resolution. A change preserving every compared field is an acknowledged observational limit, not an original consistent-snapshot proof. V5-B01 differs: changed leaf fields are simply never revisited by the final tree pass. | F:363-365; S:138-141, 246-266, 530-567 |

No residual ruling changes a required accepted case, contract, proof floor, control or Phase One exit requirement. None removes V5-B01/V5-B02 or authorizes use of this UNQUALIFIED candidate.
```

## Appendix B. Schemas (exact key sets; every record also carries the §4.4 common fields)

Common fields of every record: `generation` (str, 32 hex), `attempt` (str stamp or `null` for P_adm), `boot_id`
(str), `channel_heads` (`{"F2W": hex, "W2F": hex}` or the pair of the invoking channel), `record_seq` (int),
`prev_commit` (hex or `null` for the first of a journal, §4.4), `at` (UTC ISO-8601 string), `label` (v5 `LABEL`). The
new keys listed below are str, int (|n| < 2^63), bool, null, list or object, never floating-point; embedded v5
structures (observations, samples, v5 record keys) keep their v5 types unchanged.

### B.1 Role identity: `wlscratch-role-identity-v1`

`role` ∈ {`front`, `writer`, `seal-front`, `launcher`, `child`, `observer`, `root-launcher`}; `pid`, `ppid`,
`start_time_ticks` (int); `comm` (str); `argv` (list of str); `exe` `{path, dev, ino, sha256}`; `uids`, `gids` (4 ints:
real, effective, saved, fs); `groups` (list of int); `caps` `{inh, prm, eff, bnd, amb}` (hex str); `no_new_privs`,
`seccomp` (int); `dumpable` `{set_result, pr_get_dumpable, proc_self_fd_uid}` (int); `umask` (int); `rlimits`
`{core, nofile, nproc}` (pairs of int); `cgroup` (str); `namespaces` `{mnt, pid, user}` (int inode); `cwd` `{dev, ino}`;
`stdio` (list of `{fd, type, dev, ino, mode, flags}`, `type` ∈ {`fifo`, `socket`, `regular`, `char`, `dir`, `other`});
`open_fds` (list of int); `environment` `{names, sha256, values}` (values only for the clear keys of §8.1); `python`
`{version, executable, prefix, base_prefix, flags, path}`; `modules` `{files: [{name, path, bytes, sha256}], builtins:
[str]}`; `frame_inventory` `{sha256, bytes}`.

### B.2 Participants, waits, scopes

- `wlscratch-participant-v1`: `role` ∈ {`S1`, `W`, `S2`, `L`, `SR/C`, `T`, `S_O`, `O`, `S3`, `W2`, `RL`}; `pid`,
  `start_time_ticks`, `ppid` (int); `uids`, `gids` (4 ints); `groups`; `cmdline` (list of str); `cgroup` (str);
  `observed_by` (role); `state` ∈ {`alive`, `absent`, `reused`, `unknown`}.
- `wlscratch-wait-v1`: `waiter_role`, `waited_role`; `pid`, `start_time_ticks` (int); `raw_status` (int or null);
  `exited`, `signaled`, `core_dumped` (bool); `exit_code`, `signal` (int or null); `wait_error` (object or null);
  `interrupts` (list); `unresolved` (bool); `meaning` (str).
- `wlscratch-scope-v1`: `manager_uid` (int); `unit` (str); `invocation_id` (str); `control_group` (str);
  `properties_at_start`, `properties_at_end` (objects with `LoadState`, `ActiveState`, `SubState`, `Result`,
  `ControlGroup`, `MemoryMax`, `MemorySwapMax`); `cgroup_state` ∈ {`ABSENT`, `EMPTY`, `NONEMPTY`, `UNAVAILABLE`}.
- `wlscratch-scan-v1`: `stage`; `scans` `{gate, r, w, name, scope, units, refs}`, each `{result: [participant] or
  verdict, unknown: [reason]}`; `verdict` ∈ {`known-terminal`, `live`, `unknown`}.

### B.3 Records

| Record | Schema name | Keys beyond the common fields |
|---|---|---|
| `generation.json` | `wlscratch-generation-v1` | `created_at`, `writer` (B.1), `invocation` `{argv, sudo_user, sudo_uid, sudo_command, n_f}`, `front_triple` `{pid, start_time_ticks, boot_id}`, `lease` `{lease_dir: [dev, ino], lock: [dev, ino], uid, gid, mode}`, `location_chain` (list of `{name, dev, ino, uid, gid, mode, acl_sha256}`), `installed_frame` `{inventory_sha256, inventory_bytes, install_root}`, `setup_identities_sha256`, `channel` `{protocol, n_f, n_w, genesis}`, `verb`, `run_label`, `attempt0` |
| `inputs/<seq>-<name>` and `.json` header | `wlscratch-input-v1` (header) | raw bytes file; header `{seq, name, class ∈ {pinned, joined, observation}, size, mode, sha256, pin_source, verdict}` (§8.6) |
| `inputs/manifest.json` | `wlscratch-inputs-manifest-v1` | `entries` (list of `{seq, name, class, size, mode, sha256, written_to}`), `heads_after_inputs` |
| `materialization.json` | `wlscratch-materialization-v1` | every v5 `claude-scratch-materialization-v5` key (with `run` = g's path), plus `generation_pin`, `inputs_manifest_pin`, `partition_roots` (list of `{path, dev, ino, mode, acl_text}`), `recipe_mode_property` `{files_others_readable, dirs_others_searchable}` |
| `attempts/<A>/attempt.json` | `wlscratch-attempt-v1` | `kind` ∈ {`materialize`, `dispatch`}, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` `{generation, materialization, generation_marker, materialization_marker}`, `lease`, `channel`, `verb`, `args`, `fallback_journal` `{path, bytes, slots}` |
| `launch.json` | v5 keys plus | `generation_pin`, `attempt_pin`, `parent_observation_pin` (O's full walk incl. excluded-leaf keys), `launcher_argv_template`, `child_argv_template` (C), `streams` (names), `front_stage_pins`; v5 `environment` holds the relocated environment |
| `reservation-intent.json`, `reservation.json` | v5 keys plus | `window_lock_identity` `{dev, ino, nlink}` observed by F under the lock, `request_digest` |
| `admission.json` | v5 keys plus | `gate0_receipt_pin`, `front_stage_pins`, `observer_parent_pin`, `writer_half_pins` |
| `launcher-intent.json` | v5 `scope_argv` plus | `launcher_argv`, `seals` `{launch_sha256, admission_sha256}`, `n_w2l`, `streams` (list of `{name, dev, ino}`), `journal_head` |
| `launcher-start.json`, `launcher-wait.json`, `sudo-launcher-wait.json`, `observer-wait-<n>.json` | B.2 participant or wait | — |
| `child-wrapper.json`, `child-stage-<half>.json`, `effective-limits.json`, `child-start.json`, `child-wait.json`, `child-refusal.json`, `child-cleanup.json` | v5 keys | relayed from C, committed by W; plus `relay` `{via: "L", l2c_head, w2l_head}` |
| `spawn-ok.json` | `wlscratch-spawn-ok-v1` | `c_identity_pin`, `admission_summary_sha256`, `front_pong_at`, `writer_errors` (must be empty) |
| `front/front-identity.json`, `front/front-stage-<stage>.json` | `wlscratch-front-stage-v1` | `stage`, `front` (B.1 at stage), `lead_observation`, `frame_admission_front` `{inventory, review, adoption, rollout, adoption_observation}`, `base_tree_observation`, `runtime_observation` (compact or full, v5 item 4), `manager_environment`, `sibling_units`, `storage_reading`, `window_ownership` (child stage), `vault` (where run) |
| `front/front-terminal.json` | `wlscratch-front-terminal-v1` | `s1_wait` (B.2), `w_final`, `w_absent`, `answers_forwarded` (list of `{n, sha256, at}`), `interrupts`, `errors`, `heads`, `durability` |
| `result.json` | v5 `claude-scratch-run-result-v5` keys plus | `record_states` (name → `primary`/`retry`/`fallback`/`unknown`), `durability` ∈ {`complete`, `UNKNOWN`}, `terminal_scans` (B.2 scan), `w1` `{generation, attempt}` |
| `commits/<seq>-<pathhash16>.commit` | `wlscratch-commit-v1` | `seq`, `record` `{path, sha256, bytes, mode}`, `kind` ∈ {`primary`, `retry`} |
| fallback slot payload | `wlscratch-fallback-v1` | `record_name`, `stage`, `errors`, `value_sha256`, `value_bytes`, `value` or `value_truncated: true` |
| `export/<A>/manifest.json` | `wlscratch-export-v1` | `entries` (list of `{export_path, source_path, sha256, bytes, source_marker_sha256}`) |
| `export/<A>/freeze.json` | `wlscratch-freeze-v1` | `manifest_sha256`, `journal_head`, `heads` |
| `channel/<first>-<last>.json` | `wlscratch-channel-segment-v1` | `messages` (list of `{dir, seq, prev, kind, length, payload_sha256, payload or ref {record, offset, length, sha256}}`) |

### B.4 Channel kinds (body key sets) and the states that permit them

| Channel | Kind (direction) | Body keys |
|---|---|---|
| F↔W | `W_HELLO` (W→F) | `n_w`, `writer` (B.1), `generation`, `attempt`, `first_record` (descriptor) |
| | `HELLO_ACK` (F→W) | `n_w`, `front` (B.1) |
| | `REQUEST_INPUTS` (W→F) | `phase` ∈ {`descriptors`, `overlay`, `base`}, `names` |
| | `BEGIN` / `CHUNK` / `END` (either) | `{name, size, mode, sha256, chunks}` / `{index, data_b64}` / `{sha256}` |
| | `STAGE_REQUEST` (W→F) / `STAGE_RESULT` (F→W) | `{stage}` / `{stage, results_sha256}`, followed by `BEGIN`/`CHUNK`/`END` carrying the B.3 front-stage record bytes |
| | `CHALLENGE` (W→F) / `ANSWER` (F→W, then `BEGIN`/`CHUNK`/`END` for the receipt bytes) | `{kind, number, challenge_sha256, expression}` / `{n, line_b64}` |
| | `RECORD_COMMITTED`, `RESERVE_INTENT_COMMITTED`, `LAUNCH_INTENT_COMMITTED`, `RELEASE_INTENT_COMMITTED` (W→F) | `{descriptor, marker_sha256}` |
| | `RESERVE_INTENT_REQ`, `RESERVE_DONE`, `RESERVE_ABORT`, `RELEASE_INTENT_REQ`, `RELEASE_DONE`, `RELEASE_WITHHELD` (F→W) | `{token, prior_window, current_window, reason}` (the keys each needs) |
| | `PROCEED_LAUNCH` (F→W) | `{intent_descriptor}` |
| | `PARTICIPANT`, `TARGET_STARTED`, `TARGET_EXITED` (W→F) | `{participant}` (B.2) |
| | `CHILD_STAGE_REQUEST` (W→F) / `CHILD_STAGE_RESULT` (F→W) | `{stage: "child"}` / `{results_sha256}`, followed by bulk bytes |
| | `PING` (W→F) / `PONG` (F→W) | `{nonce}` |
| | `STOP` (F→W) | `{reason}` |
| | `CONCLUSION` (W→F) | `{result_descriptor, terminal_ok, scans, record_states}` |
| | `FINAL` (W→F) | `{exit_status, success, released, export_manifest_sha256, unknown_records}` |
| | `RECORD_UNKNOWN`, `REFUSAL` (W→F) | `{name, sha256, length, errors}` / `{stage, error}` |
| | `MATERIALIZED` (W→F) | `{generation_descriptor, materialization_descriptor, export_manifest_sha256}` |
| | `BYE` (F→W) | `{}` |
| W↔L | `L_HELLO`, `GO` (+ chunks, + `SCM_RIGHTS` for four descriptors), `LAUNCHER_START`, `RELAY`, `STOP`, `LAUNCHER_WAIT`, `BYE` | `{launcher}` / `{records: [names], fds: [names]}` / `{participant}` / `{inner: <C message>}` / `{reason}` / `{wait}` / `{}` |
| L↔C | `C_HELLO`, `RECORDS` (chunks), `STREAMS` (`SCM_RIGHTS`), `CHILD_STAGE_REQUEST`, `CHILD_STAGE_RESULT`, `SPAWN_REQUEST`, `SPAWN_OK`, `CHILD_START`, `CHILD_WAIT`, `CHILD_REFUSAL`, `CHILD_CLEANUP`, `STOP` | the v5 child record keys for the record-like kinds; `{admission_summary_sha256}` for `SPAWN_REQUEST`; `{spawn_ok_descriptor}` for `SPAWN_OK` |
| W↔O | `O_HELLO`, `OBSERVE_REQUEST`, `OBSERVATION` (chunks), `REPORT_BYTES` (chunks), `O_DONE` | `{observer}` / `{stage}` / B.2 scan, walk and identities / report bytes / `{status}` |

States (in order) for F↔W: `HELLO` → (`INPUTS` for `materialize`) → `PARENT_STAGE` → `GATE0` → `LAUNCH_RECORD` →
`RESERVE` → `MEMORY_GATE` → `ADMIT` → `PROCEED` → `RUNNING` → `CONCLUDE` → `RELEASE` → `EXPORT` → `FINAL` → `DONE`.
A kind outside its state is a channel failure (§7.4). Clean EOF is permitted only in `DONE`; EOF from F in `RUNNING`
or `CONCLUDE` is handled as "front absent" (§9.5), never as a clean end.

## Appendix C. JACKAL results used in this document

All calls through actual MCP `jackal_exact`; each returned status `exact`, `formal` false, lane `rat`, evaluator
sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three non_claims quoted in §14.
`parsed` is the tool's echo.

| Use | parsed | exact | approx (tool display) |
|---|---|---|---|
| v5 frame member total | `13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891` | 38434397 | 38434397 |
| v5 frame review roster | `49133+602614+68556+250916+8543` | 979762 | 979762 |
| base descriptors | `1735+105491+1542` | 108768 | 108768 |
| recipe file-mode rows | `617+18` | 635 | 635 |
| A_idf | `2*3*25492333` | 152953998 | 152953998 |
| A_in, A_jrnl | `128*2^20` | 134217728 | 134217728 |
| A_fb, A_setuprec | `16*2^20` | 16777216 | 16777216 |
| A_tmp | `256*2^20` | 268435456 | 268435456 |
| A_selftest, MAX_FRAME | `64*2^20` | 67108864 | 67108864 |
| A_homes | `1*2^20` | 1048576 | 1048576 |
| A_install | `3*38434397` | 115303191 | 115303191 |
| A_exp, A_retry | `545393048+152953998+134217728` | 832564774 | 832564774 |
| X | `2*545393048+3*152953998+3*134217728+16777216` | 1969078490 | 1969078490 |
| X check | `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` | 0 | 0 |
| W-1 dispatch addition | `2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` | 4340810164 | 4340810164 |
| Required, dispatch | `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` | 15368462701360/1397 | 11001047030.322119 |
| addition check | `15368462701360/1397-9304350902252/1397-4340810164` | 0 | 0 |
| Required, setup | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` | 2027732564230/1397 | 1451490740.3221188 |
| Required, selftest | `2*67108864+134217728+1468268019712/1397` | 1843272351744/1397 | 1319450502.3221188 |
| historical margin, dispatch | `10460753920-10000000000-15368462701360/1397` | -14724789475120/1397 | -10540293110.322119 |
| historical margin, setup | `10460753920-10000000000-2027732564230/1397` | -1384059337990/1397 | -990736820.3221189 |
| historical margin, selftest | `10460753920-10000000000-1843272351744/1397` | -1199599125504/1397 | -858696582.3221189 |
| records payload with images | `545393048+1969078490` | 2514471538 | 2514471538 |
| ideal payload identity | `16777216+2242440646+545393048+1969078490+16777216+2242440646+545393048+1969078490+1468268019712/1397+268435456+134217728-15368462701360/1397` | 0 | 0 |
| CHUNK | `4*2^20` | 4194304 | 4194304 |
| frame headroom | `67108864-4*(4194304+2)/3` | 61516456 | 61516456 |
| fallback slots | `16*2^20/(64*2^10)` | 256 | 256 |
| slot size | `64*2^10` | 65536 | 65536 |
| new groups | `1+1+1` | 3 | 3 |
| new users | `1+1` | 2 | 2 |
| last id of `sicarii`'s subordinate range | `100000+65536-1` | 165535 | 165535 |

Values used as given (observations, or results reproduced by the sealed re-review, not recomputed here): 9304350902252/1397
(v4.3 Required), the allowances of §14.1, 25492333 (O2 runtime closure), 10460753920 (free at 23:32:06Z), 10000000000
(reserve), the file sizes read from `frame-inventory.json`, `wc -c` and the inventory JSON.

