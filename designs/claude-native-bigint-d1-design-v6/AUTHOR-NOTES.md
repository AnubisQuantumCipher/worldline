# D1 DESIGN v6: author notes

Author: the D1 drafting subagent (Claude Code, claude-opus-5-5), 2026-10-05. Model-origin prose: a process record, not
evidence.

## 1. Package

| File | sha256 | Bytes |
|---|---|---|
| `DESIGN.md` | `fc3e3a6186f924fe07027b1d806b2ed7f85f04705232f0661c9eab5f39294e95` | 353396 |
| `APPENDIX-A-python-conversion-surface.md` | `c0acdc6d99f1490477b3f8630cf0eb4e21cbc0ac88e23d512771481728e01268` | 55361 |
| `APPENDIX-B-arow-horizon.md` | `902ac1a9d6456d1857449f1e60ca6270144f15f2aaed8e397dac93d146504db4` | 36853 |
| `jackal.json` | `61883be3bceb44f5bce5c825abe850e02eb66027f7494b43358cd5b5982c8a14` | 5260 |
| `decisions.json` | `b0b3eb63d83ab9d99c37bfc5f6a791136fa45ae3aafcefb8e7019e90c6e2c92c` | 17861 |
| `AUTHOR-NOTES.md` | this file; its hash is in the hand-back | — |

All six were created and edited only with the Write and Edit tools, in this directory. No `scratch/` folder was
needed, so none exists. No Bash command created or modified any file.

## 2. What was done

- Read in full: `D5/review/claude-v1/REVIEW.md` and `review.json` (not `raw-final-message.txt`).
- Loaded all eight Ada skills with the Skill tool before reading any Ada source in this session.
- Read only (C5): `core/resource_quantities.ads` (whole), `.adb:205-226`, `core/resource_run_ledger.ads:140-270`,
  `.adb:1-95`.
- Wrote DESIGN v6: V5-RC1 (guarded LA-9N and LA-9), V5-RC2 (LA-11's own iterative per-kind body, LR-0, PO-A35,
  RL-25E), V5-RC3 (A-ROW's final text written out in §5.12-§5.13; Appendix B re-presented with GT-01..GT-50, U-1..U-6
  and the LR-4/LR-4A derivations), V5-RC4 (F42 cost statements, RL-27, RL-25C `2E`), V5-RC5 (PO-A34 defined, W-11a
  reworded, `decisions.json`).
- Carried v5's §6, §7.1-§7.7, §10 and §11 and Appendix A; checked with read-only section diffs that only the intended
  edits differ (§10/§11 header sentences, the C12 row's history annotations, §7.4's list of ghost copies).
- JACKAL: 15 `jackal_exact` calls (K-251..K-265), one at a time or at most four at a time, with literal exponents; all
  `status=exact`, `formal=false`, `lane=rat`; no refusal.

## 3. Disclosures and deviations

1. No deviation from the lead's limits is known in v6.
2. Design choices I made beyond the RC text (all lead-owned, reversible, contract-preserving):
   - `Compare_To_Target` now has a Post (evaluated once per call), so that LR-5 is that Post and its body proof; v5
     left it Post-free with an LR-5 lemma about an opaque function, which could not have been proved.
   - New ghost helpers `Low_Quantity`/`Low_Prefix`, `Mode_Of_H`, and new lemmas LR-0, LR-6, LR-5a/5b/5c, needed to
     write the final text the inventory enumerates.
   - LA-11's v6 body is shared by A-COL, so A-COL's `E = 0` path also no longer reaches LA-7.
   - LR-4A uses up to two (D) splits per sign row; LR-4 at most one.
   - RL-27's baseline uses a two-byte parent amount (65535) so that every span is short.
3. Editorial: history annotations ("new in v5", "Found while completing (g)") were trimmed from the carried C12 row.

## 4. Adversarial pass (requested by the lead; also Appendix B.12)

Method: for each construct GT-01..GT-50 of the final A-ROW text (and `Pair_Sum_Order`), I listed every quantity span of
`Data` it passes to a Big_Integer-forming function, then built the worst originally successful direct-Ada input in each
family below and checked, by enumeration, whether the original evaluates that span at the same call (with
`Exact_Value`, which forms `256**L`). Families covered: Budget and Held rows; usage present and absent; valid and
invalid usage (including invalid spans with `Length = Byte_Count'Last`); usage greater, equal or lower than the amount;
signed operands and negative zero; `E = 0` (Length-0 amounts and target, empty `Rows`) and `E > 0`; zero-length amounts
with a long Budget usage (RL-25E); rows not selected for the current target; duplicate identities; non-default bounds;
`Both_Kinds` mixes whose mixed partial sums would exceed `2**6432`; long-span inputs on which the original itself
fails.

Result: on every originally successful family, no construct evaluates a `Data` span that the original does not evaluate
at the same call. The defects the v5 review found are closed in the text: RL-25 (the Budget usage is reached by no
construct: GT-03, GT-08, GT-10, GT-11, GT-12) and RL-25E (the `E = 0` path reaches only LR-0 on the target and the
amounts). Two non-original spans remain and are bounded and stated in U-1: `Empty_Quantity` (Length 0; forms only 0 and
`P(0) = 1`) and D1-A's own accumulator arrays (values below `256**E`). One thing the pass turned up and I fixed in the
text: v5's LR-5 was a lemma about a Post-free, non-expression function, so it could not be proved; v6 gives
`Compare_To_Target` the Post instead. This pass is a desk enumeration by the author, not an execution, a proof or an
independent review.

## 5. What I did not do

- No compiler, prover, build, test, WORLDLINE code, systemctl, sudo, project-vault or restic command. No WORLDLINE
  import. No TaskStop, kill or timeout wrapper.
- No SIA query or note.
- Did not read `R5/raw-final-message.txt`, `review-records/`, `D4/review/gpt61-*`, the lead's transcript, any other
  transcript, or `~/.local/share/sia/.gbrain/`. Did not list or stat `/home/sicarii`, `~/iPad` or `~/iPadBackup`.
- Did not select or recommend OD-1, OD-2 or any operator item, and added no gate.
- Did not modify any existing tree, earlier design or review.
- Did not re-evaluate the carried JACKAL records K-01..K-250 or re-run the Python census.
- Did not close F35: the re-presented Theorem H-A is unreviewed and unproved, and F35 stays OPEN and BLOCKING for D1-A
  (R-H-A); A-COL stays OPEN (R-F38).
- Did not resolve F32 (owned outside D1).
