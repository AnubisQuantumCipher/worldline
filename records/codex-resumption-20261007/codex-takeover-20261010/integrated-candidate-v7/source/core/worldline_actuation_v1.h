#ifndef WORLDLINE_FULL_ACTUATION_V1_H
#define WORLDLINE_FULL_ACTUATION_V1_H
#include "worldline_core.h"
#define WL_ACTUATION_AUTHORIZED 0u
#define WL_ACTUATION_INVALID_REQUEST 255u
/* Exact physical value representation from declared public 035545 source.
 * No fixed evaluation/service authority representation is imported. */
struct wl_entry_identity { uint8_t present; uint64_t device,inode; };
struct wl_actuation_request {
 struct wl_collapse_request collapse_facts;
 struct wl_entry_identity expected_live,observed_live,expected_stage,observed_stage;
 uint8_t expected_marker_digest[WL_HASH_BYTES],observed_marker_digest[WL_HASH_BYTES];
 uint8_t payload_durable,recovery_clean;
};
uint8_t wl_actuation_decide(const struct wl_actuation_request *request);
#endif
