# W-1 v11 independent design review (ISOLATION-STORAGE-PROPOSAL-v11.md)

**Reviewer:** an independent Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review and I am not the drafting agent. This is a design review on W-1's own design-review track; v6/v7 (gpt-6.1-sol) and v8/v9/v10 (independent Claude subagents) were all NOT_ENDORSED.

**Verdict: NOT_ENDORSED.** This review grants no acceptance, approval, exception, proof acceptance, phase acceptance or source acceptance. Every original Phase One obligation stays OPEN with its original owner, release and dependencies. The three form/bookkeeping required changes from the sealed v10 review (W1-V10-FORM, W1-V10-COUNT, W1-V9-REVIEW-PROVENANCE residual) are all correctly and completely RESOLVED in v11, and nothing else changed from v10's spec-closed content; but v11 is a narrow form revision that establishes no substantive obligation, so the design is not endorsable for the same reasons v10 was not — the core confinement obligations remain OPEN and adoption stays blocked.

**Hashes (computed by this reviewer):**
- Brief `briefs/w1-design-v11.md`: sha256 `7595264e8b270e797e43131b86d3e44be037c588f29bc6efdd3e43192083e634`, 7807 bytes.
- Override `scratchpad/review-override-v2.txt`: read in full; item 6 shell hygiene applied (no file written anywhere, no stdin-reading command, no backgrounding, `command ls`/os.listdir only, all Python via `python3 -c`).
- v11 under review: `aac18b67144c18b22c83d739a3fd4c5cff0d2a91eca75a64858d4b791cf637aa`, 576903 bytes, 5389 newline-terminated lines (single trailing newline). Matches the brief and jackal.json:5-8.
- `v11-support/jackal.json`: `4fae39d5da081643a14b0225a52aecea045c19bf6ce4298fff8eaf7a0c261d4b`, 10640 bytes. Matches the brief.
- v10 base: `d5fe8f3152dd8782adeee65478d7f70fb06e5fac50f0b17943d53598da66d8ef`, 111456 bytes. Matches the brief and v11:28-29.
- v9 base: `4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b`, 562201 bytes, 5143 lines, 134 units. Matches the brief and v11:25-27.
- Sealed v10 review `proposal/v10-review/claude-v1`: REVIEW.md `81419b7a6a830b78d6232412dfe686b9bb8ca9706f120a0caa1e1bd2fa515833`, review.json `ac21f21fba63c862c9503cf0f2bfe89d6d603fb33a9c65376c530f3ff7f7c01f`. Both match the brief and v11:6-8; read in full. Reviewer agent id `aae3a07f9c8701b8e`, task-output sha256 `91f6cf7d577f30cce3a8caa54dabc1d764c1d7d19611003f4467bc3d3f6a60b8` (review.json `sealed_by`).
- Sealed v9 review `proposal/v9-review/claude-v1`: REVIEW.md `51e80795e688bc11df156d47ca86646da45be0dce41659db3a36cddfeb851637` (read in full), review.json `050ef9d7cf3978bc7b7c8fd98d347a969808e248921bec4225404904bd3fef51` (hash computed; its nine required changes are quoted verbatim in REVIEW.md:198-200 and carried by the v10 review).

**Independence and limits.** I did not read: any v11 review directory, `review-records/`, `review-records/live/`, any gpt61-v* directory of this revision, drafts in progress, or any session transcript/rollout; I did not read `~/.local/share/sia/.gbrain/` and did not list or stat `/home/sicarii`, `~/iPad` or `~/iPadBackup` (the SIA MCP server was also disconnected this session; no SIA query relied on). Nothing was executed but passive reading, read-only hashing/unit-parsing in Python (`python3 -c`, no file written), and JACKAL (MCP) calls. No WORLDLINE/COSMOGONY/frame code, prover, compiler, sudo, systemctl, unshare, mount, project-vault or restic was run. Kernel behaviour I could not verify against installed source is not re-derived; v11 re-fetched no kernel/systemd/sudo source and relies on v9's dated observations under P-KSRC (v11:50-52, 5205-5218), which I did not independently re-derive.

**Sensitive-area handling.** Per the brief and override I judged W1-V9-ASYNC-ENUM and every privilege-boundary probe only as OBLIGATION + ENTRY-RULE + discharge/refute PREDICATE. I did not request, write or reward any step-by-step procedure or exploit detail. v11 keeps that discipline verbatim from v10 (v11:39-45, 4095-4097, jackal.json:79).

---

## 1. W1-V10-FORM / self-containment — RESOLVED

**Method.** I re-parsed the assembled v11 file by the §0.1 unit rule (v11:67-69: a unit begins at each `# `/`## `/`### ` line outside fenced code and runs to the line before the next; bytes are those lines with terminators; the file ends with exactly one trailing newline). I then did a **full scripted parse of Part V11-MAP (§V11-C.3, v11:5250-5389)** — not a sample — and checked every row against the file.

**What verifies (scripted, zero mismatches):**
- The whole-file sha256 over the assembled bytes equals `aac18b67…` (jackal.json:5, v11:5 title area). Confirmed byte-for-byte.
- v11 parses into **140 physical units** = 136 spec units + the 4 Part-V11-MAP apparatus headers.
- **All 136 §V11-C.3 rows**: for every row the stated v11 line range, read from the file, produces exactly the stated byte count and the stated v11 sha256. **Zero mismatches across all 136 rows.**
- The 136 rows' line ranges **tile the file contiguously** from line 1 to 5221 with no gaps and no overlaps; the only physical units not in the map are the 4 apparatus headers (5222-5223, 5224-5234, 5235-5249, 5250-5389), whose identities match `jackal.json:66-71` exactly (bytes and sha256). This is the "only identities not inside the file are the map apparatus + whole-file hash" requirement (v11:5232-5233, jackal.json:63-72).
- **All 100 CARRIED units are byte-identical to v9**: for each the stated v11 sha256 equals the stated v9 sha256, AND the actual v11 unit bytes equal the v9 file's unit bytes for that sha256 (checked against an independent parse of the v9 file into 134 units, all 134 shas distinct). Verified for all 100, not a sample.
- **23 AMENDED** and **11 COMPOSED** units each carry a computed v11 sha256 that matches the file (verified above). The 23 AMENDED labels are exactly 2.2, 2.3, 4.2, 4.6, 5.3, 6.1, 8.1, 8.6, 9.1, 9.3, 9.8, 10.6, 11.3, 11.4, 11.5, 11.6, 12.2, 12.3, 15.3, 17, 21.3, B.3, App. D (v11:5240-5241); the 11 COMPOSED are title, §0, §0.1, §13, §13.1, §13.2, §16, §16.1, §20, §18.5, App. I (v11:5246-5247). The 2 NEW are §0.7 and §23.

**Normalization rule (part (a) of the v10 required change).** §V11-0.1 states it (v11:83-92): the quoted anchor is matched against v9's bytes read as if soft-wrapped; the replacement is re-wrapped to ≤118 bytes at spaces, preserving v9's indentation, list markers, backticks and the single `\n` per line; append/insert-rows placements are specified; every other byte is v9's. Because v11 now **materializes** every AMENDED unit's bytes and pins each with a computed sha256 in the map, reproducibility is no longer load-bearing — the actual bytes are present and hash-verified — and the rule is correctly stated as the documented method. This directly discharges the v10 review's part (a) and eliminates its underlying concern (unmaterialized/un-byte-pinned AMENDED bytes, v10-review REVIEW.md:85, 112).

**Appendix-I off-by-one (part (b)).** Resolved. v11's Appendix I (COMPOSED, v11:5181-5221) is **no longer the last unit** — Part V11-MAP follows it — so it carries its own computed v11 sha256 in the map (verified above) and embeds no inline whole-file self-hash; the whole-file identity is recorded in `jackal.json:65`. The v10 defect (Appendix I recorded 3189 bytes but was 3188, v10-review REVIEW.md:83) does not recur. §18.5 (v11:4059-4066) is a short pointer to Part V11-MAP, explicitly placed last to avoid the self-reference cascade.

**W1-V8-FORM-SUBUNIT is RESTORED** (no longer regressed): v11 is a single self-contained specification with every unit materialized and a per-unit v11 sha256 (v11:31-37, 71-81; §20 bullet v11:4111-4115). This answers the brief's §5 question.

## 2. W1-V10-COUNT — RESOLVED (JACKAL-confirmed)

The partition is now correct and internally consistent across Part V11-MAP (§V11-C.3), §V11-C.2 (v11:5235-5248), §18.5/§0.7 (v11:218-223) and `v11-support/jackal.json` (`jackal_results` lines 37-48; `v11_unit_partition` lines 49-62):
- The **corrected v10 partition is recorded**: 100 CARRIED, 23 AMENDED, 9 COMPOSED, 2 SUPERSEDED = 134 (I4′); changed = 23+9 = 32 (I4″); v10's wrong 101/22/"31" is named as the defect (v11:5237-5239, jackal.json:43-44).
- The **v11 partition it actually produces**: the 2 formerly-SUPERSEDED units (v9 §0.1, v9 §18.5) are materialized as COMPOSED, giving 100 CARRIED, 23 AMENDED, 11 COMPOSED, 0 SUPERSEDED = 134 (I5′), changed-from-v9 = 23+11 = 34 (I5″), plus 2 NEW (§0.7, §23) = 136 total v11 spec units (I6′) (v11:5243-5248).
- My scripted row count = exactly 100 CARRIED / 23 AMENDED / 11 COMPOSED / 2 NEW = 136. Matches.
- JACKAL (status `exact`, lane `rat`, NOT formal-bounded, informational) confirms every sum: `100+23+9+2`=134; `23+9`=32; `100+23+11`=134; `23+11`=34; `100+23+11+2`=136; `1+1+1+1+1+1+1+1+1`=9 (the nine v9 required changes, I3′). All match the document and jackal.json.

## 3. W1-V9-REVIEW-PROVENANCE residual — RESOLVED

The prompt source path is corrected to `/home/sicarii/Documents/complete-phase1-prompt.txt` at **every** cite site: v11:49 (title/§0 input line), v11:210 (§0.7 item 8), v11:3911 (§16 step-9 closing paragraph), v11:4324 (§23.3 quoted original text), v11:5208 (Appendix I inputs). A full-file grep finds **zero** remaining `outputs/complete-phase1-prompt.txt` citations. `HANDOFF.md:173` stays correctly under `…/outputs/claude-phase1-handoff-20261004/` (v11:50, 4320, 5207, and paired at 3911). The v10 review named three defective sites (v10:58, 467, 1085); v11 corrects their v11 counterparts and the superset. §23 is otherwise unchanged from v10's spec-closed state: my byte-diff of §23 (v10 vs v11) shows only the path correction (re-wrapped, same words and line :60) and the "v10→v11" version label (v11:4299-4360 region; diff hunks at v11:4324 and the §23.6 adoption sentence). The quoted ~17:05Z authority, the 14 dependent sites, the precise replacement join and "adoption blocked / not a loosening by assertion" are all carried unchanged.

## 4. Nothing-else-changed (vs v10 spec-closed content; vs v9)

- **CARRIED (100):** byte-identical to v9 (§1). No spec-closed answer carried as CARRIED can have changed.
- **AMENDED (23):** each v11 unit = v9 unit + only the documented v10 Part-V10-A edits. I diffed a sample well beyond the brief's ≥5 (2.2, 2.3, 5.3, 6.1, 8.1, 9.3, 9.8, 10.6, 11.4, 11.6, 12.2, 21.3) against v9: every hunk is additive and matches the documented edit — e.g. §2.2 appends the RL-SELFTEST-FIXTURE sentence (v10 A-§2.2); §8.1 `role-identity-v1`→`-v2`; §11.6 candidate baseline → "evidence only … never a comparison baseline"; §9.8 (+30/-9) and §11.4 (+40/-13) are the documented ASYNC-ENUM and ENUM-USERDEL amendments (67/104 counts and "held-but-unusable" preserved). No deletion or shrink beyond the documented edits; no obligation, fixture, control, threshold, accepted case or join weakened.
- **COMPOSED spec-closed (5):** §13, §13.1, §13.2, §16, §16.1 diffed v10 vs v11 — §13.1 and §16.1 **byte-identical**; §13/§13.2/§16 differ **only** by "v10"→"v11" version labels and (§16 only) the one provenance-path fix. No spec content altered.
- **COMPOSED bookkeeping (6):** title, §0, §0.1, §18.5, §20, Appendix I legitimately carry the COUNT/FORM/PROVENANCE fixes. §20 diff (v10 vs v11): only version labels, the added `W1-V10-COUNT` corrections tag, and the W1-V10-FORM bullet rewritten from "OPEN regression" to "resolved" — the non-claim still states it weakens no obligation/fixture/threshold/accepted case/join (v11:4111-4115). §18.5 is reduced to a pointer; Appendix I is v11's.
- The sensitive async/privilege material (ASYNC-ENUM obligation+predicate, NOOWNER-SCOPE, ENUM-USERDEL 67/104, PLAN-CONSTRAINTS, PREMISE-ORDER, RL-SELFTEST-FIXTURE, INVENTORY V15-V17/fd-set) is carried unchanged; the detailed procedures stay operator-reserved and OPEN (v11:39-45, 231-235).

## 5. Prior closures stay; execution-bound and core obligations stay OPEN

- The **eight CLOSED_AT_SPEC_LEVEL** items from the v10 review (ASYNC-ENUM, NOOWNER-SCOPE, ENUM-USERDEL, PLAN-CONSTRAINTS, PREMISE-ORDER, RL-SELFTEST-FIXTURE, INVENTORY, plus FORM-CONSISTENCY now fully closed since the COUNT miscount is fixed) stay closed in substance — their carrying units are CARRIED byte-identical or AMENDED-only-as-documented (v10-review review.json:11-20).
- The carried **execution-bound** W1-V8-PRESERVATION-ESTABLISH, W1-V8-PREMISE-DISCHARGE, W1-V8-EVIDENCE-EQUIV stay OPEN (v11:234-235, 4088-4090; jackal.json:81); V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE, Gate 0 and all 219 `OBLIGATIONS-v2.json` entries stay OPEN (v11:17-21, 54-59, 4088-4090).
- The §23 join change (D-LEAD-REVIEW-PROVENANCE) **stays an unreviewed change**; adoption stays blocked until the frame-design revision reviews it (v11:57-59, 3908-3911 [§16 step-9 paragraph], §23.6, §20 bullet v11:4108-4110).
- W1-V8-FORM-SUBUNIT: RESTORED (§1).

## 6. Anything else that would weaken a contract/domain/case/fixture/control/threshold/proof floor, add an assumption or gate, or present an unverified premise as fact

- None found. v11 adds no approval gate (v11:4106-4107); every privileged element stays inside the existing reserved operator authority (§16.1). The form self-containment is a tightening, not a weakening. No premise is presented as fact: every N7 premise is NAMED_UNESTABLISHED (v11:54-56, 4093), probes refute only, and the JACKAL arithmetic is correctly carried as `exact` (lane rat, NOT formal-bounded, informational, no capacity/geometry/correctness claim; v11:4101-4103, jackal.json:21-35, 85).
- The v11 partition classification (v9 §0.1 and §18.5 → COMPOSED; the v10 NEW §V10-0.1 form content now lives in the COMPOSED §0.1 occupying v9 §0.1's slot, so NEW drops 3→2) is internally consistent and loses/double-counts no unit (136 map rows = 100+23+11+2; whole-file hash verified).

## Why NOT_ENDORSED

The three form/bookkeeping defects the v10 review required are correctly and completely fixed, and nothing else changed — this is a clean narrow revision. But a form revision cannot make an open-obligation design endorsable:
1. The core confinement obligations are unestablished and deferred: V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE and every N7 critical premise (P-KSRC, P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC) stay OPEN/NAMED_UNESTABLISHED; v11 establishes nothing (v11:19 "v11 closes no obligation by itself").
2. The execution-bound W1-V8-PRESERVATION-ESTABLISH / -PREMISE-DISCHARGE / -EVIDENCE-EQUIV remain required and unperformed; the P-ASYNC containment stays a closed specification whose completeness is itself unestablished.
3. The §23 review-provenance join change is not reviewed, so the design cannot reach adoption.

I grant no acceptance of any kind.

## Required changes (none weakens any obligation; the three v10 form items are now CLOSED, not re-listed)

- **W1-V8-PRESERVATION-ESTABLISH** (execution-bound, still required): establish §21 for every OPEN V/C/D row, or redesign (v11:4117-4178, §13.2).
- **W1-V8-PREMISE-DISCHARGE** (execution-bound, still required), in the W1-V9-PREMISE-ORDER order (critical-premise E0 discharge review before O-1; S-1 binds the running kernel image/build-id).
- **W1-V8-EVIDENCE-EQUIV** (execution-bound, still required): B1–B5 for U-14/I-6; safe fresh capacity OPEN.
- **D-LEAD-REVIEW-PROVENANCE / §23**: the join change must be reviewed in the frame-design revision before any adoption relies on it; adoption stays blocked until then.
- V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE, Gate 0 and all 219 `OBLIGATIONS-v2.json` entries stay OPEN and are not narrowed.
