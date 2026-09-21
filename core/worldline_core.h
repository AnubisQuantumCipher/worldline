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
#define WL_COLLAPSE_OWNER_MISMATCH 3u
#define WL_COLLAPSE_BASE_MISMATCH 4u
#define WL_COLLAPSE_DELTA_MISMATCH 5u
#define WL_COLLAPSE_ROOT_SET_MISMATCH 6u
#define WL_COLLAPSE_STAGED_ROOT_MISMATCH 7u
#define WL_COLLAPSE_CONFLICT 8u
#define WL_COLLAPSE_FOREIGN_MANAGED_WRITE 9u
#define WL_COLLAPSE_VALIDATION_CONTEXT_MISMATCH 10u
#define WL_COLLAPSE_STAGED_UNTESTED 11u
#define WL_COLLAPSE_INVALID_REQUEST 255u

/* Layout version of struct wl_collapse_request. The runtime and the library ship together;
 * a runtime built for a different layout must not call wl_collapse_decide. */
#define WL_COLLAPSE_REQUEST_VERSION 2u

struct wl_collapse_request {
    uint8_t candidate_state;
    uint8_t has_conflicts;
    uint8_t has_foreign_managed_writes;
    uint8_t reserved;
    uint8_t expected_parent[WL_HASH_BYTES];
    uint8_t candidate_parent[WL_HASH_BYTES];
    uint8_t expected_owner[WL_HASH_BYTES];
    uint8_t candidate_owner[WL_HASH_BYTES];
    uint8_t expected_base[WL_HASH_BYTES];
    uint8_t candidate_base[WL_HASH_BYTES];
    uint8_t expected_delta[WL_HASH_BYTES];
    uint8_t candidate_delta[WL_HASH_BYTES];
    uint8_t expected_root_set[WL_HASH_BYTES];
    uint8_t candidate_root_set[WL_HASH_BYTES];
    uint8_t expected_staged_root[WL_HASH_BYTES];
    uint8_t actual_staged_root[WL_HASH_BYTES];
    uint8_t expected_validation_context[WL_HASH_BYTES];
    uint8_t candidate_validation_context[WL_HASH_BYTES];
    uint8_t tested_root[WL_HASH_BYTES];
    uint8_t staged_content_root[WL_HASH_BYTES];
};

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

#ifdef __cplusplus
}
#endif

#endif
