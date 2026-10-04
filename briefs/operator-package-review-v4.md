You are the independent, different-author reviewer for: the WORLDLINE Phase One consolidated OPERATOR DECISION PACKAGE
(final draft, v4 line). The author is the Claude Code lead (claude-opus-5-5), with drafting and analysis subagents for some
referenced designs. You are actual gpt-6.1-sol and authored nothing under review. The package goes to the human operator after
your review; it asks for choices and grants none.

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/package-review/gpt61-v1
- Do not import or execute WORLDLINE or frame code (read proof_manifest.py as text/AST only); do not run compilers, provers,
  builds, tests, sudo, useradd, setfacl, mount, loginctl, systemctl, project-vault, restic or any window/reservation action. Do
  not write SIA notes. Do not modify anything outside your cwd. Never read anything under ~/.local/share/sia/.gbrain/.
- Use JACKAL (MCP) for any derived arithmetic; carry its status class and non_claims. Re-derive every number the package
  derives (storage requirement, margins, rates, image minimums, counts) and say whether it reproduces.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Package under review: W/work/claude-operator-decision-package-v1/DRAFT-v4.md (sha256
  e36f517c6ecc891f256626bbbeb6f049dd57a2c565a632c763b73d7b3baf0b48, 35034 bytes; a byte-identical frozen copy is
  WT/package-frozen/DRAFT-v4.md). Earlier drafts v0-v3 are preserved beside it. Verify the hash before reviewing.
- Requirements (verbatim authority): W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json};
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- WORLDLINE monitor corrections the package must carry exactly (quoted in the package where used):
  - storage: observations versus justified allowances; no shrinking an allowance because the last run used less; sampling plus
    a factor on observed write rates is not a bound; keep dispatch deferred if safe capacity cannot be established;
  - frame: an own-inode "detected and refused" residual does not satisfy "frame mutations stay within the intended run tree";
    V5-B02 stays OPEN until the original criterion is met; a reviewer cannot grant an operator-only weakening;
  - a root-made filesystem is a candidate, not an established sufficient design or approved sudo/install action;
  - Packet 13 notice removal is an untested hypothesis until matching-source evidence exists;
  - no review-model substitution: every review is actual gpt-6.1-sol;
  - isolation guard: success through another tool is not clearance; no alternate-tool bypass of a refusal;
  - pinned implementation files (supervision correction, 2026-10-04): "the human's preserved authorization covers routine
    reversible engineering; a review brief or review finding is not new authority to add approval gates"; "Do not request
    retroactive or blanket operator approval solely because an implementation file is pinned"; HANDOFF acceptance-sequence
    item 1 "explicitly requires reviewed source deltas and recomputing effective pins"; this "is not permission to redefine
    reference semantics, change an unapproved API, lower contracts, scope, accepted cases or controls, or waive any
    proof/runtime/review gate. Material API/owner-policy and merge/release/install/sudo/production/real-PRIME decisions remain
    reserved." The sealed D2 review and the lead's erratum E1 are preserved unchanged.
- Sealed actual gpt-6.1-sol reports it relies on (verify each review-freeze.json against its files):
  - frame v5: W/work/claude-scratch-frame-v5/review/gpt61-v1;
  - D1 v2: W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1; D1 v3: WT/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1;
  - C-API v2: W/work/claude-capi-boundary-design-v2/review/gpt61-v1; C-API v3: WT/designs/claude-capi-boundary-design-v3/review/gpt61-v1;
  - D2 inventory: WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1;
  - root-worker seam design v1: WT/designs/claude-root-worker-seam-design-v1/review/gpt61-v1;
  - compositions v5-alpha/beta: W/work/claude-composition-v5-{alpha,beta}/review/gpt61-v1.
- Supporting lead documents (author-side; not reviewed unless stated):
  - isolation/storage proposal W-1: WT/proposal/ISOLATION-STORAGE-PROPOSAL.md;
  - runbook Gate 0 v4.1: WT/RUNBOOK-first-proof-iteration.md (history in WT/runbook-history);
  - frame plan: WT/frame-v6-PLAN.md;
  - recursive-notice evidence: W/work/claude-operator-decision-package-v1/evidence-recursive-notices.json;
  - D2 inventory: WT/designs/claude-d2-checked-ghost-inventory-v1/{INVENTORY.md,inventory.json};
  - erratum E1 (pinned-file coverage, written after the D2 review sealed): WT/errata/d2-inventory-E1-pinned-files.md;
  - manifest for P-1 facts: W/work/claude-composition-v5-beta/source/runtime/worldline/proof_manifest.py;
  - packets: W/work/claude-workflow-v1/packets (01-14; read-only tree) and WT/packets (13, 14);
  - isolation record: WT/ISOLATION.md; live status index: WT/STATUS.md.

WHAT TO DECIDE (numbered; answer each in REVIEW.md with file:line evidence)
1. Facts. For every item (S-1, F-1/W-1, P-1, R-1, R-2, C-1, C-2, C-3, N-1, N-2, N-3, RW-1 and the isolation record), are the
   facts, pins, quoted criteria and numbers accurate against their sources? Does every derived number reproduce under JACKAL?
   Are observations distinguished from allowances and judgments, with no past observation presented as a bound?
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
5. Storage. Is Gate 0 v4.1 correctly carried? Does the package avoid presenting any sampling monitor or past rate as a bound,
   and require a reviewed admission argument before the gate changes?
6. P-1 (pinned implementation files). Verify the effective pin count and the per-packet pinned-file table (erratum E1) from the
   manifest AST and the packet file lists. Is the sealed D2 correction C-PINS carried verbatim, and is its provenance stated
   accurately (the lead's own D2 brief item 4 introduced the "operator approval for pinned text or public contract" boundary)?
   Then correct the provenance/scope inconsistency against the original requirements: state what HANDOFF acceptance-sequence item
   1 and the fixed phase exit require for an explicit reviewed delta to a pinned implementation file, as distinct from changes to
   reference semantics, specifications or public contracts, APIs/ABIs, owner policy, or any reserved decision; and state which
   part, if any, of C-PINS's operator-approval boundary has a basis in the original requirements. Confirm that the package
   requests no approval solely because a file is pinned, and that it presents no reserved change (redefined reference semantics,
   an unapproved API change, lowered contracts/scope/accepted cases/controls, or a waived proof/runtime/review gate), including
   in R-1 or R-2 options, as lead-authorized.
7. Native and C-API items. Are the D1 OD-1/OD-2 packages and the C-API operator items (D-13, N-06, N-01) stated as the sealed
   v2 and v3 reviews rule? Are the D2 hazards stated with their evidence class (static reasoning, not measurement) and with the
   sealed corrections (C-SLOT, C-SUM, C-OWNER, C-EMPTY, C-UNIT, C-PACKET-GAP, C-P12-REACH, C-COPY, C-ABI)?
8. Anything that would let the human's choice weaken a contract, domain, accepted case, fixture, threshold, control or proof
   floor, add an assumption, suppress checked code, or skip a review, without the package saying so plainly.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only). On resume continue from the first unfinished
item; never rewrite an existing file.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json:
  {"schema":"claude-operator-package-review-v1","package":"<absolute path>","package_sha256":"<sha256 you computed>",
  "different_from_author":true,"actual_model_selection":"gpt-6.1-sol","author":"Claude Code lead claude-opus-5-5",
  "verdict":"READY_FOR_OPERATOR|READY_WITH_REQUIRED_CORRECTIONS|NOT_READY","required_corrections":[{"id","item","correction","evidence"}],
  "item_findings":{"S-1":"...",...},"w1_assessment":"...","p1_assessment":"...","jackal_reproduction":[...],"open_obligations":[...],
  "approval_granted":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, required corrections, the W-1 assessment in two sentences, the P-1 provenance/scope correction in two
sentences, and the sha256 of each of your four output files.
