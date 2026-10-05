You are the independent, different-author reviewer for: the WORLDLINE Phase One consolidated OPERATOR DECISION PACKAGE, DRAFT v7,
and its supporting W-1 isolation proposal v4. The author is the Claude Code lead (claude-opus-5-5); W-1 v4 was written by an
author-role Claude drafting subagent for the lead. You are actual gpt-6.1-sol and authored nothing under review. Three separate
gpt-6.1-sol sessions reviewed DRAFT v4, v5 and v6 (all NOT_READY); the v6 review's eight required corrections, the prior corrections
it left NOT_CLOSED, and its W-1 gap and sub-gap rulings are your closure targets. The package goes to the human operator after your
review; it asks for choices and grants none.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/package-review/gpt61-v4
- Do not import or execute WORLDLINE or frame code (read proof_manifest.py/scratch.py as text/AST only); do not run compilers,
  provers, builds, tests, sudo, useradd, setfacl, mount, loginctl, systemctl (read-only `systemctl show`/`cat` included: do not run
  them), project-vault, restic or any window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd.
  Never read or list anything under ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup
  (FUSE mounts; the iPad is offline and a stat can hang). Do not touch the vault repository or its state; Codex owns its recovery.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls
  modestly (sequentially or in groups of at most four); a large concurrent batch stalled a different reviewer's tool layer on
  2026-10-05. Do not read any review directory that is still in progress (the C-API v5 review under
  WT/designs/claude-capi-boundary-design-v5/review/, and the stalled D1 v4 review).
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims. Re-derive every number the package or the
  proposal derives that you rely on, and say whether it reproduces.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify every hash first):
  - Package: WT/package-drafts/DRAFT-v7.md (sha256 96dc07e822d117f6a4d351e652bb310873a02e84474b0e9e1f56a8462513b781, 73209 bytes;
    byte-identical frozen copy WT/package-frozen/DRAFT-v7.md). Its header explains why the working draft moved into the worktree:
    the edit guard refused edits to W/work/claude-operator-decision-package-v1/DRAFT-v7.md, an earlier working copy (044ede9f...)
    that is preserved there unchanged and is NOT under review.
  - W-1 v4: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v4.md (sha256 a1924e74555ca85169e33d25d9fd9adc0c89f2a19fbc846edd7c49ed11b49c1c,
    321052 bytes; frozen copy WT/package-frozen/ISOLATION-STORAGE-PROPOSAL-v4.md) and WT/proposal/v4-support/jackal.json
    (298caa0371fe7f2b3af90f71f24e27e25051cc09c698bbec6bf469ed77f547a5). Its predecessor v3 (97f39c89...) and v3-support/jackal.json
    (6b085323...) are preserved; v4 states which v3 sections it carries byte-for-byte and maps every ruling in its §18.
  - Runbook Gate 0 v4.3: WT/RUNBOOK-first-proof-iteration.md (sha256 d7db4439c75e664bc20022b01bc49a68be4c7f1b8316f90a80aaf225258f7201).
- Closure targets: WT/package-review/gpt61-v3/{REVIEW.md, review.json, checks.json, REVIEW-LIMITS-ERRATUM.md} (verdict NOT_READY):
  required corrections W1-GENERATION-PROTOCOL, W1-COMMIT-JOURNAL-EXPORT, W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE,
  W1-SETUP-PROBES-ROLLBACK, W1-IMAGE-TREE, PKG-V6-OPERATOR-TEXT, PKG-SUPERVISION-RECORD; prior corrections it left NOT_CLOSED
  (W1-CUSTODY, W1-SETUP, W1-LIFETIME-ROLLBACK); its section-3 gap rulings and W-1 sub-gap rulings. Earlier package reviews:
  WT/package-review/gpt61-v1, gpt61-v2. Prior drafts DRAFT-v4/v5/v6 and W-1 v1/v2/v3 are preserved.
- Requirements (verbatim authority): W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json};
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- Monitor and supervision rules the package must carry (as quoted in it): storage allowances versus bounds; "frame mutations stay
  within the intended run tree" and the own-inode ruling; root-made filesystem and W-1 are candidates; Packet 13 notice removal
  is an untested hypothesis; every review actual gpt-6.1-sol; isolation guard (no alternate-tool bypass after a guard refusal);
  pinned implementation files need no approval solely for pinning, while reference semantics, unapproved API/ABI, owner policy,
  contracts, scope, accepted cases, controls and gates stay reserved; no interruption of ongoing tools; a failed-durability
  UNKNOWN withholds success credit but is not by itself a new approval gate; the D1 v4 review stays untouched and INCOMPLETE until
  the human chooses a recovery; vault recovery is Codex's, with no lead vault operation or offload until Codex reports verified
  recovery; missing packs and failed checks are verified, disconnect causation is a hypothesis, saved snapshots establish no
  healthy backup.
- Sealed actual gpt-6.1-sol reports it relies on (verify freezes): frame v5 W/work/claude-scratch-frame-v5/review/gpt61-v1; D1 v2
  W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1; D1 v3 WT/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1;
  C-API v2 W/work/claude-capi-boundary-design-v2/review/gpt61-v1; C-API v3 and v4 WT/designs/claude-capi-boundary-design-v{3,4}/review/gpt61-v1;
  D2 WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1; root-worker seam v1 and v2
  WT/designs/claude-root-worker-seam-design-v{1,2}/review/gpt61-v1; compositions W/work/claude-composition-v5-{alpha,beta}/review/gpt61-v1;
  package reviews WT/package-review/gpt61-v{1,2,3}.
- Author-side records the package cites (not reviews): WT/frame-v6-selfcheck/RESULTS.md and WT/frame-v6w1-proto/RESULTS.md
  (ENGINEERING_ONLY self-checks; the subordinate-UID caveat), WT/review-monitoring/ (the D1 v4 review: INCOMPLETE, suspected
  tool-layer stall, recovery proposal awaiting a human decision), WT/deviations/ (drafting agents' process events, including the
  C-API v5 author's record and every TaskStop), WT/backup-repair-packet/ (the lead's read-only vault observations before the
  handover to Codex), WT/ISOLATION.md, WT/STATUS.md (live index, not a seal).
- Frame source for W-1 checks (read as text): W/work/claude-scratch-frame-v5/scratch.py, W/work/claude-scratch-frame-v6/scratch.py,
  WT/frame-v6-PLAN.md.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Closure of the v6 review's eight required corrections and of the three prior corrections it left NOT_CLOSED: CLOSED or
   NOT_CLOSED with the remaining gap (quote the v7 / W-1 v4 text). Include every section-3 gap and every W-1 sub-gap the v6 review
   left NOT_CLOSED. A coherent, complete specification is the bar; deferred execution/installed evidence is expected to remain
   future work.
2. Facts and numbers in v7 and W-1 v4: accurate against sources; every relied-on derived number reproduces under JACKAL (including
   W-1 v4's new values, the carried staged Gate 0, and v7's storage readings and margins); observations distinguished from
   allowances; no past observation presented as a bound; the corrected lingering-account fact.
3. W-1 v4 design: is it, as specified, capable of meeting V5-B01 and V5-B02 if implemented exactly with a successor frame and
   verified on the installed system? Assess specifically: the target account's user manager (every process-starting unit masked
   including the user bus, the empty-PAMName drop-in, no (sd-pam), quiescence and reference-freedom, the absorbing argument); the
   kernel lease test for writable open descriptions including queued ones; the per-verb channel state machines and create-only
   ordering; the fallback allocation descriptor, slot rules and consumers; export ACL readback and journal-prefix cuts; release
   without a committed release intent; absent.py, fail-stop scripts and the S-R reconciliation; the headed getfacl restore dump;
   the single layout with the records image inside the protected tree; and the stated unverified premises and compatibility
   hypotheses. Name every remaining gap; do not treat design text as executed evidence.
4. Criteria, ineligibility and authority: carried verbatim and unweakened; no reserved change presented as lead-authorized; no
   approval gate added without an original basis. Check in particular that the operator-run S-R reconciliation and the
   user-manager drop-in are presented as part of the existing reserved privileged setup and rollback, not as new gates.
5. Options and consequences: complete for a human decision now (S-1 now; F-1 optional now and setup later; others later), with
   exact consequences, evidence still required and authority; recommendations separated from facts; correction-status tables
   accurate (nothing called closed on the author's word); the supervision and isolation records accurate and complete.
6. Anything that would let the human's choice weaken a contract, domain, accepted case, fixture, threshold, control or proof floor,
   add an assumption, suppress checked code, or skip a review, without the package saying so plainly.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only). On resume continue from the first unfinished
item; never rewrite an existing file.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json:
  {"schema":"claude-operator-package-review-v1","package":"<absolute path>","package_sha256":"<sha256 you computed>",
  "w1_proposal_sha256":"<sha256 you computed>","runbook_sha256":"<sha256 you computed>",
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5 (W-1 v4 via drafting subagent)",
  "verdict":"READY_FOR_OPERATOR|READY_WITH_REQUIRED_CORRECTIONS|NOT_READY","prior_closure":{"W1-GENERATION-PROTOCOL":"...",...,
  "W1-CUSTODY":"...","W1-SETUP":"...","W1-LIFETIME-ROLLBACK":"..."},"w1_gap_closure":{"generation-order":"...",...},
  "w1_subgap_closure":{"W1-CUSTODY":"...",...},"required_corrections":[{"id","item","correction","evidence"}],"item_findings":{...},
  "w1_assessment":"...","jackal_reproduction":[...],"open_obligations":[...],"approval_granted":false,"proof_acceptance":false,
  "phase_acceptance":false,"source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure of each prior correction, gap and sub-gap, any new required corrections, the W-1 v4 assessment in
two sentences, and the sha256 of each of your four output files.
