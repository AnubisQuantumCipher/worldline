/* Examiner-only native compiler dependency, CPython 3.14 with the GIL.
 *
 * The fixed pre-workload bootstrap supplies the byte inventory. This component
 * does not authenticate that bootstrap, establish lifetime custody, cover every
 * generator/native provider, restrict native memory access, or establish confinement.
 * There is intentionally no Python API for registering a caller's code object.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <marshal.h>
#include <errno.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/sched.h>
#include <linux/seccomp.h>
#include <sys/prctl.h>
#include <sys/syscall.h>

#include "generator_templates.h"

#if PY_MAJOR_VERSION != 3 || PY_MINOR_VERSION != 14
#error "The examiner guard requires reviewed CPython 3.14 headers"
#endif
#ifdef Py_GIL_DISABLED
#error "The examiner guard requires the reviewed GIL-enabled interpreter"
#endif
#if !defined(__linux__) || !defined(__aarch64__) || !defined(__LP64__) || \
    __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "The examiner process filter requires reviewed little-endian Linux AArch64 LP64"
#endif

/* A fixed constructor policy, with no Python mutation or caller-supplied program.
 * Kernel mode/count samples are not independent observations of these opcodes.
 * clone3 arguments are indirect: ENOSYS permits libc's legacy-clone fallback,
 * where actual flags must still describe a thread in the existing thread group.
 */
#define THREAD_FLAGS (CLONE_THREAD | CLONE_VM | CLONE_SIGHAND)
static const struct sock_filter process_filter[] = {
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_execve, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_execveat, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#ifdef SYS_fork
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_fork, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#endif
#ifdef SYS_vfork
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_vfork, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
#endif
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_clone3, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | ENOSYS),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_ptrace, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_clone, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    /* Little-endian AArch64: this is the low word of the flags register. */
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[0])),
    BPF_STMT(BPF_ALU | BPF_AND | BPF_K, THREAD_FLAGS | CSIGNAL),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, THREAD_FLAGS, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
};
_Static_assert(sizeof(process_filter) / sizeof(process_filter[0]) <= USHRT_MAX,
               "process filter length must fit kernel sock_fprog");
static int process_filter_installed;
static int no_new_privs_result;
static long process_filter_result;

static void
process_filter_failure(const char *stage, long result, int saved_errno)
{
    char diagnostic[192];
    int count = snprintf(diagnostic, sizeof(diagnostic),
        "WORLDLINE_NATIVE_FILTER_FAILED stage=%s return=%ld errnoValid=%d errno=%d\n",
        stage, result, result == -1, result == -1 ? saved_errno : 0);
    /* Best-effort bounded diagnostic. Failure to write never continues startup. */
    if (count > 0 && (size_t)count < sizeof(diagnostic))
        (void)write(STDERR_FILENO, diagnostic, (size_t)count);
    _exit(125);
}

static void
install_process_filter(void)
{
    struct sock_fprog program = {
        .len = (unsigned short)(sizeof(process_filter) / sizeof(process_filter[0])),
        .filter = (struct sock_filter *)process_filter
    };
    no_new_privs_result = prctl(PR_SET_NO_NEW_PRIVS, 1UL, 0UL, 0UL, 0UL);
    if (no_new_privs_result != 0)
        process_filter_failure("no-new-privs", no_new_privs_result, errno);
    process_filter_result = syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER,
                                    SECCOMP_FILTER_FLAG_TSYNC, &program);
    /* TSYNC may return a positive failing TID. errno is not valid in that case. */
    if (process_filter_result != 0)
        process_filter_failure("thread-sync-filter", process_filter_result, errno);
    process_filter_installed = 1;
}

static PyObject *
process_filter_status(void)
{
    Py_ssize_t count = (Py_ssize_t)(sizeof(process_filter) / sizeof(process_filter[0]));
    PyObject *rows = PyList_New(count);
    if (rows == NULL)
        return NULL;
    for (Py_ssize_t i = 0; i < count; ++i) {
        const struct sock_filter *row = &process_filter[i];
        PyObject *value = Py_BuildValue("(iiiI)", (int)row->code,
            (int)row->jt, (int)row->jf, row->k);
        if (value == NULL) {
            Py_DECREF(rows);
            return NULL;
        }
        PyList_SET_ITEM(rows, i, value);
    }
    PyObject *result = Py_BuildValue("{s:s,s:s,s:I,s:O,s:i,s:l,s:O,s:O,s:O}",
        "policyId", "worldline-examiner-thread-group-only-v1",
        "architecture", "linux-aarch64-little-endian-lp64",
        "auditArch", (unsigned int)AUDIT_ARCH_AARCH64,
        "installed", process_filter_installed ? Py_True : Py_False,
        "noNewPrivsResult", no_new_privs_result,
        "seccompResult", process_filter_result,
        "threadSync", Py_True, "instructions", rows,
        "independentKernelProgramObservation", Py_False);
    Py_DECREF(rows);
    return result;
}

enum phase { BOOTSTRAP, CONFIGURING, CONFIGURED, ACTIVE, FAILED };
enum route_index { NAMEDTUPLE_ROUTE, DATACLASS_ROUTE, AST_ROUTE, ROUTE_COUNT };

struct source {
    PyObject *path;
    char *bytes;
    Py_ssize_t length;
};

struct cached_snapshot;
struct code_slot {
    PyObject *code;                 /* strong reference, pointer identity */
    struct source *source;          /* stable inventory or owned generation */
    struct cached_snapshot *cached_origin; /* separate trusted startup origin */
};

struct generator_route {
    PyObject *code, *globals;
    struct source *source;
    PyObject *tuple_new, *factory_marker, *recursive_repr, *frozen_error, *builder_type;
    PyObject *ast_base;
    int bound;
};

struct generation {
    struct source source;
    struct source *producer;
    unsigned int route;
    int mode, flags;
    struct generation *next;
};

struct compile_permit {
    PyThreadState *thread;
    PyInterpreterState *interpreter;
    struct source *source;
    int audit_seen;
    int completion_required, audit_completed;
    PyObject *audit_arguments;
    PyFrameObject *parser_frame;
};

enum parse_outcome { PARSE_PENDING, PARSE_ARGUMENT_ERROR, PARSE_COMPILER_ERROR,
                     PARSE_PROTOCOL_ERROR, PARSE_RETURNED };
struct parse_attempt {
    struct source source;
    struct source *producer;
    /* Exact immutable caller values survive normalization and early data errors. */
    PyObject *source_argument, *filename_argument, *mode_argument;
    PyObject *flags_argument, *feature_argument, *optimize_argument;
    int mode, flags, feature_version, optimize;
    enum parse_outcome outcome;
    struct parse_attempt *next;
};

struct guard {
    enum phase phase;
    int installed;
    int violated;
    const char *first_failure;       /* static native strings only */
    PyInterpreterState *interpreter;
    PyThreadState *bootstrap_thread;
    PyObject *run_id;
    struct source *sources;
    size_t source_count;
    struct code_slot *codes;
    size_t code_capacity;
    size_t code_count;
    unsigned long long bootstrap_events;
    unsigned long long active_events;
    unsigned long long compilations;
    unsigned long long generated_compilations;
    struct generator_route routes[ROUTE_COUNT];
    struct generation *generations;
    struct parse_attempt *parses;
    unsigned long long ast_attempts, ast_returns;
    int audit_sealed, registration_pending, registration_seen;
    int probe_pending, probe_seen, tail_verified;
    PyFrameObject *installation_frame;
    PyObject *tail_callback, *add_audit_hook;
    int cached_operation, metadata_operation, frozen_operation;
};

static struct guard state;
static Py_tss_t permit_key = Py_tss_NEEDS_INIT;
static Py_tss_t frozen_permit_key = Py_tss_NEEDS_INIT;

/* These exact declarations are exported in the bound installed
 * internal/pycore_import.h. The public cpython/import.h owns struct _frozen.
 * Alias metadata is a separate CPython facility, not implied by these rows. */
PyAPI_DATA(const struct _frozen *) _PyImport_FrozenBootstrap;
PyAPI_DATA(const struct _frozen *) _PyImport_FrozenStdlib;
PyAPI_DATA(const struct _frozen *) _PyImport_FrozenTest;
static const struct _frozen *frozen_tables[3];

struct frozen_origin {
    struct source raw;             /* marshal bytes, never a source selector */
    PyObject *name;
    const struct _frozen *original;
    size_t table, position;
    int is_package, excluded, invalid;
    PyObject *original_name;       /* NULL until a successful owned association */
    struct frozen_origin *next;
};

enum frozen_outcome { FROZEN_PENDING, FROZEN_LOOKUP_ERROR,
                      FROZEN_PROTOCOL_ERROR, FROZEN_DECODE_ERROR, FROZEN_RETURNED };
enum frozen_availability { AVAIL_UNOBSERVED, AVAIL_ERROR, AVAIL_FALSE,
                           AVAIL_TRUE, AVAIL_INVALID };
struct frozen_attempt {
    PyObject *name, *failure;
    struct frozen_origin *origin;
    enum phase request_phase;
    enum frozen_availability availability;
    enum frozen_outcome outcome;
    struct frozen_attempt *next;
};

struct frozen_permit {
    PyThreadState *thread;
    PyInterpreterState *interpreter;
    struct frozen_origin *origin;
    int audit_seen;
};

static struct frozen_origin *frozen_origins;
static struct frozen_attempt *frozen_attempts;
static PyObject *frozen_available;
static PyObject *frozen_finder, *frozen_finder_keywords;
static size_t frozen_count;
static unsigned long long frozen_requests, frozen_returns;

enum metadata_outcome { METADATA_PENDING, METADATA_ABSENT, METADATA_PROVIDER_ERROR,
                        METADATA_PROTOCOL_ERROR, METADATA_RETURNED };
struct metadata_attempt {
    PyObject *name, *original_name, *failure;
    PyObject *failure_type, *failure_args, *failure_name;
    struct frozen_origin *origin;
    enum phase request_phase;
    enum metadata_outcome outcome;
    struct metadata_attempt *next;
};
static struct metadata_attempt *metadata_attempts;
static unsigned long long metadata_requests, metadata_returns;

enum cached_state { CACHE_ABSENT, CACHE_MALFORMED, CACHE_CAPTURED };
struct cached_snapshot {
    enum cached_state state;
    PyObject *module, *namespace, *owner, *owner_dict, *function, *code, *globals;
    PyObject *defaults, *kwdefaults, *kwdefault_values, *builtins;
    PyObject *namespace_values, *owner_values, *builtin_values;
    PyObject *file, *name, *operation;
    PyObject *helpers[4];
};
struct cached_route_name {
    const char *label, *module, *owner, *member, *qualified, *path, *operation;
};
static const struct cached_route_name cached_names[ROUTE_COUNT] = {
    {"collections.namedtuple", "collections", NULL, "namedtuple", "namedtuple",
     "/usr/lib/python3.14/collections/__init__.py", "eval"},
    {"dataclasses._FuncBuilder.add_fns_to_class", "dataclasses", "_FuncBuilder",
     "add_fns_to_class", "_FuncBuilder.add_fns_to_class",
     "/usr/lib/python3.14/dataclasses.py", "exec"},
    {"ast.parse", "ast", NULL, "parse", "parse", "/usr/lib/python3.14/ast.py", "compile"}
};
static const char *cached_helper_names[ROUTE_COUNT][4] = {
    {NULL, NULL, NULL, NULL},
    {"_HAS_DEFAULT_FACTORY", "recursive_repr", "FrozenInstanceError", "_FuncBuilder"},
    {"AST", NULL, NULL, NULL}
};
static struct cached_snapshot cached_snapshots[ROUTE_COUNT];
enum cached_outcome { CACHE_REQUESTED, CACHE_REFUSED, CACHE_BOUND };
struct cached_attempt {
    PyObject *label, *reference, *failure;
    struct cached_snapshot *snapshot;
    struct source *source;
    enum phase request_phase;
    enum cached_outcome outcome;
    int flags, optimize;
    struct cached_attempt *next;
};
static struct cached_attempt *cached_attempts;
static unsigned long long cached_requests, cached_returns;

static int
native_operation_active(void)
{
    return state.cached_operation || state.metadata_operation || state.frozen_operation ||
           PyThread_tss_get(&permit_key) != NULL ||
           PyThread_tss_get(&frozen_permit_key) != NULL;
}

static PyObject *dict_ascii_value(PyObject *, const char *);
static int capture_cached_generators(void);
static int cached_unchanged(unsigned int, PyObject *);

static int
refuse(const char *reason)
{
    state.violated = 1;
    if (state.first_failure == NULL)
        state.first_failure = reason;
    if (PyThreadState_GetUnchecked() == NULL)
        _exit(125); /* No Python exception API is safe without a thread state. */
    PyErr_SetString(PyExc_PermissionError, reason);
    return -1;
}

static void
latch(const char *reason)
{
    state.violated = 1;
    if (state.first_failure == NULL)
        state.first_failure = reason;
}

static int
count_event(unsigned long long *counter)
{
    if (*counter == ULLONG_MAX)
        return refuse("native observation counter exhausted");
    ++*counter;
    return 0;
}

static int
same_interpreter(void)
{
    PyThreadState *thread = PyThreadState_GetUnchecked();
    if (thread == NULL || PyThreadState_GetInterpreter(thread) != state.interpreter)
        return refuse("native guard interpreter differs");
    return 0;
}

static int
single_bootstrap_thread(void)
{
    PyThreadState *thread = PyThreadState_GetUnchecked();
    if (same_interpreter() < 0)
        return -1;
    if (thread != state.bootstrap_thread ||
        state.interpreter != PyInterpreterState_Main() ||
        PyInterpreterState_Head() != state.interpreter ||
        PyInterpreterState_Next(state.interpreter) != NULL ||
        PyInterpreterState_ThreadHead(state.interpreter) != thread ||
        PyThreadState_Next(thread) != NULL)
        return refuse("native configuration requires the sole bootstrap thread");
    return 0;
}

static size_t
code_position(PyObject *code, size_t capacity)
{
    /* Slots compare addresses; Python code equality/hash never grants authority. */
    return ((uintptr_t)code / sizeof(void *)) % capacity;
}

static struct code_slot *
lookup_code(PyObject *code)
{
    if (state.code_capacity == 0)
        return NULL;
    size_t at = code_position(code, state.code_capacity);
    while (state.codes[at].code != NULL) {
        if (state.codes[at].code == code)
            return &state.codes[at];
        at = (at + 1) % state.code_capacity;
    }
    return NULL;
}

static int
grow_codes(void)
{
    size_t capacity;
    if (state.code_capacity == 0) {
        capacity = 64;
    } else {
        if (state.code_capacity > SIZE_MAX / 2 / sizeof(struct code_slot)) {
            PyErr_NoMemory();
            return -1;
        }
        capacity = state.code_capacity * 2;
    }
    struct code_slot *slots = calloc(capacity, sizeof(*slots));
    if (slots == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    for (size_t i = 0; i < state.code_capacity; ++i) {
        if (state.codes[i].code == NULL)
            continue;
        size_t at = code_position(state.codes[i].code, capacity);
        while (slots[at].code != NULL)
            at = (at + 1) % capacity;
        slots[at] = state.codes[i];
    }
    free(state.codes);
    state.codes = slots;
    state.code_capacity = capacity;
    return 0;
}

static int
retain_code(PyObject *code, struct source *source)
{
    if (!PyCode_Check(code))
        return refuse("native compiler returned a non-code object");
    if (lookup_code(code) != NULL)
        return 0;
    if (state.code_count >= state.code_capacity / 2 && grow_codes() < 0)
        return -1;
    size_t at = code_position(code, state.code_capacity);
    while (state.codes[at].code != NULL)
        at = (at + 1) % state.code_capacity;
    state.codes[at].code = Py_NewRef(code);
    state.codes[at].source = source;
    ++state.code_count;
    return 0;
}

static int
retain_tree_origin(PyObject *code, struct source *source, struct cached_snapshot *cached)
{
    /* Iterative traversal: the native C stack does not grow with nested code. */
    PyObject **pending = NULL;
    size_t used = 0, capacity = 0;
    PyObject *current = code;
    for (;;) {
        if (lookup_code(current) == NULL) {
            if (retain_code(current, source) < 0)
                goto error;
            lookup_code(current)->cached_origin = cached;
            PyObject *constants = ((PyCodeObject *)current)->co_consts;
            if (!PyTuple_CheckExact(constants)) {
                refuse("native compiler constants are not an exact tuple");
                goto error;
            }
            for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(constants); ++i) {
                PyObject *child = PyTuple_GET_ITEM(constants, i);
                if (!PyCode_Check(child) || lookup_code(child) != NULL)
                    continue;
                if (used == capacity) {
                    size_t next = capacity == 0 ? 32 : capacity * 2;
                    if (next < capacity || next > SIZE_MAX / sizeof(*pending)) {
                        PyErr_NoMemory();
                        goto error;
                    }
                    PyObject **grown = realloc(pending, next * sizeof(*pending));
                    if (grown == NULL) {
                        PyErr_NoMemory();
                        goto error;
                    }
                    pending = grown;
                    capacity = next;
                }
                pending[used++] = child;
            }
        }
        if (used == 0)
            break;
        current = pending[--used];
    }
    free(pending);
    return 0;
error:
    free(pending);
    latch("native code retention failed");
    return -1;
}

static int
retain_tree(PyObject *code, struct source *source)
{
    return retain_tree_origin(code, source, NULL);
}

static int
compile_event(PyObject *args)
{
    struct compile_permit *permit = PyThread_tss_get(&permit_key);
    PyThreadState *thread = PyThreadState_GetUnchecked();
    if (permit == NULL || thread != permit->thread ||
        PyThreadState_GetInterpreter(thread) != permit->interpreter ||
        permit->audit_seen || !PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 2)
        return refuse("compilation has no matching native permit");
    PyObject *source = PyTuple_GET_ITEM(args, 0);
    PyObject *path = PyTuple_GET_ITEM(args, 1);
    if (!PyBytes_CheckExact(source) || !PyUnicode_CheckExact(path) ||
        PyBytes_GET_SIZE(source) != permit->source->length ||
        memcmp(PyBytes_AS_STRING(source), permit->source->bytes,
               (size_t)permit->source->length) != 0 ||
        PyUnicode_Compare(path, permit->source->path) != 0)
        return refuse("compile event differs from owned native source");
    permit->audit_seen = 1;
    if (permit->completion_required)
        permit->audit_arguments = Py_NewRef(args);
    return 0;
}

static int
frozen_event(PyObject *args)
{
    struct frozen_permit *permit = PyThread_tss_get(&frozen_permit_key);
    PyThreadState *thread = PyThreadState_GetUnchecked();
    if (state.violated || permit == NULL || thread != permit->thread ||
        PyThreadState_GetInterpreter(thread) != permit->interpreter ||
        PyThread_tss_get(&permit_key) != NULL || permit->audit_seen ||
        !PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 1)
        return refuse("deserialization has no matching native frozen permit");
    PyObject *bytes = PyTuple_GET_ITEM(args, 0);
    if (!PyBytes_CheckExact(bytes) ||
        PyBytes_GET_SIZE(bytes) != permit->origin->raw.length ||
        memcmp(PyBytes_AS_STRING(bytes), permit->origin->raw.bytes,
               (size_t)permit->origin->raw.length) != 0)
        return refuse("marshal event differs from owned native frozen bytes");
    permit->audit_seen = 1;         /* consumed before any later audit callback */
    return 0;
}

static int
audit_hook(const char *event, PyObject *args, void *userdata)
{
    if (userdata != &state)
        return refuse("native audit state identity differs");
    if (state.phase == BOOTSTRAP || state.phase == CONFIGURING) {
        /* Observed trusted startup, not newly bound loader/registry execution. */
        return count_event(&state.bootstrap_events);
    }
    if (count_event(&state.active_events) < 0)
        return -1;
    if (same_interpreter() < 0)
        return -1;
    if (strcmp(event, "sys.addaudithook") == 0 && state.audit_sealed) {
        if (!state.registration_pending || state.registration_seen ||
            PyThreadState_Get() != state.bootstrap_thread ||
            PyEval_GetFrame() != state.installation_frame)
            return refuse("native AST audit completion order is sealed");
        state.registration_pending = 0; /* consumed before any later hook can reenter */
        state.registration_seen = 1;
    }
    if (strcmp(event, "compile") == 0) {
        if (state.violated)
            return refuse("native guard has a retained violation");
        return compile_event(args);
    }
    if (strcmp(event, "marshal.loads") == 0)
        return frozen_event(args);
    if (strcmp(event, "marshal.load") == 0)
        return refuse("stream deserialization is outside native frozen acquisition");
    if (state.phase != ACTIVE && state.phase != FAILED)
        return 0;
    if (strcmp(event, "exec") == 0 || strcmp(event, "function.__new__") == 0) {
        if (state.violated || !PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) < 1 ||
            !PyCode_Check(PyTuple_GET_ITEM(args, 0)) ||
            lookup_code(PyTuple_GET_ITEM(args, 0)) == NULL)
            return refuse("execution code is absent from the native registry");
    }
    if (strcmp(event, "code.__new__") == 0 || strcmp(event, "sys.addaudithook") == 0 ||
        strcmp(event, "cpython.PyInterpreterState_New") == 0)
        return refuse("operation is outside native source compilation");
    return 0;
}

static void
free_sources(struct source *sources, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        Py_XDECREF(sources[i].path);
        free(sources[i].bytes);
    }
    free(sources);
}

static PyObject *
frozen_failure(struct frozen_attempt *attempt, enum frozen_outcome outcome)
{
    attempt->outcome = outcome;
    /* Preserve the actual primary exception, including an earlier audit hook's.
     * This is component retention, not authenticated external custody. */
    PyObject *error = PyErr_GetRaisedException();
    attempt->failure = Py_XNewRef(error);
    PyErr_SetRaisedException(error);
    return NULL;
}

static void
frozen_import_error(const char *format, PyObject *name)
{
    PyObject *message = PyUnicode_FromFormat(format, name);
    if (message == NULL)
        return;                   /* retain the original allocation exception */
    PyErr_SetImportError(message, name, NULL);
    Py_DECREF(message);
}

static int
frozen_tables_unchanged(void)
{
    if (PyImport_FrozenModules != NULL ||
        frozen_tables[0] != _PyImport_FrozenBootstrap ||
        frozen_tables[1] != _PyImport_FrozenStdlib ||
        frozen_tables[2] != _PyImport_FrozenTest)
        return refuse("native built-in frozen table identities changed");
    return 0;
}

static int
capture_frozen(void)
{
    if (frozen_tables_unchanged() < 0)
        return -1;
    struct frozen_origin **tail = &frozen_origins;
    for (size_t table = 0; table < sizeof(frozen_tables) / sizeof(frozen_tables[0]); ++table) {
        if (frozen_tables[table] == NULL)
            return refuse("native built-in frozen table is absent");
        size_t position = 0;
        for (const struct _frozen *row = frozen_tables[table]; row->name != NULL; ++row) {
            if (frozen_count == (size_t)PY_SSIZE_T_MAX || position == SIZE_MAX)
                return refuse("native frozen inventory count exhausted");
            struct frozen_origin *origin = calloc(1, sizeof(*origin));
            if (origin == NULL) {
                PyErr_NoMemory();
                return -1;
            }
            *tail = origin;
            tail = &origin->next;  /* keep partial acquisition on later failure */
            origin->original = row;
            origin->table = table;
            origin->position = position++;
            origin->name = PyUnicode_FromString(row->name);
            origin->raw.path = PyUnicode_FromFormat("<frozen-provider %s>", row->name);
            if (origin->name == NULL || origin->raw.path == NULL)
                return -1;
            Py_ssize_t length = (Py_ssize_t)row->size;
            origin->is_package = row->is_package != 0 || length < 0;
            if (length == PY_SSIZE_T_MIN)
                return refuse("native frozen size cannot be normalized");
            if (length < 0)
                length = -length;
            origin->raw.length = length;
            origin->excluded = row->code == NULL;
            origin->invalid = length == 0 || (!origin->excluded && row->code[0] == 0);
            if (!origin->excluded && length > 0) {
                origin->raw.bytes = malloc((size_t)length);
                if (origin->raw.bytes == NULL) {
                    PyErr_NoMemory();
                    return -1;
                }
                memcpy(origin->raw.bytes, row->code, (size_t)length);
            }
            ++frozen_count;
        }
    }
    PyObject *module = PyImport_ImportModule("_imp");
    if (module == NULL)
        return -1;
    PyObject *available = PyModule_CheckExact(module) ?
        dict_ascii_value(PyModule_GetDict(module), "is_frozen") : NULL;
    int valid = available != NULL && PyCFunction_Check(available) &&
        PyCFunction_GetSelf(available) == module &&
        PyCFunction_GetFlags(available) == METH_O &&
        strcmp(((PyCFunctionObject *)available)->m_ml->ml_name, "is_frozen") == 0;
    if (valid)
        frozen_available = Py_NewRef(available);
    PyObject *finder = PyModule_CheckExact(module) ?
        dict_ascii_value(PyModule_GetDict(module), "find_frozen") : NULL;
    int finder_valid = finder != NULL && PyCFunction_Check(finder) &&
        PyCFunction_GetSelf(finder) == module &&
        PyCFunction_GetFlags(finder) == (METH_FASTCALL | METH_KEYWORDS) &&
        strcmp(((PyCFunctionObject *)finder)->m_ml->ml_name, "find_frozen") == 0;
    if (finder_valid)
        frozen_finder = Py_NewRef(finder);
    Py_DECREF(module);
    if (!valid)
        return refuse("native frozen availability builtin identity differs");
    if (!finder_valid)
        return refuse("native frozen metadata builtin identity differs");
    frozen_finder_keywords = Py_BuildValue("(s)", "withdata");
    if (frozen_finder_keywords == NULL)
        return -1;
    return 0;
}

static struct frozen_origin *
find_owned_frozen(PyObject *name)
{
    for (struct frozen_origin *origin = frozen_origins; origin != NULL; origin = origin->next) {
        int comparison = PyUnicode_Compare(name, origin->name);
        if (comparison == -1 && PyErr_Occurred())
            return NULL;
        if (comparison == 0)
            return origin;
    }
    return NULL;                  /* an inventory miss is not a finder error */
}

/* Caller holds the complete metadata or frozen-code operation. No marshal
 * permit is granted here; no returned buffer becomes a source/code origin. */
static PyObject *
acquire_frozen_metadata(PyObject *name)
{
    struct metadata_attempt *attempt = calloc(1, sizeof(*attempt));
    if (attempt == NULL)
        return PyErr_NoMemory();
    attempt->name = Py_NewRef(name);
    attempt->request_phase = state.phase;
    attempt->next = metadata_attempts;
    metadata_attempts = attempt;
    PyObject *info = NULL, *result = NULL;
    if (count_event(&metadata_requests) < 0 || frozen_tables_unchanged() < 0)
        goto protocol_error;
    struct frozen_origin *origin = find_owned_frozen(name);
    attempt->origin = origin;
    if (PyErr_Occurred())
        goto protocol_error;
    /* An audit observation, never an origin/admission token. Python-emitted
     * events cannot create this native attempt or enter the owned provider. */
    if (PySys_Audit("worldline.frozen_metadata", "O", name) < 0) {
        latch("native frozen metadata audit refused");
        goto protocol_error;      /* preserve the actual hook's primary error */
    }
    if (state.violated) {
        refuse("native frozen metadata audit retained a violation");
        goto protocol_error;
    }
    /* Exact validated FASTCALL|KEYWORDS ABI: one positional name, followed by
     * the value of the held sole keyword. withdata is never positional. */
    PyCFunctionFastWithKeywords finder =
        _PyCFunctionFastWithKeywords_CAST(PyCFunction_GetFunction(frozen_finder));
    PyObject *arguments[] = {name, Py_True};
    info = finder(PyCFunction_GetSelf(frozen_finder), arguments, 1, frozen_finder_keywords);
    if (info == NULL) {
        attempt->outcome = state.violated ? METADATA_PROTOCOL_ERROR : METADATA_PROVIDER_ERROR;
        goto error;               /* retain the provider's ordinary primary error */
    }
    if (state.violated) {
        refuse("native frozen metadata provider completed after a violation");
        goto protocol_error;
    }
    if (info == Py_None) {
        attempt->outcome = METADATA_ABSENT;
        result = Py_NewRef(Py_None);
        goto done;
    }
    if (origin == NULL || !PyTuple_CheckExact(info) || PyTuple_GET_SIZE(info) != 3) {
        refuse("native frozen metadata lacks an owned provider result");
        goto protocol_error;
    }
    PyObject *data = PyTuple_GET_ITEM(info, 0);
    PyObject *package = PyTuple_GET_ITEM(info, 1);
    PyObject *original_name = PyTuple_GET_ITEM(info, 2);
    if (!Py_IS_TYPE(data, &PyMemoryView_Type) || !PyBool_Check(package) ||
        (original_name != Py_None && !PyUnicode_CheckExact(original_name))) {
        refuse("native frozen metadata result types differ");
        goto protocol_error;
    }
    const Py_buffer *buffer = PyMemoryView_GET_BUFFER(data);
    if (origin->excluded || origin->invalid || buffer->buf == NULL ||
        !buffer->readonly || buffer->ndim != 1 || buffer->itemsize != 1 ||
        !PyBuffer_IsContiguous(buffer, 'C') || buffer->len != origin->raw.length ||
        memcmp(buffer->buf, origin->raw.bytes, (size_t)origin->raw.length) != 0 ||
        (package == Py_True) != origin->is_package) {
        refuse("native frozen metadata differs from owned bytes or package");
        goto protocol_error;
    }
    attempt->original_name = original_name == Py_None ? Py_NewRef(Py_None) :
        PyUnicode_FromKindAndData(PyUnicode_KIND(original_name), PyUnicode_DATA(original_name),
                                 PyUnicode_GET_LENGTH(original_name));
    if (attempt->original_name == NULL)
        goto protocol_error;
    if (origin->original_name != NULL) {
        int equal = origin->original_name == Py_None || original_name == Py_None ?
            origin->original_name == original_name :
            PyUnicode_Compare(origin->original_name, original_name) == 0;
        if (PyErr_Occurred() || !equal) {
            refuse("native frozen original-name association changed");
            goto protocol_error;
        }
    } else {
        origin->original_name = Py_NewRef(attempt->original_name);
    }
    result = Py_BuildValue("{s:O,s:O,s:O}", "name", origin->name,
                          "isPackage", package, "originalName", attempt->original_name);
    if (result == NULL)
        goto protocol_error;
    attempt->outcome = METADATA_RETURNED;
done:
    Py_DECREF(info);
    if (state.violated) {
        info = NULL;
        refuse("native frozen metadata cleanup observed a violation");
        goto protocol_error;
    }
    if (attempt->outcome == METADATA_RETURNED && count_event(&metadata_returns) < 0) {
        info = NULL;
        goto protocol_error;
    }
    return result;
protocol_error:
    attempt->outcome = METADATA_PROTOCOL_ERROR;
error:;
    PyObject *primary = PyErr_GetRaisedException();
    Py_XDECREF(info);
    Py_XDECREF(result);
    attempt->failure = Py_XNewRef(primary);
    /* Snapshot ordinary immutable facts now, before the raised exception is
     * returned to Python and its writable attributes can change. NULL fields
     * remain explicit if allocation/unsupported values prevented a copy. */
    if (primary != NULL && PyExceptionInstance_Check(primary)) {
        attempt->failure_type = PyUnicode_FromString(Py_TYPE(primary)->tp_name);
        PyObject *args = ((PyBaseExceptionObject *)primary)->args;
        if (args != NULL && PyTuple_CheckExact(args)) {
            int strings = 1;
            for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(args); ++i)
                if (!PyUnicode_CheckExact(PyTuple_GET_ITEM(args, i)))
                    strings = 0;
            if (strings)
                attempt->failure_args = Py_NewRef(args);
        }
        PyObject *exception_name = Py_None;
        if (Py_IS_TYPE(primary, (PyTypeObject *)PyExc_ImportError)) {
            PyObject *held_name = ((PyImportErrorObject *)primary)->name;
            if (held_name != NULL)
                exception_name = held_name;
        }
        if (exception_name == Py_None || PyUnicode_CheckExact(exception_name))
            attempt->failure_name = Py_NewRef(exception_name);
    }
    PyErr_Clear();                /* snapshot allocation cannot replace primary */
    PyErr_SetRaisedException(primary);
    return NULL;
}

static PyObject *
frozen_metadata(PyObject *self, PyObject *name)
{
    (void)self;
    if (same_interpreter() < 0)
        return NULL;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated ||
        native_operation_active() || !PyUnicode_CheckExact(name)) {
        refuse("native frozen metadata requires a clean non-reentrant selector");
        return NULL;
    }
    state.metadata_operation = 1;
    PyObject *result = acquire_frozen_metadata(name);
    state.metadata_operation = 0;
    return result;
}

static PyObject *
metadata_observations_owned(void)
{
    static const char *outcomes[] = {"pending", "absent", "provider-error",
                                     "protocol-error", "returned"};
    static const char *phases[] = {"bootstrap", "configuring", "configured", "active", "failed"};
    PyObject *rows = PyList_New(0);
    if (rows == NULL)
        return NULL;
    for (struct metadata_attempt *attempt = metadata_attempts;
         attempt != NULL; attempt = attempt->next) {
        PyObject *row = Py_BuildValue("{s:O,s:s,s:s,s:O,s:O,s:O,s:O,s:O,s:O}",
            "name", attempt->name, "phase", phases[attempt->request_phase],
            "outcome", outcomes[attempt->outcome],
            "ownedOrigin", attempt->origin == NULL ? Py_False : Py_True,
            "originalName", attempt->original_name == NULL ? Py_None : attempt->original_name,
            "exceptionType", attempt->failure_type == NULL ? Py_None : attempt->failure_type,
            "exceptionName", attempt->failure_name == NULL ? Py_None : attempt->failure_name,
            "exceptionArgs", attempt->failure_args == NULL ? Py_None : attempt->failure_args,
            "exceptionFactsComplete", attempt->failure_type != NULL &&
                attempt->failure_name != NULL && attempt->failure_args != NULL ? Py_True : Py_False);
        if (row == NULL || PyList_Append(rows, row) < 0) {
            Py_XDECREF(row);
            Py_DECREF(rows);
            return NULL;
        }
        Py_DECREF(row);
    }
    /* Like status(), retained failure facts remain readable after a violation.
     * Every authority-changing operation stays excluded while these copy. */
    return rows;
}

static PyObject *
frozen_metadata_observations(PyObject *self, PyObject *ignored)
{
    (void)self;
    (void)ignored;
    if (same_interpreter() < 0)
        return NULL;
    if (native_operation_active()) {
        refuse("native frozen observation copying is not reentrant");
        return NULL;
    }
    state.metadata_operation = 1;
    PyObject *rows = metadata_observations_owned();
    state.metadata_operation = 0;
    return rows;
}

static PyObject *
frozen_code_owned(PyObject *name)
{
    struct frozen_attempt *attempt = calloc(1, sizeof(*attempt));
    if (attempt == NULL)
        return PyErr_NoMemory();   /* no allocated record for this failure */
    attempt->name = Py_NewRef(name);
    attempt->request_phase = state.phase;
    attempt->availability = AVAIL_UNOBSERVED;
    attempt->next = frozen_attempts;
    frozen_attempts = attempt;
    if (count_event(&frozen_requests) < 0 || frozen_tables_unchanged() < 0)
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    struct frozen_origin *origin = frozen_origins;
    for (; origin != NULL; origin = origin->next) {
        int equal = PyUnicode_Compare(name, origin->name);
        if (equal == -1 && PyErr_Occurred()) {
            latch("native frozen selector comparison failed");
            return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
        }
        if (equal == 0)
            break;
    }
    attempt->origin = origin;
    if (origin == NULL) {
        frozen_import_error("No such frozen object named %R", name);
        return frozen_failure(attempt, FROZEN_LOOKUP_ERROR);
    }
    /* Exact immutable builtin, typed METH_O ABI; Python attribute replacement
     * cannot change availability, and availability never adds an origin. */
    PyCFunction predicate = PyCFunction_GetFunction(frozen_available);
    PyObject *available = predicate(PyCFunction_GetSelf(frozen_available), name);
    if (available == NULL) {
        attempt->availability = AVAIL_ERROR;
        latch("native frozen availability lookup failed");
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    }
    int enabled = available == Py_True;
    int boolean = PyBool_Check(available);
    attempt->availability = !boolean ? AVAIL_INVALID : (enabled ? AVAIL_TRUE : AVAIL_FALSE);
    Py_DECREF(available);
    if (!boolean) {
        refuse("native frozen availability is not a builtin boolean");
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    }
    if (!enabled || origin->excluded || origin->invalid) {
        frozen_import_error("Frozen object named %R is unavailable", name);
        return frozen_failure(attempt, FROZEN_LOOKUP_ERROR);
    }
    PyObject *metadata = acquire_frozen_metadata(name);
    if (metadata == NULL)
        return frozen_failure(attempt, state.violated ? FROZEN_PROTOCOL_ERROR : FROZEN_LOOKUP_ERROR);
    int present = metadata != Py_None;
    Py_DECREF(metadata);
    if (state.violated) {
        refuse("native frozen metadata verification retained a violation");
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    }
    if (!present) {
        frozen_import_error("Frozen object named %R is unavailable", name);
        return frozen_failure(attempt, FROZEN_LOOKUP_ERROR);
    }
    struct frozen_permit permit = {
        .thread = PyThreadState_Get(), .interpreter = state.interpreter,
        .origin = origin, .audit_seen = 0
    };
    if (PyThread_tss_set(&frozen_permit_key, &permit) != 0) {
        refuse("native frozen permit could not be installed");
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    }
    PyObject *code = PyMarshal_ReadObjectFromString(origin->raw.bytes, origin->raw.length);
    if (PyThread_tss_set(&frozen_permit_key, NULL) != 0)
        _exit(125);               /* no dangling stack permit may survive */
    if (code == NULL) {
        latch("native frozen acquisition failed");
        if (!PyErr_Occurred())
            PyErr_SetString(PyExc_TypeError, "native frozen provider returned no code");
        return frozen_failure(attempt, FROZEN_DECODE_ERROR);
    }
    if (!permit.audit_seen || state.violated || !PyCode_Check(code)) {
        Py_DECREF(code);
        refuse("native frozen acquisition lacks a clean actual code result");
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    }
    if (retain_tree(code, &origin->raw) < 0 || count_event(&frozen_returns) < 0) {
        Py_DECREF(code);
        return frozen_failure(attempt, FROZEN_PROTOCOL_ERROR);
    }
    attempt->outcome = FROZEN_RETURNED;
    return code;
}

static PyObject *
frozen_code(PyObject *self, PyObject *name)
{
    (void)self;
    if (same_interpreter() < 0)
        return NULL;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated ||
        native_operation_active() || !PyUnicode_CheckExact(name)) {
        refuse("native frozen acquisition requires a clean non-reentrant selector");
        return NULL;
    }
    state.frozen_operation = 1;
    PyObject *result = frozen_code_owned(name);
    if (result != NULL && state.violated) {
        Py_DECREF(result);
        result = NULL;
        refuse("native frozen acquisition cleanup retained a violation");
    }
    state.frozen_operation = 0;
    return result;
}

static PyObject *
configure(PyObject *self, PyObject *args)
{
    (void)self;
    if (state.phase != BOOTSTRAP || state.violated) {
        refuse("native configuration is one-shot");
        return NULL;
    }
    state.phase = CONFIGURING;
    struct source *sources = NULL;
    size_t count = 0;
    PyObject *run = NULL;
    if (single_bootstrap_thread() < 0)
        goto error;
    if (!PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 2 ||
        !PyUnicode_CheckExact(PyTuple_GET_ITEM(args, 0)) ||
        !PyTuple_CheckExact(PyTuple_GET_ITEM(args, 1))) {
        refuse("configuration requires exact run string and source tuple");
        goto error;
    }
    PyObject *run_arg = PyTuple_GET_ITEM(args, 0);
    PyObject *rows = PyTuple_GET_ITEM(args, 1);
    if (PyUnicode_GET_LENGTH(run_arg) == 0 || PyTuple_GET_SIZE(rows) == 0) {
        refuse("native configuration is empty");
        goto error;
    }
    run = PyUnicode_FromKindAndData(PyUnicode_KIND(run_arg), PyUnicode_DATA(run_arg),
                                   PyUnicode_GET_LENGTH(run_arg));
    if (run == NULL)
        goto error;
    count = (size_t)PyTuple_GET_SIZE(rows);
    if (count > SIZE_MAX / sizeof(*sources)) {
        PyErr_NoMemory();
        goto error;
    }
    sources = calloc(count, sizeof(*sources));
    if (sources == NULL) {
        PyErr_NoMemory();
        goto error;
    }
    for (size_t i = 0; i < count; ++i) {
        PyObject *row = PyTuple_GET_ITEM(rows, (Py_ssize_t)i);
        if (!PyTuple_CheckExact(row) || PyTuple_GET_SIZE(row) != 2 ||
            !PyUnicode_CheckExact(PyTuple_GET_ITEM(row, 0)) ||
            !PyBytes_CheckExact(PyTuple_GET_ITEM(row, 1))) {
            refuse("native source rows require exact path string and bytes");
            goto error;
        }
        PyObject *path = PyTuple_GET_ITEM(row, 0);
        PyObject *content = PyTuple_GET_ITEM(row, 1);
        Py_ssize_t length;
        const char *text = PyUnicode_AsUTF8AndSize(path, &length);
        if (text == NULL)
            goto error;
        if (length == 0 || text[0] != '/' || memchr(text, '\0', (size_t)length) != NULL) {
            refuse("native source path must be an absolute NUL-free string");
            goto error;
        }
        for (size_t previous = 0; previous < i; ++previous) {
            if (PyUnicode_Compare(path, sources[previous].path) == 0) {
                refuse("duplicate native source path");
                goto error;
            }
        }
        sources[i].path = PyUnicode_FromKindAndData(
            PyUnicode_KIND(path), PyUnicode_DATA(path), PyUnicode_GET_LENGTH(path));
        if (sources[i].path == NULL)
            goto error;
        sources[i].length = PyBytes_GET_SIZE(content);
        if ((size_t)sources[i].length == SIZE_MAX) {
            PyErr_NoMemory();
            goto error;
        }
        sources[i].bytes = malloc((size_t)sources[i].length + 1);
        if (sources[i].bytes == NULL) {
            PyErr_NoMemory();
            goto error;
        }
        memcpy(sources[i].bytes, PyBytes_AS_STRING(content), (size_t)sources[i].length);
        sources[i].bytes[sources[i].length] = '\0';
    }
    if (capture_cached_generators() < 0 || capture_frozen() < 0)
        goto error;
    state.sources = sources;
    state.source_count = count;
    state.run_id = run;
    state.phase = CONFIGURED;
    Py_RETURN_NONE;
error:
    state.phase = FAILED;
    latch("native configuration failed");
    if (sources != NULL)
        free_sources(sources, count);
    Py_XDECREF(run);
    return NULL;
}

static PyObject *
compile_owned_internal(struct source *source, int mode, int compiler_flags,
                       int optimize, int cached)
{
    if (same_interpreter() < 0)
        return NULL;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated) {
        refuse("native compilation requires configured owned source");
        return NULL;
    }
    if (PyThread_tss_get(&permit_key) != NULL ||
        PyThread_tss_get(&frozen_permit_key) != NULL ||
        state.metadata_operation || state.frozen_operation ||
        (state.cached_operation && !cached)) {
        refuse("native compilation is not reentrant");
        return NULL;
    }
    if (memchr(source->bytes, '\0', (size_t)source->length) != NULL) {
        latch("owned source contains a NUL byte");
        PyErr_SetString(PyExc_SyntaxError, "source code string cannot contain null bytes");
        return NULL;
    }
    struct compile_permit permit = {
        .thread = PyThreadState_Get(), .interpreter = state.interpreter,
        .source = source, .audit_seen = 0
    };
    if (PyThread_tss_set(&permit_key, &permit) != 0) {
        refuse("native compilation permit could not be installed");
        return NULL;
    }
    PyCompilerFlags flags = {.cf_flags = compiler_flags};
    PyObject *code = Py_CompileStringObject(source->bytes, source->path,
                                           mode, &flags, optimize);
    /* No code is returned or registered while the compilation permit is live. */
    if (PyThread_tss_set(&permit_key, NULL) != 0) {
        /* A dangling stack permit cannot remain reachable. End this process. */
        _exit(125);
    }
    if (code == NULL) {
        latch("native compilation failed");
        return NULL;                /* preserve the actual compiler exception */
    }
    if (!permit.audit_seen || state.violated) {
        Py_DECREF(code);
        refuse("native compilation lacks a clean matching audit event");
        return NULL;
    }
    if (retain_tree(code, source) < 0 || count_event(&state.compilations) < 0) {
        Py_DECREF(code);
        return NULL;
    }
    return code;
}

static PyObject *
compile_owned(struct source *source, int mode, int compiler_flags)
{
    return compile_owned_internal(source, mode, compiler_flags, -1, 0);
}

static PyObject *
compile_source(PyObject *self, PyObject *path)
{
    (void)self;
    if (same_interpreter() < 0)
        return NULL;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated ||
        !PyUnicode_CheckExact(path)) {
        refuse("native compilation requires configured owned source");
        return NULL;
    }
    if (native_operation_active()) {
        refuse("native compilation is not reentrant");
        return NULL;
    }
    for (size_t index = 0; index < state.source_count; ++index)
        if (PyUnicode_Compare(path, state.sources[index].path) == 0)
            return compile_owned(&state.sources[index], Py_file_input, 0);
    refuse("source selector is absent from the native inventory");
    return NULL;
}

static PyObject *namedtuple_eval(PyObject *, PyObject *);
static PyObject *dataclass_exec(PyObject *, PyObject *);
static PyObject *ast_compile(PyObject *, PyObject *, PyObject *);
static PyMethodDef generator_methods[] = {
    {"_namedtuple_eval", namedtuple_eval, METH_VARARGS, "Execute an exact bound namedtuple template."},
    {"_dataclass_exec", dataclass_exec, METH_VARARGS, "Execute an exact bound dataclass template."},
    {"_ast_compile", (PyCFunction)(void (*)(void))ast_compile, METH_VARARGS | METH_KEYWORDS,
     "Parse through the bound AST route without granting executable code authority."}
};

/* Authority lookup must never ask a stored arbitrary key for rich equality. */
static PyObject *
dict_ascii_value(PyObject *dictionary, const char *name)
{
    if (!PyDict_CheckExact(dictionary))
        return NULL;
    Py_ssize_t position = 0;
    PyObject *key, *value;
    while (PyDict_Next(dictionary, &position, &key, &value))
        if (PyUnicode_CheckExact(key) && template_word(key, name))
            return value;
    return NULL;
}

static int
dict_has_only_exact_string_keys(PyObject *dictionary)
{
    Py_ssize_t position = 0;
    PyObject *key, *value;
    if (!PyDict_CheckExact(dictionary))
        return 0;
    while (PyDict_Next(dictionary, &position, &key, &value))
        if (!PyUnicode_CheckExact(key))
            return 0;
    return 1;
}

static void
clear_route(struct generator_route *route)
{
    Py_XDECREF(route->code);
    Py_XDECREF(route->globals);
    Py_XDECREF(route->tuple_new);
    Py_XDECREF(route->factory_marker);
    Py_XDECREF(route->recursive_repr);
    Py_XDECREF(route->frozen_error);
    Py_XDECREF(route->builder_type);
    Py_XDECREF(route->ast_base);
    memset(route, 0, sizeof(*route));
}

static PyObject *
ast_audit_tail(PyObject *self, PyObject *args)
{
    (void)self;
    if (!PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 2 ||
        !PyUnicode_CheckExact(PyTuple_GET_ITEM(args, 0)) ||
        !PyTuple_CheckExact(PyTuple_GET_ITEM(args, 1))) {
        refuse("native audit completion callback arguments differ");
        return NULL;
    }
    PyObject *event = PyTuple_GET_ITEM(args, 0);
    PyObject *arguments = PyTuple_GET_ITEM(args, 1);
    if (template_word(event, "worldline.ast.audit_tail_probe")) {
        if (!state.probe_pending || state.probe_seen || state.violated ||
            PyTuple_GET_SIZE(arguments) != 0 ||
            PyThreadState_Get() != state.bootstrap_thread ||
            PyThreadState_GetInterpreter(PyThreadState_Get()) != state.interpreter ||
            PyEval_GetFrame() != state.installation_frame) {
            refuse("native AST completion installation probe differs");
            return NULL;
        }
        state.probe_pending = 0;
        state.probe_seen = 1;
    } else if (template_word(event, "compile")) {
        struct compile_permit *permit = PyThread_tss_get(&permit_key);
        if (permit != NULL && permit->completion_required) {
            if (!state.tail_verified || state.violated || !permit->audit_seen ||
                permit->audit_completed || arguments != permit->audit_arguments ||
                PyThreadState_Get() != permit->thread ||
                PyThreadState_GetInterpreter(PyThreadState_Get()) != permit->interpreter ||
                PyEval_GetFrame() != permit->parser_frame) {
                refuse("native AST audit completion identity differs");
                return NULL;
            }
            permit->audit_completed = 1;
        }
    }
    Py_RETURN_NONE;                /* fixed C callback, no later user work */
}

static PyMethodDef audit_tail_method = {
    "_ast_audit_completion", ast_audit_tail, METH_VARARGS,
    "Private native audit completion observer."
};

static int
install_ast_audit_tail(void)
{
    if (state.audit_sealed || state.tail_callback != NULL || state.violated ||
        single_bootstrap_thread() < 0)
        return refuse("native AST audit completion binding is one-shot");
    PyObject *module = PyImport_ImportModule("sys");
    if (module == NULL)
        return -1;
    PyObject *registration = PyModule_CheckExact(module) ?
        dict_ascii_value(PyModule_GetDict(module), "addaudithook") : NULL;
    int valid = registration != NULL && PyCFunction_Check(registration) &&
        PyCFunction_GetSelf(registration) == module &&
        PyCFunction_GetFlags(registration) == (METH_FASTCALL | METH_KEYWORDS) &&
        strcmp(((PyCFunctionObject *)registration)->m_ml->ml_name, "addaudithook") == 0;
    if (valid)
        state.add_audit_hook = Py_NewRef(registration);
    Py_DECREF(module);
    if (!valid)
        return refuse("AST audit registration is not the trusted sys builtin");
    state.tail_callback = PyCFunction_NewEx(&audit_tail_method, NULL, NULL);
    if (state.tail_callback == NULL)
        return -1;
    PyFrameObject *frame = PyEval_GetFrame();
    if (frame == NULL)
        return refuse("AST audit registration has no trusted bootstrap frame");
    state.installation_frame = (PyFrameObject *)Py_NewRef(frame);
    state.audit_sealed = 1;        /* also retained on every partial-failure path */
    state.registration_pending = 1;
    /* Pinned generated FASTCALL|KEYWORDS signature; no vectorcall profile hook. */
    PyCFunctionFastWithKeywords register_hook =
        _PyCFunctionFastWithKeywords_CAST(PyCFunction_GetFunction(state.add_audit_hook));
    PyObject *registration_args[] = {state.tail_callback};
    PyObject *result = register_hook(PyCFunction_GetSelf(state.add_audit_hook),
                                     registration_args, 1, NULL);
    state.registration_pending = 0;
    int success = 0;
    if (result == NULL)
        goto done;
    valid = result == Py_None && state.registration_seen && !state.violated;
    Py_DECREF(result);
    if (!valid) {
        refuse("native AST audit registration did not complete cleanly");
        goto done;
    }
    /* sys.addaudithook may suppress an earlier hook's Exception. Observe actual
     * installation, rather than treating a returned None as acknowledgement. */
    state.probe_pending = 1;
    if (PySys_Audit("worldline.ast.audit_tail_probe", NULL) < 0)
        goto done;
    if (!state.probe_seen || state.violated) {
        refuse("native AST audit completion hook installation was not observed");
        goto done;
    }
    state.tail_verified = 1;
    success = 1;
done:
    state.probe_pending = 0;
    Py_CLEAR(state.installation_frame);
    if (!success)
        latch("native AST audit completion installation failed");
    return success ? 0 : -1;
}

static PyObject *
bind_generator_internal(PyObject *self, PyObject *args, int cached)
{
    (void)self;
    struct generator_route prepared = {0};
    PyObject *callback = NULL;
    if (state.phase != CONFIGURED || state.violated ||
        PyThread_tss_get(&permit_key) != NULL || PyThread_tss_get(&frozen_permit_key) != NULL ||
        state.metadata_operation || state.frozen_operation ||
        (state.cached_operation && !cached) ||
        single_bootstrap_thread() < 0 ||
        !PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 3) {
        if (!PyErr_Occurred())
            refuse("generator binding requires the configured sole bootstrap thread");
        goto error;
    }
    PyObject *label = PyTuple_GET_ITEM(args, 0);
    PyObject *function = PyTuple_GET_ITEM(args, 1);
    PyObject *path = PyTuple_GET_ITEM(args, 2);
    if (!PyUnicode_CheckExact(label) || !PyFunction_Check(function) || !PyUnicode_CheckExact(path)) {
        refuse("generator binding requires an exact fixed route, function and source selector");
        goto error;
    }
    unsigned int route;
    const char *qualified, *origin, *module_name, *operation;
    if (template_word(label, "collections.namedtuple")) {
        route = 0;
        qualified = "namedtuple";
        origin = "/usr/lib/python3.14/collections/__init__.py";
        module_name = "collections";
        operation = "eval";
    } else if (template_word(label, "dataclasses._FuncBuilder.add_fns_to_class")) {
        route = 1;
        qualified = "_FuncBuilder.add_fns_to_class";
        origin = "/usr/lib/python3.14/dataclasses.py";
        module_name = "dataclasses";
        operation = "exec";
    } else if (template_word(label, "ast.parse")) {
        route = AST_ROUTE;
        qualified = "parse";
        origin = "/usr/lib/python3.14/ast.py";
        module_name = "ast";
        operation = "compile";
    } else {
        refuse("generator route is not an installed template");
        goto error;
    }
    PyObject *code = PyFunction_GET_CODE(function);
    PyObject *globals = PyFunction_GET_GLOBALS(function);
    struct code_slot *slot = lookup_code(code);
    if (state.routes[route].bound || slot == NULL || !dict_has_only_exact_string_keys(globals) ||
        !template_word(path, origin) || !template_equal(slot->source->path, path) ||
        !template_word(((PyCodeObject *)code)->co_qualname, qualified)) {
        refuse("generator origin is not the unbound exact owned stdlib route");
        goto error;
    }
    PyObject *file = dict_ascii_value(globals, "__file__");
    PyObject *name = dict_ascii_value(globals, "__name__");
    if (file == NULL || name == NULL || !PyUnicode_CheckExact(file) ||
        !PyUnicode_CheckExact(name) || !template_equal(file, path) ||
        !template_word(name, module_name)) {
        refuse("generator module identity differs from its owned source");
        goto error;
    }
    /* A previously installed Python replacement is not silently adopted. */
    PyObject *previous = dict_ascii_value(globals, operation);
    if (previous != NULL && previous != dict_ascii_value(PyEval_GetBuiltins(), operation)) {
        refuse("generator operation was replaced before native binding");
        goto error;
    }
    prepared.code = Py_NewRef(code);
    prepared.globals = Py_NewRef(globals);
    prepared.source = slot->source;
    if (route == 0) {
        prepared.tuple_new = PyObject_GetAttrString((PyObject *)&PyTuple_Type, "__new__");
        if (prepared.tuple_new == NULL)
            goto error;
    } else if (route == DATACLASS_ROUTE) {
        PyObject *marker = dict_ascii_value(globals, "_HAS_DEFAULT_FACTORY");
        PyObject *decorator = dict_ascii_value(globals, "recursive_repr");
        PyObject *exception = dict_ascii_value(globals, "FrozenInstanceError");
        PyObject *builder = dict_ascii_value(globals, "_FuncBuilder");
        if (marker == NULL || decorator == NULL || !PyFunction_Check(decorator) ||
            exception == NULL || !PyExceptionClass_Check(exception) ||
            builder == NULL || !PyType_Check(builder)) {
            refuse("dataclass bootstrap operands are incomplete");
            goto error;
        }
        prepared.factory_marker = Py_NewRef(marker);
        prepared.recursive_repr = Py_NewRef(decorator);
        prepared.frozen_error = Py_NewRef(exception);
        prepared.builder_type = Py_NewRef(builder);
    } else {
        /* _ast was imported by the exact owned ast.py during trusted bootstrap. */
        PyObject *module = PyImport_ImportModule("_ast");
        if (module == NULL)
            goto error;
        PyObject *base = PyModule_CheckExact(module) ?
            dict_ascii_value(PyModule_GetDict(module), "AST") : NULL;
        int valid = base != NULL && PyType_Check(base) &&
            dict_ascii_value(globals, "AST") == base;
        if (valid)
            prepared.ast_base = Py_NewRef(base);
        Py_DECREF(module);
        if (!valid) {
            refuse("AST bootstrap base differs from the native AST module");
            goto error;
        }
        if (install_ast_audit_tail() < 0)
            goto error;
    }
    callback = PyCFunction_NewEx(&generator_methods[route], NULL, NULL);
    if (callback == NULL || (cached && !cached_unchanged(route, NULL))) {
        if (!PyErr_Occurred())
            refuse("cached generator changed during binding callbacks");
        goto error;
    }
    if (PyDict_SetItemString(globals, operation, callback) < 0)
        goto error;
    if (cached && !cached_unchanged(route, callback)) {
        if (!PyErr_Occurred())
            refuse("cached generator changed at binding commit");
        goto error;
    }
    prepared.bound = 1;
    state.routes[route] = prepared;
    Py_DECREF(callback);
    Py_RETURN_NONE;
error:
    clear_route(&prepared);
    Py_XDECREF(callback);
    latch("native generator binding failed");
    return NULL;
}

static PyObject *
bind_generator(PyObject *self, PyObject *args)
{
    return bind_generator_internal(self, args, 0);
}

static int
capture_cached_generators(void)
{
    PyObject *modules = PyImport_GetModuleDict();
    if (!PyDict_CheckExact(modules))
        return refuse("native bootstrap module inventory is not an exact dictionary");
    for (unsigned int route = 0; route < ROUTE_COUNT; ++route) {
        struct cached_snapshot *snapshot = &cached_snapshots[route];
        const struct cached_route_name *name = &cached_names[route];
        PyObject *module = dict_ascii_value(modules, name->module);
        if (module == NULL) {
            snapshot->state = CACHE_ABSENT;
            continue;
        }
        snapshot->state = CACHE_MALFORMED;
        snapshot->module = Py_NewRef(module);
        if (!PyModule_CheckExact(module))
            continue;
        PyObject *namespace = PyModule_GetDict(module);
        snapshot->namespace = Py_NewRef(namespace);
        if (!dict_has_only_exact_string_keys(namespace))
            continue;
        PyObject *owner_dict = namespace;
        if (name->owner != NULL) {
            PyObject *owner = dict_ascii_value(namespace, name->owner);
            snapshot->owner = Py_XNewRef(owner);
            if (owner == NULL || !Py_IS_TYPE(owner, &PyType_Type))
                continue;
            owner_dict = ((PyTypeObject *)owner)->tp_dict;
        }
        if (!dict_has_only_exact_string_keys(owner_dict))
            continue;
        snapshot->owner_dict = Py_NewRef(owner_dict);
        PyObject *function = dict_ascii_value(owner_dict, name->member);
        snapshot->function = Py_XNewRef(function);
        if (function == NULL || !PyFunction_Check(function) ||
            PyFunction_GET_GLOBALS(function) != namespace ||
            PyFunction_GET_CLOSURE(function) != NULL)
            continue;
        snapshot->code = Py_NewRef(PyFunction_GET_CODE(function));
        snapshot->globals = Py_NewRef(PyFunction_GET_GLOBALS(function));
        snapshot->builtins = Py_NewRef(((PyFunctionObject *)function)->func_builtins);
        if (!dict_has_only_exact_string_keys(snapshot->builtins))
            continue;
        snapshot->namespace_values = PyDict_Copy(namespace);
        snapshot->owner_values = PyDict_Copy(owner_dict);
        snapshot->builtin_values = PyDict_Copy(snapshot->builtins);
        if (snapshot->namespace_values == NULL || snapshot->owner_values == NULL ||
            snapshot->builtin_values == NULL)
            return -1;
        snapshot->defaults = Py_XNewRef(PyFunction_GET_DEFAULTS(function));
        snapshot->kwdefaults = Py_XNewRef(PyFunction_GET_KW_DEFAULTS(function));
        if (snapshot->kwdefaults != NULL) {
            if (!dict_has_only_exact_string_keys(snapshot->kwdefaults))
                continue;
            snapshot->kwdefault_values = PyDict_Copy(snapshot->kwdefaults);
            if (snapshot->kwdefault_values == NULL)
                return -1;
        }
        snapshot->file = Py_XNewRef(dict_ascii_value(namespace, "__file__"));
        snapshot->name = Py_XNewRef(dict_ascii_value(namespace, "__name__"));
        snapshot->operation = Py_XNewRef(dict_ascii_value(namespace, name->operation));
        for (unsigned int i = 0; i < 4; ++i)
            if (cached_helper_names[route][i] != NULL)
                snapshot->helpers[i] = Py_XNewRef(dict_ascii_value(
                    namespace, cached_helper_names[route][i]));
        snapshot->state = CACHE_CAPTURED;
    }
    return 0;
}

static int
cached_dictionary_unchanged(PyObject *dictionary, PyObject *original,
                            const char *operation, PyObject *inserted_callback)
{
    if (!dict_has_only_exact_string_keys(dictionary) || !PyDict_CheckExact(original))
        return 0;
    int inserted = inserted_callback != NULL && dict_ascii_value(original, operation) == NULL;
    if (PyDict_GET_SIZE(dictionary) != PyDict_GET_SIZE(original) + inserted)
        return 0;
    PyObject *key, *value;
    Py_ssize_t position = 0;
    while (PyDict_Next(original, &position, &key, &value)) {
        PyObject *expected = inserted_callback != NULL && template_word(key, operation) ?
            inserted_callback : value;
        if (PyDict_GetItemWithError(dictionary, key) != expected)
            return 0;
    }
    return inserted_callback == NULL || dict_ascii_value(dictionary, operation) == inserted_callback;
}

static int
cached_unchanged(unsigned int route, PyObject *inserted_callback)
{
    struct cached_snapshot *snapshot = &cached_snapshots[route];
    const struct cached_route_name *name = &cached_names[route];
    if (snapshot->state != CACHE_CAPTURED ||
        dict_ascii_value(PyImport_GetModuleDict(), name->module) != snapshot->module ||
        PyModule_GetDict(snapshot->module) != snapshot->namespace ||
        !dict_has_only_exact_string_keys(snapshot->namespace) ||
        !dict_has_only_exact_string_keys(snapshot->owner_dict))
        return 0;
    if (!cached_dictionary_unchanged(snapshot->namespace, snapshot->namespace_values,
                                    name->operation, inserted_callback) ||
        (snapshot->owner_dict != snapshot->namespace &&
         !cached_dictionary_unchanged(snapshot->owner_dict, snapshot->owner_values, NULL, NULL)) ||
        !cached_dictionary_unchanged(snapshot->builtins, snapshot->builtin_values, NULL, NULL))
        return 0;
    if (name->owner != NULL &&
        (dict_ascii_value(snapshot->namespace, name->owner) != snapshot->owner ||
         ((PyTypeObject *)snapshot->owner)->tp_dict != snapshot->owner_dict))
        return 0;
    if (dict_ascii_value(snapshot->owner_dict, name->member) != snapshot->function ||
        PyFunction_GET_CODE(snapshot->function) != snapshot->code ||
        PyFunction_GET_GLOBALS(snapshot->function) != snapshot->globals ||
        ((PyFunctionObject *)snapshot->function)->func_builtins != snapshot->builtins ||
        PyFunction_GET_CLOSURE(snapshot->function) != NULL ||
        PyFunction_GET_DEFAULTS(snapshot->function) != snapshot->defaults ||
        PyFunction_GET_KW_DEFAULTS(snapshot->function) != snapshot->kwdefaults ||
        dict_ascii_value(snapshot->namespace, "__file__") != snapshot->file ||
        dict_ascii_value(snapshot->namespace, "__name__") != snapshot->name ||
        dict_ascii_value(snapshot->namespace, name->operation) !=
            (inserted_callback == NULL ? snapshot->operation : inserted_callback))
        return 0;
    if (snapshot->kwdefaults != NULL) {
        if (!dict_has_only_exact_string_keys(snapshot->kwdefaults) ||
            PyDict_GET_SIZE(snapshot->kwdefaults) != PyDict_GET_SIZE(snapshot->kwdefault_values))
            return 0;
        PyObject *key, *value;
        Py_ssize_t position = 0;
        while (PyDict_Next(snapshot->kwdefault_values, &position, &key, &value)) {
            /* Both dictionaries have exact Unicode keys; no user equality. */
            if (PyDict_GetItemWithError(snapshot->kwdefaults, key) != value)
                return 0;
        }
    }
    for (unsigned int i = 0; i < 4; ++i)
        if (cached_helper_names[route][i] != NULL &&
            dict_ascii_value(snapshot->namespace, cached_helper_names[route][i]) != snapshot->helpers[i])
            return 0;
    return 1;
}

static int cached_constant_equal(PyObject *, PyObject *);

static int
cached_code_equal(PyCodeObject *left, PyCodeObject *right)
{
    if (left->co_argcount != right->co_argcount ||
        left->co_posonlyargcount != right->co_posonlyargcount ||
        left->co_kwonlyargcount != right->co_kwonlyargcount ||
        left->co_stacksize != right->co_stacksize || left->co_flags != right->co_flags ||
        left->co_firstlineno != right->co_firstlineno ||
        left->co_nlocalsplus != right->co_nlocalsplus ||
        left->co_framesize != right->co_framesize || left->co_nlocals != right->co_nlocals ||
        left->co_ncellvars != right->co_ncellvars || left->co_nfreevars != right->co_nfreevars ||
        left->_co_firsttraceable != right->_co_firsttraceable)
        return 0;
    PyObject *a[] = {left->co_consts, left->co_names, left->co_exceptiontable,
        left->co_localsplusnames, left->co_localspluskinds, left->co_filename,
        left->co_name, left->co_qualname, left->co_linetable};
    PyObject *b[] = {right->co_consts, right->co_names, right->co_exceptiontable,
        right->co_localsplusnames, right->co_localspluskinds, right->co_filename,
        right->co_name, right->co_qualname, right->co_linetable};
    for (size_t i = 0; i < sizeof(a) / sizeof(*a); ++i) {
        int equal = cached_constant_equal(a[i], b[i]);
        if (equal != 1)
            return equal;
    }
    /* Logical bytecode, not adaptive instructions, version or runtime caches. */
    PyObject *left_bytes = PyCode_GetCode(left);
    if (left_bytes == NULL)
        return -1;
    PyObject *right_bytes = PyCode_GetCode(right);
    if (right_bytes == NULL) {
        Py_DECREF(left_bytes);
        return -1;
    }
    int equal = cached_constant_equal(left_bytes, right_bytes);
    Py_DECREF(left_bytes);
    Py_DECREF(right_bytes);
    return equal;
}

static int
cached_set_equal(PySetObject *left, PySetObject *right)
{
    if (left->used != right->used)
        return 0;
    if (right->mask < 0 || (size_t)right->mask == SIZE_MAX)
        return refuse("native cached frozen-set layout is invalid");
    unsigned char *matched = calloc((size_t)right->mask + 1, sizeof(*matched));
    if (matched == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    int result = 1;
    /* Direct exact frozen-set tables: no object iterator, equality or hash call. */
    for (Py_ssize_t i = 0; i <= left->mask; ++i) {
        setentry *item = &left->table[i];
        if (item->key == NULL || item->hash == -1)
            continue;
        int found = 0;
        for (Py_ssize_t j = 0; j <= right->mask; ++j) {
            setentry *other = &right->table[j];
            if (matched[j] || other->key == NULL || other->hash == -1)
                continue;
            int equal = cached_constant_equal(item->key, other->key);
            if (equal < 0) {
                result = -1;
                goto done;
            }
            if (equal) {
                matched[j] = 1;
                found = 1;
                break;
            }
        }
        if (!found) {
            result = 0;
            goto done;
        }
    }
done:
    free(matched);
    return result;
}

static int
cached_constant_body(PyObject *left, PyObject *right)
{
    if (left == NULL || right == NULL || Py_TYPE(left) != Py_TYPE(right))
        return 0;
    if (left == Py_None || left == Py_Ellipsis || PyBool_Check(left))
        return left == right;
    if (PyUnicode_CheckExact(left)) {
        int equal = PyUnicode_Compare(left, right);
        return PyErr_Occurred() ? -1 : equal == 0;
    }
    if (PyBytes_CheckExact(left))
        return PyBytes_GET_SIZE(left) == PyBytes_GET_SIZE(right) &&
            memcmp(PyBytes_AS_STRING(left), PyBytes_AS_STRING(right),
                   (size_t)PyBytes_GET_SIZE(left)) == 0;
    if (PyLong_CheckExact(left)) {
        /* Fixed native exact-int comparator; never generic operand dispatch. */
        PyObject *answer = PyLong_Type.tp_richcompare(left, right, Py_EQ);
        if (answer == NULL)
            return -1;
        int equal = answer == Py_True;
        Py_DECREF(answer);
        return equal;
    }
    if (PyFloat_CheckExact(left)) {
        double a = PyFloat_AS_DOUBLE(left), b = PyFloat_AS_DOUBLE(right);
        return memcmp(&a, &b, sizeof(a)) == 0;
    }
    if (PyComplex_CheckExact(left)) {
        Py_complex a = ((PyComplexObject *)left)->cval;
        Py_complex b = ((PyComplexObject *)right)->cval;
        return memcmp(&a.real, &b.real, sizeof(a.real)) == 0 &&
            memcmp(&a.imag, &b.imag, sizeof(a.imag)) == 0;
    }
    if (PyTuple_CheckExact(left)) {
        if (PyTuple_GET_SIZE(left) != PyTuple_GET_SIZE(right))
            return 0;
        for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(left); ++i) {
            int equal = cached_constant_equal(PyTuple_GET_ITEM(left, i), PyTuple_GET_ITEM(right, i));
            if (equal != 1)
                return equal;
        }
        return 1;
    }
    if (PyFrozenSet_CheckExact(left))
        return cached_set_equal((PySetObject *)left, (PySetObject *)right);
    if (PySlice_Check(left)) {
        PySliceObject *a = (PySliceObject *)left, *b = (PySliceObject *)right;
        int equal = cached_constant_equal(a->start, b->start);
        if (equal != 1)
            return equal;
        equal = cached_constant_equal(a->stop, b->stop);
        return equal == 1 ? cached_constant_equal(a->step, b->step) : equal;
    }
    if (PyCode_Check(left))
        return cached_code_equal((PyCodeObject *)left, (PyCodeObject *)right);
    return refuse("unsupported native cached source constant type");
}

static int
cached_constant_equal(PyObject *left, PyObject *right)
{
    if (Py_EnterRecursiveCall(" while comparing native cached source") < 0)
        return -1;
    int result = cached_constant_body(left, right);
    Py_LeaveRecursiveCall();
    return result;
}

static int
cached_reference(PyObject *tree, const char *qualified, PyObject **found)
{
    if (Py_EnterRecursiveCall(" while locating native cached reference") < 0)
        return -1;
    int result = -1;
    PyCodeObject *code = (PyCodeObject *)tree;
    if (template_word(code->co_qualname, qualified)) {
        if (*found != NULL) {
            refuse("native cached source has an ambiguous fixed route");
            goto done;
        }
        *found = Py_NewRef(tree);
    }
    for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(code->co_consts); ++i) {
        PyObject *child = PyTuple_GET_ITEM(code->co_consts, i);
        if (PyCode_Check(child) && cached_reference(child, qualified, found) < 0)
            goto done;
    }
    result = 0;
done:
    Py_LeaveRecursiveCall();
    return result;
}

static PyObject *
bind_cached_generator(PyObject *self, PyObject *label)
{
    (void)self;
    if (state.phase != CONFIGURED || state.violated || native_operation_active() ||
        single_bootstrap_thread() < 0) {
        if (!PyErr_Occurred())
            refuse("cached binding requires the configured sole bootstrap thread");
        return NULL;
    }
    struct cached_attempt *attempt = calloc(1, sizeof(*attempt));
    if (attempt == NULL) {
        latch("native cached attempt retention failed");
        return PyErr_NoMemory();
    }
    attempt->label = Py_NewRef(label);
    attempt->request_phase = state.phase;
    attempt->optimize = -1;
    attempt->next = cached_attempts;
    cached_attempts = attempt;
    state.cached_operation = 1;
    PyObject *tree = NULL, *arguments = NULL, *result = NULL;
    if (count_event(&cached_requests) < 0)
        goto error;
    unsigned int route;
    for (route = 0; route < ROUTE_COUNT; ++route)
        if (PyUnicode_CheckExact(label) && template_word(label, cached_names[route].label))
            break;
    if (route == ROUTE_COUNT) {
        refuse("cached binding requires an exact fixed native label");
        goto error;
    }
    attempt->snapshot = &cached_snapshots[route];
    if (state.routes[route].bound || !cached_unchanged(route, NULL)) {
        refuse("cached bootstrap route is absent, malformed, changed or already bound");
        goto error;
    }
    for (size_t i = 0; i < state.source_count; ++i)
        if (template_word(state.sources[i].path, cached_names[route].path)) {
            attempt->source = &state.sources[i];
            break;
        }
    if (attempt->source == NULL) {
        refuse("cached generator source is absent from the owned inventory");
        goto error;
    }
    /* Retain the actual explicit option passed to this reference compilation. */
    if (PyConfig_GetInt("optimization_level", &attempt->optimize) < 0)
        goto error;
    attempt->flags = 0;
    tree = compile_owned_internal(attempt->source, Py_file_input, attempt->flags,
                                  attempt->optimize, 1);
    if (tree == NULL || cached_reference(tree, cached_names[route].qualified, &attempt->reference) < 0)
        goto error;
    if (attempt->reference == NULL) {
        refuse("owned source lacks the fixed cached generator");
        goto error;
    }
    int equal = cached_constant_equal(attempt->snapshot->code, attempt->reference);
    if (equal != 1) {
        if (equal == 0)
            refuse("cached generator differs from complete owned source metadata");
        goto error;
    }
    if (state.violated || !cached_unchanged(route, NULL)) {
        refuse("cached generator changed during reference compilation");
        goto error;
    }
    /* These exact held pointers, not equal copies or cached siblings, are adopted. */
    if (retain_tree_origin(attempt->snapshot->code, attempt->source, attempt->snapshot) < 0)
        goto error;
    arguments = PyTuple_Pack(3, label, attempt->snapshot->function, attempt->source->path);
    if (arguments == NULL || !cached_unchanged(route, NULL)) {
        if (!PyErr_Occurred())
            refuse("cached generator changed before native route binding");
        goto error;
    }
    result = bind_generator_internal(NULL, arguments, 1);
    if (result == NULL || count_event(&cached_returns) < 0)
        goto error;
    attempt->outcome = CACHE_BOUND;
    state.cached_operation = 0;
    Py_DECREF(tree);
    Py_DECREF(arguments);
    return result;
error:
    attempt->outcome = CACHE_REFUSED;
    latch("native cached generator binding failed");
    /* Clear operation authority before cleanup; preserve the first exception. */
    state.cached_operation = 0;
    PyObject *failure = PyErr_GetRaisedException();
    attempt->failure = Py_XNewRef(failure);
    Py_XDECREF(tree);
    Py_XDECREF(arguments);
    Py_XDECREF(result);
    PyErr_SetRaisedException(failure);
    return NULL;
}

static int
generator_caller(struct generator_route *route, PyFrameObject **result)
{
    if (same_interpreter() < 0)
        return -1;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated ||
        !route->bound || native_operation_active())
        return refuse("native generator requires a clean bound non-reentrant route");
    PyFrameObject *frame = PyEval_GetFrame();
    if (frame == NULL)
        return refuse("native generator has no calling frame");
    PyCodeObject *code = PyFrame_GetCode(frame);
    PyObject *globals = PyFrame_GetGlobals(frame);
    int valid = (PyObject *)code == route->code && globals == route->globals;
    Py_XDECREF(code);
    Py_XDECREF(globals);
    if (!valid)
        return refuse("native generator caller identity differs");
    *result = frame;                /* current executing frame remains live */
    return 0;
}

static int
namedtuple_namespace(struct generator_route *route, PyObject *globals)
{
    if (!dict_has_only_exact_string_keys(globals) || PyDict_Size(globals) != 3 ||
        dict_ascii_value(globals, "_tuple_new") != route->tuple_new)
        return 0;
    PyObject *builtins = dict_ascii_value(globals, "__builtins__");
    PyObject *name = dict_ascii_value(globals, "__name__");
    if (builtins == NULL || !PyDict_CheckExact(builtins) || PyDict_Size(builtins) != 0 ||
        name == NULL || !PyUnicode_CheckExact(name))
        return 0;
    struct template_cursor p;
    if (!template_begin(name, &p) || !template_take(&p, "namedtuple_"))
        return 0;
    PyObject *typename = template_identifier(&p);
    int valid = typename != NULL && p.at == p.end;
    Py_XDECREF(typename);
    return valid;
}

static int
dataclass_operands(struct generator_route *route, PyFrameObject *frame,
                   PyObject *closures, PyObject *globals, PyObject *locals)
{
    PyObject *builder = NULL, *namespace = NULL, *attributes = NULL;
    int valid = 0;
    builder = PyFrame_GetVarString(frame, "self");
    namespace = PyFrame_GetVarString(frame, "ns");
    if (builder == NULL || namespace == NULL ||
        (PyObject *)Py_TYPE(builder) != route->builder_type || namespace != locals)
        goto done;
    /* Bypass a mutable Python __getattribute__; inspect the exact instance dict. */
    attributes = PyObject_GenericGetDict(builder, NULL);
    if (attributes == NULL || !PyDict_CheckExact(attributes) ||
        dict_ascii_value(attributes, "globals") != globals)
        goto done;
    PyObject *values = dict_ascii_value(attributes, "locals");
    if (values == NULL || !PyDict_CheckExact(values))
        goto done;
    if (PyDict_Size(values) != PyList_GET_SIZE(closures))
        goto done;
    Py_ssize_t position = 0, index = 0;
    PyObject *key, *operand;
    while (PyDict_Next(values, &position, &key, &operand)) {
        if (index >= PyList_GET_SIZE(closures) || !PyUnicode_CheckExact(key) ||
            !template_equal(key, PyList_GET_ITEM(closures, index)))
            goto done;
        ++index;
        if ((template_word(key, "__dataclass_builtins_object__") &&
             operand != (PyObject *)&PyBaseObject_Type) ||
            (template_word(key, "__dataclass_HAS_DEFAULT_FACTORY__") && operand != route->factory_marker) ||
            (template_word(key, "__dataclasses_recursive_repr") && operand != route->recursive_repr) ||
            (template_word(key, "FrozenInstanceError") && operand != route->frozen_error))
            goto done;
    }
    valid = index == PyList_GET_SIZE(closures);
done:
    Py_XDECREF(attributes);
    Py_XDECREF(namespace);
    Py_XDECREF(builder);
    return valid;
}

static PyObject *
generated_code(unsigned int route_index, PyObject *text)
{
    struct generator_route *route = &state.routes[route_index];
    Py_ssize_t length;
    const char *bytes = PyUnicode_AsUTF8AndSize(text, &length);
    if (bytes == NULL)
        return NULL;
    if ((size_t)length == SIZE_MAX)
        return PyErr_NoMemory();
    struct generation *generation = calloc(1, sizeof(*generation));
    if (generation == NULL)
        return PyErr_NoMemory();
    generation->source.path = PyUnicode_FromString("<string>");
    generation->source.bytes = malloc((size_t)length + 1);
    if (generation->source.path == NULL || generation->source.bytes == NULL) {
        Py_XDECREF(generation->source.path);
        free(generation->source.bytes);
        free(generation);
        if (!PyErr_Occurred())
            PyErr_NoMemory();
        return NULL;
    }
    memcpy(generation->source.bytes, bytes, (size_t)length);
    generation->source.bytes[length] = '\0';
    generation->source.length = length;
    generation->producer = route->source;
    generation->route = route_index;
    generation->mode = route_index == 0 ? Py_eval_input : Py_file_input;
    generation->flags = (((PyCodeObject *)route->code)->co_flags & PyCF_MASK) | PyCF_SOURCE_IS_UTF8;
    /* Stable separately allocated source; retain attempted inputs even on error. */
    generation->next = state.generations;
    state.generations = generation;
    PyObject *code = compile_owned(&generation->source, generation->mode, generation->flags);
    if (code != NULL && count_event(&state.generated_compilations) < 0)
        Py_CLEAR(code);
    return code;
}

static PyObject *
execute_generator(unsigned int route_index, PyObject *args)
{
    struct generator_route *route = &state.routes[route_index];
    PyFrameObject *frame = NULL;
    if (generator_caller(route, &frame) < 0)
        return NULL;
    Py_ssize_t count = route_index == 0 ? 2 : 3;
    if (!PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != count) {
        refuse("native generator arguments differ from the installed call site");
        return NULL;
    }
    PyObject *source = PyTuple_GET_ITEM(args, 0);
    PyObject *globals = PyTuple_GET_ITEM(args, 1);
    PyObject *locals = route_index == 0 ? globals : PyTuple_GET_ITEM(args, 2);
    int valid = PyUnicode_CheckExact(source) && PyDict_CheckExact(globals) && PyDict_CheckExact(locals);
    if (valid && route_index == 0) {
        valid = template_namedtuple(source) && namedtuple_namespace(route, globals);
    } else if (valid) {
        PyObject *closures = template_dataclass(source);
        valid = closures != NULL && dataclass_operands(route, frame, closures, globals, locals);
        Py_XDECREF(closures);
    }
    if (!valid) {
        if (!PyErr_Occurred())
            refuse("generated source or trusted operands differ from the complete native template");
        else
            latch("native generator validation failed");
        return NULL;
    }
    PyObject *code = generated_code(route_index, source);
    if (code == NULL) {
        latch("native generator compilation failed");
        return NULL;
    }
    if (PyDict_GetItemString(globals, "__builtins__") == NULL &&
        PyDict_SetItemString(globals, "__builtins__", PyEval_GetBuiltins()) < 0) {
        Py_DECREF(code);
        return NULL;
    }
    /* PyEval_EvalCode does not replace builtin exec/eval's audit notification. */
    if (PySys_Audit("exec", "O", code) < 0) {
        Py_DECREF(code);
        return NULL;
    }
    PyObject *result = PyEval_EvalCode(code, globals, locals);
    Py_DECREF(code);
    return result;                  /* eval's lambda or exec's actual None */
}

static PyObject *
namedtuple_eval(PyObject *self, PyObject *args)
{
    (void)self;
    return execute_generator(0, args);
}

static PyObject *
dataclass_exec(PyObject *self, PyObject *args)
{
    (void)self;
    return execute_generator(1, args);
}

static int
ast_integer(PyObject *value, int *result)
{
    if (!PyLong_CheckExact(value) && !PyBool_Check(value))
        return refuse("AST compiler options require built-in integer values");
    *result = PyLong_AsInt(value);
    return PyErr_Occurred() ? -1 : 0;
}

static PyObject *
ast_compile(PyObject *self, PyObject *args, PyObject *keywords)
{
    (void)self;
    struct generator_route *route = &state.routes[AST_ROUTE];
    PyFrameObject *frame = NULL;
    if (generator_caller(route, &frame) < 0)
        return NULL;
    if (!PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 4 ||
        !dict_has_only_exact_string_keys(keywords) || PyDict_Size(keywords) != 2) {
        refuse("AST compiler arguments differ from the installed parse call site");
        return NULL;
    }
    PyObject *source = PyTuple_GET_ITEM(args, 0);
    PyObject *filename = PyTuple_GET_ITEM(args, 1);
    PyObject *mode = PyTuple_GET_ITEM(args, 2);
    PyObject *feature = dict_ascii_value(keywords, "_feature_version");
    PyObject *optimization = dict_ascii_value(keywords, "optimize");
    if ((!PyUnicode_CheckExact(source) && !PyBytes_CheckExact(source)) ||
        !PyUnicode_CheckExact(filename) || !PyUnicode_CheckExact(mode) ||
        feature == NULL || optimization == NULL) {
        refuse("AST route requires exact text/bytes, filename, mode and fixed options");
        return NULL;
    }
    PyObject *flags_argument = PyTuple_GET_ITEM(args, 3);
    if ((!PyLong_CheckExact(flags_argument) && !PyBool_Check(flags_argument)) ||
        (!PyLong_CheckExact(feature) && !PyBool_Check(feature)) ||
        (!PyLong_CheckExact(optimization) && !PyBool_Check(optimization))) {
        refuse("AST compiler options require built-in integer values");
        return NULL;
    }
    struct parse_attempt *attempt = calloc(1, sizeof(*attempt));
    if (attempt == NULL)
        return PyErr_NoMemory();   /* no allocation exists in which to retain this attempt */
    attempt->producer = route->source;
    attempt->source_argument = Py_NewRef(source);
    attempt->filename_argument = Py_NewRef(filename);
    attempt->mode_argument = Py_NewRef(mode);
    attempt->flags_argument = Py_NewRef(flags_argument);
    attempt->feature_argument = Py_NewRef(feature);
    attempt->optimize_argument = Py_NewRef(optimization);
    attempt->next = state.parses;
    state.parses = attempt;
    if (count_event(&state.ast_attempts) < 0) {
        attempt->outcome = PARSE_PROTOCOL_ERROR;
        return NULL;
    }
    int options, feature_version, optimize;
    if (ast_integer(flags_argument, &options) < 0 ||
        ast_integer(feature, &feature_version) < 0 ||
        ast_integer(optimization, &optimize) < 0) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        return NULL;
    }
    if (!(options & PyCF_ONLY_AST) ||
        (options & ~(PyCF_ONLY_AST | PyCF_OPTIMIZED_AST | PyCF_TYPE_COMMENTS))) {
        attempt->outcome = PARSE_PROTOCOL_ERROR;
        refuse("AST route cannot authorize executable compiler flags");
        return NULL;
    }
    int start = template_word(mode, "exec") ? Py_file_input :
        template_word(mode, "eval") ? Py_eval_input :
        template_word(mode, "single") ? Py_single_input :
        template_word(mode, "func_type") ? Py_func_type_input : -1;
    if (start < 0) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        PyErr_SetString(PyExc_ValueError,
            "compile() mode must be 'exec', 'eval', 'single' or 'func_type'");
        return NULL;
    }
    if (optimize < -1 || optimize > 2) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        PyErr_SetString(PyExc_ValueError, "compile(): invalid optimize value");
        return NULL;
    }
    Py_ssize_t length;
    const char *bytes;
    if (PyUnicode_CheckExact(source)) {
        bytes = PyUnicode_AsUTF8AndSize(source, &length);
    } else {
        bytes = PyBytes_AS_STRING(source);
        length = PyBytes_GET_SIZE(source);
    }
    if (bytes == NULL) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        return NULL;
    }
    if ((size_t)length == SIZE_MAX) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        return PyErr_NoMemory();
    }
    attempt->source.path = PyUnicode_FromKindAndData(
        PyUnicode_KIND(filename), PyUnicode_DATA(filename), PyUnicode_GET_LENGTH(filename));
    attempt->source.bytes = malloc((size_t)length + 1);
    if (attempt->source.path == NULL || attempt->source.bytes == NULL) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        if (!PyErr_Occurred())
            PyErr_NoMemory();
        return NULL;
    }
    memcpy(attempt->source.bytes, bytes, (size_t)length);
    attempt->source.bytes[length] = '\0';
    attempt->source.length = length;
    attempt->mode = start;
    attempt->flags = options | PyCF_SOURCE_IS_UTF8 |
        (((PyCodeObject *)route->code)->co_flags & PyCF_MASK) |
        (PyUnicode_CheckExact(source) ? PyCF_IGNORE_COOKIE : 0);
    attempt->feature_version = feature_version >= 0 ? feature_version : PY_MINOR_VERSION;
    attempt->optimize = optimize;
    if (PyUnicode_FindChar(filename, 0, 0, PyUnicode_GET_LENGTH(filename), 1) >= 0) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        PyErr_SetString(PyExc_ValueError, "embedded null character");
        return NULL;
    }
    if (memchr(bytes, '\0', (size_t)length) != NULL) {
        attempt->outcome = PARSE_ARGUMENT_ERROR;
        PyErr_SetString(PyExc_SyntaxError, "source code string cannot contain null bytes");
        return NULL;
    }
    struct compile_permit permit = {
        .thread = PyThreadState_Get(), .interpreter = state.interpreter,
        .source = &attempt->source, .audit_seen = 0,
        .completion_required = 1, .parser_frame = (PyFrameObject *)Py_NewRef(frame)
    };
    if (PyThread_tss_set(&permit_key, &permit) != 0) {
        Py_DECREF(permit.parser_frame);
        attempt->outcome = PARSE_PROTOCOL_ERROR;
        refuse("native AST permit could not be installed");
        return NULL;
    }
    PyCompilerFlags flags = {.cf_flags = attempt->flags,
                            .cf_feature_version = attempt->feature_version};
    PyObject *result = Py_CompileStringObject(attempt->source.bytes, attempt->source.path,
                                             start, &flags, optimize);
    if (PyThread_tss_set(&permit_key, NULL) != 0)
        _exit(125);
    Py_XDECREF(permit.audit_arguments);
    Py_DECREF(permit.parser_frame);
    if (!permit.audit_seen || !permit.audit_completed || state.violated) {
        attempt->outcome = PARSE_PROTOCOL_ERROR;
        Py_XDECREF(result);
        if (PyErr_Occurred())
            latch("native AST parsing lacks a clean matching audit event");
        else
            refuse("native AST parsing lacks a clean matching audit event");
        return NULL;
    }
    if (result == NULL) {
        attempt->outcome = PARSE_COMPILER_ERROR;
        if (!PyErr_ExceptionMatches(PyExc_SyntaxError))
            latch("native AST parsing failed outside ordinary syntax rejection");
        return NULL;              /* ordinary parse error, original exception, no code authority */
    }
    if (PyCode_Check(result) || !PyObject_TypeCheck(result, (PyTypeObject *)route->ast_base)) {
        attempt->outcome = PARSE_PROTOCOL_ERROR;
        Py_DECREF(result);
        refuse("native AST compiler returned a non-AST object");
        return NULL;
    }
    attempt->outcome = PARSE_RETURNED;
    if (count_event(&state.ast_returns) < 0) {
        attempt->outcome = PARSE_PROTOCOL_ERROR;
        Py_DECREF(result);
        return NULL;
    }
    return result;                /* data only: never retain_tree or executable registry */
}

static PyObject *
activate(PyObject *self, PyObject *ignored)
{
    (void)self;
    (void)ignored;
    if (single_bootstrap_thread() < 0)
        return NULL;
    if (state.phase != CONFIGURED || state.violated || state.code_count == 0 ||
        native_operation_active()) {
        refuse("native activation requires a prepared clean registry");
        return NULL;
    }
    state.phase = ACTIVE;
    Py_RETURN_NONE;
}

static PyObject *
contains(PyObject *self, PyObject *code)
{
    (void)self;
    if (same_interpreter() < 0)
        return NULL;
    return PyBool_FromLong(PyCode_Check(code) && lookup_code(code) != NULL);
}

static PyObject *
status(PyObject *self, PyObject *ignored)
{
    (void)self;
    (void)ignored;
    static const char *phases[] = {"bootstrap", "configuring", "configured", "active", "failed"};
    if (same_interpreter() < 0)
        return NULL;
    PyObject *report = Py_BuildValue("{s:s,s:O,s:O,s:z,s:O,s:n,s:n,s:K,s:K,s:K,s:O,s:O,s:K,s:K,s:K,s:n,s:K,s:K,s:K,s:K}",
        "phase", phases[state.phase], "preinitializationInstalled", state.installed ? Py_True : Py_False,
        "violated", state.violated ? Py_True : Py_False, "firstFailure", state.first_failure,
        "runId", state.run_id == NULL ? Py_None : state.run_id,
        "sourceCount", (Py_ssize_t)state.source_count, "registeredCodeCount", (Py_ssize_t)state.code_count,
        "bootstrapEvents", state.bootstrap_events, "subsequentEvents", state.active_events,
        "compilations", state.compilations, "confinementEstablished", Py_False,
        "permitActive", native_operation_active() ? Py_True : Py_False,
        "generatedCompilations", state.generated_compilations,
        "astParseAttempts", state.ast_attempts, "astParseReturns", state.ast_returns,
        "frozenOriginCount", (Py_ssize_t)frozen_count,
        "frozenRequests", frozen_requests, "frozenReturns", frozen_returns,
        "cachedBindingAttempts", cached_requests, "cachedBindingReturns", cached_returns);
    if (report == NULL)
        return NULL;
    PyObject *policy = process_filter_status();
    if (policy == NULL || PyDict_SetItemString(report, "syscallPolicy", policy) < 0) {
        Py_XDECREF(policy);
        Py_DECREF(report);
        return NULL;
    }
    Py_DECREF(policy);
    PyObject *metadata = Py_BuildValue("{s:O,s:i,s:K,s:K,s:O}",
        "providerCaptured", frozen_finder == NULL ? Py_False : Py_True,
        "providerFlags", frozen_finder == NULL ? 0 : PyCFunction_GetFlags(frozen_finder),
        "requests", metadata_requests, "returns", metadata_returns,
        "keywordNames", frozen_finder_keywords == NULL ? Py_None : frozen_finder_keywords);
    if (metadata == NULL || PyDict_SetItemString(report, "frozenMetadata", metadata) < 0) {
        Py_XDECREF(metadata);
        Py_DECREF(report);
        return NULL;
    }
    Py_DECREF(metadata);
    return report;
}

static PyMethodDef methods[] = {
    {"configure", configure, METH_VARARGS, "Copy exact trusted-bootstrap source bytes once."},
    {"compile_source", compile_source, METH_O, "Compile the owned source selected by its path."},
    {"frozen_code", frozen_code, METH_O, "Acquire code only from the owned native frozen provider."},
    {"frozen_metadata", frozen_metadata, METH_O, "Copy metadata joined to owned native frozen bytes."},
    {"frozen_metadata_observations", frozen_metadata_observations, METH_NOARGS,
     "Copy retained metadata attempt facts; never grant code or confinement authority."},
    {"bind_generator", bind_generator, METH_VARARGS, "Bind a fixed owned stdlib generator during trusted bootstrap."},
    {"bind_cached_generator", bind_cached_generator, METH_O, "Bind a fixed captured startup generator after owned-source correspondence."},
    {"activate", activate, METH_NOARGS, "Activate native compile/exec checks once."},
    {"contains", contains, METH_O, "Observe actual native code identity; never register it."},
    {"status", status, METH_NOARGS, "Return component observations, not confinement evidence."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_worldline_examiner_guard",
    .m_doc = "Native compiler dependency; complete confinement remains unestablished.",
    .m_size = -1,
    .m_methods = methods
};

static PyObject *
initialize_module(void)
{
    PyThreadState *thread = PyThreadState_Get();
    PyInterpreterState *interpreter = PyThreadState_GetInterpreter(thread);
    if (!state.installed || interpreter != PyInterpreterState_Main()) {
        refuse("native guard was not installed before the main interpreter");
        return NULL;
    }
    if (state.interpreter == NULL) {
        state.interpreter = interpreter;
        state.bootstrap_thread = thread;
    } else if (same_interpreter() < 0) {
        return NULL;
    }
    return PyModule_Create(&module);
}

__attribute__((constructor)) static void
install_before_python(void)
{
    /* Loading this library late is a refused process, never a Python fallback. */
    const char *version = Py_GetVersion();
    if (Py_IsInitialized() || strncmp(version, PY_VERSION " ", sizeof(PY_VERSION)) != 0)
        _exit(125);
    install_process_filter();
    if (PyThread_tss_create(&permit_key) != 0 ||
        PyThread_tss_create(&frozen_permit_key) != 0 ||
        PyImport_AppendInittab("_worldline_examiner_guard", initialize_module) != 0 ||
        PySys_AddAuditHook(audit_hook, &state) != 0)
        _exit(125);
    frozen_tables[0] = _PyImport_FrozenBootstrap;
    frozen_tables[1] = _PyImport_FrozenStdlib;
    frozen_tables[2] = _PyImport_FrozenTest;
    state.installed = 1;
}
