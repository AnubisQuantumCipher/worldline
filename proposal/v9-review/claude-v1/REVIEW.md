# W-1 v9 independent design review (ISOLATION-STORAGE-PROPOSAL-v9.md)

**Reviewer:** an independent Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review and I am not the drafting agent.
**Verdict: NOT_ENDORSED.** This review grants no acceptance, approval, exception, proof acceptance, phase acceptance or source acceptance. Every original Phase One obligation stays OPEN.

**Hashes (computed by this reviewer):**
- Brief `briefs/w1-design-v9.md`: sha256 `baef3a28237d014c603d558fe9cff7b32a9fef1188f4578f650bd536601cb0e5`, 75 lines.
- Override: `bdb0815da741d72468c05087cb7a4136445cba26c533e69e24dee03935530b00`.
- v9: `4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b`, 562201 bytes, 5143 lines. Matches the brief.
- `v9-support/jackal.json`: `2d225e26780c95035f2ef57d79cc1a1758304fb82f08c4a75adab254d2b02270`. Matches the brief.
- v8: `804da95b…c4367a6`. Matches. v7: `8646f0fe…bb41bd0`. Matches.
- The sealed v8 Claude review: REVIEW.md `38dcb076…`, review.json `afc0d828…`, checks.json `0bbdf32b…` and review-freeze.json `c0a2bc3f…`. All four match the brief and v9:16-21.
- Author-process NOTE.md: `80c85076…`.

**Independence and limits.**
- I did not read the following:
  - `v8-review/gpt61-v1`, `review-records/`, any v9 review directory, any transcript or rollout, or `~/.local/share/sia/.gbrain/`.
  - Drafts in progress.
- I made no SIA query, so that SIA recall about v9 reviews could not contaminate independence. This is disclosed.
- Nothing was executed except passive reading, hashing, read-only grep/listing and in-memory Python unit hashing. No file was written.
- Earlier reviews (v7/v6 gpt61-v1, package-review gpt61-v1..7) were not re-read. For their statuses I rely on the sealed v8 Claude review's `prior_closure`, which v9 §18.2-§18.4 quotes verbatim.
- The frame-v5 review is read only through v9 Appendix A's verbatim blocks.
- Kernel behaviour below that I could not verify against the installed source is labelled "(my unverified reasoning on upstream behaviour)".

---

## 1. Closure of the W1-V8 required changes, and of the earlier items

| Required change | Author | This review | Would the specified run establish it, if it produced the stated result? (none executed) |
|---|---|---|---|
| **W1-V8-HOLDER-IOEXIT** | CLOSED-AT-SPEC-LEVEL (redesign) | **PARTIALLY_CLOSED** | **Partly.** Denying `io_setup`/`io_uring_setup` closes the two named paths (§2 below). But the closed list N4 (i)-(vi) omits a context in which task-created references outlive the cgroup exit (v9:1970-1973, 1983-1984). S-2 gives no exhaustive enumeration basis for the universal P-ASYNC (v9:3413). U-9 does not hold the memory context across exit (v9:3388, 3431). The self-check claims overstate what they detect (v9:1989-1991, 2355-2356, 3729-3731). |
| **W1-V8-PRESERVATION-ESTABLISH** | OPEN | **NOT_CLOSED** | **No.** The change inventory is incomplete (§7: cross-mount `EXDEV`, M_run id restrictions). U-11 and I-7 are runs the original constraints forbid or block, and they are under-budgeted (§5). I-7 has no nondeterminism control. |
| **W1-V8-PREMISE-DISCHARGE** | OPEN (needs execution) | **NOT_CLOSED** | **Insufficient as ordered and specified:**<br>- The independent review of the critical S-readings comes after installation (v9:3772-3773, 3779-3783), while A1 can drive installed RL as soon as S-D runs (§5).<br>- S-1 does not bind the *running* kernel to the package (v9:3412).<br>- P-NOOWNER's inventory is scoped to `sicarii` (§3).<br>- P-ASYNC has no enumeration basis. |
| **W1-V8-WRITER-AS-W** | CLOSED-AT-SPEC-LEVEL | **CLOSED_AT_SPEC_LEVEL** for the W vector. This rests on P-NOOWNER, whose route inventory is incomplete (new RC W1-V9-NOOWNER-SCOPE). | Not applicable, beyond P-NOOWNER's discharge. |
| **W1-V8-COMPOSED-ENUM** | CLOSED-AT-SPEC-LEVEL | **PARTIALLY_CLOSED** | Counts reproduce under JACKAL (exact). The reachable set is **not** complete (§4), so O-5's rehearsal would be classified against an incomplete table. |
| **W1-V8-EVIDENCE-EQUIV** | OPEN for the establishment | **PARTIALLY_CLOSED** | Consumers B1-B5 and their predicates are named (v9:1377-1392). U-14/I-6 would establish B1-B5 for the tested trees only (per input). Capacity stays OPEN. The consistency claim inherits the P-ASYNC gaps and the self-check overclaim. |
| **W1-V8-FORM-SUBUNIT** | CLOSED-AT-SPEC-LEVEL | **CLOSED_AT_SPEC_LEVEL** | Verified in full (§6). Minor consistency defects are noted there. |

**Earlier items.** Everything the v8 review CLOSED stays closed in substance:
- W1-V7-ARCHITECTURE: the c8 analysis holds with owner N ≠ 1000 (v9:1903).
- W1-V7-VIEW-ROOT: step 8 and step 12 are unchanged in substance (v9:3142-3146, 3176-3184).
- W1-V7-C3-DATA: C2 `RECORDS` still delivers `launcher-rl-identity.json` (v9:1533-1543).
- W1-V7-PROBES, W1-V7-SYNC-PROVENANCE (v9:2290-2325), W1-V7-PREMISES.
- Every CLOSED_AT_SPEC_LEVEL_CARRIED correction, gap and sub-gap.

The release-rule paragraphs carried by reference in v8 are inlined. I diffed v7:1652-1695 against v9:1668-1717: only v8's deadline→EOF amendments and one added paragraph differ, so W1-DURABILITY-RELEASE is preserved.

Every item the v8 review left PARTIALLY_CLOSED or NOT_CLOSED stays at that status:
- W1-V7-HOLDER-STATE, W1-V7-FULL-DOMAIN, W1-V7-READ-EFFECTS (routes R-d, R-e', R-f, R-h, R-i, R-j OPEN, v9:2032-2033), W1-V7-COMPOSED-STATE, W1-V7-EVIDENCE-RESTORE.
- W1-V5-PRESERVATION and W1-V6-PRESERVE (NOT_CLOSED).
- The custody/setup/protocol group and the six partially closed gaps and nine sub-gaps, for the reasons in §2-§5.

## 2. The seccomp / asynchronous-I/O redesign

**What it closes.**
- The filter program (v9:3189-3199) denies `io_setup` (aarch64 0, compat 243) and `io_uring_setup` (425 on both tables).
  - I read the installed build's generated `unistd_64.h:4,284` and `unistd_32.h:204,382`; they define exactly these numbers.
  - `.config` sets `CONFIG_AIO=y`, `CONFIG_IO_URING=y` and `CONFIG_COMPAT=y` (observed).
- An AIO context is created only by `io_setup`, and `io_submit` and the related calls need that context. A context is not inherited by `fork` or `exec`. So AIO "via other syscalls" is closed (my unverified reasoning on upstream behaviour).
- An `io_uring` ring is created only by `io_uring_setup`. `io_uring_enter`/`register` need a ring descriptor, and none can reach a view: T receives only `/dev/null` and its two streams (v9:1117-1118), and push routes are closed (N1).
  - Spec gap: step 12 closes only descriptors opened *before* step 8 (v9:3182-3183).
  - Descriptors RL opens after step 8 (the held g directory, the helper's ns fd, `open_tree` fds, the Landlock ruleset fd) are not stated closed or `O_CLOEXEC`.
  - G4 and C1 check fd types only (v9:1497-1499, 1528), not an exact fd set {0,1,2}. This must be made exact (RC W1-V9-INVENTORY).
- `splice`, `vmsplice`, `sendfile`, `copy_file_range`, synchronous direct I/O, writeback of already-dirtied pages, `fsync` of other descriptors, timers and signals: none changes logical content after the task's last syscall returns. N4 (i)/(v) states this correctly.
- binder: `CONFIG_ANDROID_BINDER_IPC=y` (observed), but there is no device and binderfs needs a mount (Landlock).
- userfaultfd: `CONFIG_USERFAULTFD` is not set in `.config` (observed; v9 does not mention it).
- NFS/FUSE are irrelevant to g, which is on ext4, and no view process can mount.

**What it does not state correctly.**
1. **The closed list omits the outside memory-context holder as a context for final `fput`.**
   - N4 (iv) names two contexts for a deferred final `fput`: task work before cgroup exit, or the UNIX-socket GC (v9:1970-1973).
   - A world-readable `/proc/<pid>/cmdline` read by A1 takes `mm_users` (v9:1920-1921). While it is held, `exit_mm` does not tear down the mappings. The `vm_file` references of every mapping of an admitted file are then dropped by A1's `mmput`, **after** the cgroup exit, in A1's task context.
   - P-RELEASE (v9:2067) is stated context-free, so the effect class may still hold. But N4's "From (2) to (3)" claims every task-created reference is held "by tasks of U, by sockets only they could read, or by kernel objects reachable only through those … none by a principal outside the tree" (v9:1983-1984). That is literally false for this case: N0 counts "a mapping of E" as a reference (v9:1848-1850).
   - The argument must be restated: the reference is held, but unusable, because `get_mm_cmdline` reads anonymous memory only and there is no ptrace access.
   - N2's "briefly" (v9:1921) is understated. A1 can make the copy-out target a FUSE-backed page (FUSE is a module here, `fusermount3` is set-ID, v9:209) and stall the read indefinitely while the mm is held (my unverified reasoning on upstream `get_mm_cmdline`).
2. **P-ASYNC is a universal negative over the whole kernel, but S-2 lists only named functions** (v9:3413). There is no enumeration basis, such as every entry of both syscall tables plus every kernel context that can hold a task-created file or mm reference past exit (task_work, the delayed-`fput` workqueue, the UNIX GC, outside `mmput` via `get_task_mm` callers, io-wq, kernel threads). This repeats the v8 review's P-IOEXIT observation (v8 REVIEW.md:67) in a new form: "S" is claimed, but the procedure cannot show completeness.
3. **U-9 / the P-ASYNC probe** (v9:3388, 3431) only "repeatedly reads" `/proc/<pid>/cmdline`. It does not hold the mm across the exit or observe the file after the holder releases it, and "a recorded period" is unspecified. As a refutation it cannot exercise the path in point 1.
4. **The self-checks overclaim.**
   - "a refutation of P-ASYNC in practice would show as a failed self-check, never as a silent change" (v9:1989-1991, 2355-2356; similarly 3729-3731).
   - Equal `stat_key` readings detect only changes inside the readings' window. A late write after the last reading, or after `stream-finality.json` or the capture is committed, would be silent.
   - The self-check is evidence for its own window only.

**Domain effect and classification.** V14 is listed as an OPEN target-world change with discharge S-6/U-11/I-7 (v9:3241, 4185). It is not presented as preserving, which is correct.
- A passive string search of `~/opt/gnat` found `io_uring`/`io_submit` strings only in sanitizer runtimes and gdb, not in the gnatprove/gprbuild/prover binaries.
- That is an observation, not a discharge: raw syscalls leave no symbol, and absence of a string is not absence of use.
- No original accepted case is shown to use AIO or `io_uring`, and none is shown not to.

## 3. The namespace-owner account N

- **The W vector is removed.** U8's owner is N (v9:3148-3150), so A1's euid-W `writer.py` holds no capability over U8 (v9:1905). This closes W1-V8-WRITER-AS-W at spec level.
- **Construction is sound** (my unverified reasoning on upstream behaviour):
  - The helper `setresuid(N)` → `PR_SET_DUMPABLE 0` → `unshare(CLONE_NEWUSER)` sequence is sound. After the uid change, dumpability falls to `suid_dumpable=2` (observed), so no ptrace window opens.
  - Root writes the maps; `verify_root_map` is satisfied because the opener is root.
  - The mount and network namespaces are owned by the initial user namespace (v9:3146). So even an euid-N process could not `setns` into the view's mount namespace, but it could `setns` into U8 and gain full capabilities there.
  - Because the identity map includes every id, those capabilities would give it DAC override over every host inode. P-NOOWNER is therefore correctly marked critical (v9:3220-3222).
- **The route closure is under-scoped.**
  - §2.3 (v9:247-251), §5.3 (v9:958, 964), P12 (v9:2452: "`sudo -l -U sicarii` … no rule names N"), P13 (v9:2453: polkit grants to `sicarii` or its groups only) and S-I (v9:2998-2999) check `sicarii`'s routes and rules that *name* N.
  - They do not exclude:
    - a rule for any other principal whose Runas list resolves to N through `ALL`, `%wlscratch-ns`, `#951`, an alias or a negation;
    - a polkit grant to any other subject for unit management or exec-as-user (for example `systemd-run --uid=wlscratch-ns`).
  - This host has other non-root accounts (`cosmov1lab`, `wlrehearsal`, `wldrill`, `worldline`, v9:974-975).
  - P-NOOWNER says "no process other than RL's helper ever has euid N" (v9:2050). Its discharge must cover every principal and every Runas and polkit form. The same applies to W.
  - New RC W1-V9-NOOWNER-SCOPE.
- **Operator reservation is correct.** The accounts are S-A atoms k2/k4 (v9:2844, 2851-2858) inside O-1 (v9:3804), and N is expired at setup (v9:962).

## 4. §11.4 atom table and reachable set

- **Arithmetic reproduces (JACKAL exact).**
  - 19 atoms; 63 + 3·n_d + 5·n_m states.
  - With images: 30 atoms; 100 + 3·n_d + 5·n_m states.
- **Independent per-atom recount.**
  - Forward intermediates: `1+1+2+3+2+2+2+2+2+0+0+0+2+2+3+3+3+0+3` = 33.
  - Total without images: `(19+1)+33+(1+1+1+1+1+1+1+1)+1+1` = 63.
  - With images: `(30+1)+(33-(2+2)+(2+4+4+2+3+3+2+2+0+0+1+1+2))+(8+1+1+1+1)+1+1` = 100.
  - All JACKAL exact.
- **The enumeration is incomplete, so "exactly" (v9:2575) and "never *other*" (v9:3031-3032) are false.**
  - `/etc/login.defs:305` sets `USERGROUPS_ENAB yes` (observed). The account class says `userdel` then removes the same-name user-private group (v9:3016). That applies to **k3 (`userdel wlscratch` removes group W, k1)** as well as k4, but only W_A, for k4, is modelled (v9:2584-2585).
  - The class table implies an update order: passwd before shadow (account I_rev), group before gshadow (group I_rev).
  - Under that order, these reachable states are missing (none is G_j, G_j^±(s), D_SD or W_A):
    - **X1:** k1 post, k2 = "gshadow without group", k3 post, k4 absent (inside k4's `userdel`).
    - **X2:** k1 post, k2 absent, k3 = "shadow without passwd", k4 absent (k3's `userdel` from W_A).
    - **X3:** k1 = "gshadow without group", k2 post, k3 absent (k3's `userdel` from G_3).
    - **X4:** k1 absent, k2 post, k3 absent (that `userdel` completed).
  - That makes at least 67 constant states (JACKAL exact: `63+1+1+1+1`).
  - S-R's **reverse** has no rule from W_A (v9:2622-2626; resume only, v9:2619). After `userdel` co-removes a group, the reversing `groupdel` of k2/k1 is a failing command, so S-R stops (v9:2629).
  - Whether `useradd` touches `/var/log/lastlog` (present, 0 bytes, observed) is unverified and should be captured as a possible co-object.
- **The rollback table** (v9:3629-3643) is a separate machine with per-step states. It is acceptable as specified.

## 5. §13.2 / §16.1 plan

The plan is ordered, S/P/T kinds are used consistently, nothing is presented as executed (v9:3405-3406, 4113-4116), and "redesign, no exception" is kept (v9:2040-2042, 3400). Defects:

- **Steps that violate original constraints and gates.**
  - U-11 (v9:3433) runs every allowlisted action, which is `gnatprove`/`gprbuild` per `scratch.py:88, 1054-1070`, in the original context with no frame. START-CLAUDE.txt:8 forbids that: "do not … launch the raw prover outside the reviewed frame".
  - I-7 (v9:3451) runs the same actions through the original v5 frame (unadopted; V5-B01/B02 OPEN) and through the selftest view before adoption.
  - Neither step has a dispatch-stage Gate 0 receipt. I-7 runs at the selftest stage, whose allowance is A_selftest 67108864 bytes (v9:3495, 3504), against full proof outputs budgeted elsewhere at A_obj 2242440646. That lowers the capacity gate in effect, against the storage ruling "keep dispatch deferred" (v9:193-195).
  - I-7's "any difference refutes" also lacks an original-versus-original nondeterminism control: v9:4147-4154 makes timing-dependent prover outcomes part of the relation.
- **Order of critical premise discharge.** S-2's discharge requires "an independent review accepts the reading" (v9:3413). §16 places that review at step 8 (v9:3772-3773, 3782-3783), after installation (step 6) and selftests (step 7). From S-D onward A1 can run `writer.py selftest` through the S1 rule (`writer.py *`, v9:2927-2929) and so drive installed RL. P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP and P-ASYNC therefore meet installed use before their reviewed discharge, contrary to W1-V8-PREMISE-DISCHARGE.
- **Installed RL manufactures the catastrophic fixture on demand.** O-2 (v9:3805) has RL's `selftest` verb write a set-user-ID-root program and a `cap_dac_override` program, as root, into a view tmpfs.
  - Through S1 → `writer.py selftest` → RL, A1 can invoke that path at will.
  - If P-NOSUID ever failed, that path would hand A1 euid 0 in an identity-mapped U8, which means host DAC override.
  - The writer's test-only switches (v9:3266-3268, 3351, 3362) are likewise installed and reachable through `writer.py *`.
  - None of this is listed in N5 or §2.2. S-5 (v9:3416) does not require showing that the test paths cannot affect real state.
- **S-1** binds the installed package files (`pacman -Qkk`) but not the running kernel image or build-id to that package (v9:3412). P-KSRC concerns the code that runs.
- **Positives.** The S/P/T classes are correct elsewhere, and there is no circular P-VIEW qualification. One inconsistency:
  - §11.6 records a "candidate view baseline" (v9:3043-3044, 3782).
  - §8.4 says the only new baseline is the writer-context one (v9:1353).
  - The candidate view baseline must be evidence only, never a comparison baseline.
- **Operator package.** O-1..O-5 are correctly operator-reserved, and each is labelled "not a new gate" (v9:3798-3800).

## 6. Form

- v9 is self-contained (v9:64-68). I recomputed the units of v7 (124), v8 (131) and v9 (134) by the §0.1 rule.
- **All 134 rows of §18.5 verify** against the recomputed units: every v8 line range, byte count and sha256, and every v9 line range, byte count and sha256 except §18.5's own, as stated.
- Every "= v7 unit" row (41) equals a v7 unit with the same sha256 that v8's map marked CARRIED. No unmarked v9 unit equals a v7 unit. Only Appendix H equals a v8 unit.
- Statuses: 86 COMPOSED = 45 v8-C + 41 v8-A; 44 REVISED = 38 v8-R + 6 new in v8; JACKAL `45+41+38+6+1-131` = 0, `131+3` = 134.
- I diffed the four v8-CARRIED units that v9 edited (8.1, 14.5, 15.4, B.1). The edits are coherent with v9's changes.
- Consistency defects (not self-containment defects):
  - §8.1 names `wlscratch-role-identity-v1` (v9:1247), but B.1 defines `-v2` (v9:4379).
  - §9.1 names `wlscratch-scope-v2` and `wlscratch-census-v1` (v9:1433-1435), but B.2 defines `-v3` and `-v2` (v9:4404, 4408).
  - The header's list of critical premises (v9:51-52) omits P-SECCOMP, which N7 includes (v9:2041-2042).

## 7. Weakening, assumptions, gates and review provenance

- **Domain-change inventory incomplete (an undisclosed narrowing until listed).** §12.3 claims the complete known inventory (v9:3224-3242).
  - In v5 the run tree, `TMPDIR`, `/tmp` and `$HOME` were on one mount (mount 32, v9:270-271). In v9 a `rename`/`link` between the run tree, `TMPDIR` and any other host path fails with `EXDEV`. The author's own probe expects this (v9:3315), yet no V-row lists it.
  - Through M_run (uid/gid `W 1000 1`), the target can no longer `chgrp` its files to its supplementary groups, and can no longer set ACL entries that name other ids (P-IDMAP, v9:2063). §6.1 says the target sets ACLs "as in v5" (v9:989-993).
  - Possibly also user keyrings, which are per user namespace (my unverified reasoning).
  - These must become OPEN V-rows.
- **Gates and thresholds.** No approval gate is added. Release is still not conditioned on durability, capture or H(U) (v9:1675-1676, 2398-2399).
  - The dispatch success conjunction now also requires a committed capture, final streams and `observed` provenance (v9:2363-2367). These are disclosed as D6 OPEN (v9:4207), not as a redefinition of success.
  - Gate 0 allowances are only raised (v9:3470).
  - Under-budgeting does occur through I-7 (§5).
- **Review provenance.**
  - v9 records the conflict honestly as an open item, "not decided here" (v9:3789-3794, 4124-4125, 4093). It is stale against D-LEAD-REVIEW-PROVENANCE (STATUS.md:326-346, ~19:05Z), which v9 does not state.
  - v9 names only "§4.6's adoption joins". Further sites depend on GPT rollout provenance:
    - AD4 provenance triples (v9:526) and D7 rollout joins (v9:624);
    - §4.6 joins 1-2 and the consumers' "rollout re-join" at the parent and child stages (v9:847-850, 872);
    - the `~/.codex/sessions` uniqueness check (v9:862-866) and §8.6 (v9:1410, 1414);
    - the B.3 adoption key set (`reviewer_thread`, `rollout`, `exec_argv`…, v9:839-840, 4467);
    - Appendix D J5/A3/A6 (v9:4775, 4816, 4819) and §17 (v9:3817-3818);
    - the adoption payload pack's "provenance triples" (v9:3674);
    - v5's compiled `REVIEW_PROFILE` `actual_model_selection: gpt-6.1-sol` (`scratch.py:98-103`).
  - The joins are part of the boundary the sealed v5 review recorded (Appendix A, v9:4332).
  - The original requirement says to keep the review gate blocked rather than substitute a model (`complete-phase1-prompt.txt:60`; HANDOFF.md:173).
  - The lead records that the human's 17:05Z direction superseded this (STATUS.md:279-290). Even so, replacing the compiled join is a change to an original admission join. It must be stated as such, with that authority quoted exactly. It is not shown as "not a loosening" by assertion (STATUS.md:341-342).
  - It must also be reviewed in the frame-design revision. Until then, v9 as written cannot reach adoption.

## Why NOT_ENDORSED

1. V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE remain unestablished, and every §21 row is OPEN.
2. Every premise is NAMED_UNESTABLISHED. The critical ones would meet installed use before their reviewed discharge.
3. HOLDER-IOEXIT, COMPOSED-ENUM and EVIDENCE-EQUIV are only partially closed, for the concrete defects above.
4. The plan contains runs that violate START-CLAUDE.txt:8 and are under-budgeted against Gate 0.
5. Installed RL can manufacture set-ID fixtures at A1's request.
6. The domain-change inventory omits at least two observable changes.

## Required changes (none weakens any obligation)

See review.json `required_changes`: W1-V9-ASYNC-ENUM, W1-V9-NOOWNER-SCOPE, W1-V9-ENUM-USERDEL, W1-V9-PLAN-CONSTRAINTS, W1-V9-PREMISE-ORDER, W1-V9-RL-SELFTEST-FIXTURE, W1-V9-INVENTORY, W1-V9-REVIEW-PROVENANCE and W1-V9-FORM-CONSISTENCY. The execution-bound W1-V8-PRESERVATION-ESTABLISH, W1-V8-PREMISE-DISCHARGE and W1-V8-EVIDENCE-EQUIV stay required.
