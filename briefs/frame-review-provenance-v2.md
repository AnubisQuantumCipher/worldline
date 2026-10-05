You are the independent, different-author reviewer for: the WORLDLINE scratch-frame D-LEAD-REVIEW-PROVENANCE join change,
revision v2 (W-1 §23 / §23.6), implemented as a SOURCE-ONLY delta lane. The author is the Claude Code lead (claude-opus-4-8)
through a drafting subagent. You authored nothing under review and are not the drafting agent. This is the frame-design-revision
review W-1 §23.6 requires before any adoption may rely on a Claude-subagent review.

WHAT THIS IS. The frame's adoption join originally required gpt-6.1-sol rollout provenance. Under the human's 2026-10-05 ~17:05Z
direction (reviews moved to independent Claude review subagents), §23 specifies a CHANGE to that admission join: accept EITHER the
existing gpt-6.1-sol rollout provenance (for a GPT review) OR a sealed Claude-subagent provenance, selected by reviewer_kind; a review
of neither form REFUSES; never a label alone; never a Claude review claiming to be GPT. v1 of this change was reviewed
ENDORSED_WITH_REQUIRED_CHANGES. **v2 is the revision that implements the three required changes (R1/R2/R3).** You are reviewing v2.
You grant no acceptance of W-1 or the frame; the only output is a verdict on this change: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or
NOT_ENDORSED. Nothing is installed; adoption stays BLOCKED regardless of this verdict until the operator acts (§23.6).

THE THREE REQUIRED CHANGES v2 CLAIMS TO IMPLEMENT (the heart of this review — verify each against the code, not the author's prose):
- **R1 (PRIMARY — the self-authorship gap).** v1's Claude form read the reviewer task-output bytes and DISCARDED them, checked the agent
  id only as a filename substring, and bound raw-final-message.txt's sha256 without tying its CONTENT to anything — so a lead could
  self-author the entire review (REVIEW.md/review.json/checks.json + a matching raw-final-message.txt) and adopt. The GPT form does not
  have this hole: the independent codex rollout's final message must CITE the sha256 of the sealed review files. v2 claims to make the
  Claude form at least as strong by: (i) a hardened sealer (WT/tools/seal_claude_review.py) that REQUIRES the reviewer's verbatim final
  message to carry a `=== SEAL ===` block `{"completed_at":…,"sections":{"REVIEW.md":<sha>,"review.json":<sha>,"checks.json":<sha>}}` and
  verifies each cited hash against the extracted section bytes before sealing; (ii) a join (`claude_review_join`) that RE-DERIVES the
  binding from bytes (helpers `_seal_block`, `_raw_section`, `_mode_int`) rather than trusting any boolean — parses the SEAL block out of
  raw-final-message.txt, requires its cited section hashes to equal the on-disk file hashes (review.json accepted over on-disk OR raw-emitted,
  mirroring the sealer's dual acceptance), and BINDS the previously-inert task-output pin and agent id.
- **R2.** The Claude join requires a non-empty `freeze.completed_at` AND requires it to equal the SEAL block's completed_at (the independent
  reviewer's own sealed time), used as the Claude-branch ordering lower bound in `validate_adoption_observation`. Fail-closed if absent.
- **R3.** `review_profile_problems` no longer pins bound-inputs.json/tool-topology.json for a Claude review (the 3-file Claude roster does
  not seal them; pinning would FileNotFoundError and crash adopt). For reviewer_kind=='claude-subagent' it keeps checks.json REQUIRED
  (sha256 + bytes + normalized mode) and skips the other two. The GPT form is unchanged (full-pin over all three sidecars).

HARD LIMITS. Passive reading and hashing only. Do NOT import or execute the frame or any WORLDLINE code (read scratch.py and the sealer as
text/AST), no prover/tests, no sudo/systemctl/unshare, no project-vault/restic. Per override item 6 (shell hygiene): write no file anywhere,
never run a command that reads stdin, never background a command, use command ls/os.listdir. Never read/list ~/.local/share/sia/.gbrain/;
never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read any review directory of THIS lane (frame-review-provenance-v2)
or any transcript. JACKAL for derived numbers.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review, in WT/lanes/frame-review-provenance-v2/ (verify hashes yourself):
  - MANIFEST.json  28b73cd64135a5ead854bec8fb0883310a2f0490b70a48aef41a98878543edd9
  - frame-review-provenance.patch  a13caa564e9b945cf5c9f8dafd255dc6f59810f8ddead54c2f6494446e500674  (authored diffstat: 7 hunks, +287/-27)
  - postimage/scratch.py  c0b6bf1a9038001fed79a0d26ddeca0fe2161eecc8477450a8b59fcfd9274d53
  - preimage-region.py  c5e86142a700ac4d6d503a13d464c0291e1d0059f7e0c28c85844b809e27a272
  - changed-functions.postimage.py  468311e60cada6fbf6b077f0237fa83cdbcf7792d2bad4cd7272f530d7a980b8
  - AUTHOR-NOTES.md  7e8801a8ce490d8f319348f2a22e1de5cdba573baf626cfca58f5be0f3d32ef2
  - base/scratch.py  f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86
  The base equals the live frame v5 scratch.py (the lead confirmed base == live v5; live v5 `f9f6596d…` and v6 `2255d6e1…` are UNTOUCHED).
  The lead independently reconstructed patch(base/scratch.py) == postimage/scratch.py (sha256 c0b6bf1a…); confirm this yourself.
- The hardened sealer is WT/tools/seal_claude_review.py — read it in full as text. The join v2's assumptions about the on-disk shapes of
  review-freeze.json and review.json['sealed_by'] MUST match what this sealer actually writes. Verify the join reads the fields the sealer
  writes (freeze: completed_at, seal_verified, reviewer_agent_id, source_task_output_sha256, reviewer_cited_section_sha256, files;
  review.json['sealed_by']: raw_final_message_is_verbatim_independent_final_message, source_task_output_sha256, reviewer_agent_id).
- The spec: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v11.md §23 in full (§23.2 authority, §23.3 original texts, §23.4 the replacement join,
  §23.5 the 14 dependent sites, §23.6 adoption blocked until reviewed). Also §17 and §4.6 (the join sites).
- Real sealed Claude freezes present to study the binding against: WT/proposal/v10-review/claude-v1/ and WT/proposal/v11-review/claude-v1/.
  NOTE (author-flagged, confirm): these and the v1 lane's sample freeze (WT/lanes/frame-review-provenance-v1/review/claude-v1/review-freeze.json)
  are in the OLD pre-hardening format — their raw-final-message.txt has NO `=== SEAL ===` block. Join v2 is built against the hardened sealer
  and would REFUSE those old-format freezes fail-closed. Decide whether that fail-closed behavior is correct, and whether the absence of any
  on-disk hardened-format freeze to exercise the join against is a defect of this change or an execution-bound obligation for later.
- Authority: the operator's ~17:05Z direction, quoted verbatim in WT/STATUS.md and v11 §23.2. HANDOFF.md:173 and
  /home/sicarii/Documents/complete-phase1-prompt.txt:60 are the original texts the change modifies. A finding is not authority to add a gate.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. R1 closure. Does `claude_review_join` (postimage ~826) actually re-derive the binding FROM BYTES and refuse a self-authored review? Trace:
   does it parse the SEAL block from raw-final-message.txt; require sections['REVIEW.md']==on-disk sha256(REVIEW.md) and
   sections['checks.json']==on-disk sha256(checks.json); accept review.json's cite over on-disk OR raw-emitted (and is that dual acceptance
   exactly the sealer's, not a loophole); require freeze.reviewer_cited_section_sha256==the SEAL sections and freeze.seal_verified True;
   require sealed_by.raw_final_message_is_verbatim_independent_final_message True; and BIND freeze.source_task_output_sha256==pinned==
   sealed_by.source_task_output_sha256 and freeze.reviewer_agent_id==supplied==sealed_by.reviewer_agent_id (agent-<id> filename binding)?
   Is there ANY residual path by which a lead could satisfy the Claude form without an independent reviewer having emitted those digests?
   Compare the strength to the GPT form's rollout cite — is the Claude form now at least as strong, in a different form?
2. R2. Is completed_at non-empty required AND == SEAL completed_at, bound to the independent final message, and used as the ordering lower
   bound in validate_adoption_observation (observation after review completion, before adoption record)? Fail-closed if absent?
3. R3. Is the sidecar pin now form-aware: checks.json required for claude-subagent (sha256+bytes+normalized mode via `_mode_int`), the other
   two skipped, GPT form unchanged (all three)? Does `_mode_int('0600')` correctly normalize the sealer's octal string to the int Dir.ident
   returns? Could the mode normalization accept a wrong mode?
4. GPT form unchanged. Is `rollout_join` byte-identical in substance to base/v1 for a gpt-6.1-sol review; is the form selected by reviewer_kind;
   is a sealed GPT review never downgraded and a Claude review never routed to the GPT join? Does neither form refuse, and does a bare label
   only SELECT (the selected join still binding every byte)?
5. Refusal completeness and non-bypass. Does a review of NEITHER form refuse? Is a LABEL ALONE refused? Is the change confined to the join
   region (nothing in materialization/admission/launch/spawn/recovery touched)? Does it preserve the source/runtime binding and the proof
   binding — the provenance change must NOT become a path to adopt around the proof/source/runtime gates. Is the adoption schema bump
   (v5→v6) handled with re-join/re-pin at every use (frame_admitted ~1084)? Are the five acceptance Falses and the candidate/lead_id/
   inventory/report checks untouched?
6. The two author-flagged discrepancies (AUTHOR-NOTES.md §"Discrepancies found"): (a) no hardened-format freeze exists on disk yet, so the
   join could not be exercised against a real one — is that acceptable (execution-bound) or a blocking defect? (b)
   raw_final_message_is_verbatim_independent_final_message lives in review.json['sealed_by'], not the freeze top-level — is the join reading
   it from the correct place, and is that content-bound (via the freeze files['review.json'] sha256) rather than trusting an unbound field?
7. The open points (AUTHOR-NOTES.md §"Open points"): ratify or revise (i) the one-field-stricter-than-§23.4 SEAL-sealed completed_at
   requirement; (ii) the dual on-disk/raw-emitted review.json cite acceptance; (iii) the deliberate scope choice NOT to re-parse the
   task-output JSONL in the frame (relying on the SEAL content-cite + sealed_by assertion + task-output sha256 pin instead).
8. Anything else that weakens a contract/control/threshold, adds a gate, or lets adoption proceed on weaker provenance than the original GPT
   join demanded. Confirm the live frames are untouched and nothing is installed.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text, then the === SEAL ===
block the override requires). review.json schema:
{"schema":"claude-frame-join-review-v2","lane":"<abs path of the v2 lane>","postimage_sha256":"...","patch_sha256":"...",
"base_equals_live_v5":true/false,"patch_reconstructs_postimage":true/false,"different_from_author":true,
"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)","reviewer_kind":"claude-subagent",
"author":"Claude Code lead claude-opus-4-8 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
"r1_self_authorship":"...","r2_completed_at":"...","r3_sidecar":"...","gpt_form_unchanged":"...","refusal_and_nonbypass":"...",
"discrepancies":"...","open_points":"...","required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],
"adoption_still_blocked":true,"proof_acceptance":false,"source_acceptance":false}
