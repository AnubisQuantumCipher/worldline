# D161 actual compatibility source — initial implementation review candidate

SOURCE PREPARATION ONLY. No derivative is attributed to an upstream commit.
The original AdaCore/gnatcoll-core commit remains
`1d4374ae9187fd14d42ca99a3deb0ab2ff1ebc55`; its preserved body is
`original/gnatcoll-boyer_moore.adb`, SHA256
`8559ffbde746e34833294f631548b4536606ca29bacd849213ab9842d4018ece`.
The exact three-site derivative is `derived/gnatcoll-boyer_moore.adb`, SHA256
`f0843c5a17d7cd01901828b46a291649349131ce55592ae72155d9ecf966143c`.
`prospective.diff` is the unchanged reviewed patch. Original source cuts, failed
W, dependency projects, pins, strict switches, policy caps and deadlines are unchanged.

The binding design is the approved D160 v2 lifecycle specification identified
in input-references.json. This package is the new D161 actual-source candidate;
its initial independent pair/judge review has not occurred. It has at most one
subsequent evidenced revision, without resetting D160/D158/D159 (all zero).
No F7 review is performed or implied. Storage remains HUMAN_PAUSED.

The threat model for this finite fixture includes wrong search values, incorrect
case folding/index origin, first-match selection, incompatible repeated public
Free/reuse, checked accessibility/finalization, consumer separator state and
malformed/truncated/unknown/duplicate output. The fixture has no effect authority,
external mail, file mailbox, parsing call, process spawn, concurrency or ownership
copy in source. Compiler-created parameter temporaries remain a separate obligation.
This finite domain excludes arbitrary mail/lengths, allocation-failure injection,
aliased Pattern clients, Search after Free and real concurrent users. Those product
obligations are not waived, repaired or proved by this package.

Each lifecycle source Pattern starts fresh; Compile precedes Search; Free/Free
precedes scope exit and C10 reuse. C01 alone omits Case_Sensitive. Empty motif is
fresh C08 and returns -1 by the pinned body's convention. Search values and an
independent bounded ASCII oracle are both reported against fixed expectations.
The oracle uses ascending absolute starts (at most ten) and at most six character
comparisons per start; case folding is ASCII A..Z only. Its contracts/invariants
are authored source, not discharged proof obligations.

The two consumer buffers are library-level aliased Strings, fixed exact bytes
and bounds in Input_Buffers and case-roster.json, and remain unmodified. Both
calls pass On_Close => null. Box and Cursor scopes end before consumer reporting;
no static buffer is given to default Free_String. Accessibility and finalization
must be tested with checks enabled. The unchanged consumer From_Pattern elaborates
once before lifecycle execution and remains persistent. No manual Free of it occurs.

Normal completion emits exactly 25 canonical LF-terminated ASCII rows: 11 SEARCH,
11 FREE, D01, D02, COMPLETE. The validator accepts the exact ordered bytes only;
unknown/malformed/duplicate/missing/truncated/extra rows or bytes fail closed.
Maximum input is 16 KiB, maximum row 128 bytes. Wrong expectations and missing row
controls are SOURCE ONLY. No validator module or fixture has been run/imported.
Validator I/O deadline and retained terminal/log evidence belong to the future
admitted harness. A syntactically valid transcript alone proves no native execution.

Result rows preserve returned actual/expected/oracle values before comparison
failure propagates. FREE means two public normal returns, never private nulling,
release or allocator proof. Consumer rows are emitted after lexical finalization.
Any exception or failed assertion prevents COMPLETE and produces failure status;
normal execution checks the 24-row prefix before completion. Elaboration failures,
I/O failures and partial allocation/exception cleanup remain runtime obligations;
there is no success recovery after a failed case. A future outer harness must
retain bounded stdout/stderr, partial rows, exit/signal/time/resource receipts.
A bare exit zero, incomplete stdout or uncaptured exception is not a pass.

Fixture GPR imports unchanged gnatcoll_core.gpr through later controlled project
search paths. Its sentinel object/exec defaults are NOT an admission guard and
must never be used for execution. No configuration, staging, wrapper or integration
is authored here. Later admission must retain exact CGPR, normalize/match selected
configuration, establish consumed runtime/compiler/link closure and controlled
absolute object/exec paths, and confirm this derivative alone replaces the body
in a newly registered working source staging area. Do not edit sealed source cuts.
Strict warnings-as-errors, assertions, range/access checks, overflow/validity and
stack checks remain enabled. No suppressed checks or unchecked-access workaround.
The fixture GPR alone does not strengthen the imported dependency's effective flags;
future composition must inspect those and preserve the required strict profile.
Fixture -gnata does not retroactively enable assertions in separately compiled
GNATCOLL dependencies or establish execution of canonical intrinsic Post. The
unchanged dependency build argv/assertion policy requires its own retained evidence.

Evidence labels: source identities/textual patch correspondence and finite literal
arithmetic may be OBSERVED by the recorded static commands. Native legality,
warning cleanliness, assertions/accessibility, dispatch, compiler/intrinsic behavior,
pool selection, stack/allocator accounting, functional runtime outcomes, allocation
release and whole-process fit are UNPROVEN/UNRUN. No PROVED or TESTED-native claim.

Next sound step: fresh D161 actual-source reviews and separate judge on this exact
manifest. Only an approved, separately registered composition may select the exact
CGPR/wiring and admit bounded compilation and controls. Acceptance then requires
clean strict dependency and fixture builds, exact artifact/config/flag identities,
all complete results, failing wrong-expectation/missing-row controls, actual retained
terminal/resource evidence and separate intrinsic/allocator evidence. Whole-phase
build/proof/runtime/protected/actor/independent F7 obligations remain open.
