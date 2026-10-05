# D1 v4 drafter: Bash-created temporary file (process deviation, disclosed)

**What happened.** The D1 DESIGN v4 drafting agent was an author-role Claude subagent. Its prompt allowed Bash only for
read-only inspection. It ran one read-only Python command whose output was redirected into
`/tmp/claude-jk-table.txt`, 21015 bytes, sha256 `41d6a9a509b817169873e096586afadbc76b30081855d8ab30634ee0cacc193b`.
The content is derived only from its own `jackal.json`.

**What it was not.**
- It was not a workaround for a Write or Edit refusal. The agent reports no refusal.
- It touched no package, source or evidence file.

**Where it is recorded.**
- The agent disclosed it in its report, in `AUTHOR-NOTES.md` §3, and in `decisions.json` under `deviations`.

**What the lead did (2026-10-04 ~23:55Z).**
1. Copied the file here byte-for-byte and verified the sha256.
2. Removed the `/tmp` original. `/tmp` is a shared tmpfs, and the file was the subagent's scratch output.

No clearance or acceptance is implied for anything.
