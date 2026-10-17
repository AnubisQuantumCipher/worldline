#ifndef WORLDLINE_OWNER_AUDIT_V1_H
#define WORLDLINE_OWNER_AUDIT_V1_H
#include <stdint.h>
#include <stddef.h>
/* C convention, native alignment: never pack these structures. Layout kind
 * selectors follow schema order; field 0=size, 1=alignment, following selectors
 * are each field offset. Actual native layout MUST match before dereference.
 * Arena spans are one based; present is independent from length/zero.
 * Epochs are complete unsigned LE magnitude spans with no numeric word cap.
 * Matching bytes and a READY value are not protected authenticity.
 */
typedef struct {
    uint8_t present;
    size_t first;
    size_t length;
} wl_owner_identity_v1;
typedef struct {
    uint8_t present;
    wl_owner_identity_v1 sequence;
    wl_owner_identity_v1 run;
} wl_owner_cursor_v1;
typedef struct {
    wl_owner_identity_v1 subject;
    wl_owner_identity_v1 content;
    wl_owner_identity_v1 requirement;
    wl_owner_identity_v1 run;
    wl_owner_identity_v1 sequence;
    uint8_t state;
    uint8_t outcome;
} wl_owner_row_v1;
typedef struct {
    uint8_t action;
    uint8_t state;
    wl_owner_identity_v1 grant;
    wl_owner_identity_v1 use_id;
    wl_owner_identity_v1 issuer;
    wl_owner_identity_v1 principal;
    wl_owner_identity_v1 subject;
    wl_owner_identity_v1 content;
    wl_owner_identity_v1 transaction;
    wl_owner_identity_v1 current_requirement;
    wl_owner_identity_v1 expected_requirement;
    wl_owner_identity_v1 reason;
    wl_owner_identity_v1 issued_grant;
    wl_owner_identity_v1 reserved_grant;
    wl_owner_identity_v1 reserved_use;
    wl_owner_cursor_v1 failed_run;
    wl_owner_cursor_v1 prior_head;
    wl_owner_cursor_v1 next_run;
    wl_owner_identity_v1 epoch;
} wl_owner_grant_v1;
typedef struct {
    uint8_t action;
    wl_owner_identity_v1 peer;
    wl_owner_identity_v1 owner;
    wl_owner_identity_v1 trusted_issuer;
    wl_owner_identity_v1 subject;
    wl_owner_identity_v1 content;
    wl_owner_identity_v1 transaction;
    wl_owner_identity_v1 current_requirement;
    wl_owner_identity_v1 resulting_requirement;
    wl_owner_cursor_v1 current_head;
    wl_owner_cursor_v1 attempt;
    wl_owner_identity_v1 current_epoch;
    wl_owner_grant_v1 grant;
} wl_owner_request_v1;
typedef struct {
    wl_owner_request_v1 before_request;
    wl_owner_grant_v1 consumed;
    wl_owner_identity_v1 issued_event;
    wl_owner_identity_v1 reserved_event;
    wl_owner_identity_v1 consumed_event;
    wl_owner_identity_v1 consumed_issue;
    wl_owner_identity_v1 consumed_reservation;
    wl_owner_cursor_v1 current_head;
    wl_owner_cursor_v1 prepared_evidence;
    wl_owner_identity_v1 current_epoch;
} wl_owner_audit_v1;
typedef struct {
    wl_owner_identity_v1 subject;
    wl_owner_identity_v1 content;
    wl_owner_identity_v1 transaction;
} wl_owner_scope_v1;
/* Original ABI 6 collapse records keep their complete historical layout. */
typedef struct { uint8_t present; uint8_t value[32]; } wl_owner_hash_v1;
typedef struct { uint8_t present; uint8_t value_le[8]; } wl_owner_counter_v1;
typedef struct {
    uint8_t candidate_state,phase,evaluation_mode,conflicts,foreign_writes;
    uint8_t roster_complete,staged_roster_complete;
    wl_owner_hash_v1 expected_parent;
    wl_owner_hash_v1 candidate_parent;
    wl_owner_hash_v1 expected_subject;
    wl_owner_hash_v1 evidence_subject;
    wl_owner_hash_v1 expected_base;
    wl_owner_hash_v1 candidate_base;
    wl_owner_hash_v1 expected_delta;
    wl_owner_hash_v1 candidate_delta;
    wl_owner_hash_v1 expected_root_set;
    wl_owner_hash_v1 candidate_root_set;
    wl_owner_hash_v1 expected_staged_root;
    wl_owner_hash_v1 actual_staged_root;
    wl_owner_hash_v1 staged_content_root;
    wl_owner_hash_v1 tested_root;
    wl_owner_hash_v1 current_requirement;
    wl_owner_hash_v1 resulting_requirement;
    wl_owner_hash_v1 evaluated_requirement;
    wl_owner_hash_v1 declared_verifiers;
    wl_owner_hash_v1 executed_verifiers;
    wl_owner_hash_v1 staged_evaluated_requirement;
    wl_owner_hash_v1 staged_executed_verifiers;
    wl_owner_hash_v1 staged_examined_root;
    wl_owner_hash_v1 expected_checkpoint;
    wl_owner_hash_v1 witnessed_checkpoint;
    wl_owner_hash_v1 registered_watch_set;
    wl_owner_hash_v1 watched_set;
    wl_owner_counter_v1 generation_before,generation_after;
} wl_owner_original_collapse_v1;
/* Modes audit=0, retry-collapse=1, checkpoint=2, Adopt-consumed-receipt=3.
 * status 0 is transport success, typed decision is separate; all consulted
 * inputs are copied before output aliases. Extent checks do not prove readable
 * native mappings, no allocation, termination, provenance or host pressure.
 */
uint32_t wl_owner_audit_version_v1(void);
size_t wl_owner_audit_layout_v1(uint8_t kind,uint8_t field);
int wl_owner_audit_decide_v1(uint8_t mode,const void *data,size_t data_length,
 const wl_owner_row_v1 *before,size_t before_count,const wl_owner_row_v1 *after,size_t after_count,
 uint8_t before_present,const wl_owner_row_v1 *before_final,uint8_t after_present,const wl_owner_row_v1 *after_final,
 const wl_owner_audit_v1 *audit,const wl_owner_original_collapse_v1 *original,const wl_owner_scope_v1 *scope,
 const wl_owner_hash_v1 *resulting,uint8_t adopt_present,const wl_owner_request_v1 *adopt,uint8_t *output);
#endif
