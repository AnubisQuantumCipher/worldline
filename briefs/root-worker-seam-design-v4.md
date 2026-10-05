You are the independent, different-author design reviewer for: WORLDLINE Phase One root-worker SEAM DESIGN v4.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing under
review. Separate gpt-6.1-sol sessions reviewed v1, v2 and v3. (The draft lane the design analyzes was authored by a different
gpt-6.1-sol session; you review the Claude design, not that lane's acceptance.)

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v4/review/gpt61-v1
- Do not import or execute any WORLDLINE/COSMOGONY/root-worker code (Python or C); read it as text or AST. Do not run compilers,
  provers, tests, services, systemctl, sudo, namespaces, project-vault or restic; do not touch /srv labs, stores, sockets or windows.
  Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under ~/.local/share/sia/.gbrain/;
  never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup (the iPad mounts are offline and can hang). Do not read
  WT/packets/capi-pk0/ (a packet in progress), WT/package-review/gpt61-v5/ (a review in progress) or any session transcript.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in groups of at most four).
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance; the only output is a design verdict: ENDORSED,
  ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-root-worker-seam-design-v4/ (verify all four hashes): SEAM-DESIGN.md
  (f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda), seams.json (92a814a4883d3e01680dbfeae82cb7889b038930bc4e21bcaefd39b622a2a86c),
  jackal.json (4d556a457caa268c80b5d7ef4edae949433034ffeb950a5b4d2f8a29fcafcfab), AUTHOR-NOTES.md
  (0bd92ccd556e39a358a5e93db5a57fe55ba206080d7b6dc1f033508d7f9c66e4). v4 binds 24 v3 slices by line range and sha256 with quoted line
  replacements R4-1..R4-64 (six of them replace v2 lines), and transitively the v2 and v1 slices; verify the slices you rely on.
- v3 and its sealed review (closure targets): WT/designs/claude-root-worker-seam-design-v3/{SEAM-DESIGN.md (a0f2f411...), seams.json}
  and review/gpt61-v1/{REVIEW.md (1e1c5ef8...), review.json (35b264e7...), checks.json (63bcb753...), review-freeze.json (c52bd9ee...)}
  - verdict ENDORSED_WITH_REQUIRED_CHANGES; required changes V3-REQ-A..V3-REQ-L; V2-REQ-A..L and RQ-1 PARTIALLY_CLOSED; D-2b
  CLOSED_AT_DESIGN_LEVEL; other rulings PARTIALLY_CLOSED; clause closures; NF-1..NF-11 verified statically. Earlier designs and
  sealed reviews: WT/designs/claude-root-worker-seam-design-v{1,2}.
- Draft lane (status INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY): W/work/protected-original-root-worker-repair-v1 (handoff-to-claude-v1-retry1/
  HANDOFF.md, source/, preimage/, dependency-source/); other lanes the design cites: W/work/resource-child-authority-source-v1,
  W/work/protected-canonical-full-bridge-repair-v2, W/work/claude-root-worker-notes-v1.
- C-API lane: v4 binds the sealed C-API v5 review (ENDORSED_WITH_REQUIRED_CHANGES) and the sealed C-API v6 review (ENDORSED; its
  required changes closed at design level only; implementation and ROOT_WORKER_INTEGRATION OPEN), in
  WT/designs/claude-capi-boundary-design-v{5,6}/review/gpt61-v1. Qualified source composition: W/work/claude-composition-v5-beta/source.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json, ALL-ORIGINAL-OBLIGATIONS.md,
  REQUIRED-LIFETIME-CONTROLS.json, ORIGINAL-ORDINARY-ROSTER.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule on approval gates: reserved operator decisions are those the rulings name (D-2a provisioning/installation, D-2b
  frontier re-enrollment adjudication, D-4a resource policy, D-5a/D-5b delegation and privileged lab/install, D-7a original API/owner
  policy, D-8b kernel measurement, D-9a fault campaign) plus merge/release/install/sudo/production/PRIME; a brief or finding is not
  new authority to add approval gates; do not lower any reserved one.
- The author reports new static findings NF4-1..NF4-13, new items K-22/K-23 (under OP-7) and RC-5/RC-6 (lead-owned), and asks you to
  weigh these choices (AUTHOR-NOTES §4): the M8(c) stop on an authorized job.cancel when no owner is reachable (it changes C2-93's
  UNKNOWN row); restoring the serial route's workload refusal on the root route (DF-3); the new RELAY path; accounting option G; the
  escrow's retained read copy of output pipes; the sub-helper calling the native library. Process record:
  WT/deviations/seam-v4-author-process/NOTE.md (the author scanned the lead's transcript against instruction and reports using
  nothing from it).

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each of V3-REQ-A..V3-REQ-L and RQ-1, and for every RC clause and ruling still PARTIALLY_CLOSED or NOT_CLOSED (including clauses
   01.2, 01.3, 04.1, 07.3 and 09.1): CLOSED_AT_DESIGN_LEVEL, PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; owners and
   evidence requirements preserved?
2. Carried items: do the slices verify; are R4-1..R4-64 exact quotes, correct, justified and the only changes; is everything the v3
   review closed or assessed (D-2b, closed clauses, NF-1..NF-11, N-1..N-10, DF-1..DF-6, OP-1..OP-9 with OP-7's range repair) carried
   exactly?
3. Verify NF4-1..NF4-13 statically against the lane source and cited files; state each one's consequence for the design.
4. Does anything create a new refusal of an original accepted case, a new cap, a narrowed domain, a retired or weakened control
   (including the v1 frontier control), a changed original behaviour (assess M8(c) and the restored workload refusal explicitly), a
   lead-only acceptance or an added assumption? Assess RQ-1's window mapping W0-W5 and the RELAY/queue path.
5. The C-API integration (V4-K, U-1..U-8, MX-RW/MQ-RW/PX-RW, IC-13/IC-14): sound and complete against the sealed C-API v5 and v6
   reviews, with no root-worker wfx row or exclusive-map key, without deciding either lane's acceptance?
6. Operator items: exactly the reserved decisions, nothing added, nothing lowered (check K-22/K-23 under OP-7 and RC-5/RC-6)?
7. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of SEAM-DESIGN.md>",
  "design_sha256":"<sha256 you computed>","seams_sha256":"<sha256 of seams.json>","different_from_author":true,
  "actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V3-REQ-A":"...",...,"V3-REQ-L":"...","RQ-1":"..."},
  "clause_closure":{...},"ruling_closure":{"D-1a":"...",...},"findings_assessment":{"NF4-1":"...",...},
  "required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],
  "open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per required change, RQ-1, clause and ruling, the NF4-1..NF4-13 assessment, required changes,
rulings, and the sha256 of each of your four output files.
