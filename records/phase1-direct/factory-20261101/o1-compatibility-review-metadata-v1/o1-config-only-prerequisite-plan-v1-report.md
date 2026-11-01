Prepare **one separate configuration-only prerequisite**, then terminate and seal its evidence. Review happens after the job is terminal. A later dependency/compiler package consumes the approved CGPR as readonly input; the original generator’s 1500-second worker and 1590-second monitor limits remain unchanged.

Let:

```text
G=/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1
P=/home/sicarii/opt/gnat/gprbuild-aarch64-linux-26.0.0-1
F=<fresh registered configuration-stage root>
```

The candidate argv, requiring later admission and verification, is:

```text
P/bin/gprconfig
--batch
--db-
--db=P/share/gprconfig
--target=aarch64-linux-gnu
--config=Ada,16.1,default,G/bin,gnatls
--config=C,16.1.0,,G/bin,gcc
-o F/native.cgpr
```

Expand every placeholder to an exact absolute argument before review. Do not add `--fallback-targets`, `--autoconf`, project arguments or compilation commands.

The binary’s observed embedded help establishes:

- Offset `15170078`: `CONFIG=language[,version[,runtime[,path[,name]]]]`.
- Offsets `15170130–15170278`: `name` accepts a KB block name or executable basename.
- Offset `15169818`: `--db-` disables the standard KB.
- Offset `15169776`: `--db` adds the selected directory.
- Offset `15170488`: target selection supports a specified target or `all`.

Binary SHA256: `58e81e9c21d18f20b80f7c2594a3f473621b64dff2498f191e4fbe2da9d0ce46`.

**Executable basenames `gnatls` and `gcc` are the narrower candidate selectors.** They seek the unprefixed executables in the selected directory, reducing ambiguity between unprefixed and target-prefixed copies. `GNAT`/`GCC` are valid installed KB names, but describe compiler families and may admit several matching executables. Neither selector strategy has been executed here. Exact path matching, version matching, duplicate resolution and target normalization remain parser/runtime obligations; a rejected selection must stop rather than trigger automatic alternative selectors.

Installed KB support:

- `compilers.xml:20–33`: GCC C discovery, full version and target.
- `compilers.xml:190–214`: GNAT discovery through `gnatls`; major/minor version, `default` runtime and target.
- `c.xml:17`: C driver derives from selected path/executable.
- `gnat.xml:12–33`: Ada driver, `gprbind` and runtime.
- `linker.xml:1688–1705`: Ada compiler drives executable linking.
- `0_default.xml:7–53`: default naming and binder substitutions.

The `--db-` plus explicit KB-directory combination must be checked against actual output: successful generation does not alone prove that only the intended configuration data influenced it. Pin the complete existing KB inventory, including entity files, rather than selecting individual XML files.

Use an allowlisted environment from the initial process entry:

```text
PATH=G/bin:P/bin:/usr/bin
HOME=F/home
TMPDIR=F/tmp
XDG_CACHE_HOME=F/cache
LC_ALL=C
TZ=UTC
```

Exclude inherited GPR configuration/project/runtime overrides, compiler flag variables, startup hooks and loader overrides. Record descriptors 0/1/2 and CORE=0. Existing heavy-helper and bubblewrap mechanisms can supply bounded containment and readonly host inputs, with only `F` writable and network isolated; this requires a separately reviewed fixed invocation, not changes to old sealed packages.

Expected discovery executions include selected `gnatls -v --version`, `gcc -v`, and `gcc -dumpmachine`, directly supported by `compilers.xml`. Their complete transitive process/load closure remains unestablished. Keep the existing pinned compiler/GPR/KB/runtime set available; additionally verify the selected executable identities and actual generated tool paths.

A small independent profile can propose:

- Configuration command: **30 seconds**, no retry.
- Existing **8 GiB memory / zero swap** envelope.
- Each configuration/log file: **64 KiB maximum**, reject reaching its ceiling.
- Owned payload: **1 MiB / 128 entries** maximum, excluding separately bounded heavy-helper metadata.
- Explicit finite monitoring, admission wait and owned cleanup bounds inherited from qualified mechanisms.
- Preserve partial files, nonzero exits and unknown termination; no automatic successor.

Registered outputs should be limited to `native.cgpr`, complete stdout/stderr, exact argv/environment and identities, result/terminal receipts, and an inventory of `home/tmp/cache`. Unexpected files or diagnostics require classification; do not erase them to produce a clean seal.

Before approving the CGPR for later use, verify:

1. Selected target and any normalized target are explicit and justified.
2. Ada/C drivers resolve to the selected `G/bin` executables.
3. Runtime resolves to `G/lib/gcc/aarch64-linux-gnu/16.1.0/`, with matching `adainclude/adalib`.
4. Binder/library drivers resolve to `P/libexec/gprbuild/{gprbind,gprlib}`.
5. Link driver is the selected Ada compiler; all bare archive/object tools resolve through the recorded environment.
6. Complete CGPR bytes, KB/tool identities and side-effect inventory are sealed.

Later builds use only `P/bin/gprbuild --config=<sealed absolute CGPR> ...`, with no implicit configuration discovery. The prerequisite’s completed review interval is not charged to or hidden inside a running generator job.

This is **UNRUN planning**, not admission or parser qualification. No writes, tool execution, network, locks, services or offloads occurred. **F7 NOT PERFORMED.**