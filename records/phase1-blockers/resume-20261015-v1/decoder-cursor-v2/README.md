# Source-relative decoder candidate — unapplied

**UNVERIFIED.** This is an internal repair candidate, not an implementation of a new accepted grammar. Neither the candidate nor its proposed controls/proof project has been compiled, imported, executed or proved. Production Raw_JSON and its callers are untouched by this proposal and remain unfixed until integration. Source/proposal bytes, command and observed revision are in `preparation-receipt.json`.

The candidate extracts the original encoding detection and scalar interpretation from `Worldline.Raw_JSON.Decode_JSON`. A caller retains the complete original `Resource_Quantities.Byte_Array`, supplies it explicitly on every `Read`, and stores only `(Item, Kind, Offset)` in a cursor. Offset and span length use the original Byte_Count domain. `Step.Value` is the existing Archive_Text.Code_Point subtype, including surrogates. No complete UTF8 output, summed output extent, array allocation, access value, exception recovery, input-size cap, Assume, justified check or SPARK-Off body was added. Compiler-generated calling convention or hidden temporaries have not been measured.

## Candidate surface and semantics

- `Initial` is total. Detection retains the exact original BOM and BOM-less precedence and returns the source offset after only the initial BOM. An invalid span is preserved and produces a harmless default encoding/offset; `Read` rejects it before accessing data.
- `Read` is total for every typed original span, encoding and offset. It has no precondition. On `Decoded`, its Next_Offset strictly advances and stays within the span. On other statuses it preserves the offset and returns the zero placeholder value. `End_Of_Text` occurs exactly at the end of a valid span; invalid positions and malformed/truncated sequences are distinct statuses.
- Offset validity is only source-relative. There is no unit-alignment condition and no requirement that Offset be at or after Initial's BOM skip. Direct reads at unaligned UTF16/32 offsets remain defined by the bytes there; direct UTF8 continuation reads report Invalid_Sequence, not Invalid_Position. Controls include these cases and a direct read of an initial BOM as content.
- The public record is deliberately not a source-custody capability. Supplying another encoding/offset means requesting that local interpretation; it does not certify detection, previous content, complete decoding, JSON grammar or bytes from an earlier call. Whole-source consumers must begin at `Initial`, use the same immutable Data and Item/Kind, follow each returned Next_Offset, and reject any invalid status. No externally supplied success Boolean substitutes for that traversal.
- `Reference_Read` is a Ghost expression defining the local step with explicit byte equations. The executable body does not call it. Both the expression and the independently structured body remain in candidate proof scope; neither has a proof result. This is a local scalar denotation, not a full-value/'Old solution or a proof of the existing JSON parser.
- Helper Byte_At/Unit_16/Unit_32/Pair_Value preconditions protect only internal byte accesses and formulas. They impose no new precondition on Initial or Read. Control helper preconditions express the explicit fixture oracle at each test call and create caller obligations; they do not constrain production input. Controls still compare actual Read results against independent fixture constants with assertions enabled.

## Exact source-case correspondence to be reviewed/proved

The following table describes the intended equality to the retained original source, **UNVERIFIED** until the candidate's body contracts and eventual integration correspondence are proved. It does not claim the old Natural/String materializer is total.

| Original case | Candidate case and remaining obligation |
|---|---|
| `not P.Valid(Data, Item)` | Same span-domain condition through Archive_Text.Span_Valid: empty spans are valid regardless of First; positive spans require First in Data and complete extent inclusion. Initial reads nothing on invalid spans; Read returns Invalid_Position. Equivalence of the two positive-span arithmetic formulations remains an explicit integration proof obligation. |
| UTF32 BE BOM; UTF32 LE BOM | Detected_Encoding checks these before overlapping UTF16 BOMs; BOM_Length skips the same prefix. `FF FE 00 00` remains UTF32 LE, never UTF16 LE followed by a NUL. |
| UTF16 BE BOM; UTF16 LE BOM | Same precedence and source start; odd remaining byte counts are eventually Invalid_Sequence, not EOF. |
| UTF8 BOM | Same initial-only skip. A second BOM is returned as the existing codepoint, not stripped again. |
| BOM-less span length at least four | Same first/second/third/fourth-byte condition tree. Leading zero/second-byte-zero cases retain the original UTF16 versus UTF32 choice. |
| BOM-less span length exactly two | Same two-byte UTF16 heuristic. No such heuristic is added at length three or one. |
| UTF8 scalar | Same Archive_Text.Unit_Width and Value_At. Existing canonical surrogatepass UTF8 acceptance/rejection is unchanged; overlong, out-of-range, truncated and bad continuation sequences remain invalid. |
| UTF16 complete non-high unit | Same unit value and source advance, including lone low surrogates. |
| UTF16 high unit with complete following low unit | Same pair formula and combined source advance. Candidate guards remaining bytes before forming the lookahead offset. |
| UTF16 high without a following low unit | Same unpaired high codepoint; a complete non-low lookahead is left for the next Read. A trailing odd byte is rejected on the next step, so a valid prefix never establishes whole-input success. |
| UTF32 | Body keeps the original byte-order recurrence; Unit_32 specifies its unrolled byte polynomial. Same maximum Code_Point ceiling, including acceptance of surrogate values and rejection of greater values. Prove recurrence/polynomial equality, not only the result range. |
| Empty source or BOM only | Initial cursor is at end; decoded sequence is empty. This does not call it valid JSON. |
| Old `Length := Length + Width(C)` and full UTF8 String emission | Deliberately absent from this scalar API. Exact codepoint content and order are retained without an expanded total-output index. Production consumers still need shared grammar/stream integration; merely replacing the old call with a cursor and leaving String consumers would not repair the domain. |

No scalar error is translated into success. The original first pass abandoned all output on error; the replacement whole-source consumer must do so as well. Partial decoded prefixes are observable only through the explicit incremental API and must never be promoted to a complete JSON result.

## Proposed deterministic controls

`decoder_cursor_controls.adb` contains fixed assertions for every supported byte order with and without BOM; overlapping BOM precedence; the length-three non-heuristic; empty/BOM-only inputs; double BOM; UTF8 multi-byte values and maximum; surrogatepass in UTF8/16/32; minimal/maximum surrogate pairs; lone high/low units; non-low lookahead; malformed/truncated tails; overlong/out-of-range UTF8; UTF32 ceiling rejection; shifted array and span origins; invalid spans and offsets; and small arrays whose actual index is Byte_Count'Last.

These endpoint-index fixtures are small arrays, not measured enormous inputs. An invalid huge span is a refusal control, not a valid huge-input execution. Universal extent/progress safety remains a proof obligation. This proposal neither runs a second isolated positive revalidation diagnostic nor replaces any original acquisition/runtime/protected/actor control.

The arithmetic for selected expected scalar constants was requested through JACKAL exact rational arithmetic; full responses are retained in `jackal-arithmetic.json`. Status is **exact**, outside the Lean certificate chain and not formal-bounded. Their non-claims are retained. Parsed inputs are `2*64+34`, `2*4096+2*64+44`, `13*4096+32*64`, `4*262144+15*4096+63*64+63`, and `65536+(56319-55296)*1024+57343-56320`. This confirms only those arithmetic evaluations; byte interpretation/transcription and Ada correctness still need their own evidence.

## Intended candidate proof/build closure — not executed

`decoder_cursor_candidate.gpr` explicitly enrolls the new spec/body, proposed control main, and unchanged byte-pinned dependencies: Resource_Quantities spec/body, Archive_Text spec/body, Worldline root spec, and Attest/Attest.SHA256 spec/body. It imports the configured full SPARK library, not the repository's stub. It writes only to this candidate's obj/bin paths if the coordinator later launches it. There are no assumed replacement dependencies. The manifest records exact dependency bytes.

Proposed payloads, from this directory, after the coordinator's existing admission/lock/scope wrapper and toolchain environment are selected:

```text
gprbuild -P decoder_cursor_candidate.gpr -j2 -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True
gnatprove -P decoder_cursor_candidate.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on --memlimit=1024 --timeout=60 -j2 -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True
bin/decoder_cursor_controls
```

These are not permission to bypass flock, post-lock memory admission, systemd MemoryMax, storage admission or retained output policy. The coordinator owns the launcher and chooses a fresh result path. The complete candidate closure must have zero unproved/justified/Assume and no silently skipped new unit; runtime assertions must be enabled. Unproved dependency checks remain visible. Source snapshots prevent concurrent product edits from silently changing a candidate run, but a successful snapshot run still cannot substitute for full WORLDLINE proof/build/runtime on the later integrated frozen source.

Proof targets include span/index arithmetic, all initial offset bounds, Unit_16 and Pair_Value result constraints, Unit_32/body recurrence correspondence, Archive_Text UTF8 contracts/bodies, total status classification, strict successful progress, unchanged invalid offsets, and every explicit finite fixture call's precondition. The installed toolchain may require additional truthful invariants/assertions or expose real defects; no compile or proof claim is made here.

## Smallest future shared-grammar integration

1. Enroll this internal source reader in the complete original source/proof inventories after review. Complete its proof and retain any failures. Replace Raw_JSON's *representation* only together with its consuming interface changes; do not keep the impossible total String return or add a Natural cap.
2. Factor the existing Producer_Values parser body over a scalar read/advance interface, retaining one grammar implementation. Use Count-relative token start/after positions and Count ordinals for the wide reader. Keep the old String signatures as adapters to that shared grammar where their actual bounds justify conversions. Preserve ordinary last-duplicate-wins semantics, exact/duplicate-free predicates, nonfinite numbers and Python equality rules. Do not copy or replace the grammar with Canonical_Artifacts.
3. Use complete scalar traversal and the existing grammar's complete-consumption condition to validate the whole source. Parse node spans and decoded strings through cursors; Slice returns a view and Text returns an escape-decoding iterator on the wide path. Numeric tokens remain exact through the existing Count-indexed Exact_Decimal API without a String intermediate. Consumers compare/render local pieces rather than materializing an entire expanded UTF8 result.
4. Migrate Raw_JSON matchers, Evaluation_Role_Native mixed String/view consumers, and Recovery_Material_Replay journal/JSON/Syntax_Inputs materializers as mapped in the preceding total-domain design. Preserve complete original raw evidence and lifetime; no view may retain a pointer into a local byte-array temporary.
5. Prove parser/adapter/consumer correspondence and all range/progress obligations on the full original domain, then execute every original required control and full frozen-source gate. Independent acceptance remains NOT PERFORMED.

This candidate closes no gate and does not classify the retained acquisition timeout. It supplies a concrete narrow decoder primitive for review, proof and integration work.
