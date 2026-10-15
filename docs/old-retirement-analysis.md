# Full-value and `'Old` retirement investigation

Source target: `a1bda52b53a9a220b2333fe09a135e2d94127dbc`. Binding engineering disposition is recorded in docs/decisions.md D5; independent acceptance is NOT PERFORMED. Relative experiment paths in this document resolve under scratch/old-analysis unless explicitly prefixed scratch/reviewer or core/.

Current verdict: **NOT ACHIEVABLE ON THIS TOOLCHAIN for the inspected candidate mechanisms.** This is a mechanism-specific engineering verdict, not a universal impossibility theorem. The initial experiments and corrected independent reviewer experiments are completed and retained below. The original conjunction remains **UNVERIFIED** and its production gate **FAILED-OPEN**. No narrowed production claim is selected.

## Exact original claim

The requirement is the entire conjunction, retained from `historical/value-lifetime-design.json` (`retained_exact_contracts`) and the current source:

- All valid original Strings and every Character, empty lines and duplicate lines as distinct positions, arbitrary chronological FIFO, without a new cumulative line/byte/count ceiling.
- `Push` retains `Appended (Pending_Contents'Old, Pending_Contents, Text)` and nonempty postcondition. Full strings/order/prefix matter, not only count or a hash.
- `Take_All (Items : aliased out Line_Access)` retains `Contents (Items) = Pending_Contents'Old and then Empty`; pointer-only native reversal and by-reference exceptional ownership handoff remain.
- Full-value snapshots are ordinary nonlimited values independent of subsequent native mutation and release. Their backing storage retires automatically when no live value needs it, including compiler-generated `'Old` constants and exceptional postcondition exits.
- No new caller snapshot-death precondition, application `Controlled`/`SPARK_Mode Off`/custom-pool proof boundary, hidden model side effects, permanent allocations, ignored Ghost, `Assume`, justified checks, full-value encoding into a scalar, or new cumulative bound.
- Native `Push` keeps one complete-text allocation and constant link operations; `Take_All` moves links without copying runtime text or allocating runtime nodes. Checked model evaluation and retirement cost remain part of the requirement. Explicit retirement of native `Line_Access` is distinct from retirement of inaccessible model `'Old` values.

## Affected contract and obligation inventory

The complete literal `'Old` search is retained in `evidence/all-old-contract-occurrences.txt`, with its exact command and commit in `evidence/all-old-contract-command.json`. Ordinary scalar/inline array `'Old` occurrences are not evidence of this lifetime defect.

| Source and contract | Missing obligation |
|---|---|
| `core/native_diagnostic_trace.ads:31` `Contents` | Complete physical-order independent value; structural termination; no borrowing that survives source mutation; representation lifetime and actual checked allocation/retirement remain open. |
| `core/native_diagnostic_trace.ads:37` `Pending_Contents` | Complete chronological independent value, exact effects, no hidden output or owner move. |
| `core/native_diagnostic_trace.ads:40` `Appended` | Exact old prefix plus complete new text; equality and indexed access must remain valid for the whole old lifetime. |
| `core/native_diagnostic_trace.ads:48` `Empty` | Empty sequence means no lines, preserving empty-string positions. |
| `core/native_diagnostic_trace.ads:56` `Push` | Literal enabled full-value `'Old` construction, independent copy semantics, cleanup on normal and postcheck-exception exits, checked runtime cost. |
| `core/native_diagnostic_trace.ads:68` `Take_All` | Literal full-value equality to entry sequence through destructive reversal; by-reference handoff; inaccessible implicit snapshot retirement after postchecks. |
| `core/native_diagnostic_trace.ads:72` `Release` | Existing null-or-tail-null precondition and null postcondition; explicit native node release does not retire old model snapshots. |
| `core/native_diagnostic_trace.ads:79` `Stack_Contents` | Complete chronological snapshot, independent from mutable link graph; same value-lifetime/cost issue. |
| `core/native_diagnostic_trace.ads:101` `Split_Contents` | Complete prefix/suffix conservation across native reversal, all text and positions; model snapshot lifetime plus repeated checked evaluation cost. |
| `core/native_diagnostic_trace.adb:21,41,43,83,105` named ghost snapshots | Safe independent normal and exceptional lifetimes, actual allocation/copy/retirement cost, retained full-content conservation invariants. |
| `core/worldline-c_api.adb:207` `Flush_Native_Diagnostic_Trace` | Native normal/exception cleanup owns transferred nodes, not implicit `'Old` objects; generated postcheck failures cannot be repaired by introducing a hidden caller lifetime protocol. |
| `core/evaluation_completion_c.adb:43` and `core/worldline-c_api.adb:191` producers | Full original diagnostic content and primary-result preservation; no dropping captured output to avoid the model cost. |

PROVED obligations are not yet claimed for this source in this analysis. A source declaration in SPARK is not evidence that its imported implementation or retirement has been proved.

## Toolchain and matching support

MEASURED version commands retained in `evidence/probe-run-20261013T174100Z/*-version.stdout` report GNAT 16.1.0, GNATprove FSF 16.1.0, Why3 1.8.2+git, and GPRBUILD 26.0.0. Command and source identities are retained in that run's `results.json`.

MEASURED source identities: `evidence/inspected-source-identities.json` pins the installed and product files inspected. Installed `Infinite_Sequences` has a `SPARK_Mode (Off)` private part and body, uses `Functional.Base`, and converts mathematical indices to `Count_Type`. `Functional.Base` implements automatic reference-counted `Controlled` finalization; this supports an actual runtime implementation, but it does not supply a proof of the excluded representation/finalization body or remove the cumulative representability bound. Setting a visible SPARK aspect or proving callers does not close that boundary. The installed `System.Pool_Local` does implement automatic reclaim at pool finalization; this is a distinct type/pool-scope mechanism, not per-value last-copy retirement for an existing library-level snapshot type. Using it as a substitute would require an additional scope/non-escape protocol and matching proof. The inspected global default pool explicitly states no automatic reclaim.

## Historical attempts and donor branches

The original M4 source is preserved byte-for-byte under `cases/m4`; historical stderr, report, detailed design, and consultation are retained under `historical/`, with origins and hashes in `evidence/historical-inputs.json`. The historical M4 result is exactly `Items is not writable` in `Content`, caused by conversion of an input owner to a named readonly view; its report says flow/proof were skipped because of ownership errors. This is not an executed implicit-`'Old` cleanup failure and not a general infeasibility proof.

`evidence/donor-review.json` records exact heads, logs, and patches for `origin/archive/phase1-donors-20261012/{flow-c,flow-d,replay-derive,roster-custody}`. None changes `native_diagnostic_trace.ads` or `.adb` relative to the frozen source. Their flow/recovery/roster work therefore supplies no missing automatic model-retirement implementation. Broad donor replacement would also discard unrelated frozen-source evolution and is not selected.

## Minimal discriminators and options

The exact reproducible driver is `scratch/old-analysis/probe_driver.py`; every case uses a private scratch object directory, checked assertions, all-unit analysis, configured level 3, explicit solver memory and time bounds, and complete retained stdout/stderr/report. Execute only through the coordinator-approved shared lock/resource scope runner. Reviewer copies the sources to its own scratch before independent reproduction.

| Option / case | What it discriminates | Claim boundary |
|---|---|---|
| Original retained `m4` | Named immutable root conversion versus SPARK owner permissions | Reproducing this rejects the constructor only. |
| `controlled` | Native Ada finalization hook versus installed SPARK support | Compile acceptance alone is not SPARK support or proof of retirement. |
| `limited_old` | Limited explicit owner versus literal `'Old` legality | A limited owner cannot silently replace ordinary nonlimited value semantics. |
| `observer_old` | Anonymous borrowed result under `'Old` | A scoped observer is not an independent past value. |
| `fresh_old` | Fresh complete String allocation returned to implicit `'Old` | Complete-value construction does not automatically retire its owned allocation. |
| `explicit_prestate` | Named full-String capture, equality assertion, explicit `Destroy` | Positive control for a different explicit protocol; it does not prove automatic old retirement or the full queue/cost/exception claim. |

Ghost snapshots preserve specification structure only when their implementation also supports the required lifetime. A fresh ghost clone still needs retirement. Explicit prestates can make the owner accessible for cleanup, but change the original literal `'Old`/ordinary-copy contract and require all normal/exception callers to obey a new protocol. Restated postconditions using a scalar counter/hash lose full content; inline full arrays impose a cumulative representability obligation; neither is an equivalent solution. A complete explicit full-queue protocol would need independent proof and execution of capture, clone, equality, full reversal, cleanup, and exceptional paths before even a narrowed claim could be selected.

## Decision and Step 3 dependency map

Recommendation after TESTED candidate exclusions and the reviewer's independent reproductions: retain the original gate FAILED-OPEN. Do not select a production restatement merely because the small explicit-prestate positive control proves. No production implementation or contract changes are proposed by this analysis, and no NARROWED CLAIM is selected. D5 records the coordinator decision and actual GPT-6.1 internal verdict; this is not independent acceptance.

The `Native_Diagnostic_Trace` model, full checked native diagnostic execution, generated postcheck-exception cleanup, and same-source final full build/proof/runtime depend on this unresolved facility. Conservation, lifecycle, recovery, and evidence-join authority bodies may be inspected, proved, and exercised independently where their command does not require claiming full diagnostic-model lifetime closure. Integrated acceptance cannot exclude diagnostic snapshots or treat those independent results as closing this gate. Existing ordinary scalar/inline-array `'Old` contracts in authority packages are not blocked merely by the presence of the attribute.

Reversal of the proposed decision: retain all failed evidence, identify a concrete supported full-value representation with matching automatic lifetime semantics, add its implementation and preservation tests without changing the target, and rerun fresh full-source gates plus independent review. Deleting scratch experiments is not required or proposed.

## Documentation corroboration and version boundary

The primary [SPARK RM assignment/finalization rule](https://docs.adacore.com/spark2014-docs/html/lrm/packages.html#assignment-and-finalization) prohibits controlled types in SPARK. The [access-type rules](https://docs.adacore.com/spark2014-docs/html/lrm/declarations-and-types.html#access-types) distinguish borrowed `'Old` prefixes from non-traversal fresh function results, and retain reclamation obligations for enabled assertion allocations. These live pages identify release **28.0w**; they corroborate the mechanism classification but do not replace the actual GNATprove **16.1.0** experiments. Attempts to retrieve the Ada 2022 postcondition page from adaic.org and ada-auth.org did not produce usable content in this run; the corresponding scope/exception discussion above is retained historical analysis until independently supported by fresh toolchain evidence.


## Initial live experiments

Exact outer command:

```sh
python3 -B scripts/phase1_heavy.py --out scratch/old-analysis/probe-scope-20261013T174100Z --timeout 15m -- bash -c 'source /home/sicarii/opt/gnat/env.sh; python3 -B scratch/old-analysis/probe_driver.py scratch/old-analysis/evidence/probe-run-20261013T174100Z'
```

The output directory is an identifier; actual UTC timestamps are recorded inside the launch/admission/result files. Commit: `a1bda52b53a9a220b2333fe09a135e2d94127dbc`. MEASURED admission read `MemAvailable: 25825092 kB` after flock acquisition. The scope recorded `memory.max=8589934592`, `memory.swap.max=0`, and an inactive, unpopulated terminal state. RUSAGE_CHILDREN reported `ru_maxrss_kib=92716`; this is maximum child RSS, not aggregate RSS or proof of a memory bound. All inner exact build/proof commands are in `evidence/probe-run-20261013T174100Z/results.json`.

| Case | Class and actual outcome | What this establishes |
|---|---|---|
| `m4` | TESTED: build exit 0; proof exit 1. `Items is not writable` at `diagnostic_immutable_observation.adb:15:55`; report explicitly skips flow/proof for ownership error. | Reproduction of the original failing named-view constructor. Not general infeasibility and not executed old cleanup. |
| `controlled` | TESTED: build exit 4; proof exit 1. E0003 early-call/freezing rule suggests `Elaborate_Body`. | Initial case stops too early to establish controlled finalization support; corrected follow-up required. |
| `limited_old` | TESTED: build exit 4; proof exit 1. `attribute "Old" cannot apply to limited objects`. | This limited-value route cannot preserve the literal attribute. |
| `observer_old` | TESTED: build exit 4 with GNAT BUG DETECTED / `Storage_Error stack overflow or erroneous memory access`; proof exit 1 with traversal-function `'Old` rejection under SPARK RM 3.10(13). | Concrete compiler failure is retained separately from supported checker rejection. No runtime test or cleanup proof ran. |
| `fresh_old` | TESTED: build exit 4; proof exit 1. Potentially unevaluated attribute prefix restriction in the second conjunct. | Initial case stops too early to test automatic retirement; unconditional legal form required. |
| `explicit_prestate` | PROVED, scoped to analyzed obligations: build and proof exit 0; report total 11, justified `.`, unproved `.`. | Complete String capture/assertion and explicit null-after cleanup contract prove in this small program. The report explicitly skips the instantiated deallocator body as SPARK_Mode Off; this is neither automatic `'Old` retirement nor full queue/exception/cost proof. |

Every failure's complete stdout/stderr is retained beneath its case directory; positive scoped proof has its complete `gnatprove.out`. Successful driver exit means the experiment recorder completed, not that the deliberately failing cases passed.

The precise independent/dependent Step 3 source, current production-call, required project, and existing-control map is in `docs/phase1-authority-obligations.md`. That map is static observed correspondence only; no production authority execution was performed by this subtask.


## Corrected independent reviewer experiments

Actual GPT-6.1 internal reviewer `/root/reviewer` independently copied the original cases, confirmed their failures, then repaired the cases whose initial errors occurred before the intended discriminator. Its retained internal prose verdict is located at `scratch/reviewer/old-review-v2.md`; exact source hashes, command arguments, working directories, exit codes and tool versions are retained in `scratch/reviewer/old-independent-results-v2/results.json` and the files beside it. These are internal review records, never independent acceptance.

Exact reviewer outer command:

```sh
python3 scripts/phase1_heavy.py --out scratch/reviewer/old-independent-scope-v2 --timeout 10m -- bash -c 'source /home/sicarii/opt/gnat/env.sh && python3 scratch/reviewer/probe_driver.py scratch/reviewer/old-independent-results-v2'
```

Source commit: `a1bda52b53a9a220b2333fe09a135e2d94127dbc`; actual result timestamp: `2026-10-13T17:13:28.289113+00:00`. The admitted scope, cgroup cap and terminal state are in `scratch/reviewer/old-independent-scope-v2/`. The build command is `gprbuild -p -P <case>/probe.gpr -c -U -j1`; strict proof is `gnatprove -P <case>/probe.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on -j1 --memlimit=1024 --timeout=30`. The manifest supplies each absolute `<case>` path.

| Corrected case | Class and actual outcome | Supported conclusion |
|---|---|---|
| `controlled_legal` | TESTED: adding `Elaborate_Body` makes build exit 0; strict proof exits 1. `proof.stderr` explicitly rejects `Ada.Finalization.Controlled`, `Snapshot` and `Item` as not allowed in SPARK due to controlled types. | The language's automatic controlled-finalization hook cannot be used directly inside this SPARK proof boundary on the installed toolchain. The earlier E0003 is retained as an earlier, separate failure. |
| `fresh_old_legal` | TESTED: unconditional `Post => Capture (Text)'Old.all = Text` builds with exit 0; strict proof exits 1. `proof.stderr` proves the full-value postcondition and dereference, but reports `resource or memory leak might occur` because an allocating call inside an assertion leaks. `gnatprove.out` lists one unproved check. | A legal fresh owning full-value snapshot can prove equality while failing the retirement obligation. Proved value equality is not evidence of automatic cleanup. The earlier potentially-unevaluated-prefix error is retained separately. |

The independent review authorizes these precise mechanism exclusions only. It does not authorize an O1 PASSED claim, universal target infeasibility, or treating manual named-prestate cleanup as automatic compiler-generated `'Old` cleanup. The final analysis therefore does not propose changing an original production contract or claiming a narrower accepted Phase 1 target.


## Resumed strict Finalizable investigation (D43, D44, D47)

These are new finite discriminators, not replacements for any earlier failure. Every new path below is relative to the owned repository root. Original O1 remains FAILED-OPEN with no restatement or NARROWED CLAIM. The previous inspected-mechanism verdict is not a universal impossibility theorem.

Primary GNAT Reference Manual revision `28.0w`, section 18.2.11, documents root-record `Finalizable` with Initialize/Adjust/Finalize hooks. Its default relaxed setting omits some heap/exception guarantees, so every candidate explicitly uses `Relaxed_Finalization => False`. The SPARK Pro 27 roadmap describes planned support; it is not installed-support evidence. Actual compiler/GNATprove paths, hashes and version outputs are retained by each probe. No global toolchain installation or replacement occurred.

| Candidate | Actual source/command/output | Finite result and open obligation |
|---|---|---|
| D43 strict scalar | `python3 -B records/phase1-blockers/resume-20261015-v1/run_finalizable_scalar.py`; source `finalizable-scalar-v1`, results under that directory and its sibling parent/scope directories | TESTED build/runtime `0`; PROVED report says all `12` checks proved and both units/explicit null hook bodies analyzed. Compiler unused-parameter and flow not-modified warnings remain. Null hooks do not establish modeled implicit effects, heap reclamation or full-value independence. |
| D44 heap v1 | `run_finalizable_heap.py`; source/results `finalizable-heap-v1`, exact parent/scope receipts | TESTED build `4`, proof `1`, runtime NOT PERFORMED. RM 6.1.1(27) rejects potentially unevaluated First/Last Old prefixes in Adjust's short-circuit contract. This syntax defect was corrected only in fresh v2; v1 bytes remain unchanged. |
| D44 heap v2 | `run_finalizable_heap_v2.py`; source/results `finalizable-heap-v2`, exact parent/scope receipts | TESTED build/runtime `0`, proof `1`: owning-variable `Object'Old` rejected for aliasing under SPARK RM 3.10(13). No independent assignment proof completed, even though the runtime control passed. This is not a rejection of every fresh function-result prefix. |
| D47 fresh full value | `run_finalizable_fresh.py`; source/results `finalizable-fresh-v1`, exact parent/scope receipts | TESTED build/runtime `0`, complete proof `1`. Report total `23`, unproved `6`, justified `.`: reclamation remains unproved for overwritten Adjust owner, all three `Capture(Text)'Old` allocations and two Main scope owners. Content/bounds assertions proved as listed, while standard instantiated deallocator body remains explicitly SPARK_Mode Off. Runtime success is not measured leak freedom. |

All commands above resolve inside `records/phase1-blockers/resume-20261015-v1/`. Each parent binds its actual base commit, exact dirty-source diff, nonsecret environment, tool/version/command/output hashes and UTC bounds; tracked identities remained unchanged during each execution. Their own actual systemd scope retained the unchanged 8G/swap0 cap, post-lock memory admission and terminal cleanup. D43 originally ran at documentary base b6a7143; resumed heap/fresh probes identify their actual 9522e89 base and separate source diffs rather than claiming clean frozen-source acceptance.

Actual GPT-6.1 internal reviews are `D43-finalizable-scalar-actual-review-v1.json`, `D44-heap-v2-actual-result-review-v1.json` and `D47-fresh-finalizable-actual-review-v1.json` under `scratch/reviewer2/resume-20261015-v1/`. They confirm the finite observations only. No unchanged retry, lifetime-weakening precondition, ignored assertion, Assume, hidden observer state, custom pool, application Controlled or new Off implementation was selected. The fresh-route caller deliberately uses separate constructors, so ordinary implicit `B := A` independence remains an additional open obligation. Physical retirement, allocation/exception failure behavior, negative controls, production queue/content/FIFO/duplicate semantics and native Push/Take_All costs remain unclosed.

A complete matching compiler/prover implementation has not been established by these results. Further work must identify a concrete supported representation or matching tool support that preserves the original conjunction; it cannot close O1 using proved content alone or a roadmap promise. Independent acceptance remains NOT PERFORMED.
