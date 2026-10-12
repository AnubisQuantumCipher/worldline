#ifndef WORLDLINE_CANONICAL_OWNER_COMPLETION_V1_H
#define WORLDLINE_CANONICAL_OWNER_COMPLETION_V1_H
#include "worldline_canonical_exchange_v1.h"
/* Complete historical and current frames share the same owned arena. The
 * historical rosters precede the current rosters. Neither DTOs nor an earlier
 * native verdict establish protected historical custody. */
typedef struct {
 wl_canonical_exchange_input_v1 historical;
 wl_operation_input_v1 current;
} wl_canonical_owner_completion_input_v1;
typedef struct { uint8_t disposition; } wl_canonical_owner_completion_result_v1;
enum wl_canonical_owner_completion_decisions {
 WL_CANONICAL_OWNER_COMPLETION_REFUSED,
 WL_CANONICAL_OWNER_COMPLETION_RESOLVE_EFFECT,
 WL_CANONICAL_OWNER_COMPLETION_RESOLVE_NO_EFFECT,
 WL_CANONICAL_OWNER_COMPLETION_EFFECT_ALREADY,
 WL_CANONICAL_OWNER_COMPLETION_NO_EFFECT_ALREADY
};
uint32_t wl_canonical_owner_completion_version_v1(void);
long wl_canonical_owner_completion_layout_v1(uint32_t,uint32_t);
int wl_canonical_owner_completion_decide_v1(const void *input,size_t input_length,
 const void *arena,size_t arena_length,
 const void *grants,size_t grants_count,size_t grants_length,
 const void *uses,size_t uses_count,size_t uses_length,
 const void *rows,size_t rows_count,size_t rows_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipts_count,size_t worker_receipts_length,
 const void *worker_events,size_t worker_events_count,size_t worker_events_length,
 const void *effect_receipts,size_t effect_receipts_count,size_t effect_receipts_length,
 const void *effect_events,size_t effect_events_count,size_t effect_events_length,
 const void *current_grants,size_t current_grants_count,size_t current_grants_length,
 const void *current_uses,size_t current_uses_count,size_t current_uses_length,
 const void *current_receipts,size_t current_receipts_count,size_t current_receipts_length,
 const void *current_events,size_t current_events_count,size_t current_events_length,
 void *output,size_t output_length);
#endif
