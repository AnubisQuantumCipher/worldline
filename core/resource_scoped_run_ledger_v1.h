#ifndef WL_RESOURCE_SCOPED_RUN_LEDGER_V1_H
#define WL_RESOURCE_SCOPED_RUN_LEDGER_V1_H
#include "resource_run_ledger_v1.h"
#include "resource_observation_v1.h"
/* Additive full scoped history. Packet fields/bytes are data, never authority. */
typedef struct {
    wl_run_context current;
    wl_run_epoch resource_epoch;
    wl_run_id universe_head;
    wl_run_id ledger_head;
    wl_run_id history_head;
    wl_run_id physical_head;
} wl_scoped_state;
typedef struct {
    wl_run_context scope;
    wl_run_epoch first_epoch;
    wl_run_id universe_head;
    wl_run_id frame_head;
    wl_run_id prior_frame;
    wl_run_id store_genesis;
    wl_run_id store_id;
    wl_run_id root_head;
    wl_run_id prime;
    wl_run_quantity root_count;
    wl_run_id cause;
    wl_run_id requester;
    wl_run_id receipt;
    wl_run_id catalogue_head;
    wl_run_id observation_head;
} wl_scoped_scope_frame;
typedef struct {
    wl_run_id machine;
    wl_run_id resource;
    wl_run_id unit;
} wl_scoped_physical_key;
typedef struct {
    wl_scoped_physical_key key;
    wl_run_quantity capacity;
    wl_run_quantity held_total;
    wl_run_quantity charged_total;
    wl_run_id capacity_source;
    wl_run_id catalogue_head;
    wl_run_id observation_head;
} wl_scoped_bucket;
typedef struct {
    wl_scoped_physical_key key;
    wl_run_binding bound;
    wl_run_context origin;
    wl_run_id catalogue_head;
    wl_run_quantity numerator;
    wl_run_quantity denominator;
    wl_run_quantity amount;
} wl_scoped_projection;
typedef struct {
    wl_run_context scope;
    wl_run_epoch resource_epoch;
    wl_run_id universe_head;
    wl_run_id ledger_head;
    wl_run_id history_head;
    wl_run_id physical_head;
    wl_run_id store_genesis;
    wl_run_id store_id;
    wl_run_id root_head;
    wl_run_id prime;
    wl_run_quantity root_count;
    wl_run_id cause;
    wl_run_id requester;
    wl_run_id receipt;
    wl_run_id catalogue_head;
    wl_run_id observation_head;
} wl_scoped_current_observation;
typedef struct {
    uint8_t kind;
    wl_run_request original;
    wl_run_epoch expected_epoch;
    wl_run_id expected_ledger_head;
    wl_run_id request_id;
    wl_run_id cause;
    wl_run_id requester;
    wl_run_id receipt;
} wl_scoped_intent;
typedef struct {
    uint32_t schema_version;
    wl_scoped_state before_state;
    wl_scoped_state proposed_state;
    wl_scoped_current_observation current;
    wl_scoped_intent request;
} wl_scoped_packet;
enum wl_scoped_layout_kind {
    WL_SCOPED_LAYOUT_STATE,
    WL_SCOPED_LAYOUT_SCOPE_FRAME,
    WL_SCOPED_LAYOUT_PHYSICAL_KEY,
    WL_SCOPED_LAYOUT_BUCKET,
    WL_SCOPED_LAYOUT_PROJECTION,
    WL_SCOPED_LAYOUT_CURRENT_OBSERVATION,
    WL_SCOPED_LAYOUT_INTENT,
    WL_SCOPED_LAYOUT_PACKET,
    WL_SCOPED_LAYOUT_RESULT
};
uint32_t wl_resource_scoped_run_ledger_version_v1(void);
long wl_resource_scoped_run_ledger_layout_v1(uint32_t kind, uint32_t field);
int wl_resource_scoped_run_ledger_check_v1(
    const void *input, size_t input_length, const void *arena, size_t arena_length,
    const void *history, size_t history_count,
    const void *proposed_history, size_t proposed_history_count,
    const void *rows, size_t rows_count,
    const void *proposed_rows, size_t proposed_rows_count,
    const void *projection, size_t projection_count,
    const void *proposed_projection, size_t proposed_projection_count,
    const void *buckets, size_t buckets_count,
    const void *proposed_buckets, size_t proposed_buckets_count,
    const void *actual_buckets, size_t actual_buckets_count,
    const void *observed, size_t observed_count,
    const void *facts, size_t facts_count,
    void *output, size_t output_length);
/* Consistent snapshot data does not authorize a transition. */
int wl_resource_scoped_run_ledger_validate_v1(
    const void *input, size_t input_length, const void *arena, size_t arena_length,
    const void *history, size_t history_count,
    const void *proposed_history, size_t proposed_history_count,
    const void *rows, size_t rows_count,
    const void *proposed_rows, size_t proposed_rows_count,
    const void *projection, size_t projection_count,
    const void *proposed_projection, size_t proposed_projection_count,
    const void *buckets, size_t buckets_count,
    const void *proposed_buckets, size_t proposed_buckets_count,
    const void *actual_buckets, size_t actual_buckets_count,
    const void *observed, size_t observed_count,
    const void *facts, size_t facts_count,
    void *output, size_t output_length);
/* All original numeric magnitudes and complete retained rows/history remain required.
 * Pointer/extent bounds describe transport storage only, not quantity/epoch caps.
 * Complete pointer, native semantics, caller and cost proof remain OPEN REQUIRED. */
int wl_resource_scoped_run_ledger_classify_v1(
    const void *input, size_t input_length, const void *arena, size_t arena_length,
    const void *history, size_t history_count,
    const void *proposed_history, size_t proposed_history_count,
    const void *rows, size_t rows_count,
    const void *proposed_rows, size_t proposed_rows_count,
    const void *projection, size_t projection_count,
    const void *proposed_projection, size_t proposed_projection_count,
    const void *buckets, size_t buckets_count,
    const void *proposed_buckets, size_t proposed_buckets_count,
    const void *actual_buckets, size_t actual_buckets_count,
    const void *observed, size_t observed_count,
    const void *facts, size_t facts_count,
    void *output, size_t output_length);
#endif
