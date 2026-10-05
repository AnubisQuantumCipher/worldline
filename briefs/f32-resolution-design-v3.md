You are the independent, different-author design reviewer for: WORLDLINE Phase One F32-CONFLICT RESOLUTION DESIGN v3. The author is
the Claude Code lead (claude-opus-5-5) through a drafting subagent. You authored nothing under review.

HARD LIMITS
- Passive reading and hashing only. Do not import or execute WORLDLINE/COSMOGONY code, tests, compilers or provers; read Python as text or
  AST only. No sudo, systemctl, project-vault or restic. GIT_OPTIONAL_LOCKS=0 for any read-only git. Do not write SIA notes or modify
  anything. Never read or list ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read
  any session transcript or rollout, or any review directory in progress (any review directory in progress, WT/proposal/v8-review, any gpt61-v2,
  review-records/). Do not stop or interrupt any process. JACKAL (MCP) for any derived number, sequentially, carrying status, parsed= and
  non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance; the only output is a design verdict: ENDORSED,
  ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review, in WT/designs/claude-f32-resolution-v3/ (verify hashes): DESIGN.md
  (37879bc8eef800607b26b5d9eac2fd91c7b3d43ec8edd246849e500b6f58ea5e), evidence.json
  (d193351cee6f40b4fd22405caa453065cf4f5c2a7ff1ed60b19de513f8a5f0ce), jackal.json
  (a6b3b722b91b3fd9811fa24f11d3571479b43abda4fa985db2cb61d0dd4278de), f32-r-a.patch
  (226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650, byte-identical to v1's and v2's).
- Closure targets: v2 (WT/designs/claude-f32-resolution-v2/) and its sealed Claude review WT/designs/claude-f32-resolution-v2/review/claude-v1
  (REVIEW.md 86569100..., review.json b8b27d23...): ENDORSED_WITH_REQUIRED_CHANGES with RC-1, RC-2, RC-4 CLOSED, RC-3 closed in substance,
  new RC-5, and non-blocking notes 1-6. Also v1 and its sealed review (WT/designs/claude-f32-resolution-v1/review/claude-v1). Everything
  those reviews confirmed must stay correct. You may read both sealed reviews. The patch's preimage equals S5's two test files (lead-verified by cmp).
- The finding it resolves: WT/investigations/f32-resulting-requirement/FINDINGS.md (static; a different subagent). Source S5 =
  W/work/claude-composition-v5-beta/source. Item1 lineage: /home/sicarii/Work/ada-spark-readiness-20260927/codex-continuation-20260930/
  phase1-finalization-owned-acquisition-engineering-v1 (source/, authority-item1-priority-v1/, -v2/) and W/work/item1-repair.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json (OB-003),
  ALL-ORIGINAL-OBLIGATIONS.md, REQUIRED-LIFETIME-CONTROLS.json, ORIGINAL-ORDINARY-ROSTER.json}; /home/sicarii/Documents/complete-phase1-prompt.txt;
  the human's 2026-10-05 delegation (WT/STATUS.md, "Full human directive"): routine reversible engineering preserving the original external
  contract and success domain is the lead's; incompatible API/contract redefinition, merge/release/install/sudo/production/PRIME are
  reserved. A brief or finding is not authority to add approval gates.
- Since 2026-10-05 ~17:05Z the human moved reviews to independent Claude review subagents (WT/STATUS.md); the original GPT-6.1 text is
  recorded there and no GPT-6.1 gate is claimed.

WHAT TO DECIDE (answer each with file:line evidence)
0. Closure of RC-5 and of non-blocking notes 1-6 (CLOSED / PARTIALLY_CLOSED / NOT_CLOSED with the gap); RC-1..RC-4 still closed; anything else changed versus v2.
1. Is F32 correctly characterized: AUTHORIZED unreachable for the four controls on S5; the cause (item1 V2 fixture change not propagated to
   candidate helpers); is OB-003's own acceptance ("the 1.9.1 control is AUTHORIZED") correctly read as requiring the positive case?
2. Original intent: is the design's account of what "original fixture" means for the candidate helpers versus checkpoint() supported by the
   pre-item1, V1 and V2 bytes and handoffs?
3. R-A: does the exact patch preserve every assertion, the kernel, wire, ABI, contract, checkpoint() and every accepted case; does it
   weaken or narrow anything; is the 35-field equivalence with the V1-updated literal (raw :473-481) correct; are there other callers of
   the two helpers or other controls that change meaning? Is the extra dependent assertion (row projection :97-99) handled?
4. Rejected options: is each rejection sound; is any non-weakening option missed?
5. Authority: is R-A within the lead's delegated authority rather than a reserved decision? Is any gate added or lowered?
6. Closure plan: are the required matching-source runs, lifetime controls, OB-003 neighbours, full roster and strict proof complete; is the
   re-binding of frozen lanes (PK-0 v2 packet.json, D1 v4 DESIGN.md) handled without in-place edits; does anything remain open?
7. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, or add an assumption.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json schema:
{"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>","design_sha256":"...","patch_sha256":"...","rc_closure":{"RC-1":"...","RC-2":"...","RC-3":"...","RC-4":"...","RC-5":"..."},
"different_from_author":true,"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)",
"reviewer_kind":"claude-subagent","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
"verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","item_findings":{...},"required_changes":[{"id","change","reason","evidence"}],
"open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false}
