The smallest next preparation is a **separate, freshly bound successor package**, conditional on D160 approval. Preserve failed `o1-xgen-build-v1`, both sealed D158/D159 packages, their decisions and exhausted revision budgets. I did not inspect current D160 verdicts.

Use proposed new paths, registered before writing:

```text
records/phase1-direct/factory-20261101/o1-dependency-compatibility-package-v1/
records/phase1-direct/factory-20261101/o1-dependency-compatibility-job-v1/
records/phase1-direct/completion-20261026/o1-dependency-compatibility-v1/
records/phase1-direct/factory-20261101/o1-dependency-root-control-v1/
```

Exact successor changes required:

| Existing source/function | Required successor binding |
|---|---|
| `o1-xgen-build-package-v2/xgen_common.py:9–15` | Bind `HERE`, `WORK`, `LIVE_ROOT`, `JOB` exclusively to fresh successor paths. Preserve old paths as readonly evidence. |
| `xgen_worker.py:30–43`, `stage_inputs()` | Retain validation of all 342 original pins. Separately declare the approved Boyer–Moore derivative and fixture/configuration inputs. Do not silently replace the pinned upstream identity. |
| `xgen_worker.py:152–167`, `prepare()` | Materialize only into fresh successor source/output directories; bind original preimage, approved transformation and resulting derivative hash explicitly. |
| `xgen_worker.py:90–112`, `scenarios()/build_commands()` | Point object root and project search paths at successor outputs; add retained `--config=ABSOLUTE_CGPR` to every later build. Dependency builds remain DEBUG/static; future consumers use `EXTERNALLY_BUILT=true` only after qualification. |
| `xgen_worker.py:170–210`, `run()` | Register finite help/configuration/fixture stages and distinct result fields. Gate compilation on validated CGPR bytes. Do not reach core/helpers/generation/recovery automatically from preparation-only authorization. |
| `xgen_worker.py:194–196` | Replace its “all staged sources equal originals” check with two explicit obligations: unchanged inputs match original pins; the sole approved derivative matches its separately recorded identity. Preserve the original identity check. |
| `xgen_diagnostics.py:74–119` | Register separate diagnostic policies for new stages. Current dispatcher rejects unknown stages; current compiler allowlist is not a help-output policy. |
| `progress_policy_source.py`, `progress-policy.json` | Bind the successor input/derivative roster and fixture progress records. No warning exemptions. |
| `xgen_guard.py:253–270` | Fresh package/job/work identities and manifest; preserve freshness refusal, capacity, memory, timeout and terminal requirements. |
| D159 `launch.sh:7,79–84` | A separately reviewed binding must select fresh control root and successor guard. Existing D159 launch is fixed to old root/guard. |
| `profile.json`, manifests, registration, tests, policy origins | New exact paths, identities, stage/output bounds and provenance. Keep old package references immutable. |

For the fixture, use a separate registered GPR/source/output directory; do not add files to the preserved upstream cut. No retained Boyer–Moore test suite exists. A minimal fixture needs the two deallocation paths and bounded search/lifecycle behavior established in the earlier report.

**Resolve selector grammar first with help readback only.** Proposed future argv:

```text
/home/sicarii/opt/gnat/gprbuild-aarch64-linux-26.0.0-1/bin/gprconfig --help
```

Pinned executable SHA256:

```text
58e81e9c21d18f20b80f7c2594a3f473621b64dff2498f191e4fbe2da9d0ce46
```

The separately authorized capture should:

- Verify executable identity before/after; record exact argv, environment, exit and complete stdout/stderr identities.
- Start with an allowlisted environment **before the first shell**, descriptors only 0/1/2, `LC_ALL=C`, `TZ=UTC`, controlled `PATH`, fresh owned `HOME/TMPDIR`; omit startup hooks, loader overrides and GPR overrides.
- Reuse existing readonly-root/network-isolation mechanisms; writable paths restricted to fresh registered capture storage.
- Bound wall time to **5 seconds plus 1-second kill grace**, CORE=0, and each output stream to **48 KiB**; reject reaching the ceiling rather than truncate. Total public capture plus bounded metadata stays below 120 KiB.
- Preserve the existing 8 GiB/zero-swap upper envelope if using the heavy workflow; make no tighter memory-adequacy claim without evidence.
- Pass **no** `-o`, `--config`, `--target`, project or generation arguments. Nonzero exit or incomplete capture remains failure/unknown, not usable grammar evidence.

**No existing approved wrapper identified here can perform that exact readback unchanged.** D158 `stage_command()` invokes `stage_diagnostics()`, which rejects this unregistered stage; its worker automatically proceeds into builds. D159 has fixed old guard/root bindings and requires empty public streams (`launch.sh:118–125`). The generic heavy runner is a reusable mechanism, but these fixed approved invocation packets do not authorize arbitrary help commands.

After successful help readback, extract and review exact tuple grammar, then prepare a separately bounded configuration-generation stage. Seal and inspect the resulting CGPR before any compile; consume it using `gprbuild --config`, not implicit generation or `--autoconf`.

All of this remains **planning/UNRUN**. No writes, native tools, locks, services, network or offloads performed. Full `'Old` guarantee unchanged; **F7 NOT PERFORMED**.