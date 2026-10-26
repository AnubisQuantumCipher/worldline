# Replay target-only compiler legality recipe

PREPARED, NOT RUN. This directory contains no build, proof, or test result.
Production source, original contracts, pins, toolchains and existing objects
remain unchanged. Only the root may allocate and execute this diagnostic.

The GPR references the actual sibling candidate and actual core specifications.
It imports the same absolute private SPARKlib and Attest projects. There is no
source copy, shim, alternate decision kernel or whole-project build claim.
The dependency specs are sufficient for this target's context; their bodies
are deliberately not compiler targets in this legality-only command. This is
not proof coverage or a reduced replacement for the original required build.

The installed gprbuild --help was read without compiling: -c means compile
only, -u means only the given files, and -p creates missing object/library/exec
directories. Consequently this command uses -c -u -j1 and DOES NOT use -p,
-U, -r, a binder, a linker, or a prover. Root must create only this directory's
new obj directory after safe admission. No existing production Object_Dir is
reused or relocated. Private SPARKlib is explicitly selected as prebuilt.

The exact argv and environment requirements are in recipe.json. -gnatc requests
semantic checking without code generation. The GPR retains the checked core
compiler switches and adds -gnatwe to reject warnings; no warning/assertion is
suppressed. Do not silently remove a strict switch when diagnosing a refusal.

Before launch, root must verify the GPR, all listed source/import identities,
and the referenced134-file private manifest against current files; capture
installed tool paths/versions and the actual argv. Installed runtime specs are
toolchain inputs, not independently qualified by this source-only recipe.
Any source/project identity change requires a successor recipe. Do not infer
compiler legality from this preparation or from prior source review.

Use the existing serialized8GiB/swap0 wrapper and original reserve/admission
rules; keep stdout/stderr, result, source recheck and terminal scope evidence
on disk. TMPDIR selection requires the separately reviewed RAM-output plan;
this recipe neither mounts RAM nor authorizes ephemeral evidence loss.

Expected output is one target's semantic-check metadata, possible ALI/GPR
switch/configuration files, and diagnostics. No executable/native object or
whole dependency build is intended. That is an expectation, NOT an enforced
byte limit or demonstrated output roster. No output-size estimate is used as
admission evidence: actual root resource review must fit both compiler scratch
and retained failure evidence. With roughly50MB margin, the existing driver's
reserve+60MB admission is NOT met; this recipe does not lower that guard.

After any allocated run, require the exact target and actual compiler command,
all strict switches, zero exit, zero warnings and unchanged source hashes.
Retain a nonzero result, diagnostics and all partial output as failure evidence.
Check imported project/output identities for unexpected writes before claiming
target-only execution. Stop rather than allowing automatic dependency rebuilds.
No successful binding, integrated library, functional equivalence, Plan bridge,
whole proof, original runtime, C1-C4 or Phase One acceptance follows from legality.
