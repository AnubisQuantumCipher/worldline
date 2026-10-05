You are the independent, different-author design reviewer for: WORLDLINE Phase One root-worker SEAM DESIGN v6.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You authored nothing under review and are not the
drafting agent. Earlier revisions v1-v5 were reviewed by separate sessions.

HARD LIMITS
- Passive reading and hashing only. Do not import or execute any WORLDLINE/COSMOGONY/root-worker code (Python or C); read it as text or
  AST. Do not run compilers, provers, tests, services, systemctl, sudo, namespaces, project-vault or restic; do not touch /srv labs,
  stores, sockets or windows. Do not write SIA notes. Do not modify anything. Never read or list anything under ~/.local/share/sia/.gbrain/;
  never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read any review directory of v6, any gpt61-v* review directory,
  review-records/, or any session transcript. Never start a shell command that waits on stdin.
- Do not stop, kill or interrupt any process. JACKAL (MCP) for any derived arithmetic, sequentially or in groups of at most four, carrying
  status, parsed= and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance; the only output is a design verdict: ENDORSED,
  ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-root-worker-seam-design-v6/ (verify all four hashes): SEAM-DESIGN.md
  (f41566d8bb694817f27efb4dd336d25e554357976808aad577b91365a9a10787), seams.json (a54dc595051b582d8c4a06dca62ad00ca9d728896c063cb2d73e4c01d046ddbe),
  jackal.json (5d6684296284d33d3580e5dc123401b493fdf2431d3d54c57b8b4d98abcc84b0), AUTHOR-NOTES.md
  (95826c1ee59c7ef11cd9cefbcb3e212053d5ecbd05908224ba59572ebf922633). v6 carries v5 as 13 hash-pinned slices (seams.json
  self_containment; the lead verified 13/13) with quoted replacements R6-1..R6-29. It is NOT self-contained (the author's stated reason is
  in AUTHOR-NOTES §6-7); assess whether the composed specification is unambiguous.
- Closure target: v5 (WT/designs/claude-root-worker-seam-design-v5/, SEAM-DESIGN.md 938c832d...) and its sealed independent Claude review
  WT/designs/claude-root-worker-seam-design-v5/review/claude-v1 (REVIEW.md and review.json; read them in full): verdict
  ENDORSED_WITH_REQUIRED_CHANGES with V5-REQ-A..V5-REQ-M, rc/clause/ruling closures and findings NF5-*/RF-*. Everything that review closed
  (V4-REQ-H, V4-REQ-K, the CLOSED_AT_DESIGN_LEVEL clauses, D-2b, the C-API integration) must stay closed. Earlier designs and reviews:
  WT/designs/claude-root-worker-seam-design-v{1,2,3,4}.
- Draft lane (INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY): W/work/protected-original-root-worker-repair-v1 (handoff-to-claude-v1-retry1/
  HANDOFF.md, source/, preimage/, dependency-source/); other cited lanes W/work/resource-child-authority-source-v1,
  W/work/protected-canonical-full-bridge-repair-v2, W/work/claude-root-worker-notes-v1. C-API: WT/designs/claude-capi-boundary-design-v{5,6}
  and their sealed reviews; source composition W/work/claude-composition-v5-beta/source.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json, ALL-ORIGINAL-OBLIGATIONS.md,
  REQUIRED-LIFETIME-CONTROLS.json, ORIGINAL-ORDINARY-ROSTER.json}; /home/sicarii/Documents/complete-phase1-prompt.txt; the human's 2026-10-05
  directives recorded in WT/STATUS.md (routine reversible engineering preserving the original external contract and success domain is the
  lead's; reserved operator decisions are those the rulings name - D-2a, D-2b, D-4a, D-5a/D-5b, D-7a, D-8b, D-9a operator parts, OP-1..OP-9 -
  plus merge/release/install/sudo/production/PRIME; a brief or finding is not new authority to add approval gates; none may be lowered).
  Reviews are by independent Claude review subagents since the 17:05Z direction; no GPT-6.1 gate is claimed.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each of V5-REQ-A..V5-REQ-M and every rc, clause and ruling the v5 review left PARTIALLY_CLOSED or NOT_CLOSED: CLOSED_AT_DESIGN_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; owners and evidence requirements preserved.
2. Carried items: do the 13 slices verify; are R6-1..R6-29 exact quotes of their targets and the only changes; is everything the v5 review
   closed carried unchanged; is the composed specification unambiguous enough to implement and review?
3. The new containment gaps CG-2 (worker-served IP bound), CG-3 (later-WL queueing), CG-4 (owner.retry): are they stated exactly, with
   closure conditions that do not depend on D-4a, and with nothing presented as preserved that is not?
4. Option H′: is the per-request reservation + per-agent child mapping sound against the lane and original source; do its AO marks hold;
   does adopting H′ change any resource-policy field (deciding whether adoption is the lead's engineering call or the operator's D-4a
   selection)? Do not adopt it yourself.
5. V5-REQ-E archive_equal against the actual archive encoding; V5-REQ-F custody-return evidence after a front restart (pidfd_open + start
   tick + fresh exclusive flock) and the OB-ESC obligation; V5-REQ-G Unknown→service; V5-REQ-H PREPARED ordering and phase-conditional
   UNKNOWN; V5-REQ-I the RC-10 dual outcome; V5-REQ-J the pre-unshare factory - sound, complete, preserving?
6. Does anything create a new refusal of an original accepted case, a new cap, a narrowed domain, a retired or weakened control, a changed
   original behaviour, a lead-only acceptance, an added assumption, or an added or lowered approval gate (check K-27/K-28/RC-11 under OP-7)?
7. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-design-review-v1","design":"<absolute path of SEAM-DESIGN.md>","design_sha256":"...","seams_sha256":"...",
"different_from_author":true,"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)",
"reviewer_kind":"claude-subagent","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
"verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V5-REQ-A":"...",...},"clause_closure":{...},
"ruling_closure":{...},"containment_gaps":{"CG-1":"...","CG-2":"...","CG-3":"...","CG-4":"..."},"option_h_prime":"...",
"required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],"open_obligations":[...],
"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false}
