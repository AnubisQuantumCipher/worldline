Ready for the registered sole revision. I verified the decision/judge packet hashes, all seven judge references and unchanged v1 payloads. No writes or operational execution occurred.

The minimal plan is:

1. **Make final receipt retention necessary for exit0.** Check the final `best_effort_record` result. Write, flush, short-write or budget failure must prevent zero exit. Preserve an existing nonzero exit. Cleanup remains independent of receipt availability and is attempted at most once within the existing bounds; earlier receipts remain intact.

2. **Validate both diagnostic streams after complete capture.** Keep command flags unchanged. Build stderr must be empty. Build stdout may contain only a finite, packet-registered set of exact progress records: fixed phase headers and producer/artifact records joined to the frozen input roster and explicit library/binder/executable names. Reject every other record, extra suffix, control delimiter, incomplete line or missing/mismatched capture evidence. Unknown legitimate progress fails closed; this does not claim universal output parsing.

3. **Require silent recovery diagnostics.** Native create/extract stdout and stderr must both be empty after successful complete capture and identity checks. Nonzero exit, capture exhaustion, missing evidence or nonempty output fails recovery. Preserve raw logs and partial archives.

I recommend **no quiet flag**: available local evidence does not establish complete warning preservation across GPR/compiler/binder/linker producers. Historical logs show ordinary progress interleaved with warnings, supporting literal progress validation rather than accepting an entire exit-zero transcript.

The regression matrix will cover:

- Final receipt success; write/flush exceptions; short write; exhausted record/total budget; preserved nonzero exit; cleanup independent of logging.
- All three build stages, both streams: clean permitted progress, synthetic warnings, unknown records, appended warnings, nonzero exit, exact-limit/overflow and missing/hash-mismatched evidence.
- Both recovery stages and streams with equivalent clean/warning/failure controls.
- Existing tests, immutable input/GPR/tool pins, caps, deadlines, cleanup ordering and read-only reviewer mode.

Changes belong only in v2’s necessary source, tests, contracts and provenance/manifests. V1 and every failure remain preserved. Functions remain≤60lines.

Native warning-free execution, format compatibility, resource fit and recovery remain UNRUN/UNPROVEN. The next step is the registered v2 writer lease after the current writer releases, then freeze and fresh paired review/judge. Any mandatory defect surviving this sole revision means BLOCK, without reset.
