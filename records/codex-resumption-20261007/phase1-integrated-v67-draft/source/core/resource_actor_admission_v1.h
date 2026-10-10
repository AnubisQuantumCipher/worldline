#ifndef WL_RESOURCE_ACTOR_ADMISSION_V1_H
#define WL_RESOURCE_ACTOR_ADMISSION_V1_H
#include "resource_scoped_run_ledger_v1.h"
/* Native credential conjunct, never standalone launch permission. */
typedef struct {
    wl_run_binding bound;
    wl_run_id raw_frame;
    wl_run_id raw_sender;
    wl_run_id ticket;
    wl_run_id raw_proc_status;
    wl_run_id raw_proc_cgroup;
    wl_run_id raw_proc_maps;
    wl_run_id raw_proc_cmdline;
    wl_run_id raw_pidfd_info;
    wl_run_id namespace;
    wl_run_id held_namespace;
    wl_run_id helper_image;
    wl_run_id expected_helper_image;
    wl_run_id executable_plan;
    wl_run_id expected_executable_plan;
    wl_run_id original_requester;
    wl_run_id requester_credentials;
    wl_run_id expected_requester_credentials;
    wl_run_id dispatch;
    wl_run_id running_event;
    wl_run_id expected_running_event;
    wl_run_id canonical_use_event;
    wl_run_id expected_canonical_use_event;
    wl_run_id store_genesis;
    wl_run_id expected_store_genesis;
    wl_run_id source_lease;
    wl_run_id expected_source_lease;
    wl_run_id actor_wait;
    wl_run_id helper_wait;
    wl_run_id namespace_wait;
    wl_run_quantity host_pid;
    wl_run_quantity namespace_pid;
    wl_run_quantity sender_uid;
    wl_run_quantity sender_gid;
    wl_run_quantity real_uid;
    wl_run_quantity effective_uid;
    wl_run_quantity saved_uid;
    wl_run_quantity real_gid;
    wl_run_quantity effective_gid;
    wl_run_quantity saved_gid;
    wl_run_quantity capability_version;
    wl_run_quantity effective_low;
    wl_run_quantity permitted_low;
    wl_run_quantity inheritable_low;
    wl_run_quantity effective_high;
    wl_run_quantity permitted_high;
    wl_run_quantity inheritable_high;
    wl_run_quantity securebits;
    wl_run_quantity no_new_privs;
    wl_run_quantity requester_uid;
    wl_run_quantity requester_gid;
    wl_run_quantity configured_requester_uid;
    wl_run_quantity workload_uid;
    wl_run_quantity workload_gid;
    wl_run_quantity proc_host_pid;
    wl_run_quantity proc_namespace_pid;
    wl_run_quantity proc_real_uid;
    wl_run_quantity proc_effective_uid;
    wl_run_quantity proc_saved_uid;
    wl_run_quantity proc_real_gid;
    wl_run_quantity proc_effective_gid;
    wl_run_quantity proc_saved_gid;
    wl_run_quantity proc_effective;
    wl_run_quantity proc_permitted;
    wl_run_quantity proc_inheritable;
    wl_run_quantity proc_bounding;
    wl_run_quantity proc_ambient;
    wl_run_quantity proc_no_new_privs;
    wl_run_quantity proc_fs_uid;
    wl_run_quantity proc_fs_gid;
} wl_actor_observation;
typedef struct { wl_run_quantity index, bounding, ambient; } wl_actor_capability;
typedef struct { wl_scoped_packet ledger; wl_actor_observation captured; } wl_actor_packet;
uint32_t wl_resource_actor_admission_version_v1(void);
long wl_resource_actor_admission_layout_v1(uint32_t kind, uint32_t field);
int wl_resource_actor_admission_check_v1(
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
    const void *capabilities, size_t capabilities_count,
    const void *groups, size_t groups_count,
    const void *proc_groups, size_t proc_groups_count,
    void *output, size_t output_length);
#endif
