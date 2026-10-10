#ifndef WORLDLINE_RESOURCE_CHILD_EXECUTION_V1_H
#define WORLDLINE_RESOURCE_CHILD_EXECUTION_V1_H
#include "resource_actor_admission_v1.h"
#include "worldline_operation_authority_v1.h"
/* Complete immutable payloads/ownership/layout/native proof remain required. */
typedef struct {
  wl_run_id raw_status;
  wl_run_id raw_stat;
  wl_run_id raw_cgroup;
  wl_run_id raw_maps;
  wl_run_id raw_cmdline;
  wl_run_id raw_pidfd_info;
  wl_run_id namespace;
  wl_run_id cgroup;
  wl_run_id actual_unit;
  wl_run_id invocation;
  wl_run_id source_lease;
  wl_run_id pidfd_wait;
  wl_run_quantity host_pid;
  wl_run_quantity start_tick;
  wl_run_quantity parent_pid;
  wl_run_quantity parent_start_tick;
  wl_run_quantity real_uid;
  wl_run_quantity effective_uid;
  wl_run_quantity saved_uid;
  wl_run_quantity real_gid;
  wl_run_quantity effective_gid;
  wl_run_quantity saved_gid;
} wl_child_process;
typedef struct {
  wl_run_binding bound;
  wl_child_process process;
  wl_run_quantity requester_uid, requester_gid;
  wl_run_id raw_manager;
  wl_run_id raw_channel;
  wl_run_id owner_endpoint;
  wl_run_id expected_owner_endpoint;
  wl_run_id source_lease;
  wl_run_id expected_source_lease;
  wl_run_id worker_image;
  wl_run_id expected_worker_image;
  wl_run_id handler_plan;
  wl_run_id expected_handler_plan;
  wl_run_id raw_request;
  wl_run_id requester;
  wl_run_id dispatch;
  wl_run_id running_event;
  wl_run_id expected_running_event;
  wl_run_id store_genesis;
  wl_run_id expected_store_genesis;
  wl_run_id current_source;
} wl_child_controller;
typedef struct {
  uint8_t action;
  wl_run_binding root, child;
  wl_run_id task_id;
  wl_run_id root_world;
  wl_run_id child_world;
  wl_run_id root_instance;
  wl_run_id child_instance;
  wl_run_id world_store;
  wl_run_id full_world_ancestry;
  wl_run_id original_workload;
  wl_run_id sandbox;
  wl_run_id adapter;
  wl_run_id context;
  wl_run_id mission;
  wl_run_id stdin;
  wl_run_id credential_source;
  wl_run_id executable_source;
  wl_run_id configuration;
  wl_run_id owner_plan;
  wl_run_id native_cost_input;
  wl_run_id raw_request;
  wl_run_id requester;
  wl_run_id cause;
  wl_run_id root_dispatch;
  wl_run_id root_running_event;
  wl_run_id task_journal;
  wl_run_id task_intent;
  wl_run_id task_reservation_event;
  wl_run_id task_launch_event;
  wl_run_id parent_namespace_source;
  wl_run_id fd_lineage;
  wl_run_id source_lease;
} wl_child_task;
typedef struct {
  wl_run_id identity;
  wl_run_id parent;
  wl_run_id raw_nsfs;
  wl_run_id raw_get_parent;
  wl_run_id source_lease;
} wl_child_namespace;
typedef struct { uint8_t mode; wl_child_controller controller; wl_child_task task; } wl_child_input;
enum wl_child_mode { WL_CHILD_ROOT_CONTROLLER_ADMISSION, WL_CHILD_CHILD_ADMISSION, WL_CHILD_TASK_RESERVATION_ADMISSION };
enum wl_child_record_kind { WL_CHILD_D_RAW_OBSERVATION, WL_CHILD_D_RAW_CAPABILITY, WL_CHILD_D_RAW_PACKET, WL_CHILD_X_RAW_CROSSWALK, WL_CHILD_W_RAW_ID, WL_CHILD_W_RAW_QUANTITY, WL_CHILD_W_RAW_EPOCH, WL_CHILD_W_RAW_CONTEXT, WL_CHILD_W_RAW_BINDING, WL_CHILD_W_RAW_ROW, WL_CHILD_W_RAW_STATE, WL_CHILD_W_RAW_NATIVE, WL_CHILD_W_RAW_REQUEST, WL_CHILD_W_RAW_PACKET, WL_CHILD_W_RAW_RESULT, WL_CHILD_N_RAW_STATE, WL_CHILD_N_RAW_SCOPE_FRAME, WL_CHILD_N_RAW_PHYSICAL_KEY, WL_CHILD_N_RAW_BUCKET, WL_CHILD_N_RAW_PROJECTION, WL_CHILD_N_RAW_CURRENT_OBSERVATION, WL_CHILD_N_RAW_INTENT, WL_CHILD_N_RAW_PACKET, WL_CHILD_O_RAW_FACTS, WL_CHILD_O_RAW_INPUT, WL_CHILD_T_RAW_QUANTITY, WL_CHILD_T_RAW_UID, WL_CHILD_T_RAW_BINDING, WL_CHILD_T_RAW_GRANT, WL_CHILD_T_RAW_USE, WL_CHILD_T_RAW_EVIDENCE, WL_CHILD_T_RAW_INPUT, WL_CHILD_T_RAW_RESULT, WL_CHILD_TC_RAW_DIGEST, WL_CHILD_TC_RAW_ROW, WL_CHILD_TC_RAW_ANCHORS, WL_CHILD_TC_RAW_RESULT, WL_CHILD_Y_RAW_PROCESS, WL_CHILD_Y_RAW_CONTROLLER, WL_CHILD_Y_RAW_TASK, WL_CHILD_Y_RAW_NAMESPACE, WL_CHILD_Y_RAW_INPUT };
uint32_t wl_resource_child_execution_version_v1(void);
long wl_resource_child_execution_layout_v1(uint32_t kind, uint32_t field);
int wl_resource_child_execution_decide_v1(
  const void *input,
  size_t input_length,
  const void *arena,
  size_t arena_length,
  const void *history,
  size_t history_count,
  const void *proposed_history,
  size_t proposed_history_count,
  const void *rows,
  size_t rows_count,
  const void *proposed_rows,
  size_t proposed_rows_count,
  const void *projection,
  size_t projection_count,
  const void *proposed_projection,
  size_t proposed_projection_count,
  const void *buckets,
  size_t buckets_count,
  const void *proposed_buckets,
  size_t proposed_buckets_count,
  const void *actual_buckets,
  size_t actual_buckets_count,
  const void *observed,
  size_t observed_count,
  const void *facts,
  size_t facts_count,
  const void *capabilities,
  size_t capabilities_count,
  const void *groups,
  size_t groups_count,
  const void *proc_groups,
  size_t proc_groups_count,
  const void *authority_input,
  size_t authority_input_length,
  const void *authority_arena,
  size_t authority_arena_length,
  const void *authority_grants,
  size_t authority_grants_count,
  const void *authority_uses,
  size_t authority_uses_count,
  const void *authority_receipts,
  size_t authority_receipts_count,
  const void *authority_events,
  size_t authority_events_count,
  const void *crosswalk,
  size_t crosswalk_length,
  const void *child_input,
  size_t child_input_length,
  const void *tasks,
  size_t tasks_count,
  const void *processes,
  size_t processes_count,
  const void *namespaces,
  size_t namespaces_count,
  void *output,
  size_t output_length);
#endif
