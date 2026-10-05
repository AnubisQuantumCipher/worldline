# W-1 v11 drafting author: process record (preserved; disclosed)

Fresh Opus 4.8 agent (`a1fa6daf607e569a8`), resumed to fix the three v10-review form defects. v11 is self-contained.

**Lead verified (engineering).** Whole-file sha256 `aac18b67…` matches jackal.json; 576903 bytes. A full scripted parse
of Part V11-MAP: 134 v9-unit rows, partition 100 CARRIED / 23 AMENDED / 11 COMPOSED; 0 hash mismatches, 0 byte-count
mismatches; all 100 CARRIED units byte-identical to v9 (v11 sha256 == v9 sha256). The whole-file hash matches and is
recorded in jackal.json.

**Disclosures (author).**
1. The whole-file self-hash is recorded in jackal.json, not inline (a file cannot contain its own post-assembly hash);
   this also fixes v10's Appendix-I off-by-one-newline self-reference.
2. 4 Part-V11-MAP apparatus headers are excluded from the 136 spec-unit count (stated in §V11-C.1); their identities are
   in jackal.json (so 140 headers, 136 spec units).
3. Fixed en route: a 1-byte transcription error in CARRIED Appendix H (spurious trailing blank line) — now byte-identical
   to v9.
4. Sensitive-area discipline preserved: the async refutation and privilege-boundary/E0 probe PROCEDURES stay
   operator-reserved and OPEN (obligation+predicate only). No obligation/fixture/control/threshold/accepted case/join
   weakened or added. Adoption stays blocked; V5-B01/B02 and the execution-bound items stay OPEN.
5. No execution; Write/Edit only to the two v11 paths; no WebFetch; SIA MCP was down (no note).
