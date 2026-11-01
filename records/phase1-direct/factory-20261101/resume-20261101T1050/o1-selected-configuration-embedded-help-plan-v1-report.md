**Yes. The exact pinned binary contains its compiled help grammar, removing the need for a native `--help` invocation merely to learn field order.** This is byte inspection, not execution or parser qualification.

Inspected binary:

```text
/home/sicarii/opt/gnat/gprbuild-aarch64-linux-26.0.0-1/bin/gprconfig
size:   38,836,096 bytes
SHA256: 58e81e9c21d18f20b80f7c2594a3f473621b64dff2498f191e4fbe2da9d0ce46
```

Offsets below are zero-based byte offsets; lengths exclude surrounding binary separators.

| Offset | Length | Exact printable bytes |
|---:|---:|---|
| 15170040 | 9 | `--config=` |
| 15170056 | 21 | `Preselect a compiler.` |
| 15170078 | 51 | `  CONFIG=language[,version[,runtime[,path[,name]]]]` |
| 15170130 | 69 | `  Name is either one of the names of the blocks in the knowledge base` |
| 15170200 | 78 | `  ('GCC', 'GCC-28',...) or the base name of an executable ('gcc', 'gnatmake').` |
| 15170279 | 70 | `  An empty string can be specified for any of the optional parameters,` |
| 15170350 | 44 | `  otherwise positional prefixes can be used:` |
| 15170395 | 64 | `  --config=language:ada,runtime:zfp equals to --config=ada,,zfp.` |
| 15169368 | 9 | `--target=` |
| 15170488 | 47 | `Select specified target or "all" for any target` |
| 15169584 | 7 | `--batch` |
| 15169592 | 45 | `Batch mode, no interactive compiler selection` |
| 15169688 | 3 | `-o:` |
| 15169696 | 37 | `Name and directory of the output file` |
| 15169768 | 5 | `--db:` |
| 15169776 | 41 | `Parse DIR as an additional knowledge base` |
| 15169818 | 63 | ` --db-                  Do not load the standard knowledge base` |
| 15169960 | 18 | `--fallback-targets` |
| 15169984 | 52 | `Look for native toolchains of different architecture` |

The 2,300-byte raw window starting at offset `15168800` has SHA256:

```text
89b269565b4803a852414115df793dc49357d50443a71582312a87264e471b25
```

Combined with installed `compilers.xml:20–33,190–214`, this supports a **prospective positional selection**:

```text
--target=aarch64-linux-gnu
--config=Ada,16.1,default,/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/bin,GNAT
--config=C,16.1.0,,/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/bin,GCC
```

`GNAT` and `GCC` are exact installed KB block names. The GNAT KB version regex captures major/minor (`16.1`); its GCC C regex captures the full compiler version (`16.1.0`). The Ada KB identifies `default` runtime discovery. Avoid `all` and omit fallback selection for this explicit native configuration.

**Still UNVERIFIED:** the precise matching/normalization semantics of `path` and `version`, treatment of multiple matching executables, runtime selection and actual generated CGPR. The embedded help names the fields but does not establish those parser details. The prospective selectors must therefore remain unexecuted candidates until the later bounded configuration stage checks actual selected drivers, runtime, target and complete retained CGPR bytes before compilation.

No writes, network, native tool execution, locks or services. The binary read stayed below 64 MiB and printed excerpts below 16 KiB. **F7 NOT PERFORMED.**