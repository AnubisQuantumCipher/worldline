# Open issues outside this run's repair authority

- Cosmogony files are unchanged. WORLDLINE aggregate library currently includes Cosmogony interfaces;
  any failed dependency obligation in those sources stays open with evidence. This run cannot repair
  it by editing them or excluding their original proof/build scope.
- Machine-wide installation, deployment, other checkouts, branch publication and vault/SIA state
  mutation are outside this run's worktree-only instruction. No such action establishes acceptance.
- Independent acceptance remains NOT PERFORMED by explicit instruction.


## Diagnostic observer crash and isolation incident

MEASURED on `d3c88bbbaa0f4b1f7910de9706a6cdee9ab39ded` plus the retained D22 documentation diff: the disposable GDB stack-capture fixture observer encountered allocation failures, and busy control PID `4015874` exited by SIGSEGV. The host crash handler wrote an external core under `/var/lib/systemd/coredump/`; the exact read-only query and output are retained in `records/phase1-blockers/diagnostic-observer-core-incident-v1/`. This is a worktree-isolation violation. The external artifact remains untouched. It is a diagnostic-tool failure, not evidence that the positive revalidation case hangs. Native stack qualification and crash containment remain open until measured corrective controls pass. No acquisition deadline or memory cap was changed.
