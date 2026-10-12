# Claude Phase One engineering checkpoint

**This is an unfinished engineering checkpoint, not Phase One acceptance, a release, or a deployment.** It preserves the integrated source at `802708bf23f875c96000fff5e5fed3c68f8103a6`, the original committed development history, and selected execution evidence. It extends the existing checkpoint branch without modifying its historical records or the active development checkout.

The source includes acquisition closure, process-wait and timer repairs; bytes-capable finalization encoding; Base64 runtime-cost changes; canonical agent-record comparison; component proof repairs; recovery replay fixes; and the newly committed custody foreign-key and fixture-order changes. The snapshot is copied from committed Git objects, not from a changing working tree. `source-inventory.json` records the original Git blob identities, modes and SHA-256 hashes.

`history/source-history.bundle` preserves the captured branch histories. `history/source-refs.json` distinguishes refs included in the integrated source from unmerged component work. Those unmerged commits are retained for recovery only. They are not additional accepted candidates, and no uncommitted edits have been swept into this checkpoint. The source repository began with a separate Source20 snapshot history; the existing publication branch has not been rebased, replaced, or force-pushed.

**Execution evidence retains its original scope.** The completed diagnostic runtime survey names source `6b1b67db623948e58cf9c5f04b3a3293384ca982` and reports 127 action records, with 103 reported exit-zero outcomes and the remaining failures listed in its summary. It used an extended survey deadline and continued beyond failed dependencies. Those outcomes are not a pass of the original required campaign and do not establish behavior of publication source `802708b`. Missing runners/binaries and setup failures are not successful launches of the intended product tests.

The older independent audit in `evidence/audit/` is a time-stamped historical snapshot. Its runtime inventory predates the survey's completion; the later results are in `evidence/work/evidence/roster-run-3/`. Both are retained rather than silently rewriting the earlier record. Some retained prose names a different revision from the machine-readable run metadata; the discrepancy remains explicit.

The evidence includes the captured acquisition diagnosis, targeted passing runs, baseline comparisons, focused strict-proof successes, unresolved proof reports, failed or interrupted full surveys, the aggregate-build failure, runtime failures and custody regression work. `copy-receipts.json` maps each selected original to its stored bytes. Large completed acquisition streams are retained losslessly under `compressed-raw/`, with original and compressed hashes and full decompression verification. The largest gzip stream is split into ordered parts below GitHub's per-file limit; receipts preserve part identities and the complete compressed-stream hash, and the verifier reads and decompresses their concatenation. These supplement the initial compact selection's exclusions. Other build trees, proof caches, active streams, native binaries, credentials and conversation transcripts remain outside the package.

**Do not treat inherited source claims as fresh acceptance.** In particular, `source/proof-manifest.json` contains the historical statement “all checks proved, nothing assumed”; it is not evidence for this source revision. The observer redesign's exact-byte/digest binding claim in the inherited changelog remains subject to independent semantic review. Broadened preconditions, changed fixtures, and real production callers must still meet the original accepted guarantees.

Phase One still requires a fresh complete build; the full original strict proof and project gates; the complete original runtime suite and additions under their original conditions on matching source/library identities; timeout closure; all required production authority and ownership/reclamation obligations; authentic protected and world/child-world execution; and independent actual GPT-6.1 final acceptance. Only then can there be accepted final publication. The original requirements, accepted cases, controls, proof floors, and frozen candidates remain binding.

The retained context scripts are historical diagnostic tools, not a replacement for the authorized execution paths. Absolute paths in original records refer to the originating machine; this is selected checkpoint evidence, not a self-contained portable execution environment. No product build, proof, runtime campaign, installation or protected fixture was executed by the publisher.

To verify the preserved bytes, run:

```bash
python3 records/phase1-claude-checkpoint-20261012/verify_checkpoint.py
```

To recover the original integrated source history into a new directory, use the bundle without changing an active checkout:

```bash
git init /path/to/new/recovered-source
git -C /path/to/new/recovered-source fetch /absolute/path/to/source-history.bundle refs/checkpoint-source/main:refs/heads/recovered-main
git -C /path/to/new/recovered-source checkout recovered-main
```

Use `git bundle list-heads` to inspect the additional recovery refs. Their original names and exact tips are recorded in `history/source-refs.json`. Hash checks and bundle recovery establish preservation, not correctness or Phase One completion.
