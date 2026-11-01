# Bounded lifecycle and dependent-consumer specification — revision v2

SPECIFICATION ONLY; every product behavior below is UNRUN/UNPROVEN. No Ada fixture, native test, worker, guard or executable wrapper is authored here. Later code must use strict warnings and enabled range/overflow/access checks/assertions, explicit error propagation, bounded loops, short single-purpose routines and independent side-effect-free oracles. No recursive control, authority, unsafe pointer trick, external mail or destructive operation is needed.

## Exact public API and ownership

Pinned GNATCOLL.Boyer_Moore exports private type Pattern; Compile (Motif : in out Pattern; From_String : String; Case_Sensitive : Boolean := True); Free (Motif : in out Pattern); Search (Motif : Pattern; In_String : String) return Integer. Its comment specifies match location or -1. Max_Pattern_Length = Integer'Last is not a fixture allocation allowance. There are no public Pre/Post contracts specifying ownership or every lifecycle boundary.

Select one combined lifecycle/consumer executable per required clean build profile. Package elaboration creates the unchanged persistent consumer From_Pattern before lifecycle cases run; one lifecycle-local Pattern is additionally live during a case. The one-owner/no-initialized-copy/no-concurrency constraint applies separately to each Pattern. No source change or manual Free of the persistent consumer Pattern is proposed. Start fresh; Compile, Search, Free before leaving scope or recompiling. Search only a compiled Pattern, never a freed or uncompiled one. Repeated Free is a source/intrinsic-supported control expecting no exception, not a new documented API guarantee. Empty pattern gets a fresh object, never overwrites live allocated storage. Motif <= 6 ASCII characters; text <= 10 characters, positive lower bounds 1 or explicit 5. Empty text is String (1 .. 0). No allocation-failure injection or alias misuse in this fixture.

## Lifecycle cases and oracles

Each row starts fresh. Execute Compile, required Search, Free, Free; require explicit completion without exception. Default Case_Sensitive is exercised only by C01; every other row supplies the Boolean. Every expected integer is also checked by an independently authored bounded first-match oracle (<=10 candidate starts, <=6 character comparisons each, ASCII A..Z folding only when False). Oracle returns absolute String indices and -1 for no match; it never calls Boyer-Moore. Empty motif means no match here because the pinned body explicitly defines that branch, not because general string-search convention mandates it.

| ID | Motif / mode | Search text and exact bounds | Expected |
|---|---|---|---:|
| C01 | "aba" / default True | "zzabazzaba", 1 .. 10 | 3, earliest match |
| C02 | "aba" / True | "zzabb", 1 .. 5 | -1 |
| C03 | "AbC" / True | "xxabc", 1 .. 5 | -1 |
| C04 | "AbC" / False | "xxaBc", 1 .. 5 | 3 |
| C05 | "a" / True | "a", 1 .. 1 | 1 |
| C06 | "abcdef" / True | "abc", 1 .. 3 | -1 |
| C07 | "aba" / True | String (5 .. 11) = "zzabazz" | 7 |
| C08 | "" / True, fresh Pattern | "abc", 1 .. 3 | -1 |
| C09 | "aba" / True | String (1 .. 0), empty | -1 |
| C10 | "aba" / True | "aba", 1 .. 3 | 1 |

C10 continues after Free/Free: Compile same Pattern with "Bc", False; Search "xxbC" (1 .. 4) expects 3; Free/Free. No Search occurs between freeing and recompiling. C03/C04 are mode controls; C01 covers earliest match, C06 too-long motif, C07 non-1 absolute indexing, C08 source-defined empty motif, C09 empty text. Wrong result, unexpected exception/warning, timeout, missing row, incomplete output or nonzero status is FAILED.

Public completion/reuse cannot expose private null fields or prove release of both allocations. Later source/intrinsic lowering inspection must separately map Offset_Array_Access/Good_Suffix and String_Access/Motif to their exact pools/deallocations, including null actual semantics, canonical Post/Depends and actual assertion policy. If separately registered allocator telemetry is available, bound and identify it before use; correlate both lifecycle allocations/releases and return to the post-elaboration baseline, which includes the persistent consumer Pattern. Do not claim that the persistent Pattern is freed or that whole-process allocation returns to zero. Zero exit or flat RSS cannot replace that evidence. No private representation cast or extra production API is permitted just to get a green result.

## Dependent core consumer

Use unchanged GNATCOLL.Email.Mailboxes.Mbox and its public Open (Self : in out Mbox; Fp : access String; On_Close : Destructor := Free_String'Access), First returning Cursor'Class, Has_Element and Next. The exact D01 and D02 caller-owned aliased String buffers must be declared at library level, not as local stack objects merely outliving a Box. Their accessibility must be legal for Open's conversion to the library-level GNAT.Strings.String_Access with all checks enabled. Pass On_Close => null; scope each Box/cursor so finalization completes before any buffer mutation or fixture termination. Do not use Unchecked_Access, unchecked conversions, suppressed checks, or a deeper-accessibility workaround. Never let default deallocation own a static/stack buffer. No filename overload, real mail, Get_Message, factory callback or parser allocation is needed. Existing tagged cursor dispatch remains part of this boundary and must be checked; do not add new dispatch machinery.

D01 exact bytes: "From a" & LF & "Subject: A" & LF & LF & "one" & LF & LF & "From b" & LF & "Subject: B" & LF & LF & "two" & LF. Length 47, bounds 1 .. 47. LF & "From " begins at index 24; second "From " begins at 25. First must give Has_Element=True; one Next -> True; second Next -> False. Observe at most three states; never use an unbounded iterator loop. This exercises elaborated From_Pattern, Search on a non-1 slice and match-to-message offset.

D02 exact bytes: "From a" & LF & "Subject: A" & LF & LF & "one" & LF. Length 23, bounds 1 .. 23. First -> True; one Next -> False. This exercises no next separator. Buffers are longer than the initial five-character read and begin with "From ". Fresh Box/cursor per case, with lexical finalization before the aliased buffer dies. Do not parse arbitrary mail. These public iterator outcomes do not prove Pattern deallocation because consumer From_Pattern is long-lived.

The author initially miscounted D01/D02/position in an unwritten draft; draft-static-failure.json retains the failed pre-write arithmetic check. Corrected counts/position are statically checked against independent literal bytes in this packet. Later fixture authors must recompute them before running a test so malformed test expectations cannot be mislabeled product failures.

## Finite resource/result contract

One combined executable per required clean profile is mandatory for this proposal. The following normal-completion accounting covers the two specified Pattern sources, not the whole process:

| Contribution | Compile calls | Nonempty Compile calls | Allocation operations | Maximum simultaneous Pattern objects | Maximum designated heap blocks |
|---|---:|---:|---:|---:|---:|
| Lifecycle-only C01–C10 plus C10 reuse | 11 | 10 | 20 | 1 | 2 |
| Persistent consumer elaboration From_Pattern | 1 | 1 | 2 | 1 | 2 |
| Combined specified Pattern sources | 12 | 11 | 22 | 2 | 4 |

The consumer's elaboration calls Compile once with six-character LF & "From ", before lifecycle tests; its allocated String and suffix table persist throughout them. At lifecycle motif maximum length 6, designated payload is <=6 Character units +7 Offset units per Pattern, so the two together have <=12 Character units +14 Offset units, excluding allocator headers/alignment. Sequential lifecycle cases do not remove consumer allocations.

Account separately for both Pattern records (each 256 Offset entries plus access values/Boolean/alignment), temporary Compile prefix arrays (<=12 Offset units for the one active Compile; elaboration and lifecycle compiles do not overlap), two library-level aliased buffers, cursor/Box records and finalization, fixed result/oracle storage, and all other library/runtime allocations. The 22 operations count only these two Pattern sources; no whole-process allocation count or exact byte bound is established. Require actual type/storage-size, generated stack/allocator/runtime accounting and admitted measured resource results before judging whole-executable fit.

Lifecycle deallocation must return its allocation contribution to the post-elaboration baseline. The consumer Pattern is not freed by these controls; never infer whole-process-zero allocation or a persistent-Pattern-free result. Public observations alone establish neither internal pointer nulling nor actual storage release.

Fixed case/results; <=100 total API calls including the one consumer-elaboration Compile and consumer controls; at most two caller buffers of <=128 bytes each and three cursor states per dependent case. Run one case at a time, no fixture-spawned process. stdout <=16 KiB, stderr <=16 KiB, all fixture result/metadata <=64 KiB. Prospective invocation threshold <=64 MiB and <=5 seconds, one invocation of the combined executable per required clean build profile. These are UNMEASURED fail thresholds within unchanged 8 GiB/swap0 and shared 1500/1590 envelope, not extra resources or a profile increase. All objects/binaries/logs count within existing output/descendant ceilings. If composition cannot fit, stop for separate disposition.

Retain fixture source/hash/roster, exact config/runtime/compiler/linked artifact identity, flags/checks/assertion policy, every expected/actual/completed row, exceptions, full bounded logs and resource/terminal receipts. Add separately registered harness controls: intentionally wrong expected value must fail; missing/truncated row must fail closed. Do not mutate library code or execute undefined memory use as a negative. A passing finite fixture is TESTED evidence only, not proof of all inputs, allocator behavior, allocation-failure cleanup, alias ownership or whole-system safety.
