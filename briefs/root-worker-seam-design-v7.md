You are the independent, different-author design reviewer for: WORLDLINE Phase One root-worker SEAM DESIGN v7.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You authored nothing under review and are not the
drafting agent. Earlier revisions v1-v6 were reviewed by separate sessions (v5 and v6 by independent Claude review subagents).

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
- Design under review, in WT/designs/claude-root-worker-seam-design-v7/ (verify all four hashes): SEAM-DESIGN.md
  (62b7d5877a4df95b86ab5354d64d4fadd6bcf8017da20b8ba53dbbec34169f16), seams.json (de716b0bf38671abef088957014885ecd1002380b8eb56f5966230cd1ba2e817),
  jackal.json (f691a36b3a9efbd49e6d56ad2c264f85b0b83f17ab64ef1fd58db698f181263f), AUTHOR-NOTES.md
  (b651f5e61fe3deca19e6bed1753bb83e7b93d059cc39a2fbc1ea1768968e9da6). v7 is its own text plus 14 hash-pinned slices of v6
  (seams.json self_containment; the lead verified 14/14 and the v6 base hash) with quoted replacements R7-1..R7-86. Assess whether the
  composed specification is unambiguous. CAPI5R/CAPI6R hashes in Appendix B are carried from v4 (deviation 6), not recomputed, because
  they sit in gpt61-v1 directories; you need not read those directories.
- Closure target: v6 (WT/designs/claude-root-worker-seam-design-v6/, SEAM-DESIGN.md f41566d8...) and its sealed independent Claude review
  WT/designs/claude-root-worker-seam-design-v6/review/claude-v1 (REVIEW.md and review.json; read them in full): verdict
  ENDORSED_WITH_REQUIRED_CHANGES with V6-REQ-A..V6-REQ-L and the rc/clause/ruling closures and findings. Everything that review closed
  (V5-REQ-B/H/L/M, V4-REQ-H, V4-REQ-K, the CLOSED_AT_DESIGN_LEVEL clauses, D-2b, the C-API integration) must stay closed. Earlier designs
  and reviews: WT/designs/claude-root-worker-seam-design-v{1,2,3,4,5}.
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
1. For each of V6-REQ-A..V6-REQ-L and every rc, clause and ruling the v6 review left PARTIALLY_CLOSED or NOT_CLOSED: CLOSED_AT_DESIGN_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; owners and evidence requirements preserved; everything the v6 review closed stays closed.
2. Carried items: do the 14 slices verify; are R7-1..R7-86 exact quotes of their targets, none replaced twice and none already replaced by an
   earlier version; is the composed specification unambiguous; is the ~50-line stale-text sweep (AUTHOR-NOTES §2) complete — search for any
   remaining carried line that a v2..v7 change makes stale or contradictory (D-4a dependence, pidfd-only evidence, withdrawn conventions,
   RC-10 naming, alias rules, history-only references used normatively)?
3. The NEW design elements, scrutinized against the lane source and original behaviour: V7-H's router reconstruction-task wait (replacing :192);
   V7-I's PEER_STATUS/PEER_HELD/PEER_LOST_WITH_FRONT reattach protocol and per-request sequence numbers; V7-J's factory fork point
   (C1:308-322, keeping only fds 0/1/2 + its socketpair end); V7-K's D-H7 LAUNCH_REQUEST_ROOT helper and CJ-H-5 (agents nested in the request
   root). Are they sound, complete, and preserving; do they introduce a new refusal, cap, narrowed domain, changed behaviour or assumption?
4. V7-D dispatcher: the result set restricted to stopped/failure/success/None; OOM via memory.events telemetry; the four OPEN persisted-field
   differences (source, supervisionEvidence, events, launcherStderr) — nothing classifies on them?
5. V7-E JsonInput Canonical/Lenient per call site (incl. the corrected protected_startup.py:682/:706 lenient); both refusal tables; CJ-JSON
   per mode so SOURCE_JSON_NATIVE_DISAGREES cannot fire for a Python-accepted input.
6. H' / option K: is adoption correctly NOT taken (CJ-H-1/2/5 open) and correctly left to D-4a (OP-3) if those fail; are all 10 resource-policy
   fields shown unchanged; AO-5/AO-9 "part"?
7. V7-F custody-return (worker-gone/E-CR evidence, pid-pidfd pairing, boot identity K-29 under OP-7); V7-G non-circular C-APPEND and the cause
   as an X-5 operand (04.3/12.1 stay closed); V7-C CG-4 and the swept D-4a lines; V7-L Appendix B identity binding and the RC-13/14/15 rename.
8. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, or add/lower an approval gate.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-design-review-v1","design":"<absolute path of SEAM-DESIGN.md>","design_sha256":"...","seams_sha256":"...",
"different_from_author":true,"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)",
"reviewer_kind":"claude-subagent","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
"verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V5-REQ-A":"...",...},"clause_closure":{...},
"ruling_closure":{...},"containment_gaps":{"CG-1":"...","CG-2":"...","CG-3":"...","CG-4":"..."},"option_h_prime":"...","new_elements_assessment":"...",
"required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],"open_obligations":[...],
"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false}
