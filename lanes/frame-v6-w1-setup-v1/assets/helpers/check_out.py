import os, subprocess, sys

def write_all(fd, data):
    done = 0
    while done < len(data):
        n = os.write(fd, data[done:])
        if n <= 0:
            raise OSError('short write')
        done += n

def main(argv):
    if '--' not in argv:
        return 2
    i = argv.index('--')
    opts, cmd = argv[1:i], argv[i + 1:]
    if not cmd or not cmd[0].startswith('/'):
        return 2
    if opts in (['--print'], ['--empty']):
        mode, arg = opts[0], None
    elif len(opts) == 2 and opts[0] in ('--equal', '--line-ci'):
        mode, arg = opts
    else:
        return 2
    try:
        done = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, check=False)
    except OSError:
        return 4
    if done.returncode != 0:
        return 4
    out = done.stdout
    if mode == '--print':
        try:
            write_all(1, out)
        except OSError:
            return 6
        return 0
    if mode == '--empty':
        return 0 if out == b'' else 5
    try:
        with open(arg, 'rb') as f:
            want = f.read()
    except OSError:
        return 2
    if mode == '--equal':
        return 0 if out == want else 5
    if not want.endswith(b'\n') or want.count(b'\n') != 1:
        return 2
    return 0 if want[:-1].lower() in [l.lower() for l in out.split(b'\n')] else 5

sys.exit(main(sys.argv))
