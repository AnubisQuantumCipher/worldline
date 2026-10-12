#ifndef WORLDLINE_ACTUATOR_H
#define WORLDLINE_ACTUATOR_H

#include "worldline_full_physical_v1.h"
#include <stdbool.h>

/* Directory descriptors must be opened by the protected actuator service.
 * data_fd contains an entry named live; transaction_fd contains mapping.
 * These descriptors and the expected facts are not safe to take from an
 * untrusted same-UID client. This API is the narrow syscall boundary, not an
 * authorization service or a deployed OS isolation policy. */


/* Rechecks the complete SPARK exchange frame at the last syscall boundary.
 * It supplies observed recovery cleanliness, never an endpoint success flag. */
typedef bool (*wl_actuator_redecide)(void *context);

enum wl_actuator_result wl_actuator_exchange(
    int data_fd,
    int transaction_fd,
    const struct wl_actuation_request *requested,
    wl_actuator_redecide redecide,
    void *context,
    struct wl_actuator_witness *witness);

/* Historical recognition only: never invokes renameat2 or a fresh peer. */
enum wl_actuator_result wl_actuator_recover(
    int data_fd,
    int transaction_fd,
    const struct wl_actuation_request *requested,
    wl_actuator_redecide redecide,
    void *context,
    struct wl_actuator_witness *witness);

#endif
