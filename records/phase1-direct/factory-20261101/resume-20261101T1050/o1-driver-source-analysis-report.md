**Translator selection is still UNESTABLISHED.** The two acquired bodies establish delegation to missing action implementations; they do not establish an override option, environment variable, or relocation rule.

Both inspected files freshly match their pinned Git blobs and supplied SHA-256 identities:

```text
configuration.adb
184085 B
Git: 29eb034f34b427bf9a7fba737ef74adceb98e884
SHA256: 70be5c4e4d86aab91bf0560bb7946608ccbf7c41f6a4191546af838868a91c52

gnatprove_build.adb
36087 B
Git: c76c3aadadf576fa85719707a863f2f71de664ca
SHA256: 435d6c1103f115db76c229b776dca816b41be73d65db17262926d011758ad6b5
```

They reside under:

```text
records/phase1-direct/completion-20261026/
old-retirement-driver-selection-source-cut-v1/src/gnatprove/
```

The source-established execution graph is:

- `gnatprove_build.adb:12–14` imports `Analysis`, `Data_Rep`, and `Global_Gen` action packages.
- Lines **372–373** initialize and enqueue `Global_Gen`.
- Lines **427–429** initialize and enqueue `Analysis`.
- Lines **455–459** configure `gnatprove_build.json`.
- Lines **530–532** execute those actions through the GPR2 scheduler.
- `configuration.adb:3335–3339` loads the project with its runtime; executable selection is not established there.
- `Configuration` uses `SPARK_Install` installation paths, including an explicit `gnatwhy3` path at **4928–4930**, but its visible definition is missing.

Importantly, `gnatprove_build.adb:698–725` resolves and spawns a command through PATH, but its demonstrated caller is **`why3server`**, not the translator. It cannot justify candidate `gnat2why` selection.

The minimal now-justified follow-up request is **three files, 39,488 bytes**, at SPARK commit `b9410c6ed36d4e69a6c4d31e152fa8facaf0235c`:

| Repository path | Bytes | Git blob | Required evidence |
|---|---:|---|---|
| `src/gnatprove/configuration.ads` | 16,014 | `855eec6808363909a6ea4709b9ab25368fe01b3b` | Visible installation/path declarations and switch definitions used by the inspected body. |
| `src/gnatprove/gpr2-build-actions-process-compile-ada-analysis.adb` | 9,185 | `ffcca769c01f8791ed50d2b14557f06becd1e73a` | Analysis action’s actual executable/command construction. |
| `src/gnatprove/gpr2-build-actions-process-compile-ada-global_gen.adb` | 14,289 | `d7543861dc4ae85dd58b2d9916003397dda9e246` | Global-generation action’s actual executable/command construction. |

Their exact records are in `old-retirement-compiler-metadata-v1/spark-src-tree-response.json`, matching `tree[].path` without the leading `src/`. No acquisition occurred. `gnatprove.adb` remains conditional; no additional driver closure is requested.

Future acceptance must retain successful child-execution evidence for **both translator phases**, executable identity and ancestry, argv/cwd, selected inputs/configuration, fresh scheduler JSON, complete outputs, and unchanged D47 static failures. Scheduler JSON, printed commands, PATH ordering, or cached results alone do not establish the executed candidate.

Installed-binary/source correspondence remains **UNKNOWN**. No supported selection command can yet be supplied without speculation. Read-only work released; no launch admission or source changed.
