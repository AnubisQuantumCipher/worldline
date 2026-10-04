You are the independent, different-author reviewer for: the WORLDLINE Phase One consolidated OPERATOR DECISION PACKAGE
<VERSION>. The author is the Claude Code lead (claude-opus-5-5), with drafting and analysis subagents for some referenced designs.
You are actual gpt-6.1-sol and authored nothing under review. The package goes to the human operator after your review; it asks
for choices and grants none.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  <REVIEW_DIR>
- Do not import or execute WORLDLINE or frame code; do not run compilers, provers, builds, tests, sudo, useradd, setfacl, mount,
  loginctl, systemctl, project-vault, restic or any window/reservation action. Do not write SIA notes. Do not modify anything
  outside your cwd.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims. Re-derive every number the package
  derives (storage requirement, margins, image minimums, counts) and say whether it reproduces.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow)
- Package under review: <PACKAGE_PATH> (sha256 <PACKAGE_SHA>). Earlier drafts are preserved beside it.
- Requirements (verbatim authority): W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt};
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- WORLDLINE monitor corrections the package must carry exactly. They are quoted in the package; verify the quotes against the
  operator transcript where cited:
  - storage allowances versus bounds;
  - "frame mutations stay within the intended run tree";
  - no review-model substitution;
  - isolation guard.
- Sealed actual gpt-6.1-sol reports it relies on:
  - frame v5: W/work/claude-scratch-frame-v5/review/gpt61-v1;
  - D1 v2: W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1 <AND D1 v3 REVIEW IF SEALED>;
  - C-API v2: W/work/claude-capi-boundary-design-v2/review/gpt61-v1 <AND C-API v3 REVIEW IF SEALED>;
  - compositions v5-alpha/beta: W/work/claude-composition-v5-{alpha,beta}/review/gpt61-v1.
- Supporting lead documents:
  - isolation/storage proposal W-1: W/work/claude-lead-isolation-v1/wt-1/proposal/ISOLATION-STORAGE-PROPOSAL.md;
  - runbook Gate 0 v4.1: wt-1/RUNBOOK-first-proof-iteration.md;
  - frame plan: wt-1/frame-v6-PLAN.md;
  - recursive-notice evidence: W/work/claude-operator-decision-package-v1/evidence-recursive-notices.json;
  - D2 inventory: W/work/claude-d2-checked-ghost-inventory-v1;
  - packets 13/14: wt-1/packets;
  - isolation record: wt-1/ISOLATION.md.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Facts. For every item (S-1, F-1/W-1, R-1, R-2, C-1, C-2, C-3, N-1, N-2, N-3 and any others), are the facts, pins, quoted
   criteria and numbers accurate against their sources? Does every derived number reproduce under JACKAL? Are observations
   distinguished from allowances and judgments, with no past observation presented as a bound?
2. Criteria. Is each unresolved criterion carried verbatim and unweakened? Is any option presented as a resolution when it is an
   exception to the target, an operator-only weakening, or a reviewer-ungrantable change?
3. Options. Is each set complete enough for a human decision, with exact consequences, evidence still required, and authority
   (operator / lead / reviewer)? Are recommendations clearly separated from facts?
4. W-1. If implemented as described with a successor frame, would the protected-writer design be capable of meeting the frame
   v5 V5-B01 required change ("custody that prevents the admitted generation from changing before use") and V5-B02 required
   change ("enforced location custody ... independently protected writer/location boundary")? Name every gap. Also judge:
   - the authority boundary;
   - the setup commands: are they exact, minimal, reversible and verifiable, and does any widen access beyond the stated need;
   - the failure/custody table;
   - the rollback, and that nothing is deleted;
   - the retained evidence;
   - the resource budget, including whether optional images are correctly described as enforcement rather than capacity;
   - the non-claims.
5. Storage. Is Gate 0 v4.1 correctly carried? Does the package avoid presenting any sampling monitor as a bound, and require a
   reviewed admission argument before the gate changes?
6. Native and C-API items. Are the D1 OD-1/OD-2 packages and the C-API operator items (D-13, N-06, N-01) stated as the sealed
   reviews rule? Are the D2 hazards stated with their evidence class (static reasoning, not measurement)?
7. Anything that would let the human's choice weaken a contract, domain, accepted case, fixture, threshold, control or proof
   floor, add an assumption, suppress checked code, or skip a review, without the package saying so plainly.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only). On resume continue from the first unfinished
item; never rewrite an existing file.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json:
  {"schema":"claude-operator-package-review-v1","package":"<absolute path>","package_sha256":"<sha256 you computed>",
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5",
  "verdict":"READY_FOR_OPERATOR|READY_WITH_REQUIRED_CORRECTIONS|NOT_READY","required_corrections":[{"id","item","correction","evidence"}],
  "item_findings":{"S-1":"...",...},"w1_assessment":"...","jackal_reproduction":[...],"open_obligations":[...],
  "approval_granted":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, required corrections, the W-1 assessment in two sentences, and the sha256 of each of your four
output files.
