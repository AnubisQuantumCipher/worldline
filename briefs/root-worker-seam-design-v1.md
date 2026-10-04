You are the independent, different-author design reviewer for: WORLDLINE Phase One root-worker SEAM DESIGN v1.
The author is the Claude Code lead (claude-opus-5-5), through an analysis subagent. You are actual gpt-6.1-sol and authored nothing
under review. (The draft lane it analyzes was authored by a different gpt-6.1-sol session; you review the Claude design, not that
lane's acceptance.)

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/review/gpt61-v1
- Do not import or execute any WORLDLINE/COSMOGONY/root-worker code (Python or C); read it as text or AST. Do not run compilers,
  provers, tests, services, systemctl, sudo, namespaces, project-vault, restic, or touch /srv labs, stores, sockets or windows.
  Do not write SIA notes. Do not modify anything outside your cwd.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance; the only output is a design verdict.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow)
- Design under review: W/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/{SEAM-DESIGN.md (sha256
  531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46), seams.json (sha256
  b8fa87fb573596de9fa0a789b7a8c93c909eeeb18f4d192edad73e038a2caf5d)}. Verify both hashes.
- Draft lane analyzed (status INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY): W/work/protected-original-root-worker-repair-v1
  (handoff-to-claude-v1-retry1/HANDOFF.md with its ten blockers; source/, preimage/, dependency-source/, inventories, deltas).
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json,
  ALL-ORIGINAL-OBLIGATIONS.md, REQUIRED-LIFETIME-CONTROLS.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Related: the C-API boundary design lineage (W/work/claude-capi-boundary-design-v2 and its review; v3 is being drafted) - the
  seam design reports a worldline-c_api.adb growth collision with it.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Verify the design's factual findings against the lane source: the claimed non-reentrant gate mutex deadlock
   (protected_scoped_resource_runtime.py:385/388/357 with dependency-source/lab/intent_gate.py:371), the stale protected_operations.py
   contract pin and pin counts, the duplicate attach_scoped_resource definitions, the three checks missing from the root route,
   the RootController expected_* self-comparison (OB-030), the undefined scoped historical-settlement adapters, the SO_PEERCRED PID
   namespace concern, and the lane's relation to commonV4 and to worldline-c_api.adb. Correct anything wrong; say which are
   reasoning-only (e.g. kernel behavior).
2. For each of the ten seams: is the stated original requirement accurate and complete, is the design direction requirement-
   preserving (no flattened scoped state, no initialized missing state, no settlement on EOF/handler return, no caps, no
   failures counted as refusals, no trusted labels), and are the dependencies and operator-gated items correctly identified?
3. The recommended first slices SL-0 (lock discipline, single attach, pin plan) and SL-1 (spec-only additive
   Worldline.Scoped_Canonical_Operation with Decide/Post => Reference, literal clauses, scoped resource clause, a proof-only
   equivalence lemma to Canonical_Operation.Reference on single-frame inputs): are they sound, independently reviewable, and
   free of any weakening? Is the equivalence lemma statable without changing the original references?
4. The operator-gated list and the dependency on paused lab infrastructure: complete and accurate? Anything that the design
   presents as lead-only that actually needs operator authority, or vice versa?
5. Anything that would weaken a contract, domain, accepted case, fixture, control or proof floor, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of SEAM-DESIGN.md>",
  "design_sha256":"<sha256 you computed>","decisions_sha256":"<sha256 of seams.json>","different_from_author":true,
  "actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (analysis subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","fact_checks":[{"id","claim","status","evidence"}],
  "required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],
  "open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, fact-check results, required changes, rulings, and the sha256 of each of your four output files.
