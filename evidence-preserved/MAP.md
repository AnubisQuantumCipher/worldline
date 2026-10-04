# Durable copies of job-scratch evidence referenced by the ledger

The job scratch directory (/home/sicarii/.claude/jobs/c9272506/tmp) is deleted with the job. Ledger entries
whose evidence pointer lives there are preserved here byte-identically. The ledger pointers themselves are not
rewritten (history is append-only); this map resolves them.

| Ledger evidence path (68 items, adjudication facet) | sha256 | Durable copy |
|---|---|---|
| /home/sicarii/.claude/jobs/c9272506/tmp/adjudication-note.md | eead8fb8d93623c5b898641c8bd83c8c183a95360a183ded45f472d58b2be418 | evidence-preserved/adjudication-note.md |

## Review runner records and briefs (job scratch -> durable copy)

- Copied 2026-10-04 ~19:08Z: all of /home/sicarii/.claude/jobs/c9272506/tmp/p1/review-* and briefs/ (132 files,
  66709535 bytes on disk, byte-identical) to work/claude-lead-isolation-v1/review-records/ (outside git), with
  MANIFEST.json (sha256 19a5442532d0948f513e72df43184c0668945e39030a8da2ca82e2fadf695188).
- The originals stay where they are (adoption/readback pins reference those paths).
- review-scratch-v5 and review-d1-design-v2 were still running at copy time; their final records will be copied as
  a separate dated snapshot, never by overwriting this one.
