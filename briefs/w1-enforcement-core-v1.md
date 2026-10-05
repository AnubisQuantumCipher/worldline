You are the independent, different-author code reviewer for: the WORLDLINE Phase One W-1 scratch-frame ENFORCEMENT CORE,
revision v1 (the W-1 §16 step-2 code review). The author is the Claude Code lead (claude-opus-4-8) through a drafting subagent.
You authored nothing under review and are not the drafting agent. This is the §16 step-2 independent code review of the
authored enforcement, required BEFORE the §16 step-5b critical-premise E0 review and BEFORE O-1 installs anything.

WHAT THIS IS. W-1 (§12.2 and the §3/§5/§9.8/§13.1/§15.3 seam) is the scratch-frame confinement: a privilege split
F (front/coordinator) → W (writer; the single mutation choke point) → RL (the launcher that constructs the confined view)
→ L/C/O (the launched target), plus the §12.2 16-step view construction (mount/net/user namespaces, idmapped binds, a
tmpfs skeleton, Landlock, a step-13b seccomp filter that forces the async-submission syscalls to ENOSYS, a
mountinfo-independent verification, and an exact {0,1,2} O_CLOEXEC fd discipline). This lane is the SOURCE of that
enforcement, authored as a FROZEN, REVIEWABLE, UNINSTALLED delta over the reviewed base frame v6 scratch.py. Nothing is
installed, compiled, or executed; adoption stays BLOCKED (v11 §23; the sealed v11 design review is NOT_ENDORSED with the
remaining obligations execution-bound). You grant no acceptance of W-1 or the frame; your only output is a code-review
verdict: ENDORSED, ENDORSED_WITH_REQUIRED_CHANGES or NOT_ENDORSED.

CRUCIAL FRAMING — serving a premise is NOT discharging it. The critical premises P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP,
P-ASYNC (and P-KSRC) stay NAMED_UNESTABLISHED and OPEN; a refutation of any ONE forces redesign (v11 §9.8 N7). Writing the
enforcement that makes a premise CHECKABLE provides no evidence for it — discharge is the operator's reviewed runtime probe
(E0 source readings S-2/S-5, E1 operator boundary exercises, E2 installed selftest/capture). Do NOT credit any construct as
discharging its premise, and flag anywhere the code or its SELFCHECK implies otherwise. Equally: a brief or finding is not
authority to add an approval gate, narrow a domain, or weaken a control.

HARD LIMITS. Passive reading and hashing only. Do NOT execute, import, compile, build, or run ANY member (read the .py as
text/AST and the .c as text); no gcc/cc, no prover/tests, no sudo/systemctl/unshare/mount/seccomp. Per override item 6
(shell hygiene): write no file anywhere, never run a command that reads stdin, never background a command, use command
ls/os.listdir. Never read/list ~/.local/share/sia/.gbrain/; never list or stat /home/sicarii itself, ~/iPad or ~/iPadBackup.
Do not read any review directory of THIS lane or any session transcript/rollout. JACKAL (MCP) for every derived number,
carrying status, parsed= and non_claims. (The members are Python and C, not Ada/SPARK; the Ada-skills rule does not apply
unless you find Ada under review.)

CONTEXT (W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; WT = W/work/claude-lead-isolation-v1/wt-1)
- Under review, in WT/lanes/frame-v6-w1-enforcement-v1/ (verify every hash yourself with sha256sum):
  - front.py            e491587a1752717277ac1253731b84740343ab2c42d453fae2d36c49134db96f  (F coordinator)
  - writer.py           17db5d9baac764945aff580e4c34b613a47e89947673d594e0adf8ed9235b837  (W: lease/choke/commit)
  - sandbox_launch.py   652d74a1b9dfb196067599ff14d1f9f944739c6850d9a8d85415fd8fcdbb40b4  (RL: §12.2 view construction)
  - launch_target.py    8d651056eae9cf30580a6a1155a1db091089e4035cf9b4bd637992421c66e2c7  (L/C/O)
  - nsowner_helper.c    9201332a5c92eef370d823ac45d6978a019038053644dc45d8f0748a6442306a  (§12.2 step-10 helper)
  - framelib.py         1c45b08257a02c4ab79745a300a6e1543adec2502614bf8fb894b67fff32253e  (shared reused primitives)
  - SELFCHECK.md        b5d5b4eb17afc1fd48551911e816c7dc098a61b4a1b1f43bdcfbf7e4c575aef9  (step→member map; construct→premise map)
  - MANIFEST.json       0e30b47be0d119c15d75b032fa77fc74f45a171ed90420788f77c2198869f95f  (pins base + member hashes)
  Base frame v6 scratch.py sha256 2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84 — the lead confirmed it
  is cited and UNMODIFIED, and live frame v5 (f9f6596d…) is untouched. The reused primitives cite base-frame line ranges
  (SELFCHECK §A) — spot-check a few against WT/work/claude-scratch-frame-v6/scratch.py (read-only) that the cited logic
  matches and is not silently altered.
- The spec: WT/proposal/ISOLATION-STORAGE-PROPOSAL-v11.md. Read §12.2 (the 16 steps + 13b) in FULL, plus §3 (members/roles),
  §5 (§5.1 lease, §5.2 mutation choke point, §5.3 the P-NOOWNER route), §9.8 (N1–N7, the premises and the critical list),
  §10.1 (the O_TMPFILE commit), §13.1/§13.2 (the probe staging), §15.3 (export ACL), §8.3 (the attribute table), §16 (the
  review order; step-2 is this review, step-5b is the later E0 review), §16.1 (O-1, O-ASYNC). SELFCHECK.md §A is the author's
  own step→member map and §B the construct→premise map — use them as a guide, verify against the code, do not trust them.
- The sealed v11 design review (WT/proposal/v11-review/claude-v1) is required reading as the closure context: it is
  NOT_ENDORSED with the remaining obligations execution-bound. This code review does not reopen the design; it reviews the
  faithfulness and soundness of the enforcement SOURCE against that design.

WHAT TO DECIDE (answer each in REVIEW.md with file:line evidence)
1. §12.2 step fidelity. For each of steps 1–16 and 13b, does the named member.function actually implement what v11 §12.2
   specifies, including each step's own verification (the right-hand column of SELFCHECK §A)? Call out any step that is
   missing, weaker than the spec, out of order, or whose verification is absent/stubbed. Pay specific attention to: step 2
   (invoker-is-W: SUDO_UID==W AND nearest non-sudo ancestor uid==W, else refuse — is there a spoofable path?); step 3/12
   (exact {0,1,2} fd set, scandir fd excluded — can an extra inherited fd survive to execve?); step 10 (the U8 identity map
   0 0 4294967295 and M_run map W 1000 1; NS_GET_OWNER_UID==N; the helper reaped before L exists); step 14 (credential drop:
   setresuid(1000), bounding set reduced, Cap{Prm,Eff,Amb,Inh}=0, the NoNewPrivs/Seccomp:2 verification).
2. The step-13b seccomp filter (build_async_submission_filter / install_async_submission_filter). Read the BPF program as
   data: does it force io_setup AND io_uring_setup to ERRNO|ENOSYS on BOTH the AARCH64 table (io_setup=0, io_uring_setup=425)
   AND the 32-bit ARM compat table (io_setup=243, io_uring_setup=425), with the architecture checked via AUDIT_ARCH before
   the syscall-number compares (so a compat-mode call cannot slip the aarch64 numbers), and ALLOW otherwise? Is the arch
   match-fail handled safely (not a blind ALLOW)? Is there any jump/offset that lets either syscall through? Confirm the
   constants are composed from installed headers, not magic literals. (Use JACKAL for any arithmetic you do on the BPF
   offsets or the 2^32-1 map value.) NOTE the author's flagged correspondence: the ARM numbers 243/425 are CARRIED-FROM-SPEC
   (v11 App I), not read from the installed aarch64 headers — decide whether carrying them is acceptable pending S-1/S-2 or a
   blocking defect, and whether a wrong compat number would silently leave a hole.
3. Landlock (build_landlock_domain, step 13). Ruleset over {MAKE_SOCK, RESOLVE_UNIX, REFER}; REFER on /, MAKE_SOCK on the two
   bind roots, NO RESOLVE_UNIX grant; landlock_restrict_self under CAP_SYS_ADMIN with no no_new_privs. Is the ABI≥6 assertion
   present and correct; is the attr-size review-dependency honestly flagged; does omitting a RESOLVE_UNIX grant actually deny
   it (default-deny semantics) rather than silently no-op on an older ABI?
4. The privilege seam (F → W → RL → L/C/O). Does F write nothing in T and issue W via the S1 sudo rule only; is W the single
   mutation choke point (lease §5.1 + authorize §5.2) that makes NO boundary/view call and issues RL via the RL rule; does RL
   perform the entire view construction and own the U8 (W never owns U8, §5.3); does L/C/O verify RL_IDENTITY and the
   /proc/self/exe mount id before re-homing the v5 admission/spawn? Is there any path by which W or a view process gains a
   capability or the N identity, or by which F's role is widened? Confirm the directive's loose "front issues RL and writer"
   one-liner was correctly resolved to v11's F→W→RL (SELFCHECK §C.4).
5. The §10.1 commit and lease. framelib.commit (O_TMPFILE + create-only linkat) superseding the base frame's O_CREAT|O_EXCL:
   does it preserve the create-only / no-overwrite guarantee and the export-ACL variant (§15.3)? Does the lease + choke point
   keep every frame mutation inside T (serving V5-B02 — which stays OPEN; the choke point makes the mutation set auditable,
   it does not prove it complete)?
6. Premise honesty (the heart of the review). Verify SELFCHECK §B: every construct is mapped to the premise it SERVES, and
   nowhere does the code, a comment, MANIFEST, or SELFCHECK claim that implementing enforcement DISCHARGES a premise. Flag any
   place that blurs serve-vs-discharge, treats a construct as evidence, or would let an installed use proceed as if a
   critical premise were established. Confirm NO boundary-exploit, boundary-refutation, or async-holder-defeat procedure is
   written or referenced (these are OBLIGATION-level, operator-reserved, OPEN — §16.1 O-ASYNC); if you find one, that is a
   NOT_ENDORSED-level finding and you must NOT reproduce it in your report.
7. The three flagged installed-build correspondences (SELFCHECK §A.52–66) and the four disclosed deviations (§C): for each,
   decide whether it is an acceptable disclosed drafting choice / execution-bound item, or a blocking defect. In particular:
   (a) NS_GET_MNTNS_ID absent → NS_MNT_GET_INFO + /proc/self/ns/mnt inode; (b) framelib.py as a fifth module vs v11's four
   named members; (c) nsowner_helper.c rendered as a fork+execv C target vs v11's "forks a helper"; (d) verb bodies delegated
   to cited installed code rather than re-transcribed — is the delegation boundary drawn so that nothing load-bearing is
   hidden in an un-reviewed "installed body"?
8. Anything else that weakens a contract/control/threshold/proof-floor/source-identity, adds a gate, or would let the frame
   be adopted or installed on weaker grounds than v11 requires. Confirm base frame v6 is unmodified and nothing is installed.

OUTPUT: the format required by the override instructions you were given (REVIEW.md, review.json, checks.json as text, then
the === SEAL === block). review.json schema:
{"schema":"claude-w1-enforcement-review-v1","lane":"<abs path of the enforcement lane>","base_frame_v6_sha256":"...",
"base_frame_unmodified":true/false,"members":{"<file>":"<sha256>",...},"different_from_author":true,
"actual_model_selection":"claude-opus-5-5 (independent Claude Code review subagent, fresh context)","reviewer_kind":"claude-subagent",
"author":"Claude Code lead claude-opus-4-8 (drafting subagent)","verdict":"ENDORSED|ENDORSED_WITH_REQUIRED_CHANGES|NOT_ENDORSED",
"step_fidelity":"...","seccomp_filter":"...","landlock":"...","privilege_seam":"...","commit_and_lease":"...",
"premise_honesty":"...","correspondences_and_deviations":"...","required_changes":[{"id","change","reason","evidence"}],
"premises_still_open":["P-NOSUID","P-NOCAP","P-NOOWNER","P-SECCOMP","P-ASYNC","P-KSRC","..."],"open_obligations":[...],
"adoption_still_blocked":true,"proof_acceptance":false,"source_acceptance":false}
