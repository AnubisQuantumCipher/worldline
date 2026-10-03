# Phase One native process-filter checkpoint — 2026-10-03

The examiner-only native constructor now installs a fixed Linux AArch64 seccomp
filter before Python initialization. It refuses direct process creation and
execution while preserving same-thread-group threads. It refuses ptrace and
uses the installed libc fallback for clone3. Installation failure ends the
examiner before Python entry. Native status retains the installed instruction
description as a self-report; daemon-held startup/preparation status samples
retain kernel mode, count and NoNewPrivs separately.

D32's native build and component action passed:

Ran 99 tests in 2.865s

OK

The independently reviewed local D32 source also passed pending/core builds and
the entry-component action (190 tests, all OK), including live threaded private
evaluation. Actual GPT-6.1 reviewed the design, exact source, launch binding and
results. All original cases were retained. The complete native component source
and tests in this checkpoint match the executed bytes. The broader runtime
integration remains in the pinned local D32 frame and is not published by this
component checkpoint.

[The evidence index](../assurance/checkpoints/phase1-native-kernel-filter-2026-10-03.json)
records exact artifacts, retained action results, all native case outcomes and
review pins. The resource window is released. D31's preparation-log mismatch was
caught before any target execution and remains retained; D32 corrected output
placement without changing source, launch controls or caps.

Phase One remains OPEN. Neither a kernel mode/count sample nor native instruction
self-report proves lifetime confinement or independently identifies the installed
BPF program. Native confinement remains Unmeasured. Complete startup, frozen
alias metadata, codec/native-provider coverage, original accepted generator
domains, candidate-read/broker/report lifetime provenance and protected custody
remain required. The original positive admission requirements remain unresolved.

All remaining original campaign and fault cases, independent compiled review and
matching full strict formal proof remain required: -U --level=3 --report=all,
strict warnings and original floors/body/caller/flow/runtime-error/termination/
native-cost scope. The checked core build is not a proof or warning-clean claim.
No contract, accepted case, cap, coverage or evidence requirement is reduced.
No release, installation or integrated acceptance is claimed.
