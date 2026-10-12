/* Disposable campaign fault operator. No custody/native verdict is replaced.
 * aarch64 only: attach an actually held pidfd's PID; suppress exactly one real
 * file syscall and return -EIO, or kill at its entry/exit. Rootguard/selected
 * source admission and original process ownership belong to the parent runner.
 */
#define _GNU_SOURCE
#include <asm/ptrace.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/elf.h>
#include <limits.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <linux/ptrace.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <unistd.h>

#if !defined(__aarch64__)
#error The original selected fault operator requires the qualified aarch64 ABI
#endif

static void fail(const char *what) { perror(what); exit(1); }
static unsigned long number(const char *word) {
    char *end = NULL;
    errno = 0;
    unsigned long value = strtoul(word, &end, 10);
    if (errno || !*word || *end || *word == '-' || *word == '+') {
        fputs("FAULT_EXACT_UNSIGNED_ARGUMENT_REQUIRED\n", stderr); exit(1);
    }
    return value;
}
static void remote_string(pid_t pid, uint64_t address, char *out, size_t capacity) {
    size_t used = 0;
    while (used < capacity) {
        errno = 0;
        long value = ptrace(PTRACE_PEEKDATA, pid, (void *)(uintptr_t)(address + used), NULL);
        if (value == -1 && errno) fail("PTRACE_PEEKDATA");
        size_t count = sizeof(value);
        if (count > capacity - used) count = capacity - used;
        memcpy(out + used, &value, count);
        if (memchr(out + used, 0, count)) return;
        used += count;
    }
    fputs("FAULT_PATH_EXCEEDS_ORIGINAL_PATH_CAPACITY\n", stderr); exit(1);
}
static void descriptor_path(pid_t pid, uint64_t fd, char *out, size_t capacity) {
    char proc[96];
    int length = snprintf(proc, sizeof(proc), "/proc/%ld/fd/%lu", (long)pid, (unsigned long)fd);
    if (length < 0 || (size_t)length >= sizeof(proc)) fail("descriptor name");
    ssize_t count = readlink(proc, out, capacity - 1);
    if (count < 0) fail("readlink original descriptor");
    if ((size_t)count == capacity - 1) { fputs("FAULT_DESCRIPTOR_PATH_TRUNCATED\n", stderr); exit(1); }
    out[count] = 0;
}
static void registers(pid_t pid, struct user_pt_regs *regs, int write_back) {
    struct iovec view = {.iov_base = regs, .iov_len = sizeof(*regs)};
    if (ptrace(write_back ? PTRACE_SETREGSET : PTRACE_GETREGSET,
               pid, (void *)(uintptr_t)NT_PRSTATUS, &view) < 0) fail("original registers");
    if (view.iov_len != sizeof(*regs)) {
        fputs("FAULT_REGISTER_ABI_CHANGED\n", stderr); exit(1);
    }
}
static void corrupt_readback(const char *wal) {
    size_t length = strlen(wal);
    if (strncmp(wal, "/srv/cosmogony-canonical-v1.control-",
                sizeof("/srv/cosmogony-canonical-v1.control-") - 1)) {
        fputs("FAULT_ACTUAL_DISPOSABLE_SQLITE_WAL_REQUIRED\n", stderr); exit(1);
    }
    char database[4096];
    int selected_wal = length >= 5 && !strcmp(wal + length - 4, "-wal");
    if (selected_wal) {
        /* Preserve the complete original accepted WAL-to-database route. */
        if (length - 4 >= sizeof(database)) { fputs("FAULT_DATABASE_PATH_TRUNCATED\n", stderr); exit(1); }
        memcpy(database, wal, length - 4); database[length - 4] = 0;
    } else {
        /* The original custody-v2 owner creates DELETE mode. Its durable
         * boundary fsyncs this actual named DB before complete readback. */
        static const char suffix[] = "/authority/issuer/state/root-custody-v2.sqlite";
        size_t suffix_length = sizeof(suffix) - 1;
        if (length <= suffix_length || strcmp(wal + length - suffix_length, suffix)) {
            fputs("FAULT_ACTUAL_ORIGINAL_DELETE_DATABASE_REQUIRED\n", stderr); exit(1);
        }
        if (length >= sizeof(database)) { fputs("FAULT_DATABASE_PATH_TRUNCATED\n", stderr); exit(1); }
        memcpy(database, wal, length); database[length] = 0;
    }
    int fd = open(database, O_RDWR | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) fail("actual durable readback database");
    struct stat observed;
    if (fstat(fd, &observed) < 0) fail("actual readback inode");
    if (!S_ISREG(observed.st_mode) || observed.st_uid != 0 || observed.st_nlink != 1 ||
        (observed.st_mode & 022)) { fputs("FAULT_DATABASE_NOT_PRIVATE_ORIGINAL_INODE\n", stderr); exit(1); }
    unsigned char before[16];
    if (pread(fd, before, sizeof(before), 0) != sizeof(before)) fail("actual header preimage");
    if (!selected_wal && memcmp(before, "SQLite format 3", sizeof(before))) {
        fputs("FAULT_ACTUAL_ORIGINAL_DELETE_SQLITE_HEADER_REQUIRED\n", stderr); exit(1);
    }
    static const unsigned char bad[16] = "bad-readback-v1!";
    if (pwrite(fd, bad, sizeof(bad), 0) != sizeof(bad) || fsync(fd) < 0) fail("actual header corruption");
    fprintf(stderr, "ACTUAL_READBACK_HEADER_PREIMAGE path=%s dev=%lu inode=%lu bytes=",
            database, (unsigned long)observed.st_dev, (unsigned long)observed.st_ino);
    for (size_t i = 0; i < sizeof(before); ++i) fprintf(stderr, "%02x", before[i]);
    fputc('\n', stderr); fflush(stderr);
    if (close(fd) < 0) fail("close actual readback fault");
}
static int selected_path(const char *actual, const char *selection) {
    const char *star = strchr(selection, '*');
    if (!star) return !strcmp(actual, selection);
    if (strchr(star + 1, '*') || star == selection || star[-1] != '/' || star[1] != '/') {
        fputs("FAULT_SINGLE_ORIGINAL_OPERATION_COMPONENT_REQUIRED\n", stderr); exit(1);
    }
    size_t prefix = (size_t)(star - selection);
    if (strncmp(actual, selection, prefix)) return 0;
    const char *suffix = strchr(actual + prefix, '/');
    return suffix && suffix != actual + prefix && !strcmp(suffix, star + 1);
}
static void armed(pid_t pid, int pidfd, char **argv, unsigned long occurrence) {
    fprintf(stderr, "ACTUAL_SYSCALL_FAULT_ARMED pid=%ld pidfd=%d syscall=%s occurrence=%lu effect=%s path_hex=",
            (long)pid, pidfd, argv[3], occurrence, argv[6]);
    const unsigned char *path = (const unsigned char *)argv[4];
    for (; *path; ++path) fprintf(stderr, "%02x", (unsigned int)*path);
    fputc('\n', stderr);
    if (fflush(stderr) < 0 || ferror(stderr)) fail("actual arm acknowledgment");
}
int main(int argc, char **argv) {
    if (argc != 7 || geteuid() != 0) {
        fputs("usage: syscall_fault PID PIDFD SYSCALL ABSOLUTE_PATH OCCURRENCE eio|kill-entry|kill-exit|corrupt-readback-exit\n", stderr);
        return 1;
    }
    unsigned long raw_pid = number(argv[1]), raw_pidfd = number(argv[2]);
    if (raw_pid > INT_MAX || raw_pidfd > INT_MAX) return 1;
    pid_t pid = (pid_t)raw_pid;
    int pidfd = (int)raw_pidfd;
    unsigned long wanted = number(argv[5]);
    if (pid <= 0 || wanted == 0 || argv[4][0] != '/') return 1;
    /* pidfd identity is kernel-owned; never attach using a caller PID alone. */
    char info_path[96], info[4096];
    snprintf(info_path, sizeof(info_path), "/proc/self/fdinfo/%d", pidfd);
    int fd = open(info_path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) fail("inherited actual pidfd");
    ssize_t got = read(fd, info, sizeof(info) - 1);
    if (got <= 0) fail("pidfd fdinfo");
    close(fd); info[got] = 0;
    char expected[96];
    snprintf(expected, sizeof(expected), "\nPid:\t%ld\n", (long)pid);
    if (!strstr(info, expected)) {
        fputs("FAULT_HELD_PIDFD_PID_CHANGED\n", stderr); return 1;
    }
    int create_only = !strcmp(argv[3], "openat-create");
    long syscall_number;
    if (!strcmp(argv[3], "openat") || create_only) syscall_number = SYS_openat;
    else if (!strcmp(argv[3], "fsync")) syscall_number = SYS_fsync;
    else if (!strcmp(argv[3], "fdatasync")) syscall_number = SYS_fdatasync;
    else if (!strcmp(argv[3], "pread64")) syscall_number = SYS_pread64;
    else if (!strcmp(argv[3], "pwrite64")) syscall_number = SYS_pwrite64;
    else { fputs("FAULT_ORIGINAL_FILE_SYSCALL_REQUIRED\n", stderr); return 1; }
    int eio = !strcmp(argv[6], "eio");
    int kill_entry = !strcmp(argv[6], "kill-entry");
    int kill_exit = !strcmp(argv[6], "kill-exit");
    int corrupt = !strcmp(argv[6], "corrupt-readback-exit");
    if (!eio && !kill_entry && !kill_exit && !corrupt) return 1;
    if (ptrace(PTRACE_SEIZE, pid, NULL, (void *)(uintptr_t)PTRACE_O_TRACESYSGOOD) < 0) fail("PTRACE_SEIZE");
    if (ptrace(PTRACE_INTERRUPT, pid, NULL, NULL) < 0) fail("PTRACE_INTERRUPT");
    int status;
    if (waitpid(pid, &status, __WALL) != pid || !WIFSTOPPED(status)) fail("actual initial stop");
    unsigned long matches = 0;
    int selected = 0;
    int pending_signal = 0;
    int arm_emitted = 0;
    for (;;) {
        if (ptrace(PTRACE_SYSCALL, pid, NULL, (void *)(uintptr_t)pending_signal) < 0) fail("PTRACE_SYSCALL");
        pending_signal = 0;
        if (!arm_emitted) { armed(pid, pidfd, argv, wanted); arm_emitted = 1; }
        if (waitpid(pid, &status, __WALL) != pid) fail("actual traced wait");
        if (WIFEXITED(status) || WIFSIGNALED(status)) {
            fputs("FAULT_TARGET_TERMINATED_BEFORE_INJECTION\n", stderr); return 1;
        }
        if (!WIFSTOPPED(status)) continue;
        if (WSTOPSIG(status) != (SIGTRAP | 0x80)) {
            int signal_number = WSTOPSIG(status);
            if (signal_number != SIGTRAP) pending_signal = signal_number;
            continue;
        }
        struct ptrace_syscall_info call;
        memset(&call, 0, sizeof(call));
        if (ptrace(PTRACE_GET_SYSCALL_INFO, pid, sizeof(call), &call) < 0) fail("PTRACE_GET_SYSCALL_INFO");
        if (call.op == PTRACE_SYSCALL_INFO_ENTRY && (long)call.entry.nr == syscall_number) {
            if (create_only && (call.entry.args[2] & (O_CREAT | O_EXCL)) != (O_CREAT | O_EXCL)) continue;
            char path[4096];
            if (syscall_number == SYS_openat) remote_string(pid, call.entry.args[1], path, sizeof(path));
            else descriptor_path(pid, call.entry.args[0], path, sizeof(path));
            if (!selected_path(path, argv[4])) continue;
            if (++matches != wanted) continue;
            selected = 1;
            if (corrupt && strchr(argv[4], '*')) {
                fputs("FAULT_READBACK_REQUIRES_EXACT_ACTUAL_DATABASE_PATH\n", stderr); return 1;
            }
            fprintf(stderr, "ACTUAL_SYSCALL_SELECTED pid=%ld nr=%ld occurrence=%lu path=%s effect=%s\n",
                    (long)pid, syscall_number, matches, path, argv[6]);
            fflush(stderr);
            if (kill_entry) {
                if (syscall(SYS_pidfd_send_signal, pidfd, SIGKILL, NULL, 0) < 0) fail("actual pidfd kill");
                if (ptrace(PTRACE_DETACH, pid, NULL, NULL) < 0 && errno != ESRCH) fail("detach killed target");
                fputs("ACTUAL_SYSCALL_FAULT_APPLIED kill-entry\n", stderr);
                return 0;
            } else if (eio) {
                int cancelled = -1;
                struct iovec call_register = {.iov_base = &cancelled, .iov_len = sizeof(cancelled)};
                if (ptrace(PTRACE_SETREGSET, pid, (void *)(uintptr_t)NT_ARM_SYSTEM_CALL,
                           &call_register) < 0) fail("cancel actual file syscall");
            }
        } else if (selected && call.op == PTRACE_SYSCALL_INFO_EXIT) {
            if (kill_exit) {
                if (syscall(SYS_pidfd_send_signal, pidfd, SIGKILL, NULL, 0) < 0) fail("actual post-effect pidfd kill");
            } else if (eio) {
                struct user_pt_regs regs;
                registers(pid, &regs, 0);
                regs.regs[0] = (uint64_t)-(int64_t)EIO;
                registers(pid, &regs, 1);
            }
            if (corrupt) {
                if (call.exit.rval < 0) { fputs("FAULT_ORIGINAL_SYNC_ALREADY_FAILED\n", stderr); return 1; }
                corrupt_readback(argv[4]);
            }
            if (ptrace(PTRACE_DETACH, pid, NULL, NULL) < 0) {
                if (errno != ESRCH) fail("PTRACE_DETACH");
            }
            fprintf(stderr, "ACTUAL_SYSCALL_FAULT_APPLIED pid=%ld raw_return=%lld\n",
                    (long)pid, (long long)call.exit.rval);
            return 0;
        }
    }
}
