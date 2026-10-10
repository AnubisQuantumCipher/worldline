/* Source-only recovery ABI v3. No protected authority is conferred by these DTOs.
 * All structs use the platform C ABI; qualification must measure sizes/offsets.
 * Epoch first/length denote storage extents, never numeric values. */
#ifndef WORLDLINE_RECOVERY_AUTHORIZATION_V3_H
#define WORLDLINE_RECOVERY_AUTHORIZATION_V3_H
#include <stddef.h>
#include <stdint.h>
typedef struct { uint8_t present; uint8_t value[32]; } wl_recovery_digest_v3;
typedef struct {
    uint8_t present, negative;
    int64_t first, length;
} wl_recovery_epoch_v3;
typedef struct {
    uint8_t mode;
    wl_recovery_digest_v3 operation;
    wl_recovery_digest_v3 transaction;
    wl_recovery_digest_v3 capability;
    wl_recovery_digest_v3 universe_head;
    wl_recovery_digest_v3 instance;
    wl_recovery_digest_v3 subject;
    wl_recovery_digest_v3 staged_root;
    wl_recovery_digest_v3 current_requirement;
    wl_recovery_digest_v3 resulting_requirement;
    wl_recovery_digest_v3 requester;
    wl_recovery_digest_v3 grant_use;
    wl_recovery_digest_v3 policy_identity;
    wl_recovery_digest_v3 selected_evaluation;
    wl_recovery_digest_v3 history_head;
    wl_recovery_digest_v3 reservation;
    wl_recovery_digest_v3 host;
    wl_recovery_digest_v3 before_prime;
    wl_recovery_digest_v3 before_root;
    wl_recovery_digest_v3 before_mapping;
    wl_recovery_digest_v3 staged_mapping;
    wl_recovery_digest_v3 input_snapshot;
    wl_recovery_digest_v3 kernel_build;
    wl_recovery_digest_v3 kernel_library;
    wl_recovery_digest_v3 kernel_mapping;
    wl_recovery_digest_v3 issuer_head;
    wl_recovery_digest_v3 receipt_head;
    wl_recovery_digest_v3 causal_head;
    wl_recovery_epoch_v3 policy_epoch, resource_epoch;
} wl_recovery_binding_v3;
typedef struct {
    wl_recovery_digest_v3 live_mapping, live_root;
} wl_recovery_native_v3;
typedef struct {
    uint32_t schema_version;
    uint8_t state, fresh, historical, grant_eligible;
    wl_recovery_binding_v3 issued_binding, recovered_binding;
    wl_recovery_native_v3 native;
} wl_recovery_request_v3;
typedef struct { uint8_t action, state; } wl_recovery_result_v3;
uint32_t wl_recovery_authorization_version_v3(void);
long wl_recovery_authorization_layout_v3(uint32_t kind, uint32_t field);
/* Copies complete request and arena before publishing output.
 * Valid caller memory, stable capture and protected provenance are caller duties.
 * Returns transport refusal on malformed shape; never falls back to bounded v2. */
int wl_recovery_authorization_decide_v3(
    const void *input, size_t input_length,
    const void *arena, size_t arena_length,
    void *output, size_t output_length);
#endif
