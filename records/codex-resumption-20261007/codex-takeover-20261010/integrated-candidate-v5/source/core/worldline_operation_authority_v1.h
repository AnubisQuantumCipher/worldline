/* Distinct full operation ABI; source-only, measured layout/proof unrun.
 * Arena quantities retain the original arbitrary magnitude/typed absence.
 * These DTOs confer no protected custody or authority. */
#ifndef WORLDLINE_OPERATION_AUTHORITY_V1_H
#define WORLDLINE_OPERATION_AUTHORITY_V1_H
#include <stddef.h>
#include <stdint.h>
#include "worldline_chain_authority_v1.h"
#include "worldline_recovery_authorization_v3.h"
enum wl_operation_ops {
 WL_OPERATION_OPS_PING,
 WL_OPERATION_OPS_STATUS,
 WL_OPERATION_OPS_LIST,
 WL_OPERATION_OPS_SHOW,
 WL_OPERATION_OPS_LOG_VERIFY,
 WL_OPERATION_OPS_INIT,
 WL_OPERATION_OPS_ROOT_ADD,
 WL_OPERATION_OPS_ROOT_REMOVE,
 WL_OPERATION_OPS_ROOT_LIST,
 WL_OPERATION_OPS_FORK,
 WL_OPERATION_OPS_RACE,
 WL_OPERATION_OPS_GRAPH,
 WL_OPERATION_OPS_LOG,
 WL_OPERATION_OPS_WHY,
 WL_OPERATION_OPS_INSPECT,
 WL_OPERATION_OPS_SWITCH,
 WL_OPERATION_OPS_COLLAPSE_PREPARE,
 WL_OPERATION_OPS_COLLAPSE_COMMIT,
 WL_OPERATION_OPS_TRANSACTION_COMMIT,
 WL_OPERATION_OPS_TRANSACTION_ABORT,
 WL_OPERATION_OPS_TRANSACTION_LIST,
 WL_OPERATION_OPS_TRANSACTION_SHOW,
 WL_OPERATION_OPS_RETURN_PREPARE,
 WL_OPERATION_OPS_JOB_CANCEL,
 WL_OPERATION_OPS_SIMULATE,
 WL_OPERATION_OPS_DOCTOR,
 WL_OPERATION_OPS_ADAPTERS,
 WL_OPERATION_OPS_GHOST_ENABLE,
 WL_OPERATION_OPS_GHOST_DISABLE,
 WL_OPERATION_OPS_GHOST_STATUS,
 WL_OPERATION_OPS_GHOST_RUN,
 WL_OPERATION_OPS_SHELL_INFO,
 WL_OPERATION_OPS_PRUNE,
 WL_OPERATION_OPS_ANCHOR_STATUS,
 WL_OPERATION_OPS_REVALIDATE,
 WL_OPERATION_OPS_VALIDATION_STATUS,
 WL_OPERATION_OPS_RETURN_SERVICES,
 WL_OPERATION_OPS_RETURN_TERMINALS,
 WL_OPERATION_OPS_RETURN_WINDOWS,
 WL_OPERATION_OPS_AUTOMATIC_GHOSTS,
 WL_OPERATION_OPS_QUARANTINE_RESOLVE,
 WL_OPERATION_OPS_COUNT
};
enum wl_operation_fields {
 WL_OPERATION_FIELDS_OPERATION_ID,
 WL_OPERATION_FIELDS_REQUEST_ID,
 WL_OPERATION_FIELDS_TRANSACTION,
 WL_OPERATION_FIELDS_UNIVERSE_HEAD,
 WL_OPERATION_FIELDS_INSTANCE,
 WL_OPERATION_FIELDS_ROOT_SET,
 WL_OPERATION_FIELDS_PRIME,
 WL_OPERATION_FIELDS_POLICY,
 WL_OPERATION_FIELDS_REQUIREMENT,
 WL_OPERATION_FIELDS_ISSUER,
 WL_OPERATION_FIELDS_ISSUER_HEAD,
 WL_OPERATION_FIELDS_GRANT_ID,
 WL_OPERATION_FIELDS_USE_ID,
 WL_OPERATION_FIELDS_RESERVATION,
 WL_OPERATION_FIELDS_RESOURCE_HEAD,
 WL_OPERATION_FIELDS_RECEIPT_GENESIS,
 WL_OPERATION_FIELDS_RECEIPT_HEAD,
 WL_OPERATION_FIELDS_CAUSAL_GENESIS,
 WL_OPERATION_FIELDS_CAUSAL_HEAD,
 WL_OPERATION_FIELDS_INPUT_SNAPSHOT,
 WL_OPERATION_FIELDS_KERNEL_BUILD,
 WL_OPERATION_FIELDS_KERNEL_LIBRARY,
 WL_OPERATION_FIELDS_KERNEL_MAPPING,
 WL_OPERATION_FIELDS_PROVENANCE,
 WL_OPERATION_FIELDS_TARGET,
 WL_OPERATION_FIELDS_QUARANTINE_HEAD,
 WL_OPERATION_FIELDS_ORIGINAL_OPERATION,
 WL_OPERATION_FIELDS_COUNT
};
enum wl_operation_states {
 WL_OPERATION_STATES_RESERVED,
 WL_OPERATION_STATES_EFFECT_OBSERVED,
 WL_OPERATION_STATES_SETTLED,
 WL_OPERATION_STATES_RELEASED,
 WL_OPERATION_STATES_QUARANTINED,
 WL_OPERATION_STATES_COUNT
};
enum wl_operation_commands {
 WL_OPERATION_COMMANDS_RESERVE_USE,
 WL_OPERATION_COMMANDS_OBSERVE_EFFECT,
 WL_OPERATION_COMMANDS_SETTLE_USE,
 WL_OPERATION_COMMANDS_RELEASE_USE,
 WL_OPERATION_COMMANDS_RESOLVE_NO_EFFECT,
 WL_OPERATION_COMMANDS_RESOLVE_EFFECT,
 WL_OPERATION_COMMANDS_REPLAY_USE,
 WL_OPERATION_COMMANDS_QUARANTINE_USE,
 WL_OPERATION_COMMANDS_RESOLVE_RECOVERY,
 WL_OPERATION_COMMANDS_CHECK_GRANTS,
 WL_OPERATION_COMMANDS_AUTHORIZE_FOLLOWUP,
 WL_OPERATION_COMMANDS_AUTHORIZE_EXECUTION,
 WL_OPERATION_COMMANDS_COUNT
};
enum wl_operation_decisions {
 WL_OPERATION_DECISIONS_REFUSED,
 WL_OPERATION_DECISIONS_RESERVED_NEW,
 WL_OPERATION_DECISIONS_RESERVED_REPLAY,
 WL_OPERATION_DECISIONS_EFFECT_ACCEPTED,
 WL_OPERATION_DECISIONS_SETTLED_NEW,
 WL_OPERATION_DECISIONS_SETTLED_REPLAY,
 WL_OPERATION_DECISIONS_RELEASED_NEW,
 WL_OPERATION_DECISIONS_RELEASED_REPLAY,
 WL_OPERATION_DECISIONS_RESOLVED_NO_EFFECT,
 WL_OPERATION_DECISIONS_RESOLVED_EFFECT,
 WL_OPERATION_DECISIONS_QUARANTINED_NEW,
 WL_OPERATION_DECISIONS_OWNER_ABORT,
 WL_OPERATION_DECISIONS_OWNER_SETTLE,
 WL_OPERATION_DECISIONS_GRANTS_VALID,
 WL_OPERATION_DECISIONS_FOLLOWUP_READY,
 WL_OPERATION_DECISIONS_EXECUTION_READY,
 WL_OPERATION_DECISIONS_COUNT
};
typedef struct { uint8_t present, negative; int64_t first, length; } wl_operation_quantity_v1;
typedef struct { uint8_t present; uint32_t value; } wl_operation_uid_v1;
typedef struct {
 uint8_t action; wl_chain_digest_v1 id[WL_OPERATION_FIELDS_COUNT];
 wl_operation_uid_v1 peer,preparer,owner,target_owner;
 wl_operation_quantity_v1 policy_epoch,resource_epoch;
} wl_operation_binding_v1;
typedef struct {
 wl_chain_digest_v1 id,parent,issuer,instance,root_set,policy;
 wl_operation_uid_v1 subject,owner;
 uint8_t allowed[WL_OPERATION_OPS_COUNT],state;
 wl_operation_quantity_v1 epoch,ceiling,issued_at,expires_at;
} wl_operation_grant_v1;
typedef struct { wl_operation_binding_v1 bound; uint8_t state; } wl_operation_use_v1;
typedef struct {
 wl_operation_binding_v1 effect_binding;
 wl_chain_digest_v1 actual_receipt_root,actual_causal_root;
 wl_operation_binding_v1 no_effect_binding,owner_resolution;
 wl_chain_digest_v1 quarantine_head,witnessed_receipt_head,witnessed_causal_head;
 wl_recovery_request_v3 recovery;
 wl_chain_digest_v1 original_use;
 int64_t effect_material_first,effect_material_length;
} wl_operation_evidence_v1;
typedef struct {
 uint32_t schema;uint8_t mode;wl_operation_binding_v1 bound;
 wl_operation_quantity_v1 now;wl_operation_evidence_v1 facts;
} wl_operation_input_v1;
typedef struct { uint8_t disposition; } wl_operation_result_v1;
uint32_t wl_operation_authority_version_v1(void);
long wl_operation_authority_layout_v1(uint32_t kind,uint32_t field);
int wl_operation_authority_decide_v1(const void *input,size_t input_length,
 const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *receipts,size_t receipt_count,size_t receipt_length,
 const void *events,size_t event_count,size_t event_length,
 void *output,size_t output_length);
#endif
