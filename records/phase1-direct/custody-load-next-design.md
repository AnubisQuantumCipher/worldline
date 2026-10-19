# Custody decoder continuation after D131

The D131 selected proof batch failed with fresh reports: Counts could not establish a possibly empty materialized array lower bound; Append_Event_Extras lost capacity facts across Extra calls and could not establish the raw cause hash precondition; both decoder wrappers lacked the private Decode_Into contract. These failures remain in custody-load-next-proofs-v1.

The candidate canonicalizes only the empty raw span origin to 1; nonempty arrays retain their origin and full length. Append_SQL_Cell now exposes scalar monotonicity and conditional arena capacity preservation; its nested Extra caller must prove the same facts. These contracts use only scalar Used old-values, not whole-arena snapshots. The cause hashing branch revalidates the actual span and residual capacity before writing its fixed SHA-256 hexadecimal result. Original sizing/preflight remain. There is no new size cap or assumed premise.

Decode_Into exposes the original public validity conjunction plus the grown-decoder count relation and actual used count. This private contract must itself be proved; successful wrapper proofs alone are insufficient. The event-extra helper now borrows distinct components instead of capturing the full Parsed_Input owner, preserving the caller's unrelated scalar facts.

The compiler-directed array-syntax candidate was applied only after both original and candidate hashes matched the prepared audit. Record aggregates and expressions are unchanged; no warning suppression was added.

Added controls exercise real producer-generated scoped event extras, an independent hashlib SHA-256 oracle, exact capacity, one-byte-short refusal, invalid Used, unchanged input bytes, and arrays ending at Byte_Index Last. The cases are synthetic decoder operands, not protected or actor evidence. Original empty/populated fixtures and all prior controls remain. New controls are enrolled in the shared assurance roster.

Acceptance required: fresh whole-unit flow, strict targeted proofs including each new contract implementation, checked builds, new endpoint controls and original decoder/runtime regressions. Full Phase One proof/runtime, authentic protected/actor witnesses and F7 remain separate open obligations. This candidate is not accepted or released.

The private Extra proof identified its existing unconstrained-output premise; this is now explicit and must be proved at all callers. The bounded Decode_Into run timed out without a completed report. Its exact initialization block is now a separate private Initialize_Input procedure with scalar postconditions, reducing the monolithic proof expression while retaining every initialization and byte-copy operation. Both bodies must be proved; this is not a skipped region.
