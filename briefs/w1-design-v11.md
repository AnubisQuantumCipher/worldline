You are the independent, different-author design reviewer for: WORLDLINE Phase One isolation proposal W-1 v11 (scratch-frame
confinement), on W-1's own design-review track. The author is the Claude Code lead (claude-opus-4-8) through a drafting subagent. You
authored nothing under review and are not the drafting agent. v6/v7 (gpt-6.1-sol) and v8/v9/v10 (independent Claude subagents) were all
NOT_ENDORSED.

WHAT v11 IS. v11 is a NARROW form/bookkeeping revision of v10: it applies EXACTLY the three fixes the sealed v10 review required
(W1-V10-FORM self-containment, W1-V10-COUNT partition, the W1-V9-REVIEW-PROVENANCE residual prompt-path citation) and changes nothing else.
All of v10's spec-closed content is carried unchanged. Your task is to (a) confirm the three fixes are correct and complete, (b) confirm
nothing else changed from v10's spec-closed answers, and (c) re-verify the closure of the nine W1-V9 required changes at the same level the
v10 review found them. This is NOT a re-litigation of the obligation-level content; judge the sensitive async/privilege material only as
OBLIGATION + PREDICATE as before, and do not request, write or reward any procedure.

HARD LIMITS (same as the v10 review). Passive reading and hashing only; no execution of WORLDLINE/frame code, no prover/compiler, no sudo/
systemctl/unshare/mount/strace/project-vault/restic/probe. Reading installed kernel headers/docs/man/pacman-DB read-only is fine; label
anything relied on you could not verify locally. Per override item 6 (shell hygiene): write no file anywhere, never run a command that reads
stdin, never background a command, use `command ls`/os.listdir. Never read ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii
itself, ~/iPad or ~/iPadBackup. Do not read any v11 review directory, review-records/, any gpt61-v* dir, or any transcript. JACKAL (MCP) for
any derived arithmetic, sequentially or ≤4, literal exponents; carry status, parsed=, non_claims. Every original Phase One obligation stays
OPEN; the only output is a design verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify hashes): WT/proposal/ISOLATION-STORAGE-PROPOSAL-v11.md (sha256
  aac18b67144c18b22c83d739a3fd4c5cff0d2a91eca75a64858d4b791cf637aa, 576903 bytes, 5389 lines) and WT/proposal/v11-support/jackal.json
  (4fae39d5da081643a14b0225a52aecea045c19bf6ce4298fff8eaf7a0c261d4b). v11 is SELF-CONTAINED: Part V11-MAP (at the end) lists every one of
  v9's 134 units with its v11 status, line range, byte count and both v9 and v11 sha256. The whole-file identity is recorded in jackal.json
  (a file cannot contain its own post-assembly hash) — verify the file's actual sha256 equals the recorded aac18b67… value.
- Bases to read alongside: v10 ISOLATION-STORAGE-PROPOSAL-v10.md (sha256 d5fe8f3152dd8782adeee65478d7f70fb06e5fac50f0b17943d53598da66d8ef)
  and v9 ISOLATION-STORAGE-PROPOSAL-v9.md (4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b).
- Closure targets: the sealed v10 Claude review WT/proposal/v10-review/claude-v1 (REVIEW.md 81419b7a6a830b78d6232412dfe686b9bb8ca9706f120a0caa1e1bd2fa515833,
  review.json ac21f21fba63c862c9503cf0f2bfe89d6d603fb33a9c65376c530f3ff7f7c01f; read both in full): verdict NOT_ENDORSED with eight of nine
  W1-V9 changes CLOSED_AT_SPEC_LEVEL, W1-V9-REVIEW-PROVENANCE stated-as-change-not-closed (adoption blocked), and required changes W1-V10-COUNT,
  W1-V10-FORM, the review-provenance residual, plus the carried execution-bound W1-V8-PRESERVATION/-PREMISE-DISCHARGE/-EVIDENCE-EQUIV. Also
  the sealed v9 review WT/proposal/v9-review/claude-v1. Everything the v10 review found CLOSED_AT_SPEC_LEVEL must stay so.
- Requirements/supervision/criteria as in the v10 brief (frame v5 review V5-B01/B02; HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json,
  complete-phase1-prompt.txt at /home/sicarii/Documents/; STATUS.md D-LEAD-REVIEW-PROVENANCE). The prompt file is at
  /home/sicarii/Documents/complete-phase1-prompt.txt (NOT under outputs/) — v11 fixes this citation; confirm it.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. W1-V10-FORM (self-containment): is v11 self-contained? Independently recompute, by the §V11-0.1 unit rule, the v11 sha256 of a sample of
   units across all statuses (verify ALL 100 CARRIED are byte-identical to v9 — v11 sha256 == v9 sha256 for each — by a scripted full parse
   of Part V11-MAP, not just a sample; and spot-check ≥5 AMENDED and ≥5 COMPOSED units). Confirm every v9 unit carries a computed v11 sha256,
   every Part V11-MAP row equals the actual file bytes (line range, byte count, sha256), the whole-file hash equals aac18b67…, and the only
   identities not inside the file are the map apparatus + whole-file hash (recorded in jackal.json). Is the §V11-0.1 normalization rule stated
   and does it make each AMENDED unit's bytes uniquely determined? Is the v10 Appendix-I off-by-one resolved?
2. W1-V10-COUNT: is the partition now correct and internally consistent across Part V11-MAP, §V11-C.2 and jackal.json? Confirm (JACKAL) the
   v11 partition (100 CARRIED, 23 AMENDED, 11 COMPOSED, 0 SUPERSEDED = 134; +2 NEW = 136; the 2 formerly-SUPERSEDED v9 units now COMPOSED)
   and that the corrected v10 partition (100/23/9/2, 23+9=32) is also recorded. The 23 AMENDED units must be exactly 2.2,2.3,4.2,4.6,5.3,6.1,
   8.1,8.6,9.1,9.3,9.8,10.6,11.3,11.4,11.5,11.6,12.2,12.3,15.3,17,21.3,B.3,App.D.
3. W1-V9-REVIEW-PROVENANCE residual: is the prompt source path corrected to /home/sicarii/Documents/complete-phase1-prompt.txt everywhere
   (and HANDOFF.md:173 still correctly under outputs/)? §23 otherwise unchanged from v10's spec-closed state (quoted authority/texts, 14
   dependent sites, precise replacement join, adoption blocked)?
4. Nothing-else-changed: diff v11's materialized AMENDED/COMPOSED unit content against v10's intended spec-closed content (and AMENDED against
   v9 + the stated edits). Confirm no spec answer (ASYNC-ENUM obligation+predicate, NOOWNER-SCOPE, ENUM-USERDEL 67/104, PLAN-CONSTRAINTS,
   PREMISE-ORDER, RL-SELFTEST-FIXTURE, INVENTORY V15-V17/fd-set) was altered, weakened, or newly broken; no obligation, fixture, control,
   threshold, accepted case or join weakened or added; the sensitive procedures remain operator-reserved/OPEN.
5. Re-confirm the eight CLOSED_AT_SPEC_LEVEL items stay closed and the carried execution-bound items stay OPEN (V5-B01/B02, premise discharges,
   §21 rows); adoption stays blocked; the §23 join change stays an unreviewed change. Is W1-V8-FORM-SUBUNIT now RESTORED (no longer regressed)?
6. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, add an assumption or gate, or
   present an unverified premise as fact.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-design-review-v1","design":"<absolute path of v11>","design_sha256":"...","support_sha256":"...","different_from_author":true,
"actual_model_selection":"claude-opus-4-8 (independent Claude Code review subagent, fresh context)","reviewer_kind":"claude-subagent",
"author":"Claude Code lead claude-opus-4-8 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
"form_assessment":"...","count_assessment":"...","provenance_residual_assessment":"...","nothing_else_changed":"...","prior_closure":{...},
"required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],"approval_granted":false,"proof_acceptance":false,
"phase_acceptance":false,"source_acceptance":false}
