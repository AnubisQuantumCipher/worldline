You are the independent, different-author design reviewer for: WORLDLINE Phase One native Big_Integer D1 DESIGN v3.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing
under review. A gpt-6.1-sol session reviewed v1 and v2 separately.

HARD LIMITS
- Passive reading only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1
- Do not run compilers, provers, builds, tests, WORLDLINE code, systemctl, project-vault or restic. Do not write SIA notes. You may
  run short read-only Python snippets for inspection (e.g. reading runtime source text, querying your own interpreter's
  int-digit limit); never import WORLDLINE modules.
- Use JACKAL (MCP) for any derived arithmetic (fixture values, chunk sizes, counts); carry its status class and non_claims.
- You grant no acceptance. The only output is a design verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES, or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow)
- Design under review, in W/work/claude-lead-isolation-v1/wt-1/designs/claude-native-bigint-d1-design-v3/: DESIGN.md (sha256
  b20554c493e8406f0fa7191802294668bf3ae94ab8a65c6a75505b6e405f261f), decisions.json (186c28e150cc2d888f066d0bfffbff7b9b19dcf63df5c66a3e6ffb5161bd33fd),
  APPENDIX-A-python-conversion-surface.md (a8ba784ac4ff3d0797fb3c7b0b2cd67981ca0fa6a0649215b88890c8d71db70a),
  APPENDIX-B-errata-and-refinements.md (e485cfc77acd28f011aa7cb799ec1496c1b6816d1d553bdf1e16264387f17a4c). Verify all four hashes.
  Appendix B states that it governs where it differs from DESIGN.md (errata E-1..E-5 and refinement B.2); assess the design as
  amended by it. (The isolation-worktree location is bookkeeping for a session write guard, not part of the design.)
- v2 and its sealed review (verdict NOT_ENDORSED; required changes V2-RC1..V2-RC6; still-open RC4..RC7; rulings R-A, R-B, R-PREFIX,
  R-WORKSPACE, R-OD1, R-OD2, R-SCOPE; fact corrections F10-F12): W/work/claude-native-bigint-d1-design-v2/{DESIGN.md, decisions.json,
  review/gpt61-v1/{review.json,REVIEW.md,checkpoint-*.json}}. These are the closure targets. v1: W/work/claude-native-bigint-d1-design-v1.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt}; /home/sicarii/Documents/complete-phase1-prompt.txt.
  Native rule: "Resolve the native Big_Integer cost correspondence without adding caps, suppressing assertions or turning required
  successes into refusals"; "Do not add a domain cap, count native failure as an accepted refusal, substitute a proof-only light
  library or suppress checked Ghost code."
- Source: W/work/claude-composition-v5-beta/source (v3 cites it) and W/work/reviewed-common-proof-source-composition-v4/source.
  GNAT runtime sources /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude; installed
  GNATprove documentation under /home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1 (v3 cites an unsupported-construct entry).
- Related analysis (separately under review, static reasoning only): W/work/claude-lead-isolation-v1/wt-1/designs/claude-d2-checked-ghost-inventory-v1
  (checked-build cost hazards). Related operator item R-1 (contracts-recursive/numeric-variant notices on recursive functions).

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each V2-RC1..V2-RC6 and each still-open RC4..RC7: CLOSED (quote the v3 text, as amended by Appendix B) or NOT_CLOSED.
2. Algorithm B as redesigned: the shape contract without a sentinel, Multiply_Add's carry-out overflow detection and its Pre, the
   ghost lockstep Decide_Work with its asserted equivalence on every path, the Prefix Post conjunct and the three internal
   alternatives. Exactly the original decision on every input, with no new refusal, cap or public Pre?
3. Workspace lifetime (V2-RC2): exits X1-X7, the free-and-reraise handler (Appendix B.2 placement under RM 11.6), probes P-W1..P-W8,
   the P-W3 unreachable-handler-warning risk and the fallbacks (stack array; GNAT experimental finally). Is any fallback ineligible
   under the native rule or the strict-warning gate? Is the installed-toolchain unsupported-construct finding correctly applied?
4. OD-1 and OD-2 as operator packages: complete options, consequences and evidence per the v2 rulings; nothing selected; no cap or
   refusal presented as a repair. Appendix A's site inventory and E2's 640-digit chunk validity under every admitted limit (JACKAL).
5. Fixtures and coverage map (V2-RC5): reference-evaluated values for RL-1/2/3, RL-12/RL-12N, RL-14/RL-14P and the new RL-4..RL-23,
   IM, PY and workspace-lifetime controls.
6. The R-1 dependency (one new recursive Side_Sum adding a notice site; the notice-free alternative at higher checked cost) and the
   D2 statements (§9.3): correctly scoped and carried as OPEN?
7. Anything that would weaken a contract, domain, accepted case, control or proof floor, add an assumption, count a resource
   failure as a refusal, or suppress checked Ghost code.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>",
  "design_sha256":"<sha256 you computed>","decisions_sha256":"<sha256 you computed>","appendix_sha256":{"A":"...","B":"..."},
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","prior_closure":{"V2-RC1":"...",...,"RC7":"..."},
  "required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],
  "fact_corrections":[...],"open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per item, required changes, rulings, and the sha256 of each of your four output files.
