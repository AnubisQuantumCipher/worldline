#ifndef WORLDLINE_EVALUATION_COMPLETION_V1_H
#define WORLDLINE_EVALUATION_COMPLETION_V1_H
#include <stdint.h>
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
#endif
