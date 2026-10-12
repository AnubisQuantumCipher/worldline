#ifndef WL_RESOURCE_OBSERVATION_V1_H
#define WL_RESOURCE_OBSERVATION_V1_H
#include "resource_run_ledger_v1.h"
/* Full arena spans and independent absence. Physical DTOs are data. */
typedef struct {
    wl_run_context current;
    wl_run_epoch current_epoch;
    wl_run_binding retained;
    wl_run_id current_universe_head;
    wl_run_id current_ledger_head;
    wl_run_id intent;
    wl_run_id dispatch;
    wl_run_id observation_head;
    wl_run_id actual_unit;
    wl_run_id cgroup;
    wl_run_id invocation;
    wl_run_id namespace;
    wl_run_id held_namespace;
    wl_run_id peer;
    wl_run_id held_peer;
    wl_run_id helper_image;
    wl_run_id expected_helper_image;
    wl_run_id challenge;
    wl_run_id held_challenge;
    wl_run_id protocol;
    wl_run_id closed_event;
    wl_run_id namespace_wait;
    wl_run_id helper_wait;
    wl_run_id cgroup_events;
    wl_run_id cgroup_type;
    wl_run_id manager_delegate;
    wl_run_epoch cgroup_owner;
    wl_run_epoch cgroup_group_write;
    wl_run_epoch cgroup_other_write;
    wl_run_id actual_store_genesis;
    wl_run_id actual_store_id;
    wl_run_id owner_store_genesis;
    wl_run_id owner_store_id;
    wl_run_id genesis_universe;
    wl_run_id genesis_instance;
    wl_run_id genesis_context_head;
    wl_run_id genesis_prime;
    wl_run_epoch genesis_root_count;
    uint8_t phase;
} wl_observation_facts;
typedef struct {
    wl_run_state state;
    wl_run_row item;
    wl_observation_facts captured;
} wl_observation_input;
uint32_t wl_resource_observation_version_v1(void);
long wl_resource_observation_layout_v1(uint32_t kind,uint32_t field);
int wl_resource_observation_current_v1(const void *input,size_t input_length,
    const void *arena,size_t arena_length,void *output,size_t output_length);
int wl_resource_observation_genesis_current_v1(const void *input,size_t input_length,
    const void *arena,size_t arena_length,void *output,size_t output_length);
int wl_resource_observation_classify_v1(const void *input,size_t input_length,
    const void *arena,size_t arena_length,void *output,size_t output_length);
#endif
