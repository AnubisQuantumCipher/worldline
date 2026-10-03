"""Build only inside the independently reviewed Root native-build action."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys


def main():
    if len(sys.argv) != 2:
        raise SystemExit('expected a fresh external native-artifact directory')
    source = Path(__file__).resolve().parent / 'examiner_guard.c'
    header = source.with_name('lifetime_stream.h')
    inputs = {item.name: {'bytes': item.stat().st_size,
                         'sha256': hashlib.sha256(item.read_bytes()).hexdigest()}
              for item in (source, header)}
    requested = Path(sys.argv[1]).absolute()
    # Require a real existing parent; compare resolved objects, not a lexical
    # path that could point back into the frozen source through a symlink.
    output = requested.parent.resolve(strict=True) / requested.name
    if requested.exists() or requested.is_symlink():
        raise SystemExit('native output must be a fresh directory')
    if source.parent.parent == output or source.parent.parent in output.parents:
        raise SystemExit('native output must be outside the frozen source tree')
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    artifact = output / 'libworldline_examiner_guard.so'
    command = ['/usr/bin/gcc', '-B/usr/bin/', '-std=c11', '-Wall', '-Wextra', '-Werror',
               '-O2', '-fPIC', '-fno-strict-aliasing', '-shared',
               '-I/usr/include/python3.14', str(source), '-L/usr/lib', '-lpython3.14',
               '-Wl,-z,defs', '-Wl,-z,relro', '-Wl,-z,now', '-Wl,-z,noexecstack',
               '-o', str(artifact)]
    environment = {'PATH': '/usr/bin', 'LC_ALL': 'C'}
    print(json.dumps({'command': command, 'environment': environment,
                      'sourceSha256': inputs[source.name]['sha256'],
                      'sourceInputs': inputs}), flush=True)
    child = subprocess.run(command, env=environment, check=False)
    if child.returncode:
        raise SystemExit(child.returncode)
    if inputs != {item.name: {'bytes': item.stat().st_size,
                             'sha256': hashlib.sha256(item.read_bytes()).hexdigest()}
                  for item in (source, header)}:
        raise SystemExit('native source inputs changed during compilation')
    # ELF inspection has its own retained output. It does not load the library.
    subprocess.run(['/usr/bin/readelf', '--file-header', '--dynamic', '--wide', str(artifact)],
                   env=environment, check=True)
    result = {'artifact': str(artifact), 'bytes': artifact.stat().st_size,
              'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
              'compilerReturncode': child.returncode,
              'confinementAcceptance': False, 'phaseAcceptance': False}
    (output / 'build.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
