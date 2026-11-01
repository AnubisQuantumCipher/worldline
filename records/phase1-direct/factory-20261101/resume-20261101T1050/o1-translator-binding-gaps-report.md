**The source graph is concrete enough to prepare a bounded translator package, but its configuration bindings are not yet executable as written.** No additional source acquisition is justified.

Three genuine preparation gaps remain:

1. **Replace symbolic `$CFG` with an exact compiler configuration and runtime binding.** The recipe invokes `--config="$CFG"` without selecting its file or creation rule (`R/o1-baseline-recipe-report.md:23–35`). Pin the compiler, binder/linker, runtime directories and GPR configuration machinery; record the exact selected/generated CGPR bytes and import paths. `env.sh:4` appends ambient `GPR_PROJECT_PATH`, so sourcing it cannot establish isolation.

2. **Fix the precise `sdefault.adb` transformation.** Upstream `C/spark2014/gnat2why/Makefile:16–24,54–58` specifies:
   - ADAINCLUDE and ADALIB from selected native `gnatls` results;
   - GNAT1DIR by removing `rts-*` and `adainclude` from ADAINCLUDE;
   - PREFIX literally `@NOPREFIX@` for the nonautomated build.

   Do **not** substitute the actual `libexec/.../gnat1` directory for that source-prescribed GNAT1DIR derivation. Filesystem readback confirms the installed executable is under `libexec/gcc/aarch64-linux-gnu/16.1.0/gnat1`, while runtime inputs are under `lib/gcc/aarch64-linux-gnu/16.1.0/{adainclude,adalib}`. Preserve this distinction and verify selected compiler readback before executing the transformation.

3. **Specify reuse of the qualified GNATcoll dependency exactly.** Final recipe flags currently state DEBUG/static but omit explicit object root, project paths and externally-built selection (`R/o1-baseline-recipe-report.md:33–38,65`). The retained minimal/core GPRs default `EXTERNALLY_BUILT=false` and `GNATCOLL_OBJECT_ROOT=""` (`X/minimal/gnatcoll_minimal.gpr:49–55`; `X/core/gnatcoll_core.gpr:108–114`). Without explicit bindings, the translator command could rebuild dependencies or select another object/library tree. Choose the qualified dependency’s exact preserved layout, matching scenarios, hashes and read-only reuse—or explicitly budget a fresh build.

The remaining include/link resolution and both-phase candidate-execution provenance are **runtime evidence obligations**, not reasons to reopen acquisition. The C analysis already found no missing immutable inputs (`R/o1-compiler-c-link-report.md:1,32–38`); driver selection is source-supported but actual GPR2 execution remains unproved (`R/o1-driver-main-analysis-report.md:43–49`).

**One next task:** after generator qualification and author release, assign a bounded translator-package preparation task that fixes those three bindings, consumes the qualified21-output/GNATcoll receipts, and registers exact finite stages/resources/recovery plus future execution-provenance requirements. Preparation grants no build or D47 replay admission.

Paths: `R=records/phase1-direct/factory-20261101/resume-20261101T1050`; `C=records/phase1-direct/completion-20261026/old-retirement-compiler-source-cut-v1`; `X=records/phase1-direct/completion-20261026/old-retirement-xgen-source-cut-v1`.

Read-only only; no capture-author work inspected, files changed, tests or operational commands run.