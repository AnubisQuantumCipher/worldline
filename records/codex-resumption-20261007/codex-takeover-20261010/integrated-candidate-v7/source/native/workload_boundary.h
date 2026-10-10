/* Actual entry and enclosing helper calls, owned by a native one-shot frame.
 * The trusted bootstrap remains an explicit dependency, not protected custody.
 */
struct wl_workload {
    int attempted, bound, used, active, entry_used, entry_started, entry_returned;
    uint64_t entry_identity;
    PyObject *function, *arguments, *code, *globals, *entry, *path, *entry_primary;
    PyFrameObject *caller;
    PyThreadState *thread;
    struct source *support_source, *entry_source;
    struct wl_operation *operation;
};
static struct wl_workload workload;

static PyObject *
wl_workload_inputs(void)
{
    struct code_slot *entry = lookup_code(workload.entry);
    if (entry == NULL) {
        refuse("native workload entry lost its held registration");
        return NULL;
    }
    return Py_BuildValue("(OKOKK)", workload.function,
        (unsigned long long)entry->identity, workload.path,
        (unsigned long long)(uintptr_t)workload.caller,
        (unsigned long long)(uintptr_t)workload.arguments);
}

static void
wl_release_workload(void)
{
    PyObject *primary = PyErr_GetRaisedException();
    /* Preserve the exception indicator even through decrefs and finalizers. */
    Py_CLEAR(workload.entry_primary);
    Py_CLEAR(workload.arguments);
    Py_CLEAR(workload.function);
    Py_CLEAR(workload.code);
    Py_CLEAR(workload.globals);
    Py_CLEAR(workload.entry);
    Py_CLEAR(workload.path);
    Py_CLEAR(workload.caller);
    PyErr_Clear();
    if (primary != NULL)
        PyErr_SetRaisedException(primary);
}

static PyObject *
bind_workload(PyObject *self, PyObject *args)
{
    if (workload.attempted || !lifetime.attached || state.phase != CONFIGURED || state.violated ||
        native_operation_active() || single_bootstrap_thread() < 0) {
        if (!PyErr_Occurred())
            refuse("workload binding requires the clean one-shot bootstrap");
        return NULL;
    }
    workload.attempted = 1;
    if (!PyTuple_CheckExact(args) || PyTuple_GET_SIZE(args) != 4) {
        refuse("workload binding argument layout differs");
        return NULL;
    }
    PyObject *function = PyTuple_GET_ITEM(args, 0);
    PyObject *arguments = PyTuple_GET_ITEM(args, 1);
    PyObject *entry = PyTuple_GET_ITEM(args, 2);
    PyObject *path = PyTuple_GET_ITEM(args, 3);
    if (!PyFunction_Check(function) || !PyTuple_CheckExact(arguments) ||
        PyTuple_GET_SIZE(arguments) != 5 || !PyCode_Check(entry) ||
        !PyUnicode_CheckExact(path)) {
        refuse("workload binding requires the fixed function and exact arguments");
        return NULL;
    }
    PyObject *code = PyFunction_GET_CODE(function), *globals = PyFunction_GET_GLOBALS(function);
    struct code_slot *driver = lookup_code(code), *root = lookup_code(entry);
    PyCodeObject *signature = (PyCodeObject *)code;
    PyFrameObject *caller = PyEval_GetFrame();
    if (driver == NULL || root == NULL || caller == NULL || !PyDict_CheckExact(globals) ||
        !template_word(driver->source->path, "/run/worldline-examiner-loader.py") ||
        !template_word(signature->co_qualname, "_native_workload") ||
        !template_word(((PyCodeObject *)entry)->co_qualname, "<module>") ||
        ((PyCodeObject *)entry)->co_argcount != 0 || ((PyCodeObject *)entry)->co_kwonlyargcount != 0 ||
        signature->co_argcount != 5 || signature->co_kwonlyargcount != 0 ||
        (signature->co_flags & (CO_GENERATOR | CO_COROUTINE | CO_ASYNC_GENERATOR |
                               CO_VARARGS | CO_VARKEYWORDS)) ||
        PyFunction_GET_CLOSURE(function) != NULL ||
        PyFunction_GET_DEFAULTS(function) != NULL || PyFunction_GET_KW_DEFAULTS(function) != NULL ||
        PyTuple_GET_ITEM(arguments, 0) != self || PyTuple_GET_ITEM(arguments, 2) != entry ||
        PyTuple_GET_ITEM(arguments, 3) != path ||
        PyUnicode_Compare(root->source->path, path) != 0) {
        refuse("workload binding differs from the owned helper and entry");
        return NULL;
    }
    workload.function = Py_NewRef(function);
    workload.arguments = Py_NewRef(arguments);
    workload.code = Py_NewRef(code);
    workload.globals = Py_NewRef(globals);
    workload.entry = Py_NewRef(entry);
    workload.path = Py_NewRef(path);
    workload.caller = (PyFrameObject *)Py_NewRef((PyObject *)caller);
    workload.thread = PyThreadState_Get();
    workload.support_source = driver->source;
    workload.entry_source = root->source;
    PyObject *inputs = wl_workload_inputs();
    if (inputs == NULL) {
        wl_release_workload();
        return NULL;
    }
    struct wl_operation operation;
    int started = wl_begin(&operation, "bind-workload", &inputs, 1,
                          workload.support_source, NULL, 0);
    Py_DECREF(inputs);
    if (started < 0) {
        wl_release_workload();
        return NULL;
    }
    workload.bound = 1;
    return wl_finish(&operation, Py_NewRef(Py_None));
}

static PyObject *
run_entry(PyObject *self, PyObject *namespace)
{
    (void)self;
    PyFrameObject *frame = PyEval_GetFrame();
    PyFrameObject *back = frame == NULL ? NULL : PyFrame_GetBack(frame);
    PyCodeObject *code = frame == NULL ? NULL : PyFrame_GetCode(frame);
    PyObject *globals = frame == NULL ? NULL : PyFrame_GetGlobals(frame);
    int allowed = workload.active && !workload.entry_used && workload.operation != NULL &&
        workload.thread == PyThreadState_Get() && frame != NULL &&
        back == workload.caller &&
        (PyObject *)code == workload.code && globals == workload.globals &&
        PyDict_CheckExact(namespace) && state.phase == ACTIVE && !state.violated &&
        !native_operation_active() &&
        PyThread_tss_get(&lifetime_operation_key) == workload.operation;
    static const char *parameters[] = {"guard", "registry", "code", "path", "read_source"};
    for (size_t i = 0; allowed && i < sizeof(parameters) / sizeof(parameters[0]); ++i) {
        PyObject *value = PyFrame_GetVarString(frame, parameters[i]);
        allowed = value != NULL && value == PyTuple_GET_ITEM(workload.arguments, (Py_ssize_t)i);
        Py_XDECREF(value);
    }
    Py_XDECREF(code);
    Py_XDECREF(globals);
    Py_XDECREF(back);
    if (!allowed) {
        if (!PyErr_Occurred())
            refuse("entry execution lacks its active held helper frame");
        return NULL;
    }
    workload.entry_used = 1;
    struct code_slot *entry = lookup_code(workload.entry);
    PyObject *inputs = entry == NULL ? NULL : Py_BuildValue("(KKKK)",
        (unsigned long long)entry->identity,
        (unsigned long long)(uintptr_t)namespace, (unsigned long long)(uintptr_t)frame,
        (unsigned long long)(uintptr_t)workload.caller);
    if (inputs == NULL) {
        if (!PyErr_Occurred())
            refuse("entry execution lost its held code");
        return NULL;
    }
    struct wl_operation operation;
    int started = wl_begin(&operation, "workload-entry", &inputs, 1,
                          workload.entry_source, NULL, 0);
    Py_DECREF(inputs);
    if (started < 0)
        return NULL;
    operation.workload_result = 1;
    workload.entry_identity = operation.identity;
    workload.entry_started = 1;
    PyObject *result = PyEval_EvalCode(workload.entry, namespace, namespace);
    workload.entry_returned = result != NULL;
    if (result == NULL) {
        workload.entry_primary = PyErr_GetRaisedException();
        if (workload.entry_primary != NULL)
            PyErr_SetRaisedException(Py_NewRef(workload.entry_primary));
    }
    return wl_finish(&operation, result);
}

static PyObject *
run_workload(PyObject *self, PyObject *unused)
{
    (void)self;
    (void)unused;
    if (!workload.bound || workload.used || workload.active ||
        state.phase != CONFIGURED || state.violated || native_operation_active() ||
        single_bootstrap_thread() < 0 || workload.thread != PyThreadState_Get() ||
        PyEval_GetFrame() != workload.caller ||
        PyFunction_GET_CODE(workload.function) != workload.code ||
        PyFunction_GET_GLOBALS(workload.function) != workload.globals ||
        PyFunction_GET_CLOSURE(workload.function) != NULL ||
        PyFunction_GET_DEFAULTS(workload.function) != NULL ||
        PyFunction_GET_KW_DEFAULTS(workload.function) != NULL) {
        if (!PyErr_Occurred())
            refuse("workload execution differs from its one-shot held binding");
        return NULL;
    }
    workload.used = 1;
    PyObject *inputs = wl_workload_inputs();
    if (inputs == NULL)
        return NULL;
    struct wl_operation operation;
    int started = wl_begin(&operation, "workload", &inputs, 1,
                          workload.support_source, NULL, 0);
    Py_DECREF(inputs);
    if (started < 0) {
        wl_release_workload();
        return NULL;
    }
    operation.workload_result = 1;
    workload.active = 1;
    workload.operation = &operation;
    PyObject *result = PyObject_Call(workload.function, workload.arguments, NULL);
    PyObject *helper_primary = PyErr_GetRaisedException();
    PyObject *selected = Py_XNewRef(workload.entry_primary != NULL ?
                                   workload.entry_primary : helper_primary);
    lifetime.busy = state.lifetime_operation = 1;
    struct wl_record record = wl_record_open();
    wl_tuple(&record, 11);
    /* The entry RESULT is the immutable pre-cleanup snapshot, already retained
     * before returning from run_entry. These are distinct post-cleanup facts;
     * a legitimate finally may mutate the same original exception object. */
    wl_ascii(&record, "native-workload-outcome-after-helper-cleanup");
    wl_unsigned(&record, operation.identity);
    if (workload.entry_started)
        wl_unsigned(&record, workload.entry_identity);
    else
        wl_tag(&record, WL_NONE);
    wl_tag(&record, workload.entry_started ? WL_TRUE : WL_FALSE);
    wl_tag(&record, workload.entry_returned ? WL_TRUE : WL_FALSE);
    wl_exception(&record, workload.entry_primary);
    wl_tag(&record, result != NULL ? WL_TRUE : WL_FALSE);
    wl_exception(&record, helper_primary);
    wl_ascii(&record, workload.entry_primary != NULL ? "entry" :
                      (helper_primary != NULL ? "helper" : "none"));
    wl_tag(&record, record.complete ? WL_TRUE : WL_FALSE);
    wl_tuple(&record, 3);
    wl_object_identity(&record, workload.entry_primary);
    wl_object_identity(&record, helper_primary);
    wl_object_identity(&record, selected);
    int retained = wl_exchange(WL_WORKLOAD_OUTCOME, &record);
    lifetime.busy = state.lifetime_operation = 0;
    workload.active = 0;
    workload.operation = NULL;
    if (selected != NULL || retained < 0 || !workload.entry_started || result != Py_None) {
        Py_XDECREF(result);
        result = NULL;
        if (selected == NULL && !PyErr_Occurred())
            refuse("native workload did not return a retained complete invocation");
    }
    Py_XDECREF(helper_primary);
    if (selected != NULL) {
        PyErr_Clear();
        PyErr_SetRaisedException(selected);
    }
    wl_release_workload();
    return wl_finish(&operation, result);
}
