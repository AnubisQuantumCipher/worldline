# Freeze-v5 gate launch commands

Preparation only; no job below was launched by this helper. Coordinator only. Use the actual clean committed HEAD captured by freeze-v5, with all final jobs on that identity. A later report commit names that tested SHA; do not create another documentary freeze merely to publish the report. No source537 pass transfers.

Before freeze: all owned prior jobs settled; required decisions recorded; actual GPT-6.1 concurrence and installed exact helper hashes checked. Binary v5, sandbox v3 and domain v2 are the reviewed original successors. Inventory v4 requires its pending review. Every output below is fresh; preserve previous attempts. No new diagnostic, qualifier, fixture or case is introduced.

Before each heavy job, retain D32 storage preflight and observe disk use periodically. Keep configured reserve10000000000 bytes; existing trigger20000000000 is informational headroom, not a proven write bound. Use only already-reviewed exact-owned cancellation and cleanup on resource refusal. After completion, archive eligible inactive outputs only through individually verified DUAT recovery, preserving active source/frame/build/tool/dependency inputs.

Existing wrappers hold the shared flock, check MemAvailable after acquiring it, release/retry300s when admission fails, and run the worker at8G/swap0. Direct runtime/domain/actor supervisors own the flock: never wrap them in another heavy launcher. Watcher query10s is unchanged. D36's successful one-shot manager query does not identify prior latency cause or approve a changed deadline. ONE acquisition diagnostic remains consumed/interrupted, classification UNVERIFIED and original1000s gate unchanged.

Run each block only after its prerequisites hold; inspect actual termination/cleanup and obtain required actual-result review before dependent jobs. A failed gate does not stop independent original work. No blind all-green assumption or duplicate completed green run.

## Freeze and variables

```bash
cd /home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z
source /home/sicarii/opt/gnat/env.sh
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
export WORLDLINE_BUILD=checks
python3 -B scratch/coordinator/freeze_v5.py
```

After the actual freeze succeeds:

```bash
phase1_root=$PWD
phase1_freeze=$phase1_root/records/phase1-blockers/freeze-v5/source.json
phase1_commit=$(python3 -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' "$phase1_freeze")
test "$(git rev-parse HEAD)" = "$phase1_commit"
test -z "$(git status --porcelain --untracked-files=no)"
phase1_frame=$phase1_root/scratch/coordinator/final-frame-v5/source
phase1_build=$phase1_root/records/phase1-blockers/final-build-steps-v5/artifacts.json
phase1_aux=$phase1_root/records/phase1-blockers/original-aux-builds-final-v6/result.json
phase1_dependency=$phase1_root/scratch/old-analysis/evidence/private-sparklib-proof-source-v1.json
phase1_template=$phase1_root/scratch/old-analysis/private-sparklib-proof
phase1_inputs=(--expected-commit "$phase1_commit" --freeze-record "$phase1_freeze" --frame "$phase1_frame" --build-manifest "$phase1_build")
phase1_binary_inputs=(--expected-commit "$phase1_commit" --freeze "$phase1_freeze" --frame "$phase1_frame" --aux-manifest "$phase1_aux" --full-build-manifest "$phase1_build")
```

## Original build and artifact prerequisites

Main45m then auxiliary45m, worker8G/swap0; all original recipes, retained-output moves, checked ALI/dependency/source joins, Ada behavior/fuzz predicates remain unchanged. Main subset alone does not close F1 selected protected artifact/helper gaps.

```bash
python3 -B scripts/phase1_heavy.py \
  --out records/phase1-blockers/final-build-scope-v5 --timeout 45m --swap-max 0 -- \
  python3 -B scratch/coordinator/final_build_v5.py
```

```bash
python3 -B scripts/phase1_heavy.py \
  --out records/phase1-blockers/original-aux-builds-scope-v6 --timeout 45m --swap-max 0 -- \
  python3 -B scratch/coordinator/original_aux_builds_v6.py
```

After both complete, before proof creates frame obj, use only the existing verified-link helper (nonheavy, under flock). It refuses unexpected directories/symlinks.

```bash
flock /home/sicarii/.worldline-heavy.lock python3 -B - \
  "$phase1_commit" "$phase1_freeze" "$phase1_frame" "$phase1_build" <<'READBACK'
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'scratch/old-analysis'))
from frozen_source_v2 import validate
receipt=validate(sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]),link=True)
with (Path.cwd()/'scratch/old-analysis/final-frame-v5-link-preflight.json').open('x') as stream:
    json.dump(receipt,stream,sort_keys=True,indent=2)
    stream.write('\n')
READBACK
```

## One required final strict proof and terminal readback

Preserve both prior120m failures as FAILED-OPEN. This is the one required run on the actual new frozen identity, not another unproved-fix loop. Carrier120m/8G/swap0; solver timeout60/memlimit1024/jobs2; full original aggregate level3/all/reportall/errors/proofwarnings and scenario values unchanged.

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/old-analysis/full-proof-scope-v5 --timeout 120m --swap-max 0 -- \
  python3 -B scratch/old-analysis/full_proof_driver_v2.py \
  --out scratch/old-analysis/full-proof-result-v5 --subdir phase1-full-proof-v5 \
  "${phase1_inputs[@]}" --dependency-template "$phase1_template" \
  --dependency-manifest "$phase1_dependency"
```

After actual terminal scope settlement, whether proof succeeded or failed:

```bash
python3 -B scratch/old-analysis/final_proof_gate_v2.py \
  --out scratch/old-analysis/final-proof-gate-v5 \
  --proof-run scratch/old-analysis/full-proof-result-v5 \
  --proof-scope scratch/old-analysis/full-proof-scope-v5 \
  "${phase1_inputs[@]}" --dependency-manifest "$phase1_dependency" \
  --private-dependency scratch/old-analysis/full-proof-result-v5/private-sparklib
```

Require all original source/contract/export pins, floors, body/caller/flow/termination coverage and zero unproved/justified/Assume. Missing reports/counts remain unknown/null. Only fully PASSED strict readback emits a candidate manifest; no pin relaxation or fabricated positive manifest.

## Original binaries and direct additions

Collect current artifacts10m/8G/swap0. Require complete original roster and current source/library/ALI/dependency joins; collection is not execution.

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/acquisition/original-binary-artifacts-scope-v5 --timeout 10m --swap-max 0 -- \
  python3 -B scratch/acquisition/original_binary_controls_v5.py --collect \
  "${phase1_binary_inputs[@]}" --out scratch/acquisition/original-binary-artifacts-v5
```

Existing full normal/timeout/detached/namespace qualifier5m/8G/swap0. D33 marker-only positive diagnostic does not replace this qualifier or original syscall fixture. Require actual complete result and GPT-6.1 cleanup/namespace review before dependent payloads.

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/acquisition/original-binary-sandbox-scope-v5 --timeout 5m --swap-max 0 -- \
  python3 -B scratch/acquisition/qualify_original_binary_sandbox_v3.py \
  --out scratch/acquisition/original-binary-sandbox-v5 --frame "$phase1_frame"
```

Original binary roster120m outer/8G/swap0; ordinary no-inner-deadline behavior and original180s additions unchanged. Require actual complete artifact and qualifier results first.

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/acquisition/original-binary-controls-scope-v5 --timeout 120m --swap-max 0 -- \
  python3 -B scratch/acquisition/original_binary_controls_v5.py --run \
  "${phase1_binary_inputs[@]}" \
  --artifact-manifest scratch/acquisition/original-binary-artifacts-v5/artifacts.json \
  --out scratch/acquisition/original-binary-controls-v5
```

Existing original direct freshness-json-object-order and execution-evidence-boundary additions, unchanged two-row order,180s each, assertions/markers/parsers/TEST_ONLY limitations; outer120m/8G/swap0. Exact deployed helper pins and matching full qualifier required.

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/acquisition2/original-additional-scope-v5 --timeout 120m --swap-max 0 -- \
  python3 -B scratch/acquisition2/original_additional_driver_v2.py \
  --out scratch/acquisition2/original-additional-v5 \
  --sandbox-qualification scratch/acquisition/original-binary-sandbox-v5/result.json
```

## Original runtime and domain

Run the unchanged paired real-supervision qualification once on v3/final source15m/8G/swap0. Require actual parser parity, zero unexpected skips, both typed-manager forms, exact source/helper/library and owned cleanup, then actual-result review. Domain v2 strictly joins this same v3 identity; do not duplicate qualification.

```bash
python3 -B scratch/old-analysis/full_runtime_supervisor_v3.py \
  --out scratch/old-analysis/runtime-qualification-v5 --suite qualification --scope-timeout 15m \
  "${phase1_inputs[@]}"
```

After qualification succeeds, original full discovery followed by original separate private-host discovery,120m/8G/swap0. Original complete roster/parsers/audit/zero-unexpected-skip/cleanup predicates remain. Partial output or missing worker summary cannot pass.

```bash
python3 -B scratch/old-analysis/full_runtime_supervisor_v3.py \
  --out scratch/old-analysis/full-runtime-v5 --suite full --scope-timeout 120m \
  "${phase1_inputs[@]}"
```

**D35 conditional only:** run the following only after SAME final-source full-runtime-v5 actually terminates and all owned children settle, if its separately required private-host command did NOT complete. Old537 terminal failure is insufficient. Do not rerun a completed green or completed failed private result automatically. The private-only result explicitly does not execute/pass the full runtime roster. Preserve original parser/zero-skip/audit/exit predicates and120m/8G/swap0.

```bash
python3 -B scratch/old-analysis/full_runtime_supervisor_v3.py \
  --out scratch/old-analysis/private-host-runtime-v5 --suite private --scope-timeout 120m \
  "${phase1_inputs[@]}"
```

Original paired complete domain qualification120m/8G/swap0, original decisive900s/caller1800s. Preserve candidate plus pinned defect commit1bd5c0890e1c2686b3e33389831c76fe1f5cc25b/runtime tree1c628de542bfc843f5f5e1aaa0580a0c4b12c40e, marker/parity/exact launch/cleanup/source predicates.

```bash
python3 -B scratch/old-analysis/evaluation_domain_supervisor_v2.py \
  --out scratch/old-analysis/domain-qualification-v5 --mode qualify --scope-timeout 120m \
  "${phase1_inputs[@]}" \
  --runtime-qualification scratch/old-analysis/runtime-qualification-v5/result.json
```

Per reviewed D31 dual-use addendum, a fully successful same-source original plain/audit pair supplies actual original two-arm execution evidence. Cite that actual receipt/status; do not duplicate successful mode-gate or fabricate a separate receipt. Failed/missing arms leave the original gate open. D7 collector-equivalence and complete F3 remain separate.

## FFI qualification and production admission component

Each120s/8G/swap0 through existing rootRO/own-worktreeRW guard. Require actual reviewed same-source finite FFI controls before component execution; original `_CFuncPtr` arguments/returns/outbuffers and refusal/restoration checks unchanged.

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/old-analysis/authority-ffi-qualification-scope-v5 --timeout 120s --swap-max 0 -- \
  bwrap --die-with-parent --ro-bind / / --dev /dev --proc /proc \
  --bind "$phase1_root" "$phase1_root" --chdir "$phase1_root" \
  python3 -B scratch/old-analysis/authority_ffi_controls_v2.py \
  --out scratch/old-analysis/authority-ffi-qualification-v5 "${phase1_inputs[@]}"
```

```bash
python3 -B scripts/phase1_heavy.py \
  --out scratch/old-analysis/authority-admission-scope-v5 --timeout 120s --swap-max 0 -- \
  bwrap --die-with-parent --ro-bind / / --dev /dev --proc /proc \
  --bind "$phase1_root" "$phase1_root" --chdir "$phase1_root" \
  python3 -B scratch/old-analysis/authority_admission_driver_v4.py \
  --out scratch/old-analysis/authority-admission-v5 "${phase1_inputs[@]}" \
  --observe-ffi --ffi-qualification scratch/old-analysis/authority-ffi-qualification-v5/result.json --run
```

This supplies only actual ordinary prelaunch admission/report/refusal/release/repeat/reconcile dispatch evidence. Native instruction entry, workload Consume, lifecycle/recovery/authentic joins and complete C1-C4 proof remain separate obligations.

## Existing ordinary actor and final inventory

D34 exact pinned companion read-only projection only. Original model/prompt/mission/fixture/target and adapter unchanged. Requested actor is `-m gpt-6-luna -c model_reasoning_effort=high` inside WORLDLINE world. Actor600s/outer20m; worker8G/swap0, actor8G with original positive observed-page-sized swap (prior4096). Actual source/current library/credentials/principals and live service cap/cleanup required; credential bytes never printed.

```bash
python3 -B scratch/acquisition/actor_world_harness_v3.py \
  --out scratch/acquisition/actor-ordinary-final-v5 --expected-commit "$phase1_commit" \
  --library "$phase1_root/lib/libworldline_core.so" --timeout 600 --scope-timeout 20m --run
```

Original requested state outcome remains mandatory; exit0/PASS/SUPERVISED/VALID alone is insufficient. Provider identity, native dispatch/custody and authentic child-world outcome are not inferred from argv or ordinary success.

After path-only inventory v4 review/install, nonheavy original final-source inventory readback (GNAT environment still sourced):

```bash
python3 -B scratch/old-analysis/final_old_inventory_v4.py
```

Fresh output is `scratch/old-analysis/old-inventory-final-v4.json`. Preserve every original owning/copy/finalization/implicit-temporary/imported boundary/donor/tool identity row. Inventory success is not retirement proof; O1 stays FAILED-OPEN, no narrowed claim selected.

## Final report and manifests

Use actual completed strict proof readback. Successful candidate requires every original proof/manifest predicate; otherwise retain explicit failure/refusal with actual nullable counts. Original assurance REQUIRED_STEPS remain checkout-identity, clean-build-tree, build, ada-tests, ada-fuzz, python-tests, private-host-tests, evaluation-domain, proof-gate, proof-manifest. There is no existing receipt-assembly command that turns incomplete subsets into a positive assurance manifest.

Do not run destructive `prove.sh` or `scripts/assurance.py run` as formatting/readback or rerun old hardcoded refusal generators. Populate the existing proof/assurance refusal schemas from exact actual final receipts when required. Original predicate/schema details are retained in `scratch/final-gates/frozen537-publication-readback-v1.md`; bind paths/source to actual freeze-v5 results rather than copying historical claims.

All19 binding gates require exact command/source/output/hash and PASSED/FAILED-OPEN/NOT PERFORMED disposition, NARROWED CLAIMS none selected, and D4/D22 isolation breaches, D25 late instruction compliance, D26 storage exception, D29 interrupted diagnostic and D7 carrier gap. Later report commit names tested frozen source separately. Existing structural checker after complete report preparation:

```bash
python3 -B scratch/reviewer/check_final_gate_report.py \
  scratch/coordinator/phase1-final-report-v5/acceptance-report.json
```

That is a planned fresh report path, not an output created here. Actual GPT-6.1 semantic review must check the evidence. Authentic protected/child prerequisites remain scoped NOT PERFORMED when unavailable; do not infer universal absence, deploy new principals or modify Cosmogony. F1 protected selected-artifact joins and full C1-C4/F5 requirements are not closed by green subsets. Independent acceptance F7 stays NOT PERFORMED; do not declare Phase1 accepted.
