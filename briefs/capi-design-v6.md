You are the independent, different-author design reviewer for: WORLDLINE Phase One C-API boundary consolidation DESIGN v6.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing under
review. Separate gpt-6.1-sol sessions reviewed v1 to v5.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v6/review/gpt61-v1
- Do not import or execute WORLDLINE code (read proof_manifest.py and the design's check sketch as text/AST only; do not execute the
  design's check sketch, even though the author did so in memory). Do not run compilers, provers, builds, tests, systemctl,
  project-vault, restic or any window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd. Never read or
  list anything under ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read any
  review directory still in progress (WT/designs/claude-root-worker-seam-design-v3/review/).
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in groups of at most four); a large concurrent batch stalled a different reviewer's tool layer on 2026-10-05.
- Use JACKAL (MCP) for any derived arithmetic (counts, tallies, append ranges); carry status and non_claims.
- You grant no acceptance. The only output is a design verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-capi-boundary-design-v6/ (verify all five hashes): DESIGN.md
  (cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417), APPENDIX-BINDINGS.md (9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946),
  decisions.json (357bb2d429a7f6e039af53f95ad7a67c58a34587dac55fcdda6fcdacfc828d2b), jackal.json
  (34a7a3ab2c27552e94ce8a114119e4b14988bd03fafe3747b0bc3fec274a94de), AUTHOR-NOTES.md (414fd7363ed415ce5dd5c2f1c675780bb5917e9e9a08bc5ab0751ae48ba2aa08).
  A-COST is not reissued: v4's APPENDIX-COST-MAP.md (5592df3a...) is carried by reference. Self-containment method: v6 binds 5 v5
  DESIGN slices (§B-v6.2) and 14 v5 A-BIND slices (§W.2) by line range and sha256, with quoted line replacements and insertions
  (X-R1..X-R8 in DESIGN, W-A1..W-A20 in A-BIND) and code changes CR1..CR6 to the B8 sketch (§B8.4). Verify every slice and quote you
  rely on.
- v5 and its sealed review (closure targets): WT/designs/claude-capi-boundary-design-v5/ and review/gpt61-v1/{REVIEW.md (73e82489...),
  review.json (800880d4...), checks.json (c1398253...), review-freeze.json (91bddf1a...)} - verdict ENDORSED_WITH_REQUIRED_CHANGES;
  required changes V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE; V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 NOT_CLOSED; L9-L12 GENUINE and
  REPAIRED_AT_DESIGN_LEVEL; 31 rulings. Earlier designs and sealed reviews: WT/designs/claude-capi-boundary-design-v{3,4} and
  W/work/claude-capi-boundary-design-v{1,2}.
- Source: W/work/claude-composition-v5-beta/source (S5), lineage W/work/reviewed-common-proof-source-composition-v4/source.
  Invariants: UNANALYZED_BOUNDARY == {"worldline-c_api"}; MINIMUM_CHECKS 251; REQUIRED_PROVED 535-name ordered prefix, append-only;
  169 effective CONTRACT_PINS keys.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt}; /home/sicarii/Documents/complete-phase1-prompt.txt.
  Never: narrow domains or accepted cases, lower contracts/floors, remove deterministic controls, skip bodies/callers, waive warnings,
  add assumptions, suppress checked assertions, restore Off exemptions, substitute a renamed Boolean for custody/confinement; native:
  no caps, no native failure counted as accepted refusal, no proof-only light library, no suppressed checked Ghost code.
- Supervision rule on approval gates: a brief or review finding is not new authority to add approval gates; reserved decisions are
  material API/ABI/owner-policy, reference/contract redefinition, operator custody, toolchain/runtime/deployment architecture, and
  merge/release/install/sudo/production/PRIME; pinned implementation files need no approval solely for pinning (reviewed deltas plus
  recomputed effective pins per HANDOFF acceptance-sequence item 1).
- Related: the sealed root-worker seam v2 review (WT/designs/claude-root-worker-seam-design-v2/review/gpt61-v1; its N-5 places the
  root-worker draft's renamings inside package body Child_Boundary). v6's L16 adopts that wording correction after the lead relayed
  the parallel lane's NF-5. A root-worker seam v3 is under its own review; note interplay, do not resolve either lane.
- Author process records (model output, recorded as stated): AUTHOR-NOTES.md; WT/deviations/capi-v6-author-process/NOTE.md (in
  particular: the author read the lead session's transcript read-only after a context compaction, an indirect path to summaries of
  other lanes; and it again executed its own B8 sketch in memory, an author self-check that is not evidence). Do not rely on the
  author's simulation results.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. V5-RC4-GATE-EXCEPTION, sub-clause by sub-clause (v6 §A.1 E.1-E.9): is the sole assignment exception now an independent invariant
   checked against the fixed CAPI_WFX_PROTOCOL constant (empty before PK-6b; from PK-6b only key G21c and only the wfx row
   (Finalization_Decide, G21c, O); declared type, region, assignments and test validated against the normative G21c protocol,
   independently of mutable tile/gate entries); are the amendment controls (added, relabelled id/object, moved) and positive controls
   for the unchanged staged tables adequate as specifications; is every gate, branch payload, diagnostic, refusal code, assignment,
   write and accepted case preserved? CLOSED_AT_DESIGN_LEVEL or NOT_CLOSED with the remaining gap.
2. V5-RC4-QUAL-CAPTURE (v6 §A.2 Q.1-Q.11): do (d1)-(d4), applied text-only to the C_API spec, the C_API body and the parent
   specification core/worldline.ads, refuse every potentially capturing library-unit prefix that a with clause mentions, including
   ancestors through a named descendant (Ada RM 10.1.2(6/2,7)), parent-spec declarations and context, subunits/body stubs, and library
   units named like routines; are the scoped exceptions and use-clause inventory unchanged; are the amendment and unchanged-context
   positive controls adequate; is installed name/overload resolution (D-38, the RM readings, child-unit capture) labelled OPEN?
   CLOSED_AT_DESIGN_LEVEL or NOT_CLOSED.
3. V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 overall, and R2_NINE_CONDITIONS / PACKET_PLAN as now mapped (DESIGN §17): closed at design
   level or not, with the gap.
4. Carried items: do the slices verify; are X-R1..X-R8, W-A1..W-A20 and CR1..CR6 exact, correct, justified and the only changes; are
   the 31 rulings, the RC closures and the L9-L12 repairs carried exactly?
5. Latent defects L13-L16 (DESIGN §A.3): genuine? correctly repaired without narrowing? Is L16 a wording correction only, and does
   control MQ24 show the nested-declaration coverage as claimed?
6. Operator items D-13 and N-06 and lead item N-01 as stated; anything mislabelled as lead-decidable or operator-owned; any approval
   gate added without an original basis.
7. Anything else that would weaken a contract, domain, accepted case, floor, control or proof scope, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>",
  "design_sha256":"<sha256 you computed>","decisions_sha256":"<sha256 of decisions.json>","appendix_sha256":{"APPENDIX-BINDINGS.md":"...","APPENDIX-COST-MAP.md (v4, carried)":"..."},
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V5-RC4-GATE-EXCEPTION":"...","V5-RC4-QUAL-CAPTURE":"...",
  "V4-RC4-GATE":"...","V4-RC4-ALIAS":"...","V3-RC4":"..."},"latent_defects":{"L13":"...","L14":"...","L15":"...","L16":"..."},
  "required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],"open_obligations":[...],
  "proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>",
  "checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per required change and per carried RC, the L13-L16 assessment, required changes, rulings, and the
sha256 of each of your four output files.
