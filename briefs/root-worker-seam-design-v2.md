You are the independent, different-author design reviewer for: WORLDLINE Phase One root-worker SEAM DESIGN v2.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing under
review. A separate gpt-6.1-sol session reviewed v1. (The draft lane the design analyzes was authored by a different gpt-6.1-sol session;
you review the Claude design, not that lane's acceptance.)

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/review/gpt61-v1
- Do not import or execute any WORLDLINE/COSMOGONY/root-worker code (Python or C); read it as text or AST. Do not run compilers,
  provers, tests, services, systemctl, sudo, namespaces, project-vault or restic; do not touch /srv labs, stores, sockets or windows.
  Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under ~/.local/share/sia/.gbrain/;
  never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup (the iPad mounts are currently offline and can hang).
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in small groups); a large concurrent batch stalled a different reviewer's tool layer today.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance; the only output is a design verdict: ENDORSED,
  ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-root-worker-seam-design-v2/ (verify all four hashes): SEAM-DESIGN.md
  (db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5), seams.json (65a8c73028ad1cb22550bf26ffb3d0027ce125c3ac4b29b64def7765a83415c4),
  jackal.json (fe664cc888e348292b6e3cd28c37f89a6e4dfb7ea2e843f94253595dda4a7561), AUTHOR-NOTES.md
  (782379cd1944dc03e59ec7f50eb4aae70bfbdf69c164e9167817b80883652990). v2 binds 22 v1 slices by line range and sha256 (with replacements
  R-1..R-4) and 92 input hashes in its Appendix B; verify the slices you rely on.
- v1 and its sealed review (closure targets): WT/designs/claude-root-worker-seam-design-v1/{SEAM-DESIGN.md, seams.json} and
  review/gpt61-v1/{REVIEW.md, review.json, checks.json} - verdict ENDORSED_WITH_REQUIRED_CHANGES; RC-01..RC-12; rulings D-1a, D-1b, D-2a,
  D-2b, D-3a, D-4a, D-5a, D-5b, D-6a, D-7a, D-8a, D-8b, D-9a (owners and evidence required in review.json).
- Draft lane (status INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY): W/work/protected-original-root-worker-repair-v1 (handoff-to-claude-v1-retry1/
  HANDOFF.md, source/, preimage/, dependency-source/); other lanes v2 cites: W/work/resource-child-authority-source-v1,
  W/work/protected-canonical-full-bridge-repair-v2, W/work/claude-root-worker-notes-v1.
- Related: C-API boundary DESIGN v4 and its sealed review (WT/designs/claude-capi-boundary-design-v4, review/gpt61-v1: ENDORSED_WITH_REQUIRED_CHANGES;
  V4-RC4-GATE, V4-RC4-ALIAS open; a v5 is being drafted) - v2 §14 designs the shared core/worldline-c_api.adb integration (H1-H8,
  R-RW-1..10, ordering O1, checks IC-1..IC-10). Qualified source composition: W/work/claude-composition-v5-beta/source.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json, ALL-ORIGINAL-OBLIGATIONS.md,
  REQUIRED-LIFETIME-CONTROLS.json, ORIGINAL-ORDINARY-ROSTER.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule on approval gates: reserved operator decisions are those the v1 rulings name (D-2a provisioning/installation, D-2b
  frontier re-enrollment adjudication, D-4a resource policy, D-5a/D-5b delegation and privileged lab/install, D-7a original API/owner
  policy, D-8b kernel measurement, D-9a fault campaign) plus merge/release/install/sudo/production/PRIME; a brief or finding is not new
  authority to add approval gates; do not lower any reserved one.
- The author reports new static observations N-1..N-10 (notably N-6: almost every scoped principal entry re-acquires the non-reentrant
  gate.mutex on its own thread, so fixing the known deadlock alone unblocks none of those paths; and the A1-origin files involved),
  unresolved items (SEAM-DESIGN §18, AUTHOR-NOTES §2, including RQ-1: a FRESH refusal could be a forbidden new refusal if context
  rollover between reserve and pre-effect is an original accepted case), and disclosed process deviations (AUTHOR-NOTES).

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each of RC-01..RC-12 (with their clauses) and each ruling D-1a..D-9a: CLOSED_AT_DESIGN_LEVEL, PARTIALLY_CLOSED or NOT_CLOSED,
   with the remaining gap; owners and evidence requirements preserved?
2. Verify the carried draft-lane defects (DF-1..DF-6) and the new observations N-1..N-10 against the lane source (static); in
   particular N-6's call-site receiver analysis and its consequence for the deadlock fix.
3. Does anything create a new refusal of an original accepted case, a new cap, a narrowed domain, a retired control (including the v1
   frontier control) or a lead-only acceptance? Assess RQ-1 explicitly.
4. The C-API v4 integration (§14): are the rename-capture hazards and ordering rules sound and complete against C-API v4 and its review,
   without deciding either lane's acceptance?
5. Operator items OP-1..OP-9: exactly the reserved decisions, nothing added, nothing lowered?
6. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of SEAM-DESIGN.md>",
  "design_sha256":"<sha256 you computed>","seams_sha256":"<sha256 of seams.json>","different_from_author":true,
  "actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"RC-01":"...",...,"RC-12":"..."},
  "ruling_closure":{"D-1a":"...",...},"findings_assessment":{"N-1":"...",...},"required_changes":[{"id","change","reason","evidence"}],
  "rulings":[{"id","ruling","owner","evidence_required"}],"open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,
  "source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per RC and ruling, the N-1..N-10 assessment, required changes, rulings, and the sha256 of each of
your four output files.
