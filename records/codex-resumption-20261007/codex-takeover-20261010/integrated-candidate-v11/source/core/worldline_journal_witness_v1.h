#ifndef WORLDLINE_JOURNAL_WITNESS_V1_H
#define WORLDLINE_JOURNAL_WITNESS_V1_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* kind: 0 complete owner-canonical witness; 1 complete K4 resource ACK.
 * current: full original scoped custody-load-v2 envelope.
 * input: complete original operation_capture.archive witness, or
 *        {'capture': original_capture, 'ack': original_ACK_envelope} archive.
 * decision: 0 READY, 1 REFUSED, 2 INPUT_INVALID; transport return is separate.
 */
int wl_journal_witness_decide_v1(uint8_t kind,
    const uint8_t *current, size_t current_length,
    const uint8_t *input, size_t input_length, uint64_t *decision);
#ifdef __cplusplus
}
#endif
#endif
