# Phase One native lifetime development checkpoint — 2026-10-03

The native guard now retains owned acquisition and operation records through
Python finalization over the original bounded lifetime stream. The daemon
retains those records before acknowledging them and joins the terminal with
actual child waits and cleanup. The role deadline connection uses the held
runtime directory descriptor, preserving the same socket endpoint when its
absolute path exceeds the Unix socket address limit.

This checkpoint includes the complete reviewed D37 source dependency composition:
the native producer, daemon receiver, private backend, staged helpers, raw
observation and systemd adapters, full core/pending build modules, and the actual
native/entry control roster with its fixture dependencies. The [evidence index](../assurance/checkpoints/phase1-native-lifetime-2026-10-03.json)
enumerates every member and its exact bytes, unchanged dependencies, review
pins, retained action receipts and individual executed cases.

Actual D37 native, pending and core builds passed. The executed suites reported:

Ran 134 tests in 4.688s

OK

Ran 196 tests in 28.580s

OK

The original source-retention and terminal-retention assertions, full-read and
no-entry controls, closed-descriptor and cleanup assertions, the late-finalizer
positive case, and the added long-runtime-path case passed. Actual GPT-6.1
reviewed the source, launch binding, actual results and complete checkpoint scope.
All original caps and controls were retained; source/tool/native artifact joins
held. The build/proof window was released after the reviewed prefix.

D35 and D36 failures remain in the evidence history. D36's actual exception was
`AF_UNIX path too long`, before either intended retention callback was reached.
D37 repairs that evidenced path; it does not change the assertions to accept a
different failure. The diagnostic copies remain additive and re-raise failures.

This is a development source checkpoint. Later required campaign actions are
listed as unrun in the index. Checked builds and these passing suites do not
establish all imported-module behavior, strict warning cleanliness, formal
proof, release eligibility or Phase One completion.

Whole-workload primary failure preservation remains OPEN: native terminal
failure can still override the process status. Complete startup/codec/native
provider coverage, independent candidate-read/broker/report provenance,
protected custody and positive private admission also remain OPEN. Native
confinement is still Unmeasured; required unavailable-provider error cases are
not waived. Original resource, capability/chain and durable recovery guarantees
still require their specified implementation and evidence.

The complete original campaigns and matching full strict formal proof remain
required: `-U --level=3 --report=all`, strict warnings and every original
body/caller/flow/runtime-error/termination/native-cost scope and proof floor.
No contract, accepted case, coverage or threshold is reduced. No release, tag,
merge, installation, production activation or authority admission is included.
