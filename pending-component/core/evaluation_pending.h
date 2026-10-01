#ifndef EVALUATION_PENDING_H
#define EVALUATION_PENDING_H
#include <stdint.h>

/* Caller owns correctly aligned, live request/result and complete input array
 * extents for the duration of this synchronous call. Input contents must remain
 * immutable. Result storage must be disjoint from request, row and byte extents;
 * read-only input extents may overlap. Numeric extent/alignment/disjointness
 * checks do not establish mapped/readable/writable memory, ownership or custody.
 * The entry snapshots request, rows and bytes into owned Ada objects before
 * calling the typed relation. Allocation/copy cost and native behavior require
 * separate evidence; snapshots do not authenticate concurrently mutable input.
 * Identity/epoch spans use first=1-based byte position; empty spans are legal.
 * Epochs are arbitrary-length unsigned little-endian magnitudes in the arena.
 * Result epoch is an input-arena span and must be copied before arena release.
 * Status 255 is a refused transport/check/allocation path, never admission.
 */
typedef struct { int64_t first, length; } wl_pending_span;
typedef struct {
  uint32_t present;
  wl_pending_span sequence, run;
} wl_pending_cursor;
typedef struct {
  wl_pending_span store_id, subject, content, run, sequence;
  wl_pending_cursor previous;
  uint32_t linked;
} wl_pending_row;
typedef struct {
  uint32_t version, operation;
  const uint8_t *data;
  int64_t data_length;
  const wl_pending_row *rows;
  int64_t row_count;
  wl_pending_span store_id, subject, content, run, proposed_epoch;
  wl_pending_cursor authority_head, target_head;
} wl_pending_request;
typedef struct {
  uint32_t reason;
  wl_pending_span sequence;
  int64_t selected;
} wl_pending_result;
/* Layout kinds 1..5: span, cursor, row, request, result. Field numbers follow
 * declaration order, starting at 1. Size includes trailing object padding and
 * is the row stride; alignment and every field offset must match the caller.
 * Unknown kind/field returns INT64_MAX. No size or pointer argument is inferred
 * from a successful layout query. ABI version remains 1; existing records and
 * decide signature are unchanged. A caller requiring these new checks must
 * refuse a library that does not export all queries. */
uint32_t wl_pending_abi_version_v1(void);
int64_t wl_pending_layout_size_v1(uint32_t kind);
int64_t wl_pending_layout_alignment_v1(uint32_t kind);
int64_t wl_pending_layout_offset_v1(uint32_t kind, uint32_t field);
int wl_pending_decide_v1(const wl_pending_request *, wl_pending_result *);
#endif
