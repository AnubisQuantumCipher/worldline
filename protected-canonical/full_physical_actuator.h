#ifndef WORLDLINE_FULL_PHYSICAL_ACTUATOR_H
#define WORLDLINE_FULL_PHYSICAL_ACTUATOR_H
#include "worldline_canonical_exchange_v1.h"
#include "worldline_actuation_v1.h"
#include "vendor-transaction-035545/worldline_actuator.h"
enum wl_full_exchange_decision { WL_FULL_REFUSED, WL_FULL_DISPATCH_WORKER,
 WL_FULL_RECORD_WORKER, WL_FULL_DISPATCH_CANONICAL, WL_FULL_RECORD_EFFECT,
 WL_FULL_SETTLE_SAME_USE, WL_FULL_REPLAY_SAME_USE, WL_FULL_OWNER_RECORD_ABORT,
 WL_FULL_OWNER_RECORD_EFFECT };
uint32_t wl_internal_full_physical_version_v1(void);
long wl_internal_full_physical_layout_v1(uint32_t kind,uint32_t field);
/* Borrowed owned buffers/descriptors stay live through the call under the
 * selected protected-principal lock. Only WORLDLINE C_API exports these entry
 * points. Pointer readability, ownership, termination and syscall/durability
 * correspondence remain acceptance obligations; lengths do not prove them. */
int wl_internal_full_physical_exchange_v1(int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
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
int wl_internal_full_physical_recover_v1(int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
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
