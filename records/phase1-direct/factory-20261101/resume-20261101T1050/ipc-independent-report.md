**APPROVE — limited to preparing a separately reviewed collector/guard successor.** No launch, IPC qualification, proof or F7 approval.

- **OBSERVED:** Packet SHA-256 matches `a08d01f5f4cef07e90b6cf0144f877472959ba19ee22419661152dac8cc02a88`; all 18 referenced lengths and hashes match.
- **TESTED:** Independent in-memory AST comparison confirms only the three declared original functions changed and all original mount predicates remain. Synthetic missing, duplicate and malformed fd mount IDs refuse. No receipt-writing mains or actual probe/IPC operations ran.
- **Preservation:** `private-ipc-probe-v2/probe.py:138–165` retains original predicates after bounded observation; `168–190` preserves namespace, identity, ownership and quotas. Existing cleanup and IPC functions remain AST-identical. `405–423` preserves the stdout ceiling and fails closed on overflow, explicitly recording evidence loss.
- **Diagnostic adequacy:** `107–159` retains covering rows, original selected ID and opened descriptor ID before original mount refusal. This supports distinguishing a covered-row selection error **when the FD ID uniquely joins a retained row**. Incomplete retention explicitly refuses.

**Required successor conditions and counterexample**

1. Do not equate `mount_evidence.complete` with a complete topology diagnosis. It means row retention completeness (`probe.py:130–132`). Independent synthetic input with normal rows IDs 1–5 and fd `mnt_id:999` returns without error and reports `complete=true` (`150–165`). This is consistent with the explicitly unchanged diagnostic predicates, but cannot establish the required discriminator. The successor’s assessment must require a unique retained-row join and preserve missing/ambiguous joins as **UNPROVEN**.
2. Existing `ram_qualification_v4.py:23` still selects v1; its positive checker at `710–738` does not check the new diagnostic evidence. Changing only its source pin would not establish diagnostic acceptance. Review exact successor pins, caller interpretation and failure retention.
3. Add bounded synthetic successor checks for unjoined/duplicate mount IDs, read failures, incomplete evidence, and pretty-result versus compact-stdout overflow. Existing tests chiefly exercise observation/rendering, not finalization/caller composition (`source_tests.py:55–87,125–149`; `probe.py:364–402`).

**No blocking v2 source fix identified for this preparation-only gate.** Actual mount topology, fd correlation, resource consumption, cleanup behavior and all six qualification cases remain unverified. Smallest sound next step: prepare the pinned collector/guard successor and its diagnostic acceptance contract for separate review; retain original execution admission and independent F7 requirements.

Requested reviewer provenance: independent internal reviewer, `gpt-6-astra`, medium. Actual routing/backend identity is for root to record; I do not attest it.

<oai-mem-citation>
<citation_entries>
MEMORY.md:613-622|note=[Kept historical Phase One evidence separate from current acceptance]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
