WORLDLINE QUALIFICATION WORKFLOW
(modeled on the NASA X-43A Hyper-X flight systems validation program;
inspired by, not certified to, DO-178C/DO-333)

0. SCOPE. Each phase has one tightly focused goal written in one sentence.
   Anything not needed for that sentence is out of scope and goes to the
   next phase's backlog. No phase may add code for a later phase.

1. VALIDATION PLAN FIRST. Before any implementation, write
   docs/<phase>/validation-plan.md: every requirement (ID, one sentence),
   its target SPARK level (PLATINUM for pure decisions, GOLD for authority
   properties, SILVER plus a GOLD boundary property for support code), the
   test or proof that validates it, the failure modes to inject, and the
   pass condition. No code is written for a requirement without a plan row.

2. TRUTH DATA. For every DECISION requirement, write an executable
   reference model from the requirement text, never from the
   implementation. Generate a truth data set (exhaustive for finite
   domains, otherwise systematic plus randomized with fixed seeds).
   Retain it.

3. IMPLEMENT AND PROVE (unit level). Implement in SPARK. GNATprove at the
   project level on the unit. Zero unproved, zero justified, zero pragma
   Assume. Postconditions copied from the body do not count as PLATINUM.

4. KERNEL-IN-THE-LOOP. Build the real shared library. Drive it through the
   real C ABI and Python bindings against the full truth data set. Any
   mismatch is a defect in the implementation, the binding, or the
   reference, and must be classified before continuing.

5. FAILURE MODES AND EFFECTS TEST. Inject every planned failure (SIGKILL
   at each durable step, power loss simulation, disk full, read-only fs,
   corrupt store, stale or cross-run evidence, missing or changed
   verifier, same-uid tampering, OOM, timeouts). Each must produce the
   specified refusal or recovery. Each becomes a permanent regression.

6. BUILD-UP INTEGRATION. Integrate one subsystem at a time onto the last
   qualified build. After each integration, rerun steps 3 to 5 for
   everything touched plus the full regression. Never integrate two
   subsystems in one step. A commit over 2,000 lines needs a written justification.

7. PLUGS-OUT TEST. Install the candidate exactly as a user would, with no
   test environment variables, test hooks, harness libraries, or skipped
   suites. Run the end-to-end scenario, including the positive success
   path, within production limits (the shipped unit's MemoryMax and the
   stated deadlines). A skipped test is a failed test.

8. CAPTIVE CARRY. Full production rehearsal on a clean host: install,
   capture PRIME, run agents, evaluate, request collapse, and stop
   immediately before the authoritative exchange. Verify every receipt,
   identity, and checksum. Then one real collapse and one real return.

9. QUALIFICATION. A qualified build is one exact commit that passed steps
   3 to 8 with a complete, regenerated proof manifest (real check count,
   current source hashes) and green contract pins. Record it in a Version
   Description Document: commit, tree, toolchain versions, proof counts,
   test counts, failures injected, open items, non-claims.
   Every other build is NOT FOR FLIGHT and is labeled so.

10. DELTA QUALIFICATION. Any change after qualification requires rerunning
    the affected steps plus the full regression and a new VDD. "Small"
    changes are not exempt.

11. SEPARATION OF ROLES. The builder verifies (steps 3 to 6). A different
    model from a different vendor validates (steps 7 to 9) and has not
    seen the builder's reasoning, only the plan, the code and the
    evidence. The operator signs the VDD. No party approves its own work.
    AI review is recorded as AI review, never as independent human audit.

12. FLIGHT 1 RULE. When the operating profile changes (data volume,
    resource limits, hardware, toolchain, deadlines), every inherited
    assumption, model, threshold and test is re-validated for the new
    profile before it is relied on. "It worked before" is not evidence.

13. FAILURES ARE KEPT. A failed qualification stays recorded. Repair
    produces a new candidate, never an edited history.

Phase exit: the qualified VDD, the validation plan with every row marked
PASSED with evidence or explicitly deferred with reason, and the
independent validation report.
