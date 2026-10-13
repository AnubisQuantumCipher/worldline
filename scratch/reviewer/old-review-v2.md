# Corrected minimal mechanism re-review

Actual GPT-6.1 internal review; independent acceptance NOT PERFORMED.

Exact command: `python3 scripts/phase1_heavy.py --out scratch/reviewer/old-independent-scope-v2 --timeout 10m -- bash -c 'source /home/sicarii/opt/gnat/env.sh && python3 scratch/reviewer/probe_driver.py scratch/reviewer/old-independent-results-v2'`.
Metadata/source hashes/actual commands/tool versions/raw reports: old-independent-results-v2/. Actual memory admission/cap/scope state: old-independent-scope-v2/.

TESTED: controlled_legal adds the suggested Elaborate_Body to resolve E0003; build succeeds. GNATprove rejects Ada.Finalization.Controlled/Snapshot as not allowed in SPARK due to controlled types.
TESTED: fresh_old_legal uses unconditional Capture(Text)'Old.all=Text; build succeeds. Strict GNATprove proves value postcondition but reports medium resource or memory leak might occur: call to allocating function inside assertion leaks some resource or memory. Proof command exits nonzero under checks-as-errors.

Verdict: these exact mechanisms fail the installed strict SPARK/full-value automatic-retirement requirement. The records support these precise exclusions only, not a theorem that every possible design satisfying the original conjunction is impossible. A narrowed explicit-prestate/manual-retirement mechanism must keep compiler-created automatic Old retirement, exceptional postcheck cleanup, general nonlimited independent full values, full queue and production acceptance open. No O1 PASSED claim authorized.
