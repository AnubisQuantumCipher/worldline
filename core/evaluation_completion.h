#ifndef WORLDLINE_EVALUATION_COMPLETION_V1_H
#define WORLDLINE_EVALUATION_COMPLETION_V1_H
#include <stdint.h>
#include "worldline_core.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Caller owns readable immutable request/arrays/arena through return, and a
 * distinct writable result. Address checks do not prove mapped memory/custody. */
typedef struct {
  int64_t first;
  int64_t length;
} wl_completion_span_v1;
typedef struct {
  uint32_t present;
  wl_completion_span_v1 value;
} wl_completion_optional_span_v1;
typedef struct {
  uint32_t present;
  wl_completion_span_v1 sequence;
  wl_completion_span_v1 run;
} wl_completion_cursor_v1;
typedef struct {
  wl_completion_span_v1 store_id;
  wl_completion_span_v1 subject;
  wl_completion_span_v1 content;
  wl_completion_span_v1 run;
  wl_completion_span_v1 sequence;
  wl_completion_optional_span_v1 requirement;
} wl_completion_binding_v1;
typedef struct {
  wl_completion_binding_v1 bound;
  wl_completion_cursor_v1 previous;
  uint32_t linked;
} wl_completion_journal_row_v1;
typedef struct {
  wl_completion_binding_v1 bound;
  wl_completion_span_v1 source_id;
  wl_completion_span_v1 context;
  uint32_t state;
  uint32_t outcome;
} wl_completion_capture_v1;
typedef struct {
  uint32_t source;
  uint32_t status;
  uint32_t channel;
  uint32_t stage;
  uint32_t exit_present;
  uint32_t exit_integer;
  uint32_t supervisor;
  uint32_t supervisor_stopped;
  uint32_t bundle_present;
  uint32_t bundle_is_mapping;
  uint32_t bundle_stable;
  uint32_t bundle_changed;
  uint32_t unsatisfied_imports;
} wl_completion_facts_v1;
typedef struct {
  uint32_t record_identified;
  uint32_t verdict_recorded;
  uint32_t binding_established;
  uint32_t declaration_matches;
  uint32_t bundle_identified;
} wl_completion_presence_v1;
typedef struct {
  wl_completion_span_v1 check_id;
  wl_completion_span_v1 declared;
} wl_completion_required_row_v1;
typedef struct {
  wl_completion_binding_v1 bound;
  wl_completion_span_v1 check_id;
  wl_completion_span_v1 source_id;
  wl_completion_optional_span_v1 execution;
  wl_completion_optional_span_v1 verifier;
  uint32_t state;
  uint32_t outcome;
  wl_completion_span_v1 payload;
  wl_completion_facts_v1 observed;
  uint32_t report;
  wl_completion_presence_v1 evidence;
  wl_completion_span_v1 declared;
} wl_completion_check_row_v1;
typedef struct {
  wl_completion_optional_span_v1 subject;
  wl_completion_optional_span_v1 content;
  wl_completion_optional_span_v1 requirement;
  wl_completion_optional_span_v1 run;
  wl_completion_optional_span_v1 sequence;
  uint32_t state;
  uint32_t outcome;
} wl_completion_history_row_v1;
typedef struct {
  uint32_t version;
  uint32_t operation;
  const void * data;
  int64_t data_length;
  const void * journal;
  int64_t journal_count;
  wl_completion_cursor_v1 current;
  wl_completion_capture_v1 captured;
  const void * captured_results;
  int64_t captured_count;
  uint32_t retained_present;
  wl_completion_capture_v1 retained;
  const void * retained_results;
  int64_t retained_count;
  const void * history;
  int64_t history_count;
  const void * required;
  int64_t required_count;
  uint32_t policy;
  wl_completion_span_v1 before_root;
  wl_completion_span_v1 after_root;
  wl_completion_required_row_v1 completion;
  wl_completion_binding_v1 observed_binding;
} wl_completion_request_v1;
typedef struct {
  uint32_t reason;
  int64_t selected;
  uint32_t summary_present;
  wl_completion_history_row_v1 summary;
  uint32_t execution_state;
  uint32_t outcome;
  uint32_t promotion;
} wl_completion_result_v1;
uint32_t wl_completion_abi_version_v1(void);
int64_t wl_completion_layout_size_v1(uint32_t);
int64_t wl_completion_layout_alignment_v1(uint32_t);
int64_t wl_completion_layout_offset_v1(uint32_t, uint32_t);
int wl_completion_decide_v1(const wl_completion_request_v1 *, wl_completion_result_v1 *);
/* Same original owned request/result/layout, operation 2 only. The two arrays
 * contain exactly captured_count raw34 and confinement-byte entries. Output
 * must be disjoint from all inputs. Genuine failure is classified independently
 * of carried lifecycle/verdict; promotion also checks their correspondence. */
int wl_completion_raw_decide_v1(const void *request, const void *raw_rows,
                              const void *confinement, void *result);

/* Full raw default join, with a separate owned context arena.
 * item Check_Row spans still name the original raw request arena; context
 * expected/observed/required/binding/cursor spans name this descriptor arena.
 * Fields follow Context_Field/Row_Field declaration order, queried at runtime.
 * Absence has no payload meaning. Every pointer has the same full live,
 * readable, immutable extent premise as the original completion interface. */
enum wl_completion_row_field_v1 {
  WL_CTX_INVOCATION_START, WL_CTX_INVOCATION_RETURN, WL_CTX_RAW_ACQUISITIONS,
  WL_CTX_INVOCATION_BINDING, WL_CTX_CANDIDATE_SNAPSHOT, WL_CTX_INVOCATION_VERIFIERS,
  WL_CTX_VERIFIER_MEMBERS, WL_CTX_VERIFIER_IDENTITY, WL_CTX_ROW_FIELD_COUNT
};
enum wl_completion_context_field_v1 {
  WL_CTX_CAPTURE_HEADER, WL_CTX_RETURNED_CONTEXT, WL_CTX_FULL_POLICY,
  WL_CTX_CANDIDATE_RECORD, WL_CTX_ROOT_MANIFESTS, WL_CTX_EFFECTIVE_ROSTER,
  WL_CTX_DECLARED_VERIFIERS, WL_CTX_EXECUTED_VERIFIERS, WL_CTX_AGENT_RECORD,
  WL_CTX_SOURCE_ID, WL_CTX_EXAMINED_ROOT, WL_CTX_INVOCATION_STREAM,
  WL_CTX_ACQUISITION_STREAM, WL_CTX_RETURNED_ROWS, WL_CTX_FIELD_COUNT
};
typedef struct {
  wl_completion_check_row_v1 item;
  wl_completion_optional_span_v1 expected[WL_CTX_ROW_FIELD_COUNT], observed[WL_CTX_ROW_FIELD_COUNT];
} wl_completion_context_row_v1;
typedef struct {
  uint32_t version;
  const void *data;
  int64_t data_length;
  wl_completion_binding_v1 expected_binding;
  wl_completion_cursor_v1 expected_current;
  wl_completion_cursor_v1 prepared_current;
  wl_completion_optional_span_v1 expected[WL_CTX_FIELD_COUNT], observed[WL_CTX_FIELD_COUNT];
  const void *rows;
  int64_t row_count;
  const void *required;
  int64_t required_count;
  uint32_t policy;
  struct wl_collapse_request projection;
  struct wl_raw_evaluation_v1 agent;
  uint8_t agent_confinement;
} wl_completion_context_v1;
int64_t wl_completion_context_layout_v1(uint32_t kind, uint32_t field);
/* Additive independent row projection; all spans name data, not the raw arena.
 * base names the unchanged context_v1 descriptor. All descriptors/arrays/arenas
 * must remain readable, immutable and live for the complete call. Numeric
 * guards do not establish allocation custody. No output extent is written. */
typedef struct {
  wl_completion_span_v1 check_id, source_id, payload;
  wl_completion_optional_span_v1 execution, verifier;
} wl_completion_row_metadata_v1;
typedef struct {
  uint32_t version;
  const wl_completion_context_v1 *base;
  const void *data;
  int64_t data_length;
  const wl_completion_row_metadata_v1 *rows;
  int64_t row_count;
} wl_completion_metadata_context_v1;
int64_t wl_completion_metadata_layout_v1(uint32_t kind, uint32_t field);
/* 1 exact match, 0 mismatch, 255 malformed native representation. This is not
 * a promotion/authorization verdict and does not establish payload provenance. */
int wl_completion_metadata_matches_v1(const void *request, const void *metadata);
#ifdef __cplusplus
}
#endif
#endif
