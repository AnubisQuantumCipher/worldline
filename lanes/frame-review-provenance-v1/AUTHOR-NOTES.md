# AUTHOR-NOTES — D-LEAD-REVIEW-PROVENANCE join change (W-1 §23), lane `frame-review-provenance-v1`

**Author:** Claude Code drafting subagent (claude-opus-4-8) under the WORLDLINE Phase One lead.
**Role:** DRAFTING AUTHOR, not a reviewer. This lane is a **reviewable delta**, not an installation.
**Status:** SOURCE-ONLY, UNINSTALLED, live frame untouched. **Adoption stays BLOCKED** until this
change is itself independently reviewed in the frame-design revision (§23.6).

This is a **change to an original admission join** (never preservation), authorized only by the
operator's 2026-10-05 ~17:05Z direction quoted in `WT/STATUS.md` and §23.2. Whether it "loosens
nothing" is an argument for the frame-design review to judge — it is **not asserted here**.

## 1. Where the join code is

Base: `work/claude-scratch-frame-v5/scratch.py`
(sha256 `f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86`, 2007 lines).

The review-provenance join is exactly these contiguous sites (v5 line numbers):

- `REVIEW_PROFILE` constant — **98-103** (the compiled profile; `actual_model_selection: gpt-6.1-sol`).
- `FRAME_REVIEW_ROSTER` — **89** (the 5-file GPT freeze roster).
- `rollout_join(events_path, argv_path)` — **687-745** (the gpt-6.1-sol rollout join: freeze roster,
  model/author profile, one thread + exactly one `~/.codex/sessions` rollout, model, cwd, provider,
  final message + timestamp, exec argv).
- `review_profile_problems(review, lead_id, inventory_sha)` — **748-761**.
- `validate_adoption_observation(...)` — **764-813** (the ordering window at **811-813** uses
  `provenance['rollout_final_timestamp']`).
- `adopt(events_path, argv_path)` — **816-837** (writes `lead-adoption.json`, schema
  `claude-scratch-frame-lead-adoption-v5`).
- `frame_admitted()` — **840-863** (re-joins the rollout and re-pins provenance at every use).

These are precisely the sites §23.5 ("Every dependent site") and §17 (placement row) enumerate as the
join. **Nothing outside the join was touched** — materialization, admission, reservation, launch,
spawn, observe/census, retain/result, recovery are all unchanged. The change therefore did **not**
require touching more than the join.

**v5/v6 equivalence (verified):** the whole join region is **byte-identical** in
`claude-scratch-frame-v6/scratch.py` (sha256 `2255d6e1…6884c84`); v6 only shifts it +9 lines
(`REVIEW_PROFILE` 98-103 identical; join functions at v6 696-872). The same delta transplants to v6
and to the next frame revision at the shifted offset. I patched **v5** because §23 cites v5's line
numbers (`scratch.py:98-103`, review appendix `S:687-863`) and v5 is the frozen, reviewed base.

## 2. The exact dual-form logic (as implemented in the postimage)

The form is selected by **`reviewer_kind` in the sealed `review-freeze.json`** (`review_freeze_kind()`):

- **GPT-6.1 form** — `reviewer_kind` absent or `gpt-6.1-sol`, with `actual_model_selection == gpt-6.1-sol`.
  Uses the **existing `rollout_join`, RETAINED UNCHANGED** except one added line: its returned provenance
  now carries `reviewer_kind: 'gpt-6.1-sol'`. Already-sealed GPT-6.1 reviews keep their standing.

- **Claude-subagent form** — `reviewer_kind == 'claude-subagent'`. New `claude_review_join(task_output_path,
  reviewer_agent_id)` requires **all** of (§23.4), binds each into the adoption record, and re-verifies at
  every use:
  - sealed `review-freeze.json` over **REVIEW.md / review.json / checks.json** (the 3-file
    `CLAUDE_REVIEW_ROSTER`; confirmed against the real v10/v11 Claude review freezes), each file's
    **sha256 and bytes** matching the sealed bytes, and the **freeze's own sha256**;
  - `raw-final-message.txt` present and sealed, with its **sha256**;
  - the **reviewer agent id**, bound to the identity of the sealed task-output file (requires
    `agent-<id>` in the task-output file name, the harness `subagents/agent-<id>.jsonl` convention) —
    not accepted as a bare label;
  - the **sha256 of the reviewer's sealed task output** — this **replaces** the `~/.codex/sessions`
    rollout-file uniqueness check (§23.5 item 3): there is no codex rollout for a Claude review, so the
    task-output file's bytes + the agent-id binding are the uniqueness/identity instead;
  - `reviewer_kind == 'claude-subagent'`;
  - `different_from_author == True`.

- **Neither form → REFUSES.** `review_provenance_join` returns a refusal mismatch for any unrecognized
  `reviewer_kind`; `adopt()` then fails on `adoption mismatches`. **Never a label alone** (reviewer_kind
  without the bound bytes never passes). **Never claims GPT** (a Claude review is recorded and re-checked
  as `claude-subagent`).

Downstream join sites updated to carry both forms:
- `review_profile_problems(..., reviewer_kind, model_selection)` — `actual_model_selection` is accepted
  per form (§23.5 item 13): `gpt-6.1-sol` for GPT; for Claude it must equal the sealed freeze's model
  string and `reviewer_kind` must be `claude-subagent`. Every other profile key is unchanged.
- `validate_adoption_observation` — the ordering window is preserved for **both** forms (see §3).
- `adopt(events_path=None, argv_path=None, task_output_path=None, reviewer_agent_id=None)` — dual inputs,
  dispatches via `review_provenance_join`, writes schema **`claude-scratch-frame-lead-adoption-v6`**
  (§23.5 item 7).
- `frame_admitted()` — accepts adoption schema **v5 (legacy GPT-only) or v6**, and re-joins + re-pins
  provenance by `reviewer_kind` (Claude branch re-pins the task-output file and re-checks every Claude
  provenance key; GPT branch unchanged).

## 3. The one augmentation beyond §23.4's literal list, and why (needs reviewer ratification)

`validate_adoption_observation` must order the adoption observation **after review completion** and before
the adoption record. The GPT form uses `rollout_final_timestamp`. **§23.4's enumerated Claude-form set
carries no completion timestamp**, and the sealed `review.json` (schema `claude-design-review-v1`) has no
timestamp field either (checked).

To **preserve the ordering invariant without loosening it**, `claude_review_join` **requires** a sealed
`completed_at` string in the Claude-review freeze and binds it as `review_completed_at`; the Claude branch
of `validate_adoption_observation` uses it exactly as the GPT branch uses `rollout_final_timestamp`. If
`completed_at` is absent the join **refuses**.

This adds **one required field stricter than §23.4's literal list** (never weaker). It is the single place
§23.4 under-specifies the Claude form. **Flagged for the §23.6 review:** either ratify requiring
`completed_at` in the Claude-review freeze, or specify an alternative sealed completion-time source. I did
**not** invent a timestamp or drop the lower bound — both would be wrong for a drafting author.

## 4. Author binding choices (disclosed; for the reviewer to accept or revise)

- **Agent-id binding.** The reviewer agent id is bound to bytes by requiring `agent-<id>` to appear in the
  sealed task-output file name. If the harness naming differs, the reviewer should specify the exact
  binding (e.g. an id field inside the task-output bytes).
- **Freeze-member check uses sha256 + bytes, not mode.** The real Claude review freeze records `mode` as
  the string `"0600"`, whereas `Dir.ident` returns `mode` as an **int**. §23.4 names "each file's sha256";
  I check sha256 and bytes (both integers/strings that match) and do **not** compare mode for the Claude
  form, to avoid a format mismatch that would wrongly refuse a legitimate review. Flagged for review.
- **`REVIEW` path constant.** `REVIEW = FRAME/'review/gpt61-v1'` has a GPT-specific basename. The join
  logic reads the installed review dir via this anchor and does **not** depend on the basename, so I left
  the constant unchanged (changing installation paths is outside the provenance join). Making the basename
  form-neutral at install time is a trivial **non-join** follow-up, noted here, not done in this delta.
- **Schema bump v5→v6.** Chosen over mutating v5 in place so legacy GPT-only adoption records keep their
  exact schema; `frame_admitted` accepts both.

## 5. What was NOT done (limits honored)

- The live frame files (`claude-scratch-frame-v5/scratch.py`, `…v6/scratch.py`) were **not modified**.
- Nothing was executed: no running of the frame, no prover, no tests. Only a **read-only `ast.parse`**
  (the file parsed as data; the module was never imported or run) confirmed syntax. Hashes are from
  `sha256sum` (observed tool output).
- This delta is uninstalled and grants nothing. Every Phase One obligation (V5-B01/V5-B02 confinement,
  storage admission, custody, §21 preservation rows) remains OPEN with its original owner.
