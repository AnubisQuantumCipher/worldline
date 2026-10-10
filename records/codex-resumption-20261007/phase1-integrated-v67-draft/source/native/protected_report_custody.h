/* Actual report descriptor custody at the existing finalized native exit.
 * Included after lifetime_stream.h and workload_boundary.h. No Python callbacks,
 * caller-provided paths, report reads, or changes to the original exit status.
 */
#include <sys/un.h>

static int
wl_report_poll(int channel, short events)
{
    for (;;) {
        uint64_t now;
        if (wl_now(&now) < 0 || now >= lifetime.deadline_ns) {
            errno = ETIMEDOUT;
            return -1;
        }
        uint64_t remaining = lifetime.deadline_ns - now;
        uint64_t millis = remaining / 1000000 + (remaining % 1000000 != 0);
        struct pollfd descriptor = {.fd = channel, .events = events};
        int result = poll(&descriptor, 1, millis > INT_MAX ? INT_MAX : (int)millis);
        if (result < 0 && errno == EINTR)
            continue;
        if (result < 0)
            return -1;
        if (result == 0)
            continue;
        if (descriptor.revents & events)
            return 0;
        errno = EPIPE;
        return -1;
    }
}

static int
wl_report_packet(int channel, unsigned char *bytes, size_t size, int report)
{
    union { struct cmsghdr alignment; unsigned char bytes[CMSG_SPACE(sizeof(int))]; } control;
    memset(&control, 0, sizeof(control));
    struct iovec vector = {.iov_base = bytes, .iov_len = size};
    struct msghdr message = {.msg_iov = &vector, .msg_iovlen = 1};
    if (report >= 0) {
        message.msg_control = control.bytes;
        message.msg_controllen = sizeof(control.bytes);
        struct cmsghdr *ancillary = CMSG_FIRSTHDR(&message);
        ancillary->cmsg_level = SOL_SOCKET;
        ancillary->cmsg_type = SCM_RIGHTS;
        ancillary->cmsg_len = CMSG_LEN(sizeof(int));
        memcpy(CMSG_DATA(ancillary), &report, sizeof(report));
    }
    for (;;) {
        if (wl_report_poll(channel, POLLOUT) < 0)
            return -1;
        ssize_t sent = sendmsg(channel, &message, MSG_DONTWAIT | MSG_NOSIGNAL);
        if (sent < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
            continue;
        if (sent == (ssize_t)size)
            return 0;
        if (sent >= 0)
            errno = EIO;
        return -1;
    }
}

static int
wl_report_ack(int channel)
{
    unsigned char ack[5];
    union { struct cmsghdr alignment; unsigned char bytes[65536]; } control;
    for (;;) {
        if (wl_report_poll(channel, POLLIN) < 0)
            return -1;
        struct iovec vector = {.iov_base = ack, .iov_len = sizeof(ack)};
        struct msghdr message = {.msg_iov = &vector, .msg_iovlen = 1,
            .msg_control = control.bytes, .msg_controllen = sizeof(control.bytes)};
        ssize_t received = recvmsg(channel, &message, MSG_DONTWAIT | MSG_CMSG_CLOEXEC);
        if (received < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
            continue;
        if (received < 0)
            return -1;
        int ancillary_seen = 0;
        for (struct cmsghdr *row = CMSG_FIRSTHDR(&message); row != NULL;
             row = CMSG_NXTHDR(&message, row)) {
            ancillary_seen = 1;
            if (row->cmsg_level == SOL_SOCKET && row->cmsg_type == SCM_RIGHTS &&
                row->cmsg_len >= CMSG_LEN(0)) {
                size_t count = (row->cmsg_len - CMSG_LEN(0)) / sizeof(int);
                for (size_t i = 0; i < count; ++i) {
                    int delivered;
                    memcpy(&delivered, CMSG_DATA(row) + i * sizeof(int), sizeof(delivered));
                    (void)close(delivered);
                }
            }
        }
        if (received == 4 && memcmp(ack, "WLPA", 4) == 0 && !ancillary_seen &&
            !(message.msg_flags & (MSG_TRUNC | MSG_CTRUNC)))
            return 0;
        errno = EPROTO;
        return -1;
    }
}

static void
wl_report_diagnostic(int operation, long result, int saved_errno)
{
    char message[192];
    int count = snprintf(message, sizeof(message),
        "WORLDLINE_NATIVE_REPORT_CUSTODY_FAILED operation=%d return=%ld errno=%d\n",
        operation, result, saved_errno);
    if (count > 0 && (size_t)count < sizeof(message))
        (void)write(STDERR_FILENO, message, (size_t)count);
}

static void
wl_protected_report_at_exit(void)
{
    /* The original exit wrapper has already observed interpreter finalization
     * and decided its original status. Abrupt exits cannot invent this record. */
    if (!lifetime.python_finalized || !lifetime.exit_attempted)
        return;
    static const char endpoint[] = "/run/worldline-protected-report.sock";
    struct stat endpoint_stat;
    if (lstat(endpoint, &endpoint_stat) < 0) {
        if (errno != ENOENT)
            wl_report_diagnostic(10, -1, errno);
        return;
    }
    int channel = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
    if (channel < 0) {
        wl_report_diagnostic(8, -1, errno);
        return;
    }
    int report = -1, operation = 9, saved_errno = 0;
    long returned = -1;
    struct sockaddr_un address = {.sun_family = AF_UNIX};
    memcpy(address.sun_path, endpoint, sizeof(endpoint));
    if (connect(channel, (struct sockaddr *)&address,
                offsetof(struct sockaddr_un, sun_path) + sizeof(endpoint)) < 0) {
        saved_errno = errno;
        goto failed;
    }
    operation = 1;
    report = open("/run/worldline-report/report", O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
    int open_errno = report == -1 ? errno : 0;
    if (report < 0) {
        returned = report;
        saved_errno = open_errno;
        goto report_error;
    }
    operation = 2;
    struct stat object;
    int fstat_result = fstat(report, &object);
    int fstat_errno = fstat_result == -1 ? errno : 0;
    if (fstat_result < 0) {
        returned = fstat_result;
        saved_errno = fstat_errno;
        goto report_error;
    }
    unsigned char header[128];
    memcpy(header, "WLPRv001", 8);
    wl_u64_bytes(header + 8, (uint64_t)object.st_dev);
    wl_u64_bytes(header + 16, (uint64_t)object.st_ino);
    wl_u64_bytes(header + 24, (uint64_t)object.st_mode);
    wl_u64_bytes(header + 32, (uint64_t)object.st_uid);
    wl_u64_bytes(header + 40, (uint64_t)object.st_gid);
    wl_u64_bytes(header + 48, (uint64_t)object.st_size);
    /* Retain each original timespec cell; nanosecond totals may exceed int64. */
    wl_u64_bytes(header + 56, (uint64_t)object.st_mtim.tv_sec);
    wl_u64_bytes(header + 64, (uint64_t)object.st_mtim.tv_nsec);
    wl_u64_bytes(header + 72, (uint64_t)object.st_ctim.tv_sec);
    wl_u64_bytes(header + 80, (uint64_t)object.st_ctim.tv_nsec);
    wl_u64_bytes(header + 88, (uint64_t)object.st_nlink);
    /* Native open result is independent of the daemon's received FD number. */
    wl_u64_bytes(header + 96, (uint64_t)report);
    wl_u64_bytes(header + 104, (uint64_t)open_errno);
    wl_u64_bytes(header + 112, (uint64_t)fstat_result);
    wl_u64_bytes(header + 120, (uint64_t)fstat_errno);
    operation = 3;
    if (wl_report_packet(channel, header, sizeof(header), report) < 0) {
        saved_errno = errno;
        goto failed;
    }
    goto acknowledged;
report_error: {
        unsigned char error[32];
        memcpy(error, "WLPEv001", 8);
        wl_u64_bytes(error + 8, (uint64_t)operation);
        wl_u64_bytes(error + 16, (uint64_t)returned);
        wl_u64_bytes(error + 24, (uint64_t)saved_errno);
        wl_report_diagnostic(operation, returned, saved_errno);
        operation = 3;
        if (wl_report_packet(channel, error, sizeof(error), -1) < 0) {
            saved_errno = errno;
            goto failed;
        }
    }
acknowledged:
    operation = 4;
    if (wl_report_ack(channel) < 0) {
        saved_errno = errno;
        goto failed;
    }
    if (report >= 0) {
        operation = 5;
        returned = close(report);
        saved_errno = returned == -1 ? errno : 0;
        report = -1; /* Linux releases the descriptor even on close errors. */
        unsigned char receipt[24];
        memcpy(receipt, "WLPCv001", 8);
        wl_u64_bytes(receipt + 8, (uint64_t)returned);
        wl_u64_bytes(receipt + 16, (uint64_t)saved_errno);
        if (wl_report_packet(channel, receipt, sizeof(receipt), -1) < 0) {
            operation = 3;
            saved_errno = errno;
            goto failed;
        }
        if (returned != 0)
            wl_report_diagnostic(5, returned, saved_errno);
    }
    operation = 6;
    returned = shutdown(channel, SHUT_WR);
    if (returned < 0) {
        saved_errno = errno;
        goto failed;
    }
    if (close(channel) < 0)
        wl_report_diagnostic(7, -1, errno);
    return;
failed:
    wl_report_diagnostic(operation, returned, saved_errno);
    if (report >= 0 && close(report) < 0)
        wl_report_diagnostic(5, -1, errno);
    if (close(channel) < 0)
        wl_report_diagnostic(7, -1, errno);
}
