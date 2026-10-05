You are the independent, different-author design reviewer for: WORLDLINE Phase One root-worker SEAM DESIGN v3.
The author is the Claude Code lead (claude-opus-5-5) through a drafting subagent. You are actual gpt-6.1-sol and authored nothing under
review. Separate gpt-6.1-sol sessions reviewed v1 and v2. (The draft lane the design analyzes was authored by a different gpt-6.1-sol
session; you review the Claude design, not that lane's acceptance.)

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v3/review/gpt61-v1
- Do not import or execute any WORLDLINE/COSMOGONY/root-worker code (Python or C); read it as text or AST. Do not run compilers,
  provers, tests, services, systemctl, sudo, namespaces, project-vault or restic; do not touch /srv labs, stores, sockets or windows.
  Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under ~/.local/share/sia/.gbrain/;
  never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup (the iPad mounts are offline and can hang). Do not read
  WT/designs/claude-capi-boundary-design-v6/ (a draft in progress) or any review directory that is still in progress.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in groups of at most four); a large concurrent batch stalled a different reviewer's tool layer on
  2026-10-05.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance; the only output is a design verdict: ENDORSED,
  ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Design under review, in WT/designs/claude-root-worker-seam-design-v3/ (verify all four hashes): SEAM-DESIGN.md
  (a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0), seams.json (093f31176dd9560a236b8ad00f5fd28a683c810c8f400d646631318ca1b582e8),
  jackal.json (8cce45e34f12d9d7976cb9b04ab6ac47e3a99ae8cacc22708a84abe06ec0c024), AUTHOR-NOTES.md
  (dd382e1b0f74e825735e168ab6856b1c85e93f9a39312f3bc15019faf390a0ea). v3 binds 43 v2 slices by line range and sha256 (§B.1) with quoted
  line replacements R3-1..R3-43 (§B.2), and transitively the v1 slices v2 bound (C2-APC); verify the slices you rely on.
- v2 and its sealed review (closure targets): WT/designs/claude-root-worker-seam-design-v2/{SEAM-DESIGN.md (db512ddb...), seams.json}
  and review/gpt61-v1/{REVIEW.md (1a41b5c5...), review.json (84c176df...), checks.json} - verdict ENDORSED_WITH_REQUIRED_CHANGES;
  required changes V2-REQ-A..V2-REQ-L; RQ-1 PARTIALLY_CLOSED with its own required change; rc_clause_closure; ruling_closure with the
  owners and evidence requirements in its rulings; RC-05, RC-10 and D-2b CLOSED_AT_DESIGN_LEVEL; findings and defects assessments
  (N-1..N-10, DF-1..DF-6); operator items OP-1..OP-9 WITHIN_RESERVED_SCOPE. v1 and its review: WT/designs/claude-root-worker-seam-design-v1.
- Draft lane (status INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY): W/work/protected-original-root-worker-repair-v1 (handoff-to-claude-v1-retry1/
  HANDOFF.md, source/, preimage/, dependency-source/); other lanes the design cites: W/work/resource-child-authority-source-v1,
  W/work/protected-canonical-full-bridge-repair-v2, W/work/claude-root-worker-notes-v1.
- C-API lane. v3 binds the sealed C-API v4 review (WT/designs/claude-capi-boundary-design-v4/review/gpt61-v1) as predecessor status and
  labels every use of C-API v5 "[depends on unreviewed CAPI5]". AFTER v3 was drafted, C-API v5's own review sealed
  (WT/designs/claude-capi-boundary-design-v5/review/gpt61-v1: ENDORSED_WITH_REQUIRED_CHANGES; V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4
  still NOT_CLOSED; new V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE). Judge v3's C-API dependencies against both sealed reviews. A
  C-API v6 is being drafted; do not read it. Qualified source composition: W/work/claude-composition-v5-beta/source.
- Requirements: W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md, START-CLAUDE.txt, OBLIGATIONS-v2.json, ALL-ORIGINAL-OBLIGATIONS.md,
  REQUIRED-LIFETIME-CONTROLS.json, ORIGINAL-ORDINARY-ROSTER.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule on approval gates: reserved operator decisions are those the v1/v2 rulings name (D-2a provisioning/installation,
  D-2b frontier re-enrollment adjudication, D-4a resource policy, D-5a/D-5b delegation and privileged lab/install, D-7a original
  API/owner policy, D-8b kernel measurement, D-9a fault campaign) plus merge/release/install/sudo/production/PRIME; a brief or finding is
  not new authority to add approval gates; do not lower any reserved one.
- The author reports new static findings NF-1..NF-11 (SEAM-DESIGN and AUTHOR-NOTES), its own first-draft errors and fixes (AUTHOR-NOTES
  §4), process records (AUTHOR-NOTES), and uncertainties it asks you to examine first: the RQ-1 trade-off (a scope rollover now passes
  the pre-effect, the native launch refuses it and the operation is then quarantined); whether residuals R1-R3 cover everything outside
  D_emb; the custody genesis as root of trust with native key handling OPEN; the C-API dependencies; measurements K-15..K-21 and
  installed-runtime checks RC-1..RC-4 not done.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. For each of V2-REQ-A..V2-REQ-L and RQ-1, and for every RC clause and ruling the v2 review left PARTIALLY_CLOSED or NOT_CLOSED:
   CLOSED_AT_DESIGN_LEVEL, PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; owners and evidence requirements preserved?
2. Carried items: do the slices verify; are R3-1..R3-43 exact quotes of their sources, correct, justified and the only changes; is
   everything the v2 review closed or assessed (RC-05, RC-10, D-2b, closed clauses, N-1..N-10, DF-1..DF-6, OP-1..OP-9) carried exactly?
3. Verify NF-1..NF-11 statically against the lane source and the cited files; state the consequence of each for the design.
4. Does anything create a new refusal of an original accepted case, a new cap, a narrowed domain, a retired or weakened control
   (including the v1 frontier control), a lead-only acceptance, or an added assumption? Assess RQ-1's command x caller x time mapping
   and the rollover-quarantine trade-off explicitly, and V2-REQ-I's queued-not-refused rule for requests that cannot be joined.
5. The C-API integration (V-K): are the stage tables, per-call qualifiers including indirect and transport paths, branch-correct gates
   without an assignment exception, unchanged glue, the gate chain G-CAPI -> G-CAPI-P -> G-PROT -> G-RW and IC-1..IC-12 sound and
   complete against both sealed C-API reviews, without deciding either lane's acceptance?
6. Operator items: exactly the reserved decisions, nothing added, nothing lowered?
7. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, or add an assumption.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of SEAM-DESIGN.md>",
  "design_sha256":"<sha256 you computed>","seams_sha256":"<sha256 of seams.json>","different_from_author":true,
  "actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (drafting subagent)",
  "verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED","rc_closure":{"V2-REQ-A":"...",...,"V2-REQ-L":"...","RQ-1":"..."},
  "clause_closure":{...},"ruling_closure":{"D-1a":"...",...},"findings_assessment":{"NF-1":"...",...},
  "required_changes":[{"id","change","reason","evidence"}],"rulings":[{"id","ruling","owner","evidence_required"}],
  "open_obligations":[...],"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per required change, RQ-1, clause and ruling, the NF-1..NF-11 assessment, required changes,
rulings, and the sha256 of each of your four output files.
