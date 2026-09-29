# Phase 1: typed absence and honest collapse inputs (1.9.0)

This closes the typed-absence item of the COSMOGONY Phase 1 authority-kernel expansion, on the
1.8.0 line, and the parts of the collapse-rule item it depends on (foreign writes, PRIME
stability, tested/staged equality).

- `Worldline.Identities` gives each identity domain its own type and an optional record with
  explicit presence.
- `Worldline.Collapse.Decide` takes those optionals, three tri-state measurements, and the
  generation and watch-set pairs, and its postcondition states the whole rule.
- `Worldline.Collapse_Wire` validates and decodes the C request in SPARK. The unproved C layer
  now only dereferences the pointer and catches exceptions.
- Python produces each input from a named source, passes what it could not establish as
  absent, and records what it passed (`decisionInputs`, `absentInputs`).

The requirement (roadmap, Phase 1):

> Represent absence explicitly for identities, hashes, measurements and evidence. Equality
> between missing values cannot satisfy a requirement.

## Requirements to contracts

Line numbers refer to `core/worldline-identities.ads` (I), `core/worldline-collapse.ads` (C)
and `core/worldline-collapse_wire.ads` (W) at this release. Every contract below is proved by
GNATprove at `--level=3` (see "Proof").

| Clause | Contract | Runtime producers |
| --- | --- | --- |
| Identities are distinct domains | Nine derived hash types and `Generation` (I:17-26). A value of one domain cannot be passed where another is expected: the program does not compile. | `CollapseInput` field names, one per request field |
| Absence is explicit | Each domain has `Optional_*` with `Present` defaulting to False (I:28-106). The wire refuses a present all-zero hash and an absent slot carrying bytes (W:72-86), so no sentinel reaches `Decide`. | `core.CollapseInput` has no defaults; `None` encodes absent; a zero digest raises INVALID_HASH before C is reached |
| Equality between missing values cannot satisfy a requirement | `Same (L, R) = L.Present and R.Present and L.Value = R.Value` for every domain (I:32-106). `All_Hold` uses only `Same` (C:192-205). | — |
| Nothing absent or unmeasured authorizes | `Decide` Post: `(Result = Authorized) = All_Hold`, and `not Required_Present or not Measured ⇒ Result /= Authorized` (C:207-215). `Required_Present` (C:135-151), `Measured` (C:125-130). | `CollapseTransaction._decide` |
| A refusal names what is actually the case | `Decide` Post, one clause per reason (C:216-264): IDENTITY_ABSENT only when something required is absent, MEASUREMENT_ABSENT only when something is unmeasured, each `*_MISMATCH`, PRIME_CHANGED and WATCH_INCOMPLETE only when both sides are present and differ (`Differ`, C:105-122). | — |
| Measurements are tri-state | `Measurement is (Unmeasured, None_Found, Found)` (C:18) for conflicts and foreign writes; generation and watch-set pairs are optional (C:69-73). | conflicts: the merge (`conflictsMeasured`); foreign writes: `_foreign_writes`; generations: the watcher; watch sets: `_watch_sets` |
| The request is well-formed or refused | `Decide_Wire` Post: 255 unless `Well_Formed`, otherwise exactly `Decide (Decode (R))` (W:251-256). `Well_Formed` (W:88-134) also requires every slot the mode or phase ignores to be empty. `Decode` is transparent (W:210-247). | `wl_collapse_decide` is a null check plus `Decide_Wire` |
| Tested and staged content are equal, or a staged evaluation covers the staged bytes | `Primary_Covers` (C:162-164), `Staged_Covers` (C:168-173), `Evidence_Holds` (C:180-189). The tested root is never overwritten. | tested root: `_tested_root` (examined root, finalized manifests, declared manifests, or absent); staged block: `_staged_block` |

### Where each pair comes from

Each pair is produced from two different records. The comments on `Collapse_Request` (C:29-74)
name them; the runtime follows them.

| Pair | Expected side | Other side |
| --- | --- | --- |
| Parent | the parent world row's own content id | the candidate row's `parent_content` |
| Evidence subject | the promotion's own arguments (candidate instance, or `return_of` with its return binding) | the speaking context's `candidate.instanceId`, and for a return the vehicle's `mission_hash` |
| Base | the candidate row's `base_root` | a capture of its base payload |
| Delta | the candidate row's `delta_hash` | the delta recomputed now |
| Root set | the registered roots | the candidate row's root set |
| Staged root | the merge's capture at prepare | a recapture at commit |
| Requirement | the current PRIME's requirement | the one the evidence was bound to |
| Verifiers | the policy's declared verifier roster | what the runner recorded it executed |
| Checkpoint | the subject's content id | the lineage child's `parent_content` or the PRIME register |
| Watch set | registered roots, resolved | roots the watcher is actually watching |
| Generation | the watcher's generation after the dirty reconcile | the same, just before the decision |

## Decisions

- **T1: owner retired, evidence subject added.** The owner pair was one computed value passed on
  both sides. `Decide` never returns OWNER_MISMATCH (code 3 is kept so no ordinal moves), and
  "owner" is reserved for requester capability (item 6b). The evidence-subject pair is
  domain-separated (`worldline-subject-v1`). On the promotion path the kernel decides whether
  the speaking evaluation belongs to this world. `verify_context` keeps the structural and hash
  checks, and the status display keeps its own binding check.
- **T2: foreign writes are measured.** The producer is the whitepaper's definition: the
  component roots of the live capture prepare (and commit) just took, against the components on
  the PRIME row. A difference is FOUND. The runtime then records an `unaccounted-write` causal
  event and marks PRIME dirty, so the next status or prepare reconciles the change into its own
  generation and a retry proceeds. A PRIME row without the components is UNMEASURED. A
  candidate carrying recorded `contamination` is FOUND.
- **T3: the watcher is required.** Without one, both generations are absent and the kernel
  refuses MEASUREMENT_ABSENT. `fork` refuses PRIME_WATCH_UNAVAILABLE at its freeze, in Python.
  A root the watcher is not watching makes the watch sets differ (WATCH_INCOMPLETE).
- **T4: the staged root is a commit obligation.** At prepare only the merge's capture exists,
  and the wire requires the other side absent. At commit the kernel compares it with a
  recapture; the Python pre-check is gone.
- **T5: no tested := staged.** The tested root is what the candidate's evidence examined:
  - a revalidation's recorded `examinedContentRoot`;
  - for a re-application, the world's finalized manifests as declared;
  - otherwise the candidate's declared manifests, and if one is missing, absent.

  When PRIME moved, a staged evaluation runs and the kernel decides whether it covers the staged
  bytes. A staged FAIL is still STAGED_UNTESTED.
- **T6: no sentinel identities.** A conflict has no staged tree: null in the record and the
  literal `"absent"` in the store's NOT NULL column. `NO_BUNDLE_IDENTITY` is used only where a
  declaration or a record states that no bundle executed; a missing key makes the whole
  executed-verifier identity absent. An unreadable kernel library or resource policy refuses
  REQUIREMENT_IDENTITY_UNAVAILABLE instead of hashing null. Two zero values remain, named and
  never handed to the kernel: `store.CHAIN_GENESIS` (the chains' first predecessor) and
  `prime.GENESIS_PARENT` (the first PRIME's parent content). Both are part of bytes already
  written, so they cannot change.
- **T7: no store migration.** Every new fact lives in the prepared transaction's JSON record
  (`recordSchema: 2`, `decisionInputs`, `decisionInputsAtCommit`). Commit refuses a record
  without `decisionInputs` (TRANSACTION_RECORD_LEGACY). Every key 1.8.0's recovery and
  listing read is kept, so a rollback still recovers.

## Defects closed (reproduced on 1.8.0 first)

One script ran five scenarios against the released 1.8.0 tree and the 1.9.0 candidate, each in
an isolated store. The script and both result files are retained with the release evidence. On
1.8.0 every scenario was AUTHORIZED and COMMITTED:

1. **An unreported write into live PRIME** went live. The receipt stated
   `foreignWorldContamination: NONE`, and no generation or causal event recorded the write.
   1.9.0 refuses it with FOREIGN_MANAGED_WRITE and records it.
2. **No watcher.** 1.9.0: MEASUREMENT_ABSENT.
3. **A watcher watching none of the roots.** 1.9.0: WATCH_INCOMPLETE.
4. **Declared manifests missing.** Whatever the payload held was treated as tested. 1.9.0:
   STAGED_UNTESTED.
5. **A staged PASS for a tree other than the staged one.** 1.9.0: STAGED_UNTESTED.

`tests/test_typed_absence.py` tests the 1.9.0 side end to end. It also covers:

- the evidence-subject cases (a context rebound with its hash recomputed, an edited return
  vehicle, an edited `returnOf`, a deleted subject);
- staging tampered between prepare and commit;
- PRIME moving during prepare and during commit;
- the conflict record;
- re-application without finalized manifests;
- the doctor census.

## Proof

`prove.sh` runs `gnatprove -P core/worldline_core.gpr -U --level=3`. It fails unless every check
is proved, none justified, with no `pragma Assume` and no GNATprove annotation of any kind. The
total must reach the floor, now `MINIMUM_CHECKS = 251`, the observed total of this release.
Each unit must list as many proved subprograms as it analyzed. `Worldline.Collapse_Wire.Decode`
and `Decide_Wire` join the required proved subprograms. `Well_Formed` is an expression function
proved with them.

**Not proved (boundary).** The C entry points in `worldline-c_api` (`SPARK_Mode => Off`) are
outside the proof: pointer dereference, exception handlers, and file and byte hashing
marshalling. So is the Python mapping of observations to the kernel's inputs. The runtime
refuses a library that is not ABI generation 5, or whose sizes or named offsets differ from
its ctypes records (selectors 0, 4 and 5 are new). `tests/test_abi_layout.py` also compiles
the header and compares every offset and code table.

**External assumptions.**

- SHA-256 is functionally correct and collision-resistant. Every identity equality `Decide`
  proves is an equality of digests.
- The runtime fills each request field from the producer named above. A value passed to both
  sides of a pair would satisfy the proof and prove nothing.
- The C header's `wl_collapse_request` layout equals `Raw_Request`. This is checked by
  name-keyed offsets at load and by the tests, not proved.
- The prepared transaction record read back at commit is the one prepare wrote. This is store
  integrity, not proved.

## What Python still decides (stated, not hidden)

- Before the kernel is asked: the VALID pre-check, INCOMPLETE_WORLD, NO_PRIME and the
  system-world refusal.
- The ancestor-of-PRIME walk.
- In `_freshness`: context integrity (EVIDENCE_CONTEXT_MISSING / INVALID), EVIDENCE_STALE, and
  VERIFIER_MODIFIED_BY_CANDIDATE, including for a staged run.
- PRIME_CHANGED_AFTER_PREPARE, CANDIDATE_CHANGED_AFTER_PREPARE, PAYLOAD_INTEGRITY_FAILED and
  TRANSACTION_RECORD_LEGACY.
- `effective_evidence` choosing which evaluation speaks for a world (item 5: a later FAIL does
  not yet supersede an earlier PASS).
- The fork's PRIME_WATCH_UNAVAILABLE refusal.
- Recovery's completion of an exchange that already happened, which commits without asking
  `Decide` again (item 7).
- PRIME changes made by reconcile and root removal. Those are not collapses.

## Non-claims

- The foreign-write measurement compares two captures. A write made and undone between them is
  not seen, and a write the watcher reported is a PRIME generation, not contamination.
- Typed absence makes a missing value refuse. It does not make a present value true: a runtime
  that states a wrong digest on both sides of a pair still satisfies the proof.
- The census in `doctor` reports what promotion will refuse. It changes nothing and repairs
  nothing.
