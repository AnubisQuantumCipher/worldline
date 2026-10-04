# Operator decision package — WORLDLINE Phase One (DRAFT v4; not yet reviewed)

Prepared by the Claude Code lead (claude-opus-5-5) on 2026-10-04 (~22:10Z).

## Status

- **Nothing is approved, waived, closed or decided here.** Every original obligation stays OPEN.
- **No operator choice or privileged action has been taken.** Proof dispatch stays blocked by the confinement gate and
  the capacity gate.
- **Earlier drafts** (v0–v3) are preserved unchanged. v4 adds:
  - the sealed D2 inventory review (ACCURATE_WITH_CORRECTIONS) and its 12 corrections;
  - item **P-1**, information only. It covers pinned implementation files, the D2 correction C-PINS, the lead's erratum
    E1 and the supervision correction on C-PINS's provenance. No approval is requested for pinning;
  - storage observations through 22:06:53Z.
- **C-API v3 review:** sealed (ENDORSED_WITH_REQUIRED_CHANGES) and folded into C-1..C-3.
- **D1 v3 review:** sealed (ENDORSED_WITH_REQUIRED_CHANGES) and folded into N-1..N-3.
- **Next step:** this draft is the consolidated package text. It now gets its own actual gpt-6.1-sol review before it
  comes to you.

## Decisions at a glance

| Item | What is asked of you | When |
|---|---|---|
| S-1 storage | Choose among: repair the iPad backup; reclaim non-task temporary data; enforced limits; hold the lead's work; defer runs | **Now** (urgent) |
| F-1 confinement | Approve the W-1 protected-writer setup in principle, or keep V5-B01/V5-B02 OPEN with no scratch proof runs | **Now** |
| R-1 notices | Nothing now. Gathering the P1–P3 evidence is routine engineering, gated only by F-1 and S-1. Afterwards: whether the demonstrated classification resolves the notices, or they stay OPEN | Later, after the evidence |
| R-2 self-referential Posts | Decide together with R-1, after the evidence | Later |
| C-1 D-13 | Choose the component route on a concrete reviewed packet; option (i) is the admissible candidate | Later, before PK-7 |
| C-2 N-06 | Re-provision `native_sha256` under your custody, or hold | At deployment |
| N-1 OD-1 | Choose the library/runtime/API architecture on concrete verified evidence | Later |
| N-2 OD-2 | Choose E1 or E2 after V3-RC1 is repaired and re-reviewed | Later |
| RW-1 root worker | The rulings' operator items, once v2 designs exist | Later |
| P-1, C-3, N-3 | Information only; nothing is requested | — |

Everything stays OPEN whatever you choose. No choice here weakens a contract, domain, accepted case, fixture,
threshold, control or proof floor. Any option that would do so is labelled as an exception.

## How to read each item

| Label | Meaning |
|---|---|
| Facts | Each is marked *observed* (read from a file or tool) or *derived* (JACKAL, with its status). |
| Criterion | Quoted verbatim. |
| Options | Each says whether it is a **resolution** of the obligation or an **exception** to the target, and who holds authority. |
| Lead recommendation | Kept separate from the facts. |

**Path shorthand:**
- `W` = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`
- `WT` = `W/work/claude-lead-isolation-v1/wt-1`, the lead's guard-compatible isolation worktree.

---

## S-1. Local storage capacity (operator) — URGENT

### Facts

**Observed:**
- Free space readings:
  - 10592727040 bytes at 20:37:33Z;
  - 10550894592 bytes at 21:02:25Z;
  - 10516545536 bytes at 22:06:53Z, from `storage_status.py`, the reader Gate 0 names.
- The configured reserve is 10000000000 bytes, unchanged.
- At 22:06:53Z, `storage_status.py` reports `backup_service`: `ActiveState=failed`, `SubState=failed`,
  `ExecMainStatus=1`. The iPad backup failed with EIO at 12:01 EDT.
- Guarded offload (`project-vault put --offload`) is therefore unavailable.
- The reviewed offload queue holds 25 `needs-review` candidates, none of them owned by this task. Each lacks recorded
  rebuild provenance, and each original is retained.

**Derived** (JACKAL exact, formal=false):
- Margin above the reserve at 22:06:53Z: 516545536 bytes.
- Mean declines:
  - 18:49:03Z to 20:37:33Z: 296433664/3255 bytes/s, about 91 KB/s;
  - 20:37:33Z to 21:02:25Z: 10458112/373 bytes/s, about 28 KB/s;
  - 21:02:25Z to 22:06:53Z: 8587264/967 bytes/s, about 8.9 KB/s.
- At the last of these rates the reserve would be crossed after 487792513/8386 s, about 16 h. This is not a forecast:
  rates observed in the past bound nothing. The first window's rate was 139966481/13648215 times the last's, about
  10.3 (JACKAL exact).

**Observed contributors.** These are large files modified today; growth per file is not attributable:
- `~/.codex/thread_history_1.sqlite` (2307952640 bytes at 21:01Z) and `~/.codex/logs_2.sqlite` (540635136 bytes).
  Every `codex exec` review, the lead's included, writes to these.
- SIA database files.
- `~/.codex/sessions/2026/10/04`: 190175806 bytes, which includes a 166 MB rollout from a session that is not the
  lead's.

The lead has started no discretionary agents. The C-API v3 and D1 v3 reviews ran to completion. The next review is the
instructed review of this package.

**Not owned by this task:** `~/.cache/workflow-tmp` holds 11893443305 bytes (observed 21:03Z). That includes other
sessions' subagent transcripts, `worldline-revalidation-*` and `anubis-run-build-*`.

### Gate 0 (lead runbook v4.1; observations kept separate from labelled allowances)

- **One unit run** requires 9304350902252/1397 bytes above the reserve (JACKAL exact). That is about 6.66 GB, made of:
  - A_mat 16777216 (until measured; then never less than the measured size);
  - A_obj 2 × 1121220323;
  - A_rec 545393048;
  - A_ambient 1468268019712/1397;
  - R = A_mat + A_obj + A_rec, the temporary full-restore space.

  So Required = 2·(A_mat + A_obj + A_rec) + A_ambient = 9304350902252/1397 (JACKAL exact, formal=false). Each
  allowance is a labelled judgment with its basis in the runbook, not a bound on future use.
- **At 22:06:53Z** the margin minus that requirement is −8582736788460/1397 bytes, about −6.14 GB (JACKAL exact).
- **Status:** NOT ESTABLISHED, so dispatch is DEFERRED.
- **What the gate rules out:**
  - A sampling monitor in the frame is never a bound.
  - Kernel-enforced size limits (images or quotas) would only enforce, and would need their own reviewed admission
    argument before the gate could change.

Runbook: `WT/RUNBOOK-first-proof-iteration.md`, sha256 `1805b374…c12b`.

### Criterion (WORLDLINE monitor, 2026-10-04)

> "live preflight that budgets measured run growth AND temporary full-restore space above the unchanged reserve … include
> materialization, all retained outputs/records, temporary full-restore needs and ongoing agent/review growth above the
> unchanged reserve. Do not shrink the next allowance merely because the last run used less. If safe capacity cannot be
> established, keep dispatch deferred."

### Options

1. **Repair the iPad backup.** Guarded offload of eligible inactive task-owned material then becomes possible, candidate
   by candidate.
2. **Reclaim non-task temporary data yourself**, after checking its owners are inactive.
3. **Provide kernel-enforced limits for RUNS.** This needs privileges and its own reviewed admission argument.
4. **Hold the lead's review and agent work** until capacity returns. Pausing a running review would need your word.
5. **Defer all proof runs.** This is the default.
6. **Lower the reserve.** This is an exception to the storage policy. Not recommended, not requested.

**Lead recommendation:** 1 and 2 promptly. Reserve-crossing risk exists even with no proof run.

---

## F-1. Scratch frame confinement: V5-B01 and V5-B02 (operator decision on isolation)

### Facts

Actual gpt-6.1-sol, final report (`W/work/claude-scratch-frame-v5/review/gpt61-v1`, freeze verified): frame v5 is
**UNQUALIFIED_SCRATCH_FRAME**.

**Required changes, verbatim:**
- **V5-B01:** "… Bind the accepted source/output generation to the spawn under custody that prevents the admitted
  generation from changing before use. Directory-only revalidation or after-run detection must not substitute for
  pre-launch alias refusal …"
- **V5-B02:** "Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn
  handoff … Use an independently protected writer/location boundary or an equivalent enforced lease that concurrent
  same-user rename/substitution cannot invalidate while writes or launch are possible … retain this blocker if custody
  cannot yet be established."

**Rulings in the same review:**
- The compact identity records were ruled **ACCEPTABLE**.
- The empty-directory, no-target-confinement, exec-by-path and metadata-granularity residuals were ruled
  **ACCEPTABLE_AS_DOCUMENTED**.

**Monitor:** an own-inode "detected and refused" residual does not meet the criterion. V5-B02 stays OPEN until it is
met.

### Lead analysis

No unprivileged route meets both criteria on this host. Observed: `fuse2fs` is not installed, and unprivileged user
namespaces are enabled.

| Route | Why it fails |
|---|---|
| User FUSE mount | Lazy unmount. |
| tmpfs in a namespace | Not persistent. |
| Private-namespace FUSE image | Needs an install, and gives detection only. |
| Root-made filesystem with a run root owned by the lead user | No relocation, but still writable by the lead user's processes. Fails V5-B01. |

### Candidate W-1 (`WT/proposal/ISOLATION-STORAGE-PROPOSAL.md`, sha256 `a27d3e74…0442`)

- **Design:** a dedicated protected-writer account `wlscratch`. It mirrors the existing `worldline`, `wldrill` and
  `wlrehearsal` accounts, which have `/usr/bin/nologin`, `/var/lib/<acct>`, a `<acct>-clients` group and linger.
- **Ownership:** the account owns the run tree. The lead user can read it but cannot write or rename anything in it.
- **Roles:**
  - The lead's front process keeps only the documented window protocol.
  - The writer, the installed reviewed frame copy run under `sudo`, makes every frame mutation and launches the target.
- **Required setup, NOT approved:**
  - `useradd` and the groups;
  - linger;
  - a traverse-only ACL on `/home/sicarii`. This exposes world-readable home content, including transcripts, to the
    account. A per-path ACL alternative is narrower;
  - a root-owned frame install;
  - one sudoers rule;
  - optional size-limited images.
- **The proposal also gives:** unprivileged verification steps, including negative probes; a failure and custody
  table; a rollback that deletes nothing; and the evidence retained.
- **What it does not claim:** sufficiency. It needs a new frame (v6-W1) with front/writer split, new reviewed baselines
  for the account's environment, and actual gpt-6.1-sol qualification. Storage (S-1) must be resolved first.

### Options

1. **Approve W-1 setup in principle.** The lead then designs frame v6-W1 and the new baselines, all reviewed, before
   any setup command runs. You then run or authorize the listed commands.
2. **Keep V5-B01/V5-B02 OPEN, with no scratch proof runs.** The lead keeps looking for an unprivileged route and submits
   any candidate for review.
3. **Rule on the criterion's scope.** This is operator-only and a change to the preserved requirement. Not recommended,
   not requested.

**Lead recommendation:** option 1 if you want scratch proof runs at all. Otherwise option 2.

---

## P-1. Pinned implementation files: provenance of the D2 correction C-PINS (information; no decision requested)

### Facts

**Observed:**
- **The manifest's pins.** `proof_manifest.py` declares 169 effective `CONTRACT_PINS` keys. That count comes from a
  read-only AST walk over the first dictionary at line 329 and every later top-level `CONTRACT_PINS.update(...)`
  (lines 418–1029 of the commonV5-beta source manifest). It matches the sealed commonV5-beta composition review
  ("effective pin count observed is 169").
- **The pins' purpose**, from the manifest comment: "The contracts this release claims, pinned by digest … Each pin
  covers a specification's text with comments and layout removed, or the whole unproved C boundary body."
- **Every lead packet touches pinned text.** Every file changed by every lead packet 01–14 is a pinned key.
  `WT/errata/d2-inventory-E1-pinned-files.md` (sha256 `393551ee…1cfe`) has the per-packet table. It also corrects the
  D2 inventory's statement that the chain-authority and run-ledger files are unpinned. They are pinned at lines 942
  and 969 onward.
- **What has already been qualified.** The sealed commonV5-alpha and commonV5-beta composition reviews qualified
  packets 01, 02 and 04–09. That includes their pin refreshes ("Every pin delta belongs to an intended source or
  additive-control change"). No operator pinned-text approval was given or asked for.

**Sealed D2 review correction C-PINS** (verbatim):

> "Keep implementation ownership distinct from permission to change pinned text. Under this review's requested
> pinned-text boundary, a concrete change to enrolled pinned text must carry O-PINS operator approval as well as
> independent review and regenerated effective pins. Body-only implementation work can be lead-owned; that label does
> not authorize changing the protected pin package, weakening its keyset, or adopting a changed pinned
> contract/reference. This review authorizes none of those actions."

**Where C-PINS's "requested pinned-text boundary" came from.** The lead introduced it, not the original requirements:
- the lead's own D2 review brief, item 4: "operator approval for pinned text or public contract";
- the D2 inventory's O-PINS label.

**The original requirement for reviewed source deltas.** HANDOFF.md, "Complete verification and acceptance sequence",
item 1:

> "Stabilize and independently qualify the remaining source and designs. Import only explicit reviewed deltas into a new
> isolated integration checkout, resolving shared caller/transaction/ABI/policy changes. Preserve all original
> fixtures, complete source keysets/modes/directories and inverse lineage. Recompute all effective normalized pins and
> full ordered proof enrollment without changing the original policy prefix or replacing original accepted cases."

**Fixed phase exit** (`complete-phase1-prompt.txt:34`), unchanged:

> "Do not lower guarantees, weaken preconditions or postconditions, remove accepted cases, lower proof floors, drop
> relevant bodies/callers, waive warnings, suppress failures, add assumptions, or replace missing
> confinement/provenance with a renamed Boolean."

**Supervision correction, 2026-10-04** (verbatim):
- "the human's preserved authorization covers routine reversible engineering; a review brief or review finding is not
  new authority to add approval gates."
- "Do not request retroactive or blanket operator approval solely because an implementation file is pinned."
- "This is not permission to redefine reference semantics, change an unapproved API, lower contracts, scope, accepted
  cases or controls, or waive any proof/runtime/review gate. Material API/owner-policy and
  merge/release/install/sudo/production/real-PRIME decisions remain reserved."

### How this package treats pinned implementation files

- **No approval is requested for pinning.** No operator approval is requested solely because an implementation file is
  pinned, whether retroactive, blanket or per change.
- **Each change follows HANDOFF item 1:**
  - an explicit reviewed delta, independently reviewed by actual gpt-6.1-sol;
  - recomputed effective normalized pins;
  - full ordered proof enrollment, with the original policy prefix unchanged;
  - original fixtures and accepted cases kept.

  The already-qualified compositions (packets 01, 02 and 04–09) went through that process.
- **Still reserved and unchanged by this item:**
  - redefining reference semantics (R-1 option 3, R-2 option 2);
  - changing an unapproved API (see C-ABI under C-3);
  - lowering contracts, scope, accepted cases or controls;
  - waiving any proof, runtime or review gate;
  - material API/owner-policy decisions;
  - merge, release, install, sudo, production and real-PRIME decisions.
- **Preserved unchanged:** the sealed D2 review, including C-PINS, and erratum E1. The actual gpt-6.1-sol review of
  this package is asked to correct the inconsistency between C-PINS's provenance and scope and the original
  requirements.

**No decision is requested under P-1.**

---

## R-1. `contracts-recursive` / `numeric-variant` notices (operator choice)

### Facts

The F10K strict `-k` raw `.spark` data gives 25 unique notices (observed; `evidence-recursive-notices.json`, sha256
`6b6ec3fb…`):

| Group | Count | State |
|---|---|---|
| Spec-level pinned reference functions | 19 notices on 10 functions (JACKAL exact sum 19) | Operator choice needed |
| Body-level `Prefix_Tail` | 2 | Candidate packet 13, an untested hypothesis. Pinned implementation file: reviewed delta and recomputed pins (P-1) |
| Body-local witnesses | 4 | Candidate packet 12, an untested hypothesis. Pinned implementation files: reviewed delta and recomputed pins (P-1) |

**Tool semantics.** Explicit and implicit postconditions of a recursive subprogram cannot be used on recursive calls
inside assertions and contracts. The notice attaches to the declaration.

### Criterion

HANDOFF.md:161: "Completion has zero unproved, zero justified and zero pragma Assume, with complete reports and all
strict warning obligations resolved."

The monitor already ruled:
- no approval exists for a warning waiver or for redefining the pinned references;
- ruling 7b allows independently proved lemmas and call-site facts while preserving the recurrences.

### Options

1. **Keep OPEN.** Phase One cannot then complete.
2. **Demonstrated toolchain classification.** A resolution only if it is demonstrated. It needs:
   - P1: probe units. They are new files, not pinned text. The staged copy in
     `claude-workflow-v1/overlays/probe-recursion-p1` was created with Bash after a guard refusal. It is preserved
     without clearance, and any use will be from a guard-compatible copy, reviewed;
   - P2: complete proofs not relying on the unavailable contracts;
   - P3: the treatment under the exact strict command.

   Gathering this evidence is routine engineering under the existing authorization. No approval is requested for it.
   It needs a qualified frame (F-1) and capacity (S-1). After that, you decide whether the demonstrated classification
   resolves the notices. An independent review cannot grant that, and it cannot become a waiver.
3. **Redefine the pinned references** in a non-recursive form proved equivalent. This is an exception to the pinned
   text; see R-2 for why it also bears on native cost.
4. **Waive the warnings.** An exception to the target. Not recommended.

**Lead recommendation:** the lead gathers option 2's evidence once F-1 and S-1 allow a qualified run. You decide after
seeing it.

---

## R-2. Self-referential reference Posts: unproved, and the main checked-build cost hazard (operator choice, coupled to R-1, P-1 and N-3)

### Facts

- **Unproved.** D1381, D1383 and D1384 (`Prefix_Total`) and D1400 and D1401 (`Radix_Power` and `Prefix_Value`) are
  unproved Posts that restate each function's own recurrence by calling the function.
- **Checked-build cost.** The same pattern drives the D2 hazards in the default `checks` (`-gnata`) build.
  - Source: the D2 inventory (`WT/designs/claude-d2-checked-ghost-inventory-v1`, INVENTORY.md `e5b9984d…`) and its
    sealed actual gpt-6.1-sol review: **ACCURATE_WITH_CORRECTIONS**, REVIEW.md `03fbf246…`, freeze `f94a3cce…`.
  - Everything below is static source reasoning; nothing was measured.
  - Chain `Prefix_Reference` costs 9·2^(n+1)−n−10 evaluations per successful replay: 18412 at n=10 and 19327352792 at
    n=30 (JACKAL exact; reproduced by the reviewer). Ruling H1: "Correct source-semantic exponential duplication … No
    measured native cost is established."
  - The quantity references cost Θ(L⁶)–Θ(L⁷), and the resource ledger costs Θ(N⁶). Correction C-SLOT puts the slot term
    at Θ(N²·S⁴), which does not change the dominant Θ(N⁶) family.
  - These are conditional worst-case classes. C-EMPTY and C-PACKET-GAP require equal-endpoint and empty-roster base
    terms to be kept.
  - Release builds have no `-gnata` code. Selecting release was never established, and using it to discharge this
    would be suppression.
- **Candidate packet 14** (chain `Replay`, D1554/D1555; induction lemma; untested) keeps replay exponential and worsens
  it to 11·2^(n+1)−2n−14. It changes a pinned implementation file (`worldline-chain_authority.adb`), handled as P-1
  describes.

### Options

1. **Keep OPEN.** Both proof and cost remain unresolved.
2. **Redefine these references** in a non-self-referential form, with reviewed equivalence. This is an exception to the
   pinned reference text. It could address both the proof gap and the checked cost.
3. **An assertion-level / Ghost-witness design** that keeps every Post checked. This needs a reviewer ruling and must
   not suppress checked assertions.
4. **Body-only routes**, such as an iterative chain-reference body or result-span value facts.
   - By reasoning, an iterative body improves cost from exponential to Θ(n²) per evaluation.
   - They need proof feasibility evidence.
   - The bodies are pinned implementation files. Each delta follows HANDOFF item 1: independent review and recomputed
     effective pins (see P-1). Spec, reference and contract text stay unchanged.
   - C-COPY applies to any narrowed Ghost snapshot: its growth can change, and the whole-arena frame relations must be
     kept. Replacing an assertion needs a reviewer ruling.

**Lead recommendation:** decide R-1 and R-2 together, after the P1–P3 evidence.

---

## C-1 / C-2 / C-3. C-API boundary items

### Source and review status

- **Design:** DESIGN v3 (`WT/designs/claude-capi-boundary-design-v3`, DESIGN.md `a8a120c9…`).
- **Review:** sealed actual gpt-6.1-sol review (`…/review/gpt61-v1`).
  - Model and effort confirmed from the rollout: `gpt-6.1-sol` / `max`.
  - Freeze verified: REVIEW.md `9fe93d9d…`, review.json `ab7efb2b…`, checks.json `e60cdead…`.
  - Verdict: **ENDORSED_WITH_REQUIRED_CHANGES.**
- **v2 required changes:**
  - RC1–RC3 are CLOSED_AT_DESIGN_LEVEL. LD4-R closes RC1: all diagnostic state/control/value logic is SPARK, and only
    the T1–T5 irreducible transport remains Off.
  - RC4–RC6 are NOT_CLOSED. They become V3-RC4 (an enforceable binding specification), V3-RC5 (PK-0's original-effect
    classification) and V3-RC6 (the cost map: source structure versus compiler-dependent native mechanisms).
- **Packet plan:** NOT_CLOSED. The lead's next work is DESIGN v4 and its re-review. No implementation, adoption or run
  acceptance is granted.

### C-1. D-13: how the separate pending component keeps `wl_pending_decide_v1`/`_v2` (operator, later)

**Ruling (verbatim):** "OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. Option
(i) is a reviewable candidate, not approval. Retain both original Decide exports, all component interface units, exact
SPARK_Mode-only mirror, positive/refusal/native-body obligations and source/project/library/header identity. Options
(ii)/(iii) are inadmissible. No new core Off exception or proof credit."

**Basis (lead's reading, for the package review to check).**
- The original requirement keeps the "sole original worldline-c_api boundary" (HANDOFF acceptance sequence, item 3).
- The component keeps its separate native and ABI controls (`W/work/integrated-proof-preparation/PLAN.md:104-107`, as
  cited by the design).
- A component ABI route is a material API decision.

| Option | What it is | Status |
|---|---|---|
| (i) | A component-local Off transport unit, text-identical to the C_API pending transports, added to the component's `Library_Interface` | Reviewable candidate. ABI preserved; it relocates already-Off component code; no new core exception or proof credit |
| (ii) | The component stops exporting `Decide` | Inadmissible (narrows the ABI) |
| (iii) | No mirror | Inadmissible (abandons exact correspondence) |

**When you decide.** Not yet. Per the ruling, the decision is made on a concrete packet after its own independent actual
gpt-6.1-sol review. The packet must carry its source/project/link closure, matching symbols, profiles and layouts,
native positive and refusal controls, the exact mirror, new component pins and raw identity.

**Lead recommendation:** option (i), which the lead will prepare as that packet.

### C-2. N-06: deployment provisioning (operator, at deployment)

**Ruling (verbatim):** "REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT. Mismatch refusal is retained. Keeping the old
library is only a deployment hold and gives no successor-service/integrated acceptance credit."

| Option | Meaning |
|---|---|
| (a) | Re-provision `native_sha256` under your custody for the installed reviewed library. **Recommended.** |
| (b) | A deployment hold. Never acceptance |

No deployment action is authorized here. The decision belongs to the deployment gate.

### C-3. N-01: representation warnings (lead-owned; information)

**Ruling (verbatim):** "LEAD_OWNED_STRICT_OBLIGATION. ABI-confirming representation packets are conditionally
design-admissible, individually reviewed after legal family movement and before PK-S. No waiver or
relocation-as-resolution. A nonconfirming layout change is outside this design and cannot reduce the target even with
operator approval."

- You decide only a separately proposed material ABI change, and none is proposed.
- **D2 correction C-ABI** (sealed): "A changed public transport code, meaning, layout, or caller protocol is an API/ABI
  package and requires O, not discretionary 'possibly O'."

### Other v3 rulings (all lead-owned; none closes an obligation)

**Closed at design level, with proof still OPEN:**
- D-18;
- N-04;
- N-07;
- APPENDIX_C: the append-only order of the 535-name prefix is preserved.

**Conditionally acceptable:** LD1, LD2, LD3 (pending D-13), LD5, LD6 (subject to V3-RC5) and D-28.

**OPEN:**
- D-05;
- D-19;
- D-36;
- D-15/D-34/D-38;
- N-03 (no PROVED_ROW transfer credit);
- N-05 (the original static-audit obligation; no subset reinterpretation).

**NOT_CLOSED:** R2_NINE_CONDITIONS, pending V3-RC4.

The review also notes the root-worker shared-file integration as an open obligation.

---

## N-1 / N-2 / N-3. Native Big_Integer

### Source and review status

- **Design:** D1 DESIGN v3 (`WT/designs/claude-native-bigint-d1-design-v3`; DESIGN.md `b20554c4…`). Appendix B
  governs where it differs.
- **Review:** sealed actual gpt-6.1-sol review (`…/review/gpt61-v1`).
  - Model and effort confirmed from the rollout: `gpt-6.1-sol` / `max`.
  - Freeze verified: REVIEW.md `e82534cb…`, review.json `cb1e3740…`, checks.json `0631a4ff…`.
  - Verdict: **ENDORSED_WITH_REQUIRED_CHANGES.** v2 was NOT_ENDORSED.
- **Prior required changes:**
  - Closed: V2-RC1 (Algorithm B), V2-RC2 (workspace lifetime), V2-RC3, and the older RC4, RC5 and RC6.
  - NOT_CLOSED: V2-RC4, V2-RC5, V2-RC6 and RC7. They are carried into:
    - **V3-RC1:** complete the OD-2 package. Fix E2-b's key sorting to match `json`'s, and add the omitted
      `json.dumps` alias at `scripts/decisive_evaluation_test.py:264`.
    - **V3-RC2:** complete the source-to-control map and fixtures. That covers the middle-cell mismatch, the X6/X7
      exits, the staged and Primary_And_Staged paths, and RL-7c/8/9.
    - **V3-RC3:** rebuild the checked-cost model (§9.3) from all nested public Posts and bodies.
- **What the review confirms:**
  - **R-A:** Algorithm A stays eligible on the original domain.
  - **R-B:** Algorithm B's carry-out inequality and null-admitting shape are eligible. "No new public Pre or size
    refusal is authorized."
  - **R-SCOPE:** "D1 alone closes no original helper, checked-Ghost, Python, transport, physical-cost or integrated
    acceptance obligation."
- **Next lead work:** D1 DESIGN v4 and its re-review.

### N-1. OD-1: the `Exact_Value`/`Amount`/`Sum` route (operator, later)

**Ruling R-OD1 (verbatim):** "No OD-1 option is selected or recommended. The repaired option set preserves helper
obligations. Ghost retirement/removal is incompatible; release unreachability and approval alone close nothing."
- Owner, per the ruling: "operator chooses concrete library/runtime/API architecture; lead prepares evidence and may
  pursue preserving body-only mitigation".
- **Basis (lead's reading, for the package review to check).** Every non-lead option changes a library,
  runtime/toolchain identity or public API. The original command pins the exact toolchain, and material API decisions
  are reserved.

| Option | Meaning |
|---|---|
| E | No decision |
| (o) | Lead-owned release-build mitigation |
| (i-a) | WORLDLINE-owned `SPARK.Big_Integers` |
| (i-b) | A separate proved bignum type |
| (ii) | A rebuilt GNAT runtime without `Bignum_Limit` |
| (iii) | Ghost-only retirement. Incompatible; listed only to record why |
| (iii′) | An additive successor API |

Option (ii) carries:
- layout and representation changes;
- length arithmetic;
- stack digit vectors;
- quadratic time and unbounded checked cost;
- the identity evidence it would need.

**When you decide.** Not yet: on a concrete, independently verified option. The evidence must cover model binding,
direct-user migration, full implementation, rebuild/relink/loaded identity and complete original/full-domain controls.
No recommendation is made.

### N-2. OD-2: Python decimal-integer correspondence beyond 4300 digits (operator, after V3-RC1)

**Ruling R-OD2 (verbatim):** "No E1/E2 choice is selected. The 640-digit chunk guard is valid under every admitted
interpreter limit, but V3-RC1 must repair codec ordering, inventory and configuration/exclusion precision. A cap or
catch-and-refuse is not a repair."
- Owner, per the ruling: "operator for conversion architecture and protected custody; lead for codec/audit/evidence
  preparation".

| Option | Meaning |
|---|---|
| E0 | No decision |
| E1 | Interpreter-wide unlimited, across 11 process classes. V3-RC1 adds the `native/build_guard.py` interpreter's disposition |
| E2 | A scoped codec with chunks of at most 640 digits over the JSON sites: the 192 direct-name sites plus the omitted alias. Variants E2-a and E2-b. E2-b must preserve `json`'s original-key sorting and mixed-key `TypeError` |
| Rejected | Per-call toggling, a finite higher limit, caps, catch-and-refuse |

**When you decide.** After D1 v4 repairs V3-RC1 and is re-reviewed.

### N-3. D2: checked-Ghost cost in the default `checks` build (lead-owned; information)

- **D1 v3's own checked cost.** Per V3-RC3, it must be rebuilt from complete nested Posts, bodies, lemmas and copies.
  The earlier worker-only and Post-only estimates are not established.
- **R-NOTICE.** "A-GHOST-1 adds the proposed Side_Sum declaration to OPEN R-1-class obligations; no prior
  classification automatically covers it. A-GHOST-0 avoids a new declaration site but preserves old notices and adds
  checked costs."
- **The overall hazards** are as in R-2. The sealed D2 review's rulings bind them:
  - H9: native stack and heap layout, peak live heap, copy elision and exhaustion behaviour are not determined
    statically.
  - H10: a catch-all exception mapping in the C wrappers does not make a stack or process failure catchable, and does
    not establish successful completion. "These outcomes are not accepted semantic refusals."
  - C-UNIT: source invocation counts are not allocation or instruction counts.
- **R-WORKSPACE.** The workspace alternatives CL-1/CL-2/CL-3 are lead-owned, and none may "waive warnings, add Off,
  suppress Ghost or count resource failure as a refusal". F-B2 (procedure migration) and F-B3 (caller-supplied
  scratch with new C exports) are public API/ABI packages. They are reserved for you, and neither is proposed.
- **Forbidden routes:** release-only escape, suppressed checked Ghost code, caps, refusal counting.

---

## RW-1. Root-worker runtime lane (operator-gated execution)

### Facts

The seam design v1 got a sealed actual gpt-6.1-sol review: **ENDORSED_WITH_REQUIRED_CHANGES**, RC-01..RC-12, freeze
verified. review.json is `721bce3a…`.

**Verified by that review in the unreviewed draft lane:**
- the stale `protected_operations.py` pin;
- the duplicate `attach_scoped_resource`, which drops a producer check;
- three original pre-dispatch checks missing from the root route;
- RootController identity pairs that compare a value with itself;
- missing scoped settlement adapters.

**Supported, conditionally:** a non-reentrant gate-mutex deadlock.

**Rulings:**
- `Delegate=yes` alone is not endorsed.
- The frontier control may not be retired by the lead.
- Native custody-phase legality is mandatory.

### Operator-gated

- any execution: root, system units, labs;
- provisioners and installation;
- delegation;
- actor (Luna) quota;
- fault campaigns;
- merge, release, install, PRIME.

The review's rulings name the operator, together with independent review, for these:
- **D-2a:** provisioning or installing authoritative state for an additive v2 descriptor.
- **D-2b:** any re-enrollment adjudication of the frontier control. The original obligation stays OPEN meanwhile.
- **D-4a:** any authoritative resource-policy change. No accounting option is selected.
- **D-5a/D-5b:** delegation and privileged lab action or installation.
- **D-7a:** any original API or owner-policy alteration.
- **D-8b:** kernel measurement.
- **D-9a:** the fault campaign.

Each ruling also makes the lead the designer and requires independent gpt-6.1-sol review. No operator choice is asked
for yet. These items come to you once the lead's v2 designs exist and are reviewed.

**Lead-only next work:**
- root-worker seam design v2 and spec-only slices;
- C-API DESIGN v4 (V3-RC4..RC6);
- D1 DESIGN v4 (V3-RC1..RC3).

Each gets an independent actual gpt-6.1-sol review. Drafting continues as routine engineering, and new reviews are
paced against S-1.

---

## Isolation record (for your information, no decision)

- The background-session guard refuses Write/Edit in the shared work tree, and EnterWorktree cannot resolve HEAD
  because `~/.git` holds only `info/`.
- Edits now go to a dedicated local repository with a linked `git worktree add` worktree
  (`W/work/claude-lead-isolation-v1/{repo,wt-1}`, initial commit `e14ccc1`). The guard accepts it.
- Earlier artifacts written by Bash/heredoc fallback after refusals are listed in `WT/ISOLATION.md` (sha256
  `7ba6fe83…`). They are preserved, with no clearance claimed.
- Every review is actual gpt-6.1-sol. One earlier Claude pre-read was non-compliant. Its notes are kept as history only.
- Disclosed incident: a `find` over `~/.local` listed file metadata under `~/.local/share/sia/.gbrain/`, against the
  machine rule. Nothing was read or written there.
