# AUTHOR-NOTES — D-LEAD-REVIEW-PROVENANCE join v2 (R1/R2/R3), lane `frame-review-provenance-v2`

**Author:** Claude Code drafting subagent (claude-opus-4-8) under the WORLDLINE Phase One lead.
**Role:** DRAFTING AUTHOR, not a reviewer. **Status:** SOURCE-ONLY, UNINSTALLED, live frame untouched,
v1 lane untouched. **Adoption stays BLOCKED** pending v2's own independent review (§23.6).

v1 was ENDORSED_WITH_REQUIRED_CHANGES. v2 patches the **same base** (`claude-scratch-frame-v5/scratch.py`,
sha256 `f9f6596d…be86`, == live v5) and implements the three required changes. The GPT form and all
proof/source/runtime binding are carried **exactly** as v1/base.

## How R1 / R2 / R3 are implemented

### R1 (PRIMARY) — cross-bind the independent transcript's *content* to the sealed review
The v1 Claude form read `task_bytes` and discarded it, checked the agent id only as a filename substring,
and bound `raw-final-message.txt`'s sha256 without tying its **content** to anything — so a lead could
self-author the whole review and adopt. The GPT form avoids this: the independent codex rollout's final
message must **cite the sha256** of the sealed review files (`rollout_join:741-743`).

v2 makes the Claude form at least as strong, mirroring that mechanism. The lead hardened the sealer
(`WT/tools/seal_claude_review.py`): the reviewer's own verbatim final message must carry a `=== SEAL ===`
block `{"completed_at":…, "sections":{"REVIEW.md":<sha>, "review.json":<sha>, "checks.json":<sha>}}`, and
the sealer verifies each cited hash against the extracted section bytes before sealing.

`claude_review_join` now **re-derives the binding from bytes** (new helpers `_seal_block`, `_raw_section`,
`_mode_int`) — it does **not** trust any boolean:
- parses the `=== SEAL ===` block out of `raw-final-message.txt`;
- requires `sections['REVIEW.md']` == on-disk sha256(REVIEW.md) and `sections['checks.json']` == on-disk
  sha256(checks.json) (the sealer writes these two verbatim, so cite == file hash);
- for `review.json` (which the lead re-serializes `indent=1`), accepts the cite over **either** the on-disk
  review.json **or** the raw emitted `=== review.json ===` section — exactly the dual acceptance the sealer
  itself performs (`emit` vs `alt_review_json`);
- requires `freeze.reviewer_cited_section_sha256` == the SEAL `sections`, and `freeze.seal_verified` is True
  (corroboration, not the primary evidence);
- requires `review.json['sealed_by'].raw_final_message_is_verbatim_independent_final_message` is True;
- **binds the task-output pin (was inert):** requires `freeze.source_task_output_sha256` == the pinned
  task-output sha256 == `review.json sealed_by.source_task_output_sha256`, and `freeze.reviewer_agent_id`
  == supplied id == `sealed_by.reviewer_agent_id`, keeping the `agent-<id>` filename binding.

Net effect: the sealed review is cryptographically tied to a verbatim independent final message that itself
emitted the digests of the exact sealed bytes, and that message is tied to the pinned task-output and agent
id. A lead cannot fabricate this without actually running an independent review that emits those digests —
the same bar the GPT join sets.

### R2 — completion time, now reviewer-sealed and consistent with R1
`claude_review_join` requires a non-empty `freeze.completed_at` **and** requires it to equal the SEAL
block's `completed_at` (the independent reviewer's own sealed time, verified by the sealer). It is bound as
`review_completed_at` and used unchanged as the Claude-branch ordering lower bound in
`validate_adoption_observation` (observation must follow review completion and precede the adoption record).
Fail-closed if absent. This resolves the v1 concern that `completed_at` was a bare lead-sealed field: it is
now bound to the independent final message via R1.

### R3 — form-aware sidecar check
`review_profile_problems` no longer pins `bound-inputs.json`/`tool-topology.json` for a Claude review (the
3-file Claude roster does not seal them; `pin()` would raise `FileNotFoundError` and crash adopt). For
`reviewer_kind=='claude-subagent'` it keeps `checks.json` **required** — compared by sha256 + bytes +
**normalized mode** (`_mode_int('0600')==0o600`) — and skips the other two. The **GPT form is unchanged**
(full-pin equality over all three sidecars).

### mode note (optional) — addressed
`_mode_int` normalizes the sealer's octal string `"0600"` to the int `Dir.ident` returns. The Claude freeze
member check and the R3 `checks.json` compare now bind **mode** too (a tightening over v1, which compared
only sha256+bytes).

## Dual-form logic unchanged for GPT
`rollout_join` is byte-identical to v1 (docstring + the one `reviewer_kind:'gpt-6.1-sol'` provenance key).
`review_freeze_kind` / `review_provenance_join` select the form by `reviewer_kind`; a sealed GPT review
still routes to `rollout_join` and is never downgraded; a Claude review never reaches it; neither form
refuses; a bare label only selects — the selected join binds every byte. `frame_admitted` re-joins and
re-pins by `reviewer_kind` at every use; the Claude re-check now also covers `source_task_output_sha256`,
`reviewer_cited_section_sha256` and `seal_verified`. `frame_inventory` and the candidate/lead_id/
frame_inventory/report checks and the five acceptance Falses are untouched — a provenance change is still
not an adoption path around the proof/source/runtime gates.

## Discrepancies found (handled honestly, flagged for the reviewer)

1. **The sample freeze is NOT in the hardened format.** `WT/lanes/frame-review-provenance-v1/review/claude-v1/
   review-freeze.json` still has only `{actual_model_selection, reviewer_kind, verdict, files}` and its
   `raw-final-message.txt` has **no `=== SEAL ===` block**. The lead's message said it was sealed with the
   new tool; it was not. I implemented v2 against `tools/seal_claude_review.py` (authoritative). **Join v2
   would REFUSE that old-format sample** (fail-closed) — correct. A freeze produced by the current sealer
   with a SEAL block is required before any Claude review can adopt. I could not run the join against a real
   hardened freeze because none exists on disk yet.
2. **`raw_final_message_is_verbatim_independent_final_message` location.** The lead's message placed this
   flag in `review-freeze.json`; the actual tool writes it in `review.json['sealed_by']`. v2 reads it from
   `sealed_by` (content-bound via the freeze `files['review.json']` sha256). Please confirm the intended
   location, or have the sealer also mirror it into the freeze.

## Open points for the frame-design review
- Ratify (or revise) the one-field-stricter-than-§23.4 requirement that the Claude freeze carry a
  SEAL-sealed `completed_at` (R2), now bound to the independent final message.
- The `review.json` cite is accepted over the on-disk **or** raw-emitted form (mirroring the sealer). If a
  single canonical form is preferred, the sealer and join should both pin it.
- Consider whether the join should additionally re-parse the task-output JSONL to confirm
  `raw-final-message.txt` is literally its last assistant message. v2 binds the task-output by sha256 and
  relies on the SEAL content-cite + `sealed_by` assertion rather than re-implementing the sealer's parser in
  the frame; this was a deliberate scope choice (keep the join from duplicating the sealer), disclosed here.

## Limits honored
Live frames (`v5`, `v6`) and the v1 lane were **not modified**; only files under this v2 lane were written.
Nothing was executed except read-only `ast.parse` (file parsed as data; the frame was never imported or run)
and `sha256sum`. This delta is uninstalled and grants nothing; every Phase One obligation stays OPEN.
