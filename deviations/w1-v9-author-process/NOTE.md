# W-1 v9 drafting author: process record (preserved; disclosed)

**Who and when.** The W-1 drafting agent (`a6d9c9e22b6b98dc0`). The lead resumed it ~18:00Z on 2026-10-05, and it handed
back ~19:00Z as a text reply. Its report is model output, recorded as stated.

## What the lead verified (engineering only, not review)

- **v9 file.** `proposal/ISOLATION-STORAGE-PROPOSAL-v9.md` is sha256 `4bc0272c…`, 562201 bytes and 5143 lines, matching
  the report.
- **Support file.** `v9-support/jackal.json` is `2d225e26…`.

## Disclosures

1. **WebFetch.** The author read upstream Linux v7.2 `kernel/exit.c`, `include/linux/io_uring.h` and `io_uring/cancel.c`
   from raw.githubusercontent.com. These are labelled upstream, not the installed build (premise P-KSRC).
2. **Its own transcript.** After a compaction it read its own subagent transcript (`agent-a6d9c9e22b6b98dc0.jsonl`), as
   permitted, to recover its JACKAL results.
3. **Saved output.** The harness auto-saved one large read-only output to the session tool-results directory. The author
   did not create that file.
4. **Not read.** It reports not reading `gpt61-v1` or `review-records/`. Nothing was interrupted.
5. **An open item it raised.** The §4.6 adoption joins require gpt-6.1-sol rollout provenance. The lead decided this as
   D-LEAD-REVIEW-PROVENANCE (STATUS).

## What this does not change

Every W-1 item stays OPEN until W-1 v9's own independent review rules.
