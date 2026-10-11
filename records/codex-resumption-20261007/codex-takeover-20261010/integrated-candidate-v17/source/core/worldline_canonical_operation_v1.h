#ifndef WORLDLINE_CANONICAL_OPERATION_V1_H
#define WORLDLINE_CANONICAL_OPERATION_V1_H
#include "worldline_operation_authority_v1.h"
#include "resource_run_ledger_v1.h"
#include "worldline_core.h"
typedef struct {
 wl_operation_input_v1 authority;
 wl_run_state state; wl_run_binding bound; wl_run_id requester;
 wl_operation_uid_v1 peer; struct wl_collapse_request collapse;
} wl_canonical_operation_input_v1;
typedef struct { uint8_t disposition; } wl_canonical_operation_result_v1;
uint32_t wl_canonical_operation_version_v1(void);
long wl_canonical_operation_layout_v1(uint32_t kind,uint32_t field);
int wl_canonical_operation_decide_v1(const void *input,size_t input_length,
 const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *rows,size_t row_count,size_t row_length,
 const void *observed,size_t observed_count,size_t observed_length,
 void *output,size_t output_length);
#endif
