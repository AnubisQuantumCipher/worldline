#ifndef WORLDLINE_FULL_PHYSICAL_V1_H
#define WORLDLINE_FULL_PHYSICAL_V1_H
#include "worldline_canonical_exchange_v1.h"
#include "worldline_actuation_v1.h"
enum wl_actuator_result {
 WL_ACTUATOR_VERIFIED=0, WL_ACTUATOR_REFUSED=1, WL_ACTUATOR_IO_REFUSED=2,
 WL_ACTUATOR_POST_EXCHANGE_UNCERTAIN=3
};
struct wl_actuator_witness {
 struct wl_entry_identity live_before,stage_before,live_after,stage_after;
 uint8_t marker_digest[WL_HASH_BYTES];
 uint8_t decision,exchange_attempted;
 int syscall_errno;
 uint8_t payload_durable,recovery_clean,parents_durable;
};
/* All buffers remain immutable/live through this synchronous borrowed call;
 * witness is exclusively owned and disjoint from every complete input extent.
 * Descriptors belong to the selected protected principal. Recover ignores the
 * peer descriptor and recognizes only a genuine historical RECORD_EFFECT.
 * No transport flag is an authorization or a substitute for native facts. */
uint32_t wl_full_physical_version_v1(void);
long wl_full_physical_layout_v1(uint32_t kind,uint32_t field);
int wl_full_physical_exchange_v1(int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
 const void *input,size_t input_length,const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *rows,size_t row_count,size_t row_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipt_count,size_t worker_receipt_length,
 const void *worker_events,size_t worker_event_count,size_t worker_event_length,
 const void *effect_receipts,size_t effect_receipt_count,size_t effect_receipt_length,
 const void *effect_events,size_t effect_event_count,size_t effect_event_length,
 const struct wl_actuation_request *actuation,size_t actuation_length,
 struct wl_actuator_witness *witness,size_t witness_length);
int wl_full_physical_recover_v1(int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
 const void *input,size_t input_length,const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *rows,size_t row_count,size_t row_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipt_count,size_t worker_receipt_length,
 const void *worker_events,size_t worker_event_count,size_t worker_event_length,
 const void *effect_receipts,size_t effect_receipt_count,size_t effect_receipt_length,
 const void *effect_events,size_t effect_event_count,size_t effect_event_length,
 const struct wl_actuation_request *actuation,size_t actuation_length,
 struct wl_actuator_witness *witness,size_t witness_length);
#endif
