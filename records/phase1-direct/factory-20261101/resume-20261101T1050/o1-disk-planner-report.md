**Prepare a fresh isolated disk build of GNATcoll minimal/core, followed by xgen.** The blocked IPC diagnostic is not a prerequisite. No build, install, acquisition, wrapper execution or source write occurred in this planning task.

Readiness is **source-observed, not executable-qualified**. The durable mapping selects279 files, including `core/VERSION` and `minimal/VERSION`; acquisition is still owned by the other writer. Wait for its terminal manifest and root’s complete bytes/mode/Git-blob/SHA readback. The62 xgen inputs, `why-sinfo.ads` and incoming `why.ads` must then be joined into an exact isolated input manifest. Source-to-installed correspondence remains **UNKNOWN**.

The smallest preparation package should contain:

- One fresh root-owned registration, reviewed wrapper and exclusive output root, for example `completion-20261026/o1-xgen-build-v1/`. Assign its source writer explicitly.
- Immutable source packets remain read-only. Copy exact sources into owned staging preserving layout; never build in either acquisition packet.
- Separate owned subdirectories for GNATcoll objects/libraries, copied xgen source/build,21 generated outputs, second-generation outputs, temporary/cache data, logs, archive and recovery comparison.
- Explicit input and tool closure, sanitized environment, command vectors, finite deadlines, retained failure path and terminal cleanup/readback. No installed prefix, `gprinstall`, product edit or semantic `'Old` change.

**Direct GPR builds avoid unnecessary installation.** The retained pinned GNATcoll projects explicitly support `GNATCOLL_OBJECT_ROOT` for both object/library redirection. These are draft command shapes for the reviewed worker, not launch instructions now:

```text
gprbuild -j2 -p -P COPY/minimal/gnatcoll_minimal.gpr
  -XGNATCOLL_BUILD_MODE=DEBUG -XLIBRARY_TYPE=static
  -XGNATCOLL_OS=unix -XGNATCOLL_VERSION=<exact minimal/VERSION>
  -XGNATCOLL_OBJECT_ROOT=OUTPUT/gnatcoll/
  -cargs:Ada -gnatwe

gprbuild -j2 -p -P COPY/core/gnatcoll_core.gpr
  -XGNATCOLL_BUILD_MODE=DEBUG -XLIBRARY_TYPE=static
  -XGNATCOLL_OS=unix -XGNATCOLL_VERSION=<exact core/VERSION>
  -XGNATCOLL_MMAP=yes -XGNATCOLL_MADVISE=yes
  -XGNATCOLL_BLAKE3_ARCH=<observed normalized target selection>
  -XGNATCOLL_XXHASH_ARCH=generic
  -XGNATCOLL_OBJECT_ROOT=OUTPUT/gnatcoll/
  -cargs:Ada -gnatwe
```

Set `GPR_PROJECT_PATH` to **only the copied core/minimal project directories**, with exact compiler/runtime configuration separately pinned. Remove inherited `ADAFLAGS`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `GPR_TOOL` and unrelated GPR search paths unless explicitly registered. DEBUG already supplies `-gnata`, `-gnatVa`, checks and warning flags. Record the complete commands and generated configuration; preserve any warning/build failure rather than weakening flags.

After successful library readback, build copied helpers:

```text
gprbuild -j2 -p -P COPY/src/why/xgen/helpers.gpr xtree
  <same exact GNATcoll scenario configuration>
  -XEXTERNALLY_BUILT=true
  -cargs:Ada -gnata -gnatVa -gnatwe
```

`EXTERNALLY_BUILT` applies to imported GNATcoll projects and prevents accidental library recompilation after their readback. Confirm both VERSION/scenario values resolve consistently before freezing this command. Run the resulting `xtree` only with cwd at the owned copied xgen directory; preserve all21 outputs, then repeat in a second fresh owned directory. **Do not run xgen’s Makefile**: it hardcodes `-j0` and copies generated files into its parent (`interface-source-cut-v1/src/why/xgen/Makefile:33–36`). Helpers’ existing assertions/debug switches are at `helpers.gpr:13–15`.

For isolation, reuse the **pattern**, not the unchanged decoder wrapper: read-only `/`, fresh private `/dev`/`proc`, no network, writable binds restricted to owned staging/output/TMP/cache; keep acquisition packets, toolchain and product read-only. Existing decoder runner binds the entire carrier writable (`decoder-cursor-v2/run.py:63–70`), so that literal command is too broad for this package.

The existing heavy wrapper supplies shared lock, post-lock14GiB admission and8GiB/swap0 scope; it **does not supply aggregate disk admission** (`scripts/phase1_heavy.py:64–92,139–150`). A task-specific disk/output guard is still required. Register a finite conservative allowance covering, simultaneously:

```text
copied inputs + both libraries/objects + xgen executable/objects
+ both generations + temp/cache + logs + archive + full restore + recovery receipts
```

Call it an **admission ceiling, not measured peak growth**. No qualified numerical object/output/archive budget currently exists (`o1-interface-analysis-report.md:34–38`; `old-retirement-translator-build-closure.json:119–124`). Existing reserve sampling is not a filesystem quota; the new wrapper must disclose that boundary and enforce reviewed stop/log/file limits. Preserve10,000,000,000-byte reserve and startup/stop margins; do not invent successful-fit evidence.

The earlier non-IPC RAM mechanism is **not a ready substitute**. Its fixed32MiB/1024-entry output and separate restoration filesystems,8MiB archive and180/220/240/270s chain were designed for probe/Chunk paths. Actual Chunk execution failed semaphore creation and retained `LOST_EPHEMERAL_OUTPUTS` on `tmp/why3server_2.sock` (`chunk-diagnostic-v3-root-readback.json:47–64`). Its dispatcher and mounts are fixed (`ram_qualification_v3.py:293–327`); GNATcoll/xgen would need a distinct reviewed preparation and fresh qualification. Do not enlarge its limits or rename/relaunch the blocked consumer.

**Next executable engineering step:** after acquisition release/root readback, author the finite disk-build registration and narrowly writable wrapper, then review that exact package. Fresh storage-owner window, lock/memory admission and source/tool readback precede launch. Reusing an existing15m disk-wrapper envelope or the180s RAM envelope requires an explicit recorded selection; neither proves this new job finishes within it.

Generator acceptance requires actual clean DEBUG/static library and xgen build diagnostics, assertions/flags readback,21 exact outputs, no unresolved template markers, repeat-generation byte equality, complete retained recovery and terminal/source readback. It establishes generator execution only; translator closure, unchanged D47 replay and O1 semantics remain open.

<oai-mem-citation>
<citation_entries>
MEMORY.md:613-622|note=[retained carrier and resource boundaries]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>
