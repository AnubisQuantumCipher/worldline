# SELFCHECK.md — §12.2 step → member coverage, and the construct → premise-served map

FROZEN, REVIEWABLE, UNINSTALLED. Author: Claude (Opus 4.8), DRAFTING implementer, not a reviewer.
Nothing in this lane was executed, compiled, installed, or privileged-run. This is a drafting
self-check for the §16 step-2 code review; it establishes nothing and discharges no premise.

Members produced here (all under this lane directory):
`front.py` (F), `writer.py` (W), `sandbox_launch.py` (RL), `launch_target.py` (L/C/O),
`nsowner_helper.c` (the §12.2-step-10 N-owner / idmap-namespace helper), and `framelib.py` (the
shared reused-primitive module — a disclosed drafting-structure deviation, below). MANIFEST.json
pins each file's sha256 and bytes.

---

## A. The v11 §12.2 step → member+function coverage table

For each step: the member and function that implement it, and the verification that function
performs (v11's own check for that step). "STAGE 1" = steps 1-6 (root, pre-scope); "STAGE 2" =
steps 7-16 (same pid, in the scope, root → dropped to 1000). Where a body is the reviewed base
frame v6 `scratch.py` logic re-homed onto the view (verb bodies), the member cites it and the
installed body carries it; those are marked `(delegates, cited)`.

| §12.2 step | Member.function | Verification the function performs |
|---|---|---|
| 1 first act / role identity / argv grammar | `sandbox_launch.stage1` (+ `load_view_spec`) | first act (v11 §7.7); argv verb/seals grammar; role identity — installed body |
| 2 invoker is W | `sandbox_launch.check_invoker_is_W` | `SUDO_UID==W`; nearest non-`sudo` ancestor via `/proc/<pid>/status` has uid W; else refuse |
| 3 descriptors exactly 0-2 | `sandbox_launch.require_fd_set({0,1,2})` | enumerate `/proc/self/fd` (excluding the scandir fd); refuse unless the open set is exactly {0,1,2} |
| 4 anchors + sealed records | `sandbox_launch.stage1` → `Dir.anchor`; `load_view_spec` | A_T/g anchored chains vs `setup-identities.json`; `launch.json`/`admission.json` sha256 == argv seals; N's account lines == pinned |
| 5 census + root scan | `sandbox_launch.root_scan_no_N` (+ `_ns_owner_uid`, `_pid_in_rl_scope`) | every `/proc/<pid>`: no uid N in any position; no user-ns owned by N outside an RL scope; else refuse (P-NOOWNER/P-SETNS/P-CG evidence) |
| 6 RLIMIT_CORE + exec systemd-run scope | `sandbox_launch.stage1` → `build_scope_argv` | `setrlimit(RLIMIT_CORE,(0,0))`; exec `systemd-run --scope --slice=user-1000.slice …` (system scope, P-CG; §12.3 V10') |
| 7 record initial ns identities | `sandbox_launch.record_initial_ns` | `/proc/self/ns/mnt` inode == PID 1's; `statx('/')` [dev,ino] recorded (mnt-ns unique-id name note below) |
| 8 mount ns + process root | `sandbox_launch.step8_mount_namespace` | `unshare(CLONE_NEWNS)`; `mount_setattr('/',AT_RECURSIVE,{NOSUID,MS_PRIVATE})`; `chdir('/')` |
| 9 network ns + loopback | `sandbox_launch.step9_network_namespace` | `unshare(CLONE_NEWNET)`; bring `lo` up via `SIOCSIFFLAGS`; nothing else |
| 10 U8 + M_run + identity maps | `sandbox_launch.make_owned_userns` + `nsowner_helper.c` | helper assumes N, `unshare(CLONE_NEWUSER)`; RL writes `setgroups`/`uid_map`/`gid_map` (`0 0 4294967295` for U8; `W 1000 1` for M_run); `NS_GET_OWNER_UID==N`; helper reaped, pid gone |
| 11 the two binds + skeleton | `sandbox_launch.step11_bind` / `step11_skeleton` (+ `openat2_nofollow`) | `openat2(RESOLVE_NO_SYMLINKS\|RESOLVE_NO_MAGICLINKS)`; `open_tree(OPEN_TREE_CLONE)` + `mount_setattr(IDMAP(M_run)\|NOSUID,private)` + `move_mount`; skeleton tmpfs + per-entry re-attach + RO remount; an unattachable entry omitted+recorded (§21 V8) |
| 12 mountinfo-independent verify + exact {0,1,2} fds | `sandbox_launch.step12_verify` + `require_fd_set({0,1,2})` | mnt-ns id changed; `statx('/')`==initial [dev,ino] & new mount id; `statx('.')`==`statx('/')`; mountinfo as data only; open-fd set exactly {0,1,2} before execve |
| 13 Landlock | `sandbox_launch.build_landlock_domain` | ruleset handles {MAKE_SOCK,RESOLVE_UNIX,REFER}; REFER on `/`; MAKE_SOCK on the two bind roots; NO RESOLVE_UNIX grant; `landlock_restrict_self` under CAP_SYS_ADMIN (no no_new_privs) |
| 13b seccomp async-submission filter | `sandbox_launch.build_async_submission_filter` + `install_async_submission_filter` | classic BPF: `io_setup`/`io_uring_setup` → `ERRNO\|ENOSYS` on AARCH64 (0/425) and ARM (243/425), else ALLOW; `seccomp(SET_MODE_FILTER)` under CAP_SYS_ADMIN; `/proc/self/status` `Seccomp:2 Seccomp_filters:1` |
| 14 credentials | `sandbox_launch.step14_credentials` | `setns(U8)`; bounding set reduced to F's `CapBnd`; `setgroups` to F's; `setresgid/uid(1000)`; verify `/proc/self/status` (uids/gids 1000, Cap{Prm,Eff,Amb,Inh}=0, NoNewPrivs:0, Seccomp:2) and `NS_GET_OWNER_UID==N` |
| 15 process attributes + environment | `sandbox_launch.apply_process_attributes` `(delegates, cited §8.3)` | applies §8.3's attribute table from `launch.json`; L's env from `launch.json`, O's the target env |
| 16 RL_IDENTITY + execve | `sandbox_launch.send_rl_identity`; `launch_target.read_rl_identity` + `verify_self_exe_mount` | RL writes RL_IDENTITY (§9.3 G3 fields) on fd 0; `execv` L/O; L/C verify `/proc/self/exe` statx mount id == record |

Supporting primitives (reused, cited to base frame v6 `scratch.py`,
sha256 `2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84`):
`framelib.Dir.anchor` (scratch.py:155-172), `Dir.verify_location` (174-190), `Dir.child` (192-223),
`Dir.read_observed` (246-268), `stat_key` (138-141), `retain`/`guarded`/`read_record` (387-424),
the open discipline `O_DIR`/`O_FILE` (104-105). `framelib.commit` is NEW W-1 code (v11 §10.1:
O_TMPFILE + create-only `linkat`), superseding the base frame's create-only `O_CREAT|O_EXCL` write
(scratch.py:308-322); the export-ACL variant is v11 §15.3. The writer lease (`writer.acquire_lease`)
is v11 §5.1; the mutation choke point (`writer.authorize`) is v11 §5.2.

### Flagged installed-build correspondences (for P-KSRC / P-LL review; read-only reads cited)
1. **ARM compat syscall numbers** (`io_setup`=243, `io_uring_setup`=425): NOT present in the aarch64
   `/usr/include` (the 32-bit `unistd_32.h` is a kernel build artifact). Carried from v11 §12.2
   step 13b / Appendix I and marked `CARRIED-FROM-SPEC` in `sandbox_launch.py`; pending S-1/S-2.
   The AARCH64 numbers (`io_setup`=0, `io_uring_setup`=425) and every other syscall number WERE read
   from `/usr/include/asm-generic/unistd.h` and `/usr/include/asm/unistd_64.h` on this box.
2. **`NS_GET_MNTNS_ID`** (v11 §12.2 step 7/12): not in the installed `/usr/include/linux/nsfs.h`,
   which provides `NS_MNT_GET_INFO` instead. `record_initial_ns`/`step12_verify` use the
   `/proc/self/ns/mnt` inode (also named by v11) and flag the ioctl-name correspondence.
3. **`landlock_ruleset_attr` size**: the installed ABI version and the attr size the kernel expects
   are a review dependency (`build_landlock_domain.attr_size_is_review_dependency`); RESOLVE_UNIX
   (1<<16) requires ABI ≥ 6, which the code asserts.
4. **Seccomp/BPF/Landlock/mount/stat constants** were read from the installed
   `/usr/include/linux/{seccomp,audit,elf-em,mount,openat2,landlock,nsfs,stat}.h`; `AUDIT_ARCH_*`
   is composed in code from its named `EM_*`/`__AUDIT_ARCH_*` components, not a magic literal.

---

## B. Construct → NAMED_UNESTABLISHED premise it SERVES

**Implementing a construct is NOT discharging its premise.** Every premise below stays
NAMED_UNESTABLISHED and OPEN (v11 §9.8 N7). Discharge is the operator's reviewed runtime probe —
the E0 source readings (S-2/S-5), the E1 operator-reserved boundary exercises, and the E2 installed
`selftest`/capture runs (v11 §13.1, §13.2) — reviewed in the W1-V9-PREMISE-ORDER order BEFORE O-1
installs the sudo rules. Writing the enforcement that serves a premise only makes the premise
*checkable*; it provides no evidence for it.

| Construct (this lane) | Premise SERVED | Why serving ≠ discharging |
|---|---|---|
| every mount `nosuid` — `step8_mount_namespace` (`MOUNT_ATTR_NOSUID` on `/` recursive), `step11_bind`/`step11_skeleton` (NOSUID on every bind, re-attached entry and the skeleton tmpfs) | **P-NOSUID** | that set-ID bits/file-caps take no effect on exec is a kernel fact about the installed build; only the operator's set-ID/file-cap fixture run in a real view (E1/E2, O-2) can refute it. Operator-only fixture; no installed path builds one. |
| no-capability exec — `step14_credentials` (`setresuid(1000)` clearing Prm/Eff/Amb; bounding set to F's; verify Cap*=0) + the `nosuid` mounts above | **P-NOCAP** | that no view process ever holds a capability in U8 or an ancestor is shown by the credential-computation source (S-2) and refuted only by an E1/E2 exercise; this code only *arranges* the empty sets. |
| N owns every U8 — `make_owned_userns` (helper assumes N; `NS_GET_OWNER_UID==N`) + `root_scan_no_N` + the §5.3 route design (W≠owner; `writer.py` never owns U8) | **P-NOOWNER** | that *no process other than RL's helper* ever has euid N needs the §5.3 route inventory over every principal (S-5/O-1) and the installed root scan (I-1); the helper's existence is the thing to be bounded, not the bound. |
| the step-13b seccomp filter — `build_async_submission_filter` + `install_async_submission_filter` | **P-SECCOMP** | that the filter returns ENOSYS on both tables, cannot be removed/bypassed, and is inherited across fork/exec is an E0 BPF reading against the installed tables + an E2 view probe; installing it is not that evidence. |
| (the filter) + the private net/user ns + Landlock topology — collectively close the async write paths of v11 §9.8 N4 | **P-ASYNC / P-RELEASE** | these are a **closed specification whose completeness is itself unestablished** (v11 §9.8 N4, §13.1). This lane reproduces NO async-holder-defeat procedure; the refutation exercise is OBLIGATION-level, operator-reserved, procedure OPEN (§16.1 O-ASYNC). The discharge/refute predicate is the operator's byte-equality state, not anything here. |
| the two idmapped binds — `step11_bind`/`make_owned_userns` M_run (`W 1000 1`) | **P-IDMAP, P-XMNT** | on-disk-W-as-1000 and cross-mount `EXDEV` are kernel facts refuted only by an E1/E2 view exercise. |
| the private mount ns + propagation + skeleton — `step8_mount_namespace`, `step11_skeleton` | **P-ROOT, P-MSET, P-PROP, P-SKEL** | each is a source-reading obligation (S-2) + benign unprivileged observation (U-5) + I-1; the construction only presents the view. |
| the Landlock domain — `build_landlock_domain` | **P-LL, P-LOCK** | the socket/refer semantics and the topology lock are S-2 readings + U-2/I-4 exercises. |
| the private network ns — `step9_network_namespace` | **P-NETNS** | abstract-socket scoping + the setns requirement are S-2 + U-4/I-1. |
| the system scope in user-1000.slice — `build_scope_argv` (RL) + the setup scope properties | **P-CG, P-SLICE, P-MGR, P-LOGLEVEL** | cgroup/manager/slice behaviour is S-3 + I-3; RL only *creates* the scope. |
| the writer lease + mutation choke point — `writer.acquire_lease`, `writer.authorize` | serves the N0(c) "every frame mutation lies in T" obligation (V5-B02) | V5-B02 stays OPEN; the single choke point makes the mutation set auditable, it does not prove it complete. |
| `O_NOATIME` owner reads in the members | **P-NOATIME** | a source/observation obligation; unchanged from v5's read discipline. |

Critical premises (P-NOSUID, P-NOCAP, P-NOOWNER, P-ASYNC, P-SECCOMP, plus P-KSRC): a refutation of
any ONE stops every installed use and forces redesign (v11 §9.8 N7). None is discharged here.

---

## C. Disclosed drafting deviations
1. **`framelib.py` (shared module).** v11 §3.2 names four Python members; the reused custody
   primitives live in `framelib.py` so the four members stay byte-reviewable instead of carrying
   four divergent copies. It is root-owned installed code either way (import resolves from the
   script directory under `python3 -I`). Adds no authority and no mutation path. (framelib.py header.)
2. **`nsowner_helper.c` as a native `execv` target.** v11 §12.2 step 10 says RL "forks a helper";
   this lane renders the helper as a tiny reviewable C program RL fork+execs (the directive asks for
   the named C helper as `.c` source). The helper "runs no other code" and exits before L exists, as
   the spec requires; the fork-then-exec rendering is the disclosed difference.
3. **Verb bodies delegated.** The reviewed base-frame v5/v6 verb logic (adopt/materialize/dispatch/
   seal-front, journals/commits/admission/observe/spawn, the window protocol) is cited, not
   re-transcribed; this enforcement-core lane authors the privilege split, the lease, the O_TMPFILE
   commit, and the whole §12.2 view. The delegated bodies are the installed members' reviewed code.
4. **`front` issues the writer, not RL.** The operator directive's one-line summary said "front …
   issues RL and writer"; the authoritative v11 §3.2/§5.1 chain is F→W (S1) and W→RL (RL rule), with
   the lease held by W. This lane follows v11.

## D. Confirmation
- EXECUTED NOTHING, INSTALLED NOTHING, COMPILED NOTHING, ran no sudo/unshare/mount/seccomp/
  systemctl/prover/test, created no set-ID/capability object, collected/wrote no password, marked
  nothing executed. The only commands run were read-only header/metadata reads, `ast.parse` syntax
  checks of this lane's own drafts, `sha256sum`/`wc`, and JACKAL MCP calls.
- Every NAMED_UNESTABLISHED premise stays OPEN; adoption stays blocked (v11 §23, sealed v11 review
  NOT_ENDORSED); every original contract/fixture/control/proof-floor/source-identity preserved; the
  base frame `scratch.py` is referenced, never modified.
- Honest provenance: this is Claude (Opus 4.8) drafting work; it is never GPT/GPT-6.1 work and
  grants no acceptance.
- SIA (`sia` MCP server) was DISCONNECTED this session (reported connection failure, not a missing
  capability), so no start/end SIA recall or note could be written through it; recorded for the next
  session to leave the durable note once SIA is reachable.
