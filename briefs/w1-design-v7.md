You are the independent, different-author design reviewer for: WORLDLINE Phase One isolation proposal W-1 v7 (scratch-frame
confinement), on W-1's OWN design-review track. The author is the Claude Code lead (claude-opus-5-5) through an author-role drafting
subagent. You are actual gpt-6.1-sol and authored nothing under review. A separate gpt-6.1-sol session reviewed W-1 v6 (NOT_ENDORSED).

HARD LIMITS
- Passive reading and hashing only. Write ONLY in your current working directory:
  /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/proposal/v7-review/gpt61-v1
- Do not import or execute WORLDLINE or frame code (read scratch.py/proof_manifest.py and toolchain files as text only). Do not run
  compilers, provers, tests, sudo, unshare, nsenter, mount, setfacl, chmod, loginctl, systemctl (including read-only show/cat), tune2fs,
  project-vault, restic or any window/reservation/probe action; nothing privileged or mutating. Reading kernel headers, documentation,
  man pages and /proc/sys values read-only is fine. Do not write SIA notes. Do not modify anything outside your cwd. Never read or list
  anything under ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup. Do not read any session
  transcript.
- Do not stop, kill or interrupt any process or tool, including your own; use bounded read-only commands. JACKAL (MCP) for any derived
  arithmetic, sequentially or in groups of at most four; carry status and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception. The only output is a design verdict:
  ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify hashes): WT/proposal/ISOLATION-STORAGE-PROPOSAL-v7.md (sha256 8646f0fed3cf3f61dceb4fbf3a583f96f2bf7a0adce4986cb415789edeb82a7a,
  501544 bytes; one complete document) and WT/proposal/v7-support/jackal.json (d62cca5521f007ccc7cc59fcce171f0de1d1d60f9e9e90eac75f51db49e20287).
  Its §18.5 maps every v6 unit (v6 = WT/proposal/ISOLATION-STORAGE-PROPOSAL-v6.md, 5a0e861b...): 29 carried byte-identical (the lead
  verified all 29), 63 amended, 26 replaced, 6 new (§22, §22.1-§22.4, Appendix G).
- Closure targets: W-1 v6's sealed review WT/proposal/v6-review/gpt61-v1 (REVIEW.md b519d27d..., review.json f8825bc0..., checks.json
  1a3c6d05..., review-freeze.json b251aab0...): verdict NOT_ENDORSED; its K0 ruling; its eleven required changes W1-V6-PRESERVE,
  W1-V6-READ-MUTATION, W1-V6-COMMIT-AMBIGUITY, W1-V6-COMPOSED-STATE, W1-V6-IMAGE-PIN, W1-V6-C1-DATA, W1-V6-SCAN-STATE,
  W1-V6-COPY-PROBES, W1-V6-INVARIANTS, W1-V6-EVIDENCE-RESTORE, W1-V6-CATALOGUE; and every correction, gap and sub-gap it left
  PARTIALLY_CLOSED or NOT_CLOSED. Items it CLOSED (W1-V5-PROTOCOL-REFUSALS, W1-DURABILITY-RELEASE, W1-SETUP-IDENTITY, W1-RESOURCES,
  the six closed gaps, the eleven closed sub-gaps) must stay closed. Earlier history: WT/package-review/gpt61-v{1..5}.
- The criteria: the sealed frame v5 review W/work/claude-scratch-frame-v5/review/gpt61-v1 (V5-B01 at REVIEW.md:76, V5-B02 at :82); frame
  sources W/work/claude-scratch-frame-v5/scratch.py, W/work/claude-scratch-frame-v6/scratch.py, WT/frame-v6-PLAN.md; requirements
  W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule on approval gates: privileged setup, the root launcher and its sudo rule, installation, rollback and every reserved
  decision stay the operator's; a review finding is not new authority to add a gate; nothing reserved may be lowered.
- Author process record: WT/deviations/w1-v7-author-process/NOTE.md.

THE AUTHOR'S POSITION. After an architecture evaluation (§22) of (a) a root-owned launcher with private namespaces, (b) unprivileged
kernel scoping (Landlock, seccomp, SCM_RIGHTS/pidfd routes) and (c) other routes (c1-c8), the author concludes that NO candidate is
established as preserving the original success domain, keeps V5-B01, V5-B02 and W1-V5-PRESERVATION OPEN, and adopts (a) with Landlock
(the "target view", §12): outputs admitted in place without copy or chmod, mount/user(root-owned)/network namespaces and a cgroup
"populated 0" holder-exit event, with listed changes to the target's world V1-V12 (§12.3) and frame-side changes C1-C7, D1-D6, R1-R2
(§21). Preservation for the allowlisted actions holds only if the new premise TOOL-CLOSURE holds (none of V1-V12 changes the observable
result of any of the 5 allowlisted actions); its evidence obligation is a source-grounded review of the pinned toolchain.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Closure of each W1-V6 required change and of every still-open earlier correction, gap and sub-gap: CLOSED_AT_SPEC_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; closed items still closed.
2. The architecture evaluation: is each candidate's conclusion sound (cite kernel/LSM facts you can verify from installed headers or
   documentation; label anything you cannot verify)? Did the author miss a preserving route? Is adopting (a)+Landlock the right design
   direction given that it is not established as preserving?
3. The target view: does it establish V5-B01/V5-B02 custody facts under its named premises (no outside principal can obtain or keep a
   description of or name for an admitted entry; holder exit; in-place admission without frame mutation of the admitted tree)? Are
   read-side mutations (the v6 ruling on atime) handled, and is READ-MUTATION correctly left OPEN for R-d, R-f and R-h?
4. V1-V12 and the frame-side changes against the original success domain: which are permissible consequences of the criteria, which are
   narrowings, and is TOOL-CLOSURE the right and sufficient premise (is "5 allowlisted actions" the complete original domain; is a
   source-grounded toolchain review a possible discharge, or what else would be)? Name every change that must be removed or reworked.
5. Premises and probes: every premise named, with a probe and "redesign, no exception"; any unjustified, untestable or circular premise.
6. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, add an assumption or
   an approval gate, or present an unverified premise as fact.

CHECKPOINTS: after each numbered item write checkpoint-<item>.json (create-only); on resume continue from the first unfinished item.

OUTPUT FILES (create-only, os.O_EXCL, fsync, mode 0600, in your cwd)
- REVIEW.md; checks.json; review.json: {"schema":"claude-design-review-v1","design":"<absolute path of v7>","design_sha256":"<sha256 you computed>",
  "support_sha256":"<sha256 of v7-support/jackal.json>","different_from_author":true,"actual_model_selection":"gpt-6.1-sol",
  "author":"Claude Code lead claude-opus-5-5 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
  "prior_closure":{...},"w1_gap_closure":{...},"w1_subgap_closure":{...},"architecture_assessment":"...","target_view_assessment":"...",
  "change_and_premise_assessment":"...","required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],
  "approval_granted":false,"proof_acceptance":false,"phase_acceptance":false,"source_acceptance":false,"report_sha256":"<sha256 REVIEW.md>",
  "checks":{"path","sha256","bytes","mode"}}
- review-freeze.json, written LAST: {"actual_model_selection":"gpt-6.1-sol","different_from_author":true,
  "files":{name:{"sha256","bytes","mode"}}} for exactly REVIEW.md, review.json, checks.json.

FINAL MESSAGE: the verdict, closure per correction, gap and sub-gap, the architecture, target-view and change/premise assessments,
required changes, and the sha256 of each of your four output files.
