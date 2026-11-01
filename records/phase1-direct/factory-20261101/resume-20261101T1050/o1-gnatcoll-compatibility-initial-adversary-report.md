Verdict: **REQUEST CHANGES — one mandatory proposal correction.** Withhold derivative/fixture preparation approval for this INITIAL packet until the finite resource contract is corrected. No native execution is authorized.

Independently OBSERVED:

- Packet SHA256 matches `7d4c2fc8dd68c27286b2c5d84ae2864b3c4055a0334002b51b5c86933c2469bc`.
- Manifest matches `c5df18ce9a98cb2ae9f9d16a4d022b22d8d43663ce2b8d53d426c06408727daa`; eight files, 39,192 bytes; listed payload hashes/types/modes/link counts match.
- HEAD is `b916c7a9f550613bb1daa54f31ecd6b1f59a0ba6`.
- Original and failed staged body match: 12,701 bytes, SHA256 `8559ff…8ece`, Git blob `6fa9d24…df6`. Acquisition row 249 matches the dossier; receipt hash matches.
- Each replacement occurs once. Applying replacements in memory produces 12,721 bytes, SHA256 `f0843c5a17d7cd01901828b46a291649349131ce55592ae72155d9ecf966143c`; reversing them restores the original exactly.
- Both runtime declaration hashes match. Both access pairs and `Good_Suffix`-then-`Motif` call order remain unchanged.
- Independent literal arithmetic confirms D01 length 47, D02 length 23, LF-separator index 24.

**Mandatory defect: combined fixture resource accounting omits the consumer’s persistent Pattern.** `LIFECYCLE-FIXTURE-SPEC.md:44` states 20 allocations, at most one Pattern and two live owned heap blocks. However, `gnatcoll-email-mailboxes.adb:39` declares `From_Pattern`, and its elaboration at line 989 calls `Compile` on the nonempty six-character `LF & "From "` pattern. If lifecycle and consumer controls share an executable, this happens before lifecycle rows and remains live throughout them. For these two Pattern sources alone, that means **22 allocation operations and up to four simultaneously live designated heap blocks**, plus two Pattern objects. Other dependency/runtime allocations remain separately unaccounted.

The smallest correction is to define the executable topology and accounting scope explicitly. For a combined executable, separate lifecycle-local contributions from the persistent consumer contribution and total them. Alternatively, specify separate executables and account for each invocation and its elaboration separately within unchanged aggregate bounds. Merely running cases sequentially does not eliminate the elaborated consumer Pattern. This correction needs no native result or resource increase.

A concrete **later fixture implementation requirement**, not an additional proposal blocker: buffer lifetime alone does not establish legal accessibility. `Open` converts the anonymous access parameter to library-level `GNAT.Strings.String_Access` at `gnatcoll-email-mailboxes.adb:120`. The inspected compiler conversion code applies accessibility checks to access parameters. A local stack buffer passed with ordinary `'Access` can therefore raise `Program_Error` despite outliving its Box. Select a legally accessible arrangement, such as separately declared library-level aliased fixture buffers, retain `On_Close => null`, and verify actual checked execution. Do not bypass accessibility checks with unchecked/unrestricted access.

The canonical-name change itself has no demonstrated mandatory textual defect. The dossier correctly leaves intrinsic lowering, actual assertion policy, canonical `Post` behavior, null handling, pool/deallocation behavior and elaboration effects UNPROVEN. Lifecycle values and consumer iterator states are reasonable finite oracles; they do not prove private null fields, release accounting, or exact private cursor boundaries.

Actual fixture code, selected configuration/runtime/tool closure, clean strict builds, linked identities, allocator evidence, negative harness controls and deadline fit properly remain later qualification requirements. Their absence is not grounds to demand native execution during this source-only review.

Use the single evidence-driven D160 revision to correct the resource specification, preserve this immutable packet and failed history, then obtain the required renewed review/judge decision. D158/D159 remain at zero revisions; storage remains human-paused; generator remains UNQUALIFIED; F7 remains NOT PERFORMED. No files were written and no native/configuration, network, lock, service or storage operation was performed.