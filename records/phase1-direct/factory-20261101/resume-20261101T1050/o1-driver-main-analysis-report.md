**The pinned driver recognizes `GNSA_ROOT` and prepends its `bin` directory to PATH.** This supplies a concrete source-established candidate-selection route, conditional on GPR2 resolution and actual installed-driver behavior.

Freshly verified main source:

```text
old-retirement-driver-main-source-cut-v1/src/gnatprove/gnatprove.adb
11476 bytes
Git blob: 1ba4b42edf9062e6e5d96c1b1b48f107cea3b2af
SHA256: 06e5456cfd88517ad1bf06e97936cdd3271fc52d07af5bb1cfcea3c5bb1a6cf9
```

The exact source chain is:

1. `configuration.ads:205–212` derives the installation prefix through `GNATCOLL.Utils.Executable_Location` and constructs `prefix/libexec/spark/bin`.
2. `configuration.ads:236–241` defines `GNSA_Dir` as `GNSA_ROOT` when present, otherwise `prefix/libexec/spark`; `GNSA_Dir_Bin` appends `bin`.
3. **`gnatprove.adb:202–208` sets PATH to:**

   ```text
   GNSA_Dir_Bin : Libexec_Spark_Bin : incoming_PATH
   ```

4. `gnatprove.adb:231–232` performs that environment setup **before** command-line/project loading.
5. Analysis `:66–67` and Global_Gen `:93–94` replace the compiler driver with bare **`gnat2why`**.
6. `gnatprove_build.adb:530–532` delegates execution to the GPR2 scheduler.

The prefix mechanism is supported by retained GNATcoll `gnatcoll-utils.adb:404–441,447–459` and Linux `executable_path.c:53–59`, which obtains the executable path through `/proc/self/exe`.

A prospective route, **not executed or admitted**, is to expose only the sealed candidate executable at:

```text
$CANDIDATE_PREFIX/bin/gnat2why
```

Then invoke the unchanged installed driver:

```sh
env GNSA_ROOT="$CANDIDATE_PREFIX" \
  "$INSTALLED_PREFIX/bin/gnatprove" -P probe.gpr -U --mode=all \
  --level=3 --report=all --checks-as-errors=on \
  --proof-warnings=on --memlimit=1024 --timeout=60 -j1
```

Keeping that candidate directory limited to `gnat2why` avoids intentionally replacing other compiler tools. Their actual selection must still be recorded. Startup also clears several compiler/Why3 environment variables (`gnatprove.adb:187–196`) and preserves incoming project-path precedence (`:215–217`).

This is a **source-recognized environment mechanism**, not an override documented by the inspected installed help. Installed-binary/source correspondence remains **UNKNOWN**, and GPR2’s bare-driver resolution is not proved by PATH construction.

A private read-only file bind remains a conditional alternative if actual resolution selects a known installed pathname. It would substitute the candidate inode only inside that namespace while retaining driver bytes. It is neither required by this source mechanism nor currently admitted.

The smallest remaining blocker is **execution provenance after the candidate build and separate launch admission**, rather than more driver-source acquisition. Retain successful executions of the candidate for both Global_Gen and Analysis, executable hashes/device/inode, parent chain, argv/cwd/environment, selected auxiliary tools/configuration, fresh scheduler records and outputs, and the complete unchanged D47 static failure signature. Reject fallback to the installed translator, mixed phases, cached zero-work results, or session-only green.

No further acquisition, writes, execution, or namespace operation occurred. Read-only work released.