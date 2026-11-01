**No additional legacy renamed predefined-unit references were found in the exact registered 342 inputs.** All 342 source hashes and byte counts match `o1-xgen-build-package-v2/input-pins.json`; the roster contains 278 GNATCOLL and 64 xgen/Why inputs, including 270 `.ads`/`.adb` files. The search also covered remaining registered text, including templates.

The complete relevant occurrence list is:

| Registered path | Lines | Canonical target | Status |
|---|---:|---|---|
| `source/gnatcoll/minimal/src/gnatcoll-boyer_moore.adb` | 77 | `Ada.Unchecked_Deallocation` | Import produced the **OBSERVED** warning |
| Same | 248–249 | `Ada.Unchecked_Deallocation` | First generic instantiation; adaptation required for visibility |
| Same | 250 | `Ada.Unchecked_Deallocation` | Second generic instantiation; adaptation required for visibility |

Canonicalizing the import requires qualifying **both** instantiations. Keeping the unqualified names after changing only the import is insufficient. No further source substitutions are supported by this inventory.

The installed runtime establishes the legacy alias set used for this bounded check:

| Legacy unit | Canonical unit | Runtime evidence |
|---|---|---|
| `Unchecked_Deallocation` | `Ada.Unchecked_Deallocation` | `unchdeal.ads:16–23` |
| `Unchecked_Conversion` | `Ada.Unchecked_Conversion` | `unchconv.ads:16–23` |
| `Text_IO` | `Ada.Text_IO` | `text_io.ads:27` |
| `Sequential_IO` | `Ada.Sequential_IO` | `sequenio.ads:24` |
| `Direct_IO` | `Ada.Direct_IO` | `directio.ads:24` |
| `IO_Exceptions` | `Ada.IO_Exceptions` | `ioexcept.ads:24` |
| `Calendar` | `Ada.Calendar` | `calendar.ads:18` |
| `Machine_Code` | `System.Machine_Code` | `machcode.ads:20` |

Runtime root: `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude`.

Renamings such as `GNAT.Case_Util → System.Case_Util` are not evidence of the same RM J.1 warning class and do not justify substitutions. This inventory establishes no additional predicted warning locations; it does **not** establish that later compiler stages will be warning-free.

**No Boyer–Moore unit tests exist in the retained source cut or registered roster.** The only matching retained paths are its `.ads` and `.adb`; no test paths were found. A bounded local lifecycle fixture would therefore need separate authorship and registration. Its minimum useful scope is search correctness with both case modes, unsuccessful search, `Compile → Search → Free`, repeated `Free`, and reuse after `Free`.

The smallest sound next step remains the distinct compatibility dossier containing the original source identity, exact three-site canonicalization, semantic obligations, and separately bounded fixture/build qualification. This does not reset D158/D159 budgets or authorize execution. No edits, tests, builds, acquisition or operational calls performed. **F7 NOT PERFORMED.**