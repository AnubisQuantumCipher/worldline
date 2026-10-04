# Scratch frame v6: change plan (lead working notes; not a review, grants nothing)

**Status.** The actual gpt-6.1-sol review of frozen v5 is still running. This plan will be completed from its final
findings before any v6 code is frozen. v6 then goes to its own actual gpt-6.1-sol review.

**Sources of changes, kept apart.**
- **(G)** Findings of the actual gpt-6.1-sol v5 review. These are authoritative.
- **(A)** The lead's own author-side engineering.
- **(H)** Points first seen in the non-compliant Claude pre-read (`historical/…NONCOMPLIANT.md`). These are
  author-side observations only. Any change made for one is the lead's own engineering and is disclosed as such.

## (G) v5 review, items 1–3 so far

- **V5-B01. `observe_tree` leaves already-observed files stale.**
  - Record every file's complete `stat_key` together with its entry identity.
  - At the end of the walk, re-reach every file through the held directory chain, re-stat it without following, and
    require the same complete key.
  - This covers recorded files and excluded generated files alike.
  - Ctime changes on any content, mode or link change, so a later change is caught. The metadata-granularity
    residual was ruled acceptable as documented.
- **V5-B02. A location check followed by a separate fd-relative mutation is not location-atomic.**
  - No POSIX primitive makes "write only if this directory is still at that name" atomic against a same-user
    renamer.
  - v6 will state and enforce the inode-ownership invariant. Every frame mutation goes through a held descriptor of
    an inode the frame itself created and authenticated, or the documented shared window. So no foreign inode is
    ever created into, written or chmod'ed.
  - A relocation of the frame's own inode is detected by the post-check and refused.
  - v6 will ask for an explicit ruling: is this "own-inode relocation, detected and refused" acceptable as a
    residual, given that the same same-user actor could move those records after the fact anyway?
  - If not, the alternative is atomic name resolution in the mutating call (`openat2` with `RESOLVE_NO_SYMLINKS`
    from `/`, through ctypes). That still has a non-atomic `mkdirat` step. The plan must say which window remains.
- **N11.** Committed-primary marker, or explicit archival interpretation of a fully written but failed primary.
- **N12.** Validate each participant record's schema and its required pid/wait fields before classifying it.
- **N13.** Recompute the disposition after late close errors, and record them.
- **N14.** The dispatch exit status reflects its own failure and interrupts.
- **V4-required-change-5.** FRAME.md must not present custody or no-alias coverage as closed.

## (H)/(A) author-side items (disclosed)

- **H-S1.** Handled signals stay blocked from just before `reserve()` onward.
  - `receipt_line` polls `sigtimedwait(SIGNALS, 0)` between bounded `select` slices and refuses on a signal.
  - The pre-launch phase records a refusal with the mask held.
  - No async handler can run at the `finally`'s mask call. CPython's `pthread_sigmask` runs pending Python handlers.
- **H-M1.** `release()` separates the commit (`os.replace`) from the post-commit checks. A post-commit failure records
  `committed=True` plus the error, and still retains `window-release.json`.
- **H-M2.** The child's order before the spawn:
  1. open the streams;
  2. take the final memory sample;
  3. run the full `verify_materialization` and check the identity map;
  4. call `verify_location` on every held handle;
  5. sweep `pending_handled`;
  6. spawn.
- **H-M3.** The same mask discipline covers `child`'s pre-spawn phase and `dispatch`'s.
- **H-M4.** Keep and compare the pins of every gate record, or narrow the FRAME claim to the compared set. Prefer
  keeping and comparing them:
  - challenge, receipt and stdin-response;
  - lead observation;
  - samples, vault and identity records.
- **H-M5.** Do a guarded summary print before closing handles; failure records go out while handles are still open.
- **H-M6.** The child authenticates `reservation.json` against the argv-authenticated `admission.json` pin, and takes
  the token from it.
- **H-M7.** Run the sealed child with `/usr/bin/python3 -I -B`, so the inherited PYTHONPATH cannot shadow the
  stdlib. Or state this explicitly under N08.
- **H-M8.** Dispatch exit and last-resort output, and late-conclusion signal recording, are covered by N14 and N13.

## (A) Runtime storage guard: the enforced bound behind Gate 0 v4

- **Sampling.** In the parent's wait loop, about every 30 s, take `os.statvfs` of the RUNS filesystem. The exact
  free-bytes definition must match `storage_status.py`.
- **Retained estimate.** retained = measured materialization + (free at launch − free now). This attributes all
  decline, ambient included, to the run, which is conservative.
- **Stop condition.** When free − reserve < retained + H:
  1. retain `storage-guard-stop.json` with every sample;
  2. send SIGTERM to the launcher/child wrapper, which forwards it to the target;
  3. wait for the actual exits;
  4. conclude: non-success, retained.

  H is a stated headroom allowance: ambient growth during the stop plus final records.
- **Unobservable storage.** If storage cannot be observed, stop the run. This fails closed.
- **What it changes in Gate 0.** At dispatch, the generated-output allowance A_obj is replaced by the guard's
  enforced threshold:
  - Required = A_mat + A_rec + H + restore(A_mat + A_rec).
  - The run is guaranteed never to take free space below reserve + retained + H, within the sampling interval.
    That interval needs its own justification: H must cover the maximum observed write rate × the interval × a factor.
- **Approval.** This changes the Gate 0 allowance model. It goes to the monitor/operator in the package (S-1
  option 4) and to actual gpt-6.1-sol review. It is not adopted silently.
