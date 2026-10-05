You are the independent, different-author design reviewer for: WORLDLINE Phase One isolation proposal W-1 v6 (the protected-writer
confinement design for the scratch proof frame), on W-1's OWN design-review track. The author is the Claude Code lead (claude-opus-5-5)
through an author-role drafting subagent. You are actual gpt-6.1-sol and authored nothing under review. Earlier W-1 versions were
reviewed inside the operator-package reviews WT/package-review/gpt61-v{1..5}; from v6 W-1 is reviewed on its own (the sealed package
review gpt61-v6 ruled that this separation "does not weaken the original requirements").

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/proposal/v6-review/gpt61-v1
- Do not import or execute WORLDLINE or frame code (read scratch.py/proof_manifest.py as text/AST only). Do not run compilers, provers,
  tests, sudo, useradd, setfacl, chmod, mount, loginctl, systemctl (including read-only show/cat), tune2fs, project-vault, restic or any
  window/reservation/probe action; nothing privileged or mutating. Do not write SIA notes. Do not modify anything outside your cwd. Never
  read or list anything under ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup. Do not read any
  session transcript.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. JACKAL (MCP) for any derived
  arithmetic, sequentially or in groups of at most four; carry status and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception. The only output is a design verdict:
  ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify hashes): WT/proposal/ISOLATION-STORAGE-PROPOSAL-v6.md (sha256 5a0e861b042d11f0d9932b6b0f83020d61e944b09e730d2f7279867f24ec8f6d,
  501735 bytes; ONE complete document) and WT/proposal/v6-support/jackal.json (10c30d8ea534269d90b83c56da2dffe38c3e96dff4ff21f426fb9b1378eb23f3).
  Its §18.5 maps every unit against the composed v5 text WT/package-frozen/ISOLATION-STORAGE-PROPOSAL-v5-COMPOSED.md (6cbc9c07...):
  70 carried byte-identical (the lead verified all 70), 29 amended, 16 replaced, 3 new (§14.7, §21, Appendix F). Earlier versions:
  WT/proposal/ISOLATION-STORAGE-PROPOSAL{,-v2,-v3,-v4,-v5}.md.
- Closure targets: the sealed package review WT/package-review/gpt61-v5 (REVIEW.md 88103063..., review.json 2307f10e...): its six W-1
  corrections W1-V5-PRESERVATION, W1-V5-REVOCATION-CONFINEMENT, W1-V5-PROTOCOL-REFUSALS, W1-V5-JOURNAL-FAILED-CLOSE,
  W1-V5-RECONCILIATION-STATES, W1-V5-IMAGE-PINS, and every W-1 correction, section-3 gap and W-1 sub-gap it left NOT_CLOSED (W1-GENERATION-PROTOCOL,
  W1-COMMIT-JOURNAL-EXPORT, W1-TERMINAL-CUSTODY, W1-SETUP-PROBES-ROLLBACK, W1-IMAGE-TREE, W1-CUSTODY, W1-SETUP, W1-LIFETIME-ROLLBACK,
  W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-RECONCILIATION, W1-IMAGE-OBSERVATION; gaps
  generation-order, channel-and-dumpability, prestate-and-installation, commits-and-durable-channel, participants-and-recovery,
  rollback-and-evidence; sub-gaps CUSTODY, CLOSURE, CHANNEL, SETUP-EXACTNESS, FAILURE-LEASE, FAILURE-RECORDS, REBOOT-RECOVERY, ROLLBACK,
  EVIDENCE). Items it CLOSED (including W1-DURABILITY-RELEASE and W1-SETUP-IDENTITY) must stay closed. Earlier reviews:
  WT/package-review/gpt61-v{1,2,3,4}.
- The criteria: the sealed frame v5 review W/work/claude-scratch-frame-v5/review/gpt61-v1 (V5-B01 at REVIEW.md:76, V5-B02 at :82, verbatim
  in W-1 §1 and Appendix A); frame sources W/work/claude-scratch-frame-v5/scratch.py and W/work/claude-scratch-frame-v6/scratch.py,
  WT/frame-v6-PLAN.md; requirements W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json} and
  /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule on approval gates: privileged setup, installation, rollback and every reserved decision stay the operator's; a review
  finding is not new authority to add a gate; nothing reserved may be lowered.
- Author process record (model output, recorded as stated): WT/deviations/w1-v6-author-process/NOTE.md (it read part of the lead's
  transcript, printing only SIA calls, and reports using nothing; it cannot confirm its start-of-task sia.ask).

THE AUTHOR'S CENTRAL CLAIM (§0.4, §9.8 K0): no custody mechanism meets V5-B01 and V5-B02 without some new non-success outcome or
behaviour change, because a target can give another principal a writable open file description or a reference to an output it made
writable, and Linux revokes neither. v6 therefore keeps V5-B01 and V5-B02 OPEN, withdraws v5's revocation and its new refusals, and
offers an in-place route (outputs already closed) and a copy route (O copies outputs into fresh W-created roots; W swaps roots with
RENAME_EXCHANGE), with copy-route confinement K5 resting on new premises PTRACE-GID, EXCH and COPY. §21 catalogues every change against
the original in tables A-E (removed; target restrictions; observable changes C1-C7 including the copy route's inode/time/metadata
differences; non-success outcomes D1-D8; original behaviour kept).

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Closure of each W1-V5 correction and of every still-open earlier W-1 correction, gap and sub-gap: CLOSED_AT_SPEC_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; closed items still closed.
2. The K0 argument: is it correct that V5-B01/V5-B02 cannot be met without a new non-success outcome or behaviour change? If you find a
   mechanism that can, say so. Is keeping both blockers OPEN stated without narrowing them?
3. The two routes: is the in-place route's closure condition exact and checked at the right moment; is the copy route confined at each
   mutation (K5) on its stated premises; is K8 (access-time update of another uid's source on read) a frame mutation under V5-B02?
4. The §21 catalogue: complete and accurate against the original frame (cite scratch.py)? For each change (especially C1 and D1-D8),
   is it a permissible consequence of meeting the criteria or an impermissible narrowing, cap, refusal of an original accepted case or
   weakening of "Preserve the exact base recipe, output partitions, allowlist, caps and original gates"? Name every one that must change.
5. Premises and probes: is every premise named with its probe and "redesign, no exception"; are any premises unjustified or untestable?
6. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, add an assumption or
   an approval gate, or present an unverified premise as fact.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of v6>","design_sha256":"<sha256 you computed>",
  "support_sha256":"<sha256 of v6-support/jackal.json>","different_from_author":true,"actual_model_selection":"gpt-6.1-sol",
  "author":"Claude Code lead claude-opus-5-5 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
  "prior_closure":{"W1-V5-PRESERVATION":"...",...},"w1_gap_closure":{...},"w1_subgap_closure":{...},"k0_assessment":"...",
  "routes_assessment":"...","change_catalogue_assessment":"...","required_changes":[{"id","change","reason","evidence"}],
  "open_obligations":[...],"approval_granted":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per correction, gap and sub-gap, the K0, routes and catalogue assessments, required changes, and the
sha256 of each of your four output files.
