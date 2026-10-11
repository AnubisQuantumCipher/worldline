#ifndef EVALUATION_PENDING_V2_H
#define EVALUATION_PENDING_V2_H
#include "evaluation_pending.h"
/* Additive ABI. All v1 layouts/exports stay available unchanged. The complete
 * v1 ownership/extent/immutability premises also apply here. Optional presence
 * is 0 or 1; present-empty requirement differs from absence. Layout kinds are
 * span, cursor, v2 row, v2 request, v2 result, optional requirement, in order.
 * Source copies and numeric checks do not authenticate the supplied store. */
typedef struct { uint32_t present; wl_pending_span value; }
  wl_pending_optional_requirement_v2;
typedef struct {
  wl_pending_span store_id, subject, content, run, sequence;
  wl_pending_cursor previous;
  uint32_t linked;
  wl_pending_optional_requirement_v2 requirement;
} wl_pending_row_v2;
typedef struct {
  uint32_t version, operation;
  const uint8_t *data;
  int64_t data_length;
  const wl_pending_row_v2 *rows;
  int64_t row_count;
  wl_pending_span store_id, subject, content, run, proposed_epoch;
  wl_pending_cursor authority_head, target_head;
  wl_pending_optional_requirement_v2 required;
} wl_pending_request_v2;
typedef struct {
  uint32_t reason;
  wl_pending_span sequence;
  int64_t selected;
  wl_pending_optional_requirement_v2 requirement;
} wl_pending_result_v2;
uint32_t wl_pending_abi_version_v2(void);
int64_t wl_pending_layout_size_v2(uint32_t kind);
int64_t wl_pending_layout_alignment_v2(uint32_t kind);
int64_t wl_pending_layout_offset_v2(uint32_t kind, uint32_t field);
int wl_pending_decide_v2(const wl_pending_request_v2 *, wl_pending_result_v2 *);
#endif
