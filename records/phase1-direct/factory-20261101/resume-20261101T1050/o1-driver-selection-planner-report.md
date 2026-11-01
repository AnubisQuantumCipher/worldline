**Supported candidate selection remains UNESTABLISHED.** Available installed documentation does not specify a translator override, and the retained source does not include the driver bodies that select it. No launch, network access, or writes occurred.

Verified installed evidence, under `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/`:

| File | SHA-256 | Finding |
|---|---|---|
| `bin/gnatprove` | `11db5cc1032d51474c2b84cc8567095c4ec4f5ae4428ff525b7bac92e7d86bc9` | Current driver identity; correspondence to pinned source UNKNOWN. |
| `share/spark/help.txt` | `b319b6c0e36362385cbb3c294a6ec875d6ad293f35be405edc0cf44ec0209eac` | Lines 13–46 and 66–123 document options, including verbosity, but no translator-path or environment selector. This does not exclude undocumented mechanisms. |
| `share/spark/config/gnat2why/config.xml` | `a78737344b583024dab5e120f5a8011a64a2c8bb3b4370d807a953481183ec64` | Configures `.spark`, `ALI_Closure`, and `-gnateO=`; does not select an executable. |
| `share/spark/config/frames/config.xml` | `d712b6c40252b16652df96533f907c3217d1d3aad47c564d1f460e389c72c57d` | Configures `.ali` and `ALI_File`; no executable selector. |
| `share/spark/config/gnatprove.conf` | `4ff4651508373959ad0d6834e482b539670e9f6f0ca6b90bb3683fd27d8be6cf` | Prover configuration, not translator selection. |

Retained pinned `src/common/call.adb`, blob `a1dfb403f0bac90fabda292fd7a152e0cc968b93`, calls `Locate_Exec_On_Path(Command)` and spawns the resulting path. Its verbose output prints the original `Command`. Consequently, verbose text alone does not prove the resolved executable, and the missing driver source must establish what command is passed and whether other execution paths exist.

The smallest justified **initial acquisition** is two bodies at SPARK commit `b9410c6ed36d4e69a6c4d31e152fa8facaf0235c`:

| Path | Bytes | Git blob | Question resolved |
|---|---:|---|---|
| `src/gnatprove/configuration.adb` | 184,085 | `29eb034f34b427bf9a7fba737ef74adceb98e884` | Installation discovery, environment/option handling, configured executable paths. |
| `src/gnatprove/gnatprove_build.adb` | 36,087 | `c76c3aadadf576fa85719707a863f2f71de664ca` | Construction of analysis/global-generation jobs and tool selection. |

Total: **220,172 bytes**, two immutable raw-source requests. Exact mappings are already durable in `old-retirement-compiler-metadata-v1/spark-src-tree-response.json`, SHA-256 `417c3600d9aed248702e4e9b59cac9b32cdfeae8f1ce992df6874893de90b940`.

Only if their references require it, follow with:

```text
src/gnatprove/gnatprove.adb
  11476 B  1ba4b42edf9062e6e5d96c1b1b48f107cea3b2af

src/gnatprove/configuration.ads
  16014 B  855eec6808363909a6ea4709b9ab25368fe01b3b

src/gnatprove/gpr2-build-actions-process-compile-ada-analysis.adb
   9185 B  ffcca769c01f8791ed50d2b14557f06becd1e73a

src/gnatprove/gpr2-build-actions-process-compile-ada-global_gen.adb
  14289 B  d7543861dc4ae85dd58b2d9916003397dda9e246
```

These six files total **271,136 bytes**. The four follow-ups are conditional candidates, not yet demonstrated necessary. No driver rebuild or additional dependency acquisition follows from this inspection.

Once source-established selection semantics and launch admission exist, a prospective execution trace is:

```sh
strace -f -ttt -s 16384 -e trace=execve,execveat \
  -o "$RECEIPTS/exec.trace" \
  "$ISOLATED_UNCHANGED_DRIVER" -P probe.gpr -U --mode=all \
  --level=3 --report=all --checks-as-errors=on \
  --proof-warnings=on --memlimit=1024 --timeout=60 -j1
```

This is **not ready to execute**: `$ISOLATED_UNCHANGED_DRIVER` and its translator-selection mechanism remain unresolved. Do not invent an override flag or assume relocating the driver changes its installation root.

Required provenance includes the successful child executions, PID/parent chain, argv and working directory, executable path plus observed device/inode/hash, sealed candidate identity, driver identity, selected configuration/theory/prover identities, bounded trace completion, and fresh outputs. Verify every translator analysis phase uses the candidate; data-representation compiler executions must be distinguished explicitly.

Selection qualifies only when that evidence accompanies the **full unchanged D47 baseline**, including its static `.spark` leak failures. PATH precedence, version strings, printed commands, or Why3-session success alone do not qualify it.

Read-only investigation released; no source or launch admission changed.
