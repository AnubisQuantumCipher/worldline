# Phase 1 agent rules — retained user instructions

## Active goal instruction

/goal First, save my full instructions verbatim to docs/phase1-agent-rules.md
in your worktree and re-read that file after any context compaction. Then
complete Steps 0 through 4 autonomously, following the AUTONOMOUS DECISION
RULES. Done means: a frozen commit on your branch where the full build,
full proof, full runtime suite, protected runs and actor runs have all been
executed on that exact source; docs/phase1-acceptance-report.md maps every
gate to its evidence and states each gate as PASSED, FAILED-OPEN, or NOT
PERFORMED; any NARROWED CLAIMS are listed; docs/decisions.md records every
decision; and independent acceptance is marked NOT PERFORMED. Do not mark
any gate PASSED without the command, commit and output that prove it. Stop
when that report is complete.

The following user messages are reproduced verbatim from this task. This file was restored late after discovery that the goal-required instruction file was absent; it is not evidence of earlier compliance. After context compaction, reread this file and apply later user steering.

## User message 01a13631-d4f0-7562-ac33-f97bf29cf10d

You are working on WORLDLINE Phase 1 (github.com/AnubisQuantumCipher/worldline).
Phase 1 is OPEN on frozen commit a1bda52. Native, entry and serializer
controls passed; full acceptance has not. Your job is to close the four
remaining blockers below autonomously, in order, with evidence. No human is
available during this run. Another agent session is working in this
repository at the same time.

THE FOUR BLOCKERS
1. Acquisition: the full campaign timed out; a later diagnostic proved an 8G
   memory-limit kill during evidence processing.
2. Authority: production conservation, lifecycle, recovery and evidence
   joins still need complete proof and execution.
3. Hardest problem: automatic full-value/'Old retirement with matching
   GNAT/SPARK support remains unestablished.
4. Final gates: same-source full build/proof/runtime, authentic protected
   and actor runs, and independent acceptance remain open.

ISOLATION (mandatory)
- Create a new git worktree on real disk (not /tmp or tmpfs) on a new branch
  astra/phase1-blockers-<UTC timestamp> from a1bda52. Work only there.
- Never check out, commit to, push to, rebase, or delete any other branch or
  worktree. Never modify files outside your worktree. Never kill processes
  you did not start.
- Small commits, one logical change each, with messages stating what was
  verified.

RESOURCES (40 GB host, shared with another session)
- Every heavy job (acquisition campaign, full GNATprove run, full build) must
  run as: flock ~/.worldline-heavy.lock <command>
  so at most one heavy job runs at a time across all of your agents.
- After acquiring the lock, read MemAvailable from /proc/meminfo. Start only
  if at least 14 GB is available; otherwise release the lock, wait 5
  minutes, and retry. Log each check.
- Set explicit solver memory and timeout bounds. Run every heavy job in its
  own systemd-run scope with an explicit MemoryMax so a failure cannot take
  down the host or the other session.

MULTI-AGENT COORDINATION (you are running with parallel agents)
- One coordinating agent owns the worktree and is the only one that commits.
  Other agents either work read-only or in their own separate worktrees on
  sub-branches, and hand back changes the coordinator reviews before
  applying.
- No two agents edit the same file. Assign file ownership before any
  parallel editing starts.
- Parallel split at the start: one agent on Step 1 (acquisition); one on
  the Step 2 'Old analysis (read-only plus scratch reproducers); one drafting
  Step 0 and mapping which Step 3 obligations depend on 'Old; one reviewer
  agent checking every claim the others make against the evidence rules.
- The reviewer agent's sign-off is internal review only. It never counts as
  independent acceptance.

EVIDENCE RULES
- Every claim is PROVED, MEASURED, TESTED, ASSUMED, or UNVERIFIED, with the
  exact command, commit, and output location. Unknown is not success.
  Missing is not empty is not zero is not pass.
- Failed runs stay recorded. Never overwrite evidence.
- No new features. Anything out of scope goes in OPEN-ISSUES.md.

AUTONOMOUS DECISION RULES (these replace human approval)
- Every decision is recorded in docs/decisions.md: options considered,
  evidence, the choice, the reviewer agent's verdict, and exactly how to
  reverse it. A decision without a log entry is invalid.
- Step 0: docs/phase1-acceptance.md becomes binding once the reviewer agent
  confirms each of the four blockers has a gate with a machine-checkable
  pass condition. Gates may be added later, never removed or weakened.
- Step 2 ('Old): decide in this fixed order.
  1. ACHIEVABLE AS STATED: implement it.
  2. Otherwise, a restated claim is allowed only if the reviewer agent
     independently reproduces the infeasibility on this toolchain from the
     minimal reproducer, the restated claim is written precisely, and what
     it no longer covers is listed under NARROWED CLAIMS in the acceptance
     report. Choose the strongest restatement that proves cleanly.
  3. If neither works, mark the gate FAILED-OPEN with full evidence and
     continue all independent work. Never hide it.
- Never resolve a blocker by deleting or skipping tests, weakening
  contracts, adding pragma Assume or justified checks, widening a proof
  boundary, or raising the 8G limit, unless it is a documented policy change
  backed by measurements AND the reviewer agent concurs. Otherwise it is
  forbidden.
- Do not touch Cosmogony files; record them in OPEN-ISSUES.md.
- Independent acceptance is never self-approved. It stays NOT PERFORMED.

STEP 0 - Acceptance definition
Draft docs/phase1-acceptance.md: the exact gates for "Phase 1 accepted",
derived from the four blockers and the existing phase1 docs and assurance
checkpoints, each with a machine-checkable pass condition. It becomes
binding under the decision rules above.

STEP 1 - Acquisition memory
Find where the 8G limit is set and the diagnostic output. Reproduce the kill
under the same limit. Measure peak RSS per stage of evidence processing and
identify what holds data resident. Make evidence processing streaming or
chunked so peak memory is bounded. Add a regression test asserting the bound.
Done when the full acquisition campaign completes under the unchanged 8G
limit with complete retained evidence and recorded peak memory. Raising the
limit is allowed only under the policy-change rule, and only if streaming
cannot meet the bound.

STEP 2 - 'Old retirement (analysis before implementation)
List every affected contract and the exact unproved or unsupported
obligations, with GNAT and GNATprove versions. Build the smallest reproducer
that shows the problem. Review what earlier branches tried, including
origin/archive/phase1-donors-20261012/*. Evaluate options such as ghost
snapshots, explicit pre-state parameters, restructured postconditions, or a
restated claim. Write docs/old-retirement-analysis.md with a verdict
(ACHIEVABLE AS STATED / ACHIEVABLE WITH RESTATED CLAIM / NOT ACHIEVABLE ON
THIS TOOLCHAIN), the evidence, the design, the exact claim to be proved, and
which Step 3 obligations depend on it. Then decide and implement under the
decision rules.

STEP 3 - Authority proof and execution
Items independent of 'Old may start immediately; dependent items wait for
the Step 2 decision. Close each obligation with GNATprove at the project's
configured level: zero unproved, zero new justified, zero pragma Assume.
Then execute each through the production path, not only unit tests, and
record runtime evidence that Python calls the proved kernel for the decision
instead of deciding itself. Done when conservation, lifecycle, recovery and
evidence joins each have proof output plus production execution evidence
tied to the same commit.

STEP 4 - Final gates on one frozen commit
Freeze a commit. On that exact source run: full build, full proof, full
runtime suite, authentic protected runs and actor runs. Generate the proof
and assurance manifests for that commit. Write
docs/phase1-acceptance-report.md mapping every gate in
docs/phase1-acceptance.md to its evidence, stating each gate as PASSED,
FAILED-OPEN, or NOT PERFORMED, and listing any NARROWED CLAIMS. Do NOT
declare Phase 1 accepted. Independent acceptance stays NOT PERFORMED.

REPORTING
After each step, update docs/phase1-progress.md: what is done, the evidence,
what is open, and what is next. If the same failure survives two serious
attempts, document it precisely, mark it FAILED-OPEN if it is a gate, and
move on to the next independent item.

## User message 01a1368e-2a32-7340-a356-d5404ae52230

Acquisition: the memory fix is verified (peak 6521163776 bytes under the
unchanged 8G cap, no OOM). Record that as MEASURED. The remaining failure is
the timeout, which has had one attempt, not two. After the strict proof
finishes and releases the heavy-job lock, run one diagnostic attempt of the
positive revalidation case only, and classify the timeout before changing
anything:
1. Throttling: record the scope's MemoryHigh and MemoryMax, memory.events
   (high and max counts), and memory.pressure PSI throughout the run. If
   memory.events high is climbing or memory pressure is sustained, the cause
   is reclaim throttling near the cap; fix memory headroom, not the deadline.
2. Slow but progressing: add progress timestamps to the revalidation case
   and record how far it got at the deadline. If progress is steady, measure
   the projected completion time; any deadline change goes through the
   policy-change rule with those measurements.
3. Hang: if progress stops while CPU and I/O go idle, capture stacks of all
   processes in the scope and identify what it is waiting on.
Log the classification and evidence in docs/decisions.md, apply the fix
that matches it, rerun the full acquisition campaign, and update the gate.

## User message 01a13741-b41c-73f1-9502-3e2fefb68b8f

Acquisition: throttling is ruled out (MemoryHigh unlimited, zero memory
pressure). Record that in docs/decisions.md. The timeout is still
unclassified: slow versus hang. Both full runs stalled in the positive
revalidation case only. When the heavy-job lock is free, run ONE
diagnostic of the positive revalidation case alone. It is diagnostic
evidence, not acceptance evidence; the gate keeps its 1000s deadline.
- Emit progress timestamps from inside the case (per stage, per item).
- Let it run up to 3x the deadline under the same 8G cap.
- Sample CPU and I/O for the scope every 30s.
- If progress stops while CPU and I/O go idle for 120s, capture stacks of
  every process in the scope (py-spy dump for Python, gdb/eu-stack or
  /proc/<pid>/stack for native) and record what each is waiting on.
Classify as SLOW (completes, with the measured time and slowest stage) or
HANG (with the blocking point). A HANG is a correctness defect: record it
in OPEN-ISSUES.md and the acceptance report as such, not as a timeout.
A SLOW result goes through the policy-change rule with its measurements.
Then continue the goal.


## Later user storage steering (2026-10-14)

ok here ok here what i need you to do i built duat. the reason why i build it is so my staroage wont delplete doing all this proof work and programming. look how much storage got eating up on the desktop because of all the work you been doing for the past eight hours. i need you to utilizise the hell out of duat and the ipad pad pro. my storage shoud never be eating up or going down ben your have duat at your disposal. you look at it again fighure out how you gon do this because im tired of my storage getting eat up because of my projects. i have a 2tb ipad and i built duat. free up my storage and put it on the ipad and anyhtin you need or any file or info u can just get it back from the ipad. there 700gb full of thias tryomarcy and its shouldnt bee like that if u have duat. do what you need to do then continue with what u were doing

### Explicit exception for transport recovery

Asked: The existing DUAT backup is stuck on a disconnected iPad mount and holds the archive lock. May I stop only `project-vault-backup.service` cleanly, let the existing iPad supervisor reconnect, then run the verified offloads? I need this exception because your earlier Phase 1 instruction forbids stopping processes I did not start.

User answer: Stop the stuck backup and recover the connection

## Later user crash steering (2026-10-14)

A process crashed on this Omarchy machine and I want to know why.

What systemd-coredump recorded:
  process:  alt-ergo
  PID:      434642
  binary:   /home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/libexec/spark/bin/alt-ergo
  signal:   SIGABRT
  time:     Wed 2026-10-14 13:06:31 EDT

Use the diagnose-crash skill: it covers how to investigate, what to report, and
when a crash is worth reporting upstream to Omarchy. If your harness has no skill
mechanism, read the skill files directly and follow them instead:

  /usr/share/omarchy/default/agents/skills/diagnose-crash/SKILL.md

## Later user publication steering (2026-10-14)

all those commits i hope your putting them to github were they belong
