You are the independent, different-author reviewer for: the WORLDLINE Phase One consolidated OPERATOR DECISION PACKAGE, DRAFT v6,
and its supporting W-1 isolation proposal v3. The author is the Claude Code lead (claude-opus-5-5); W-1 v3 was written by an
author-role Claude drafting subagent for the lead. You are actual gpt-6.1-sol and authored nothing under review. Two separate
gpt-6.1-sol sessions reviewed DRAFT v4 and DRAFT v5 (both NOT_READY); the v5 re-review's seven required corrections and its W-1
gap list are your closure targets. The package goes to the human operator after your review; it asks for choices and grants none.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/package-review/gpt61-v3
- Do not import or execute WORLDLINE or frame code (read proof_manifest.py/scratch.py as text/AST only); do not run compilers,
  provers, builds, tests, sudo, useradd, setfacl, mount, loginctl, systemctl, project-vault, restic or any window/reservation
  action. Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under
  ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup (FUSE mounts can hang).
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in small groups); a large concurrent batch stalled a different reviewer's tool layer today.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims. Re-derive every number the package or the
  proposal derives that you rely on, and say whether it reproduces.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify every hash first):
  - Package: W/work/claude-operator-decision-package-v1/DRAFT-v6.md (sha256
    106dea2c460044b0d586b0107f4060c7284f9599197feed86164e4d53b8769fc, 56918 bytes; byte-identical frozen copy WT/package-frozen/DRAFT-v6.md).
  - W-1 v3: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v3.md (sha256 97f39c8967ec32538474827256271e65ab8ee0347165aa971b5887608e02ed8c,
    193544 bytes; frozen copy WT/package-frozen/ISOLATION-STORAGE-PROPOSAL-v3.md) and WT/proposal/v3-support/jackal.json
    (6b0853230bf777c9861a0b1f71cdfdd875d315eca7ddac725aeeca2243fcc86b).
  - Runbook Gate 0 v4.3 (O1 provenance corrected): WT/RUNBOOK-first-proof-iteration.md (sha256
    d7db4439c75e664bc20022b01bc49a68be4c7f1b8316f90a80aaf225258f7201); v4.1 and v4.2 preserved in WT/runbook-history/.
- Closure targets: WT/package-review/gpt61-v2/{REVIEW.md, review.json, checks.json} (verdict NOT_READY; required corrections
  W1-CUSTODY, W1-SETUP, W1-RESOURCES, W1-LIFETIME-ROLLBACK, OD2-CONSEQUENCES, PKG-V5-FACTS, PKG-CLOSURE-STATUS; the section-3 gap
  list; W-1 subgap statuses). Earlier: WT/package-review/gpt61-v1. Prior drafts DRAFT-v4/v5 and W-1 v1/v2 are preserved.
- Requirements (verbatim authority): W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json};
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- Monitor and supervision rules the package must carry (as quoted in it): storage allowances versus bounds; "frame mutations stay
  within the intended run tree" and the own-inode ruling; root-made filesystem and W-1 are candidates; Packet 13 notice removal
  is an untested hypothesis; every review actual gpt-6.1-sol; isolation guard (no alternate-tool bypass); pinned implementation
  files need no approval solely for pinning, while reference semantics, unapproved API/ABI, owner policy, contracts, scope,
  accepted cases, controls and gates stay reserved; no interruption of ongoing tools; a failed-durability UNKNOWN withholds
  success credit but is not by itself a new approval gate.
- Sealed actual gpt-6.1-sol reports it relies on (verify freezes): frame v5 W/work/claude-scratch-frame-v5/review/gpt61-v1; D1 v2
  W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1; D1 v3 WT/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1;
  C-API v2 W/work/claude-capi-boundary-design-v2/review/gpt61-v1; C-API v3 WT/designs/claude-capi-boundary-design-v3/review/gpt61-v1;
  D2 WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1; root-worker seam v1
  WT/designs/claude-root-worker-seam-design-v1/review/gpt61-v1; compositions W/work/claude-composition-v5-{alpha,beta}/review/gpt61-v1;
  package reviews WT/package-review/gpt61-v{1,2}.
- Author-side records the package cites (not reviews): WT/frame-v6-selfcheck/RESULTS.md and WT/frame-v6w1-proto/RESULTS.md
  (ENGINEERING_ONLY self-checks; the subordinate-UID caveat), WT/review-monitoring/ (the D1 v4 review: INCOMPLETE, suspected
  tool-layer stall, recovery proposal awaiting a human decision), WT/deviations/ (a drafting agent's Bash tmp file; a drafting
  agent's TaskStop on its own task and the lead's two historical TaskStops), WT/ISOLATION.md, WT/STATUS.md (live index, not a seal).
- Frame source for W-1 checks (read as text): W/work/claude-scratch-frame-v5/scratch.py, W/work/claude-scratch-frame-v6/scratch.py,
  WT/frame-v6-PLAN.md. D1 v3 design for OD-2: WT/designs/claude-native-bigint-d1-design-v3/DESIGN.md:1700-1790 and its review
  REVIEW.md:119-136.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Closure of the v5 re-review's seven required corrections: CLOSED or NOT_CLOSED with the remaining gap (quote the v6 / W-1 v3
   text). Include every section-3 gap (generation-order, lease-and-writer-authority, per-entry-modes-acls, channel-and-dumpability,
   prestate-and-installation, exposure-options, fresh-identities-and-vault, denial-probes, resources-and-images,
   commits-and-durable-channel, participants-and-recovery, rollback-and-evidence) and every W-1 subgap still NOT_CLOSED. A
   coherent, complete specification is the bar; deferred execution/installed evidence is expected to remain future work.
2. Facts and numbers in v6 and W-1 v3: accurate against sources; every relied-on derived number reproduces under JACKAL (including
   W-1 v3's staged Gate 0 figures); observations distinguished from allowances; no past observation presented as a bound.
3. W-1 v3 design: is it, as specified, capable of meeting V5-B01 and V5-B02 if implemented exactly with a successor frame and
   verified on the installed system? Assess specifically the new gate-group/no_new_privs/seccomp anti-setid measure, the no-ACL
   recipe-mode preservation with export copies, writer.lock as root-owned 0440 flock-only, the separate commit markers and the
   in-generation fallback journal, the launch gating against late launch, front-only window release, and the stated residuals and
   compatibility hypotheses. Name every remaining gap; do not treat design text as executed evidence.
4. Criteria, ineligibility and authority: carried verbatim and unweakened; exceptions labelled ineligible; no reserved change
   presented as lead-authorized; no approval gate added without an original basis.
5. Options and consequences: complete for a human decision now (S-1 now; F-1 optional now and setup later; others later), with
   exact consequences, evidence still required and authority; recommendations separated from facts; correction-status tables
   accurate (nothing called closed on the author's word).
6. Anything that would let the human's choice weaken a contract, domain, accepted case, fixture, threshold, control or proof floor,
   add an assumption, suppress checked code, or skip a review, without the package saying so plainly.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only). On resume continue from the first unfinished
item; never rewrite an existing file.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json:
  {"schema":"claude-operator-package-review-v1","package":"<absolute path>","package_sha256":"<sha256 you computed>",
  "w1_proposal_sha256":"<sha256 you computed>","runbook_sha256":"<sha256 you computed>",
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (W-1 v3 via drafting subagent)",
  "verdict":"READY_FOR_OPERATOR|READY_WITH_REQUIRED_CORRECTIONS|NOT_READY","prior_closure":{"W1-CUSTODY":"...",...},
  "w1_gap_closure":{"generation-order":"...",...},"w1_subgap_closure":{"W1-CUSTODY":"...",...},
  "required_corrections":[{"id","item","correction","evidence"}],"item_findings":{...},"w1_assessment":"...",
  "jackal_reproduction":[...],"open_obligations":[...],"approval_granted":false,"proof_acceptance":false,
  "phase_acceptance":false,"source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure of each prior correction and W-1 gap, any new required corrections, the W-1 v3 assessment in
two sentences, and the sha256 of each of your four output files.
