/* Native-owned lifetime transport. Included after guard state and refusals.
 * This identifies retention by an examiner process, not protected custody.
 * No Python API submits these records or replaces the transport after bootstrap.
 */
#include <fcntl.h>
#include <poll.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>

enum wl_kind { WL_HELLO = 1, WL_ATTEMPT, WL_RESULT, WL_ACTIVATION, WL_TERMINAL };
enum wl_tag { WL_NONE, WL_FALSE, WL_TRUE, WL_INTEGER, WL_TEXT, WL_BYTES,
              WL_TUPLE, WL_UNAVAILABLE };
#define WL_MAGIC_SIZE (sizeof("WLNLv001") - 1)
#define WL_TOKEN_SIZE 32
#define WL_HEADER_SIZE (WL_MAGIC_SIZE + sizeof(uint64_t) * 3 + WL_TOKEN_SIZE)
#define WL_ACK_SIZE (WL_HEADER_SIZE + WL_TOKEN_SIZE)

struct wl_stream {
    int descriptor, attempted, attached, failed, busy;
    uint64_t sequence, deadline_ns, outstanding;
    unsigned char previous[WL_TOKEN_SIZE];
};
static struct wl_stream lifetime = {.descriptor = -1};
static Py_tss_t lifetime_operation_key = Py_tss_NEEDS_INIT;
struct wl_operation {
    uint64_t identity;
    struct wl_operation *parent;
    PyThreadState *thread;
    struct generator_route *result_route;
    int begun;
};

struct wl_record {
    int descriptor, failed, complete;
    uint64_t extent;
    size_t buffered;
    unsigned char buffer[8192]; /* transport chunk only; not an input limit */
};

static void
wl_u64_bytes(unsigned char *destination, uint64_t value)
{
    for (size_t i = 0; i < sizeof(value); ++i)
        destination[i] = (unsigned char)(value >> (i * CHAR_BIT));
}

static uint64_t
wl_bytes_u64(const unsigned char *source)
{
    uint64_t value = 0;
    for (size_t i = 0; i < sizeof(value); ++i)
        value |= (uint64_t)source[i] << (i * CHAR_BIT);
    return value;
}

static int
wl_now(uint64_t *value)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0 || now.tv_sec < 0 ||
        (uint64_t)now.tv_sec > (UINT64_MAX - (uint64_t)now.tv_nsec) / 1000000000)
        return -1;
    *value = (uint64_t)now.tv_sec * 1000000000 + (uint64_t)now.tv_nsec;
    return 0;
}

static int
wl_deadline(void)
{
    uint64_t now;
    if (wl_now(&now) < 0 || now >= lifetime.deadline_ns) {
        errno = ETIMEDOUT;
        return -1;
    }
    return 0;
}

static int
wl_poll(short events)
{
    for (;;) {
        uint64_t now;
        if (wl_now(&now) < 0 || now >= lifetime.deadline_ns) {
            errno = ETIMEDOUT;
            return -1;
        }
        uint64_t remaining = lifetime.deadline_ns - now;
        uint64_t millis = remaining / 1000000 + (remaining % 1000000 != 0);
        int timeout = millis > INT_MAX ? INT_MAX : (int)millis;
        struct pollfd descriptor = {.fd = lifetime.descriptor, .events = events};
        int result = poll(&descriptor, 1, timeout);
        if (result < 0 && errno == EINTR)
            continue;
        if (result < 0)
            return -1;
        if (result == 0)
            continue;
        if (descriptor.revents & events)
            return 0;
        errno = EPIPE;
        return -1;
    }
}

static struct wl_record
wl_record_open(void)
{
    struct wl_record record = {.descriptor = -1, .complete = 1};
    if (wl_deadline() == 0)
        record.descriptor = memfd_create("worldline-native-lifetime", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (record.descriptor < 0)
        record.failed = 1;
    return record;
}

static int
wl_flush(struct wl_record *record)
{
    if (record->failed)
        return -1;
    const unsigned char *cursor = record->buffer;
    size_t remaining = record->buffered;
    while (remaining) {
        if (wl_deadline() < 0)
            goto failure;
        size_t chunk = remaining > (size_t)SSIZE_MAX ? (size_t)SSIZE_MAX : remaining;
        ssize_t count = write(record->descriptor, cursor, chunk);
        if (count < 0 && errno == EINTR)
            continue;
        if (count <= 0)
            goto failure;
        cursor += (size_t)count;
        remaining -= (size_t)count;
    }
    record->buffered = 0;
    return 0;
failure:
    record->failed = 1;
    return -1;
}

static int
wl_write(struct wl_record *record, const void *data, size_t length)
{
    if (record->failed)
        return -1;
    if (length > UINT64_MAX - record->extent) {
        record->failed = 1;
        errno = EOVERFLOW;
        return -1;
    }
    const unsigned char *cursor = data;
    while (length) {
        size_t available = sizeof(record->buffer) - record->buffered;
        size_t chunk = length < available ? length : available;
        memcpy(record->buffer + record->buffered, cursor, chunk);
        record->buffered += chunk;
        record->extent += chunk;
        cursor += chunk;
        length -= chunk;
        if (record->buffered == sizeof(record->buffer) && wl_flush(record) < 0)
            return -1;
    }
    return 0;
}

static int
wl_tag(struct wl_record *record, enum wl_tag tag)
{
    unsigned char value = (unsigned char)tag;
    return wl_write(record, &value, sizeof(value));
}

static int
wl_count(struct wl_record *record, uint64_t count)
{
    unsigned char value[sizeof(count)];
    wl_u64_bytes(value, count);
    return wl_write(record, value, sizeof(value));
}

static int
wl_blob(struct wl_record *record, enum wl_tag tag, const void *bytes, size_t length)
{
    return wl_tag(record, tag) < 0 || wl_count(record, length) < 0 ||
           wl_write(record, bytes, length) < 0 ? -1 : 0;
}

static int
wl_tuple(struct wl_record *record, uint64_t count)
{
    return wl_tag(record, WL_TUPLE) < 0 || wl_count(record, count) < 0 ? -1 : 0;
}

static int
wl_integer_bytes(struct wl_record *record, const unsigned char *bytes, size_t length)
{
    /* Unique minimal signed representation, including the single-byte zero. */
    while (length > 1 &&
           ((bytes[length - 1] == 0 && !(bytes[length - 2] & 0x80)) ||
            (bytes[length - 1] == 0xff && (bytes[length - 2] & 0x80))))
        --length;
    return wl_blob(record, WL_INTEGER, bytes, length);
}

static int
wl_unsigned(struct wl_record *record, uint64_t value)
{
    /* Extra zero sign byte preserves every unsigned native counter exactly. */
    unsigned char bytes[sizeof(value) + 1] = {0};
    wl_u64_bytes(bytes, value);
    return wl_integer_bytes(record, bytes, sizeof(bytes));
}

static int
wl_signed(struct wl_record *record, int64_t value)
{
    unsigned char bytes[sizeof(value)];
    wl_u64_bytes(bytes, (uint64_t)value);
    return wl_integer_bytes(record, bytes, sizeof(bytes));
}

static int
wl_ascii(struct wl_record *record, const char *value)
{
    if (value == NULL)
        return wl_tag(record, WL_NONE);
    size_t length = strlen(value);
    if (length > UINT64_MAX / sizeof(uint32_t)) {
        record->failed = 1;
        return -1;
    }
    if (wl_tag(record, WL_TEXT) < 0 || wl_count(record, length * sizeof(uint32_t)) < 0)
        return -1;
    for (size_t i = 0; i < length; ++i) {
        unsigned char point[sizeof(uint32_t)] = {(unsigned char)value[i], 0, 0, 0};
        if ((unsigned char)value[i] > 0x7f || wl_write(record, point, sizeof(point)) < 0) {
            record->failed = 1;
            return -1;
        }
    }
    return 0;
}

static int
wl_scalar(struct wl_record *record, PyObject *value)
{
    if (value == Py_None)
        return wl_tag(record, WL_NONE);
    if (PyBool_Check(value))
        return wl_tag(record, value == Py_True ? WL_TRUE : WL_FALSE);
    if (PyBytes_CheckExact(value))
        return wl_blob(record, WL_BYTES, PyBytes_AS_STRING(value), (size_t)PyBytes_GET_SIZE(value));
    if (PyUnicode_CheckExact(value)) {
        Py_ssize_t length = PyUnicode_GET_LENGTH(value);
        if ((uint64_t)length > UINT64_MAX / sizeof(uint32_t)) {
            record->failed = 1;
            return -1;
        }
        if (wl_tag(record, WL_TEXT) < 0 ||
            wl_count(record, (uint64_t)length * sizeof(uint32_t)) < 0)
            return -1;
        int kind = PyUnicode_KIND(value);
        const void *data = PyUnicode_DATA(value);
        for (Py_ssize_t i = 0; i < length; ++i) {
            uint32_t codepoint = PyUnicode_READ(kind, data, i);
            unsigned char point[sizeof(codepoint)];
            for (size_t part = 0; part < sizeof(codepoint); ++part)
                point[part] = (unsigned char)(codepoint >> (part * CHAR_BIT));
            if (wl_write(record, point, sizeof(point)) < 0)
                return -1;
        }
        return 0;
    }
    if (PyLong_CheckExact(value)) {
        Py_ssize_t length = PyLong_AsNativeBytes(value, NULL, 0, Py_ASNATIVEBYTES_LITTLE_ENDIAN);
        if (length <= 0)
            goto failure;
        void *bytes = malloc((size_t)length);
        if (bytes == NULL) {
            PyErr_NoMemory();
            goto failure;
        }
        Py_ssize_t required = PyLong_AsNativeBytes(value, bytes, length, Py_ASNATIVEBYTES_LITTLE_ENDIAN);
        int result = required <= 0 || required > length ? -1 :
                     wl_integer_bytes(record, bytes, (size_t)length);
        free(bytes);
        if (result < 0)
            goto failure;
        return 0;
    }
    if (PyFunction_Check(value)) {
        struct code_slot *slot = lookup_code(PyFunction_GET_CODE(value));
        wl_tuple(record, 3);
        wl_ascii(record, "function-code-and-globals-observation");
        if (slot == NULL) {
            wl_tag(record, WL_NONE);
            record->complete = 0;
        } else {
            wl_unsigned(record, slot->identity);
        }
        /* Actual address at observation, not an independently trusted identity.
         * The binding operation separately holds and checks these globals. */
        return wl_unsigned(record, (uint64_t)(uintptr_t)PyFunction_GET_GLOBALS(value));
    }
    /* A native type name is an explicit missing-content observation, never a
     * substitute for invoking arbitrary repr/attributes or serializing a graph. */
    record->complete = 0;
    const char *name = Py_TYPE(value)->tp_name;
    return wl_blob(record, WL_UNAVAILABLE, name, strlen(name));
failure:
    record->failed = 1;
    return -1;
}

static int
wl_value(struct wl_record *record, PyObject *value)
{
    struct level { PyObject *tuple; Py_ssize_t next; };
    struct level *stack = NULL;
    size_t depth = 0, capacity = 0;
    int result = -1;
    for (;;) {
        if (PyTuple_CheckExact(value)) {
            Py_ssize_t length = PyTuple_GET_SIZE(value);
            if (wl_tuple(record, (uint64_t)length) < 0)
                break;
            if (length) {
                if (depth == capacity) {
                    if (capacity > (SIZE_MAX / sizeof(*stack) - 1) / 2) {
                        errno = EOVERFLOW;
                        break;
                    }
                    size_t grown = capacity * 2 + 1;
                    struct level *replacement = realloc(stack, grown * sizeof(*stack));
                    if (replacement == NULL) {
                        PyErr_NoMemory();
                        break;
                    }
                    stack = replacement;
                    capacity = grown;
                }
                stack[depth++] = (struct level){.tuple = value, .next = 1};
                value = PyTuple_GET_ITEM(value, 0);
                continue;
            }
        } else if (wl_scalar(record, value) < 0) {
            break;
        }
        while (depth && stack[depth - 1].next == PyTuple_GET_SIZE(stack[depth - 1].tuple))
            --depth;
        if (!depth) {
            result = 0;
            break;
        }
        struct level *top = &stack[depth - 1];
        value = PyTuple_GET_ITEM(top->tuple, top->next++);
    }
    free(stack);
    if (result < 0)
        record->failed = 1;
    return result;
}

static int
wl_close(int descriptor)
{
    /* Linux releases the descriptor even when close reports EINTR. Never retry
     * a reused number. A reported failure remains an actual failed producer. */
    return descriptor < 0 ? 0 : close(descriptor);
}

static int
wl_mapping(struct wl_record *record, PyObject *mapping)
{
    /* A flat exact dictionary snapshot. Values use the bounded-work iterative
     * serializer; arbitrary nested mutable graphs remain explicitly unavailable. */
    if (!PyDict_CheckExact(mapping))
        return wl_value(record, mapping);
    wl_tuple(record, 2);
    wl_ascii(record, "exact-dict-entries");
    wl_tuple(record, (uint64_t)PyDict_Size(mapping));
    Py_ssize_t cursor = 0;
    PyObject *key, *value;
    while (PyDict_Next(mapping, &cursor, &key, &value)) {
        if (wl_deadline() < 0) {
            record->failed = 1;
            return -1;
        }
        wl_tuple(record, 2);
        wl_value(record, key);
        wl_value(record, value);
    }
    return record->failed ? -1 : 0;
}

static void
wl_cached_origin(struct wl_record *record, struct cached_snapshot *snapshot)
{
    if (snapshot == NULL) {
        wl_tag(record, WL_NONE);
        return;
    }
    for (size_t route = 0; route < ROUTE_COUNT; ++route) {
        if (snapshot != &cached_snapshots[route])
            continue;
        struct code_slot *slot = lookup_code(snapshot->code);
        wl_tuple(record, 7);
        wl_ascii(record, "held-cached-origin");
        wl_ascii(record, cached_names[route].label);
        wl_ascii(record, cached_names[route].path);
        if (slot == NULL) {
            record->failed = 1;
            return;
        }
        wl_unsigned(record, slot->identity);
        wl_unsigned(record, (uint64_t)(uintptr_t)snapshot->function);
        wl_unsigned(record, (uint64_t)(uintptr_t)snapshot->globals);
        wl_unsigned(record, (uint64_t)(uintptr_t)snapshot->namespace);
        return;
    }
    record->failed = 1;
}

static void
wl_code_tree(struct wl_record *record, PyObject *root)
{
    PyObject **nodes = NULL;
    size_t count = 0, capacity = 0, cursor = 0;
    uint64_t visit = lifetime.sequence + 1;
    PyObject *current = root;
    if (visit == 0)
        goto failure;
    for (;;) {
        struct code_slot *slot = lookup_code(current);
        if (slot == NULL || wl_deadline() < 0)
            goto failure;
        if (slot->lifetime_visit != visit) {
            if (count == capacity) {
                if (capacity > (SIZE_MAX / sizeof(*nodes) - 1) / 2)
                    goto failure;
                size_t grown = capacity * 2 + 1;
                PyObject **replacement = realloc(nodes, grown * sizeof(*nodes));
                if (replacement == NULL)
                    goto failure;
                nodes = replacement;
                capacity = grown;
            }
            nodes[count++] = current;
            slot->lifetime_visit = visit;
        }
        if (cursor == count)
            break;
        PyObject *constants = ((PyCodeObject *)nodes[cursor++])->co_consts;
        if (!PyTuple_CheckExact(constants))
            goto failure;
        for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(constants); ++i) {
            PyObject *child = PyTuple_GET_ITEM(constants, i);
            if (!PyCode_Check(child))
                continue;
            struct code_slot *child_slot = lookup_code(child);
            if (child_slot == NULL || wl_deadline() < 0)
                goto failure;
            if (child_slot->lifetime_visit == visit)
                continue;
            if (count == capacity) {
                if (capacity > (SIZE_MAX / sizeof(*nodes) - 1) / 2)
                    goto failure;
                size_t grown = capacity * 2 + 1;
                PyObject **replacement = realloc(nodes, grown * sizeof(*nodes));
                if (replacement == NULL)
                    goto failure;
                nodes = replacement;
                capacity = grown;
            }
            nodes[count++] = child;
            child_slot->lifetime_visit = visit;
        }
        /* Every queued node is already marked; the cursor is the worklist. */
        if (cursor == count)
            break;
        current = nodes[cursor];
    }
    wl_tuple(record, 3);
    wl_ascii(record, "owned-code-tree");
    wl_unsigned(record, lookup_code(root)->identity);
    wl_tuple(record, count);
    for (size_t i = 0; i < count; ++i) {
        struct code_slot *slot = lookup_code(nodes[i]);
        PyCodeObject *code = (PyCodeObject *)nodes[i];
        PyObject *constants = code->co_consts;
        uint64_t edges = 0;
        for (Py_ssize_t j = 0; j < PyTuple_GET_SIZE(constants); ++j) {
            if (wl_deadline() < 0)
                goto failure;
            edges += PyCode_Check(PyTuple_GET_ITEM(constants, j)) != 0;
        }
        wl_tuple(record, 6);
        wl_unsigned(record, slot->identity);
        wl_value(record, slot->source->path);
        wl_cached_origin(record, slot->cached_origin);
        wl_value(record, code->co_qualname);
        wl_unsigned(record, (uint64_t)PyTuple_GET_SIZE(constants));
        wl_tuple(record, edges);
        for (Py_ssize_t j = 0; j < PyTuple_GET_SIZE(constants); ++j) {
            PyObject *child = PyTuple_GET_ITEM(constants, j);
            if (!PyCode_Check(child))
                continue;
            wl_tuple(record, 2);
            wl_unsigned(record, (uint64_t)j);
            wl_unsigned(record, lookup_code(child)->identity);
        }
    }
    free(nodes);
    return;
failure:
    free(nodes);
    record->failed = 1;
}

static void
wl_route(struct wl_record *record, struct generator_route *route)
{
    for (size_t index = 0; index < ROUTE_COUNT; ++index) {
        if (route != &state.routes[index] || !route->bound)
            continue;
        struct code_slot *slot = lookup_code(route->code);
        if (slot == NULL) {
            record->failed = 1;
            return;
        }
        wl_tuple(record, 7);
        wl_ascii(record, "held-generator-binding");
        wl_ascii(record, cached_names[index].label);
        wl_value(record, route->source->path);
        wl_blob(record, WL_BYTES, route->source->bytes, (size_t)route->source->length);
        wl_unsigned(record, (uint64_t)(uintptr_t)route->globals);
        wl_cached_origin(record, slot->cached_origin);
        wl_code_tree(record, route->code);
        return;
    }
    record->failed = 1;
}

static int
wl_exchange(enum wl_kind kind, struct wl_record *record)
{
    int result = -1;
    if (record->failed || lifetime.failed || lifetime.sequence == UINT64_MAX || wl_flush(record) < 0)
        goto done;
    if (fcntl(record->descriptor, F_ADD_SEALS,
              F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL) < 0)
        goto done;
    unsigned char header[WL_HEADER_SIZE];
    memcpy(header, "WLNLv001", WL_MAGIC_SIZE);
    wl_u64_bytes(header + WL_MAGIC_SIZE, kind);
    wl_u64_bytes(header + WL_MAGIC_SIZE + sizeof(uint64_t), lifetime.sequence);
    wl_u64_bytes(header + WL_MAGIC_SIZE + sizeof(uint64_t) * 2, record->extent);
    memcpy(header + WL_MAGIC_SIZE + sizeof(uint64_t) * 3, lifetime.previous, WL_TOKEN_SIZE);
    union { struct cmsghdr alignment; unsigned char bytes[CMSG_SPACE(sizeof(int))]; } control;
    memset(&control, 0, sizeof(control));
    struct iovec vector = {.iov_base = header, .iov_len = sizeof(header)};
    struct msghdr message = {.msg_iov = &vector, .msg_iovlen = 1,
        .msg_control = control.bytes, .msg_controllen = sizeof(control.bytes)};
    struct cmsghdr *ancillary = CMSG_FIRSTHDR(&message);
    ancillary->cmsg_level = SOL_SOCKET;
    ancillary->cmsg_type = SCM_RIGHTS;
    ancillary->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(ancillary), &record->descriptor, sizeof(record->descriptor));
    for (;;) {
        if (wl_poll(POLLOUT) < 0)
            goto done;
        ssize_t sent = sendmsg(lifetime.descriptor, &message, MSG_DONTWAIT | MSG_NOSIGNAL);
        if (sent < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
            continue;
        if (sent != (ssize_t)sizeof(header))
            goto done;
        break;
    }
    if (kind == WL_TERMINAL && shutdown(lifetime.descriptor, SHUT_WR) < 0)
        goto done;
    unsigned char ack[WL_ACK_SIZE + 1];
    /* Matches the existing original packet bound; an ACK permits no ancillary
     * data. Own and close every handle the kernel delivered, even on refusal. */
    union { struct cmsghdr alignment; unsigned char bytes[65536]; } delivered;
    for (;;) {
        if (wl_poll(POLLIN) < 0)
            goto done;
        struct iovec input = {.iov_base = ack, .iov_len = sizeof(ack)};
        struct msghdr reply = {.msg_iov = &input, .msg_iovlen = 1,
            .msg_control = delivered.bytes, .msg_controllen = sizeof(delivered.bytes)};
        ssize_t received = recvmsg(lifetime.descriptor, &reply, MSG_DONTWAIT | MSG_CMSG_CLOEXEC);
        if (received < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
            continue;
        if (received < 0)
            goto done;
        int unexpected = reply.msg_controllen != 0;
        for (struct cmsghdr *item = CMSG_FIRSTHDR(&reply); item != NULL; item = CMSG_NXTHDR(&reply, item)) {
            if (item->cmsg_len >= CMSG_LEN(0) && item->cmsg_level == SOL_SOCKET && item->cmsg_type == SCM_RIGHTS) {
                size_t bytes = item->cmsg_len - CMSG_LEN(0);
                for (size_t offset = 0; offset + sizeof(int) <= bytes; offset += sizeof(int)) {
                    int descriptor;
                    memcpy(&descriptor, (unsigned char *)CMSG_DATA(item) + offset, sizeof(descriptor));
                    (void)wl_close(descriptor);
                }
            }
        }
        if (received != (ssize_t)WL_ACK_SIZE || unexpected ||
            (reply.msg_flags & ~(MSG_EOR | MSG_CMSG_CLOEXEC)) ||
            memcmp(ack, "WLAKv001", WL_MAGIC_SIZE) != 0 ||
            wl_bytes_u64(ack + WL_MAGIC_SIZE) != (uint64_t)kind ||
            wl_bytes_u64(ack + WL_MAGIC_SIZE + sizeof(uint64_t)) != lifetime.sequence ||
            memcmp(ack + WL_MAGIC_SIZE + sizeof(uint64_t) * 3, lifetime.previous, WL_TOKEN_SIZE) != 0)
            goto done;
        uint64_t deadline = wl_bytes_u64(ack + WL_MAGIC_SIZE + sizeof(uint64_t) * 2);
        if (!deadline || deadline > lifetime.deadline_ns)
            goto done;
        lifetime.deadline_ns = deadline;
        if (wl_deadline() < 0)
            goto done;
        memcpy(lifetime.previous, ack + WL_HEADER_SIZE, WL_TOKEN_SIZE);
        ++lifetime.sequence;
        result = 0;
        break;
    }
done:
    if (wl_close(record->descriptor) < 0)
        result = -1;
    record->descriptor = -1;
    if (result < 0) {
        lifetime.failed = 1;
        latch("native lifetime retention failed");
    }
    return result;
}

static int
wl_python_failure(void)
{
    lifetime.failed = 1;
    latch("native lifetime retention failed");
    if (!PyErr_Occurred())
        PyErr_SetString(PyExc_PermissionError, "native lifetime retention failed");
    return -1;
}

static void
wl_optional_object(struct wl_record *record, PyObject *value)
{
    wl_tuple(record, 2);
    wl_tag(record, value == NULL ? WL_FALSE : WL_TRUE);
    if (value == NULL)
        wl_tag(record, WL_NONE);
    else if (PyDict_CheckExact(value))
        wl_mapping(record, value);
    else
        wl_value(record, value);
}

static void
wl_exception(struct wl_record *record, PyObject *primary)
{
    if (primary == NULL) {
        wl_tag(record, WL_NONE);
        return;
    }
    wl_tuple(record, 4);
    const char *name = Py_TYPE(primary)->tp_name;
    wl_blob(record, WL_BYTES, name, strlen(name));
    wl_ascii(record, "native-boundary-before-return");
    if (!PyExceptionInstance_Check(primary)) {
        wl_tag(record, WL_NONE);
        wl_tag(record, WL_NONE);
        record->complete = 0;
        return;
    }
    PyBaseExceptionObject *base = (PyBaseExceptionObject *)primary;
    PyObject *base_fields[] = {base->args, base->dict, base->notes, base->traceback,
                              base->context, base->cause};
    wl_tuple(record, sizeof(base_fields) / sizeof(base_fields[0]) + 1);
    for (size_t i = 0; i < sizeof(base_fields) / sizeof(base_fields[0]); ++i)
        wl_optional_object(record, base_fields[i]);
    wl_tag(record, base->suppress_context ? WL_TRUE : WL_FALSE);
    if (PyObject_TypeCheck(primary, (PyTypeObject *)PyExc_ImportError)) {
        PyImportErrorObject *error = (PyImportErrorObject *)primary;
        PyObject *fields[] = {error->msg, error->name, error->path, error->name_from};
        wl_tuple(record, sizeof(fields) / sizeof(fields[0]) + 1);
        wl_ascii(record, "ImportError");
        for (size_t i = 0; i < sizeof(fields) / sizeof(fields[0]); ++i)
            wl_optional_object(record, fields[i]);
        if (Py_TYPE(primary) != (PyTypeObject *)PyExc_ImportError &&
            Py_TYPE(primary) != (PyTypeObject *)PyExc_ModuleNotFoundError)
            record->complete = 0;
    } else if (PyObject_TypeCheck(primary, (PyTypeObject *)PyExc_SyntaxError)) {
        PySyntaxErrorObject *error = (PySyntaxErrorObject *)primary;
        PyObject *fields[] = {error->msg, error->filename, error->lineno, error->offset,
            error->end_lineno, error->end_offset, error->text, error->print_file_and_line,
            error->metadata};
        wl_tuple(record, sizeof(fields) / sizeof(fields[0]) + 1);
        wl_ascii(record, "SyntaxError");
        for (size_t i = 0; i < sizeof(fields) / sizeof(fields[0]); ++i)
            wl_optional_object(record, fields[i]);
        if (Py_TYPE(primary) != (PyTypeObject *)PyExc_SyntaxError &&
            Py_TYPE(primary) != (PyTypeObject *)PyExc_IndentationError &&
            Py_TYPE(primary) != (PyTypeObject *)PyExc_TabError)
            record->complete = 0;
    } else if (PyObject_TypeCheck(primary, (PyTypeObject *)PyExc_OSError)) {
        PyOSErrorObject *error = (PyOSErrorObject *)primary;
        PyObject *fields[] = {error->myerrno, error->strerror, error->filename, error->filename2};
        wl_tuple(record, sizeof(fields) / sizeof(fields[0]) + 2);
        wl_ascii(record, "OSError");
        for (size_t i = 0; i < sizeof(fields) / sizeof(fields[0]); ++i)
            wl_optional_object(record, fields[i]);
        wl_signed(record, error->written);
        /* OSError subclasses can carry additional native or Python fields. */
        if (Py_TYPE(primary) != (PyTypeObject *)PyExc_OSError)
            record->complete = 0;
    } else {
        wl_ascii(record, "base-fields-only-not-a-subclass-object-snapshot");
        /* No type/argument summary claims a complete arbitrary exception object. */
        record->complete = 0;
    }
}

static int
wl_begin(struct wl_operation *operation, const char *name,
         PyObject *const *inputs, size_t input_count, const struct source *source,
         const int64_t *options, size_t option_count)
{
    memset(operation, 0, sizeof(*operation));
    if (!lifetime.attached)
        return 0;
    if (lifetime.failed || lifetime.busy || lifetime.outstanding == UINT64_MAX)
        return wl_python_failure();
    lifetime.busy = state.lifetime_operation = 1;
    operation->thread = PyThreadState_Get();
    operation->parent = PyThread_tss_get(&lifetime_operation_key);
    operation->identity = lifetime.sequence;
    struct wl_record record = wl_record_open();
    wl_tuple(&record, 9);
    wl_ascii(&record, name);
    wl_unsigned(&record, (uint64_t)state.phase);
    wl_unsigned(&record, PyThreadState_GetID(operation->thread));
    if (operation->parent == NULL)
        wl_tag(&record, WL_NONE);
    else
        wl_unsigned(&record, operation->parent->identity);
    int generated = strcmp(name, "validated-generator-source") == 0;
    wl_tuple(&record, input_count + (generated != 0));
    for (size_t i = 0; i < input_count; ++i) {
        if (PyDict_CheckExact(inputs[i]))
            wl_mapping(&record, inputs[i]);
        else
            wl_value(&record, inputs[i]);
    }
    if (generated) {
        if (option_count != 1 || options[0] < 0 || options[0] >= ROUTE_COUNT)
            record.failed = 1;
        else
            wl_route(&record, &state.routes[options[0]]);
    }
    if (source == NULL) {
        wl_tag(&record, WL_NONE);
        wl_tag(&record, WL_NONE);
    } else {
        wl_value(&record, source->path);
        wl_blob(&record, WL_BYTES, source->bytes, (size_t)source->length);
    }
    wl_tuple(&record, option_count);
    for (size_t i = 0; i < option_count; ++i)
        wl_signed(&record, options[i]);
    wl_unsigned(&record, state.code_count);
    int result = wl_exchange(WL_ATTEMPT, &record);
    lifetime.busy = state.lifetime_operation = 0;
    if (result < 0)
        return wl_python_failure();
    if (PyThread_tss_set(&lifetime_operation_key, operation) != 0)
        return wl_python_failure();
    ++lifetime.outstanding;
    operation->begun = 1;
    return 0;
}

static PyObject *
wl_finish(struct wl_operation *operation, PyObject *result)
{
    if (!operation->begun)
        return result;
    PyObject *primary = PyErr_GetRaisedException();
    if (lifetime.busy || PyThreadState_Get() != operation->thread ||
        PyThread_tss_get(&lifetime_operation_key) != operation || !lifetime.outstanding) {
        Py_XDECREF(result);
        result = NULL;
        wl_python_failure();
    }
    lifetime.busy = state.lifetime_operation = 1;
    struct wl_record record = wl_record_open();
    wl_tuple(&record, 9);
    wl_unsigned(&record, operation->identity);
    wl_tag(&record, result == NULL ? WL_FALSE : WL_TRUE);
    wl_unsigned(&record, (uint64_t)state.phase);
    wl_unsigned(&record, state.code_count);
    /* Returned data is copied only when safe. Executable object authority stays
     * in the native registry; a copied type name never registers anything. */
    if (result == NULL)
        wl_tag(&record, WL_NONE);
    else if (operation->result_route != NULL)
        wl_route(&record, operation->result_route);
    else if (PyCode_Check(result))
        wl_code_tree(&record, result);
    else if (PyDict_CheckExact(result))
        wl_mapping(&record, result);
    else if (result == Py_None || PyBool_Check(result) || PyLong_CheckExact(result) ||
               PyUnicode_CheckExact(result) || PyBytes_CheckExact(result) || PyTuple_CheckExact(result)) {
        wl_value(&record, result);
    } else {
        wl_tuple(&record, 2);
        wl_ascii(&record, "non-executable-result-not-snapshotted");
        const char *name = Py_TYPE(result)->tp_name;
        wl_blob(&record, WL_BYTES, name, strlen(name));
    }
    wl_exception(&record, primary);
    wl_tag(&record, record.complete ? WL_TRUE : WL_FALSE);
    wl_tag(&record, state.violated ? WL_TRUE : WL_FALSE);
    wl_ascii(&record, state.first_failure);
    int retained = wl_exchange(WL_RESULT, &record);
    if (PyThread_tss_set(&lifetime_operation_key, operation->parent) != 0)
        _exit(125); /* A stack frame must never remain reachable after return. */
    --lifetime.outstanding;
    operation->begun = 0;
    if (retained < 0) {
        Py_XDECREF(result);
        result = NULL;
        wl_python_failure();
    }
    lifetime.busy = state.lifetime_operation = 0;
    if (primary != NULL) {
        /* Original compiler/provider exception remains the raised exception.
         * Stream failure is separately sticky and retained by the receiver. */
        PyErr_Clear();
        PyErr_SetRaisedException(primary);
    }
    return result;
}

static void
wl_at_exit(void)
{
    if (!lifetime.attached || lifetime.descriptor < 0)
        return;
    /* After Python finalization: only C-owned state and direct syscalls below. */
    struct wl_record record = wl_record_open();
    wl_tuple(&record, 7);
    wl_ascii(&record, "native-finalized");
    wl_unsigned(&record, (uint64_t)state.phase);
    wl_tag(&record, state.violated ? WL_TRUE : WL_FALSE);
    wl_ascii(&record, state.first_failure);
    wl_unsigned(&record, lifetime.outstanding);
    wl_unsigned(&record, state.code_count);
    wl_unsigned(&record, lifetime.sequence);
    int result = wl_exchange(WL_TERMINAL, &record);
    if (wl_close(lifetime.descriptor) < 0)
        result = -1;
    lifetime.descriptor = -1;
    if (result < 0 || lifetime.outstanding || lifetime.failed || state.violated) {
        const char message[] = "WORLDLINE_NATIVE_LIFETIME_FAILED at native finalization\n";
        (void)write(STDERR_FILENO, message, sizeof(message) - 1);
        _exit(125);
    }
}

static PyObject *
attach_lifetime(PyObject *self, PyObject *args)
{
    (void)self;
    if (state.phase != BOOTSTRAP || state.violated || lifetime.attempted ||
        lifetime.failed || single_bootstrap_thread() < 0) {
        refuse("native lifetime attachment is one-shot bootstrap only");
        return NULL;
    }
    lifetime.attempted = 1;
    if (!PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 3 ||
        !PyLong_CheckExact(PyTuple_GET_ITEM(args, 0)) ||
        !PyTuple_CheckExact(PyTuple_GET_ITEM(args, 1)) ||
        !PyLong_CheckExact(PyTuple_GET_ITEM(args, 2))) {
        refuse("native lifetime attachment arguments differ");
        return NULL;
    }
    int original = PyLong_AsInt(PyTuple_GET_ITEM(args, 0));
    if (PyErr_Occurred())
        goto failure;
    uint64_t deadline;
    if (PyLong_AsUInt64(PyTuple_GET_ITEM(args, 2), &deadline) < 0)
        goto failure;
    lifetime.deadline_ns = deadline;
    lifetime.busy = 1;
    state.lifetime_operation = 1;
    int domain, type;
    socklen_t domain_size = sizeof(domain), type_size = sizeof(type);
    struct ucred peer;
    socklen_t peer_size = sizeof(peer);
    if (wl_deadline() < 0 ||
        getsockopt(original, SOL_SOCKET, SO_DOMAIN, &domain, &domain_size) < 0 ||
        domain_size != sizeof(domain) || domain != AF_UNIX ||
        getsockopt(original, SOL_SOCKET, SO_TYPE, &type, &type_size) < 0 ||
        type_size != sizeof(type) || type != SOCK_SEQPACKET ||
        getsockopt(original, SOL_SOCKET, SO_PEERCRED, &peer, &peer_size) < 0 ||
        peer_size != sizeof(peer) || peer.pid < 0)
        goto failure;
    lifetime.descriptor = fcntl(original, F_DUPFD_CLOEXEC, 0);
    if (lifetime.descriptor < 0)
        goto failure;
    if (PyThread_tss_create(&lifetime_operation_key) != 0 || Py_AtExit(wl_at_exit) < 0)
        goto failure;
    struct wl_record record = wl_record_open();
    wl_tuple(&record, 3);
    wl_ascii(&record, "native-lifetime-open");
    wl_value(&record, PyTuple_GET_ITEM(args, 1));
    wl_tuple(&record, 3);
    wl_unsigned(&record, (uint64_t)peer.pid);
    wl_unsigned(&record, (uint64_t)peer.uid);
    wl_unsigned(&record, (uint64_t)peer.gid);
    if (!record.complete)
        record.failed = 1;
    if (wl_exchange(WL_HELLO, &record) < 0)
        goto failure;
    lifetime.attached = 1;
    lifetime.busy = 0;
    state.lifetime_operation = 0;
    Py_RETURN_NONE;
failure:
    (void)wl_close(lifetime.descriptor);
    lifetime.descriptor = -1;
    lifetime.busy = 0;
    state.lifetime_operation = 0;
    wl_python_failure();
    return NULL;
}
