You are the independent, different-author reviewer for: WORLDLINE Phase One C-API consolidation packet PK-0 (characterization only),
SOURCE REVIEW. The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent (the same agent that drafted the C-API
designs). You are actual gpt-6.1-sol and authored nothing under review.

WHAT THIS REVIEW IS AND IS NOT
PK-0 is the first packet of the ENDORSED C-API design (DESIGN v6, sealed review WT/designs/claude-capi-boundary-design-v6/review/gpt61-v1,
verdict ENDORSED). Its stage gate is "baseline run on L0 in an admitted frame" (v3 DESIGN §9.2). That run is NOT possible now: the
confinement gate (frame v5 UNQUALIFIED; V5-B01/V5-B02 open) and the capacity gate block it. This review judges the packet SOURCE only:
nothing in it has been executed, and nothing you conclude is run evidence, control evidence or acceptance. The baseline run, its recorded
values and any stage qualification remain OPEN.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/capi-pk0/review/gpt61-v1
- Do NOT run, import or execute the packet's tests or helpers, pytest, any WORLDLINE code, compilers, gprbuild, provers, native builds or
  libraries; read Python as text/AST only. No systemctl, sudo, project-vault, restic or window/reservation action. Do not write SIA notes.
  Do not modify anything outside your cwd. Never read or list anything under ~/.local/share/sia/.gbrain/; never list or stat
  /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read directories still being written (WT/proposal/ISOLATION-STORAGE-PROPOSAL-v6.md,
  WT/proposal/v6-support/, WT/package-review/gpt61-v6/, WT/designs/claude-root-worker-seam-design-v4/review/) or any session transcript.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls modestly
  (sequentially or in groups of at most four).
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- You grant no acceptance. The only output is a source-review verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Packet under review, in WT/packets/capi-pk0/ (verify all nine hashes): packet.json (9808145e43e8e130bc7d8f73ad0757d838ad05dc209e64ebbccda33270eb69f9),
  AUTHOR-NOTES.md (ef5de3d4136bb11c957d604bec54006676acbe259a3d055633fd07415635968c), jackal.json (787ee005f0b84a1753e621b3805e2886d2cb8499af9004cc6ee657ae42ef7817),
  and under files/tests/: capi_characterization.json (51ba5ca271a738151c4753d26118b41087db0d8101e994c4dce3bcd883fd518a),
  capi_guard_pages.py (dbe7db5998263c9c6fb1289fbf7dfbf85d485a56a49c859c34eb0621a6c44355), capi_layout_baseline.json
  (d42264f7b193eb3f3f8abfacc93d96584e561f7375be0b57bceee041c484c055), test_capi_characterization.py
  (98dd782af94aee7da112676aca128e9d98c330b3d0ec657fa23aef8b27a2995a), test_capi_diagnostics.py
  (7c4fe2aac51b680f8e52616d8bba883d76b10a47416d3fa38733696e704ce70e), test_capi_layout_identity.py
  (99ff179a51227972abd5e5a5fb9a6525fc7d5c380893033c144952153ddd4307). packet.json binds 95 L0 input files by path, sha256 and size
  (the lead re-verified all 95) and states that no existing file is touched.
- Base L0: W/work/claude-composition-v5-beta/source (S5), QUALIFIED_SOURCE_COMPOSITION (its sealed review under
  W/work/claude-composition-v5-beta/review/gpt61-v1).
- The design it implements: PK-0 row of the packet table (WT/designs/claude-capi-boundary-design-v3/DESIGN.md §9.2) and the PK-0
  specification (WT/designs/claude-capi-boundary-design-v4/DESIGN.md §9.6, carried by v5 and v6): effect classes R0, R1, R2, R3, S, H, X;
  read frontiers per export; class-H defined part; OPEN items (§9.6.4); class X (§9.6.5); controls C-01..C-07, C-11, C-13, C-15, C-16
  in baseline forms, C-12 optional, C-14 never a pass condition (§9.6.6). The C-API design reviews (v3-v6) and their rulings are in
  WT/designs/claude-capi-boundary-design-v{3,4,5,6}/review/gpt61-v1.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt}; /home/sicarii/Documents/complete-phase1-prompt.txt.
  Never: narrow domains or accepted cases, redefine original behaviour (including defects), count a native failure as an accepted
  refusal, add assumptions, or weaken an expectation so an unrun test is likely to pass.
- Author process records (model output, recorded as stated): AUTHOR-NOTES.md; the author reports no deviations and that nothing was
  executed.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Packet integrity: identities, the 95 bound inputs, no existing file touched, and the stated invariants (REQUIRED_PROVED 0 appended,
   length 535; MINIMUM_CHECKS 251; UNANALYZED_BOUNDARY {"worldline-c_api"}; 0 movers; External_Name count 31) correct?
2. Fidelity to the endorsed design: does the packet carry exactly PK-0's content and controls (C-01..C-07, C-11, C-13, C-15, C-16 in
   baseline form; C-12 not authored; C-14 not encoded) and the effect-class model of §9.6, with §9.6.4 items left OPEN and nothing
   asserted for class X?
3. Faithfulness to the ORIGINAL S5 behaviour: spot-check at least six exports (include at least one multi-write export, one mixed entry
   (C-11), one pending decide, one completion decide/raw and one with post-capture transport guards) - every expected code, frontier,
   canonical write order and handler code against the S5 bodies. Is any original behaviour (including a defect) redefined, any class-H
   code treated as an accepted refusal, or any expectation weakened?
4. Placeholders and recording: does every run-dependent value (layout baseline, the three U14d/U15f written results, D06 failure latch)
   refuse until recorded through a reviewed change, with no path by which a placeholder passes and no --record path that writes a file?
5. Test mechanics, read statically: fork isolation, page-group placement and 0xA5 fill, byte comparison scope, PROT_NONE guard placement
   at frontiers, fault handling (a fault must fail the case, never map to a code), ctypes layout assumptions, D06's use of /dev/full and
   fd 2, absence of side effects outside the test process's own scratch, and the author's listed uncertainties (unproved bodies behind
   derived expectations, finite U32 probe domains, no timeouts, header probe without -Werror). Which are acceptable as stated, and which
   need changes before the baseline run?
6. Anything else that would weaken a contract, domain, accepted case, fixture, control or proof scope, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-packet-source-review-v1","packet":"<absolute path of packet.json>",
  "packet_sha256":"<sha256 you computed>","files_sha256":{name:"..."},"different_from_author":true,"actual_model_selection":"gpt-6.1-sol",
  "author":"Claude Code lead claude-opus-5-5 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
  "item_findings":{...},"required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],"run_evidence":false,
  "control_evidence":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, findings per item, required changes, and the sha256 of each of your four output files.
