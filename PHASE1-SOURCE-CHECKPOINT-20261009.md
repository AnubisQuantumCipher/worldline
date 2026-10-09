# Phase One F60 source checkpoint — 2026-10-09

**Work in progress. Phase One remains incomplete and unaccepted.**

This checkpoint preserves the complete frozen F60 integrated source and selected
review and failure records while development continues in a separate local
repository. The goal remains **Python orchestrates; SPARK decides** evaluation
lifecycle, resource reservation arithmetic, recovery, evidence roster/completeness,
typed optional identities, capability attenuation and receipt-chain rules.

## What is preserved

- [Complete F60 source](records/codex-resumption-20261007/phase1-integrated-v60-draft/source/):
  the current integrated Ada/SPARK kernel, Python adapters, tests, controls and
  supporting source. The measured comparison against the previous public v18
  source contains 466 added files, 96 changed files and no removed files.
- F60's statement-form `Ticket_Raw` repair, reviewed JSON object-order repair,
  enforcing body-pin updates and explicit additive control files. These are
  source changes; the runtime timeout is not claimed fixed.
- [Coherent source review](records/codex-resumption-20261007/phase1-integrated-v60-draft-review/independent-review.json),
  [auxiliary review](records/codex-resumption-20261007/native-owner-join-v59/v60-runtime-proof-independent-review.json)
  and [distinct strict-source review](records/codex-resumption-20261007/native-owner-join-v59/v60-full-strict-current-aux-bound-source-independent-review.json).
  Each records actual GPT-6.1 Sol at max effort and no blocking findings in its
  source-only scope. Their actual model/effort events and review hashes were
  checked for this publication. These qualifications do not establish proof,
  runtime success, frame admission or final acceptance.
- [C18/F60 actual strict-command result](records/codex-resumption-20261007/formal-successor-v18-preparation/evidence/full-strict-formal-diagnostic-v1/result.json)
  and [compiler diagnostic](records/codex-resumption-20261007/formal-successor-v18-preparation/evidence/full-strict-formal-diagnostic-v1/child.stderr):
  the original full strict invocation returned 1 during Global-contract generation,
  with `cannot untangle node N_IF_EXPRESSION` in `Original_Source`. The collected
  result records unchanged inputs. This is retained failure evidence.
- [Earlier N59/F59 runtime outcome](records/codex-resumption-20261007/phase1-v59-native-inner-cost-diagnostic-v1/attempts/e29c01fdd3134cea8889c58f8e68782e/child-outcome.json)
  and original streams: the checked build and 32 bounded smokes passed, but the
  unchanged original whole runtime suite timed out. The observation record
  identifies the last visible Python-to-native boundary; it does not establish
  the native root cause. **N59 results belong to F59, not F60.**

## Remaining work

The full strict proof has not passed on F60. The complete original matching-source
runtime suite and additions, genuine required owner/producer/actor fixtures,
independent final acceptance and applicable publication/deployment gates remain
open. Every original contract, accepted case, control, proof scope and floor stays
unchanged. A passing subset or source review closes none of those obligations.

The active F61 repair and M4 diagnostic preparation are deliberately outside this
frozen checkpoint. Their authors can continue without their worktree, index,
processes or frozen evidence being changed by publication.

## Identity and limits of this archive

[PHASE1-SOURCE-CHECKPOINT-20261009.json](PHASE1-SOURCE-CHECKPOINT-20261009.json)
contains the complete file hashes, Git blob identities, executable modes, source
comparison, provenance and exclusions. F60 was frozen on disk but not committed
in the engineering repository at capture. That repository's separate committed
F57 checkpoint is identified in the manifest; it is not mislabeled as F60.

All selected original files were copied byte-for-byte. The source matched its
complete stable inventory before and after copying. Full local dependency
closures, private toolchain copies, binaries, generated proof objects and agent
transcripts were not published. Absolute paths in historical records retain their
original meaning; referenced local dependencies are not promised to be available
in this partial public evidence archive. Git preserves file contents and executable
bits, not all local permission bits or empty directories.

This branch has independent engineering-archive history. It is not merge-ready
product history, an admitted runnable frame, an installable release or a Phase One
completion claim. No target build, prover run, runtime campaign, merge, release,
installation or deployment was performed for this upload.

Verify the published file binding without executing product code:

```sh
python3 verify_checkpoint_20261009.py --check
```
