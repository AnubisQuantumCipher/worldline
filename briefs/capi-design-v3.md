You are the independent, different-author design reviewer for: WORLDLINE Phase One C-API boundary consolidation DESIGN v3.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing
under review. You (a gpt-6.1-sol session) reviewed v1 and v2 in separate sessions.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v3/review/gpt61-v1
- Do not import or execute WORLDLINE code (read proof_manifest.py as text/AST). Do not run compilers, provers, builds, tests,
  systemctl, project-vault, restic or any window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd.
- Use JACKAL (MCP) for any derived arithmetic (symbol/name/unit counts, pin key counts, append ranges); carry status and non_claims.
- You grant no acceptance. The only output is a design verdict.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow)
- Design under review, in W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v3/:
  DESIGN.md (sha256 a8a120c9a704177cdab5232a757f1ef405cb3ad1c694ff135cdd2e8f26a14aa7), decisions.json (2517dd49f6b96e4fe23cd9631aead320ac038605b7286fe8fc5b72c92d99813a),
  APPENDIX-BINDINGS.md (5ffb8736b6ce89f655041129991ed0bce4133941129bc7b1566b0da68695d32e), APPENDIX-COST-MAP.md
  (c2a320a266fdd088c203e0d61f4cd7c5ea94f7b3b731f5be400f6b2f3d5b114f). Verify all four hashes. (It lives in a lead isolation
  worktree because of a session write guard; that is bookkeeping, not part of the design.)
- v2 and its sealed review (verdict ENDORSED_WITH_REQUIRED_CHANGES; RC1-RC6; rulings LD1-LD6, D-13, N-01, N-06, D-05, D-18, D-19,
  D-28, D-36, D-15/D-34/D-38, N-03, N-04, N-05, R2_NINE_CONDITIONS, APPENDIX_C, PACKET_PLAN):
  W/work/claude-capi-boundary-design-v2/{DESIGN.md, decisions.json, units/, review/gpt61-v1/{review.json,REVIEW.md,checkpoint-*.json}}.
  Those required changes and rulings are the closure targets. v1: W/work/claude-capi-boundary-design-v1.
- Source: v3 states it builds from the GPT-6.1-qualified composition W/work/claude-composition-v5-beta/source (lineage over
  W/work/reviewed-common-proof-source-composition-v4/source). Invariants: UNANALYZED_BOUNDARY == {"worldline-c_api"};
  MINIMUM_CHECKS 251; REQUIRED_PROVED 535-name ordered prefix, append-only.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt}; /home/sicarii/Documents/complete-phase1-prompt.txt.
  Never: narrow domains or accepted cases, lower contracts/floors, remove deterministic controls, skip bodies/callers, waive
  warnings, add assumptions, suppress checked assertions, restore Off exemptions, substitute a renamed Boolean for custody/confinement;
  native: no caps, no native failure counted as accepted refusal, no proof-only light library, no suppressed checked Ghost code.
- F10K diagnostic data: W/work/claude-lead-v2/executions/f10k-retry1/{diagnostic-map-v1.json,strict-report-analysis-v1.json}.
- Related: a root-worker seam analysis (W/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1) reports
  that the unreviewed root-worker draft lane grows worldline-c_api.adb substantially - a potential collision to note, not to resolve.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each v2 RC1-RC6: CLOSED_AT_DESIGN_LEVEL or NOT_CLOSED with the remaining gap. RC1 especially: does LD4-R keep all diagnostic
   state/control/value logic analyzable in SPARK (External abstract state, Atomic access order) and is each transported item T1-T5
   genuinely irreducible?
2. Spot-check at least 3 unit sections and the cost-map appendix against the base source (guard order, read staging, write
   order/conditions, overlap, exception scope, value-routine totality, per-call-site cost claims under RM 6.2): does the design
   preserve every accepted case, refusal code and order, and are cost statements resolved, not assumed?
3. Bindings appendix and RC4/RC5: whole-closure binding, ordered required calls, predecessor manifest edits (exact old/new), identity
   binding per stage, monotonic append schedule consistent with Appendix C, PK-6a enrolment, PK-0 characterization scope, placement of
   representation repairs, seal limits. Sound, enforceable and append-only?
4. Rulings on the operator items D-13 and N-06 as now packaged, and on N-01 (strict obligation; confirming representation clauses as
   reviewed ABI-preserving packets). Is anything mislabelled as lead-decidable or operator-owned?
5. Anything else that would weaken a contract, domain, accepted case, floor, control or proof scope, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>",
  "design_sha256":"<sha256 you computed>","decisions_sha256":"<sha256 of decisions.json>","appendix_sha256":{"APPENDIX-BINDINGS.md":"...","APPENDIX-COST-MAP.md":"..."},
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"RC1":"...",...,"RC6":"..."},
  "required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],
  "open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, RC1-RC6 closure, required changes, rulings, and the sha256 of each of your four output files.
