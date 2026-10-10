#ifndef COSMOGONY_USE_RESERVATION_H
#define COSMOGONY_USE_RESERVATION_H
#include <stdint.h>
#include <stddef.h>
int cosmogony_use_reservation_version_v1(void);
long cosmogony_use_reservation_layout_v1(uint32_t kind, uint32_t field);
int cosmogony_use_reservation_decide_v1(const void *input, size_t input_length,
 const void *rows, size_t row_count, size_t rows_length,
 const void *grants, size_t grant_count, size_t grants_length,
 void *output, size_t output_length);
#endif
