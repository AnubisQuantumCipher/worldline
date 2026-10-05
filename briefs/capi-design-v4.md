You are the independent, different-author design reviewer for: WORLDLINE Phase One C-API boundary consolidation DESIGN v4.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing under
review. Separate gpt-6.1-sol sessions reviewed v1, v2 and v3.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4/review/gpt61-v1
- Do not import or execute WORLDLINE code (read proof_manifest.py and any check sketches as text/AST only; do not execute the
  design's check sketches). Do not run compilers, provers, builds, tests, systemctl, project-vault, restic or any window/reservation
  action. Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under
  ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in small groups); a large concurrent batch stalled a different reviewer's tool layer today.
- Use JACKAL (MCP) for any derived arithmetic (counts, tallies, append ranges); carry status and non_claims.
- You grant no acceptance. The only output is a design verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-capi-boundary-design-v4/ (verify all six hashes): DESIGN.md
  (a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6), decisions.json (59e71dd68724b0420b670d79a99ea74194134dbc6d219b7b91f146ad01843625),
  APPENDIX-BINDINGS.md (39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626), APPENDIX-COST-MAP.md
  (5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4), jackal.json (dec64a324685496195a7cb1c48e9ee3cf168255f8a1214d62b9491e42653f39d),
  AUTHOR-NOTES.md (ccac4f63a00ed36199642b8691535890719879187b135ecce69f67edc5214b07).
  Self-containment method: v4 binds carried v3 text by line range plus the sha256 of each slice (31 slices, DESIGN §B.2) and
  quotes 15 replaced v3 lines verbatim with their replacements (§B.4). Verify every slice hash against v3 and read the bound v3
  text where you rely on it.
- v3 and its sealed review (closure targets): WT/designs/claude-capi-boundary-design-v3/{DESIGN.md, decisions.json,
  APPENDIX-BINDINGS.md, APPENDIX-COST-MAP.md} and review/gpt61-v1/{REVIEW.md, review.json, checks.json} - verdict
  ENDORSED_WITH_REQUIRED_CHANGES; RC1-RC3 CLOSED_AT_DESIGN_LEVEL; V3-RC4, V3-RC5, V3-RC6 NOT_CLOSED; rulings LD1..LD6, LD4-R, D-13,
  N-06, N-01, D-05, D-18, D-19, D-28, D-36, D-15/D-34/D-38, N-03, N-04, N-05, N-07, R2_NINE_CONDITIONS, APPENDIX_C, PACKET_PLAN.
  v2 and v1 with their reviews under W/work/claude-capi-boundary-design-v{1,2}.
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
- Related: root-worker seam design v1 and its sealed review (WT/designs/claude-root-worker-seam-design-v1); the unreviewed
  root-worker draft edits core/worldline-c_api.adb (v4 DESIGN §19 notes rename-capture hazards) - note, do not resolve. The author
  reports latent defects L1-L8 (DESIGN §A.4), four of them in v3. Author process records: WT/deviations/capi-v4-author-taskstop/NOTE.md.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each of V3-RC4 (with its sub-requirements: scoped rename/use inventory; deterministic O6(b)/(c); K3 actual Library_Interface
   membership; provenance/gating for every write form; O4/R-W/B4/B8 alignment), V3-RC5 (PK-0 classification: pre-/post-capture
   frontiers, defined handler mappings and write order, OPEN only where genuinely unresolved, foreign faults separate, C-14 outside
   baseline) and V3-RC6 (cost map corrections): CLOSED_AT_DESIGN_LEVEL or NOT_CLOSED with the remaining gap.
2. Spot-check at least 4 exports' tiles, read frontiers and write rows against S5 (guard order, read staging, write order/
   conditions, exception scope, totality, per-call-site cost statements): does the design preserve every accepted case, refusal
   code and order; are cost statements resolved and correctly labelled source versus native?
3. Carried items: are RC1-RC3, LD4-R, the closed/conditional rulings and APPENDIX_C ordering preserved exactly (slice hashes
   verify; replacements correct and justified)? Are L1-L8 genuine and correctly repaired?
4. Operator items D-13 and N-06 and lead item N-01 as now stated; anything mislabelled as lead-decidable or operator-owned; any
   approval gate added without an original basis.
5. Anything else that would weaken a contract, domain, accepted case, floor, control or proof scope, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>",
  "design_sha256":"<sha256 you computed>","decisions_sha256":"<sha256 of decisions.json>","appendix_sha256":{"APPENDIX-BINDINGS.md":"...","APPENDIX-COST-MAP.md":"..."},
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V3-RC4":"...","V3-RC5":"...","V3-RC6":"..."},
  "latent_defects":{"L1":"...",...},"required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],
  "open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per required change, L1-L8 assessment, required changes, rulings, and the sha256 of each of
your four output files.
