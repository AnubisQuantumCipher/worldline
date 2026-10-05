You are the independent, different-author reviewer for: WORLDLINE Phase One C-API consolidation packet PK-0 REVISION 2
(characterization only), SOURCE REVIEW. The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent (the same agent that
drafted the C-API designs and PK-0 v1). You are actual gpt-6.1-sol and authored nothing under review. A separate gpt-6.1-sol session
reviewed PK-0 v1.

WHAT THIS REVIEW IS AND IS NOT
PK-0 is the first packet of the ENDORSED C-API design (DESIGN v6, sealed review WT/designs/claude-capi-boundary-design-v6/review/gpt61-v1,
verdict ENDORSED). Its stage gate is "baseline run on L0 in an admitted frame" (v3 DESIGN section 9.2). That run is NOT possible now: the
confinement gate (frame v5 UNQUALIFIED; V5-B01/V5-B02 open) blocks it. This review judges the packet SOURCE only: nothing in it has been
executed, and nothing you conclude is run evidence, control evidence or acceptance. The baseline run, its recorded values, the six launch
obligations and any stage qualification remain OPEN.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/capi-pk0-v2/review/gpt61-v1
- Do NOT run, import or execute the packet's tests or helpers, the S5 producers or fixtures, pytest, any WORLDLINE code, compilers,
  gprbuild, provers, native builds or libraries; read Python as text/AST only. No systemctl, sudo, project-vault, restic or
  window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under
  ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup (the iPad mounts can hang). Do not read
  reviews or drafts in progress (WT/proposal/v8-review/, WT/designs/claude-native-bigint-d1-design-v4/review/,
  WT/designs/claude-root-worker-seam-design-v5/review/) or any session transcript.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls modestly
  (sequentially or in groups of at most four).
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- You grant no acceptance. The only output is a source-review verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Packet under review, in WT/packets/capi-pk0-v2/ (verify all nine hashes): packet.json (c5ce00cd7d0dbeaff29a35f87e257abe165a8c116acf3b02760d732ef12e032d),
  AUTHOR-NOTES.md (4f50ad4611727746e1645d35c5ea1d0144ab4c7819e3a5ca146dd45219dde514), jackal.json (f4b69fdf0ce1080f96aa5c7f1c6f466a59d0a455a260b1fd1e9f081a1db7668e),
  and under files/tests/: capi_characterization.json (42d23d67f1d324ff41ddff29759d206492137cbc9088c927b0e0cd8bbda9befb),
  capi_guard_pages.py (29e496d590db927315e69b45bb5d474e8a3aa8ecebebcc1d3bdad2649ab3d12b), capi_layout_baseline.json
  (4df25239c3fd173b4076fe34e9f250948f8c92f7068c701c364723ba18294bf0), test_capi_characterization.py
  (acbdcc42eefff6d0d0988694e9e62f0e89641274b336ac0d9d07b93e221bc5b1), test_capi_diagnostics.py
  (835377234921c004db221d90c6cb81323d1923639e873bceefa2996ef28c8f7b), test_capi_layout_identity.py
  (76f086ddff012854a6962cae3bc1c62f8adae4e09dbda616e5c8828e01af12fa). packet.json binds 100 L0 input files by path, sha256 and size
  (95 from v1 plus 5 v2 reads; the lead re-verified all 100) and gives a file-by-file change list against v1.
- Closure targets: PK-0 v1 (WT/packets/capi-pk0/, packet.json 9808145e..., unchanged) and its sealed review WT/packets/capi-pk0/review/gpt61-v1
  (REVIEW.md 7d86d533..., review.json fc615b5be33f0caf4e2964e06b2d001d2568c12088c9ca306bb8500bd70dbdf5, checks.json 949b6150...,
  review-freeze.json fa987ae0...): verdict ENDORSED_WITH_REQUIRED_CHANGES with required changes PK0-RC1..PK0-RC5. Everything that review
  found correct must stay correct.
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
1. Packet integrity: identities, the 100 bound inputs, no existing file touched, v1 unchanged, the change list against v1 exact, and the
   invariants (REQUIRED_PROVED 0 appended, length 535; MINIMUM_CHECKS 251; UNANALYZED_BOUNDARY {"worldline-c_api"}; 0 movers;
   External_Name count 31). Are all 609 v1 cases and 28 v1 diagnostic cases byte-identical and in order?
2. Closure of each of PK0-RC1..PK0-RC5: CLOSED_IN_SOURCE, PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap. For RC1 specifically:
   are the ready inputs genuinely S5's producers and fixtures, is the pointer-rewrite owner check sound, does the Authorized oracle check
   make a not-ready fixture fail rather than pass as a refusal, are the guard-page twins and end-of-object guards placed correctly, and
   is the coverage (primary-only, staged-only, both; nested context-join refusal groups; Kind-1 metadata refusals after Authorized;
   Engine-origin agent) complete against the S5 bodies? Are the two groups declared not exercised acceptable as stated, or required?
3. The Resulting_Requirement deviation and the S5 finding: is the finding correct against the cited S5 source? Does setting
   Resulting_Requirement in the new cases redefine original behaviour, alter an original fixture or control, or narrow the domain? What
   does it mean for the original controls that assert AUTHORIZED (relate it to author finding F32 in WT/STATUS.md if useful), and who
   owns that question? Do not decide it beyond the source evidence.
4. Faithfulness to ORIGINAL S5 behaviour for the new cases and diagnostics (U15y, D29-D55): spot-check at least six, including a mixed
   entry Authorized case, a nested context-join refusal, a Kind-1 metadata refusal after Authorized and an Engine-origin agent case:
   every expected code, frontier, write order and handler code against the S5 bodies. Any class-H code treated as an accepted refusal,
   any expectation weakened?
5. Mechanics, read statically: --record output-only on every path, the --headers digest gate, --measure-headers confined to
   WORLDLINE_PK0_SCRATCH, bytecode-suppression refusal, signal-disposition reset and re-check around every export call, abnormal child
   exit failing before code comparison, HarnessFaultControl (reachable only in the admitted run, never at import or record),
   lossless fd 2 comparison and hex fallback, the stated isolation boundary (parent-side init and layout calls, libc load at import, no
   deadline), and the six OPEN launch obligations. Which are acceptable, and which need changes before the baseline run?
6. Placeholders: are the RECORD_ON_L0 placeholders unchanged from v1 with none added, and can none of them pass?
7. Anything else that would weaken a contract, domain, accepted case, fixture, control or proof scope, or add an assumption or an
   approval gate.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-packet-source-review-v1","packet":"<absolute path of packet.json>",
  "packet_sha256":"<sha256 you computed>","files_sha256":{name:"..."},"different_from_author":true,"actual_model_selection":"gpt-6.1-sol",
  "author":"Claude Code lead claude-opus-5-5 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
  "rc_closure":{"PK0-RC1":"...",...,"PK0-RC5":"..."},"item_findings":{...},"required_changes":[{"id","change","reason","evidence"}],
  "open_obligations":[...],"run_evidence":false,"control_evidence":false,"proof_acceptance":false,"phase_acceptance":false,
  "source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per PK0-RC, findings per item, required changes, and the sha256 of each of your four output files.
