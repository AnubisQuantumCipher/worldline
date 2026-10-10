#ifndef WL_RESOURCE_RUN_LEDGER_V1_H
#define WL_RESOURCE_RUN_LEDGER_V1_H
#include <stddef.h>
#include <stdint.h>
/* Magnitudes are arena spans, never uint64 values. Presence is independent. */
typedef struct {
    uint8_t present;
    int64_t first;
    int64_t length;
} wl_run_id;
typedef struct {
    uint8_t negative;
    int64_t first;
    int64_t length;
} wl_run_quantity;
typedef struct {
    uint8_t present;
    wl_run_quantity value;
} wl_run_epoch;
typedef struct {
    wl_run_id universe;
    wl_run_id policy;
    wl_run_id resource;
    wl_run_id unit;
    wl_run_id instance;
    wl_run_id host;
    wl_run_id boot;
    wl_run_id authority;
    wl_run_epoch policy_epoch;
} wl_run_context;
typedef struct {
    wl_run_id reservation;
    wl_run_id operation;
    wl_run_id owner;
    wl_run_id workload;
    wl_run_id universe_head;
    wl_run_id capability;
    wl_run_id grant_use;
    wl_run_id payload;
    wl_run_id provenance;
    wl_run_epoch resource_epoch;
} wl_run_binding;
typedef struct {
    wl_run_context scope;
    wl_run_binding bound;
    wl_run_id parent;
    uint8_t kind;
    uint8_t state;
    wl_run_quantity amount;
    wl_run_epoch observed_usage;
    wl_run_id planned_unit;
    wl_run_id actual_unit;
    wl_run_id cgroup;
    wl_run_id invocation;
} wl_run_row;
typedef struct {
    wl_run_context scope;
    wl_run_epoch resource_epoch;
    wl_run_id universe_head;
    wl_run_id ledger_head;
    wl_run_quantity capacity;
    wl_run_quantity held_total;
    wl_run_quantity charged_total;
} wl_run_state;
typedef struct {
    wl_run_context scope;
    wl_run_epoch resource_epoch;
    wl_run_binding bound;
    wl_run_id actual_unit;
    wl_run_id cgroup;
    wl_run_id invocation;
    wl_run_id observation_head;
    uint8_t observed;
} wl_run_native;
typedef struct {
    uint8_t kind;
    wl_run_context scope;
    wl_run_epoch expected_epoch;
    wl_run_id expected_ledger_head;
    wl_run_id request_id;
    wl_run_id reservation;
    wl_run_id operation_id;
    wl_run_id requester;
    wl_run_binding bound;
    wl_run_row new_row;
} wl_run_request;
typedef struct {
    uint32_t schema_version;
    wl_run_state before_state;
    wl_run_state proposed_state;
    wl_run_request intent;
} wl_run_packet;
typedef struct {
    uint32_t status;
} wl_run_result;
uint32_t wl_resource_run_ledger_version_v1(void);
long wl_resource_run_ledger_layout_v1(uint32_t kind,uint32_t field);
int wl_resource_run_ledger_check_v1(const void *input,size_t input_length,
    const void *arena,size_t arena_length,const void *before_rows,size_t before_count,
    const void *proposed_rows,size_t proposed_count,const void *native,size_t native_count,
    void *output,size_t output_length);
#endif
