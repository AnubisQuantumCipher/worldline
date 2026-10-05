You are the independent, different-author design reviewer for: WORLDLINE Phase One native Big_Integer D1 DESIGN v5.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You authored nothing under review and are not the
drafting agent. Earlier revisions were reviewed by separate sessions (v4 by an independent Claude review subagent).

HARD LIMITS
- Passive reading and hashing only. Do not run compilers, provers, builds, tests, WORLDLINE code, systemctl, project-vault or restic. You may
  run short read-only Python snippets for inspection (reading source/stdlib text, AST, your own interpreter); never import WORLDLINE modules.
  Write no file anywhere (not /tmp, not the scratchpad). Never start a shell command that waits on stdin. Do not write SIA notes. Never read
  or list anything under ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read any review
  directory of v5, the v4 review/gpt61-v1 or gpt61-v2 directories, review-records/, or any session transcript.
- Do not stop, kill or interrupt any process. JACKAL (MCP) for any derived arithmetic (sequentially or in groups of at most four); carry
  status, parsed= and non_claims (jackal_exact refuses ^ with non-literal exponents; jackal_poly_eq for polynomial identities).
- You grant no acceptance. The only output is a design verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-native-bigint-d1-design-v5/ (verify all six hashes): DESIGN.md
  (5994b2436376d71d8cbf6eb8c90f2c1c601244d6c239872f604c469046a11ebd), APPENDIX-A-python-conversion-surface.md
  (11cad97d194d90e8e7c16ffbac6e61221fd4d0c9fec2ff3f00094826ffd07f98), APPENDIX-B-arow-horizon.md
  (b588941d059d7e9c6a8679714b0873faad1bb54faf8407665c53fbc1ddd71fc4), jackal.json (edbdc9dee50a8b4fb630fab89d272c92f2f52c39bf996edb64cd4dabf5f99195),
  decisions.json (fd470295050c0bac53ed176f4c46450dbaefe94b9c58b6d2b6a28b262fc70396), AUTHOR-NOTES.md
  (be43d1b993af8c20aed98efd20d40fe067423a2f5eca817ef7ef259c9124ae12).
- Closure target: v4 (WT/designs/claude-native-bigint-d1-design-v4/) and its sealed independent Claude review
  WT/designs/claude-native-bigint-d1-design-v4/review/claude-v1 (REVIEW.md a81c41f6..., review.json a5a26a90...; read in full): verdict
  ENDORSED_WITH_REQUIRED_CHANGES with V4-RC1, V4-RC2 (a)-(h), rulings R-DRC5, R-F35 (F35 OPEN and BLOCKING; no Pre, cap, domain restriction or
  refusal eligible), R-EXTENT, R-F32, R-OD2-DEPTH, R-CARRY, and findings F32/F34/F35/F36/F37. Earlier: v3 and its sealed review
  (WT/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1).
- The author's position (claims, not closures): new primary engine A-ROW (row-order per-kind accumulators, Theorem H-A in §5.14 / Appendix B:
  every ghost value D1-A forms is representable whenever the original's checked evaluation's values are, on the complete original domain, incl.
  RL-24/25/26); A-COL (v4 column engine) kept as recorded alternative with F35 OPEN (F38: every ghost model forms truncated multi-row sums; RL-26);
  V4-RC1 Held-only usage (Usage_Candidate) in both engines, RL-25 and RL-25C; V4-RC2 (a)-(h); LA-10 per-kind (A-ROW cost 3·N·n_s + 6·n_s).
  Author disclosure: during v4 drafting it grepped the lead's top-level transcript once (recorded in WT/deviations/d1v5-author-process/NOTE.md);
  nothing from it is used in v5.
- Source: W/work/claude-composition-v5-beta/source (S5). GNAT runtime sources /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/
  aarch64-linux-gnu/16.1.0/adainclude; GNATprove docs under /home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1; Python stdlib /usr/lib/python3.14.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt}; /home/sicarii/Documents/complete-phase1-prompt.txt.
  Native rule: "Resolve the native Big_Integer cost correspondence without adding caps, suppressing assertions or turning required successes
  into refusals"; "Do not add a domain cap, count native failure as an accepted refusal, substitute a proof-only light library or suppress
  checked Ghost code." Supervision: routine reversible engineering preserving the original external contract and success domain is the lead's;
  OD-1/OD-2 remain operator selections where the sealed rulings say so; a brief or finding is not authority to add gates.
- F32 is owned outside D1 (WT/designs/claude-f32-resolution-v4/ and its sealed review; R-A test-helper fix); D1 must not decide it.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Closure of V4-RC1 (each part) and V4-RC2 (a)-(h): CLOSED or NOT_CLOSED with the gap; every v4-review CLOSED item and ruling preserved.
2. Theorem H-A and A-ROW: is the horizon argument complete and correct on the COMPLETE original domain (both builds; direct-Ada and Check
   paths; signed operands; Held and Budget; every selector; every row count; the original's own checked evaluation as the reference)? Does every
   new D1 ghost construct execute (no uncalled proof-only lemma), with no Pre, cap, domain restriction, refusal or suppressed Ghost? Is F35
   closed at design level for A-ROW? Verify every JACKAL value H-A relies on (K-213..K-250) by re-running them.
3. Does A-ROW preserve the original decision on every input and the original release-build cost class (or is any cost change stated and
   obligated)? Is the per-kind LA-10 change sound?
4. F38 / A-COL: correctly carried OPEN; correctly not selected.
5. RL-24, RL-25, RL-25C, RL-26, W-0 calibration, IM-10, RL-12IN/RL-12I: controls well-formed and expectations correct against S5?
6. Anything that would weaken a contract, domain, accepted case, control or proof floor, add an assumption, count a resource failure as a
   refusal, suppress checked Ghost code, or add/lower an approval gate.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-design-review-v1","design":"<absolute path of DESIGN.md>","design_sha256":"...","decisions_sha256":"...",
"appendix_sha256":{"A":"...","B":"..."},"different_from_author":true,"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)",
"reviewer_kind":"claude-subagent","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
"verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","prior_closure":{"V4-RC1":"...","V4-RC2":"..."},
"findings":{"F35":"...","F37":"...","F38":"...","H-A":"..."},"required_changes":[{"id","change","reason","evidence"}],
"rulings":[{"id","ruling","owner","evidence_required"}],"open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,
"source_acceptance":false,"native_acceptance":false}
