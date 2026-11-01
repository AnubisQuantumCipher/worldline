Use byte-identical owned staging and the original GPRs. This avoids making an untested GPR-extension adapter a prerequisite.

**Source observations:** all 284 prerequisite-manifest payloads and 74 interface-manifest payloads match their recorded bytes/hashes. Prerequisite manifest matches `e9782379…268d`. Both GNATcoll `VERSION` files contain `25.0`; core’s generated constants default to `0.0`, so set the version explicitly.

- GNATcoll minimal/core already support absolute `GNATCOLL_OBJECT_ROOT`, redirecting both objects and libraries without source edits.
- `helpers.gpr` fixes `Object_Dir="obj"` and `Exec_Dir="."`.
- A small project extending `helpers.gpr` could override those two attributes while leaving imported GNATcoll controlled by `GNATCOLL_OBJECT_ROOT`. Its installed-tool behavior remains UNVERIFIED because no GPR invocation was allowed.
- Copying the 62 xgen files plus `why-sinfo.ads` and `why.ads` preserves the original relative layout and makes unchanged `helpers.gpr` sufficient. These 64 inputs total 389,163 bytes. Copy the prerequisite GNATcoll selection into its own owned tree as well; never build in acquisition packets.

Let `W` be a fresh registered work root, `G=W/source/gnatcoll`, and `X=W/source/spark/src/why/xgen`. All compiler/configuration, objects, libraries, executable, temporary/cache and log writes stay under `W`.

Use these explicit scenarios consistently:

```text
GNATCOLL_BUILD_MODE=DEBUG
LIBRARY_TYPE=static
GNATCOLL_VERSION=25.0
GNATCOLL_OS=unix
GNATCOLL_MMAP=yes
GNATCOLL_MADVISE=yes
GNATCOLL_XXHASH_ARCH=generic
GNATCOLL_OBJECT_ROOT=W/gnatcoll/
```

Select `GNATCOLL_BLAKE3_ARCH=aarch64-linux` only after confirming the normalized target receipt. That is the retained upstream wrapper’s aarch64 selection; `generic` is the raw GPR default, so do not silently interchange them.

The command graph is:

```text
gprbuild -p -j2 -P G/minimal/gnatcoll_minimal.gpr <scenarios>
  -XEXTERNALLY_BUILT=false
  -cargs:Ada -gnatwa -gnatwe -gnatVa
  -cargs:C -Wall -Wextra -Werror

gprbuild -p -j2 -P G/core/gnatcoll_core.gpr <same scenarios/flags>
  -XEXTERNALLY_BUILT=false

gprbuild -p -j2 -P X/helpers.gpr xtree <same scenarios>
  -XEXTERNALLY_BUILT=true
  -cargs:Ada -gnata -gnatVa -gnatwa -gnatwe
```

DEBUG retains its existing checks, `Initialize_Scalars`, `-O0`, stack checking and binder `-E`. Helpers retains `-gnatg`. Preserve warning/build failures; do not suppress them to qualify the baseline. Sanitize inherited flags/search paths and set `GPR_PROJECT_PATH` only to the selected core/minimal directories. Do not invoke either Makefile, Python build wrapper, installation or shared-library lane.

Run the same hashed executable twice in fresh `W/generation-a` and `W/generation-b`, each containing the exact 21 templates. `Templates.Process` reads templates and creates outputs relative to cwd. Require both exits, complete diagnostics, no substitution warnings, no remaining markers, exactly the expected outputs and byte equality across generations:

```text
why-classes.ads             why-atree.ads
why-ids.ads                 why-unchecked_ids.ads
why-opaque_ids.ads          why-conversions.ads
why-atree-builders.ads      why-atree-builders.adb
why-atree-accessors.ads     why-atree-mutators.ads
why-atree-mutators.adb      why-atree-traversal.ads
why-atree-traversal.adb     why-atree-traversal_stub.ads
why-atree-traversal_stub.adb
why-atree-treepr.ads        why-atree-treepr.adb
why-kind_validity.ads       why-atree-validity.ads
gnat_ast.ml                 why-atree-to_json.adb
```

A concrete **UNMEASURED candidate envelope for review**, not demonstrated fit:

- Live staging/build/tmp/log/generation aggregate: 4GiB; maximum 8,192 entries.
- Individual writable file and each full stdout/stderr stream: 64MiB using inherited OS `RLIMIT_FSIZE`; exceeding it fails the attempt.
- Reserve archive and complete restoration space separately: approximately 4GiB each plus framing/filesystem allowances; retain another 1GiB shutdown/growth margin.
- Minimal/core deadlines 300/600 seconds, helpers 300, generations 30 each, verification 120; heavy-worker deadline 1,500 seconds.
- A separate finite outer supervisor must bound lock waiting, first memory refusal and cleanup, retain capped receipts, cancel only its launcher group and exact scope, and report incomplete cleanup as UNVERIFIED.

Do not edit `phase1_heavy.py` casually. Its five-minute memory retry and indefinite supervisor cleanup are intended service behavior; the new finite package supervisor must contain them. Its shared lock, post-lock14GiB and8GiB/swap0 remain mandatory.

Disk sampling and per-file limits **do not establish an aggregate disk quota or preserve reserve against unrelated writers**. The proposed aggregate ceiling is an admission/stop threshold requiring a reviewed monitor and current storage-owner handoff. No aggregate-hard-bound claim is available. Capture full logs up to their stated ceiling; overflow is explicit evidence loss/failure, never silent truncation or success.

Remaining decisions are the exact profile ceilings/deadlines, target/tool/configuration pins, narrowly writable isolation and finite supervisor/capture implementation. These require preparation review before admission. Successful xgen would establish generator execution only: translator closure, installed correspondence, unchanged D47 reproduction and O1 remain unproved. No writes or prohibited execution occurred.
