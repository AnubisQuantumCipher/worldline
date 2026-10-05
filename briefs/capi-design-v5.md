You are the independent, different-author design reviewer for: WORLDLINE Phase One C-API boundary consolidation DESIGN v5.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing under
review. Separate gpt-6.1-sol sessions reviewed v1, v2, v3 and v4.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5/review/gpt61-v1
- Do not import or execute WORLDLINE code (read proof_manifest.py and the design's check sketch as text/AST only; do not execute the
  design's check sketch, even though the author did so in memory). Do not run compilers, provers, builds, tests, systemctl,
  project-vault, restic or any window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd. Never read or
  list anything under ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup (the iPad mounts are
  offline and can hang). Do not read another review that is still in progress (WT/designs/claude-root-worker-seam-design-v2/review/).
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in small groups); a large concurrent batch stalled a different reviewer's tool layer on 2026-10-05.
- Use JACKAL (MCP) for any derived arithmetic (counts, tallies, append ranges); carry status and non_claims.
- You grant no acceptance. The only output is a design verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-capi-boundary-design-v5/ (verify all five hashes): DESIGN.md
  (533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de), decisions.json (a069632a035b62f18d886112763472f13040779d2d5dd79c872a6d6ce951c55b),
  APPENDIX-BINDINGS.md (f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2), jackal.json
  (612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4), AUTHOR-NOTES.md (ed45d1db766f3b03ec946946942a571ae50b0eae21e339c5724b5e2480280e47).
  A-COST is not reissued: v5 carries v4's APPENDIX-COST-MAP.md unchanged by reference (5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4).
  Self-containment method: v5 DESIGN binds 20 v4 DESIGN line ranges by sha256 (§B-v5.2) and quotes 9 replaced lines with their
  replacements (V-R1..V-R9, §B-v5.4; V-R9 replaces the effective v3:1931 line that v4 carries); A-BIND v5 binds 13 v4 A-BIND ranges
  (§V.2), two quoted line replacements (A-R1, A-R2, §V.3) and eight code replacements to the B8 sketch (BR1..BR8, §B8.1). Verify every
  slice hash against v4 and read the bound v4 (and v3) text where you rely on it.
- v4 and its sealed review (closure targets): WT/designs/claude-capi-boundary-design-v4/{DESIGN.md (a9b5dcce...), decisions.json,
  APPENDIX-BINDINGS.md (39ca9959...), APPENDIX-COST-MAP.md, jackal.json, AUTHOR-NOTES.md} and review/gpt61-v1/{REVIEW.md (3d1ef7f8...),
  review.json (d7bf825a...), checks.json (d70fe467...), review-freeze.json (f1dcb0a7...)} - verdict ENDORSED_WITH_REQUIRED_CHANGES;
  V3-RC5, V3-RC6 CLOSED_AT_DESIGN_LEVEL; V3-RC4 NOT_CLOSED; required changes V4-RC4-GATE and V4-RC4-ALIAS (quoted in v5 DESIGN §A);
  latent defects L1-L8 ruled GENUINE; rulings RC1-RC3, LD1..LD6, LD4-R, D-13 (with its clarification), N-06, N-01, D-05, D-18, D-19,
  D-28, D-36, D-15/D-34/D-38, N-03..N-07, R2_NINE_CONDITIONS, APPENDIX_C, PACKET_PLAN. v3 with its review under
  WT/designs/claude-capi-boundary-design-v3; v2 and v1 with their reviews under W/work/claude-capi-boundary-design-v{1,2}.
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
- Related: root-worker seam design v2 (WT/designs/claude-root-worker-seam-design-v2/SEAM-DESIGN.md, sha256
  db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5); its §14 designs the shared core/worldline-c_api.adb integration
  (H1-H8, R-RW-1..10, ordering O1, checks IC-1..IC-10) and its own review is in progress elsewhere. v5 §19 adds that R-QUAL fails
  closed on the root-worker draft and that a rebase needs re-observed, reviewed tables. Note interplay; do not resolve either lane.
- Author process records (model output, recorded as stated): AUTHOR-NOTES.md §4-§5; WT/deviations/capi-v5-author-process/NOTE.md
  (a read-only command prefixed by a `mkdir -p /dev/null` slip; Bash commands outside the literal list; a late sia.ask; and the
  author's in-memory execution of its own B8 sketch, judged by the lead as an author self-check, not evidence and not a control run);
  WT/deviations/capi-v4-author-taskstop/NOTE.md (the v4 TaskStop event). Do not rely on the author's simulation results.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. V4-RC4-GATE, sub-requirement by sub-requirement: is the gate rule now stated once and identically in normative B0.7, DESIGN §8.4
   (V-R4, V-R5), the B4 tiles, the B8 gate algorithm (BR3, BR4, BR7), the B10.3 gate rows, the B11 promises, the B12 mutation
   specifications and decisions.json; does the branch-sensitive rule permit G16a's existing False-variant rejection diagnostic
   (FA.Rejected_Position) inside its rejection branch and only there; is the sole WF-X finalization O exception (G21c,
   CAPI_GATE_EXCLUSIVE) stated with exact exclusive assignments before its test and nothing else assigned, passed whole or renamed;
   are A1 (RR-V4 must enforce A1's unchanged text, not reinterpret it), diagnostics, codes, write order and the accepted domain
   preserved? Spot-check at least G16a, G16b, G21c and two further gate rows against the B4 tiles and S5. CLOSED_AT_DESIGN_LEVEL
   or NOT_CLOSED with the remaining gap.
2. V4-RC4-ALIAS: does R-QUAL ((a) exact per-scope CAPI_QUALIFIED multisets with the nine scoped CAPI_QUALIFIER_EXCEPTIONS; (b) no
   selection from a non-name prefix; (c) no attribute of a full expanded name; (d) no capture of a full expanded name's first
   identifier by a declaration or through a with clause) give a deterministic, text-only, exact per-call expanded-qualifier
   invariant that refuses every indirect denotation path admitted by the scoped inventory, including F.P.Decide and paths through
   the transport package qualifier, C_API-qualified paths, parent shortenings, library-unit paths and Standard. prefixes? Check each
   exception denotes what is claimed; check the 80-path inventory (B9.4.5) against S5's visible renamings; consider use-visibility
   through the permitted use clauses (R-INV (vii), A-R2), subprogram renaming declarations, renaming-as-body, generic
   instantiation, overloading/homographs and child-unit capture. Are the matching mutation controls (MQ1-MQ14, MV1-MV4, MA1, the L9
   positive control) adequate as specifications? Is V7/O6(a) unweakened and the scoped inventory unrelaxed? Is everything that
   needs installed name resolution (D-38, the RM 8.4 readings) labelled OPEN? CLOSED_AT_DESIGN_LEVEL or NOT_CLOSED.
3. V3-RC4 overall, and R2_NINE_CONDITIONS / PACKET_PLAN as now mapped (DESIGN §17): closed at design level or not, with the gap.
4. Carried items: do the 20 + 13 slice hashes verify; are V-R1..V-R9, A-R1, A-R2 and BR1..BR8 exact quotes of their sources,
   correct, justified and the only changes; is everything the v4 review closed, preserved or accepted (RC1-RC3, LD1-LD6, LD4-R,
   L1-L8 repairs, APPENDIX_C ordering, D-13 with its clarification, N-06, N-01 and the others in §B-v5.1) carried exactly?
5. Latent defects L9-L12 (DESIGN §A.3): genuine? correctly repaired? For L9, does staging the removed-routine K. pairs at PK-6b
   remove any refusal of designed text or weaken anything against the original requirements, rather than only stop refusing the
   unchanged S5 residual at PK-1..PK-5? For L11, is the new (vii) whitelist strictly stronger?
6. Operator items D-13 and N-06 and lead item N-01 as now stated; anything mislabelled as lead-decidable or operator-owned; any
   approval gate added without an original basis.
7. Anything else that would weaken a contract, domain, accepted case, floor, control or proof scope, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>",
  "design_sha256":"<sha256 you computed>","decisions_sha256":"<sha256 of decisions.json>","appendix_sha256":{"APPENDIX-BINDINGS.md":"...","APPENDIX-COST-MAP.md (v4, carried)":"..."},
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V4-RC4-GATE":"...","V4-RC4-ALIAS":"...","V3-RC4":"..."},
  "latent_defects":{"L9":"...","L10":"...","L11":"...","L12":"..."},"required_changes":[{"id","change","reason","evidence"}],
  "rulings":[{"id","ruling","owner","evidence_required"}],"open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,
  "source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per required change and V3-RC4, the L9-L12 assessment, required changes, rulings, and the sha256 of
each of your four output files.
