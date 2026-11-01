No unchanged DISK recipe is presently qualified for D152. Historical disk execution is useful evidence of tool usability, but does not qualify the new source, imported-output handling or current storage contract. This is a present readiness finding, not a permanent disk-path blocker.

Verified by read-only inspection:

- Carrier HEAD is `e6c8fc7bd495ae9b5c87f6b29365c989de6a0c3e`.
- D152 manifest remains `98c97fd6…20a6a`; proposed body remains `b04f6bcc…64104`.
- All 29 original/snapshot mappings in `replay-proof-proposal-v1/source-closure.json` still match their recorded preimages.
- Current public lifecycle spec is `ecb01e4d…51c27`; current lifecycle body is `87aa67b6…403bf`; reviewed shadow body is `1b4b5870…60593`. That shadow changes only the reconciliation Post and redundant visibility clause.
- All 24 original source-derived row oracles remain present and UNRUN.

The actual existing disk routes are:

| Route | Retained evidence | Suitability boundary |
|---|---|---|
| `checked-build-v2` through `scripts/phase1_heavy.py` | Checked `gprbuild` exited 0 on dirty `c6c0674`, 2026-10-26; 8GiB/swap0; terminal scope inactive/unpopulated | Historical build only. No task-specific aggregate output/restore budget in its launch receipt |
| `numeric_isolated_v1.py` | D139 records independently read back scoped proof results | Checks 10GB reserve +60MB admission, polls +30MB stop margin, 180s command deadline; no aggregate output cap or restore procedure |
| `utf8_chunk_proof_v2.py` using that disk driver | Corrected-source run stopped after six seconds on falling filesystem capacity | No fresh qualifying summary; D140 expressly says sampling is not a filesystem quota |

Relevant implementation locations are `numeric_isolated_v1.py:41`, `scripts/phase1_heavy.py:60` and `:128`, and `docs/decisions.md:2260–2330`. The heavy wrapper alone retains indefinite refusal/backoff and cleanup loops; the reviewed capacity guard supplies finite scheduling/cancellation.

The smallest D152 source preparation would reuse the 29-file proof closure, substitute only the exact D152 replay after-body, preserve the public spec, and add `Equality_Model` and `Row_Model` to required report entities. Preserve the two separate whole-unit targets:

```text
gnatprove -P <reviewed-project>
  --no-inlining --mode=all --level=3 --report=all
  --checks-as-errors=on --proof-warnings=on --warnings=error
  --memlimit=1024 --timeout=5 -j2
  -XWORLDLINE_BUILD=checks -XSPARKLIB_MODE=full
  -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static
  -XSPARKLIB_INSTALLED=True
  -XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True
  -XREPLAY_PROOF_OBJECT_DIR=<fresh-owned-output>
  -u worldline-ordinary_reservation_replay.adb
```

The ordinary target separately selects `worldline-ordinary_reservation_lifecycle.adb`. Keep 180s tool, 220s collector, 240s heavy-wrapper and 270s outer-monitor bounds; 8GiB/swap0 and post-lock 14GiB admission remain unchanged.

Minimum disk readiness gaps:

1. **Reviewed sequencing decision:** D152 at `docs/decisions.md:2827` explicitly requires private IPC qualification first. Master Phase 1.3 permits a qualified disk alternative, but does not silently amend that recorded sequence.
2. **Imported-output ownership:** changing `REPLAY_PROOF_OBJECT_DIR` alone is insufficient. The local Attest GPR hardcodes original `obj/attest-sha256`; SPARKlib uses its real original object/library paths. The existing RAM adapter overlays private copies. A direct disk launch has no reviewed equivalent protecting those originals.
3. **Registered allocation budget:** retain original ceilings—32MiB output/1,024 inodes, separate 32MiB restoration, 8MiB archive, 4MiB receipts, plus bounded heavy-wrapper/monitor evidence. Moving those RAM allocations onto disk changes the simultaneous disk peak. The first four already total 76MiB, exceeding the old 60MB admission margin. Exact total disk growth/recovery allowance is presently UNKNOWN.
4. **Current controlled-failure evidence:** no reviewed disk adaptation demonstrates refusal, partial output, bounded termination, complete retention/recovery and unchanged original imports for this package.
5. **Proof coverage:** the two `-u` targets do not prove all dependency bodies. The 13-body source closure, actual selector/parser callbacks, imported SPARKlib and Attest retain separate coverage obligations. Source availability is not body proof.

A qualifying replay report must cover both new models, both Posts, every existing replay entity, caller obligations and generated flow/RTE/termination checks, with zero warnings, unproved, justified or Assume checks. Independent readback must bind the fresh report, exact sources/tools/argv, complete retained outputs, restored metadata and terminal cleanup.

The 24 oracles, arbitrary Node/Op domain, malformed matched-attach `(False,1)`, null-versus-missing distinction, independent `ne`/`literalFalse`, mask bounds, malformed-prefix cutoff and mutant rejection remain mandatory runtime work. Fold induction, both declarative-equivalence directions, production Plan establishment and G0/A/O/C/F acceptance remain open. Nothing inspected establishes F7.

Your selected continuation of the already prepared IPC diagnostic avoids introducing another verification mechanism now. No source, storage, locks, pins or runtime state were changed during this investigation.

<oai-mem-citation>
<citation_entries>
MEMORY.md:613-615|note=[located authoritative carrier and historical heavy wrapper boundaries; verified against current files]
MEMORY.md:619-622|note=[preserved scoped proof and acceptance distinctions]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
