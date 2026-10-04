# Durable copies of job-scratch evidence referenced by the ledger

The job scratch directory (/home/sicarii/.claude/jobs/c9272506/tmp) is deleted with the job. Ledger entries
whose evidence pointer lives there are preserved here byte-identically. The ledger pointers themselves are not
rewritten (history is append-only); this map resolves them.

| Ledger evidence path (68 items, adjudication facet) | sha256 | Durable copy |
|---|---|---|
| /home/sicarii/.claude/jobs/c9272506/tmp/adjudication-note.md | eead8fb8d93623c5b898641c8bd83c8c183a95360a183ded45f472d58b2be418 | evidence-preserved/adjudication-note.md |
