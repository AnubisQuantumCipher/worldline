#define _GNU_SOURCE
#include "worldline_actuator.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/fs.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define MARKER_NAME ".worldline-generation.json"
#define MARKER_LIMIT 4096u

static bool parent_identity(int fd, struct stat *result) {
    return fstat(fd, result) == 0 && S_ISDIR(result->st_mode);
}

static bool entry_identity(int parent_fd, const char *name,
                           struct wl_entry_identity *result) {
    struct stat value;
    memset(result, 0, sizeof(*result));
    if (fstatat(parent_fd, name, &value, AT_SYMLINK_NOFOLLOW) != 0 ||
        !S_ISDIR(value.st_mode)) {
        return false;
    }
    result->present = 1;
    result->device = (uint64_t)value.st_dev;
    result->inode = (uint64_t)value.st_ino;
    return true;
}

static bool same_entry(const struct wl_entry_identity *left,
                       const struct wl_entry_identity *right) {
    return left->present == 1 && right->present == 1 &&
           left->device == right->device && left->inode == right->inode;
}

static bool marker_digest(int parent_fd, const char *name,
                          uint8_t digest[WL_HASH_BYTES]) {
    int mapping_fd = openat(parent_fd, name,
                            O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (mapping_fd < 0) {
        return false;
    }
    int marker_fd = openat(mapping_fd, MARKER_NAME,
                           O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
    close(mapping_fd);
    if (marker_fd < 0) {
        return false;
    }
    struct stat before;
    if (fstat(marker_fd, &before) != 0 || !S_ISREG(before.st_mode) ||
        before.st_size <= 0 || (uint64_t)before.st_size > MARKER_LIMIT) {
        close(marker_fd);
        return false;
    }
    uint8_t content[MARKER_LIMIT];
    size_t used = 0;
    while (used < (size_t)before.st_size) {
        ssize_t amount = read(marker_fd, content + used, (size_t)before.st_size - used);
        if (amount <= 0) {
            close(marker_fd);
            return false;
        }
        used += (size_t)amount;
    }
    struct stat after;
    bool stable = fstat(marker_fd, &after) == 0 &&
                  before.st_dev == after.st_dev && before.st_ino == after.st_ino &&
                  before.st_size == after.st_size &&
                  before.st_mtim.tv_sec == after.st_mtim.tv_sec &&
                  before.st_mtim.tv_nsec == after.st_mtim.tv_nsec &&
                  before.st_ctim.tv_sec == after.st_ctim.tv_sec &&
                  before.st_ctim.tv_nsec == after.st_ctim.tv_nsec;
    close(marker_fd);
    return stable && wl_hash_bytes(content, used, digest) == WL_OK;
}

static bool observe_before(int data_fd, int transaction_fd,
                           struct wl_actuation_request *facts,
                           struct wl_actuator_witness *witness) {
    if (!entry_identity(data_fd, "live", &facts->observed_live) ||
        !entry_identity(transaction_fd, "mapping", &facts->observed_stage) ||
        !marker_digest(transaction_fd, "mapping", facts->observed_marker_digest)) {
        return false;
    }
    witness->live_before = facts->observed_live;
    witness->stage_before = facts->observed_stage;
    memcpy(witness->marker_digest, facts->observed_marker_digest, WL_HASH_BYTES);
    return true;
}

enum wl_actuator_result wl_actuator_exchange(
    int data_fd,
    int transaction_fd,
    const struct wl_actuation_request *requested,
    wl_actuator_redecide redecide,
    void *context,
    struct wl_actuator_witness *witness) {
    if (requested == NULL || witness == NULL || redecide == NULL) {
        return WL_ACTUATOR_REFUSED;
    }
    memset(witness, 0, sizeof(*witness));
    witness->decision = WL_ACTUATION_INVALID_REQUEST;
    struct stat data_dir, transaction_dir;
    if (!parent_identity(data_fd, &data_dir) ||
        !parent_identity(transaction_fd, &transaction_dir) ||
        (data_dir.st_dev == transaction_dir.st_dev &&
         data_dir.st_ino == transaction_dir.st_ino)) {
        return WL_ACTUATOR_REFUSED;
    }

    struct wl_actuation_request facts = *requested;
    witness->payload_durable = facts.payload_durable;
    witness->recovery_clean = facts.recovery_clean;
    if (!observe_before(data_fd, transaction_fd, &facts, witness)) {
        return WL_ACTUATOR_REFUSED;
    }
    witness->decision = wl_actuation_decide(&facts);
    if (witness->decision != WL_ACTUATION_AUTHORIZED) {
        return WL_ACTUATOR_REFUSED;
    }
    if (fsync(data_fd) != 0 || fsync(transaction_fd) != 0) {
        witness->syscall_errno = errno;
        return WL_ACTUATOR_IO_REFUSED;
    }

    /* The protected service must own both parent directories. Recheck the
     * entries and marker just before the syscall; renameat2 has no compare-
     * and-swap condition for directory inodes. */
    struct wl_actuation_request last = facts;
    if (!observe_before(data_fd, transaction_fd, &last, witness) ||
        !same_entry(&last.observed_live, &facts.observed_live) ||
        !same_entry(&last.observed_stage, &facts.observed_stage) ||
        memcmp(last.observed_marker_digest, facts.observed_marker_digest,
               WL_HASH_BYTES) != 0) {
        return WL_ACTUATOR_REFUSED;
    }
    last.recovery_clean = redecide(context) ? 1 : 0;
    witness->recovery_clean = last.recovery_clean;
    witness->decision = wl_actuation_decide(&last);
    if (witness->decision != WL_ACTUATION_AUTHORIZED) {
        return WL_ACTUATOR_REFUSED;
    }
    witness->parents_durable = 0;

    witness->exchange_attempted = 1;
    if (renameat2(data_fd, "live", transaction_fd, "mapping", RENAME_EXCHANGE) != 0) {
        witness->syscall_errno = errno;
        return WL_ACTUATOR_IO_REFUSED;
    }

    bool observed = entry_identity(data_fd, "live", &witness->live_after) &&
                    entry_identity(transaction_fd, "mapping", &witness->stage_after);
    bool swapped = observed &&
                   same_entry(&witness->live_after, &facts.observed_stage) &&
                   same_entry(&witness->stage_after, &facts.observed_live);
    bool durable = fsync(data_fd) == 0 && fsync(transaction_fd) == 0;
    int sync_errno = durable ? 0 : errno;
    witness->parents_durable = durable ? 1 : 0;
    /* Durable success is tied to a readback after the actual fsyncs. */
    observed = entry_identity(data_fd, "live", &witness->live_after) &&
               entry_identity(transaction_fd, "mapping", &witness->stage_after);
    swapped = swapped && observed &&
              same_entry(&witness->live_after, &facts.observed_stage) &&
              same_entry(&witness->stage_after, &facts.observed_live);
    if (!swapped || !durable) {
        witness->syscall_errno = sync_errno;
        return WL_ACTUATOR_POST_EXCHANGE_UNCERTAIN;
    }
    return WL_ACTUATOR_VERIFIED;
}

static bool observe_after(int data_fd, int transaction_fd,
                          const struct wl_actuation_request *requested,
                          struct wl_actuator_witness *witness) {
    return entry_identity(data_fd, "live", &witness->live_after) &&
           entry_identity(transaction_fd, "mapping", &witness->stage_after) &&
           same_entry(&witness->live_after, &requested->expected_stage) &&
           same_entry(&witness->stage_after, &requested->expected_live) &&
           marker_digest(data_fd, "live", witness->marker_digest) &&
           memcmp(witness->marker_digest, requested->expected_marker_digest,
                  WL_HASH_BYTES) == 0;
}

enum wl_actuator_result wl_actuator_recover(
    int data_fd, int transaction_fd,
    const struct wl_actuation_request *requested,
    wl_actuator_redecide redecide, void *context,
    struct wl_actuator_witness *witness) {
    if (requested == NULL || witness == NULL || redecide == NULL) {
        return WL_ACTUATOR_REFUSED;
    }
    memset(witness, 0, sizeof(*witness));
    witness->decision = WL_ACTUATION_INVALID_REQUEST;
    witness->payload_durable = requested->payload_durable;
    witness->live_before = requested->expected_live;
    witness->stage_before = requested->expected_stage;
    if (same_entry(&requested->expected_live, &requested->expected_stage) ||
        !observe_after(data_fd, transaction_fd, requested, witness) ||
        requested->payload_durable != 1 || !redecide(context)) {
        return WL_ACTUATOR_REFUSED;
    }
    if (fsync(data_fd) != 0 || fsync(transaction_fd) != 0) {
        witness->syscall_errno = errno;
        return WL_ACTUATOR_POST_EXCHANGE_UNCERTAIN;
    }
    witness->parents_durable = 1;
    if (!observe_after(data_fd, transaction_fd, requested, witness) ||
        !redecide(context)) {
        return WL_ACTUATOR_POST_EXCHANGE_UNCERTAIN;
    }
    witness->recovery_clean = 1;
    /* No current collapse/peer policy is substituted for original history. */
    return WL_ACTUATOR_VERIFIED;
}
