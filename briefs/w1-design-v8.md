You are the independent, different-author design reviewer for: WORLDLINE Phase One isolation proposal W-1 v8 (scratch-frame
confinement), on W-1's OWN design-review track. The author is the Claude Code lead (claude-opus-5-5) through an author-role drafting
subagent. You are actual gpt-6.1-sol and authored nothing under review. Separate gpt-6.1-sol sessions reviewed v6 and v7 (both
NOT_ENDORSED).

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/proposal/v8-review/gpt61-v1
- Do not import or execute WORLDLINE or frame code. Do not run compilers, provers, tests, sudo, unshare, nsenter, mount, setfacl, chmod,
  loginctl, systemctl (including read-only show/cat), tune2fs, project-vault, restic or any probe; nothing privileged or mutating.
  Reading installed kernel headers, documentation, man pages and /proc/sys values read-only is fine; label anything you rely on that
  you could not verify locally. Do not write SIA notes. Do not modify anything outside your cwd. Never read or list anything under
  ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup. Do not read any session transcript, or
  WT/designs/claude-root-worker-seam-design-v5/ or WT/packets/capi-pk0-v2/ (drafts in progress).
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. JACKAL (MCP) for any derived
  arithmetic, sequentially or in groups of at most four; carry status and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception. The only output is a design verdict:
  ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify hashes): WT/proposal/ISOLATION-STORAGE-PROPOSAL-v8.md (sha256 804da95bed429aded004a433d9b43aa6f7fe94a9e94d66eda74d2a44ec4367a6,
  197628 bytes) and WT/proposal/v8-support/jackal.json (cdae49fc3b537aaf8d97849882b9702087390aee4b4bab3fd0a56c5ce485a0c9).
  FORM: v8 is a delta over v7 (WT/proposal/ISOLATION-STORAGE-PROPOSAL-v7.md, 8646f0fe...): §0.1 and §18.5 bind all 124 v7 units by line
  range, size and sha256 (45 CARRIED, 41 AMENDED, 38 REPLACED; the lead verified all 124 rows) plus new §21.1-§21.6 and Appendix H.
  CARRIED and AMENDED units are stubs; some AMENDED stubs state superseding rules rather than exact old/new text. Read v7 alongside v8
  and say whether the composed specification is unambiguous; ambiguity is itself a finding.
- Closure targets: W-1 v7's sealed review WT/proposal/v7-review/gpt61-v1 (REVIEW.md 2cbb34d4..., review.json 1883e530..., checks.json
  0007d396..., review-freeze.json 539a62bc...): verdict NOT_ENDORSED; eleven required changes W1-V7-ARCHITECTURE, W1-V7-VIEW-ROOT,
  W1-V7-HOLDER-STATE, W1-V7-FULL-DOMAIN, W1-V7-C3-DATA, W1-V7-READ-EFFECTS, W1-V7-PROBES, W1-V7-COMPOSED-STATE, W1-V7-SYNC-PROVENANCE,
  W1-V7-EVIDENCE-RESTORE, W1-V7-PREMISES; and every correction, gap and sub-gap it left PARTIALLY_CLOSED or NOT_CLOSED. Items it CLOSED
  must stay closed. Earlier reviews: WT/proposal/v6-review/gpt61-v1, WT/package-review/gpt61-v{1..5}.
- Criteria: the sealed frame v5 review W/work/claude-scratch-frame-v5/review/gpt61-v1 (V5-B01 REVIEW.md:76, V5-B02 :82); frame sources
  W/work/claude-scratch-frame-v{5,6}/scratch.py, WT/frame-v6-PLAN.md; requirements W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,
  START-CLAUDE.txt,OBLIGATIONS-v2.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule on approval gates: privileged setup, the launcher and its sudo rule, installation, rollback and every reserved
  decision stay the operator's; a review finding is not new authority to add a gate; nothing reserved may be lowered.
- Author process record: WT/deviations/w1-v8-author-process/NOTE.md (WebFetch of upstream kernel source; premise P-KSRC).

THE AUTHOR'S POSITION. Following the v7 review's direction, v8 re-evaluated c8 and adopts a "same-identity view" (SIV): the target keeps
the lead's uid, gid, groups, bounding set and limits, inside a user namespace owned by the writer account W with identity maps, a kernel
copy of the host mount namespace (all nosuid, private propagation) with g/source and g/tmpdir bound through an idmap, a private network
namespace, and Landlock MAKE_SOCK/RESOLVE_UNIX/REFER; pull routes are argued from the commoncap/ptrace/pidfd/procfs source; the
remaining changes V1-V4, V6', V7', V8, V10', V12, V13 and frame-side C/D rows are listed OPEN. The author keeps V5-B01, V5-B02,
W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE OPEN (P-IOEXIT gap stated), and lists 32 NAMED_UNESTABLISHED premises
(critical: P-NOSUID, P-NOCAP, because identity maps mean a set-ID root exec inside the namespace would give DAC override over the host).

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Closure of each W1-V7 required change and of every still-open earlier correction, gap and sub-gap: CLOSED_AT_SPEC_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; closed items still closed.
2. The c8/SIV argument: is the pull-route analysis correct (commoncap, ptrace_may_access, pidfd_getfd, procfs), including the choice of
   a W-owned rather than root-owned user namespace? Are push and name routes closed under the stated premises? Is the identity-map
   privilege risk (P-NOSUID/P-NOCAP) fully contained, and is anything else exposed by identity maps?
3. The alternatives table: sound conclusions; any preserving route missed?
4. The remaining changes against the complete original success domain: which are criterion-required, which are narrowings to rework;
   is HOLDER-STATE (P-IOEXIT) correctly left open and stated exactly?
5. Composition and form: is the delta (stubs plus rule-amendments over v7) unambiguous enough to implement and review?
6. Premises and probes: complete register, correct S/P/T classes, no circular qualification, "redesign, no exception" kept.
7. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, add an assumption or
   an approval gate, or present an unverified premise as fact.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of v8>","design_sha256":"<sha256 you computed>",
  "support_sha256":"<sha256 of v8-support/jackal.json>","different_from_author":true,"actual_model_selection":"gpt-6.1-sol",
  "author":"Claude Code lead claude-opus-5-5 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
  "prior_closure":{...},"w1_gap_closure":{...},"w1_subgap_closure":{...},"siv_assessment":"...","alternatives_assessment":"...",
  "change_and_premise_assessment":"...","form_assessment":"...","required_changes":[{"id","change","reason","evidence"}],
  "open_obligations":[...],"approval_granted":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,
  "report_sha256":"<sha256 REVIEW.md>","checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per correction, gap and sub-gap, the SIV, alternatives, change/premise and form assessments,
required changes, and the sha256 of each of your four output files.
