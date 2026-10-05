You are the independent, different-author design reviewer for: WORLDLINE Phase One isolation proposal W-1 v10 (scratch-frame
confinement), on W-1's own design-review track. The author is the Claude Code lead (claude-opus-4-8) through an author-role drafting
subagent. You authored nothing under review and are not the drafting agent. v6/v7 (gpt-6.1-sol) and v8/v9 (independent Claude review
subagents) were all NOT_ENDORSED.

HARD LIMITS
- Passive reading and hashing only. Do not import or execute WORLDLINE or frame code. Do not run compilers, provers, tests, sudo, unshare,
  nsenter, mount, setfacl, chmod, loginctl, systemctl (including read-only show/cat), tune2fs, strace, project-vault, restic or any probe.
  Reading installed kernel headers, docs, man pages, /proc/sys values and pacman's local DB read-only is fine; label anything you rely on
  that you could not verify locally. Do not write SIA notes. Never read or list ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii
  itself, ~/iPad or ~/iPadBackup. Do not read any session transcript, review-records/, the v9 gpt61 dir (none), any v10 review directory, or
  drafts in progress. Per override item 6 (shell hygiene): write no file anywhere, never run a command that reads stdin, never background a
  command, use `command ls`/os.listdir.
- Do not stop, kill or interrupt any process. JACKAL (MCP) for any derived arithmetic, sequentially or in groups of at most four, literal
  exponents; carry status, parsed= and non_claims.
- Every original Phase One obligation stays OPEN. You grant no acceptance, approval or exception. The only output is a design verdict:
  ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

SENSITIVE-AREA NOTE (read carefully). v10 deliberately specifies the asynchronous-holder enumeration (W1-V9-ASYNC-ENUM) and every
privilege-boundary probe at the level of OBLIGATION + discharge/refute PREDICATE only, NOT as step-by-step procedures, because the detailed
procedures are operator-reserved (an earlier attempt to write them was stopped by a safety classifier; the lead does not reproduce that
material). Your job is to judge whether, AS A CLOSED SPECIFICATION, each obligation is complete and correctly stated and whether its
predicate would actually establish the property if an operator probe produced the stated observation — NOT to ask for, write, or reward a
procedure. Do not request exploit-level detail. If any obligation is under-specified as a specification, say so as a required change at that
same abstract level.

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review (verify hashes): WT/proposal/ISOLATION-STORAGE-PROPOSAL-v10.md (sha256
  d5fe8f3152dd8782adeee65478d7f70fb06e5fac50f0b17943d53598da66d8ef, 111456 bytes) and WT/proposal/v10-support/jackal.json
  (a3e84a9ce492cc53dda10ef4c23e7f2ccbd7838a1ab9e9d3645003ed72089252).
  FORM: v10 is a CHANGE DOCUMENT over v9, NOT self-contained (the author's disclosed primary deviation; recorded as OPEN item
  W1-V10-FORM, §V10-0.7, §20). §18.5 is the change map over v9's 134 units: COMPOSED and NEW units carry computed v10 sha256 (verify a
  sample by recomputation); CARRIED units bind v9's reviewer-verified v9 sha256 (verify against v9 and the sealed v9 review); AMENDED
  units carry ONLY their v9 identities — their composed v10 bytes are NOT materialized (this is the W1-V10-FORM limitation). Assess whether
  the composed specification is unambiguous and reviewable despite this, and whether W1-V10-FORM is the correct disposition or a blocker.
- Base to read alongside: v9 WT/proposal/ISOLATION-STORAGE-PROPOSAL-v9.md (sha256 4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b).
- Closure target: W-1 v9's sealed Claude review WT/proposal/v9-review/claude-v1 (REVIEW.md 51e80795..., review.json 050ef9d7...; read in
  full): verdict NOT_ENDORSED; nine required changes W1-V9-ASYNC-ENUM, W1-V9-NOOWNER-SCOPE, W1-V9-ENUM-USERDEL, W1-V9-PLAN-CONSTRAINTS,
  W1-V9-PREMISE-ORDER, W1-V9-RL-SELFTEST-FIXTURE, W1-V9-INVENTORY, W1-V9-REVIEW-PROVENANCE, W1-V9-FORM-CONSISTENCY, plus the execution-bound
  W1-V8-PRESERVATION-ESTABLISH / -PREMISE-DISCHARGE / -EVIDENCE-EQUIV and every still-open earlier item. Items it CLOSED (W1-V8-WRITER-AS-W,
  W1-V8-FORM-SUBUNIT) must stay closed unless v10's change-document form regresses them — assess that explicitly.
- Criteria: the sealed frame v5 review W/work/claude-scratch-frame-v5/review/gpt61-v1 (V5-B01 :76, V5-B02 :82); requirements
  W/outputs/claude-phase1-handoff-20261004/{HANDOFF.md,START-CLAUDE.txt,OBLIGATIONS-v2.json}; /home/sicarii/Documents/complete-phase1-prompt.txt.
- D-LEAD-REVIEW-PROVENANCE: recorded in WT/STATUS.md and now written into v10 §23 as a CHANGE to an original admission join (not
  preservation), with the operator's verbatim 17:05Z authority and the dependent-site list. Assess whether §23 states it exactly, lists
  every dependent site, specifies the replacement Claude-review join precisely, and keeps adoption blocked until that change is itself
  reviewed. The replacement join must never accept a label alone and never claim GPT.
- Supervision rule: privileged setup, the launcher and its sudo rule, installation, rollback and every reserved decision stay the
  operator's; the human's 2026-10-05 direction delegates routine reversible engineering preserving the original external contract and
  success domain to the lead; a finding is not authority to add a gate; nothing reserved may be lowered.
- Author process: WT/deviations/w1-v9-author-process/NOTE.md (v9) and the v10 author's disclosed deviations (change-document form;
  §13/§13.1/§13.2 authored fresh at the obligation level; no WebFetch for v10, relying on v9's dated kernel observations under P-KSRC).

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. Closure of each of the nine W1-V9 required changes and of every still-open earlier change/correction/gap/sub-gap: CLOSED_AT_SPEC_LEVEL,
   PARTIALLY_CLOSED or NOT_CLOSED, with the remaining gap; closed items still closed. For execution-bound items state whether the specified
   probe, IF it produced the stated observation, would establish the item (plan sufficiency), separately from the fact that none is executed.
2. W1-V9-ASYNC-ENUM as a CLOSED SPECIFICATION: is the enumeration basis (both syscall tables; the four deferred-holder classes) complete;
   is the outside-memory-context holder correctly characterized as held-but-unusable; is the discharge/refute predicate (committed capture
   byte-equals a re-read after every holder class is shown released) one that would actually establish absence of post-commit writes; are the
   self-check overclaims withdrawn? Judge the specification only; do not request a procedure.
3. W1-V9-NOOWNER-SCOPE (every principal/Runas/polkit form for N and W), W1-V9-ENUM-USERDEL (USERGROUPS_ENAB co-removal for k3 and k4, the
   intermediates, S-R reverse rules, the 67/104 recount — JACKAL-verify), W1-V9-RL-SELFTEST-FIXTURE (no installed/S1/RL-reachable path
   creates a set-ID or capability object), W1-V9-INVENTORY (V15 EXDEV, V16 M_run ids, V17 keyrings; exact {0,1,2} fd set + O_CLOEXEC after
   step 8): complete and correct against the installed system facts and the lane, as specifications.
4. W1-V9-PLAN-CONSTRAINTS (U-11 withdrawn; I-7 only under an adopted frame with dispatch-stage Gate 0 and a nondeterminism control, else
   blocked; no allowlisted prover/build runs outside a reviewed frame — START-CLAUDE.txt:8) and W1-V9-PREMISE-ORDER (critical-premise review
   before O-1; S-1 binds the running kernel image/build-id): correct and sufficient.
5. The E0/E1/E2 staging and the E0 step list: is each E0 step genuinely unprivileged, non-mutating outside a lead scratch dir, running no
   prover/compiler/WORLDLINE code and creating no set-ID/cap object (so the lead MAY execute it before endorsement), with an exact
   discharge/refute predicate; are all privileged steps correctly E1/E2 operator-reserved; is "redesign, no exception" kept?
6. Form: does the change map verify (recompute a sample of COMPOSED/NEW v10 hashes; check CARRIED bindings against v9 and the sealed v9
   review); is the AMENDED-units-not-materialized limitation (W1-V10-FORM) the correct disposition or a blocker to review; does it regress
   W1-V8-FORM-SUBUNIT, and is that stated?
7. W1-V9-REVIEW-PROVENANCE / §23: the join change stated exactly, every dependent site listed, the replacement join precise, adoption
   blocked until reviewed; no GPT claim; not presented as "not a loosening" by assertion.
8. Anything else that would weaken a contract, domain, accepted case, fixture, control, threshold or proof floor, add an assumption or an
   approval gate, or present an unverified premise as fact.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text). review.json:
{"schema":"claude-design-review-v1","design":"<absolute path of v10>","design_sha256":"...","support_sha256":"...","different_from_author":true,
"actual_model_selection":"claude-opus-4-8 (independent Claude Code review subagent, fresh context)","reviewer_kind":"claude-subagent",
"author":"Claude Code lead claude-opus-4-8 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
"prior_closure":{...},"plan_sufficiency":{...},"async_enum_assessment":"...","noowner_assessment":"...","enum_userdel_assessment":"...",
"plan_constraints_assessment":"...","e0_staging_assessment":"...","form_assessment":"...","review_provenance_assessment":"...",
"required_changes":[{"id","change","reason","evidence"}],"open_obligations":[...],"approval_granted":false,"proof_acceptance":false,
"phase_acceptance":false,"source_acceptance":false}
