#ifndef WORLDLINE_CANONICAL_EXCHANGE_V1_H
#define WORLDLINE_CANONICAL_EXCHANGE_V1_H
#include "worldline_canonical_operation_v1.h"
typedef struct {
 wl_recovery_binding_v3 worker_issued;
 wl_recovery_binding_v3 worker_recovered;
 wl_recovery_binding_v3 canonical_issued;
 wl_recovery_binding_v3 canonical_recovered;
 wl_recovery_native_v3 worker_native;
 wl_recovery_native_v3 canonical_native;
 wl_recovery_digest_v3 worker_receipt_genesis;
 wl_recovery_digest_v3 owner_receipt_genesis;
 wl_recovery_digest_v3 worker_receipt_head;
 wl_recovery_digest_v3 worker_causal_genesis;
 wl_recovery_digest_v3 owner_causal_genesis;
 wl_recovery_digest_v3 worker_causal_head;
 wl_recovery_digest_v3 quarantine_head;
} wl_canonical_exchange_material_v1;
typedef struct { wl_canonical_operation_input_v1 operation_input; wl_canonical_exchange_material_v1 material; uint8_t before,mode; } wl_canonical_exchange_input_v1;
typedef struct { uint8_t disposition; } wl_canonical_exchange_result_v1;
uint32_t wl_canonical_exchange_version_v1(void);
long wl_canonical_exchange_layout_v1(uint32_t,uint32_t);
int wl_canonical_exchange_decide_v1(const void *input,size_t input_length,const void *arena,size_t arena_length,
 const void *grants,size_t grants_count,size_t grants_length,
 const void *uses,size_t uses_count,size_t uses_length,
 const void *rows,size_t rows_count,size_t rows_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipts_count,size_t worker_receipts_length,
 const void *worker_events,size_t worker_events_count,size_t worker_events_length,
 const void *effect_receipts,size_t effect_receipts_count,size_t effect_receipts_length,
 const void *effect_events,size_t effect_events_count,size_t effect_events_length,
 void *output,size_t output_length);
#endif
