You are the independent, different-author reviewer for: WORLDLINE Phase One C-API consolidation packet PK-0 REVISION 3
(characterization only), SOURCE REVIEW. The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent (the same agent that
drafted the C-API designs and PK-0 v1). You authored nothing under review and are not the drafting agent. A gpt-6.1-sol session reviewed PK-0 v1; an
independent Claude review subagent reviewed PK-0 v2.

WHAT THIS REVIEW IS AND IS NOT
PK-0 is the first packet of the ENDORSED C-API design (DESIGN v6, sealed review WT/designs/claude-capi-boundary-design-v6/review/gpt61-v1,
verdict ENDORSED). Its stage gate is "baseline run on L0 in an admitted frame" (v3 DESIGN section 9.2). That run is NOT possible now: the
confinement gate (frame v5 UNQUALIFIED; V5-B01/V5-B02 open) blocks it. This review judges the packet SOURCE only: nothing in it has been
executed, and nothing you conclude is run evidence, control evidence or acceptance. The baseline run, its recorded values, the six launch
obligations and any stage qualification remain OPEN.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/capi-pk0-v3/review/claude-v1
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
- Packet under review, in WT/packets/capi-pk0-v3/ (verify all nine hashes): packet.json (06e87658058f4f453f575da06a82112fefdf605ce6657549652b74b869dccc0c),
  AUTHOR-NOTES.md (adcd62c686428b3bb66122a2bf7caf4489386e470b89fb80ad82c0b30af56aef), jackal.json (069dccf89a50355b3ea1393697d7230831cbe651ea34daae0ba22e53d5d349dd),
  and under files/tests/: capi_characterization.json (50ecbf029ffdb65b467bed9c125b24a0ed00f26ae025e79da42ee8535227a336),
  capi_guard_pages.py (bfac3aa398c490d3de20cc420ba0fea2c01b211e4e20c2a249f69529f6d3727c), capi_layout_baseline.json
  (4df25239c3fd173b4076fe34e9f250948f8c92f7068c701c364723ba18294bf0, unchanged from v2), test_capi_characterization.py
  (2f8adccb4fa573a3445219d5bd48680e0b365074c6cf12ba33fd4bec2ef343c2), test_capi_diagnostics.py
  (1cbf5b2481a57b7cd486c7c9a5c1a9ee536e3e6788ec819ac35288061eda4236), test_capi_layout_identity.py
  (e19113c3554a0094dc6a0c06919a0e6bbcf367c720cdd98dc374349f8d4b3b3f). packet.json binds 100 L0 inputs (lead re-verified all 100) and
  gives a file-by-file change list against v2.
- Closure targets: PK-0 v2 (WT/packets/capi-pk0-v2/, packet.json c5ce00cd..., unchanged) and its sealed independent Claude review
  WT/packets/capi-pk0-v2/review/claude-v1 (REVIEW.md 0246243a..., review.json d42e962d...; read in full): ENDORSED_WITH_REQUIRED_CHANGES with
  RC-v2-1..RC-v2-4 (PK0-RC4 and PK0-RC5 CLOSED_IN_SOURCE). Also PK-0 v1 (WT/packets/capi-pk0/) and its sealed review (review/gpt61-v1).
  Everything those reviews found correct must stay correct. The author reports RC-v2-1 NOT fully closed: the Kind 1 R.Captured_Results /
  R.Required overlap with the Context_Input descriptor is recorded OPEN (deviation 2) because no construction was found that keeps the
  descriptor's earlier transport conjuncts true without changing the fixture's accepted rows; judge whether that is correct, whether a
  construction exists, and whether OPEN is the right disposition.
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
1. Packet integrity: identities, the 100 bound inputs, no existing file touched, v1 and v2 unchanged, the change list against v2 exact, and the
   invariants (REQUIRED_PROVED 0 appended, length 535; MINIMUM_CHECKS 251; UNANALYZED_BOUNDARY {"worldline-c_api"}; 0 movers;
   External_Name count 31). Are all v1/v2 cases and diagnostic cases byte-identical in content and order except the declared readiness field?
2. Closure of RC-v2-1..RC-v2-4: CLOSED_IN_SOURCE, PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; PK0-RC4/RC5 still closed. For
   RC-v2-1: the nested_conjuncts table complete against the S5 bodies; each new case (D56-D75) correct (spot-check at least eight against the
   bodies: code, frontier, twin placement, exact stream); unexercisable reasons correct; the OPEN overlap (deviation 2). For RC-v2-2: does
   probe_readiness make exactly Read_Ready's checks and does assert_ready make a not-ready fixture fail rather than pass as a refusal?
3. RC-v2-3/RC-v2-4 mechanics, read statically: refusal before any non-stdlib import; --measure-headers gating; HarnessFaultControl status line
   on every path including pass, captured by the launch.
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
