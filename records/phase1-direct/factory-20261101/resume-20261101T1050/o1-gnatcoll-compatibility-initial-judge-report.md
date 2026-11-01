Verdict: **REQUEST CHANGES — mandatory finite-resource specification correction.** Withhold derivative/fixture preparation approval for D160 INITIAL. No implementation or native execution is authorized.

**OBSERVED:** Judge packet SHA256 matches `88ce3c1c6fd14b33d53797a189ee4e7f1670b41e33e42a93ef0eca681e75f368`. All 26 directly checked references across judge and original review packets match recorded sizes/hashes. HEAD matches `b916c7a9f550613bb1daa54f31ecd6b1f59a0ba6`; four disclosed documentary differences are present. Local reviewer routing records are provenance metadata, not backend attestation.

The adversary’s objection is substantiated. `LIFECYCLE-FIXTURE-SPEC.md:44` gives an unqualified bound of 20 allocation operations, one Pattern and two live owned heap blocks. The combined lifecycle/consumer executable necessarily elaborates `gnatcoll-email-mailboxes.adb` first: its package-level `From_Pattern` at line 39 is compiled with six characters at line 989. `Compile` allocates a String and an Offset_Array for this nonempty input. That Pattern remains live while lifecycle cases execute. Sequential cases do not remove this contribution.

This is a proposal-level accounting defect, rather than an implementation detail: the proposed finite resource contract must identify what it bounds before preparation approval.

**Exact minimal revision:** Explicitly select one combined executable per required clean build profile, retaining existing thresholds, and correct the specification as follows:

- State that the one-owner/no-copy rule applies separately to each Pattern; there is one lifecycle-local Pattern and the unchanged persistent consumer Pattern.
- Label the existing 11 Compile calls, ten nonempty calls and 20 allocation operations as **lifecycle-only**.
- Add consumer elaboration: one additional nonempty Compile, two additional allocations and two persistent designated heap blocks.
- For these two Pattern sources together, state **12 Compile calls, 11 nonempty calls, 22 allocation operations, at most two simultaneously live Pattern objects and four designated heap blocks**, on normal completion.
- State their combined maximum live designated payload as **12 Character units plus 14 Offset units**, excluding allocator overhead. Account separately for both Pattern records, temporary Compile arrays, buffers, cursors and other library/runtime allocations. This is symbolic source accounting, not a whole-executable byte bound.
- Require lifecycle deallocation evidence to return to the **post-elaboration baseline**; do not claim the persistent consumer Pattern is freed or that whole-process allocation returns to zero.

Retain the consumer accessibility requirement: caller-owned library-level aliased buffers, `On_Close => null`, proper Box/cursor finalization order, no unchecked-access workaround or suppressed checks. Actual checked execution remains later evidence.

No mandatory textual defect in the three-site canonical naming change was established by this adjudication. Intrinsic lowering, canonical contracts/assertion policy, nulling, pools, actual release behavior, allocation-failure cleanup, semantic equivalence and native resource fit remain **UNPROVEN/UNRUN**.

Smallest sound next step: use D160’s single evidence-driven revision for this correction, retain the immutable initial packet and dissent, then obtain renewed pair/judge review. Any actual derivative/fixture preparation still requires distinct future registration. D158/D159 remain at zero revisions; generator remains UNQUALIFIED; storage remains HUMAN_PAUSED; F7 remains NOT PERFORMED.

All checks were read-only. No native compiler/configuration, network, lock, service, offload or file mutation was performed.