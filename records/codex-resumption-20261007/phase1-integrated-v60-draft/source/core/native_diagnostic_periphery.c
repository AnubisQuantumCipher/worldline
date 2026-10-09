#define _GNU_SOURCE
#include "native_diagnostic_periphery.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pthread.h>
#include <signal.h>
#include <stdatomic.h>
#include <time.h>
#include <unistd.h>

static pthread_mutex_t native_mutex = PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP;
static _Thread_local unsigned native_depth;
static _Thread_local int prior_cancel_state;
static _Atomic uint32_t native_errors;

static void latch(uint32_t errors)
{
    if (errors != 0)
        atomic_fetch_or_explicit(&native_errors, errors, memory_order_relaxed);
}


int wl_native_call_enter_v1(void)
{
    int saved_errno = errno, previous, result;
    if (native_depth == UINT_MAX) {
        latch(WL_DIAG_GUARD);
        return EOVERFLOW;
    }
    result = pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &previous);
    if (result != 0) {
        latch(WL_DIAG_GUARD);
        errno = saved_errno;
        return result;
    }
    result = pthread_mutex_lock(&native_mutex);
    if (result != 0) {
        latch(WL_DIAG_GUARD);
        if (pthread_setcancelstate(previous, NULL) != 0)
            latch(WL_DIAG_CANCEL_RESTORE);
        errno = saved_errno;
        return result;
    }
    if (native_depth == 0) prior_cancel_state = previous;
    ++native_depth;
    errno = saved_errno;
    return 0;
}

int wl_native_call_leave_v1(void)
{
    int saved_errno = errno, result, restore;
    if (native_depth == 0) {
        latch(WL_DIAG_GUARD);
        return EPERM;
    }
    result = pthread_mutex_unlock(&native_mutex);
    if (result != 0) {
        /* Still owned: never claim release or re-enable cancellation. */
        latch(WL_DIAG_GUARD);
        errno = saved_errno;
        return result;
    }
    --native_depth;
    if (native_depth == 0) {
        restore = pthread_setcancelstate(prior_cancel_state, NULL);
        if (restore != 0) {
            latch(WL_DIAG_CANCEL_RESTORE);
            result = restore;
        }
    }
    errno = saved_errno;
    return result;
}

unsigned wl_native_call_depth_v1(void) { return native_depth; }
uint32_t wl_native_diag_errors_v1(void)
{
    return atomic_load_explicit(&native_errors, memory_order_relaxed);
}
void wl_native_diag_reset_errors_v1(void)
{
    if (native_depth != 0)
        atomic_store_explicit(&native_errors, 0, memory_order_relaxed);
}


uint32_t wl_native_diag_emit_v1(const void *bytes, size_t length)
{
    int saved_errno = errno, flags = -1, changed = 0, masked = 0;
    int had_pending = 0, broken = 0, own_signal_unresolved = 0;
    uint32_t failures = 0;
    size_t offset = 0;
    sigset_t block, previous, pending;
    const unsigned char *text = bytes;
    const unsigned char newline = '\n';
    if (native_depth == 0) {
        latch(WL_DIAG_GUARD);
        return WL_DIAG_GUARD;
    }
    sigemptyset(&block);
    sigaddset(&block, SIGPIPE);
    if (pthread_sigmask(SIG_BLOCK, &block, &previous) != 0) {
        failures |= WL_DIAG_SIGNAL_MASK;
        goto finish;
    }
    masked = 1;
    if (sigpending(&pending) != 0) {
        failures |= WL_DIAG_SIGNAL_PENDING;
        goto cleanup;
    }
    had_pending = sigismember(&pending, SIGPIPE);
    if (had_pending < 0) {
        failures |= WL_DIAG_SIGNAL_PENDING;
        goto cleanup;
    }
    flags = fcntl(STDERR_FILENO, F_GETFL);
    if (flags < 0) {
        failures |= WL_DIAG_GET_FLAGS;
        goto cleanup;
    }
    if (!(flags & O_NONBLOCK)) {
        /* A failed SETFL can have an ambiguous physical outcome. Attempt the
         * original restoration/readback even when the set itself reports error. */
        changed = 1;
        if (fcntl(STDERR_FILENO, F_SETFL, flags | O_NONBLOCK) != 0) {
            failures |= WL_DIAG_SET_FLAGS;
            goto cleanup;
        }
    }
    {
        int observed = fcntl(STDERR_FILENO, F_GETFL);
        if (observed < 0 || observed != (flags | O_NONBLOCK)) {
            failures |= WL_DIAG_READBACK;
            goto cleanup;
        }
    }
    while (offset < length) {
        size_t remaining = length - offset;
        /* The original complete String domain has no artificial message cap.
         * write's representable syscall extent is consumed in finite chunks. */
        size_t chunk = remaining > (size_t)SSIZE_MAX ? (size_t)SSIZE_MAX : remaining;
        ssize_t written = write(STDERR_FILENO, text + offset, chunk);
        if (written <= 0 || (size_t)written > chunk) {
            if (written == 0) failures |= WL_DIAG_ZERO_WRITE;
            else failures |= WL_DIAG_WRITE;
            if (written < 0 && errno == EPIPE) broken = 1;
            goto cleanup;
        }
        offset += (size_t)written;
    }
    {
        ssize_t written = write(STDERR_FILENO, &newline, 1);
        if (written != 1) {
            failures |= written == 0 ? WL_DIAG_ZERO_WRITE : WL_DIAG_WRITE;
            if (written < 0 && errno == EPIPE) broken = 1;
        }
    }
cleanup:
    if (changed && fcntl(STDERR_FILENO, F_SETFL, flags) != 0)
        failures |= WL_DIAG_RESTORE_FLAGS;
    if (flags >= 0) {
        int observed = fcntl(STDERR_FILENO, F_GETFL);
        if (observed < 0 || observed != flags) failures |= WL_DIAG_READBACK;
    }
    /* POSIX thread-scoped SIGPIPE pattern: preserve a signal pending on entry;
     * consume only a newly pending signal after this thread's actual EPIPE.
     * No signal disposition is installed, and no other thread is targeted. */
    if (broken && !had_pending) {
        if (sigpending(&pending) != 0) {
            failures |= WL_DIAG_SIGNAL_PENDING;
            own_signal_unresolved = 1;
        } else if (sigismember(&pending, SIGPIPE) == 1) {
            struct timespec zero = {0, 0};
            if (sigtimedwait(&block, NULL, &zero) != SIGPIPE) {
                failures |= WL_DIAG_SIGNAL_CONSUME;
                own_signal_unresolved = 1;
            }
        }
    }
    if (masked) {
        /* If actual signal cleanup failed, unblocking our unresolved SIGPIPE
         * can kill the consumer. Retain the safer mask and explicitly fail;
         * this is NOT successful restoration or successful retention. */
        if (own_signal_unresolved && sigismember(&previous, SIGPIPE) == 0)
            failures |= WL_DIAG_SIGNAL_RESTORE;
        else if (pthread_sigmask(SIG_SETMASK, &previous, NULL) != 0)
            failures |= WL_DIAG_SIGNAL_RESTORE;
    }
finish:
    latch(failures);
    errno = saved_errno;
    return failures;
}
