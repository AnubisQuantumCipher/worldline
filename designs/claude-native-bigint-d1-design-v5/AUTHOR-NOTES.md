# D1 DESIGN v5: author notes

Author: the D1 drafting subagent (Claude Code, claude-opus-5-5), 2026-10-05. Model-origin prose: a process record, not
evidence.

## 1. Package

| File | sha256 | Bytes |
|---|---|---|
| `DESIGN.md` | `5994b2436376d71d8cbf6eb8c90f2c1c601244d6c239872f604c469046a11ebd` | 314808 |
| `APPENDIX-A-python-conversion-surface.md` | `11cad97d194d90e8e7c16ffbac6e61221fd4d0c9fec2ff3f00094826ffd07f98` | 55237 |
| `APPENDIX-B-arow-horizon.md` | `b588941d059d7e9c6a8679714b0873faad1bb54faf8407665c53fbc1ddd71fc4` | 17815 |
| `jackal.json` | `edbdc9dee50a8b4fb630fab89d272c92f2f52c39bf996edb64cd4dabf5f99195` | 8138 |
| `decisions.json` | `fd470295050c0bac53ed176f4c46450dbaefe94b9c58b6d2b6a28b262fc70396` | 28140 |
| `AUTHOR-NOTES.md` | this file; its hash is in the hand-back | — |

All six were created and edited only with the Write and Edit tools, in this directory. No `scratch/` folder was
needed, so none exists. No Bash command created or modified any file anywhere.

## 2. What was done

- Read in full: the sealed v4 review (`D4/review/claude-v1/REVIEW.md`, `review.json`, `checks.json`) and the lead's
  deviation record (`WT/deviations/d1v4-drafter-tmp-file/NOTE.md`, `claude-jk-table.txt`).
- Read only, for the RCs: C5 sources cited in DESIGN.md (`core/worldline-identities.ads`, `core/worldline-collapse.*`,
  `runtime/worldline/core.py`, `core/resource_run_ledger*.ad?`, `core/resource_quantities.ad?`,
  `native/build_guard.py`) and `/usr/lib/python3.14/subprocess.py`.
- Wrote DESIGN v5: V4-RC1 in both engines; V4-RC2 (a)..(h); the A-ROW engine with Theorem H-A (DESIGN.md §5.12-§5.16,
  Appendix B); F37, F38, F39 and the A-COL mixed-partial-sum observation; new POs, costs, failure rows, controls and
  OPEN items. Carried v4's §6, §7.1-§7.7, §10, §11 and §15 with the listed edits.
- JACKAL: 38 `jackal_exact` calls (K-213..K-250), one at a time or at most four at a time; all `status=exact`,
  `formal=false`, `lane=rat`; no refusal; K-227 and K-232 not relied on. One of my own mental estimates (3·T(803)) was
  wrong before the call; the design uses only JACKAL's value (K-228).

## 3. Disclosures and deviations

1. **v4 `/tmp` file (V4-RC2 h).** v4's AUTHOR-NOTES §3 and `decisions.json` said `/tmp/claude-jk-table.txt` was "left in
   place". That was stale: the lead copied it to `WT/deviations/d1v4-drafter-tmp-file/claude-jk-table.txt` and removed
   the original (`NOTE.md:15-17`). v4's files were not edited; DESIGN.md §2 and `decisions.json` record the correction.
2. **v4-era read of the lead's transcript (first disclosure).** During v4 drafting, before the lead named my own
   subagent transcript as the only one I may read, I ran a read-only grep over the lead's top-level transcript
   `0e157c30-4700-4604-ab0e-cc6c3b9c6c37.jsonl` for the strings `12N+13` and `u_all`. It is a read the lead's limits now
   forbid. It was not repeated, and nothing from it is used in v5.
3. **Own transcript after compaction.** After a context compaction I read my own transcript
   (`subagents/agent-a46a0376f825ad165.jsonl`) read-only with `grep` and `python3`, to recover my JACKAL calls exactly.
   That is the permitted file. The JACKAL ledger was not used as a source.
4. **Scope additions I made beyond the RC text** (all lead-owned, reversible, contract-preserving):
   - A-ROW as the primary engine (R-F35 asked for a candidate; A-GHOST-2 does not work, F38).
   - LA-10 restricted to per-kind calls in A-ROW, after finding that its `Both_Kinds` form creates mixed partial sums.
   - C12 inventory item (5) (interpreter diagnostics of other uncaught exceptions), found while completing (g).
   - R-OVR condition 1 classifies by `type (v)` rather than `isinstance`, because a false `__class__` would make
     `int.__abs__` raise inside the pre-scan.
   - Cost coefficient for A-ROW raised from `N·n_s + 5·n_s` to `3·N·n_s + 6·n_s` after adding the LA-10 calls.
   - Wording: v4's "GPT-6.1 review" mentions in §10 and §13 now say "independent review", per the lead's assignment of
     reviews to Claude review subagents. Who reviews changed; what must be established did not.

## 4. What I did not do

- No compiler, prover, build, test, WORLDLINE code, systemctl, sudo, project-vault or restic command. No WORLDLINE
  import. No TaskStop, kill or timeout wrapper.
- No SIA query or note.
- Did not read `D4/review/gpt61-v1`, `D4/review/gpt61-v2`, anything under `review-records/`, any other agent's
  transcript, or `~/.local/share/sia/.gbrain/`. Did not list or stat `/home/sicarii`, `~/iPad` or `~/iPadBackup`.
- Did not select or recommend OD-1, OD-2 or any operator item, and added no gate.
- Did not modify any existing tree, earlier design, review or deviation record.
- Did not re-run the Python census or re-evaluate v4's JACKAL records; both are carried by hash.
- Did not close F35: Theorem H-A is unreviewed and unproved, and A-COL stays OPEN.
- Did not resolve F32; it is restated only and owned outside D1.
- The Ada skills were loaded in this agent's session before any Ada reading (v4 drafting) and were not re-invoked
  after compaction.
