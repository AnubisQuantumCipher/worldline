Read-only planning completed. No network requests, writes, builds, proof runs, installations, or lock operations.

The smallest sound next action is **two metadata recovery requests**, followed by a separately registered source acquisition using the resulting exact manifest:

| Repository | Immutable endpoint suffix | Expected subtree |
|---|---|---|
| AdaCore/spark2014 | `/git/trees/0f1f51c51973750ae9d69c6b83c78afdb2598307?recursive=1` | `src` |
| gcc-mirror/gcc | `/git/trees/a3b9f0d4c999c8c127cebdc239ca8218284137aa?recursive=1` | `gcc/ada` |

Use the existing complete SPARK root, GNAT2Why tree, and GCC root mappings. Recovering `gcc/gcc` separately is unnecessary for this translator project graph unless subsequent actual source include analysis establishes an additional dependency.

Suggested metadata limits: exactly two GETs; 1 MiB response each; 4,096 entries each; 30 seconds per request; 90 seconds total; no redirects or retries. Require HTTP 200, `truncated=false`, expected subtree SHA, valid bounded relative paths, unique paths, recognized Git modes and object types. Persist raw response and receipt before parsing. Retain the original eight consumed queries and the separate GNATcoll recovery in request history.

The smallest defensible **project-level candidate source selection** is:

- SPARK: direct source files under `src/{why,spark,utils,flow,common,counterexamples}`; existing complete `src/why/xgen` inputs; direct Ada files at repository root; GNAT2Why project/configuration/template/C inputs from its already durable tree; license.
- GCC: direct `.ads`/`.adb` files under `gcc/ada`, plus root `*-tmpl` inputs and `libgnat/s-rident.ads`. Retain `gnat1drv.adb` because setup copies it into `obj-gnat2why`, despite its exclusion from the GNAT subproject. The other excluded GNAT bodies need not enter the candidate compile inputs.
- Existing GNATcoll Linux core/minimal selection and `src/why/why.ads` remain owned by the acquisition agent.

This avoids acquiring GCC documentation and entire runtime trees. It is a bounded project-source candidate; the executable closure remains **UNPROVEN** until source include/unit resolution and successful baseline build establish it. Preserve any actual newly discovered dependency as an explicit manifest amendment.

Fresh verification established:

- All **70 interface files, 873,083 bytes**, match their retained size/Git-blob mapping.
- All **five separately saved frontend bodies, 507,029 bytes**, match.
- All **24 actual local files** referenced by `reusable-source-evidence.json` match their recorded size/Git blob.
- Beyond those existing 70 plus five, **16 additional local files, 6,159,286 bytes**, are reusable: eight SPARK files totaling **2,042,969 bytes**, and eight GCC files totaling **4,116,317 bytes**.

The additional SPARK files are `spark_definition.adb`, `common_containers.ads`, `gnat2why-borrow_checker.adb`, `gnat2why-expr.adb`, `why-atree-to_json.ads`, `why-atree.adb`, `why-gen-decl.adb`, and `why-types.ads`. GCC reuse comprises the eight recorded `exp_attr`, `exp_ch3`, `exp_ch7`, `exp_spark`, `exp_util`, `sem_attr`, `sem_ch13`, and `sem_util` bodies. Reuse their actual paths from the durable JSON and freshly verify again when copying. Cross-repository reuse is valid only where bytes and blob identity match; for example, SPARK `LICENSE`, GCC `COPYING3`, and GNATcoll `COPYING3` share blob `94a9ed024d3859793618152ea559a168bbcbb5e2`.

One correction is necessary before materializing embedded SPARK build inputs. In `old-retirement-build-inputs.json`, three strings omit their final LF. Explicitly recording addition of **one LF** reconstructs the expected immutable blobs:

| JSON pointer | Reconstructed source | Exact bytes | Matching Git blob |
|---|---|---:|---|
| `/readbacks/3/content` | `gnat2why/Makefile` | 3,247 | `79ee48e0da968084e74edcf29ee206f612db430d` |
| `/readbacks/4/content` | `gnat2why/gnat2why.gpr` | 2,893 | `6dc07130eeb94c44d03769bdc86247200b5b43a0` |
| `/readbacks/5/content` | `.gitmodules` | 67 | `2cc64843b052ae5e6fbcbc8368eb042435273339` |

The unmodified embedded strings do **not** match. The five SPARK bodies in `old-retirement-translator-build-closure.json` that I checked match directly without reconstruction.

After metadata recovery, compute and durably save the exact selected, reusable, and missing mappings before source admission. A conservative outer acquisition ceiling is **2,830 files, 80 MiB source bytes, 4 MiB per file, one request per missing blob, and 1,800 seconds total**, with bounded failure-body capture. Replace these ceilings with the smaller exact manifest counts and byte sums before launch. Prior observed SPARK/GCC totals—2,829 paths and 73,589,485 bytes combined—are historical summary observations, not a recovered complete manifest or storage/build admission.

Remaining generation/configuration obligations:

- Xgen’s 20 listed Ada outputs, with the separately owned bounded generator plan.
- GNAT `snames.ads`/`.adb`, seven `GEN_IL_FILES`, and generated `obj/sdefault.adb`.
- Exact copied `gnat1drv.adb` and `s-rident.ads`.
- Recorded installed compiler/runtime locations, Debug configuration, GNATcoll target/constants, and bounded concurrency.
- Static examination of actual C includes and imported/linked units after acquisition.
- Source/compiler/driver/Why3 compatibility and installed correspondence remain **UNKNOWN**.

Acceptance evidence for executable baseline preparation is a complete durable input manifest, verified materialized bytes, recorded generated outputs/configuration/tools, successful unmodified translator build, and unchanged D47 static-leak failures reproduced through the isolated baseline. This does not close O1 or authorize a semantic patch.

<oai-mem-citation>
<citation_entries>
MEMORY.md:829-841|note=[retained O1 target and evidence boundaries cross checked against current instructions]
</citation_entries>
<rollout_ids>
01a13631-cd95-7cd2-870d-21561e26c8f2
</rollout_ids>
</oai-mem-citation>
