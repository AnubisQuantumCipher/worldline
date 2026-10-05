# GAP.md — W-1 v11 §16/§12.2 component inventory: EXISTS / PARTIAL / MISSING

This is the directive's "record which components already exist and which still need
implementation." For each component that v11 §16 (setup/adoption) and §12.2 (view
construction) require, the status is one of:

- **EXISTS** — already implemented in the frozen base frame v6 `scratch.py`
  (`/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v6/scratch.py`,
  sha256 `2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84`), cited by function/line.
- **PARTIAL** — a related mechanism exists (in `scratch.py` or the uninstalled, unreviewed
  prototype `frame-v6w1-proto/w1proto.py`) but the W-1 form is incomplete.
- **MISSING** — no frozen, reviewable W-1 code exists; the design is specified in v11 only.
- **N/A** — not an installed artifact by design, or conditional on the images storage option.

Nothing below has been installed, executed, or privileged-run. The base frame v6 `scratch.py`
is the v5/v6 **unprivileged, single-process DAC frame**. The W-1 layer splits it into four
installed members (`front.py`, `writer.py`, `sandbox_launch.py` = RL, `launch_target.py`) under
root-owned `/opt/wlscratch/frame-v6w1/`, adds two system identities, two sudo rules, an sshd
drop-in, a lease, a protected run tree, and the privileged view construction. The verb LOGIC
(adopt/materialize/dispatch, commits/journals, admission, observe/final-pass, window protocol)
largely EXISTS in `scratch.py`; the **privilege split and the kernel-confinement view do not
exist as frozen code at all** — they are the bulk of the MISSING set.

Counts (JACKAL exact, see MANIFEST.json): EXISTS 6, PARTIAL 7, MISSING 30 (sum = 43); N/A 3;
43 + 3 = 46 line items.

---

## E. EXISTS in frame v6 scratch.py (6)

| # | Component (v11 ref) | Status | Citation in scratch.py |
|---|---|---|---|
| E1 | Anchored descriptor chains `Dir.anchor` — §3.4 anchors (A_T, A_R, g, O_DIRECTORY\|O_NOFOLLOW per component from `/`) | EXISTS | `class Dir` L144; `Dir.anchor` L156; `O_DIR` L104 |
| E2 | `verify_location` on held handles (the §3.4 / H-M2 location re-check) | EXISTS | `Dir.verify_location` L174; used by `child` H-M2 L120-126 of FRAME plan |
| E3 | fd / `O_CLOEXEC` / `O_NOFOLLOW` / `O_NOATIME` / `O_DIRECTORY` open discipline (generic) | EXISTS | `O_DIR` L104, `O_FILE` L105; create-only opens L312, L331, L1290 |
| E4 | `observe_tree` + final-pass re-stat of every accepted file (V5-B01 fix; feeds §15.3 capture) | EXISTS | `observe_tree` L495; `stat_key` L138; `read_files` L579 |
| E5 | Shared-window `flock(LOCK_EX)` protocol (frame-plan N07; §9.4 window) | EXISTS | `window_locked` L1263 (flock LOCK_EX L1274); `window_write` L1287; `reserve` L1304; `release` L1330 |
| E6 | Create-only record/marker commit + journal (retain / guarded / read_record; downgrade-on-failure) | EXISTS | `retain` L387; `guarded` L409; `read_record` L418; `write_bytes` O_CREAT\|O_EXCL\|O_NOFOLLOW L308 |

## P. PARTIAL (7)

| # | Component (v11 ref) | Status | What exists / what is missing |
|---|---|---|---|
| P1 | Writer lease `writer.lock` creation + per-invocation checks (§5.1): root:W 0440 lease, flock(LOCK_EX\|LOCK_NB), anchored lease dir, fstat+xattr identity | PARTIAL | `acquire_lease` exists in the UNINSTALLED, UNREVIEWED prototype `frame-v6w1-proto/w1proto.py` L30 (sha256 `2c7d6100…`); `scratch.py`'s flock is on the shared WINDOW lock (E5), not the writer lease. The installed lease OBJECT (S-B) and `writer.py`'s §5.1 checks are MISSING. |
| P2 | Commit primitive via `O_TMPFILE` + create-only `linkat` (§5.2, §10.2) | PARTIAL | `scratch.py` uses `O_CREAT\|O_EXCL\|O_NOFOLLOW` create-only (E6); the `O_TMPFILE`-then-`linkat` nameless form §10.2 describes is NOT present. |
| P3 | Exact open-fd set `{0,1,2}` + O_CLOEXEC verification before `execve` (§12.2 step 12; §9.3 G4/C1) | PARTIAL | the generic O_CLOEXEC discipline exists (E3); the RL/launcher/child exact-`{0,1,2}`-set check (close every post-step-8 fd, verify set is exactly {0,1,2} immediately before execve) is RL-specific and MISSING. |
| P4 | The per-attempt confinement scope (§12.2 step 6; §8.3; §12.3 V10') | PARTIAL | `scratch.py` L1579 runs `systemd-run --user --scope` in `app.slice` (v5's USER scope). W-1 requires RL to run `systemd-run --scope --slice=user-1000.slice` (a SYSTEM scope no non-root process can enter/leave, premise P-CG). The W-1 form is MISSING (lives in RL). Property spec: `assets/systemd/wlscratch-scope.properties`. |
| P5 | Fresh installed-frame adoption record (§4.6, §16 step 9) + review-provenance join (§23) | PARTIAL | `adopt` L825, `rollout_join` L696, `validate_adoption_observation` L773, `review_profile_problems` L757 exist and write an adoption record; v5 wrote it OUTSIDE the run tree in the frame's review dir — §4.6 MOVES it inside T at `runs/records/adoption-<I>/`, and §23's review-provenance join change is itself UNREVIEWED and blocks adoption. Both the relocation and the join change are MISSING/unreviewed. |
| P6 | Freeze / export / complete capture (§15.3) with export ACLs and payload pack | PARTIAL | `observe_tree`/`read_files`/final pass (E4) give the capture-read machinery; the §15.3 export primitive (P_exp copies, `user:1000:r-x`/`r--` export ACLs, payload pack, `capture-<A>/`) is MISSING. |
| P7 | Chained framing + streamed-input pins + non-dumpable writer (§7.2-§7.4; §12.2 step 10 `PR_SET_DUMPABLE 0`) | PARTIAL | `encode_message`/`decode_message` (framing), `verify_inputs` (pins) and `set_nondumpable` exist in the UNINSTALLED prototype `w1proto.py` (L63/L78/L100/L132); not in `scratch.py`, not frozen as a frame member. |

## M. MISSING — no frozen W-1 code (30)

### Identities and accounts (§3.1, §5.4, §11.2, S-A)
| # | Component | Setup/spec ref | Asset (bytes produced here) |
|---|---|---|---|
| M1 | group `wlscratch` (W=950), user-private | S-A k1 | `assets/scripts/S-A-accounts.sh` |
| M2 | group `wlscratch-ns` (N=951), user-private | S-A k2 | same |
| M3 | account `wlscratch` (uid/gid 950, nologin, --no-create-home, locked) | S-A k3 | same |
| M4 | account `wlscratch-ns` (uid/gid 951, nologin, --no-create-home, locked, `usermod -e 1` expired) | S-A k4 | same |
| M5 | subordinate-ID exclusion + numeric policy verification (P1-P4, §5.4) | §11.2/§11.3 | `assets/notes/numeric-identity.md` (spec); the operator prestate run is MISSING |

### Privilege policy (§5.3, §11.5 S-D/S-E, §11.3 P12/P13)
| # | Component | Setup/spec ref | Asset (bytes produced here) |
|---|---|---|---|
| M6 | `sudoers.d/wlscratch-frame`: `WLSCRATCH_W` Cmnd_Alias + S1 rule `sicarii ALL=(wlscratch) NOPASSWD: WLSCRATCH_W` + `Defaults!WLSCRATCH_W !log_allowed,!pam_session,!pam_setcred,!use_pty` | S-D | `assets/sudoers.d/wlscratch-frame` (validator-ready) |
| M7 | `sudoers.d/wlscratch-rl`: `WLSCRATCH_RL` Cmnd_Alias + RL rule `wlscratch ALL=(root) NOPASSWD: WLSCRATCH_RL` + its `Defaults!` | S-D | `assets/sudoers.d/wlscratch-rl` |
| M8 | sshd drop-in `30-wlscratch.conf`: `DenyUsers wlscratch wlscratch-ns` | S-E | `assets/sshd_config.d/30-wlscratch.conf` |

### Lease, run tree, installed frame (§5.1, §6.3, §11.5 S-B/S-C)
| # | Component | Setup/spec ref | Asset / note |
|---|---|---|---|
| M9 | lease dir `/var/lib/wlscratch/lease` (root:W 0750) + `writer.lock` (root:W 0440, empty) install | S-B 1-3 | `assets/scripts/S-B-lease-runtree.sh` |
| M10 | run tree `/var/lib/wlscratch` (root:W 0750), `runs/` (W:W 0700) T_root, `runs/records` (W:W 0700) R_root + the three `u:1000:--x` search ACLs | S-B 4-5; §6.3 | `assets/scripts/S-B-lease-runtree.sh`; `assets/acl/*.expected` |
| M11 | installed frame member `front.py` (F; verbs adopt/materialize/dispatch; uid 1000) | §3.2; S-C | — (frame member not written/frozen) |
| M12 | installed frame member `writer.py` (W; adopt/materialize/dispatch/selftest/seal-front; §5.1 lease, §5.2 mutation set) | §3.2; S-C | — |
| M13 | installed frame member `sandbox_launch.py` (RL, root; the whole §12.2 view construction) | §3.2; S-C | — |
| M14 | installed frame member `launch_target.py` (L/C/O) | §3.2; S-C | — |

### View construction — all inside RL (`sandbox_launch.py`), §12.2 (none of these exist anywhere)
| # | Component | Spec ref |
|---|---|---|
| M15 | step 8: `unshare(CLONE_NEWNS)` copy of the mount tree + `mount_setattr("/",AT_RECURSIVE,{MOUNT_ATTR_NOSUID,MS_PRIVATE})` + process-root move | §12.2 step 8 |
| M16 | step 9: `unshare(CLONE_NEWNET)` + loopback up, nothing else | §12.2 step 9 |
| M17 | step 10: the N helper (setgroups(0)/setresgid(N)/setresuid(N)/PR_SET_DUMPABLE 0/`unshare(CLONE_NEWUSER)`); U8 owned by N; `uid_map`/`gid_map` `0 0 4294967295`; M_run idmap `W 1000 1`; helper reaped before L exists | §12.2 step 10 |
| M18 | step 11: the two idmapped binds (`open_tree(OPEN_TREE_CLONE)`+`mount_setattr(MOUNT_ATTR_IDMAP\|NOSUID,private)`+`move_mount`) and the skeleton tmpfs path presentation | §12.2 step 11; `assets/notes/prestate-and-skeleton-spec.md` |
| M19 | step 12: mountinfo-independent verification (`NS_GET_MNTNS_ID`, `statx` mount-root/`statmount`/`listmount`, every mount `nosuid`) + the exact `{0,1,2}` fd close/verify (see P3) | §12.2 step 12 |
| M20 | step 13: Landlock ruleset handling `MAKE_SOCK`/`RESOLVE_UNIX`/`REFER`, `REFER` on `/`, `MAKE_SOCK` on the two bind roots, no `RESOLVE_UNIX`, applied with `landlock_restrict_self` under CAP_SYS_ADMIN | §12.2 step 13 |
| M21 | step 13b: the asynchronous-submission seccomp filter — classic BPF returning `SECCOMP_RET_ERRNO\|ENOSYS` for `io_setup` and `io_uring_setup` on both syscall tables (AARCH64 nr 0/425; ARM nr 243/425), `SECCOMP_RET_ALLOW` otherwise; `seccomp(SECCOMP_SET_MODE_FILTER)` under CAP_SYS_ADMIN, no `no_new_privs`; `Seccomp:2 Seccomp_filters:1` | §12.2 step 13b; §9.8 N4; §12.3 V14 |
| M22 | step 14: credential drop (`setns` U8, bounding set reduced to F's CapBnd, `setgroups` to F's, `setresgid(1000)`/`setresuid(1000)` clearing Prm/Eff/Amb; `/proc/self/status` verify; `NS_GET_OWNER_UID`==N) | §12.2 step 14 |
| M23 | step 15: process attributes from `launch.json` + environment (L's from launch.json, O's the target env) | §12.2 step 15 |
| M24 | step 16: `RL_IDENTITY` on fd 0 + `execve` of L or O through the view root | §12.2 step 16 |

### Setup mechanism and reconciliation (§11.4, §11.5, §11.6, §11.7)
| # | Component | Spec ref | Asset / note |
|---|---|---|---|
| M25 | staged-rename file atoms (`staged_install`/`staged_activate`/`staged_deactivate`; `renameat2 RENAME_NOREPLACE`; fail-closed deactivation on failed combined checks) | §11.4; S-common | `assets/scripts/S-common.inc.sh` + used in S-C/S-D/S-E |
| M26 | reviewed setup helpers `absent.py`, `step.py`, `check_out.py` | §11.5 | `assets/helpers/{absent,step,check_out}.py` (byte-exact transcriptions) |
| M27 | `setup-identities.json` generator (S-H) + §11.7 pinned/mutable field policy | §11.5 S-H; §11.7 | — (generator not written) |
| M28 | S-R reconciliation against the reachable set (67 / 104 states incl. the `userdel` co-removal states X1-X4 / W_A / W_B) | §11.4 | — (not written); reachable-set count is spec-exact, carried verbatim |
| M29 | post-setup verification (lead §11.6; operator S-I; P-SUDO before/after) | §11.5 S-I; §11.6 | — |

### Rollback (§15.1)
| # | Component | Spec ref | Asset |
|---|---|---|---|
| M30 | rollback state machine R1-R9 + retained-tree manifest M0/M1 equality | §15.1 | `assets/scripts/rollback.sh` (template); `ROLLBACK.md` |

## N/A — not an installed artifact, or conditional (3)

| # | Component | Why N/A |
|---|---|---|
| NA1 | polkit rule | W-1 installs NONE by design; the polkit requirement is the P13 inventory obligation (no subject resolves to W/N). See `assets/notes/polkit.md`. |
| NA2 | systemd image mount-unit files (S-J J5a/J7a) + enablement | only exist if the images storage option (S-1 option 3) is chosen; the no-images configuration installs no unit file. |
| NA3 | image work/records files, loop devices, mounts (§14.5) | images-only; not part of the default no-images setup. |

---

## Cross-cutting notes for the reviewer

1. **The view is the gap.** M15-M24 (the entire kernel-confinement view) and M11-M14 (the four
   frame members) do not exist as code anywhere — not in `scratch.py`, and only lease/framing/
   input-pin/non-dumpable fragments exist in the uninstalled `w1proto.py` prototype (P1, P7).
   The step-13b seccomp filter (M21) and the Landlock ruleset (M20) are enforcement code that
   this drafting session deliberately did NOT author (see AUTHOR-NOTES.md); their exact SPEC is
   recorded above and in the notes.

2. **Every NAMED_UNESTABLISHED premise stays OPEN.** A spec-level statement (what this package
   contains) is not execution evidence. The critical premises P-NOSUID, P-NOCAP, P-NOOWNER,
   P-SECCOMP, P-ASYNC (§9.8 N7) are OPEN; their E0 source discharges and the independent review
   of those discharges are a PRE-O-1 gate (§16 step 5b). The P-ASYNC/P-RELEASE async-holder
   refutation procedure is OBLIGATION-level and OPEN, owned by the operator package (§16.1
   O-ASYNC); this package reproduces NO such procedure.

3. **Adoption is blocked.** §16 step 9-10: the review-provenance join change (§23) is itself an
   unreviewed change to an original admission join; v11 does not reach adoption. P5 records this.

4. **Preserved originals.** This package adds nothing that weakens or removes a frame contract,
   fixture, control, proof floor or source identity. The base `scratch.py` is referenced, not
   modified. The 67/104 reachable-set count and the 19-atom (no-images) / 30-atom (images) counts
   are carried verbatim from v11's own JACKAL-exact derivations (§11.4), not re-derived here.
