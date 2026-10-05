You are the independent, different-author reviewer for: WORLDLINE Phase One C-API consolidation packet PK-0 REVISION 4
(characterization only), SOURCE REVIEW. The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent (the same agent that
drafted the C-API designs and PK-0 v1). You authored nothing under review and are not the drafting agent. A gpt-6.1-sol session reviewed PK-0 v1; independent Claude review subagents reviewed v2 and v3.

WHAT THIS REVIEW IS AND IS NOT
PK-0 is the first packet of the ENDORSED C-API design (DESIGN v6, sealed review WT/designs/claude-capi-boundary-design-v6/review/gpt61-v1,
verdict ENDORSED). Its stage gate is "baseline run on L0 in an admitted frame" (v3 DESIGN section 9.2). That run is NOT possible now: the
confinement gate (frame v5 UNQUALIFIED; V5-B01/V5-B02 open) blocks it. This review judges the packet SOURCE only: nothing in it has been
executed, and nothing you conclude is run evidence, control evidence or acceptance. The baseline run, its recorded values, the six launch
obligations and any stage qualification remain OPEN.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/capi-pk0-v4/review/claude-v1
- Do NOT run, import or execute the packet's tests or helpers, the S5 producers or fixtures, pytest, any WORLDLINE code, compilers,
  gprbuild, provers, native builds or libraries; read Python as text/AST only. No systemctl, sudo, project-vault, restic or
  window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under
  ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup (the iPad mounts can hang). Do not read
  any review directory of v3, review-records/, any gpt61-v* directory belonging to v2 or v3, drafts in progress
  (WT/designs/*-v7/, WT/designs/claude-native-bigint-d1-design-v5/, WT/designs/claude-f32-resolution-v5/), or any session transcript. Never
  start a shell command that waits on stdin.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls modestly
  (sequentially or in groups of at most four).
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- You grant no acceptance. The only output is a source-review verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Packet under review, in WT/packets/capi-pk0-v4/ (verify all nine hashes): packet.json (721ef6c1c69bf6e866ef4e62a721a78b17332e81ced2d57a2bf337c7f02fc421),
  AUTHOR-NOTES.md (ee3cb8c84ffb967401fe9f48e3f09b97eff3f00cc529377927ca903d9d6d5f06), jackal.json (c3c41a1b581b6557cd718dca1d24b9ed583af88c74e6b7b0ce93b745717aac75),
  and under files/tests/: capi_characterization.json (645a5572d31e354c5c9112e70f17d85eb15fabe3662d6499aa31ca8db5505b1f),
  capi_guard_pages.py (bfac3aa398c490d3de20cc420ba0fea2c01b211e4e20c2a249f69529f6d3727c, unchanged from v2/v3), capi_layout_baseline.json
  (4df25239c3fd173b4076fe34e9f250948f8c92f7068c701c364723ba18294bf0, unchanged), test_capi_characterization.py
  (bc6c03ed358a0a8bc3ff92a86981641f0f90bb4bbf1db6a2d6c96d06441312ed), test_capi_diagnostics.py
  (1cbf5b2481a57b7cd486c7c9a5c1a9ee536e3e6788ec819ac35288061eda4236, unchanged), test_capi_layout_identity.py
  (e19113c3554a0094dc6a0c06919a0e6bbcf367c720cdd98dc374349f8d4b3b3f, unchanged). packet.json binds 100 L0 inputs (lead re-verified all 100)
  and gives a change_list_against_v3.
- Closure targets: PK-0 v3 (WT/packets/capi-pk0-v3/, packet.json 06e87658..., unchanged) and its sealed Claude review
  WT/packets/capi-pk0-v3/review/claude-v1 (REVIEW.md 302a3ddd..., review.json 1a7b8fbb...; read in full): ENDORSED_WITH_REQUIRED_CHANGES with
  RC-v2-2/3/4 CLOSED_IN_SOURCE, RC-v2-1 PARTIALLY_CLOSED, and two new required changes RC-v3-1 (the Kind 1 R.Captured_Results/R.Required
  overlap IS constructible: place the accepted rows in the descriptor's Expected/Observed region at offset 208 which CC:765-776 never read)
  and RC-v3-2 (reachable sub-conjuncts: misalignment, overflow, null+length, invalid cursor span need cases or representative-operand
  entries). Also v1 and v2 and their sealed reviews. Everything those reviews found correct must stay correct.
- Base L0: W/work/claude-composition-v5-beta/source (S5), QUALIFIED_SOURCE_COMPOSITION (its sealed review under
  W/work/claude-composition-v5-beta/review/gpt61-v1).
- The design it implements: PK-0 row (WT/designs/claude-capi-boundary-design-v3/DESIGN.md section 9.2) and the PK-0 specification
  (WT/designs/claude-capi-boundary-design-v4/DESIGN.md section 9.6, carried by v5 and v6); C-API design reviews and rulings in
  WT/designs/claude-capi-boundary-design-v{3,4,5,6}/review/gpt61-v1.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt}; /home/sicarii/Documents/complete-phase1-prompt.txt.
  Never: narrow domains or accepted cases, redefine original behaviour (including defects), count a native failure as an accepted
  refusal, add assumptions, or weaken an expectation so an unrun test is likely to pass.
- Author process records (model output, recorded as stated): AUTHOR-NOTES.md and packet.json "deviations" (five); the lead's record
  WT/deviations/capi-pk0-v2-author-process/NOTE.md (includes the lead's own mistranscription of the v1 review.json hash, which the author
  caught). The author reports a static finding about S5: S5's own unexecuted tests (tests/test_raw_evaluation_default.py:71-89,
  tests/test_finalization_kernel.py:245-263) assert AUTHORIZED for a collapse request with no Resulting_Requirement, which by
  core/worldline-collapse.ads:139-156 and :213-217 can never be Authorized; the new U15y cases set Resulting_Requirement equal to
  Current_Requirement to reach the Authorized path; S5 was not edited.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Packet integrity: identities, the 100 bound inputs, no existing file touched, v1/v2/v3 unchanged, the change_list_against_v3 exact, and the
   invariants (REQUIRED_PROVED 0 appended, length 535; MINIMUM_CHECKS 251; UNANALYZED_BOUNDARY {"worldline-c_api"}; 0 movers; External_Name 31).
   Are all 693 v3 cases and 75 v3 diagnostic cases byte-identical in content and order?
2. Closure of RC-v3-1 and RC-v3-2: CLOSED_IN_SOURCE, PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; RC-v2-2/3/4 still closed.
   For RC-v3-1: the new `embed` mutation (CHAR:1283-1330, dispatched from mutate CHAR:1277-1278) — does it read the region bounds from the
   library (wl_completion_context_layout_v1(1,8) and (1,10)), require them to equal the ctypes offsets, place the accepted rows byte-unchanged,
   re-aim the request field, and raise PlacementError (so a differing measured layout fails visibly, never silently passes)? Are D88/D89 and
   their twins' codes, frontiers and streams correct against CC:777-778? For RC-v3-2: check D76-D87, D90-D91 against the bodies (spot-check at
   least eight: codes, frontiers, twin placement, exact stream); is the representative_operands list sound; are the completeness claims now
   accurate?
3. RC-v2-2/3/4 and the mechanics still hold (readiness probe, bytecode gate, HarnessFaultControl status line); the test_record_shape
   readiness-side check (CHAR:1634-1639); the class-X stride premise statement at REC:391.
4. Faithfulness to ORIGINAL S5 behaviour for the new cases; any class-H code treated as an accepted refusal; any expectation weakened; F32 not
   decided by the packet.
5. Placeholders unchanged, none added, none can pass.
6. Anything else that would weaken a contract, domain, accepted case, fixture, control or proof scope, or add an assumption or approval gate.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-packet-source-review-v1","packet":"<absolute path of packet.json>","packet_sha256":"...","files_sha256":{name:"..."},
"different_from_author":true,"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)",
"reviewer_kind":"claude-subagent","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
"verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"RC-v2-1":"...","RC-v2-2":"...","RC-v2-3":"...","RC-v2-4":"...",
"PK0-RC4":"...","PK0-RC5":"..."},"item_findings":{...},"required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],
"run_evidence":false,"control_evidence":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false}
