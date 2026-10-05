You are the independent, different-author reviewer for: the WORLDLINE scratch-frame D-LEAD-REVIEW-PROVENANCE join change
(W-1 §23 / §23.6), implemented as a SOURCE-ONLY delta lane. The author is the Claude Code lead (claude-opus-4-8) through a drafting
subagent. You authored nothing under review and are not the drafting agent. This is the frame-design-revision review W-1 §23.6 requires
before any adoption may rely on a Claude-subagent review.

WHAT THIS IS. The frame's adoption join currently requires gpt-6.1-sol rollout provenance. Under the human's 2026-10-05 ~17:05Z direction
(reviews moved to independent Claude review subagents), §23 specifies a CHANGE to that original admission join: accept EITHER the existing
gpt-6.1-sol rollout provenance (for a GPT review) OR a sealed Claude-subagent provenance, selected by reviewer_kind; a review of neither
form REFUSES; never accept a label alone; never let a Claude review claim to be GPT. This is a change to an original join, authorized ONLY by
that operator direction (§23.2). You grant no acceptance of W-1 or the frame; the only output is a verdict on this change: ENDORSED,
ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED. Nothing is installed; adoption stays BLOCKED regardless of this verdict until the operator acts.

HARD LIMITS. Passive reading and hashing only. Do NOT import or execute the frame or any WORLDLINE code (read scratch.py as text/AST), no
prover/tests, no sudo/systemctl/unshare, no project-vault/restic. Per override item 6 (shell hygiene): write no file anywhere, never run a
command that reads stdin, never background a command, use command ls/os.listdir. Never read/list ~/.local/share/sia/.gbrain/; never list or
stat /home/sicarii itself, ~/iPad or ~/iPadBackup. Do not read any review directory of this lane or any transcript. JACKAL for derived numbers.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review, in WT/lanes/frame-review-provenance-v1/ (verify hashes): MANIFEST.json (0272cdfbb8337d65ac685fccbca2723473b762c54fd31f4c99c390c03121a2f5),
  frame-review-provenance.patch (b67221f741b897a7cdeb882fdbeef19e4989803af59c531ac37475944a37632f), postimage/scratch.py
  (61f3dd4bab7d016285d155f8bb1f5205a37e47ac9493f8b460ada1a75ba91e5b), preimage-region.py (c5e86142a700ac4d6d503a13d464c0291e1d0059f7e0c28c85844b809e27a272),
  changed-functions.postimage.py (e2efb183bef34032db07538e558edc170106d5ea55815277d3a55f57a94e9206), AUTHOR-NOTES.md
  (4dab335db493056ea01f095cbb716ad38f733d81896ccf754be0101e5b50d20e), base/scratch.py (f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86).
  The base equals the live frame v5 scratch.py (the lead confirmed base == live v5, and that the live v5 and v6 frames are UNTOUCHED).
- The spec: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v11.md §23 (the full change: §23.2 authority, §23.3 original texts, §23.4 the replacement
  join, §23.5 the 14 dependent sites, §23.6 adoption blocked until reviewed). Read §23 in full. Also §17 and §4.6 (the join sites).
- The base join region in base/scratch.py: REVIEW_PROFILE (~98-103), FRAME_REVIEW_ROSTER (~89), rollout_join (~687-745),
  review_profile_problems (~748-761), validate_adoption_observation (~764-813), adopt (~816-837), frame_admitted (~840-863). The change is
  13 localized hunks (net +149 lines) confined to this region (lead-verified via base-vs-postimage diff).
- Real sealed Claude freezes to check the binding against: WT/proposal/v10-review/claude-v1/review-freeze.json and
  WT/proposal/v11-review/claude-v1/review-freeze.json (and any CLAUDE_REVIEW_ROSTER the change names).
- Authority: the operator's ~17:05Z direction, quoted verbatim in WT/STATUS.md and v11 §23.2. HANDOFF.md:173 and
  /home/sicarii/Documents/complete-phase1-prompt.txt:60 are the original texts the change modifies. A finding is not authority to add a gate.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Faithfulness to §23.4: does the Claude-subagent form bind ALL of: the sealed review-freeze.json over exactly REVIEW.md/review.json/checks.json
   (each sha256+bytes) and the freeze's own sha256; raw-final-message.txt sha256; the reviewer agent id (bound to the agent-<id> task-output
   filename); the reviewer task-output sha256 (replacing the ~/.codex/sessions rollout uniqueness, §23.5 item 3); reviewer_kind=='claude-subagent';
   different_from_author==True? Check the actual logic against the real v10/v11 freezes.
2. The GPT form: is rollout_join RETAINED unchanged in substance for a gpt-6.1-sol review (sealed GPT reviews keep standing), with form selected
   by reviewer_kind? Never does a Claude review claim GPT; never is a GPT review downgraded.
3. Refusal completeness: does a review of NEITHER form refuse? Is a LABEL ALONE (reviewer_kind without the bound bytes) refused? Is any path by
   which the join could pass on unsealed, unbound, mismatched, or author-identical (different_from_author False) provenance? Trace
   review_profile_problems / validate_adoption_observation / adopt / frame_admitted.
4. The flagged augmentation: the change REQUIRES a sealed completed_at in the Claude freeze (stricter than §23.4's literal list) to preserve the
   observation-after-completion ordering invariant. Is that a sound, non-loosening tightening, or should §23.6 respecify it? Does it refuse if absent?
5. Localization and binding integrity: is the change confined to the join region (nothing in materialization/admission/launch/spawn/recovery
   touched)? Does it preserve the source/runtime binding and the proof binding — i.e. the join change does NOT bypass proof, source-identity, or
   runtime binding (a review-provenance change must not become a way to adopt without the proof/source gates)? Schema bump handled (adoption
   schema v5→v6; re-join/re-pin at every use)?
6. Anything else that weakens a contract/control/threshold, adds a gate, or lets adoption proceed on weaker provenance than the original GPT join
   demanded (the replacement must be at least as strong, in a different form). Confirm the live frame is untouched and nothing is installed.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-frame-join-review-v1","lane":"<abs path>","postimage_sha256":"...","patch_sha256":"...","base_equals_live_v5":true/false,
"different_from_author":true,"actual_model_selection":"claude-opus-4-8 (independent Claude Code review subagent, fresh context)",
"reviewer_kind":"claude-subagent","author":"Claude Code lead claude-opus-4-8 (drafting subagent)",
"verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","faithfulness":"...","gpt_form":"...","refusal_completeness":"...",
"completed_at_augmentation":"...","localization_and_binding":"...","required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],
"adoption_still_blocked":true,"proof_acceptance":false,"source_acceptance":false}
