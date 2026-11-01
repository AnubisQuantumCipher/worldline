**APPROVE — preparation for one nominal diagnostic only**, conditional on future fresh complete source/tool/runtime/resource admission and an explicit DUAT owner window. This is an independent internal review, not F7 independent acceptance.

Packet `ipc-composition-review-packet-v2.json` verified at SHA256 `1454c038af90a356ba46761520c7d4469b4ae260ba6232a0e076dada4c9e6deb`. All **62 referenced files matched both size and SHA256**, initially and after testing. No current peer verdict was consulted. No files were written.

The four mandatory revision defects are resolved within the inspected and tested scope:

| Finding | Evidence |
|---|---|
| Embedded records could create a false complete unique join | `ram_qualification_v6.py:943–959` now requires printable ASCII and exactly three fields following the separator. Six appended-record variants—LF, CR, VT, FF, tab, and space—were rejected. Completeness, full candidate digest, selector accounting and unique FD-ID correlation remain separately checked at lines 962–1019. |
| Oversized malformed fields could escape and prevent parent finalization | Lines 1032–1049 bound copied tool/stage/error fields; lines 1077–1083 bound failure summaries. Lines 1086–1099 contain ordinary generation and diagnostic receipt-write exceptions. Injection tests returned bounded `UNPROVEN` metadata for generation failure and `written:false` for receipt I/O failure. Parent attempts its mandatory result immediately afterward at lines 442–449. |
| Archive parsing expanded unsupported/unlisted content before enforcing bounds | Lines 795–940 implement bounded gzip output requests, fixed USTAR headers, early member validation, complete inventory correspondence, streaming file hashes, framing checks and single-gzip EOF. The original unlisted 33 MiB counterexample now refuses before payload expansion. |
| Optional JSON comparison conflated integer and float | Lines 1022–1029 compare canonical serialized JSON, preserving integer/float/boolean distinctions. Lines 752–775 reject duplicate keys, nonfinite constants and finite-token overflow. Independent `True` and `3.0` replacements for integer candidate count both produced `DIFFERENT` and `UNPROVEN`. |

**TESTED:** I inspected helper entrypoints, then invoked only their pure functions, with `PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1`, `python -B -W error`, and external 50-second/15-second bounds. Aggregate measured test-script time was approximately **0.688 seconds**, below the 60-second allowance.

Passing checks comprised:

- 42 inherited synthetic controls and two exit-zero observation controls.
- Reproduction of all four original v5 defects, followed by their v6 refusals.
- 13 scanner controls, six delimiter controls, bounded field/nonfinite tests and exception-containment injections.
- Additional independent controls for type differences, nested JSON, oversized integer tokens, duplicate keys, truncated gzip, trailing compressed bytes and trailing expanded data.
- A positive scanner boundary fixture containing **1,023 members and exactly 32 MiB payload**, compressed to 37,776 bytes.
- Actual historical **485-byte archive compatibility**: preserved stdout SHA256 `5cbae8de9c3d5f28a20645a57f6ab04cfd1aade4fb6754aba486eec643a1752a`; original `FAILED` / `private shm mount mismatch` remained unchanged.

**SOURCE-INSPECTED / AST-TESTED:** Every inherited v4 function except `parent` is AST-identical. Normalization verified the complete allowed collector delta, including the unchanged terminal success expression. Guard v3 is exactly the four permitted literal substitutions. The maximum collector function length is 54 lines. Original retention/restoration, positive and negative operational predicates, terminal exits, owned cleanup, shared locking and resource limits remain in place. Probe v3 remains pinned to `8d7816d6a37ed353c6682dd27b97c4b7cbbc95f7e20282cb84a4c10177b16260`; its exhausted revision allowance is unchanged.

**Limits:** No operational collector, guard or probe main ran. No IPC, namespace, mount, compiler, proof, network or storage-management action occurred. Parent finalization was assessed through source ordering and injected helper failures, not execution of the operational parent. Real I/O failure can still defeat the mandatory result write. Python, JSON, zlib and OS implementation behavior are trusted dependencies, not formally proved components. Synthetic malformed fixtures establish consumer behavior; they do not establish that the frozen authentic producer emits those fixtures or that receipt forgery is reachable.

No mandatory blocking defect was found in this review. D154’s actual failure and unknown cause remain preserved. Full retention credit still requires independent readback of the actual complete archive/restoration receipt chain.

The smallest sound next step is the separate judge’s disposition, followed—only if approved—by fresh admission and explicit owner-window evidence for the one nominal diagnostic. Actual execution remains **UNRUN**; mechanism qualification, product integration, Phase One acceptance and F7 remain open.
