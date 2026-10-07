#ifndef WORLDLINE_RECOVERY_PROTOCOL_H
#define WORLDLINE_RECOVERY_PROTOCOL_H
#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t before, cause; } wl_recovery_protocol_request_v1;
typedef struct { uint8_t after; } wl_recovery_protocol_result_v1;
uint32_t wl_recovery_protocol_version_v1(void);
long wl_recovery_protocol_layout_v1(uint32_t kind, uint32_t field);
int wl_recovery_protocol_decide_v1(const void *input, size_t input_length,
                                 void *output, size_t output_length);
#endif
