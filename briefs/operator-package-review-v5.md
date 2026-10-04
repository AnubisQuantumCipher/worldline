You are the independent, different-author reviewer for: the WORLDLINE Phase One consolidated OPERATOR DECISION PACKAGE, DRAFT v5,
and its supporting W-1 isolation proposal v2. The author is the Claude Code lead (claude-opus-5-5). You are actual gpt-6.1-sol and
authored nothing under review. A separate gpt-6.1-sol session reviewed DRAFT v4 and found it NOT_READY with nine required corrections;
those corrections are your closure targets. The package goes to the human operator after your review; it asks for choices and grants none.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/package-review/gpt61-v2
- Do not import or execute WORLDLINE or frame code (read proof_manifest.py as text/AST only); do not run compilers, provers,
  builds, tests, sudo, useradd, setfacl, mount, loginctl, systemctl, project-vault, restic or any window/reservation action. Do
  not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under ~/.local/share/sia/.gbrain/.
  Never list or stat the home directory /home/sicarii itself or ~/iPad, ~/iPadBackup (FUSE mounts can hang); use full subpaths.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims. Re-derive every number the package or
  proposal derives and say whether it reproduces.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review:
  - Package: W/work/claude-operator-decision-package-v1/DRAFT-v5.md (sha256
    f423d6be7f862f562cb56636ee8d03efc746e5043a12361e9dd4255911694733, 40835 bytes; byte-identical frozen copy
    WT/package-frozen/DRAFT-v5.md).
  - W-1 proposal v2: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v2.md (sha256
    1c116f27bd11bcd3e2fae0d00792b27c2e598928bb9ccc97f1db418102232cf6, 36351 bytes; frozen copy
    WT/package-frozen/ISOLATION-STORAGE-PROPOSAL-v2.md).
  - Runbook Gate 0 v4.2 (O4 qualified): WT/RUNBOOK-first-proof-iteration.md (sha256
    612f110fbf16a2e97ecce76fd007e6ea38907790c55f36f1923de76cac2010f5); v4.1 preserved at WT/runbook-history/v4.1-SUPERSEDED.md.
  Verify all hashes first.
- Prior review (closure targets): WT/package-review/gpt61-v1/{REVIEW.md, review.json, checks.json, review-freeze.json}; verdict
  NOT_READY; required corrections PKG-FACTS, PKG-CRITERIA, W1-CUSTODY, W1-SETUP, W1-RESOURCES, W1-LIFETIME-ROLLBACK,
  D2-CORRECTIONS, OD1-CONSEQUENCES, OD2-CONSEQUENCES, and the detailed W-1 gap list in its item 4. Prior package DRAFT-v4
  (e36f517c...) and W-1 v1 are preserved for comparison.
- Requirements (verbatim authority): W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json};
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- WORLDLINE monitor and supervision corrections the package must carry (quoted in the package where used): storage allowances
  versus bounds; "frame mutations stay within the intended run tree" and the own-inode ruling; root-made filesystem and W-1 are
  candidates; Packet 13 notice removal is an untested hypothesis; every review actual gpt-6.1-sol; isolation guard (no
  alternate-tool bypass); pinned implementation files: "a review brief or review finding is not new authority to add approval
  gates" and "Do not request retroactive or blanket operator approval solely because an implementation file is pinned", while
  reference semantics, unapproved API, contracts, scope, accepted cases, controls and gates stay reserved.
- Sealed actual gpt-6.1-sol reports it relies on (verify freezes): frame v5 W/work/claude-scratch-frame-v5/review/gpt61-v1; D1 v2
  W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1; D1 v3 WT/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1;
  C-API v2 W/work/claude-capi-boundary-design-v2/review/gpt61-v1; C-API v3 WT/designs/claude-capi-boundary-design-v3/review/gpt61-v1;
  D2 WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1; root-worker seam v1
  WT/designs/claude-root-worker-seam-design-v1/review/gpt61-v1; compositions W/work/claude-composition-v5-{alpha,beta}/review/gpt61-v1;
  package v4 WT/package-review/gpt61-v1.
- Supporting (author-side): WT/frame-v6-PLAN.md; W/work/claude-scratch-frame-v5/scratch.py (read as text); WT/errata/
  d2-inventory-E1-pinned-files.md; W/work/claude-operator-decision-package-v1/evidence-recursive-notices.json;
  W/work/claude-composition-v5-beta/source; WT/ISOLATION.md; WT/STATUS.md (live index, not a seal).
- Host facts the proposal cites as observed (you may re-read them passively): /proc/sys/fs/protected_{hardlinks,symlinks,regular},
  /proc/sys/kernel/yama/ptrace_scope, /etc/pam.d/sudo, /etc/pam.d/system-auth,
  /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/cgroup.controllers, /usr/bin/python3.14 digest.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Closure of the nine prior required corrections: for each, CLOSED or NOT_CLOSED with the remaining gap (quote the v5/W-1 v2
   text). Include every sub-gap listed under the prior item 4 (W1-CUSTODY, W1-FINAL-PASS, W1-CLOSURE, W1-CHANNEL,
   W1-WRITE-AUTHORITY, W1-READ-ACCESS, W1-READ-EXPOSURE, W1-PREFLIGHT-IDENTITY, W1-SETUP-PRESTATE, W1-SETUP-ORDER,
   W1-SETUP-EXACTNESS, W1-IMAGE-GEOMETRY, W1-IMAGE-COMPATIBILITY, W1-VERIFICATION-PROBES, W1-FAILURE-LEASE, W1-FAILURE-RECORDS,
   W1-REBOOT-RECOVERY, W1-ROLLBACK, W1-EVIDENCE, W1-NONCLAIMS).
2. Facts and numbers: every fact, quote, pin and derived number in v5 and W-1 v2 accurate against its source; every derived number
   reproduces under JACKAL; observations distinguished from allowances and judgments; no past observation presented as a bound.
3. W-1 v2 design: with the separate target account, exclusive writer lease, streamed inputs and the stated residuals, is the
   design capable of meeting V5-B01 and V5-B02 if implemented exactly with a successor frame? Name every remaining gap. Judge the
   new residuals (lead-process same-user interference, lead authentication, Option A exposure, Option B privilege), the setup
   commands and prestate checks, the probes, the failure table, the rollback order and the evidence list. Do not treat a design
   statement as executed evidence.
4. Criteria and ineligibility: is each unresolved criterion carried verbatim and unweakened; is every exception labelled
   ineligible for closure of the unchanged target; does anything present a reserved change as lead-authorized or add an approval
   gate without an original-requirement basis?
5. Options and authority: complete enough for a human decision, with exact consequences, evidence still required and authority;
   recommendations separated from facts; F-1's reframing (design continues as routine engineering; setup approval later) correct.
6. Anything that would let the human's choice weaken a contract, domain, accepted case, fixture, threshold, control or proof floor,
   add an assumption, suppress checked code, or skip a review, without the package saying so plainly.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only). On resume continue from the first unfinished
item; never rewrite an existing file.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json:
  {"schema":"claude-operator-package-review-v1","package":"<absolute path>","package_sha256":"<sha256 you computed>",
  "w1_proposal_sha256":"<sha256 you computed>","runbook_sha256":"<sha256 you computed>",
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5",
  "verdict":"READY_FOR_OPERATOR|READY_WITH_REQUIRED_CORRECTIONS|NOT_READY","prior_closure":{"PKG-FACTS":"...",...},
  "w1_subgap_closure":{"W1-CUSTODY":"...",...},"required_corrections":[{"id","item","correction","evidence"}],
  "item_findings":{...},"w1_assessment":"...","jackal_reproduction":[...],"open_obligations":[...],
  "approval_granted":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure of each prior correction, any new required corrections, the W-1 v2 assessment in two
sentences, and the sha256 of each of your four output files.
