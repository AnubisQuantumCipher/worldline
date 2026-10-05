# W-1 v5 drafting author: process record (preserved; disclosed)

**Who.** The W-1 drafting agent (`a6d9c9e22b6b98dc0`), resumed by the lead at ~05:59Z on 2026-10-05 to draft W-1 v5. It
handed back shortly after 07:30:24Z, the last write of the v5 file.

**Its source.** The author's handback report, and §0.5 and Appendix E of `proposal/ISOLATION-STORAGE-PROPOSAL-v5.md`
(sha256 `303205b1531eb5752fabc866f949c609725e3e42936404495ba9adfd171cd7ee`). Both are model output, recorded as stated.

## Disclosed deviations

1. **~06:24Z: one read-only `ls` of man-page paths included `2>/dev/null`.** The lead's resume message forbade this
   explicitly ("not even 2>/dev/null"). The author reports that nothing was written to any file. It is a rule deviation
   and is recorded as one. It is not a guard-refusal workaround, and it touched no protected path.
2. **Later: one read-only `ls` of getent manual paths used `2>&1` into a pipe.** The lead's message permitted that.
   The author disclosed it anyway.

## Reported as not done

- No other deviations.
- No privileged or mutating action, and no `tune2fs`.
- No compiler, prover, WORLDLINE code, project-vault or restic.
- No access to `.gbrain`, `/home/sicarii` itself, `~/iPad` or `~/iPadBackup`.
- No interruption: no TaskStop, kill, `timeout` wrapper or background task.
- One `sia.ask` at the start; no SIA note.

## Read-only host observations the author made (dated)

- `kernel.io_uring_disabled` = 0 at 06:24:47Z.
- Installed manual line ranges for systemd.exec(5), systemd.unit(5), systemd(1) and bash(1).
- The user unit directories at 06:28:42Z: 93 process-starting unit-file names counted by `grep -c`, 10 of them
  templates, and only `systemd-tmpfiles-clean.timer` as a timer. This corrects v4's "no timer at all".
- `/usr/bin/sh` and `/bin/sh` point to bash (06:45:33Z).
- `df -h /` showed 9.2G free at 07:00:32Z.

## What the lead verified

All engineering only, not review.
- **Hashes.** Both files equal the report.
- **Composition.** A lead script implemented v5 §0.1, the composition rule (v4 units in v4 order: CARRIED,
  AMENDED by the 30 amendments of §0.4, each applied exactly once, REPLACED, and the three NEW units at their places).
  It produced 466105 bytes with sha256 `6cbc9c07994c2798910b84a02c5e445f67f24b9f51ed0efc95142df9b6113490`, equal to
  the author's rebuilt text. That composed text is kept as the derived convenience copy
  `package-frozen/ISOLATION-STORAGE-PROPOSAL-v5-COMPOSED.md`, mode 0444.
- **Change map.** All 106 rows of §18.5 match v4's units by bytes and sha256. One cosmetic error: the Appendix D row
  gives v4 lines 3267-3325, but v4 has 3324 lines. The row's bytes (7942) and sha256 (`43c155f9…`) are correct.
- **JACKAL.** All four recorded calls reproduce `exact`: `69+21+16-106`=0, `106+3`=109, `1+1+1+1+1+1`=6 and
  `69+33+4-106`=0.

## What this does not change

None of these items grants anything or closes any obligation. The six W-1 corrections of `gpt61-v4`, V5-B01, V5-B02,
Gate 0 and every original obligation stay OPEN until the independent actual gpt-6.1-sol review rules.
