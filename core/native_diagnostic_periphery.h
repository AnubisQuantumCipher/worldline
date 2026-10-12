#ifndef WORLDLINE_NATIVE_DIAGNOSTIC_PERIPHERY_H
#define WORLDLINE_NATIVE_DIAGNOSTIC_PERIPHERY_H
#include <stddef.h>
#include <stdint.h>

/* Environmental operations: no purity or termination claim. Input remains
 * immutable/readable until return. No pointer is retained. The original C_API
 * is the only Ada authority/periphery boundary. Every raw export owns this
 * same recursive guard before reading input and through handlers/drain. */
enum wl_native_diag_failure {
    WL_DIAG_GET_FLAGS = 1u << 0,
    WL_DIAG_SET_FLAGS = 1u << 1,
    WL_DIAG_WRITE = 1u << 2,
    WL_DIAG_ZERO_WRITE = 1u << 3,
    WL_DIAG_RESTORE_FLAGS = 1u << 4,
    WL_DIAG_READBACK = 1u << 5,
    WL_DIAG_SIGNAL_MASK = 1u << 6,
    WL_DIAG_SIGNAL_PENDING = 1u << 7,
    WL_DIAG_SIGNAL_CONSUME = 1u << 8,
    WL_DIAG_SIGNAL_RESTORE = 1u << 9,
    WL_DIAG_GUARD = 1u << 10,
    WL_DIAG_CANCEL_RESTORE = 1u << 11
};
/* enter disables cancellation before the lock and leaves it disabled until
 * the outermost leave. Nested entry is recursive. leave unlocks before it
 * restores cancellation; asynchronous cancellation can then take effect. */
int wl_native_call_enter_v1(void);
int wl_native_call_leave_v1(void);
unsigned wl_native_call_depth_v1(void);
uint32_t wl_native_diag_errors_v1(void);
/* Reset only after the original typed control accepts Enable=1, under the
 * same guard. Never reset on entry, drain, a foreign call or cancellation. */
void wl_native_diag_reset_errors_v1(void);
/* Writes exact bytes plus one LF to stderr. Returns a bitset, never throws,
 * never retries write EINTR/EAGAIN/zero, and never changes SIGPIPE disposition.
 * Caller exclusively owns the diagnostic observer descriptor/file-description
 * flags for this call (foreign non-WORLDLINE writes/dup2/close must be excluded).
 * The guard serializes ALL WORLDLINE uses, not unrelated application syscalls. */
uint32_t wl_native_diag_emit_v1(const void *bytes, size_t length);
/* SOURCE-ONLY transaction observation. The original frame alone arms an
 * inherited, exclusively owned O_WRONLY/O_NONBLOCK regular-file descriptor in
 * WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_ACTIVE_FD. No authority, cache,
 * guard bypass, stdout/stderr flag change or native diagnostic latch follows.
 * Six cold scalar boundaries only; no inputs/owners/payloads are retained.
 * Missing, short or failed writes supply no boundary evidence. No IO purity
 * or termination claim, and no retry, timeout or resource extension. */
void wl_native_transaction_boundary_v1(uint32_t phase);
#endif
