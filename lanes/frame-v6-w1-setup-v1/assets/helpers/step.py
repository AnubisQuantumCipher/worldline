import os, re, sys, time

def main(argv):
    if (len(argv) != 4 or argv[1] not in ('begin', 'done')
            or re.fullmatch(r'[A-J]|R[A-J]-[0-9]+', argv[2]) is None
            or re.fullmatch(r'[0-9]+(\.[0-9]+)?', argv[3]) is None):
        return 2
    line = ('%s %s %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), argv[1], argv[3])).encode('ascii')
    try:
        fd = os.open('/root/wlscratch-staging/log/S-' + argv[2] + '.log',
                     os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError:
        return 3
    status = 0
    try:
        size = os.fstat(fd).st_size
        if size > 0 and os.pread(fd, 1, size - 1) != b'\n':
            status = 3
        else:
            written = 0
            while written < len(line):
                n = os.write(fd, line[written:])
                if n <= 0:
                    status = 3
                    break
                written += n
            if status == 0:
                os.fsync(fd)
    except OSError:
        status = 3
    try:
        os.close(fd)
    except OSError:
        status = 3
    return status

sys.exit(main(sys.argv))
