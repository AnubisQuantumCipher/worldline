# HISTORICAL AUTHOR-SIDE OBSERVATIONS ONLY — NON-COMPLIANT REVIEW-MODEL TASK

**Standing.** This is a Claude Agent task, actual model `claude-opus-5-5`, titled "Adversarial pre-review of scratch
frame v5". It was dispatched by the lead before v5 was frozen.

**WORLDLINE monitor ruling (2026-10-04).**
- The task is non-compliant with the preserved requirement of actual `gpt-6.1-sol` for EVERY review, pre-reviews
  included.
- Its notes are preserved here as historical author-side observations only, with **no CLOSED, qualification or
  acceptance reliance**.
- The independent review of the frozen v5 candidate is the actual gpt-6.1-sol review in
  `work/claude-scratch-frame-v5/review/gpt61-v1`.

**How the lead uses this.**
- v5 was frozen (frame-inventory sha256 `c45720ef…5aa45`) without waiting for this task or using it.
- Any later lead change that responds to a point below is ordinary author engineering. It will be disclosed as such,
  and it is subject to actual gpt-6.1-sol review.
- Nothing below is evidence of anything.

---

The text below is the task's final report, verbatim.

> I found one blocking defect (S1) and seven minor ones. My verdicts: V4-B01, V4-B03 and V4-B04 are closed; V4-B02 is not closed, because a handled signal can skip `run()`'s whole terminal path.
>
> **Standing.** This is a read-only pre-read. I executed nothing and wrote nothing, so there is no SIA note. The frame was frozen while I was reading. `scratch.py` is unchanged and matches the pin in `frame-inventory.json` (sha256 f9f6596d…be86). `FRAME.md` changed mid-read; I re-read the frozen version (417cb61b…). FRAME.md:23-28 and AGENTS.md both say a Claude pre-read is non-compliant: these are author-side observations only. The gpt-6.1-sol review already under way in `review/gpt61-v1` is the authority.
>
> All line numbers below are in `scratch.py` unless marked FRAME.
>
> **S1 — BLOCKING (outcome 5, V4-B02 signal path). Lines 1543-1544, 1587-1612, with the handler at 1469-1475.**
> - **Defect:** `run()` keeps the async `raising_handler` armed from `reserve()` (1588) through the memory gate, which can wait up to 300 s on stdin. It only blocks signals at the head of the `finally` (1612). CPython's `signal.pthread_sigmask` calls `PyErr_CheckSignals()` after changing the mask. So a handled signal that arrives after the except clause's last eval-breaker check runs the handler inside line 1612. The resulting `Interrupted` escapes the `finally`.
> - **What gets skipped:** `launcher-wait.json`, `conclude()`, `result.json`, `release-withheld.json` and `conclude-failure.json`.
> - **Concrete trigger:** Ctrl-C or a process-group kill while `run` waits for a receipt answer after the reservation committed. `run` shares dispatch's process group (`spawn` at 1517/1930 starts no new session). It gets SIGINT directly, then dispatch forwards SIGTERM milliseconds later (1948-1952).
> - **Result:** the window stays reserved under this attempt's token, with no attempt record of the unresolved ownership. Only a traceback lands in `run.stderr`.
> - **Variant:** if the second signal lands inside `traceback.format_exc()` at 1610, `ctx.error` is lost. `result.json` then shows `error=None, launched=False` with no stated cause.
> - **What still holds:** nothing was launched, so no live release happens. But FRAME:182 ("Signals are blocked throughout") and V4-B02's requirement to always attempt terminal/unresolved records both fail. If the reviewer files this under FRAME's "parent dies" residual, it is still a FRAME:182 claim failure.
> - **Fix:** block SIGNALS before `reserve()` and keep them blocked. Make `receipt_line` poll `signal.sigtimedwait(SIGNALS, 0)` between short `select` calls, and refuse on any signal. Alternatively, make the handler record-only once a flag is set as the first bytecode of each except/finally.
>
> **M1 — MINOR. Lines 1286-1292 and 1321-1341.** `window_write` runs `directory.sync()` and `verify_location()` after `os.replace` (the commit point), outside its try. If either fails, `release()` raises after the window was already released. Conclusion then writes `release-failure.json` saying the state is unknown, writes no `window-release.json`, and sets `released=False`. This contradicts FRAME:207 and the docstring. Fix: separate the commit from the post-commit checks; on a post-commit failure set `committed=True`, record the error, and still retain `window-release.json`.
>
> **M2 — MINOR (gate ordering). Lines 1823-1847 and 1867.**
> - (a) v5 added `again = verify_materialization(...)` (a full re-hash of base and source) and the location checks after the `child-final` memory sample. That sample is therefore no longer the final pre-spawn gate. FRAME:330 lists it as "preserved unchanged", and v4 had it later in the sequence.
> - (b) After the last held `verify_location()` (1844-1845), the child creates two streams (with directory fsyncs) and spawns without re-checking `source`. The parent does re-check at 1601. FRAME:152-156 says "immediately before the spawn".
> - Fix: open the streams first. Then take the final sample, run `again`, check the identity map, and call `verify_location()` on every held handle after `pending_handled()` (1863), right before 1867.
>
> **M3 — MINOR. Lines 1578-1587, 1848-1861 and 1918-1923.** Several async-signal windows sit outside any guarded block:
> - `run`, after `launch.json` is written but before the second try.
> - `child`, at the except entry before the `suppress`. Also between the end of the try and line 1861, whose own mask call can raise outside the try.
> - `dispatch`, at 1923, before its try.
>
> Nothing is reserved or started at these points. But `refusal.json` / `child-refusal.json` are lost, contrary to FRAME:211-213. The same fix as S1 applies.
>
> **M4 — MINOR (FRAME overclaim). FRAME:66 versus code line 1663.** FRAME says conclusion compares "every retained launch-gate record" with an in-memory pin. Only seven are compared. The pins for these records are thrown away, so a rewrite after the gate is never reported as drift:
> - `challenge.json` (1227), `memory-receipt.json` (1235) and `stdin-response.bin` (1212)
> - `lead-observation-run.json` (634)
> - the preflight, vault, identity and sample records (626)
>
> Fix: keep these pins in `ctx.pins` and compare them, rather than narrowing the claim.
>
> **M5 — MINOR. Lines 1760-1764 with 1633-1641.** Conclusion closes every handle before its final `print`. If that write fails (ENOSPC or EIO on the stdout file), `run` cannot retain `conclude-failure.json`: `write_json` on a closed handle raises TypeError, so only stderr gets it. This contradicts FRAME:209. Fix: do a guarded print before closing the handles.
>
> **M6 — MINOR. Lines 1792-1798 and 1810-1811.** The child takes `token` and `holder_task` from `reservation-intent.json` without authenticating them; only the `launch` field is bound. `admission.json`, which is argv-authenticated, carries the `reservation.json` pin (1591), but the child never verifies it. Under the cooperating window protocol this allows no bypass, but FRAME:64 ("Records the frame relies on are authenticated") is not met. Fix: verify `reservation.json` against `gate['reservation']` and take the token from it.
>
> **M7 — MINOR (precision of the N08 ceiling). Lines 1077-1079 and 1570-1571.**
> - The relocated PYTHONPATH (`RUNS/NAME/source/runtime` and `…/source/tests`) is inherited by the child's `/usr/bin/python3`, which runs without `-I` or `-E`.
> - The child's imports (lines 56-57, and later `shlex`/`shutil` inside `tool_inventory`) therefore search run-tree directories before the stdlib. That happens before the child's own admission re-verifies the tree.
> - The reviewed base has no colliding module names. A module planted between parent admission and child start would still run inside the child; only conclusion would see the extra file.
> - Fix: add `-I` to the sealed child template, or state this explicitly under N08.
>
> **M8 — MINOR.**
> - Dispatch's exit status ignores its own `failure` (1988).
> - Dispatch's last-resort stderr is the lead's console, not a retained stream (FRAME:174).
> - Signals that arrive during conclusion after 1617 are never consumed or recorded.
>
> **Checked with no defect found:**
> - `CHILD_RECORD_RE` matches every participant record and every `.retry-<12 hex>` name, and correctly excludes the `child-final-*` samples.
> - Every tuple unpacking matches what its callee returns.
> - `retain`, `guarded`, `read_record` and `wait_blocked` cannot raise once signals are masked.
> - A `reserve()` interrupted after its commit is still released through `owns_window()`.
> - Another holder's reservation is never overwritten (1299, 1327-1328), and release requires an observed terminal state.
> - The descriptor passed to `fchdir` is always the held, sealed source inode.
> - The child re-derives and enforces the argv allowlist, environment equality, 8G/0/core 0-0 caps and `-j2`.
> - Conclusion uses `ctx.seal`, `ctx.pins` and the in-memory record pin.
>
> **Verdicts:**
>
> | Finding | Verdict | Closing lines / reason |
> |---|---|---|
> | V4-B01 | CLOSED | 155-223, 308-345, 1279/1292, 1546-1547, 1566-1569, 1601-1602, 1799-1813, 1842-1845, 1867, 951-955, 1040, 1679-1691. M2b is a non-blocking residual. |
> | V4-B02 | NOT_CLOSED | The mechanisms are in place (360-436, 1396-1412, 1611-1641, 1644-1765, 1848-1896, 1955-1985), but S1 lets a handled signal abort `run()`'s `finally` after reservation and skip every terminal/unresolved record. M1 and M5 are claim gaps. |
> | V4-B03 | CLOSED | 1570-1578, 1582-1585, 1593, 1783-1798, 1663-1676, 1681-1691. M4 and M6 are claim gaps. |
> | V4-B04 | CLOSED | 138-141, 246-268, 531-548, 555, 561-566, 1702-1704. Changes after an observation remain under the declared metadata-timing and no-confinement limits. |
