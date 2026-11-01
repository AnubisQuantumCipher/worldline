Verified D160 v2 decision SHA256 `0c3181f154032134bf7eb944322100efa1755872c847c1e8f270ef5a79cf7483`. No writes or execution performed.

Propose a separately registered package capped at **2 MiB, 23 files, 28 root-inclusive entries**:

- Immutable original body, exact derived body and unchanged patch; retain original SHA `8559ff…18ece` and require derived SHA `f0843c…6143c`.
- `fixture/`: library-level aliased buffers, bounded independent first-match oracle, lifecycle cases, mailbox cases, combined main and one fixture GPR. Approximately nine Ada files; short routines, fixed cases and bounded loops.
- `validation/`: bounded result validator and wrong-expectation/missing-row controls.
- Metadata: contract, case roster, resource accounting, provenance, immutable input references, registration reference, static-check receipt and self-excluded typed manifest.

The combined executable will preserve the reviewed **12 Compile / 11 nonempty / 22 allocation** accounting, two Pattern objects and four designated blocks. Library-level caller-owned buffers use `On_Close => null`, with enabled accessibility checks and lexical Box/cursor finalization. Lifecycle release checks target the post-elaboration baseline.

The fixture GPR will import the unchanged core project and enable strict warnings-as-errors, assertions, overflow and validity checks. Original dependency GPRs remain unchanged. Input references will bind exact minimal/core/constants/helper GPRs, the 342-input roster, tool/runtime pins, immutable registration/decision packets and source acquisition records. Mutable global progress/decision files will be excluded.

Results will use a fixed ordered ASCII protocol: **11 SEARCH, 11 FREE, two consumer-state records and one completion record**. The validator will accept exactly 25 records, bounded line lengths and ≤16 KiB input; reject mismatches, duplicates, missing/truncated rows and unexpected tokens. Future controls will demonstrate rejection of one deliberately wrong expectation and one missing row.

Source preparation will permit only bounded hash/roster checks, exact patch reconstruction, finite case arithmetic, Python AST parsing and source inspection—**≤10 seconds**, no compiler, fixture execution or validator-control execution. Native legality, intrinsic behavior, assertions, accessibility, pool release and whole-process fit remain unproved.

Actual CGPR selection, normalization/matching and consumed runtime closure remain future prerequisites. No wrapper or integration is proposed now. D160/D158/D159 budgets remain exhausted; awaiting a distinct registration and writer lease.