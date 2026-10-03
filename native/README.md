# Examiner native compiler dependency

`examiner_guard.c` is an additive native dependency used by the local private
evaluator integration. D32 passed the independently reviewed bounded native and
entry-component batch. It never supplies established confinement to the Ada/SPARK
decision. The original full campaign and formal proof remain required.

The examiner-only shared object must be loaded before CPython initialization.
Its constructor registers the C audit hook and built-in module. A late load or
registration failure ends that process. The independently reviewed build must
bind the actual installed compiler, headers and libpython. No global preload or
production installation is permitted by this component.

The fixed trusted bootstrap imports `_worldline_examiner_guard` and calls
`configure(run_id, ((absolute_path, exact_source_bytes), ...))` once, while it is
the sole thread of the main interpreter. Native checks accept exact built-in
types only and make owned copies. A malformed or repeated configuration is a
sticky failure. These inputs are trusted-bootstrap assertions; immutable copies
do not establish independent source authenticity or protected custody.

`compile_source(path)` selects the owned bytes, compiles in `exec` mode without
inherited future flags, and retains the actual result and all nested code
constants. A per-thread/interpreter non-reentrant permit matches the compiler's
source/path audit event. The permit is cleared before code registration or
return, including every error path. Python cannot register arbitrary code.

The proposed generator extension binds only the installed namedtuple and
dataclass builder sites through `bind_generator(label, function, source_path)`
during the sole trusted bootstrap. The function must belong to the actual native
owned-source registry. Native replacements check the immediate code/global
identities, the complete installed source template and fixed helper identities.
They retain generated source and nested code in stable native-owned storage,
preserve the original target globals, compiler flags, execution audit event and
return values, and never delegate template validation to mutable Python code.
The generator and AST dependency passed independent GPT-6.1 source, binding and
result reviews and the D25 controlled native build and component suite. Its
source and evidence remain retained separately from the next frozen extension.

D23 built the generator extension and retained a failing accepted dataclass
signature case. Its repair adds a bound `ast.parse` operation returning only
native AST data. Native validation requires ONLY_AST, the exact bound parser
caller and the installed option schema. Stable parse attempts are separate from
the executable-code registry; returned AST objects never gain code authority.
Original syntax/encoding/option errors remain errors, with the permit cleared;
authority/audit failures remain sticky. The current parser route supports exact
str/bytes sources, str filenames/modes and builtin int/bool options. Broader
public ast input domains (buffers, existing AST objects, path-like values and
subclasses) remain explicit compatibility work. The D23 failed result remains
retained. D24 also retained a new fixture's incorrect AST optimization expectation;
D25 compares the actual original and native ASTs and preserves Assert nodes.
Exact immutable argument values are retained before ordinary option conversions
and parsing, including supplied values that differ from normalized options.
Allocation failure before a record exists remains an explicit observation gap.
A private fixed C callback observes completion at the end of the interpreter
audit list; native state seals later hook registration during AST binding and
verifies installation with a scoped probe. Each AST permit binds that completion
to its real audit arguments, parser frame, thread and interpreter. An audit
callback's SyntaxError remains a sticky refusal; completed parser SyntaxError
remains an ordinary data error. The mechanism relies on the pinned CPython hook
implementation and does not claim portable Python sandbox semantics.

The frozen extension copies the pinned interpreter's built-in frozen rows into
stable native storage during trusted configuration. `frozen_code(name)` selects
only those bytes. The actual retained `_imp.is_frozen` C builtin restricts
availability, including disabled-module behavior; Python replacement of that
attribute cannot grant an origin. Native table pointer changes and custom tables
refuse. Package flags and negative sizes retain the original table semantics.
Alias code rows are retained separately; complete alias/module metadata remains
the bound importer's integration obligation. These marshal bytes never become
source selectors. A distinct exact-input native marshal permit excludes all
other native compilation/acquisition operations, in configured and active phases.
The permit is cleared before code-tree registration and on every error path;
actual primary exceptions and request/provider associations remain retained.
Native source and request records are component observations, not authenticated
external custody. D27 passed the controlled native build and all 75 native
component tests after independent GPT-6.1 source, binding and result reviews.
It does not establish absence of trailing marshal bytes or complete native-provider
coverage. The exact exercised source and receipts remain retained separately.

The next cached-generator extension captures only the fixed installed
collections.namedtuple, dataclasses builder and ast.parse objects during the
sole trusted configuration. `bind_cached_generator(label)` has no source, code,
function or globals argument. It compiles the owned complete source, compares
semantic code metadata and exact typed constants, then adopts only the held
function's actual code tree with separate cached-bootstrap provenance. This
comparison never changes pointer-only registry lookup. Existing module identities,
imported aliases and inspect's AST reference remain in place. Complete-operation
reentry exclusion and final identity rechecks cover reference-compiler and AST
audit callbacks. Original template validation and fixed-helper checks remain.
This extension awaits independent exact source review and controlled execution;
it does not supply general cached startup or protected custody acceptance.

After a clean prepared registry, `activate()` enables the component's native
exec/function-construction checks and refusals for unbound compilation, direct
code construction and deserialization. `contains(code)` reports pointer identity,
not code equality. `status()` reports native component observations and always
states `confinementEstablished: false`. Startup events are counted separately;
preloaded code is not misrepresented as checked-loader output. Source, registry
and code references intentionally live until process exit so finalizer/atexit
execution cannot outlive their authority storage.

The constructor now installs the reviewed D32 kernel process filter before
Python entry and preserves same-thread-group threads. Its native instruction
self-report and daemon-held mode/count samples have distinct evidence boundaries;
neither supplies complete lifetime confinement or protected custody.

The current frozen-metadata extension captures the actual find_frozen C builtin
during trusted configuration with its exact keyword calling convention. Each
lookup checks the complete raw buffer and package flag against owned code rows,
retains the original-name association and returns copied ordinary metadata.
Frozen code acquisition checks this same association. A distinct operation guard
excludes reentry throughout lookup, copying and cleanup without authorizing
marshal. Ordinary absence/provider errors remain distinct from authority errors.
Each actual metadata request emits the observational worldline.frozen_metadata
audit event under the full operation guard. A hook failure retains its primary
exception and a sticky protocol refusal. Python-emitted events grant no origin,
registration or custody, and are not a native lifetime transport.
The native loader locally reproduces frozen module/spec/alias metadata and
auxiliary methods; it does not delegate those methods to mutable FrozenImporter.
Its Python module attributes remain ordinary bookkeeping. This extension awaits
independent source review and controlled execution; no acceptance is implied.

Not yet complete: all required generator-template routes; all cached/frozen,
codec, native-extension and interpreter-memory controls; complete integrated
daemon-policy/entry acceptance; import/read/broker/report lifetime
provenance and protected observation custody. They remain original engineering
obligations. In particular, the trusted bootstrap can initialize codecs, but this
component does not establish provenance of later codec callbacks. Do not activate
it in a live accepted examiner until required compatibility and authority routes
are implemented and independently reviewed.

The additive controls use a supplied exact native artifact, real child
interpreters and temporary test files. Missing artifact or execution failures
fail the tests; there are no skips. Compilation and tests must use the existing
reviewed Root launch/resource procedure. No build/test has run merely because
this source or this file exists.
