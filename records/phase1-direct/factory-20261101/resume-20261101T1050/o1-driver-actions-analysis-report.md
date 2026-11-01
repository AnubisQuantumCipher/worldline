**The pinned source constructs both translator actions with the bare name `gnat2why`; it does not establish a fixed absolute translator path.** Actual executable resolution and installed-driver correspondence remain unproved.

The three newly inspected files freshly match their recorded Git blobs and SHA-256 hashes:

| File under `old-retirement-driver-actions-source-cut-v1/src/gnatprove/` | SHA-256 |
|---|---|
| `configuration.ads` | `fd8274176fdafb46744eca8dc325a416b87bc205a5de7b2277ecac1f1dfd2826` |
| `gpr2-build-actions-process-compile-ada-analysis.adb` | `cd752952a4d1bd071c37237d520df528166ac6ce556bd220253a50981de133e4` |
| `gpr2-build-actions-process-compile-ada-global_gen.adb` | `a60639252469e208e8113c7891f3cc91b34bcc571b8ba5da4cf9d64998f7b5dc` |

Source-established behavior:

- **Analysis lines 62–67:** computes the inherited compiler command, removes its driver, then calls `Cmd_Line.Set_Driver ("gnat2why")`. Lines 69–95 add `-gnatc`, translation options, object-path arguments, and recorded Cargs.
- **Global_Gen lines 89–94:** performs the same driver replacement. Lines 95–119 add global-generation options and Cargs.
- **Configuration spec lines 205–235:** derives installation directories from `GNATCOLL.Utils.Executable_Location`, including `prefix/libexec/spark/bin`, configurations, and theories.
- **Configuration spec lines 236–241:** defines `GNSA_ROOT` → `GNSA_Dir_Bin`. None of the five inspected driver files establishes how that directory affects translator resolution. It is **not yet a proved override**.
- **Previously inspected `gnatprove_build.adb:372,427,530–532`:** initializes the two actions and delegates their execution to GPR2.

The retained GNATcoll implementation establishes prefix discovery:

```text
core/src/gnatcoll-utils.adb:404–441
  Executable_Location derives the executable directory and consumes “bin”.

core/src/gnatcoll-utils.adb:447–459
  Executable_Path calls c_executable_path.

core/src/executable_path.c:53–59
  Linux implementation reads /proc/self/exe.
```

Fresh identities:

```text
gnatcoll-utils.adb
Git 143e969046fc8f35112b3108726bc8fa05bc03db
SHA256 231b4dd022c6afcb1511ed983cba0303801d179e7b8c93dad12ed82263b3e5e7

executable_path.c
Git d24107730fd491c390bb9a9a090bc14e66b86bfb
SHA256 7f40aa20e4a47062b2d018394c9c95763cc68027defc41992b3031599a5abfdb
```

The minimal remaining pinned-driver source blocker is now **`src/gnatprove/gnatprove.adb`**, **11,476 bytes**, blob **`1ba4b42edf9062e6e5d96c1b1b48f107cea3b2af`**, at SPARK commit `b9410c6ed36d4e69a6c4d31e152fa8facaf0235c`. Its record is already in `old-retirement-compiler-metadata-v1/spark-src-tree-response.json`. It is needed to establish startup PATH policy and use of the installation directories. **Not acquired.** GPR2’s resolution behavior remains a separate dependency limitation; actual child provenance is still mandatory.

A future private read-only file bind could select the isolated candidate **if actual executable lookup resolves the covered installed pathname inside that namespace**. The kernel would execute the bound candidate inode while the driver bytes and host installation remain unchanged. This applies to an observed absolute execution path or a bare-name lookup resolving to that path. It does not establish a public override, source correspondence, compatibility, or launch admission.

Such an experiment must retain namespace/mount identity, bind source and destination, driver and candidate hashes, successful child executions for both phases, executable device/inode/hash, ancestry and argv, and host-installation readback before and after. It must reproduce the full unchanged D47 baseline, including static `.spark` leak failures; PATH ordering and scheduler JSON alone are insufficient.

Installed-driver/source correspondence remains **UNKNOWN**. No writes, acquisition, namespace creation, or execution occurred. Read-only work released.
