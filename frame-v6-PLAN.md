# Scratch frame v6: change plan, v2 (lead working notes; not a review, grants nothing)

**What v2 corrects.** v1 is preserved as `frame-v6-PLAN.SUPERSEDED-v1.md`. v2 follows the WORLDLINE monitor
correction of 2026-10-04:
- **V5-B02.** An "own-inode relocation, detected and refused" residual does not satisfy the original requirement
  that frame mutations stay within the intended run tree. V5-B02 stays OPEN until that criterion is met. A
  reviewer can assess a design but cannot grant an operator-only weakening.
- **Storage guard.** Periodic storage sampling plus a factor on the maximum observed write rate establishes neither
  a maximum future write rate nor a stop latency. It cannot support a "guaranteed never" storage floor, and it
  cannot replace A_obj with an enforced bound.
  - Any monitoring guard is additive defensive engineering only.
  - The existing capacity gate (runbook Gate 0) stays in force until a reviewed, requirement-preserving admission
    argument exists.

**Status.** The actual gpt-6.1-sol review of frozen v5 is still sealing. This plan will be completed from its final
reports before any v6 code is frozen. v6 goes to its own actual gpt-6.1-sol review, which carries the exact
unresolved criteria below.

**Sources of changes, kept apart.**
- **(G)** Findings of the actual gpt-6.1-sol v5 review. These are authoritative.
- **(A)** The lead's own author-side engineering.
- **(H)** Points first seen in the non-compliant Claude pre-read. These are author-side observations only, and any
  change made for one is disclosed as lead engineering.

## Unresolved criteria carried unchanged into the v6 review (exact text)

1. **V5-B02, OPEN.** "Frame mutations stay within the intended run tree."
   - **Prohibited outcome**, from the v4 brief and still in force: the frame must never "write outside the run tree
     (other than the documented shared-window protocol)".
   - **The v5 finding:** a same-user rename or detachment between the location check and an fd-relative mutation
     "lets the frame itself create/write/chmod outside the named run tree before refusal; post-checking cannot undo
     that mutation".
2. **Storage admission, OPEN for any change of the Gate 0 model.**
   - "live preflight that budgets measured run growth AND temporary full-restore space above the unchanged
     reserve"
   - "include materialization, all retained outputs/records, temporary full-restore needs and ongoing agent/review
     growth above the unchanged reserve"
   - "Do not shrink the next allowance merely because the last run used less"
   - "If safe capacity cannot be established, keep dispatch deferred."

## (G) v5 review, items 1–6 (checkpoints; final reports pending)

- **V5-B01. `observe_tree` left already-observed files stale.**
  - *Drafted in the v6 working copy.* Every accepted file's complete `stat_key` is recorded. In the final pass every
    directory is re-reached and every accepted file in it is re-stat'ed by name without following, requiring the
    same complete key. The directory key is re-checked after that.
  - Untested until the v6 self-check runs.
- **V5-B02, OPEN.** No v6 design has been shown to meet the criterion. The lead's assessment of where it stands:
  - **What unprivileged code can do.** With mutations through held descriptors of frame-created, authenticated
    inodes, the frame never creates into, writes or chmods a foreign inode. Relocation is detected and refused.
  - **Why that falls short.** The criterion is location within the named tree. A concurrent same-user rename can
    move a frame-owned directory between any location check and the following mutation.
  - **Primitives examined:**
    - path-resolving `openat2(RESOLVE_NO_SYMLINKS)` creates at the name at the instant of the call. But `mkdirat`,
      the subsequent writes, `fchmod` and `linkat` are not covered by the same atomic resolution;
    - O_TMPFILE plus a link, where the link's parent resolution is not atomic;
    - sticky-bit ownership, but a same-uid renamer is the owner;
    - Landlock, which restricts which hierarchies are writable, not the location of one's own moved directory.

    None closes the window for a same-uid renamer.
  - **Candidate requirement-preserving designs.** These need operator action, because they change account or
    privilege arrangements:
    - (i) Run the frame and its run tree under a dedicated account whose run-tree ancestors no process of user
      `sicarii` can rename. This needs account setup and `sudo`, both operator gates.
    - (ii) An operator-provided filesystem or mount arrangement with the same property.

    Each still needs a full design and actual gpt-6.1-sol review. The lead has not shown that every unprivileged
    route is impossible. If one is found, it goes to review. None is claimed.
  - **Concrete blocker until then.** Frame qualification, and with it every scratch proof run, is blocked by V5-B02
    independently of storage. It is reported as such and added to the operator package.
- **N11–N14, V4-required-change-5.** As in plan v1:
  - N11: committed-primary marker or explicit archival interpretation;
  - N12: participant schema validation;
  - N13: recompute after late close errors;
  - N14: dispatch exit reflects its own failure and interrupts;
  - RC5: FRAME.md must not present custody or no-alias coverage as closed.
- **Rulings already given in the checkpoints:**
  - **Compact identity records: ACCEPTABLE**, as a content-reference representation with the frozen baselines
    retained and identity-checked.
  - **Residuals: ACCEPTABLE_AS_DOCUMENTED** for empty-directory, no-target-confinement, target-exec-by-path and
    metadata-granularity. These rulings do not cover V5-B02.

## (H)/(A) author-side items (disclosed)

- **H-S1, H-M3.** Block the handled signals at the start of every verb, and never install or run an asynchronous
  raising handler.
  - Signals are consumed only by synchronous `sigtimedwait` at defined interruption points:
    - between admission steps;
    - inside `receipt_line`, between bounded `select` slices;
    - before each spawn;
    - inside `wait_blocked`;
    - in dispatch's loop.
  - A pending signal at a point raises `Interrupted` as an ordinary exception into the existing guarded paths.
- **H-M1.** `window_write` separates the commit (`os.replace`) from the post-commit checks.
  - `reserve()` records post-commit errors and refuses the launch, still releasing through `owns_window` at
    conclusion.
  - `release()` returns `committed=True` with its post-commit errors, and still retains `window-release.json`.
- **H-M2.** The child's order before the spawn:
  1. open the streams;
  2. take the final memory sample;
  3. run the full `verify_materialization` and check the identity map;
  4. call `verify_location` on every held handle;
  5. reach an interruption point;
  6. spawn.
- **H-M4.** A journal on the parent's attempt handle, propagated to the handles it creates, records the pin of every
  record the parent writes. Conclusion compares every journaled record, not only seven.
- **H-M5.** Do the guarded summary print and any late-error record before handles close. After closing, a failure
  forces a non-success exit and goes to stderr.
- **H-M6.** The child authenticates `reservation.json` against the argv-authenticated `admission.json` pin, takes the
  token from it, and requires the intent's token/holder to match the launch holder.
- **H-M7.** Every verb runs as `/usr/bin/python3 -I -B`. The frame requires `sys.flags.isolated`. `started_by_dispatch`
  and the child template carry `-I`.

## (A) Additive storage monitor (defensive engineering only; NOT a bound)

- **What it does.** The parent samples free space during the wait. If free − reserve falls below a stated
  threshold, it retains `storage-monitor-stop.json` and stops the target through the existing SIGTERM forwarding.
  The attempt is then a retained non-success.
- **What it is not.** It establishes no maximum write rate, no stop latency, no storage floor and no admission
  argument.
  - **Gate 0 is unchanged.** Required = A_mat + A_obj + A_rec + A_ambient + R. A_obj is never replaced or reduced on
    account of the monitor.
  - The monitor only adds an earlier stop. It is reviewed as part of v6, and any claim about it is limited to "an
    additional stop condition".
