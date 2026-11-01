**REJECT — IPC-DIAGNOSTIC-COMPOSITION revision 1.** The malformed-input and resource boundaries need repair before admitting the nominal diagnostic.

Packet SHA256 matches `1f8193365c4f4482e3ff57175f5224cd0281e7c5524c782855ff2d0068a01ae0`; all 29 references match their sizes/hashes.

Confirmed counterexamples in `ram_qualification_v5.py`:

1. **Malformed rows can produce a false unique join** — lines 806–821. Starting with fixture rows IDs `1,2,3`, append `"\n" + raw_row_ID3` to row ID1 and recompute the declared candidate hash. The 744-byte evidence still declares three rows. `raw.split()` ignores the record boundary, and the consumer reports `candidate_digest_verified=true` and a unique FD3 join despite the duplicate ID3 record. Reject embedded CR/LF and validate exactly one record per row before hashing/correlation.

2. **Malformed bounded stdout can abort parent finalization** — lines 908–926. A valid JSON object containing schema/mode/status and `error="x"*7900`, without `mount_evidence`, occupies 7,996 stdout bytes. The missing evidence is caught, but the copied error makes the summary exceed its ceiling. The final size assertion is outside `try`, so `mount_diagnostic()` raises instead of returning UNPROVEN. Parent line 442 then prevents writing `result.json` and reaching its preserved terminal return expression. Validate/bound copied fields and return a bounded failure summary for every malformed input.

3. **Archive limits follow parsing rather than bound it** — lines 792–794. A 7,434-byte gzip containing 1,025 USTAR members is fully enumerated before entry-count refusal. A separate 34,514-byte gzip containing valid stdout plus an unlisted 33 MiB regular member is accepted for diagnostic interpretation against a two-entry inventory. Check headers, supported format, inventory correspondence, entry count and cumulative expanded size during a bounded scan, before processing excess data.

4. **Optional-result comparison conflates JSON types** — lines 884–889. Changing only optional-result `candidate_count` from integer `3` to float `3.0` produces `optional_result="IDENTICAL"` and retains the unique-join interpretation. Python dictionary equality supplies the wrong contract here. Require type-sensitive comparison of validated JSON values.

These are **TESTED synthetic counterexamples**, not observed executions of the fixed producer. Embedded newlines and the oversized error cannot arise from the inspected v3 producer’s normal encoding. Archive fixtures used a coherent mocked receipt boundary; they do not establish receipt-chain forgery or same-UID authenticity.

**Verified preservation:** independently replayed all 42 existing pure cases; confirmed the four-literal guard delta, unchanged inherited collector functions except the declared parent changes, unchanged parent return AST, and maximum collector function length 55. Inspected operational caps/cleanup and original predicates. No runtime entrypoint, guard, IPC, mount, compiler, proof, storage or network operation ran.

The historical archive still contains `FAILED / private identity / private shm mount mismatch`, with original stdout hash `5cbae8de9c3d5f28a20645a57f6ab04cfd1aade4fb6754aba486eec643a1752a`. D155 remains `APPROVED_PREPARATION_ONLY`, with revision allowance zero; neither history is reset.

Smallest sound next step: use the composition dossier’s single revision to repair these collector-consumer boundaries, preserve guard/probe/original predicates, and seal regression evidence for the four counterexamples. Require exact revised hashes, regression passes, preserved operational formation, paired review and separate judgment. Only then consider fresh source/capacity admission and explicit storage-owner handoff. Actual execution remains **UNRUN**; mechanism qualification, Phase One and F7 remain unproved/unperformed.

<oai-mem-citation>
<citation_entries>
MEMORY.md:613-615|note=[background carrier and Phase One acceptance boundaries rechecked against current packet]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>