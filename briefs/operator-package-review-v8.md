You are the independent, different-author reviewer for: the WORLDLINE Phase One consolidated OPERATOR DECISION PACKAGE, DRAFT v8,
and its supporting W-1 isolation proposal v5. The author is the Claude Code lead (claude-opus-5-5); W-1 v5 was written by an
author-role Claude drafting subagent for the lead. You are actual gpt-6.1-sol and authored nothing under review. Four separate
gpt-6.1-sol sessions reviewed DRAFT v4 to v7 (all NOT_READY); the v7 review's seven required corrections, the corrections it left
NOT_CLOSED, and its W-1 gap and sub-gap rulings are your closure targets. The package goes to the human operator after your review;
it asks for choices and grants none.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/package-review/gpt61-v5
- Do not import or execute WORLDLINE or frame code (read proof_manifest.py/scratch.py as text/AST only); do not run compilers,
  provers, builds, tests, sudo, useradd, setfacl, mount, loginctl, systemctl (including read-only `systemctl show`/`cat`), tune2fs,
  project-vault, restic or any window/reservation action. Do not write SIA notes. Do not modify anything outside your cwd. Never read
  or list anything under ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup (FUSE mounts; the
  iPad is offline and a stat can hang). Do not touch the vault repository or its state; Codex owns its recovery.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. Batch JACKAL calls modestly
  (sequentially or in groups of at most four). Do not read any directory still being written: WT/designs/claude-root-worker-seam-design-v4/,
  WT/packets/capi-pk0/, and the stalled D1 v4 review.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims. Re-derive every number the package or the
  proposal derives that you rely on, and say whether it reproduces.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify every hash first):
  - Package: WT/package-drafts/DRAFT-v8.md (sha256 ce4bb35e7fff0b25b6a086801463e8427623c7f7cd1a74340b67a6dd09cd9843, 87867 bytes;
    byte-identical frozen copy WT/package-frozen/DRAFT-v8.md).
  - W-1 v5: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v5.md (sha256 303205b1531eb5752fabc866f949c609725e3e42936404495ba9adfd171cd7ee,
    237502 bytes; frozen copy WT/package-frozen/ISOLATION-STORAGE-PROPOSAL-v5.md) with WT/proposal/v5-support/jackal.json
    (df5d2a77d6a0ba908f8079b34b33bfa0a7cb13fe43afee01821723c7a32be929). v5 is a DELTA over W-1 v4 (WT/proposal/ISOLATION-STORAGE-PROPOSAL-v4.md,
    a1924e74...): its §0.1 composition rule, its §0.4 amendments and its §18.5 change map define the complete v5 text. The lead's script
    composed it to 466105 bytes, sha256 6cbc9c07994c2798910b84a02c5e445f67f24b9f51ed0efc95142df9b6113490 (equal to the author's), kept as
    the DERIVED convenience copy WT/package-frozen/ISOLATION-STORAGE-PROPOSAL-v5-COMPOSED.md. Verify that copy by recomposing it or at
    least by hash before relying on it; the authored artifact is the delta.
  - Runbook Gate 0 v4.3: WT/RUNBOOK-first-proof-iteration.md (sha256 d7db4439c75e664bc20022b01bc49a68be4c7f1b8316f90a80aaf225258f7201).
- Closure targets: WT/package-review/gpt61-v4/{REVIEW.md (75f297ce...), review.json (70b341d6...), checks.json, review-freeze.json}
  (verdict NOT_READY): required corrections W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION,
  W1-SETUP-IDENTITY, W1-SETUP-RECONCILIATION, W1-IMAGE-OBSERVATION, PKG-V7-AUTHOR-RECORDS; corrections it left NOT_CLOSED
  (W1-GENERATION-PROTOCOL, W1-COMMIT-JOURNAL-EXPORT, W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE, W1-SETUP-PROBES-ROLLBACK,
  W1-IMAGE-TREE, PKG-SUPERVISION-RECORD, W1-CUSTODY, W1-SETUP, W1-LIFETIME-ROLLBACK); its section-3 gap and W-1 sub-gap rulings.
  Earlier package reviews: WT/package-review/gpt61-v{1,2,3}.
- Requirements (verbatim authority): W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json};
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- Monitor and supervision rules the package must carry (as quoted in it): storage allowances versus bounds; "frame mutations stay
  within the intended run tree" and the own-inode ruling; root-made filesystem and W-1 are candidates; every review actual
  gpt-6.1-sol; isolation guard (no alternate-tool bypass after a guard refusal); pinned implementation files need no approval solely
  for pinning, while reference semantics, unapproved API/ABI, owner policy, contracts, scope, accepted cases, controls and gates stay
  reserved; no interruption of ongoing tools; a failed-durability UNKNOWN withholds success credit but is not by itself a new
  approval gate; the D1 v4 review stays untouched and INCOMPLETE until the human chooses a recovery; vault recovery is Codex's, with
  no lead vault operation or offload until Codex reports verified recovery; missing packs and failed checks are verified,
  disconnect causation is a hypothesis, saved snapshots establish no healthy backup; Codex's ext4 privileged-reserve proposal
  (W/work/local-storage-relief-20261005/RESERVE-PROPOSAL.md) is NOT EXECUTED and is the human's sudo decision.
- Sealed actual gpt-6.1-sol reports it relies on (verify freezes): frame v5 W/work/claude-scratch-frame-v5/review/gpt61-v1; D1 v2
  W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1; D1 v3 WT/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1;
  C-API v2 W/work/claude-capi-boundary-design-v2/review/gpt61-v1; C-API v3-v6 WT/designs/claude-capi-boundary-design-v{3,4,5,6}/review/gpt61-v1;
  D2 WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1; root-worker seam v1-v3
  WT/designs/claude-root-worker-seam-design-v{1,2,3}/review/gpt61-v1; compositions W/work/claude-composition-v5-{alpha,beta}/review/gpt61-v1;
  package reviews WT/package-review/gpt61-v{1,2,3,4}.
- Author-side records the package cites (not reviews): WT/frame-v6-selfcheck/RESULTS.md and WT/frame-v6w1-proto/RESULTS.md
  (ENGINEERING_ONLY self-checks; the subordinate-UID caveat), WT/review-monitoring/, WT/deviations/ (drafting agents' process
  events, the lead's interruptions, the W-1 v5 author's 2>/dev/null), WT/backup-repair-packet/ (README and five observation files),
  WT/ISOLATION.md, WT/STATUS.md (live index, not a seal).
- Frame source for W-1 checks (read as text): W/work/claude-scratch-frame-v5/scratch.py, W/work/claude-scratch-frame-v6/scratch.py,
  WT/frame-v6-PLAN.md.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Closure of the v7 review's seven required corrections and of the ten corrections it left NOT_CLOSED: CLOSED or NOT_CLOSED with the
   remaining gap (quote the v8 / composed W-1 v5 text). Include every section-3 gap and every W-1 sub-gap the v7 review left
   NOT_CLOSED. A coherent, complete specification is the bar; deferred execution/installed evidence is expected to remain future work.
2. Facts and numbers in v8 and W-1 v5: accurate against sources; every relied-on derived number reproduces under JACKAL (including
   W-1 v5's values, the carried staged Gate 0 and v8's storage readings and margins); observations distinguished from allowances; no
   past observation presented as a bound or trend.
3. W-1 v5 design: as composed, is it capable of meeting V5-B01 and V5-B02 if implemented exactly with a successor frame and verified on
   the installed system? Assess specifically: the observer's write-bit revocation as a new frame mutation inside the protected tree;
   W-CLOSED, including the author's claim that conditions (c2), (c4) and (c5) are the frame walk's EXISTING rules (verify against
   scratch.py) so that only (c1), (c3) and the revocation are new, and whether any of them can refuse or change an originally accepted
   run, output, mode or case; the quiescence property and its trusted-systemd premises; the credential closure (drop-in lines, io_uring
   denial); protocol failure states; journal continuation; the external setup-identity seal; atom-based S-R and check_out.py; the
   images-directory change; and every stated premise with its probe and "redesign, no exception". Name every remaining gap; do not
   treat design text as executed evidence.
4. Criteria, ineligibility and authority: carried verbatim and unweakened; no reserved change presented as lead-authorized; no
   approval gate added without an original basis (check that v5's new setup items stay inside the existing reserved privileged setup
   and rollback, and that S-1 option 7 is presented as the human's pending sudo decision, not as the ineligible "lower the reserve").
5. Options and consequences: complete for a human decision now (S-1 now; F-1 optional now and setup later; others later), with exact
   consequences, evidence still required and authority; recommendations separated from facts; correction-status tables accurate
   (nothing called closed on the author's word); the supervision and isolation records accurate and complete (including the corrected
   interruption record).
6. Anything that would let the human's choice weaken a contract, domain, accepted case, fixture, threshold, control or proof floor, add
   an assumption, suppress checked code, or skip a review, without the package saying so plainly.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only). On resume continue from the first unfinished item;
never rewrite an existing file.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json:
  {"schema":"claude-operator-package-review-v1","package":"<absolute path>","package_sha256":"<sha256 you computed>",
  "w1_proposal_sha256":"<sha256 of the v5 delta you computed>","w1_composed_sha256":"<sha256 of the composed text you verified>",
  "runbook_sha256":"<sha256 you computed>","different_from_author":true,"actual_model_selection":"gpt-6.1-sol",
  "author":"Claude Code lead claude-opus-5-5 (W-1 v5 via drafting subagent)",
  "verdict":"READY_FOR_OPERATOR|READY_WITH_REQUIRED_CORRECTIONS|NOT_READY","prior_closure":{"W1-CUSTODY-CLOSURE":"...",...},
  "w1_gap_closure":{"generation-order":"...",...},"w1_subgap_closure":{"W1-CUSTODY":"...",...},
  "required_corrections":[{"id","item","correction","evidence"}],"item_findings":{...},"w1_assessment":"...",
  "jackal_reproduction":[...],"open_obligations":[...],"approval_granted":false,"proof_acceptance":false,
  "phase_acceptance":false,"source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure of each prior correction, gap and sub-gap, any new required corrections, the W-1 v5 assessment in
two sentences, and the sha256 of each of your four output files.
