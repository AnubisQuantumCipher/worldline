/* Complete installed-CPython-3.14 generator grammars. Included only by guard.c.
 * Input is exact Unicode, copied/owned by the caller. No Python validator runs.
 * Each production consumes every literal and repeats validated identifiers at
 * the corresponding template positions. Successful parsing requires exact EOF.
 */
struct template_cursor { const char *at, *end; };

static int
template_take(struct template_cursor *p, const char *literal)
{
    size_t length = strlen(literal);
    if (length > (size_t)(p->end - p->at) || memcmp(p->at, literal, length) != 0)
        return 0;
    p->at += length;
    return 1;
}

static int
template_equal(PyObject *a, PyObject *b)
{
    return PyUnicode_Compare(a, b) == 0;
}

static int
template_word(PyObject *word, const char *text)
{
    return PyUnicode_CompareWithASCIIString(word, text) == 0;
}

static int
template_identifier_valid(PyObject *word)
{
    static const char *keywords[] = {
        "False", "None", "True", "and", "as", "assert", "async", "await",
        "break", "class", "continue", "def", "del", "elif", "else", "except",
        "finally", "for", "from", "global", "if", "import", "in", "is",
        "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
        "while", "with", "yield", NULL
    };
    if (!PyUnicode_CheckExact(word) || !PyUnicode_IsIdentifier(word))
        return 0;
    for (size_t i = 0; keywords[i] != NULL; ++i)
        if (template_word(word, keywords[i]))
            return 0;
    return 1;
}

static PyObject *
template_identifier(struct template_cursor *p)
{
    const char *start = p->at;
    while (p->at != p->end) {
        unsigned char c = (unsigned char)*p->at;
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '_' || c >= 0x80))
            break;
        ++p->at;
    }
    if (p->at == start)
        return NULL;
    PyObject *word = PyUnicode_DecodeUTF8(start, p->at - start, "strict");
    if (word != NULL && !template_identifier_valid(word))
        Py_CLEAR(word);
    return word;
}

static int
template_take_unicode(struct template_cursor *p, PyObject *word)
{
    Py_ssize_t size;
    const char *text = PyUnicode_AsUTF8AndSize(word, &size);
    if (text == NULL || size > p->end - p->at ||
        memcmp(text, p->at, (size_t)size) != 0)
        return 0;
    p->at += size;
    return 1;
}

static int
template_append(PyObject *list, PyObject *owned)
{
    if (owned == NULL)
        return 0;
    int result = PyList_Append(list, owned);
    Py_DECREF(owned);
    return result == 0;
}

static int
template_has(PyObject *list, PyObject *word)
{
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(list); ++i)
        if (template_equal(PyList_GET_ITEM(list, i), word))
            return 1;
    return 0;
}

static int
template_begin(PyObject *text, struct template_cursor *p)
{
    Py_ssize_t length;
    if (!PyUnicode_CheckExact(text))
        return 0;
    const char *bytes = PyUnicode_AsUTF8AndSize(text, &length);
    if (bytes == NULL || memchr(bytes, '\0', (size_t)length) != NULL)
        return 0;
    p->at = bytes;
    p->end = bytes + length;
    return 1;
}

static int
template_namedtuple(PyObject *text)
{
    struct template_cursor p;
    if (!template_begin(text, &p) || !template_take(&p, "lambda _cls, "))
        return 0;
    PyObject *fields = PyList_New(0);
    if (fields == NULL)
        return 0;
    const char *arguments = p.at;
    if (p.at != p.end && *p.at != ':') {
        for (;;) {
            if (!template_append(fields, template_identifier(&p)))
                goto invalid;
            if (template_take(&p, ", "))
                continue;
            if (PyList_GET_SIZE(fields) == 1 && !template_take(&p, ","))
                goto invalid;
            break;
        }
    }
    Py_ssize_t argument_length = p.at - arguments;
    if (!template_take(&p, ": _tuple_new(_cls, (") ||
        argument_length > p.end - p.at ||
        memcmp(p.at, arguments, (size_t)argument_length) != 0)
        goto invalid;
    p.at += argument_length;
    if (!template_take(&p, "))") || p.at != p.end)
        goto invalid;
    Py_DECREF(fields);
    return 1;
invalid:
    Py_DECREF(fields);
    return 0;
}

/* A closure default name is a fixed prefix/suffix around a valid identifier. */
static int
template_default_name(PyObject *word)
{
    struct template_cursor p;
    if (!template_begin(word, &p) || !template_take(&p, "__dataclass_dflt_"))
        return 0;
    if (p.end - p.at <= 2 || memcmp(p.end - 2, "__", 2) != 0)
        return 0;
    PyObject *field = PyUnicode_DecodeUTF8(p.at, p.end - p.at - 2, "strict");
    if (field == NULL)
        return 0;
    int valid = template_identifier_valid(field);
    Py_DECREF(field);
    return valid;
}

static int
template_closure_name(PyObject *word)
{
    return template_word(word, "__dataclass_HAS_DEFAULT_FACTORY__") ||
           template_word(word, "__dataclass_builtins_object__") ||
           template_word(word, "__dataclasses_recursive_repr") ||
           template_word(word, "__class__") ||
           template_word(word, "FrozenInstanceError") || template_default_name(word);
}

static int
template_named_closure(PyObject *closures, const char *name)
{
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(closures); ++i)
        if (template_word(PyList_GET_ITEM(closures, i), name))
            return 1;
    return 0;
}

static PyObject *
template_default_for(PyObject *field)
{
    return PyUnicode_FromFormat("__dataclass_dflt_%U__", field);
}

static int
template_field_value(struct template_cursor *p, PyObject *field,
                     PyObject *parameters, PyObject *closures)
{
    struct template_cursor q = *p;
    PyObject *value = template_identifier(&q);
    if (value == NULL)
        return 0;
    PyObject *expected = template_default_for(field);
    if (expected == NULL) {
        Py_DECREF(value);
        return 0;
    }
    int valid = 0;
    if (template_equal(value, field) && template_has(parameters, field)) {
        valid = 1;
    } else if (template_equal(value, expected) && template_has(closures, expected)) {
        valid = 1;
        if (template_take(&q, "()")) {
            if (template_take(&q, " if ")) {
                valid = template_has(parameters, field) &&
                    template_named_closure(closures, "__dataclass_HAS_DEFAULT_FACTORY__") &&
                    template_take_unicode(&q, field) &&
                    template_take(&q, " is __dataclass_HAS_DEFAULT_FACTORY__ else ") &&
                    template_take_unicode(&q, field);
            }
        }
    }
    Py_DECREF(value);
    Py_DECREF(expected);
    if (valid)
        *p = q;
    return valid;
}

static int
template_init(struct template_cursor *p, PyObject *closures)
{
    PyObject *self = template_identifier(p);
    PyObject *parameters = PyList_New(0);
    if (self == NULL || parameters == NULL ||
        !(template_word(self, "self") || template_word(self, "__dataclass_self__")))
        goto invalid;
    int keyword_only = 0;
    while (template_take(p, ",")) {
        if (template_take(p, "*,")) {
            if (keyword_only)
                goto invalid;
            keyword_only = 1;
        }
        PyObject *field = template_identifier(p);
        if (field == NULL)
            goto invalid;
        if (PyList_Append(parameters, field) < 0) {
            Py_DECREF(field);
            goto invalid;
        }
        if (template_take(p, "=")) {
            PyObject *value = template_identifier(p);
            PyObject *expected = template_default_for(field);
            int valid = value != NULL && expected != NULL && template_has(closures, value) &&
                (template_equal(value, expected) ||
                 template_word(value, "__dataclass_HAS_DEFAULT_FACTORY__"));
            Py_XDECREF(value);
            Py_XDECREF(expected);
            if (!valid) {
                Py_DECREF(field);
                goto invalid;
            }
        }
        Py_DECREF(field);
    }
    if (!template_take(p, "):\n"))
        goto invalid;
    if (template_take(p, "  pass\n"))
        goto valid;
    int statements = 0, post_init = 0;
    while (template_take(p, "  ")) {
        if (post_init)
            goto invalid;
        if (template_take(p, "__dataclass_builtins_object__.__setattr__(")) {
            if (!template_named_closure(closures, "__dataclass_builtins_object__") ||
                !template_take_unicode(p, self) || !template_take(p, ","))
                goto invalid;
            /* repr(identifier) has single quotes for every valid identifier. */
            if (!template_take(p, "'"))
                goto invalid;
            PyObject *field = template_identifier(p);
            int ok = field != NULL && template_take(p, "',") &&
                template_field_value(p, field, parameters, closures) && template_take(p, ")\n");
            Py_XDECREF(field);
            if (!ok)
                goto invalid;
        } else {
            if (!template_take_unicode(p, self) || !template_take(p, "."))
                goto invalid;
            PyObject *field = template_identifier(p);
            if (field == NULL)
                goto invalid;
            int ok;
            if (template_word(field, "__post_init__") && template_take(p, "(")) {
                post_init = 1;
                ok = 1;
                if (!template_take(p, ")\n")) {
                    for (;;) {
                        PyObject *arg = template_identifier(p);
                        /* InitVar init=False can intentionally remain unbound:
                         * preserve its later Python NameError, not a new domain. */
                        int known = arg != NULL;
                        Py_XDECREF(arg);
                        if (!known) { ok = 0; break; }
                        if (template_take(p, ","))
                            continue;
                        ok = template_take(p, ")\n");
                        break;
                    }
                }
            } else {
                ok = template_take(p, "=") &&
                    template_field_value(p, field, parameters, closures) && template_take(p, "\n");
            }
            Py_DECREF(field);
            if (!ok)
                goto invalid;
        }
        statements = 1;
    }
    if (!statements)
        goto invalid;
valid:
    Py_DECREF(self);
    Py_DECREF(parameters);
    return 1;
invalid:
    Py_XDECREF(self);
    Py_XDECREF(parameters);
    return 0;
}

static int
template_repr(struct template_cursor *p)
{
    if (!template_take(p, "self):\n  return f\"{self.__class__.__qualname__}("))
        return 0;
    if (template_take(p, ")\"\n"))
        return 1;
    for (;;) {
        PyObject *field = template_identifier(p);
        int valid = field != NULL && template_take(p, "={self.") &&
            template_take_unicode(p, field) && template_take(p, "!r}");
        Py_XDECREF(field);
        if (!valid)
            return 0;
        if (template_take(p, ", "))
            continue;
        return template_take(p, ")\"\n");
    }
}

static int
template_eq(struct template_cursor *p)
{
    if (!template_take(p, "self,other):\n  if self is other:\n   return True\n"
                         "  if other.__class__ is self.__class__:\n   return "))
        return 0;
    if (!template_take(p, "True")) {
        for (;;) {
            if (!template_take(p, "self."))
                return 0;
            PyObject *field = template_identifier(p);
            int valid = field != NULL && template_take(p, "==other.") &&
                template_take_unicode(p, field);
            Py_XDECREF(field);
            if (!valid)
                return 0;
            if (!template_take(p, " and "))
                break;
        }
    }
    return template_take(p, "\n  return NotImplemented\n");
}

static PyObject *
template_self_tuple(struct template_cursor *p)
{
    if (!template_take(p, "("))
        return NULL;
    PyObject *fields = PyList_New(0);
    if (fields == NULL)
        return NULL;
    if (template_take(p, ")"))
        return fields;
    for (;;) {
        if (!template_take(p, "self.") || !template_append(fields, template_identifier(p)) ||
            !template_take(p, ","))
            break;
        if (template_take(p, ")"))
            return fields;
    }
    Py_DECREF(fields);
    return NULL;
}

static int
template_other_tuple(struct template_cursor *p, PyObject *fields)
{
    if (!template_take(p, "("))
        return 0;
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(fields); ++i)
        if (!template_take(p, "other.") ||
            !template_take_unicode(p, PyList_GET_ITEM(fields, i)) || !template_take(p, ","))
            return 0;
    return template_take(p, ")");
}

static int
template_order(struct template_cursor *p, const char *operation)
{
    if (!template_take(p, "self,other):\n  if other.__class__ is self.__class__:\n   return "))
        return 0;
    PyObject *fields = template_self_tuple(p);
    if (fields == NULL)
        return 0;
    int valid = template_take(p, operation) && template_other_tuple(p, fields) &&
        template_take(p, "\n  return NotImplemented\n");
    Py_DECREF(fields);
    return valid;
}

static int
template_hash(struct template_cursor *p)
{
    if (!template_take(p, "self):\n  return hash("))
        return 0;
    PyObject *fields = template_self_tuple(p);
    if (fields == NULL)
        return 0;
    Py_DECREF(fields);
    return template_take(p, ")\n");
}

static int
template_frozen(struct template_cursor *p, int setter, PyObject *closures)
{
    if (!template_named_closure(closures, "__class__") ||
        !template_named_closure(closures, "FrozenInstanceError") ||
        !template_take(p, setter ? "self,name,value):\n" : "self,name):\n") ||
        !template_take(p, "  if type(self) is __class__"))
        return 0;
    if (template_take(p, " or name in {")) {
        for (;;) {
            if (!template_take(p, "'"))
                return 0;
            PyObject *field = template_identifier(p);
            int valid = field != NULL && template_take(p, "'");
            Py_XDECREF(field);
            if (!valid)
                return 0;
            if (!template_take(p, ", "))
                break;
        }
        if (!template_take(p, "}"))
            return 0;
    }
    return template_take(p, setter ?
        ":\n   raise FrozenInstanceError(f\"cannot assign to field {name!r}\")\n"
        "  super(__class__, self).__setattr__(name, value)\n" :
        ":\n   raise FrozenInstanceError(f\"cannot delete field {name!r}\")\n"
        "  super(__class__, self).__delattr__(name)\n");
}

/* Return the exact ordered closure names, or NULL for invalid source/error. */
static PyObject *
template_dataclass(PyObject *text)
{
    static const char *methods[] = {"__init__", "__repr__", "__eq__", "__lt__",
        "__le__", "__gt__", "__ge__", "__setattr__", "__delattr__", "__hash__"};
    struct template_cursor p;
    if (!template_begin(text, &p) || !template_take(&p, "def __create_fn__("))
        return NULL;
    PyObject *closures = PyList_New(0), *names = PyList_New(0);
    if (closures == NULL || names == NULL)
        goto invalid;
    if (!template_take(&p, "):\n")) {
        for (;;) {
            PyObject *name = template_identifier(&p);
            int valid = name != NULL && template_closure_name(name) && !template_has(closures, name);
            if (!valid || PyList_Append(closures, name) < 0) {
                Py_XDECREF(name);
                goto invalid;
            }
            Py_DECREF(name);
            if (!template_take(&p, ","))
                break;
        }
        if (!template_take(&p, "):\n"))
            goto invalid;
    }
    int previous = -1;
    /* An empty builder contributes its own blank line before the return. */
    if (template_take(&p, "\n return ()") && p.at == p.end) {
        Py_DECREF(names);
        return closures;
    }
    for (;;) {
        int decorated = template_take(&p, " @__dataclasses_recursive_repr()\n");
        if (!template_take(&p, " def "))
            goto invalid;
        PyObject *name = template_identifier(&p);
        int method = -1;
        if (name != NULL)
            for (size_t i = 0; i < sizeof(methods) / sizeof(*methods); ++i)
                if (template_word(name, methods[i]))
                    method = (int)i;
        if (method <= previous || !template_take(&p, "(") ||
            decorated != (method == 1) ||
            (decorated && !template_named_closure(closures, "__dataclasses_recursive_repr"))) {
            Py_XDECREF(name);
            goto invalid;
        }
        if (!template_append(names, name))
            goto invalid;
        previous = method;
        int valid = 0;
        switch (method) {
            case 0: valid = template_init(&p, closures); break;
            case 1: valid = template_repr(&p); break;
            case 2: valid = template_eq(&p); break;
            case 3: valid = template_order(&p, "<"); break;
            case 4: valid = template_order(&p, "<="); break;
            case 5: valid = template_order(&p, ">"); break;
            case 6: valid = template_order(&p, ">="); break;
            case 7: valid = template_frozen(&p, 1, closures); break;
            case 8: valid = template_frozen(&p, 0, closures); break;
            case 9: valid = template_hash(&p); break;
        }
        if (!valid)
            goto invalid;
        if (template_take(&p, " return ("))
            break;
    }
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(names); ++i)
        if (!template_take_unicode(&p, PyList_GET_ITEM(names, i)) || !template_take(&p, ","))
            goto invalid;
    if (!template_take(&p, ")") || p.at != p.end)
        goto invalid;
    Py_DECREF(names);
    return closures;
invalid:
    Py_XDECREF(closures);
    Py_XDECREF(names);
    return NULL;
}
