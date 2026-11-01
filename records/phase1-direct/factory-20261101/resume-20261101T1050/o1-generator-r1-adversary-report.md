**REVISE — this exact packet does not yet satisfy its stated failure contracts. No launch authorization.**

Reviewed carrier HEAD `e6444ed158dd042d544cbeedc0e9871d47445c5c`. Packet SHA256 matches `c523710945b4eea07933107a9efaef96ea21b03f0e1b8b96eb4447985679b25f`; manifest matches `ecb97b933a8f1440cb738d07c9883292647a39ea2d539a754c4f49c2b791c23f`. All packet-listed hashes/sizes matched before and after review. Package accounting is consistent: 45 manifest payloads plus manifest = 46 files / 1,097,130 bytes.

Two concrete counterexamples require correction:

1. **Final completion-receipt failure can return success.** `xgen_guard.py:362–365` ignores the Boolean returned by `best_effort_record`. After successful terminal monitoring, an `OSError` while writing the final guard result produces exit **0**, without that result receipt. This is a demonstrated error-handling path, with the I/O failure injected in memory; an actual disk/device failure was not induced. Terminal observation can remain valid, but successful evidence retention is missing. Make the final write’s success necessary for exit 0; failure must propagate a nonzero result. Preserve cleanup semantics and retained earlier receipts.

2. **Zero-exit build warnings are accepted.** `xgen_worker.py:77–85` checks exit code, capture length and inventory, but never examines diagnostic content. `run()` at lines 186–188 can consequently mark build `OBSERVED` after such a stage. I supplied an in-memory successful subprocess result containing `gprbuild: warning: synthetic project warning`; `stage_command` returned normally with exit 0 and retained the warning. Compiler `-gnatwe`/`-Werror` flags do not themselves implement the stated contract for every producer in the GPR/build/link graph. Add bounded diagnostic validation or producer-specific fatal-warning controls covering that graph. **This is a synthetic consumer counterexample; I did not demonstrate that the exact authentic pinned build emits a zero-exit warning.**

Exact principal counterexample command, run from the carrier:

```bash
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -W error - <<'PY'
import sys, pathlib, io, types, hashlib
from unittest.mock import patch, Mock
base = pathlib.Path(
    'records/phase1-direct/factory-20261101/o1-xgen-build-package-v1'
).resolve()
sys.path.insert(0, str(base))
import xgen_worker as w, xgen_guard as g

streams = {}
class Stream(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): return False
class MemoryPath:
    def __init__(self, name): self.name = name
    def __truediv__(self, name): return MemoryPath(self.name+'/'+name)
    def open(self, *args, **kwargs):
        stream = Stream()
        streams[self.name] = stream
        return stream
    def __str__(self): return self.name
def fake_run(argv, **kwargs):
    kwargs['stdout'].write(b'Compile [Ada] unit.adb\n')
    kwargs['stderr'].write(b'gprbuild: warning: synthetic project warning\n')
    return types.SimpleNamespace(returncode=0)
def fake_digest(path):
    raw = streams[path.name].getvalue()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

with patch.object(w, 'LIVE_ROOT', MemoryPath('memory')), \
     patch.object(w, 'isolated', side_effect=lambda argv, cwd: argv), \
     patch.object(w.subprocess, 'run', side_effect=fake_run), \
     patch.object(w, 'digest', side_effect=fake_digest), \
     patch.object(w, 'inventory', return_value=({}, 0)):
    receipts = []
    w.stage_command('core', ['NEVER_EXECUTED'],
                    pathlib.Path('/mock'), 1, 10**20, receipts)
    print('ZERO_EXIT_WARNING_ACCEPTED', receipts[0]['exit'],
          streams['memory/logs/core.stderr'].getvalue())

class FinalWriteFailure(io.StringIO):
    def write(self, text):
        if '"normal_wrapper_exit"' in text:
            raise OSError('synthetic receipt device failure')
        return super().write(text)

with patch.object(g.subprocess, 'Popen', return_value=Mock(pid=123)), \
     patch.object(g, 'monitor', return_value=(0, None)):
    stream = FinalWriteFailure()
    code = g.run(stream, ['NEVER_EXECUTED'])
    print('FINAL_WRITE_OSERROR_GUARD_EXIT', code,
          'HAS_FINAL_RECEIPT', 'normal_wrapper_exit' in stream.getvalue())
PY
```

Observed output:

```text
ZERO_EXIT_WARNING_ACCEPTED 0 b'gprbuild: warning: synthetic project warning\n'
FINAL_WRITE_OSERROR_GUARD_EXIT 0 HAS_FINAL_RECEIPT False
```

Other verified evidence:

- Inspected the test entrypoints first. The explicit read-only command passed **34/34 tests in 0.062 seconds**:

  ```bash
  PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 XGEN_READ_ONLY_TESTS=1 \
    /usr/bin/python3 -B -W error source_tests.py
  ```

- Called only observational `verify_packet()` and `verify_pins(load_json(...))` for both pin lists; all passed in **0.871 seconds**. This validates current recorded identities, not tool correctness or complete loaded dependency closure.
- The inherited helper uses the explicit shared lock `/home/sicarii/.worldline-heavy.lock` (`scripts/phase1_heavy.py:16,64`), post-lock 14GiB admission (`74–81`), and 8GiB/swap0 scope plus worker readback (`89–92,139–145`). Sanitizing `HOME` does not redirect this lock.
- The fixed DEBUG/static/j2 command graph, original GPR paths, 21-output/35-callback source join, two-generation comparison, strict typed recovery inventory, and live-versus-collected terminal distinction are present. The passing tests support their bounded synthetic behavior; they do not establish native execution.
- Sampling is explicitly observational rather than an aggregate quota. I do not count the acknowledged absence of a hard aggregate quota as a newly discovered defect.
- Local recovery compares names/types/modes/bytes/hashes and root mode. It intentionally does not establish full filesystem metadata preservation or DUAT retirement authority.

The smallest sound next step is the permitted evidence-driven source revision for these two failure contracts, followed by the prescribed fresh immutable review/judge path. Any later attempt still needs current storage-owner handoff/admission; native sandbox isolation, actual memory/disk fit, complete diagnostics, two authentic matching generations, native recovery and exact terminal readback remain **UNRUN/UNPROVEN**.

This is internal NONAUTHOR adversarial review, **not F7 independent acceptance**. IPC composition remains **BLOCKED**, without reset. No operational main, compiler, generator, proof, archive, mount, service, lock or network operation was executed; no files or scratch directories were created. Bounded checks consumed far below the 60-second aggregate allowance. No current peer verdict was sought or received.

<oai-mem-citation>
<citation_entries>
MEMORY.md:701-703|note=[carrier identity and non-final acceptance boundaries rechecked against current source]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>
