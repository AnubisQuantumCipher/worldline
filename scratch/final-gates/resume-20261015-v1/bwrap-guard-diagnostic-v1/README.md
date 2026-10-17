# D45 metadata-only bwrap guard diagnostic — prepared, not run

This method performs one read-only metadata payload inside the exact retained failed private-suite carrier prefix. It imports no production/test module and runs no private evaluator, test, service, compiler or proof. It reads its own proc identity/maps and public bwrap metadata/bytes only. Existing executable approval is unchanged.

`run_bwrap_guard_diagnostic.py`, `payload.py.txt` and `source-pins.json` must remain together. `preparation.json` records hashes. Only static `ast.parse` was performed. The method is not itself an acceptance harness; actual GPT-6.1 D45 review and the coordinator's recorded decision must precede launch.

The prefix is taken from the retained ef7 private-host launch through `/usr/bin/python3 -B`. Only the audit/unittest payload is replaced by `-c` and the pinned metadata text. Every explicit environment override in the original retained worker receipt is reused, including the old owned XDG paths, which this payload never writes. The original worker's bytecode/opt-in additions and GPR_TOOL/PYTHONSTARTUP removals are preserved. Its unretained historical ambient environment is unknown. Current inherited PATH is recorded so this diagnostic cannot be mistaken for historical reconstruction.

The payload sets `requested=None`, as the original ordinary `PrivateEvaluatorIntegration.run_examiner` did, so selection uses actual `shutil.which("bwrap")`. It records requested/selected/resolved path, full stat fields, real/effective UID/GID, user/mount namespace links, uid/gid maps, all original predicates, the exact original short-circuit expression value, and public tool SHA with descriptor-before/after identity. Reads/refusals remain explicit. A complete diagnostic returning zero does not mean the guard accepted: the result separately records `guard_would_refuse` and `failed_predicates`.

The script requires actual current baseline HEAD and current decision-log SHA with a D45 heading. It records dirty tracked paths instead of claiming HEAD alone identifies the current tree. The selected current/frozen guard bytes, original carrier, original launch/environment receipts and method are hash-pinned. No documentary freeze is required solely for this diagnostic. All outputs are exclusive-created under a fresh owned directory with owner-only permissions. The child query has a diagnostic-only 60s ceiling; its `subprocess.run` timeout terminates/waits only that owned child. There is no manager enumeration or foreign-process signal.

## Coordinator command after D45 review/log and existing storage preflight

Use the existing shared-lock/post-lock admission/8G/swap0 wrapper, with a fresh output path. The administrative deadline is not an acquisition/private-test deadline change:

```sh
D45_HEAD=$(git rev-parse HEAD)
D45_LOG_SHA=$(sha256sum docs/decisions.md | cut -d ' ' -f 1)
python3 -B scripts/phase1_heavy.py \
  --out records/phase1-blockers/resume-20261015-v1/bwrap-guard-scope-v1 \
  --timeout 2m --swap-max 0 -- \
  python3 -B scratch/final-gates/resume-20261015-v1/bwrap-guard-diagnostic-v1/run_bwrap_guard_diagnostic.py \
    --expected-head "$D45_HEAD" --decisions-sha256 "$D45_LOG_SHA" \
    --out records/phase1-blockers/resume-20261015-v1/bwrap-guard-observation-v1
```

Keep the existing parent storage reserve/preflight and owned-output containment. This command is a proposal only; it was not executed. The method creates `launch.json`, raw `stdout`/`stderr`, and `result.json`; the existing heavy wrapper retains scope/admission/resource evidence. Timeout, missing fields, changed input identity, or parse failures are incomplete observations, never passes. Reuse of output directories refuses.

## Proposed D45 decision text

Options: infer root cause from generic private-suite errors or outside-carrier metadata; weaken bwrap approval; rerun the full private module; or measure only the exact guard operands inside its original carrier. Select the finite operand measurement. Retained ef7 private audit lacks stat/UID-map at refusal; namespace-v2/fullsandbox-v5 have their own mappings but neither this failed-carrier stat nor its exact recipe. Thus ownership translation is currently a hypothesis, not an established cause.

Choice: one metadata-only child with the original retained carrier prefix/environment recipe, exact guard expression, fixed source/method hashes, explicit current-versus-historical limits, unchanged executable approval and existing resource containment. Reviewer verdict: **PENDING actual GPT-6.1 review**. This method cannot approve itself.

Reversal: do not launch before valid decision/review. After launch, preserve every receipt, including refusal/incomplete output; stop using the diagnostic rather than modifying guards or repeating a failed suite for green evidence. No product/configuration mutation exists to undo. Any ensuing carrier or product repair requires its own reviewed, logged decision and original verification.
