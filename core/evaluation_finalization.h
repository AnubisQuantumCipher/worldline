#ifndef WORLDLINE_EVALUATION_FINALIZATION_V1_H
#define WORLDLINE_EVALUATION_FINALIZATION_V1_H
#include "evaluation_completion.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Additive epoch-zero Start/Input/Seal. No field claims a provisional content
 * identity. Full readable immutable extents and distinct writable output must
 * remain live through return. Numeric address checks do not prove lifetime.
 * Layout queries, including every field offset, must match before calls. */
typedef struct {
    wl_completion_span_v1 store_id, subject, run, sequence;
    wl_completion_optional_span_v1 requirement;
    wl_completion_span_v1 policy, verifier_plan, base_context;
    uint8_t parent[WL_HASH_BYTES], config[WL_HASH_BYTES], repository[WL_HASH_BYTES];
    wl_completion_span_v1 required;
    uint32_t declaration;
} wl_finalization_start_v1;
typedef struct {
    wl_finalization_start_v1 start;
    wl_completion_span_v1 root, manifests;
    uint8_t filesystem[WL_HASH_BYTES], config[WL_HASH_BYTES], repository[WL_HASH_BYTES];
} wl_finalization_input_v1;
typedef struct {
    wl_finalization_start_v1 start;
    wl_completion_span_v1 check_id, source_id;
    wl_completion_optional_span_v1 execution, verifier;
    uint32_t state, outcome;
    wl_completion_span_v1 payload, declared;
    struct wl_raw_evaluation_v1 raw;
    uint8_t confinement;
} wl_finalization_row_v1;
typedef struct {
    uint32_t version, operation;
    const void *data;
    int64_t data_length;
    wl_finalization_start_v1 start;
    wl_finalization_input_v1 inputs;
    wl_completion_span_v1 post_root, post_manifests;
    const void *rows;
    int64_t row_count;
    const void *required;
    int64_t required_count;
    wl_completion_required_row_v1 completion;
    wl_completion_span_v1 content;
    uint8_t environment_root[WL_HASH_BYTES], evidence_root[WL_HASH_BYTES];
    wl_completion_span_v1 context, source_id, evidence, environment;
} wl_finalization_request_v1;
typedef struct {
    uint32_t reason, state, outcome, promotion;
    uint32_t finalization_state, finalization_outcome;
    uint8_t identity[WL_HASH_BYTES];
} wl_finalization_result_v1;
/* Operations 0 Start, 1 Input, 2 pre-ID capture, 3 final Seal. Relation reason
 * 0 is observed, 1 invalid, 2 content mismatch. Transport failure returns 255
 * without writing any result; reason 0 is not an authenticity assertion. */
uint32_t wl_finalization_version_v1(void);
/* kind 1 Start, 2 Input, 3 Row, 4 Request, 5 Result; field 0 size, 1 alignment,
 * remaining fields in declaration order from 2. Unknown query: INT64_MAX. */
int64_t wl_finalization_layout_v1(uint32_t kind, uint32_t field);
int wl_finalization_decide_v1(const wl_finalization_request_v1 *, wl_finalization_result_v1 *);
/* Source kinds: 0 absent, 1 unchanged ordinary raw request, 2 finalization
 * request operation 3. Ordinary raw/confinement pointers retain their original
 * meaning; they are ignored for finalization. Context is the original full
 * metadata descriptor. A finalization Seal is revalidated inside this call.
 * Unneeded checkpoint inputs remain ignored; no supplied promotion flag. */
uint8_t wl_collapse_decide_finalization_v1(const void *collapse,
    uint32_t primary_kind, const void *primary, const void *primary_raw,
    const void *primary_confinement, const void *primary_context,
    uint32_t staged_kind, const void *staged, const void *staged_raw,
    const void *staged_confinement, const void *staged_context,
    const void *agent, uint8_t agent_confinement);
#ifdef __cplusplus
}
#endif
#endif
