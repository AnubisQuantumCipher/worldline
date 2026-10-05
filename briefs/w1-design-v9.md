You are the independent, different-author design reviewer for: WORLDLINE Phase One isolation proposal W-1 v9 (scratch-frame
confinement), on W-1's own design-review track. The author is the Claude Code lead (claude-opus-5-5) through an author-role drafting
subagent. You authored nothing under review and are not the drafting agent. Earlier revisions v6, v7 (gpt-6.1-sol) and v8 (independent
Claude review subagent) were NOT_ENDORSED.

HARD LIMITS
- Passive reading and hashing only. Do not import or execute WORLDLINE or frame code. Do not run compilers, provers, tests, sudo, unshare,
  nsenter, mount, setfacl, chmod, loginctl, systemctl (including read-only show/cat), tune2fs, strace, project-vault, restic or any probe;
  nothing privileged or mutating. Reading installed kernel headers, documentation, man pages, /proc/sys values and pacman's local database
  read-only is fine; label anything you rely on that you could not verify locally. Do not write SIA notes. Do not modify anything. Never read
  or list anything under ~/.local/share/sia/.gbrain/. Never list or stat /home/sicarii itself or ~/iPad, ~/iPadBackup. Do not read any session
  transcript, review-records/, WT/proposal/v8-review/gpt61-v1, any review directory of v9, or drafts in progress (WT/designs/*-v7/,
  WT/designs/claude-native-bigint-d1-design-v5/, WT/packets/capi-pk0-v3/). Never start a shell command that waits on stdin.
- Do not stop, kill or interrupt any process. JACKAL (MCP) for any derived arithmetic, sequentially or in groups of at most four; carry
  status, parsed= and non_claims (note: jackal_exact refuses ^ with non-literal exponents).
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception. The only output is a design verdict:
  ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify hashes): WT/proposal/ISOLATION-STORAGE-PROPOSAL-v9.md (sha256 4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b,
  562201 bytes) and WT/proposal/v9-support/jackal.json (2d225e26780c95035f2ef57d79cc1a1758304fb82f08c4a75adab254d2b02270).
  FORM: v9 is self-contained (every unit holds its full text). §18.5 maps all 131 v8 units to v9 units with lines, bytes and sha256; verify
  the map against v8 (WT/proposal/ISOLATION-STORAGE-PROPOSAL-v8.md, 804da95b...) and v7 (8646f0fe...) as v8's units compose.
- Closure targets: W-1 v8's sealed Claude review WT/proposal/v8-review/claude-v1 (REVIEW.md 38dcb076..., review.json afc0d828...; read in
  full): verdict NOT_ENDORSED with required changes W1-V8-HOLDER-IOEXIT, W1-V8-PRESERVATION-ESTABLISH, W1-V8-PREMISE-DISCHARGE,
  W1-V8-WRITER-AS-W, W1-V8-COMPOSED-ENUM, W1-V8-EVIDENCE-EQUIV, W1-V8-FORM-SUBUNIT, and every v7 change, correction, gap and sub-gap it
  left PARTIALLY_CLOSED or NOT_CLOSED. Items it CLOSED must stay closed. Earlier reviews: WT/proposal/v7-review/gpt61-v1,
  WT/proposal/v6-review/gpt61-v1, WT/package-review/gpt61-v{1..7}.
- Criteria: the sealed frame v5 review W/work/claude-scratch-frame-v5/review/gpt61-v1 (V5-B01 REVIEW.md:76, V5-B02 :82); frame sources
  W/work/claude-scratch-frame-v{5,6}/scratch.py, WT/frame-v6-PLAN.md; requirements W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,
  START-CLAUDE.txt,OBLIGATIONS-v2.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- Supervision rule: privileged setup, the launcher and its sudo rule, installation, rollback and every reserved decision stay the operator's;
  the human's 2026-10-05 directives (WT/STATUS.md) delegate routine reversible engineering preserving the original external contract and
  success domain to the lead; a finding is not authority to add a gate; nothing reserved may be lowered.
- LEAD DECISION recorded 2026-10-05 (WT/STATUS.md "D-LEAD-REVIEW-PROVENANCE"): §4.6/§16 adoption joins currently require gpt-6.1-sol
  rollout provenance (v9:848-849, :3789-3794). Under the human's 17:05Z direction reviews are independent Claude review subagents; the lead
  has decided the frame's review-provenance joins will require the provenance of the review mechanism actually used (sealed freeze over
  REVIEW.md/review.json/checks.json, raw-final-message.txt, the reviewer agent id, the sha256 of the reviewer's task output, the
  reviewer_kind claude-subagent, different_from_author), never a label alone, never claiming GPT. v9 keeps the v5 joins; assess whether that
  open item and this decision are stated exactly and whether anything else in v9 depends on GPT rollout provenance.
- Author process: WT/deviations/w1-v9-author-process/NOTE.md (if present; the lead writes it) and the author's disclosures in v9 §0/§20
  (WebFetch of upstream v7.2 kernel files; premise P-KSRC).

THE AUTHOR'S POSITION (claims, not closures): HOLDER-IOEXIT is answered by redesign (seccomp ENOSYS for io_setup/io_uring_setup, new
change V14; P-IOEXIT replaced by P-SECCOMP, P-ASYNC, P-RELEASE); WRITER-AS-W by a new namespace-owner account N (wlscratch-ns, uid 951)
and P-NOOWNER; COMPOSED-ENUM by an actual atom table and reachable-state enumeration in §11.4; PRESERVATION and PREMISE-DISCHARGE by an
ordered probe-and-evidence plan (§13.2: S-1..S-6, U-1..U-14, I-1..I-8) and an operator package (§16.1: O-1..O-5), not by prose;
EVIDENCE-EQUIV by §10.5/§15.3; FORM by self-containment.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Closure of each W1-V8 required change and every still-open earlier change, correction, gap and sub-gap: CLOSED_AT_SPEC_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; closed items still closed. Because preservation and premise discharge require
   execution, state for each whether the specified probe/run, if it produced the stated discharging result, would actually establish the
   item (i.e. is the plan sufficient and correctly specified), separately from whether it has been executed (it has not).
2. The seccomp/io redesign: does denying io_setup and io_uring_setup close every asynchronous completion path after populated 0 (consider
   other async write paths: AIO via other syscalls, io_uring via inherited rings or other entry points, splice/vmsplice, sendfile, mmap
   writeback, dirty page writeback after exit, NFS/FUSE, fsync of other descriptors, timers/signals, binder, userfaultfd)? Does denying them
   narrow the original success domain (does any original accepted case use AIO/io_uring), and is that classified correctly?
3. The namespace-owner account N: does it close the writer-as-W vector without opening another (who can act as N, setns, ptrace, owner
   rule), and is its setup correctly operator-reserved?
4. §11.4 atom table and reachable-state enumeration: complete and correct (spot-check transitions); JACKAL-verify the counts.
5. §13.2/§16.1: complete ordered plan; correct S/P/T classes; no circular qualification; each step's discharge/refute criterion exact; no
   step executed or presented as evidence; privileged steps correctly operator-reserved; "redesign, no exception" kept.
6. Form: is v9 self-contained and does §18.5 verify (spot-check at least 20 rows by recomputation, including COMPOSED and REVISED units)?
7. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, add an assumption or an
   approval gate, or present an unverified premise as fact; including the adoption-join/review-provenance item above.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-design-review-v1","design":"<absolute path of v9>","design_sha256":"...","support_sha256":"...","different_from_author":true,
"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)","reviewer_kind":"claude-subagent",
"author":"Claude Code lead claude-opus-5-5 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
"prior_closure":{...},"w1_gap_closure":{...},"w1_subgap_closure":{...},"plan_sufficiency":{...},"io_redesign_assessment":"...",
"namespace_owner_assessment":"...","enumeration_assessment":"...","form_assessment":"...","review_provenance_assessment":"...",
"required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],"approval_granted":false,"proof_acceptance":false,
"phase_acceptance":false,"source_acceptance":false}
