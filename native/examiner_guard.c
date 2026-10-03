/* Examiner-only native compiler dependency, CPython 3.14 with the GIL.
 *
 * The fixed pre-workload bootstrap supplies the byte inventory. This component
 * does not authenticate that bootstrap, establish lifetime custody, cover every
 * generator/native provider, restrict native memory access, or establish confinement.
 * There is intentionally no Python API for registering a caller's code object.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "generator_templates.h"

#if PY_MAJOR_VERSION != 3 || PY_MINOR_VERSION != 14
#error "The examiner guard requires reviewed CPython 3.14 headers"
#endif
#ifdef Py_GIL_DISABLED
#error "The examiner guard requires the reviewed GIL-enabled interpreter"
#endif

enum phase { BOOTSTRAP, CONFIGURING, CONFIGURED, ACTIVE, FAILED };
enum route_index { NAMEDTUPLE_ROUTE, DATACLASS_ROUTE, AST_ROUTE, ROUTE_COUNT };

struct source {
    PyObject *path;
    char *bytes;
    Py_ssize_t length;
};

struct code_slot {
    PyObject *code;                 /* strong reference, pointer identity */
    struct source *source;          /* stable inventory or owned generation */
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
};

static struct guard state;
static Py_tss_t permit_key = Py_tss_NEEDS_INIT;

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
retain_tree(PyObject *code, struct source *source)
{
    /* Iterative traversal: the native C stack does not grow with nested code. */
    PyObject **pending = NULL;
    size_t used = 0, capacity = 0;
    PyObject *current = code;
    for (;;) {
        if (lookup_code(current) == NULL) {
            if (retain_code(current, source) < 0)
                goto error;
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
    if (state.phase != ACTIVE && state.phase != FAILED)
        return 0;
    if (strcmp(event, "exec") == 0 || strcmp(event, "function.__new__") == 0) {
        if (state.violated || !PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) < 1 ||
            !PyCode_Check(PyTuple_GET_ITEM(args, 0)) ||
            lookup_code(PyTuple_GET_ITEM(args, 0)) == NULL)
            return refuse("execution code is absent from the native registry");
    }
    if (strcmp(event, "code.__new__") == 0 || strcmp(event, "marshal.load") == 0 ||
        strcmp(event, "marshal.loads") == 0 || strcmp(event, "sys.addaudithook") == 0 ||
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
compile_owned(struct source *source, int mode, int compiler_flags)
{
    if (same_interpreter() < 0)
        return NULL;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated) {
        refuse("native compilation requires configured owned source");
        return NULL;
    }
    if (PyThread_tss_get(&permit_key) != NULL) {
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
                                           mode, &flags, -1);
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
    if (PyThread_tss_get(&permit_key) != NULL) {
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
bind_generator(PyObject *self, PyObject *args)
{
    (void)self;
    struct generator_route prepared = {0};
    PyObject *callback = NULL;
    if (state.phase != CONFIGURED || state.violated || single_bootstrap_thread() < 0 ||
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
    if (callback == NULL || PyDict_SetItemString(globals, operation, callback) < 0)
        goto error;
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

static int
generator_caller(struct generator_route *route, PyFrameObject **result)
{
    if (same_interpreter() < 0)
        return -1;
    if ((state.phase != CONFIGURED && state.phase != ACTIVE) || state.violated ||
        !route->bound || PyThread_tss_get(&permit_key) != NULL)
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
        PyThread_tss_get(&permit_key) != NULL) {
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
    return Py_BuildValue("{s:s,s:O,s:O,s:z,s:O,s:n,s:n,s:K,s:K,s:K,s:O,s:O,s:K,s:K,s:K}",
        "phase", phases[state.phase], "preinitializationInstalled", state.installed ? Py_True : Py_False,
        "violated", state.violated ? Py_True : Py_False, "firstFailure", state.first_failure,
        "runId", state.run_id == NULL ? Py_None : state.run_id,
        "sourceCount", (Py_ssize_t)state.source_count, "registeredCodeCount", (Py_ssize_t)state.code_count,
        "bootstrapEvents", state.bootstrap_events, "subsequentEvents", state.active_events,
        "compilations", state.compilations, "confinementEstablished", Py_False,
        "permitActive", PyThread_tss_get(&permit_key) != NULL ? Py_True : Py_False,
        "generatedCompilations", state.generated_compilations,
        "astParseAttempts", state.ast_attempts, "astParseReturns", state.ast_returns);
}

static PyMethodDef methods[] = {
    {"configure", configure, METH_VARARGS, "Copy exact trusted-bootstrap source bytes once."},
    {"compile_source", compile_source, METH_O, "Compile the owned source selected by its path."},
    {"bind_generator", bind_generator, METH_VARARGS, "Bind a fixed owned stdlib generator during trusted bootstrap."},
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
    if (Py_IsInitialized() || strncmp(version, PY_VERSION " ", sizeof(PY_VERSION)) != 0 ||
        PyThread_tss_create(&permit_key) != 0 ||
        PyImport_AppendInittab("_worldline_examiner_guard", initialize_module) != 0 ||
        PySys_AddAuditHook(audit_hook, &state) != 0)
        _exit(125);
    state.installed = 1;
}
