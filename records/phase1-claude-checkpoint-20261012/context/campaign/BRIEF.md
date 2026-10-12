# WORLDLINE Phase One — strict SPARK proof campaign: shared brief for unit owners

You own a disjoint set of Ada units inside ONE git worktree of the Source21 candidate. Your job is
to bring every unit you own to a clean strict proof WITHOUT changing what the code does.

## Where things are
- Your worktree: given in your task (call it WT). It is a full checkout of the `source/` repo on your
  own branch `campaign/<name>`. Edit ONLY the files named in your task. If a fix truly needs another
  file (a spec you do not own, a caller elsewhere), STOP that change and report it; do not edit it.
- Never edit: `runtime/worldline/proof_manifest.py`, `CHANGELOG.md`, `proof-manifest.json`,
  anything under `tests/`, any `.gpr`, any C file.
- Evidence directory for your runs: given in your task (outside the git tree). Save stdout+stderr of
  every gnatprove/gprbuild/test run there with a one-line `meta` (command, exit code, duration).
- Toolchain: run `source ~/opt/gnat/env.sh` in every shell. GNAT FSF 16.1.0, gnatprove 16.1.0.
  Prefix every gnatprove/gprbuild/test command with the memory cap wrapper:
  `CAP=4G /home/sicarii/.cache/anubis-item21/capped.sh <command...>`
- Load the skills `ada-omarchy` and `spark-users-guide` with the Skill tool before editing. The file
  `~/.claude/skills/ada-omarchy/reference/proof-gotchas.md` lists prover refusals already met here.

## Definition of done (per unit you own)
From WT:
```
source ~/opt/gnat/env.sh
CAP=4G /home/sicarii/.cache/anubis-item21/capped.sh gnatprove -P core/worldline_core_sources.gpr \
  -u <unit>.adb --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on -j2
```
must exit 0 with ZERO unproved checks and ZERO justified checks for the unit (its spec and body), and
no legality errors. Use `--mode=flow` as the fast inner loop, then `--mode=all`. Read the summary at
`obj/core/gnatprove/gnatprove.out` (Total row: last two columns are Justified / Unproved). Warnings
("statement has no effect", "unreachable", "initialization has no effect") should also be cleared
when the fix is behavior-preserving and local; report any you leave.

## Absolute rules (these are the operator's, not negotiable)
1. NEVER add `pragma Assume`, `pragma Annotate (GNATprove, False_Positive|Intentional|...)`,
   `SPARK_Mode => Off`, `pragma Warnings (Off)`, or any other justification/suppression.
2. NEVER weaken anything: do not remove or loosen a Pre, Post, Contract_Cases, Type_Invariant,
   predicate, range, Loop_Invariant that states a property, check, refusal branch, `return False`
   path, roster entry, accepted case, or test. A Post may only be added or strengthened; a Pre may
   only be kept or weakened (and only when the body is total for the wider domain).
3. Observable behavior must be byte-identical: same inputs → same results/encodings/return codes;
   the C ABI (`Convention => C`, record layouts, exported names) is untouchable.
4. Allowed, behavior-preserving repairs: `pragma Loop_Variant`, `pragma Loop_Invariant`,
   `Subprogram_Variant` for recursion, intermediate `pragma Assert`, ghost functions/lemmas,
   splitting a subprogram, hoisting a variable-dependent bound into a `constant` (E0007), moving a
   Loop_Invariant to the top of the loop body (before any declare block), converting a function with
   side effects into a procedure with an `out` parameter (same semantics, callers in YOUR files
   updated), initializing an object whose value is overwritten before every read (or
   `with Relaxed_Initialization` plus `'Initialized` obligations), replacing `(others => <>)` /
   `[... => <>]` on components without defaults by an explicit full-value aggregate that is
   overwritten before use, replacing `Loop_Variant (Structural => ...)` by a numeric variant.
5. If a check cannot be proved without weakening: leave it UNPROVED, and report the exact check
   (file:line, message), the prover's counterexample if any, and your analysis. An honest residual
   beats a laundered proof.
6. If you find a genuine defect (the code is wrong for some input), report it with the triggering
   input. Fix it only when the intended behavior is unambiguous from the surrounding code and its
   tests, and say explicitly that behavior changed and why.
7. Preserve comments; keep the file's style (compact, no reformatting of untouched lines).

## Tests
After body changes, rebuild the library and run the targeted Python tests that mention your unit
or its predicates (grep -l in `tests/`), from WT:
```
CAP=4G /home/sicarii/.cache/anubis-item21/capped.sh gprbuild -q -p -P worldline.gpr
env -u WORLDLINE_DAEMON_UID WORLDLINE_CORE_LIB=<WT>/lib/libworldline_core.so WORLDLINE_BUILD=checks \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<WT>/runtime:<WT>/tests TMPDIR=/home/sicarii/.cache/workflow-tmp \
  XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  python3 -m unittest <test_module> -v
```
Also run `./bin/worldline_core_tests` and `./bin/worldline_core_fuzz` if the build produced them and
your unit is Ada-tested. Note: if gprbuild recompiled a body but did not relink the .so, clean first
(`rm -rf obj lib/libworldline_core.so lib/*.ali`) and rebuild.

## Commit
When all your units are done (or you have exhausted honest options), commit on your branch:
```
git -c user.name=sicarii -c user.email=sic.tau@pm.me commit -q -m "<summary>

<body: one line per unit with before→after counts>

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
(From 2026-10-12 06:30Z the session model is Opus 5.5; use this trailer for every new commit.)
Do not push. Do not merge. Do not touch other branches.

## Report back (final message)
Per unit: before → after (legality errors / flow findings / unproved), each change as `file:line —
what — why`, residual unproved checks with analysis, defects found, any spec (.ads) contract text you
changed (the lead must refresh CONTRACT_PINS for those), test commands with results, commit hash.
Be exact and terse; no praise, no padding.

## Addendum (2026-10-12 04:05Z) — lessons from the first wave; these are binding
- MEMORY, not CPU, is the binding constraint on this 31 GB machine: the kernel OOM killer has killed prover scopes. Run at most ONE
  gnatprove at a time, with `-j2` and `CAP=3G`. A run that ended with exit 137/-9 or whose scope shows "Failed with result 'oom-kill'"
  in `journalctl --user` is invalid: rerun it. Never run proofs against a copy of the untouched baseline (pre-existence of every
  unproved check is already established by the lead's surveys).
- `gnatprove.out` and gnatprove's exit code are session-wide (stale `.spark` files of other units count): before a definition-of-done
  run do `rm -f obj/core/gnatprove/*.spark` in your worktree.
- GNATprove 16.1 treats two occurrences of the same string literal as distinct terms: a precondition established with
  `F (Data, X, "name")` is not provable against a second `"name"`. Hoist the span (or the literal) into a constant used by both the
  guard and the call. Level-3 timeouts are flaky under load: rerun a timed-out check once before recording it.
- Contract-less local helpers are inlined by GNATprove at every call; a big body can produce a multi-MB VC file that pins gnatwhy3 at
  the memory cap. Giving such a helper its true `Global => null` (and a Post when needed) stops the inlining.
- Record layouts: `X.C'Position` is an uninterpreted term for the prover. Pinning offsets as named numbers guarded by
  `pragma Compile_Time_Error` against the real `'Position` (the technique the project's *_C_API bodies already use) is allowed: it is
  byte-identical on this target and fails the build closed if the layout changes.
- String building (`A & B` where the lengths come from the arena): the `Natural'Last` range checks are real but untestable. The ONLY
  admissible repair is a guard that refuses exactly the inputs on which the ORIGINAL would have raised Constraint_Error, i.e.
  `if S'Length > Natural'Last - <exact literal length being appended> then return False;` placed before the concatenation. A cap set
  below that point (any "reasonable maximum") is a forbidden value cap, even if no real input comes near it.
- Totalization of an error path is allowed: replacing a path on which the original raised an exception (out-of-range index, failed
  predicate precondition) by an explicit refusal with the same conditions is behavior-preserving for every input the original accepted.
  Say so in the commit body for each site.
- Empty arrays: `Data'First` of an empty `E.Bytes` may lie outside `E.Count`; write spans of possibly-empty arrays as
  `(if Data'Length = 0 then (1, 0) else (Data'First, Data'Length))`-style, or guard, never assume `'First >= 1`.

## Addendum 2 (2026-10-12 08:40Z) — further binding lessons
- Memory cap: CAP=4G per gnatprove (6G only after a run was OOM-killed at 4G; say so in the report). Still one gnatprove at a time.
- The checks build compiles with -gnata: every Pre/Post/Loop_Invariant/Loop_Variant/Assert and ghost code you add EXECUTES at run
  time in the original runtime roster. Keep added annotations O(1) per evaluation (no quantifiers over whole arrays inside loops, no
  recomputation of expensive functions); a Loop_Variant over SPARK.Big_Integers raises Program_Error at run time under -gnata — use a
  bounded `for` loop with `exit when` instead. A contract that turns a linear routine quadratic under -gnata is a regression
  (the original roster has deadlines).
- Two owners independently found: contract-less local helpers are inlined at every call and blow up VCs; give them their true Global
  and Posts.
