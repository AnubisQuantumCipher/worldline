# Final-pass self-check (V5-B01 first sentence): v6 working copy versus frozen v5

**Run.** 2026-10-04 23:37:20Z, by the lead. The harness is `finalpass_check.py` (sha256 `3ac71b5f…4995`). Raw outputs
are in `results-2026-10-04T233720Z/`:
- `v6.json`: `a35b44bc…`
- `v5.json`: `2cc7cef8…`
- both stderr files are empty.

**What was executed.** A library import of each frame's `observe_tree`, on throwaway trees in the job scratch
directory.
- No gprbuild, gnatprove or systemd-run was launched, and the shared window was never touched.
- The operator's scratch-frame decision (`claude-lead-v2/approvals/scratch-frame-decision-v1`) forbids any
  prover/compiler launch on WORLDLINE code outside a reviewed, adopted frame. This check launches neither.

**Method.** Each case builds a tree with:
- a recorded file, `a/ok.adb`;
- an excluded generated file inside an output partition, `obj/g.ali`;
- a late-walked directory, `0late`.

A hook on `os.listdir` fires once, while a directory walked after the target file is being listed. It mutates the
already observed file by one of: append, chmod, replace, mtime change, same-size rewrite, or delete. Every mutation
case must be refused. The two controls (no mutation) must be accepted.

## Result

| Frame | scratch.py sha256 | Cases | As required | Not as required |
|---|---|---|---|---|
| v6 working copy | `2255d6e1…` | 14 | **14** | none |
| v5, frozen and reviewed UNQUALIFIED | `f9f6596d…` | 14 | 6 | append, chmod, retime and same-size rewrite, each on the excluded and the recorded file (8) |

**How the cases were refused:**
- v6 refuses content, mode and timestamp changes with "file changed after its observation". It refuses replace and
  delete with "directory changed after its walk".
- v5 refuses only replace and delete, which change the directory. It accepts the other eight mutations and returns the
  stale pre-mutation record. That is the V5-B01 defect, reproduced on throwaway trees.

## Regression: the full v5 author self-check against v6

**Run.** 2026-10-04 23:40:21Z, through `regression_v6.py`, which leaves both the harness and the frame unmodified:
- It reads the unchanged v5 harness (`scratchgen-v5/selfcheck.py`, sha256 `3ccb9c0f…4ab3`).
- In memory, it retargets that harness's single `FRAME` line to the v6 working copy.
- Output is in `regression-2026-10-04T234021Z/`.

| Frame | Cases | Failures |
|---|---|---|
| v5 baseline (`selfcheck-2`, earlier today) | 85 | 0 |
| v6 working copy (`2255d6e1…`) | 85 | **0** |

As in the v5 run, the harness performed none of these:
- a gprbuild, gnatprove or systemd-run launch;
- any access to the real shared window;
- adopt;
- the real run or child launch path;
- a real owned scope.

The dispatch case's frame `run` verb refused before admission.

## Boundary of this result

This is ENGINEERING_ONLY evidence. It is not proof, review, admission, source-qualification or Phase One acceptance.

**What it shows:** within one walk, v6's final pass revalidates recorded and excluded files, as V5-B01's first
sentence requires. The frame calls this machinery at materialization, at admission, immediately before the spawn, and at
conclusion. That placement is stated by the `verify_materialization` docstring and has not been re-tested here.

**What it does not show:**
- **The custody half of V5-B01** ("custody that prevents the admitted generation from changing before use"). That
  needs the W-1 boundary.
- **Anything about V5-B02.**
- **Timestamp-granularity limits** (ruled acceptable) are not probed.

**Correction to W-1 v2.** W-1 v2 §4.5 says the excluded-leaf extension is "required and not yet written". That
understates it:
- the v6 working copy already records excluded files in `accepted` (`scratch.py:554`) and re-stats them in the final
  pass (`:569-573`);
- this self-check exercises that code.

This is an author-side correction, recorded here and in STATUS. The frozen v2 is not edited.
