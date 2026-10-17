# Phase 1 acceptance contract

Status: BINDING after actual GPT-6.1 internal review; original approved gate-text digest and verdict are recorded in docs/decisions.md D2. Base: `a1bda52b53a9a220b2333fe09a135e2d94127dbc`.
The review binds the gates below; later revisions may add requirements, never remove or weaken them.
Phase 1 stays OPEN during this run. Independent acceptance is always NOT PERFORMED here.

## Provenance and interpretation

Derived from the user's four blockers, `AGENTS.md`, the seven original requirements in
`docs/phase1-checkpoint-2026-10-02.md#closure-queue`, all subsequent native checkpoint
remaining-work clauses, `scripts/assurance_contract.py::REQUIRED_STEPS`, `prove.sh`, and
`verify_proof_manifest.py` coverage/floors/contract pins. Historical source checkpoints
are not current-source passes. Full historical campaign rosters and strict floors remain
required even when not tracked in this source checkout.

Each evidence record must contain: claim class (PROVED, MEASURED, TESTED, ASSUMED or
UNVERIFIED), full source commit, source diff or clean identity, exact argv/cwd/environment
(nonsecret settings), UTC times, tool versions, exit/signal status, retained output paths
and SHA256 hashes. Required missing fields, unreadable files, absent outcomes, unknown
results, unexpected skips and zero-work runs reject a pass. Preserve failed attempts.
A hash binds bytes but does not independently authenticate them. Internal review never
substitutes for independent acceptance.

The machine conditions are conjunctive. A gate is PASSED only if every predicate holds;
otherwise FAILED-OPEN if attempted and failed, or NOT PERFORMED if no qualifying attempt.
Commands run through `scripts/phase1_heavy.py --out <unique-dir> --timeout <deadline> -- ...`
when heavy, preserving original deadlines where specified. Each launch uses the shared
lock, post-lock memory admission and own bounded systemd scope; stdout/stderr are files.

## Gate roster

| ID | Required gate | Machine-checkable pass condition |
|---|---|---|
| G0 | Binding acceptance definition | Actual GPT-6.1 review artifact names this file's SHA256, affirms coverage of all four blockers and original seven authority areas, and contains `verdict: APPROVE`. Every engineering decision has options, evidence, choice, reviewer verdict and reversal in `docs/decisions.md`. |
| A0 | Original acquisition failure reproduction | Retain original exact command, source, roster, cap and diagnostic receipts. Reexecute the original failing diagnostic at unchanged `MemoryMax=8G` and original swap setting; nonzero termination plus cgroup `oom_kill` increase or matching kernel MEMCG kill record identifies this reproduction's cause. Full-campaign timeout is separately classified and never inferred from the diagnostic kill. |
| A1 | Bounded evidence processing | Stage-labelled peak RSS measurements cover source acquisition, owned-copy construction, canonical encoding/witness, producer/consumer processing and retention. Regression asserts an explicit memory bound under the cap, byte-for-byte canonical compatibility, original accepted value domain and fault semantics. Run original positive/negative serializer and interruption controls unchanged; all required cases execute with zero unexpected failure/skip. |
| A2 | Complete acquisition campaign | Original complete acquisition roster executes on repaired source under unchanged `8G`, exits successfully before original deadline, and retains every required case outcome, artifact and join. Terminal summary is complete, all required cases passed, scope has no OOM kill, recorded `memory.peak` is within `memory.max`. Full stdout/stderr, case artifacts, ownership/wait/cleanup evidence and stage measurements exist and hash-verify. |
| O0 | Exact retirement obligation inventory | Machine-readable inventory contains every affected owning/full-value contract and each required normal/exceptional/scope-exit/'Old-copy obligation; source references resolve and installed GNAT/GNATprove versions are recorded. Inventory distinguishes ordinary scalar 'Old, ghost mathematical snapshots, manual release and automatic retirement. All donor refs `origin/archive/phase1-donors-20261012/*` have immutable SHA and comparison records. |
| O1 | Automatic full-value/'Old retirement | Preserve the original conjunction: no new cumulative bound; nonlimited independent full values; implicit compiler-created 'Old automatic retirement including exceptional postchecks; no application Controlled, SPARK-Off or custom-pool boundary. Smallest positive and negative reproducers build/run/prove at configured level on installed tools, and production owning values automatically retire on required normal/exceptional exits including compiler-created 'Old snapshots. Full relevant bodies/callers discharge proof with zero unproved/justified/Assume, and executable retention/leak controls pass. Manual explicit Clear/Free alone fails this gate. Unsupported paths remain open. |
| O2 | Step 2 decision integrity | `docs/old-retirement-analysis.md` states exact original claim, inventory, tool identities, options, minimal reproducers, dependencies and one required verdict. If restatement is chosen, separate reviewer run independently reproduces the claimed infeasibility, exact strongest restatement and all exclusions appear under NARROWED CLAIMS. Restatement does not mark O1 PASSED; its original obligation remains FAILED-OPEN. No unsupported impossibility claim is accepted from timeout alone. |
| C1 | Conservation authority | Complete configured proof covers reservation Reserve/Consume/Release, accounting, containment, epochs and all faithful callers without weakening original contracts/floors. Production execution logs observe Python calling the source-bound SPARK decision kernel with independently sourced inputs, positive/negative/OOM/pressure/recovery controls and joins; all original expected outcomes match. |
| C2 | Lifecycle authority | Complete configured proof covers evaluation, completion, pending, finalization, explicit absence, malformed/missing/mixed domains, decoder/layout/export/classification, bodies/callers/termination. Production original ordinary/ownership/fault/interruption/storage/descendant-held-pipe controls and positive acceptance cases pass through the actual source-bound kernel; all required outcomes and cleanup witnesses retained. |
| C3 | Recovery authority | Complete configured proof covers world/check/transaction recovery, one-shot witnesses, transitions/callers, receipt causal chains, capability attenuation and requester/owner rights. Original K4 positives/mutants and K5 power-loss/SIGKILL/storage/corruption/stale/restart/rollback/concurrency matrix executes through production kernel with expected results and retained authenticated joins. |
| C4 | Evidence joins authority | Complete configured proof covers policy-wide required rosters, one effective evaluation, history/selector/roster/report, raw acquisition/layout, native artifacts, full collapse/mutation domain and all callers. Source-list guards and authentic independent confinement/provenance/protected-custody producer controls pass; actual source-bound kernel rejects missing/mixed/stale/forged joins and accepts original valid private cases. |
| F0 | Frozen source and tool identity | Full commit, tree and source inventory before/after all final runs match; tracked implementation is clean throughout. Rebuilt native/shared libraries, proof projects, tools/solvers, installed dependency sources and runtime module paths are hashed and joined to that commit. Reports may be committed later but identify the immutable tested source separately. |
| F1 | Full build | Fresh `gprbuild -p -P worldline.gpr` and every original required auxiliary/native/pending/protected build exit zero, complete expected artifact roster exists, exact command and artifact hashes retained. Build scope is not reduced to one library or component. |
| F2 | Complete strict proof | Run all required project/source scopes with `-U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on`, explicit per-solver timeout/memory and bounded concurrency. All original proof floors and per-subprogram/body/caller/flow/runtime-error/termination/native-cost obligations remain. Every required report exists, parses without unknowns, proves required coverage, has zero unproved, zero justified and zero `pragma Assume`; no new exclusions/imported assumptions/SPARK-Off boundary. `verify_proof_manifest.py` validates current summary, sources, contracts, coverage and library. |
| F3 | Complete runtime and assurance | All `REQUIRED_STEPS` from the existing assurance contract are retained; original full unittest discovery plus additions, Ada behavior/fuzz, private host cases and pinned two-arm evaluation-domain controls complete at frozen source. No missing expected cases, unexpected skips, FAIL/ERROR, unknown outcome or forged PASS; counterexample arm observes its pinned defect. Result manifests contain actual outcomes, never inferred pass counts. |
| F4 | Authentic protected execution | Original protected root/resource/startup/canonical/lifetime/custody/ownership/reclamation controls execute with actual required principals and host mechanisms. Required identities, positive and negative cases, command exits, retained authentic receipts and source joins all verify. Emulated protected runs or missing authorization are NOT PERFORMED, not PASSED. Cosmogony changes are forbidden and recorded in OPEN-ISSUES.md. |
| F5 | Authentic actor execution | Existing Codex actor adapter executes actual GPT-6 Luna only inside WORLDLINE world/child-world tests using `-m gpt-6-luna -c model_reasoning_effort=high`. Preserve original deterministic fixtures as separate controls. Actor identity, invocation, completion, custody/provenance, kernel decisions and required world/child-world outcomes verify at frozen source. A fixture substitution cannot pass this gate. |
| F6 | Honest manifests and acceptance report | Proof and assurance manifests regenerate from actual successful runs or explicitly record refusal/failure; never fabricate a success manifest. `docs/phase1-acceptance-report.md` covers each roster ID exactly once with status, claim class, source, command and output references plus NARROWED CLAIMS and open obligations. All hashes and joins verify; no gate omission. |
| F7 | Independent acceptance | An independently commissioned acceptance verdict over the frozen source and all gates is required for acceptance. This run must report NOT PERFORMED. Internal reviewer approval cannot satisfy F7 and the coordinator cannot declare Phase 1 accepted. |

## Dependency and failure rules

C1–C4 investigation, inventory and proof of unaffected units may proceed immediately.
Changes relying on automatic retirement or alternate pre-state representation wait for O2.
F0–F6 require integrated same-source evidence even if earlier focused runs passed.
Two serious attempts with the same unresolved failure trigger a precise FAILED-OPEN record
and work moves to the next independent item; retain both attempts. Gates and accepted cases
cannot be removed to turn a failure green. Out-of-scope work goes to OPEN-ISSUES.md.
