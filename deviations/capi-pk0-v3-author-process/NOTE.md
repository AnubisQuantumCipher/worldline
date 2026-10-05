# PK-0 v3 drafting author: process record (preserved; disclosed)

**Who and when.** The C-API drafting agent (`a15cbfbc1dbf895f6`). The lead resumed it ~18:00Z on 2026-10-05, and it handed
back ~19:20Z as a text reply. Its report is model output, recorded as stated.

## What the lead verified (engineering only)

- **Hashes.** All nine files hash to the reported values.
- **Bound inputs.** All 100 match L0.
- **Payload paths.** The six payload paths are absent from L0.
- **Earlier packets.** v1 (`9808145e…`) and v2 (`c5ce00cd…`) are unchanged.
- **Parse checks.** Every JSON file loads and every Python file parses.

## Disclosures

1. **RC-v2-1 not fully closed.** The Kind 1 request-array overlap with the descriptor is recorded OPEN (deviation 2).
2. **Beyond the letter of RC-v2-1.** Three element-guard conjuncts were added.
3. **Readiness.** It is checked by a separate per-case probe, not inside the oracle.
4. **Its own transcript.** The author grepped it once, finding nothing usable.
5. **Ada skills.** All eight were reloaded after compaction.
6. **No execution.** Writes went only under `capi-pk0-v3/`.

## What this does not change

PK-0 stays open until its independent review rules. The baseline run in an admitted frame is still required.
