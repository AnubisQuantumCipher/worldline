#ifndef WORLDLINE_CHAIN_AUTHORITY_V1_H
#define WORLDLINE_CHAIN_AUTHORITY_V1_H
#include <stddef.h>
#include <stdint.h>
typedef struct { uint8_t present; uint8_t value[32]; } wl_chain_digest_v1;
typedef struct {
  wl_chain_digest_v1 previous, actual_payload_root, stored_payload_root, stored_head;
} wl_chain_row_v1;
typedef struct {
  uint8_t kind;
  wl_chain_digest_v1 observed_genesis, witnessed_genesis, witnessed_head;
} wl_chain_anchors_v1;
typedef struct {
  uint8_t disposition;
  uint8_t head[32];
  int64_t accepted_count;
} wl_chain_result_v1;
uint32_t wl_chain_authority_version_v1(void);
long wl_chain_authority_layout_v1(uint32_t kind, uint32_t field);
int wl_chain_authority_replay_v1(const void *anchors, size_t anchors_length,
  const void *rows, size_t rows_count, size_t rows_length,
  void *output, size_t output_length);
#endif
