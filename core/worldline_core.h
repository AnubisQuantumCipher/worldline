#ifndef WORLDLINE_CORE_H
#define WORLDLINE_CORE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define WL_HASH_BYTES 32u

#define WL_OK 0
#define WL_ERR_INVALID_ARGUMENT 1
#define WL_ERR_IO 2
#define WL_ERR_TOO_LARGE 3
#define WL_ERR_INTERNAL 4

#define WL_STATE_MUTABLE 0u
#define WL_STATE_FINALIZING 1u
#define WL_STATE_VALID 2u
#define WL_STATE_DEGRADED 3u
#define WL_STATE_DEAD 4u
#define WL_STATE_ARCHIVED 5u
#define WL_STATE_COLLAPSED 6u

#define WL_COLLAPSE_AUTHORIZED 0u
#define WL_COLLAPSE_INVALID_CANDIDATE 1u
#define WL_COLLAPSE_PARENT_MISMATCH 2u
#define WL_COLLAPSE_OWNER_MISMATCH 3u /* retired in 1.9.0: never returned */
#define WL_COLLAPSE_BASE_MISMATCH 4u
#define WL_COLLAPSE_DELTA_MISMATCH 5u
#define WL_COLLAPSE_ROOT_SET_MISMATCH 6u
#define WL_COLLAPSE_STAGED_ROOT_MISMATCH 7u
#define WL_COLLAPSE_CONFLICT 8u
#define WL_COLLAPSE_FOREIGN_MANAGED_WRITE 9u
#define WL_COLLAPSE_VALIDATION_CONTEXT_MISMATCH 10u
#define WL_COLLAPSE_STAGED_UNTESTED 11u
#define WL_COLLAPSE_EXECUTION_EVIDENCE_INCOMPLETE 12u
#define WL_COLLAPSE_VERIFIER_EXECUTION_IDENTITY_MISMATCH 13u
#define WL_COLLAPSE_CHECKPOINT_UNWITNESSED 14u
#define WL_COLLAPSE_IDENTITY_ABSENT 15u
#define WL_COLLAPSE_MEASUREMENT_ABSENT 16u
#define WL_COLLAPSE_PRIME_CHANGED 17u
#define WL_COLLAPSE_WATCH_INCOMPLETE 18u
#define WL_COLLAPSE_CHECKPOINT_MISMATCH 19u
#define WL_COLLAPSE_EVIDENCE_SUBJECT_MISMATCH 20u
#define WL_COLLAPSE_INVALID_REQUEST 255u

/* ABI generation of the library (wl_abi_version). It changes whenever a record layout or the
 * meaning of an exported code changes; the runtime refuses a library that reports another. */
#define WL_ABI_VERSION 5u

/* Separately versioned recovery selector. Caller-owned readable buffers must
 * remain live/unchanged for the complete call. Presence is exactly 0 or 1;
 * absent buffers are ignored, and present empty identities remain present.
 * The selector does not authenticate marker custody or perform a mutation. */
#define WL_RECOVERY_ABI_VERSION 1u
#define WL_RECOVERY_FINISH_COMMITTED 0u
#define WL_RECOVERY_ABORT_PREPARED 1u
#define WL_RECOVERY_AMBIGUOUS 2u
#define WL_RECOVERY_INVALID_REQUEST 255u
uint32_t wl_recovery_abi_version(void);
uint8_t wl_recovery_select(
    const uint8_t *expected, size_t expected_length,
    uint8_t live_present, const uint8_t *live, size_t live_length,
    uint8_t prepared_present, const uint8_t *prepared, size_t prepared_length);

/* Layout version of struct wl_collapse_request. The runtime and the library ship together;
 * a runtime built for a different layout must not call wl_collapse_decide. */
#define WL_COLLAPSE_REQUEST_VERSION 5u

#define WL_PHASE_COMMIT 0u
#define WL_PHASE_PREPARE 1u

/* Which evidence speaks for the bytes that would become live. */
#define WL_MODE_CANDIDATE_EVALUATION 0u
#define WL_MODE_CHECKPOINT_RETURN 1u

#define WL_MEASUREMENT_UNMEASURED 0u
#define WL_MEASUREMENT_NONE_FOUND 1u
#define WL_MEASUREMENT_FOUND 2u

/* An identity the runtime could not establish is absent: present = 0 and every value byte 0.
 * A present value is never all zero, so no zero digest can pass for a real identity. */
struct wl_optional_hash {
    uint8_t present;
    uint8_t value[WL_HASH_BYTES];
};

/* A little-endian 64-bit counter with the same presence rule (a present counter may be 0). */
struct wl_optional_counter {
    uint8_t present;
    uint8_t value_le[8];
};

/* Layout 5 (1.9.0). All bytes; no padding and no reserved bytes. A request that is not
 * well formed -- a Boolean or enum out of range, a present byte other than 0 or 1, an absent
 * value with a nonzero byte, a present all-zero hash, or a slot the mode or phase does not
 * consult that is not empty -- is WL_COLLAPSE_INVALID_REQUEST. Prepare must leave
 * actual_staged_root absent; candidate mode must leave both checkpoint fields absent; checkpoint
 * mode must leave evaluated_requirement and executed_verifiers absent and roster_complete 0. */
struct wl_collapse_request {
    uint8_t candidate_state;
    uint8_t phase;
    uint8_t evaluation_mode;
    uint8_t conflicts;
    uint8_t foreign_writes;
    uint8_t roster_complete;
    uint8_t staged_roster_complete;
    struct wl_optional_hash expected_parent;
    struct wl_optional_hash candidate_parent;
    struct wl_optional_hash expected_subject;
    struct wl_optional_hash evidence_subject;
    struct wl_optional_hash expected_base;
    struct wl_optional_hash candidate_base;
    struct wl_optional_hash expected_delta;
    struct wl_optional_hash candidate_delta;
    struct wl_optional_hash expected_root_set;
    struct wl_optional_hash candidate_root_set;
    struct wl_optional_hash expected_staged_root;
    struct wl_optional_hash actual_staged_root;
    struct wl_optional_hash staged_content_root;
    struct wl_optional_hash tested_root;
    struct wl_optional_hash current_requirement;
    struct wl_optional_hash evaluated_requirement;
    struct wl_optional_hash declared_verifiers;
    struct wl_optional_hash executed_verifiers;
    struct wl_optional_hash staged_evaluated_requirement;
    struct wl_optional_hash staged_executed_verifiers;
    struct wl_optional_hash staged_examined_root;
    struct wl_optional_hash expected_checkpoint;
    struct wl_optional_hash witnessed_checkpoint;
    struct wl_optional_hash registered_watch_set;
    struct wl_optional_hash watched_set;
    struct wl_optional_counter generation_before;
    struct wl_optional_counter generation_after;
};

/* The evaluation classifications below are the declaration order in
 * Worldline.Evaluation. A new attempt needs a new evaluation identity; a
 * terminal execution state cannot resume under the same identity. */
enum wl_execution_state {
    WL_EVAL_NOT_ATTEMPTED,
    WL_EVAL_PREPARED,
    WL_EVAL_STARTED,
    WL_EVAL_INTERRUPTED,
    WL_EVAL_ERROR_BEFORE_EXAMINER,
    WL_EVAL_INCOMPLETE_UNKNOWN,
    WL_EVAL_EVALUATOR_INCOMPLETE,
    WL_EVAL_UNCLASSIFIED,
    WL_EVAL_COMPLETED
};

enum wl_evaluation_outcome {
    WL_EVAL_NO_OUTCOME,
    WL_EVAL_PASS,
    WL_EVAL_FAIL
};

enum wl_bundle_integrity {
    WL_BUNDLE_NOT_COVERED,
    WL_BUNDLE_VERIFIED,
    WL_BUNDLE_COMPROMISED,
    WL_BUNDLE_UNKNOWN
};

enum wl_report_integrity {
    WL_REPORT_NOT_APPLICABLE,
    WL_REPORT_VERIFIED,
    WL_REPORT_UNTRUSTED
};

/* Observation input codes, in the declaration order of Worldline.Evaluation's
 * Origin, Raw_Status, Channel_State, Rejection_Stage and Supervision_State. */
enum wl_evaluation_origin { WL_ORIGIN_ENGINE, WL_ORIGIN_AGENT, WL_ORIGIN_EXTERNAL };
enum wl_evaluation_status {
    WL_STATUS_ABSENT, WL_STATUS_PASS, WL_STATUS_FAIL, WL_STATUS_UNASSESSED, WL_STATUS_OTHER
};
enum wl_evaluation_channel {
    WL_CHANNEL_ABSENT, WL_CHANNEL_EMPTY, WL_CHANNEL_ACCEPTED,
    WL_CHANNEL_REJECTED, WL_CHANNEL_OTHER, WL_CHANNEL_MALFORMED
};
enum wl_evaluation_stage {
    WL_STAGE_ABSENT, WL_STAGE_SANDBOX_NEVER_STARTED, WL_STAGE_STOPPED_BY_MANAGER,
    WL_STAGE_HARNESS_SIGNALLED, WL_STAGE_OTHER
};
enum wl_evaluation_supervision {
    WL_SUPERVISION_ABSENT, WL_SUPERVISION_SUPERVISED, WL_SUPERVISION_STOPPED, WL_SUPERVISION_OTHER
};

struct wl_evaluation_observations {
    uint8_t source;
    uint8_t status;
    uint8_t channel;
    uint8_t stage;
    uint8_t exit_present;
    uint8_t exit_integer;
    uint8_t supervisor;
    uint8_t supervisor_stopped;
    uint8_t bundle_present;
    uint8_t bundle_is_mapping;
    uint8_t bundle_stable;
    uint8_t bundle_changed;
    uint8_t unsatisfied_imports;
};

struct wl_evaluation_classification {
    uint8_t execution;
    uint8_t outcome;
    uint8_t bundle;
};

/* Typed per-check evidence presence. Each byte is 0 or 1. */
struct wl_evidence_presence {
    uint8_t record_identified;
    uint8_t verdict_recorded;
    uint8_t binding_established;
    uint8_t declaration_matches;
    uint8_t bundle_identified;
};

#define WL_LAYOUT_COLLAPSE_REQUEST 0u
#define WL_LAYOUT_EVALUATION_OBSERVATIONS 1u
#define WL_LAYOUT_EVALUATION_CLASSIFICATION 2u
#define WL_LAYOUT_EVIDENCE_PRESENCE 3u
#define WL_LAYOUT_OPTIONAL_HASH 4u
#define WL_LAYOUT_OPTIONAL_COUNTER 5u
#define WL_ROSTER_MAX 4096u

int wl_hash_file(const char *path, size_t path_len, uint8_t out[WL_HASH_BYTES]);
int wl_hash_bytes(const uint8_t *data, size_t data_len, uint8_t out[WL_HASH_BYTES]);
int wl_world_id(const uint8_t parent[WL_HASH_BYTES],
                const uint8_t filesystem[WL_HASH_BYTES],
                const uint8_t config[WL_HASH_BYTES],
                const uint8_t repository[WL_HASH_BYTES],
                const uint8_t environment[WL_HASH_BYTES],
                const uint8_t evidence[WL_HASH_BYTES],
                uint8_t out[WL_HASH_BYTES]);
int wl_causal_link(const uint8_t previous[WL_HASH_BYTES],
                   const uint8_t event_root[WL_HASH_BYTES],
                   uint8_t out[WL_HASH_BYTES]);
int wl_receipt_link(const uint8_t previous[WL_HASH_BYTES],
                    const uint8_t receipt_root[WL_HASH_BYTES],
                    uint8_t out[WL_HASH_BYTES]);
#define WL_TX_PREPARED 0u
#define WL_TX_AUTHORIZED 1u
#define WL_TX_DENIED 2u
#define WL_TX_COMMITTED 3u
#define WL_TX_ABORTED 4u

uint8_t wl_transition_allowed(uint8_t from_state, uint8_t to_state);
uint8_t wl_transaction_transition_allowed(uint8_t from_state, uint8_t to_state);
uint8_t wl_collapse_decide(const struct wl_collapse_request *request);
/* 0 on successful classification, 255 for an invalid raw encoding. */
uint8_t wl_evaluation_classify(const struct wl_evaluation_observations *facts,
                               struct wl_evaluation_classification *result);
/* 0 denied, 1 admitted, 255 invalid. Evidence presence is an explicit typed input; absent
 * evidence never defaults to complete. A classification Classify could not produce (an
 * outcome without completion, completion without an outcome, or an in-flight state) is
 * invalid. */
uint8_t wl_evaluation_admissible(const struct wl_evaluation_classification *value,
                                 uint8_t report,
                                 const struct wl_evidence_presence *presence);
/* Evaluation lifecycle: 0 refused, 1 allowed, 255 invalid code. */
uint8_t wl_evaluation_transition_allowed(uint8_t from_state, uint8_t to_state);
/* 0 success (state unchanged when the step is refused), 255 invalid input. */
uint8_t wl_evaluation_advance(uint8_t *state, uint8_t requested);
/* One 0/1 admission byte per required check. 0 incomplete, 1 complete, 255 invalid.
 * An empty roster is complete only when empty_declared is 1. */
uint8_t wl_evaluation_roster_complete(const uint8_t *admitted, size_t count,
                                      uint8_t empty_declared);
uint32_t wl_abi_version(void);
/* Resource arithmetic ABI is versioned independently of existing layouts.
 * Quantities are arbitrary-length little-endian magnitudes; empty means zero.
 * Buffers must be readable, live and unchanged throughout the call.
 * 0 insufficient capacity, 1 admitted arithmetic, 255 checked shape/error.
 * Raw pointer readability, custody and ledger projection require separate assurance. */
uint32_t wl_resources_abi_version(void);
uint8_t wl_resources_can_reserve(
    uint8_t available_negative,
    const uint8_t *available, size_t available_length,
    const uint8_t *withheld, size_t withheld_length,
    const uint8_t *floor, size_t floor_length,
    const uint8_t *requested, size_t requested_length);
/* Separate numeric policy ABI. Full magnitudes live in one private byte arena.
 * first is a ONE-based arena index; length zero is zero. negative/present are
 * exactly 0 or 1. An absent optional's quantity payload is ignored.
 * Every pointer must remain aligned, live, readable (result writable), and
 * unchanged for its complete extent throughout the call. Checked shape/extent
 * arithmetic does not establish memory provenance or OS readability. */
struct wl_policy_quantity { size_t first, length; uint8_t negative; };
struct wl_policy_optional { uint8_t present; struct wl_policy_quantity value; };
struct wl_policy_input {
    struct wl_policy_quantity outstanding_count;
    struct wl_policy_optional concurrency_limit, memory_pressure;
    struct wl_policy_quantity memory_pressure_ceiling, disk_byte_floor, disk_inode_floor;
    struct wl_policy_quantity available_memory, withheld_memory, memory_floor, requested_memory;
};
struct wl_policy_disk { struct wl_policy_quantity free_bytes, free_inodes; };
enum wl_policy_check { WL_POLICY_PASSED, WL_POLICY_INSUFFICIENT,
    WL_POLICY_INVALID_REPRESENTATION, WL_POLICY_NEGATIVE_DEBIT };
enum wl_policy_gate { WL_POLICY_NO_GATE, WL_POLICY_CONCURRENCY, WL_POLICY_PRESSURE,
    WL_POLICY_DISK_BYTES, WL_POLICY_DISK_INODES, WL_POLICY_CAPACITY };
enum wl_policy_field { WL_POLICY_NO_FIELD, WL_POLICY_OUTSTANDING_COUNT,
    WL_POLICY_CONCURRENCY_LIMIT, WL_POLICY_MEMORY_PRESSURE, WL_POLICY_MEMORY_PRESSURE_CEILING,
    WL_POLICY_FREE_BYTES, WL_POLICY_DISK_BYTE_FLOOR, WL_POLICY_FREE_INODES,
    WL_POLICY_DISK_INODE_FLOOR, WL_POLICY_AVAILABLE_MEMORY, WL_POLICY_WITHHELD_MEMORY,
    WL_POLICY_MEMORY_FLOOR, WL_POLICY_REQUESTED_MEMORY };
struct wl_policy_result {
    uint8_t status, failed_gate, field, disk_present;
    size_t disk_index; /* ONE-based original row index; zero when absent. */
};
uint32_t wl_resource_policy_abi_version(void);
/* Selectors: quantity, optional, input, disk, result (in that order, from 1).
 * Fields are each record's declaration order from 1. Unknown returns SIZE_MAX. */
size_t wl_resource_policy_layout_size(uint8_t selector);
size_t wl_resource_policy_layout_offset(uint8_t selector, uint8_t field);
/* Transport: 0 => complete result; 255 => shape/exception, result must be ignored.
 * Only canonical PASSED/NO_GATE/NO_FIELD/absent/zero means Ready. A transport
 * success is not itself admission. Other statuses are refusal or unknown. */
uint8_t wl_resource_policy_admit(const uint8_t *data, size_t data_length,
    const struct wl_policy_input *input, const struct wl_policy_disk *disks,
    size_t disk_count, struct wl_policy_result *result);
/* Ordered reservation arithmetic, ABI version 1. Quantities share the policy
 * signed-magnitude layout; no semantic quantity is narrowed to a machine word.
 * Rows, metadata and usage observations retain their caller order. Output slots
 * name disjoint writable spans in detail_data. detail_data, total_data, details
 * and result name mutually disjoint writable extents and cannot alias inputs.
 * Every pointer must remain aligned and live for the declared full extent.
 * Pointer custody/readability, storage sufficiency and producer truth remain
 * separate obligations; this transport does not establish them. */
struct wl_ledger_row {
    struct wl_policy_quantity reserved;
    struct wl_policy_optional used;
    size_t output_first, output_length;
};
enum wl_ledger_status { WL_LEDGER_COMPUTED, WL_LEDGER_INVALID_INPUT,
    WL_LEDGER_INVALID_OUTPUT_LAYOUT, WL_LEDGER_INSUFFICIENT_STORAGE };
struct wl_ledger_result { uint8_t status; struct wl_policy_quantity total; };
uint32_t wl_resource_ledger_abi_version(void);
/* Selectors: quantity, optional, row, result from 1; fields in declaration order.
 * Unknown selector/field returns SIZE_MAX; sizes include trailing padding. */
size_t wl_resource_ledger_layout_size(uint8_t selector);
size_t wl_resource_ledger_layout_offset(uint8_t selector, uint8_t field);
/* Transport 0 supplies a complete typed status, 255 requires ignoring outputs.
 * Only COMPUTED has usable numeric results. Every typed refusal empties all
 * output descriptors and zeroes arenas. details has row_count quantities. */
uint8_t wl_resource_ledger_compute(const uint8_t *data, size_t data_length,
    const struct wl_ledger_row *rows, size_t row_count,
    uint8_t *detail_data, size_t detail_length,
    uint8_t *total_data, size_t total_length,
    struct wl_policy_quantity *details, struct wl_ledger_result *result);
/* Full signed headroom: available - withheld - floor. The three descriptors
 * name live Quantity records over data. output/result are disjoint writable
 * extents, do not alias inputs, and obey the same custody/alignment premises.
 * The output extent must hold both the intermediate difference and final value.
 * Transport/status/canonical-zero rules are identical to ledger_compute. */
uint8_t wl_resource_ledger_headroom(const uint8_t *data, size_t data_length,
    const struct wl_policy_quantity *available,
    const struct wl_policy_quantity *withheld,
    const struct wl_policy_quantity *floor,
    uint8_t *output, size_t output_length, struct wl_ledger_result *result);
size_t wl_layout_size(uint8_t selector);
/* Offset of the field named `name` (as spelled in this header) of record `selector`; SIZE_MAX
 * for an unknown selector or name. Keyed by name: two equal-sized fields swapped keep every
 * size and every positional offset. */
size_t wl_layout_offset(uint8_t selector, const char *name, size_t name_len);

/* Additive reservation lifecycle ABI; complete owned extents stay live,
 * readable/unchanged (inputs) or writable (output), disjoint for this call.
 * The pointer custody premise is outside the SPARK plan proof.
 */
typedef struct {
    size_t first;
    size_t length;
    uint8_t observed;
} wl_reservation_lifecycle_row;
uint32_t wl_reservation_lifecycle_abi_version(void);
size_t wl_reservation_lifecycle_row_size(void);
size_t wl_reservation_lifecycle_row_offset(uint8_t field);
/* Return 0 invalid input, 1 invalid layout, 2 no change, 3 removal planned;
 * typed refusals do not write removed; 255 means ignore every output.
 * mode: 1 exact release, 2 reconciliation. observed: 0 unknown, 1 live, 2 gone.
 */
uint8_t wl_reservation_lifecycle_plan(
    const uint8_t *data, size_t data_length,
    const wl_reservation_lifecycle_row *rows, size_t row_count,
    uint8_t mode, uint8_t present, size_t requested_first, size_t requested_length,
    uint8_t *removed, size_t removed_length);

/* Owned full-byte evaluation history transport. Inputs are live/aligned/readable
 * immutable declared extents; output is live writable disjoint storage.
 * No pointer/custody proof or durable history producer is implied. */
typedef struct { uint8_t present; size_t first, length; } wl_evaluation_identity;
typedef struct { uint8_t present; size_t first, length; } wl_evaluation_epoch;
typedef struct { uint8_t present; wl_evaluation_epoch sequence;
                 wl_evaluation_identity run; } wl_evaluation_cursor;
typedef struct { wl_evaluation_identity subject, content, requirement, run;
                 wl_evaluation_epoch sequence; uint8_t state, outcome; } wl_evaluation_row;
typedef struct { wl_evaluation_identity subject, content, requirement;
                 wl_evaluation_cursor current_head, prepared_evidence; } wl_evaluation_query;
typedef struct { uint8_t reason, head_kind; size_t head_index;
                 uint8_t failure_kind; size_t failure_index; } wl_evaluation_selection;
uint32_t wl_evaluation_history_abi_version(void);
size_t wl_evaluation_history_layout_size(uint8_t kind);
size_t wl_evaluation_history_layout_offset(uint8_t kind, uint8_t field);
uint8_t wl_evaluation_history_select(const uint8_t *data, size_t data_length,
    const wl_evaluation_row *rows, size_t row_count, uint8_t final_present,
    const wl_evaluation_row *final_row, const wl_evaluation_query *query,
    wl_evaluation_selection *output);


/* Additive raw evaluation interface. Caller owns immutable readable request,
 * raw arrays/arenas and source records through return, with distinct writable
 * classifier output. Numeric checks do not prove mapping, custody or lifetime.
 * Raw completion requests use evaluation_completion.h, operation 2. Their
 * captured_count defines every raw/confinement array extent, without a 4096 cap.
 */
struct wl_raw_evaluation_v1 {
    uint8_t observations[14];
    uint8_t report_based;
    uint8_t report_facts[14];
    uint8_t presence[5];
};
struct wl_raw_classification_v1 { uint8_t status, execution, outcome, bundle; };
uint8_t wl_evaluation_wire_version(void);
size_t wl_evaluation_wire_layout(uint8_t kind, uint8_t field);
uint8_t wl_evaluation_wire_classify(const void *raw, void *classification);
uint8_t wl_evaluation_wire_admit(const void *raw, uint8_t confinement);
uint8_t wl_evaluation_wire_report(const void *raw);
/* Dependency tags: none=0, primary=1, staged=2, both=3, malformed=255.
 * A nonzero evidence dependency is not a permission or roster verdict. */
uint8_t wl_collapse_raw_dependencies_v1(const void *request);
uint8_t wl_collapse_decide_raw_evaluation_v1(const void *request,
    const void *primary, const void *primary_raw, const void *primary_confinement,
    const void *staged, const void *staged_raw, const void *staged_confinement,
    const void *agent_raw, uint8_t agent_confinement);
/* v2 adds full context joins; v1 without them cannot authorize a required raw
 * promotion. Checkpoint-only and nonpromotion refusal paths retain v1 behavior. */
uint8_t wl_collapse_decide_raw_evaluation_v2(const void *request,
    const void *primary, const void *primary_raw, const void *primary_confinement,
    const void *primary_context, const void *staged, const void *staged_raw,
    const void *staged_confinement, const void *staged_context,
    const void *agent_raw, uint8_t agent_confinement);
int64_t wl_completion_context_layout_v1(uint32_t kind, uint32_t field);
/* v3 additionally requires independent row metadata projections for every raw
 * row. Context arguments are wl_completion_metadata_context_v1 descriptors.
 * v1/v2 remain ABI-compatible but do not establish this stronger relation. */
uint8_t wl_collapse_decide_raw_evaluation_v3(const void *request,
    const void *primary, const void *primary_raw, const void *primary_confinement,
    const void *primary_context, const void *staged, const void *staged_raw,
    const void *staged_confinement, const void *staged_context,
    const void *agent, uint8_t agent_confinement);
#ifdef __cplusplus
}
#endif

#endif
