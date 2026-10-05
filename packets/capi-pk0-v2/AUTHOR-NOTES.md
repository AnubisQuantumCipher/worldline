# PK-0 v2 author notes

PK-0 v2 revises the C-API characterization packet PK-0 in answer to its sealed source review.
- Review: `packets/capi-pk0/review/gpt61-v1`, actual model gpt-6.1-sol.
- Verdict: ENDORSED_WITH_REQUIRED_CHANGES, with required changes PK0-RC1 to PK0-RC5. Run, control, proof, phase and source acceptance are all false.
- v1 (`packets/capi-pk0/`) is unchanged. v2 is a new directory with the same layout: `packet.json`, `files/tests/*`, this file and `jackal.json`.

**Status: authored source, never run.**
- Nothing in this packet was executed, imported or compiled. It holds no run evidence and grants no control, proof or acceptance credit.
- The `json.load` and `ast.parse` checks in section 8 are text inspection only.
- The gate is unchanged: a baseline run on L0 in an admitted frame. It is blocked by the confinement gate (V5-B01, V5-B02) and the capacity gate.

## 1. Review identity, checked against its freeze

`sha256sum` (read-only) over `review/gpt61-v1/` gave these values, each equal to `review-freeze.json` in digest, size and mode 0600:

| File | sha256 | bytes |
|---|---|---|
| REVIEW.md | `7d86d533a9705a606d663d426c491dde94238d4cf688decf26ec85940bfcd769` | 32572 |
| review.json | `fc615b5be33f0caf4e2964e06b2d001d2568c12088c9ca306bb8500bd70dbdf5` | 24374 |
| checks.json | `949b6150258d0f963a901954ad4dc99705b46112be003450e8039d38ecf81886` | 65269 |

`review-freeze.json` itself is `fa987ae0…72c3`.

The task message quoted the review.json prefix as `fc615b5b0d75…`. The file and the freeze both give `fc615b5be33f…`. I used the frozen value (deviation 1).

## 2. Base and invariants (unchanged)

L0 is `W/work/claude-composition-v5-beta/source`. Its three identity files were re-observed:
- composition.json `a0e0bb5c…fa3e`
- source-inventory.json `3407119b…937a`
- review/gpt61-v1/review.json `df6cbc9d…3476`

The invariants:
- REQUIRED_PROVED: 0 names appended. The prefix length 535 is carried from v1 and from the review's own count; v2 did not recount it.
- `MINIMUM_CHECKS = 251` and `UNANALYZED_BOUNDARY = {"worldline-c_api"}`, re-read at `runtime/worldline/proof_manifest.py:22` and `:316`.
- 31 lines of `core/worldline-c_api.ads` contain External_Name (re-counted with `grep -c`).
- Movers: 0. No existing file is touched. None of the six payload paths exists in L0 (re-checked). The payload is the same six new test files.

Bound inputs:
- All 95 v1 bound inputs were re-hashed. All 95 paths are distinct, and none differs in sha256 or size.
- v2 adds 5 bound inputs that it reads or depends on (`packet.json`): `core/worldline-collapse.ads`, `runtime/worldline/environment.py`, `runtime/worldline/raw_completion_kernel.py`, `tests/test_finalization_kernel.py` and `tests/test_raw_evaluation_default.py`. That makes 100 (J32).
- Two host headers are recorded separately because they are not L0: `/usr/include/signal.h` and `/usr/include/bits/signum-generic.h`, for SIG_DFL, SIG_ERR and `signal`.

## 3. Answers to the required changes

### PK0-RC1: mixed-entry ready and authorized coverage

v1 never reached Agent_Ready = 1, so the context joins at `evaluation_finalization_c.adb:473-484` and the Kind-1 metadata joins at `:491-502` had no cases. v2 adds a child-only builder, `b_mixed_ready`, and 46 cases (`U15y_*`) plus 27 exact C-06 cases (D29-D55).

**Faithful ready inputs.** The sources are produced by the S5 runtime producers, driven by the S5 test fixtures that drive them.
- Kind 2 uses `FinalizationNativeControls.sealed`/`capture`/`joined` (`tests/test_finalization_kernel.py:30-84, 224-255`) and `FinalizationKernel.prepare_finalization`.
- Kind 1 uses `RawRequiredFailureControls.prepared`/`joined` (`tests/test_raw_evaluation_default.py:25-69`) with the base fixture `tests/test_evaluation_roster_d2.py:28-55`.
- The agent is the S5 Agent-origin record (`test_finalization_kernel.py:252-254`).
- `_adopt` copies every byte those producers make into the guarded mapping and rewrites only pointer fields. It fails closed: a pointer that names no owner, or two owners, is a PlacementError.
- These producers call native exports, so the builder runs only inside the forked case child, or inside the diagnostic child before its first step.

**A finding about S5.** The S5 candidate request leaves Resulting_Requirement absent:
- `test_raw_evaluation_default.py:71-82` and `test_finalization_kernel.py:245-255`.
- `Required_Present` (`worldline-collapse.ads:139-156`) then fails, so `Decide` cannot be Authorized (`:213-217`).
- The S5 tests nevertheless assert `'AUTHORIZED'` (`test_raw_evaluation_default.py:89`, `test_finalization_kernel.py:262-263`). Those S5 tests are unexecuted. By source reading, their assertion contradicts the collapse contract.
- PK-0 does not edit them. The U15y requests set Resulting_Requirement = Current_Requirement so that the Authorized route is reachable. This is recorded as an original obligation for review, not repaired.

**Routes covered:**
- primary-only candidate request with ready Kind 2 or Kind 1 source;
- staged-only checkpoint request (Tested_Root differs from Staged_Content_Root, staged fields covering) with ready Kind 2 or Kind 1;
- both, with Kind 2 primary and Kind 1 staged, which is the genuine S5 `decide_mixed` mix (`finalization_kernel.py:286-322`).

For each route:
- **Authorized** (code 0). The relational oracle `collapse_ready` must itself be 0.
- **Context-join refusals.** Kind 1 nested guard groups: input extents (null context), transport (Agent_Confinement differs), field, row, row field, required, and join false. Kind 2 nested groups: transport, null metadata, join false, and the inner metadata mismatch.
- **Kind-1 metadata-join refusals after Authorized:** payload mismatch, row and transport.
- **Engine-origin agent:** Agent_Ready 0, roster-clear decision, oracle `collapse_zeroed`.
- **Staged refusals** in staged-only and both modes. In both mode, the primary-first refusal leaves the staged context unread.

**Precise nested frontiers.**
- The export table's R1 entry now lists the join conjuncts and `join_frontiers` (Kind 1 context, Kind 2 context, Kind 1 metadata) with their S5 lines.
- C-05 twins place PROT_NONE on every context or metadata object beyond each refusal: `unreadable`, or `prefix` where a refusal stops inside a row array.
- Authorized paths carry `end` guards on every nonempty object.

**Route discrimination.** Every refusal returns 255, so each refusal case has three checks:
- an unguarded twin that asserts no byte changed;
- a guarded twin;
- an exact C-06 byte stream naming the refusing site.

Each refusal case also requires `collapse_ready` to be Authorized. A fixture that is not ready therefore cannot pass as a join refusal.

**Kept unchanged:** all 609 v1 cases and all 28 v1 diagnostic cases, byte-identical in content and order, including the zero-roster U15x cases.

**Unexercisable (with reasons):**
- the Final_Context_Matches seal refusal (`:273-278`, unreachable after Read_Ready on unchanged bytes);
- Operation /= 3 (`:281`, refused earlier).

**not_exercised (stated, not claimed unexercisable):**
- the Start.Required extent conjuncts (`:281-289`): I did not establish whether they are reachable;
- Context_Matches and Metadata_Matches transport conjuncts other than one representative each.

### PK0-RC2: every --record path output-only

**Layout `--record`:**
- prints layout export values and ctypes layouts, and compiles nothing;
- reads a header measurement only with `--headers PATH SHA256`, and only after the file's SHA-256 equals the bound value;
- without that argument, the header entry says NOT_MEASURED.

**Header measurement** is split out as `--measure-headers` (not a record path):
- it compiles inside a fresh directory under `WORLDLINE_PK0_SCRATCH`, which must be an existing absolute directory, or the run fails;
- TMPDIR for the compiler is set to that scratch;
- it prints the measurement with the compiler argv, status and complete output (hex).
- The unittest header test uses the same scratch-confined measurement.

**All three `--record` modes:**
- refuse to start unless `sys.flags.dont_write_bytecode` is set by the launch (-B or PYTHONDONTWRITEBYTECODE);
- open no file except that bound measurement;
- write only to stdout.
- Characterization record children use anonymous memory and a pipe. Diagnostic record children are started with PYTHONDONTWRITEBYTECODE=1. D06's write to `/dev/full` is a device write, not a file.

The false claims are corrected in `packet.json`, `capi_layout_baseline.json` (status), and the docstrings of `test_capi_layout_identity.py` and `test_capi_characterization.py`.

No automatic baseline writer was added. Observations still enter the record only through a reviewed change.

### PK0-RC3: a protection fault can never become an expected code

**Policy** (`capi_guard_pages.py`):
- In every case child, after the native runtime was initialized in the parent, `establish_fatal_faults()` sets SIGSEGV, SIGBUS, SIGILL and SIGFPE to SIG_DFL through libc `signal`.
- `verify_fatal_faults()` re-asserts SIG_DFL immediately before and immediately after every export call, and the diagnostics control calls, and requires that SIG_DFL was the disposition already in force. A changed disposition fails the case.
- A fault therefore ends the child by its signal. `assert_child_ok` fails the case on any abnormal status, before any code is compared.
- The relational oracle runs under the same policy.

**Negative control** (`HarnessFaultControl.test_protection_fault_is_never_a_code`):
- It is harness-only and calls no WORLDLINE export.
- Under the runtime initialized in the test process, a forked child maps one object "unreadable" with the helper's own layout and mprotect code, applies the policy, and reads the protected byte (`protected_probe`).
- The control requires all of the following:
  - the child ended by SIGSEGV or SIGBUS;
  - it reported nothing;
  - `assert_child_ok` raises the test failure exception on that status.
- It retains the abnormal status in its assertion messages and encodes no WORLDLINE class-X expectation.
- It runs only when the admitted launch runs the suite. Nothing runs it at import or in a record mode. It was not run here.

**Limits:**
- A handler reinstalled during an export call and used inside that same call is not prevented. It is detected after the call and fails the case.
- Faults outside the guarded mapping are not observed.
- SIG_DFL also makes a stack-overflow trap fatal, which the GNAT runtime may otherwise turn into Storage_Error and a handler code. That is consistent with "class H is never an accepted refusal".

### PK0-RC4: lossless fd 2 bytes

`test_capi_diagnostics.py` now compares the raw fd 2 bytes exactly:
- A recorded line list renders to ASCII lines, each followed by one LF.
- A stream that is not such a list is recorded as `{"hex": …}`.
- No replacement decoding remains. The child's stdout report is decoded strictly; an undecodable report fails the case.
- `--record` prints `fd2_hex` and `fd2_segments_latin1`. The second splits after each LF, keeps every terminator and any final unterminated piece, and maps bytes losslessly.
- Python-level stderr is redirected before any import in the child, so fd 2 carries native output only.
- Call steps are built and mutated before the first step runs, so producer native calls cannot write diagnostic lines into the stream.
- `test_rendering_is_exact_bytes` checks the renderer and the splitter without the library.

D06 stays RECORD_ON_L0. Its baseline must be recorded as exact bytes.

The LF terminator of `Ada.Text_IO.Put_Line` on this platform is a prediction: the comparison checks it, and S5 does not state it.

### PK0-RC5: isolation, import and layout statements corrected

| v1 statement | Correction (where) |
|---|---|
| "At import they read JSON and nothing else" (AUTHOR-NOTES v1 §1) | Importing `test_capi_characterization` imports the helper (loads libc via `ctypes.CDLL(None)`) and the runtime ctypes modules. `test_capi_layout_identity` and `test_capi_diagnostics` read JSON and import stdlib only. No native WORLDLINE call happens at import. |
| "Every native call runs in a forked child" (v1 notes §2.5; helper and characterization docstrings) | Decision calls, their oracle and their guard pages are forked. Library load and runtime initialization (Core), the layout, version and sentinel queries, and b_chain's native hash calls run in the parent. Diagnostic call steps run in the fresh child interpreter itself, not a further fork. Child-only builders call producers in the child. |
| "The child imports nothing and logs nothing" (v1 §6.7) | Case children may import S5 test fixtures and runtime modules (child-only builders). They log nothing and write only to the pipe. |
| No-timeout/hang statements (v1 §6.7) | No deadline in select/read/waitpid or subprocess.run. A hung child blocks the current parent. A hang is never a pass. Supervision is a launch requirement (below), not a semantic cap. |
| "The runtime bindings compare ctypes with the library at load time" (layout module docstring; v1 §6.2) | Core validates only its own `_LAYOUTS` at construction. The pending, completion, finalization and recovery kernels check their layouts only in their constructors, which the v1 builders never call. The U15y builders do construct FinalizationKernel, CompletionKernel and RawCompletionKernel in the child, as the S5 fixtures do. No automatic agreement of all ctypes layouts is claimed; C-13 records each spelling separately. |
| Header probe scratch | The probe follows the ambient temporary directory no longer. It is confined to `WORLDLINE_PK0_SCRATCH`, and compiler output is retained. |

**Launch requirements.** The future admitted launch must provide and evidence these. All are OPEN; none is claimed here.
1. Bytecode writing disabled before the first import of every interpreter (discovery parent, `--record`, `--measure-headers`). Diagnostic children set it themselves.
2. `WORLDLINE_PK0_SCRATCH` and `TMPDIR` bound to owned, admitted scratch.
3. `WORLDLINE_CORE_LIB` and `PYTHONPATH=runtime` selected as in S5 (`scripts/assurance.py:236, 273`).
4. Reviewed supervision of every process: the unittest parent, every forked case child, every diagnostic child, the compiler and the probe. It needs deadlines and kill/collect evidence, and a timeout is a failed run.
5. The launch's own stdout and stderr captured byte for byte.
6. HarnessFaultControl run in the same launch, its abnormal status retained, before any baseline value is accepted.

## 4. Change list against v1

`packet.json` lists each file with its v1 and v2 sha256 and bytes.

| File | Change |
|---|---|
| `capi_guard_pages.py` | Docstring rewritten (RC5). Fault policy and checks (RC3). `protected_probe`. `_map` and `_protect` factored. Strict UTF-8 report decode. Layout, placement and comparison logic unchanged. |
| `test_capi_characterization.py` | Docstring (RC5). `b_mixed_ready`, `_adopt` and the fixture helpers (RC1). `oracle_collapse_ready`. `build_scenario`. Child-only building in `run_case`. `assert_child_ok`. `oracle_value` check. Record-shape checks. HarnessFaultControl (RC3). `--record` bytecode gate (RC2). All v1 builders, mutations and expectation logic unchanged. |
| `test_capi_diagnostics.py` | Byte-exact fd 2 (RC4). Pre-built call steps. Fault policy around control calls. Lossless record output. Record bytecode gate. Renderer self-test. |
| `test_capi_layout_identity.py` | Scratch-confined header measurement. `--measure-headers`. Output-only `--record` with a bound `--headers`. Corrected docstring (RC2, RC5). C-07 and C-13 assertions unchanged. |
| `capi_layout_baseline.json` | Line 5 (status) only. All 179 placeholders (J33) and every other line unchanged. |
| `capi_characterization.json` | `design.revision`, two rules, and controls C-03/C-05/C-06/C-11 text. The mixed export entry gains the R1 join conjuncts, `join_frontiers`, the R3 note, unexercisable additions and `not_exercised`. 46 U15y cases and 27 diagnostic cases appended. Every v1 case and diagnostic case, and every other export entry, is unchanged (checked by script, section 8). |

## 5. Placeholders (RECORD_ON_L0; none can pass)

These are unchanged from v1:
- all 25 layout export values, 82 ctypes layouts and 72 header layouts;
- the written result of U14d_R3_classify_op2_record, U15f_R3_capture_op2_record and U15f_R3_seal_op3_record (code 0 is asserted);
- D06: the first stop after `/dev/full`, the final stop after the restore, and the fd 2 stream, to be recorded as exact bytes.

v2 adds no placeholder. Every U15y and D29-D55 expectation is derived from the source and fails on disagreement.

## 6. Uncertainties (in addition to v1's, which stand)

1. **U15y fixture validity.** Every U15y and D29-D55 expectation rests on the S5 fixtures being ready as assumed. That means seal Promotion 1, raw Retain_Terminal with Promotion 1, the Agent-origin record admitted, and contexts joining. If one is not, the positive case and the oracle check fail visibly; nothing passes by another route.
2. **Exact diagnostic sequences** are derived from the bodies (sites listed in each case). Nested SPARK functions (Seal, Join_Context, Decide_Envelope, Confined_Admit_Wire) emit no lines.
3. **The derived Kind-1 mixed path** differs from the S5 tests' raw v3 export. The cited S5 tests supply fixtures, not expectations, for the mixed entry.

## 7. Deviations

1. The review.json prefix in the task message (`fc615b5b0d75…`) differs from the frozen value. The frozen value was used.
2. The U15y collapse requests add Resulting_Requirement, which differs from the S5 fixtures' request (finding in §3, RC1). S5 is not edited.
3. Two not-exercised groups are stated rather than covered (§3, RC1).
4. The normal header test now requires the `WORLDLINE_PK0_SCRATCH` binding. A missing binding fails; it never skips.
5. Launch supervision, bytecode suppression and scratch are defined as launch requirements. They cannot be established by source, and remain OPEN.

## 8. Process record

**Writes.** Write and Edit only, only under `WT/packets/capi-pk0-v2/`. No write was refused. Large files were built by Write followed by Edit appends.

**Bash, read-only.** `sha256sum`, `sed -n`, `grep`, `awk`, `wc`, `ls`, `cat`, `df -h`, `test -e`, and Python heredoc scripts that read and print (`json.load`, `ast.parse`, `hashlib`). No redirection, mkdir, cp, mv, rm, tee, chmod or touch. Nothing touched `/home/sicarii` itself, `~/iPad`, `~/iPadBackup` or `.gbrain`.

**Nothing executed or interrupted.**
- No test, pytest, WORLDLINE module, packet module, compiler, prover or native build was run or imported.
- No TaskStop, kill, timeout wrapper or background task was used.

**Services.**
- SIA: one `sia.ask` at the start, and no note.
- JACKAL: J28-J33 in three sequential groups of at most four, each exact, formal false, lane rat, evaluator `4c0ae28d…d872`. J31 is unused and recorded as such. J01-J27 are carried.
- All eight Ada skills were loaded (ada, ada-omarchy, spark-users-guide, ada-programming, advanced-ada, gnat-toolchain, ada-2005-amendment, ada-high-integrity).

**Verification, by text only.**
- Every JSON file loads and every Python file parses.
- All 609 v1 cases and 28 v1 diagnostic cases are identical in v2 and in order. The only changed export entry is the mixed entry.
- 655 unique case ids (J28) and 55 diagnostic cases (J29).
- Every refusal case's code equals its class code. No U15y case expects a write.
- Every diagnostic call names an existing unguarded case. Every U15y guard name is one that `_adopt` derives from the ctypes field names.
