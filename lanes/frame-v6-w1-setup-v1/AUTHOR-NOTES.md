# AUTHOR-NOTES.md — provenance, deviations, and the lines held

**Author.** This is Claude (Opus 4.8) work, produced as the DRAFTING implementer (not a
reviewer) for WORLDLINE Phase One. It is never to be represented as GPT or GPT-6.1 work. It
grants nothing, reviews nothing, and establishes no premise. Codex owns the privileged
execution and the human's authentication; this session executed nothing privileged.

**What this package is.** FROZEN, REVIEWABLE, UNINSTALLED source: the concrete W-1 confinement
setup/installer artifacts that v11 §16/§16.1 require (the non-enforcement parts), plus an exact
EXISTS/PARTIAL/MISSING gap record and the install/rollback order. It is input to review, not an
installation.

## Deviations and judgment calls (disclosed)

1. **Numeric identities instantiated as candidates.** v11's S-A/S-B are templates with `<W>`/
   `<N>`. I instantiated W=950, N=951 (the §3.1 candidates observed 2026-10-04). These are NOT
   pinned; the concrete inventory re-verifies and pins them (`assets/notes/numeric-identity.md`).
   Deviation from byte-exact spec: the scripts carry concrete numbers and a leading provenance
   comment block, so their sha256 will differ from the concrete inventory's pinned texts. Marked
   SOURCE-ONLY in every script header.

2. **Enforcement code deliberately NOT authored.** The directive scopes the assets to "non-
   enforcement setup artifacts (the sandbox's own locked-down rules)." I therefore did NOT write
   the four frame members (`front.py`, `writer.py`, `sandbox_launch.py`/RL, `launch_target.py`)
   nor the step-13b seccomp BPF program nor the Landlock ruleset. Those are enforcement code and
   are recorded as MISSING (GAP.md M11-M24) with their exact spec. Producing them is a separate
   implementation task that must go through the §16 step 2 code review.

3. **No exploit/refutation procedure reproduced.** The async-holder refutation of P-ASYNC/
   P-RELEASE and every privilege-boundary exercise are OBLIGATION-level, operator-prepared, and
   OPEN (§13.1, §16.1 O-ASYNC/O-2′). This package reproduces NONE of them — not the method, not
   the steps. It carries only the obligation and the observed-state (byte-equality) predicate, as
   the spec itself does. The step-13b seccomp filter and the confinement ACLs/sudoers are kept
   DEFENSIVE: they are the sandbox's own locked-down rules, not attacks.

4. **ACL `*.expected` files are reconstructed, not observed.** `getfacl -n -c -p` exact bytes
   (trailing newlines, multi-operand block separation) were not observed (nothing executed), so
   `lease.expected` is omitted rather than guessed and the others carry a caveat in
   `assets/acl/README.md`. The concrete inventory must regenerate and pin them from a reviewed
   dry build.

5. **polkit asset = a deliberate absence.** W-1 installs no polkit rule; the requirement is the
   P13 inventory obligation. Recorded as `assets/notes/polkit.md` rather than a rule file. Not
   weakening policy to avoid authentication.

6. **systemd "unit property file" = runtime scope properties.** In the no-images configuration
   there is no installed unit file; the scope is transient (RL `systemd-run --scope`). I produced
   `assets/systemd/wlscratch-scope.properties` documenting the exact `-p` arguments, and noted the
   images-only mount units as conditional (N/A unless images).

7. **rollback.sh is a template with named capture obligations.** The per-step raw before/after
   captures and the M0/M1 retained-tree manifests are operator-package O-4 artifacts; the template
   names them (`capture "…"`) rather than inlining fabricated capture bodies.

## Lines held (per the operator directive and START)

- Write/Edit only under this lane directory; read-only everywhere else. Executed NOTHING
  privileged (no sudo/useradd/usermod/groupadd/systemctl/setfacl/unshare/mount), ran no prover,
  no test, did not run the frame, created no set-ID/capability object, collected/wrote no
  password, marked no setup executed.
- Every NAMED_UNESTABLISHED premise stays OPEN. A spec-level statement is not execution evidence.
  The critical premises (P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC) and V5-B02 remain OPEN.
- Preserved every original contract, fixture, control, proof-floor and source identity: the base
  frame v6 `scratch.py` is referenced, never modified; the 67/104 reachable-set and 19/30 atom
  counts are carried verbatim from v11's own JACKAL derivations.
- Derived counts routed to JACKAL (EXISTS 6 + PARTIAL 7 + MISSING 30 = 43, status `exact`;
  43 + 3 N/A = 46, status `exact`; evaluator_sha256 4c0ae28d…). Observed values (file hashes,
  line numbers, byte sizes) are reported as read.

## Environment note

SIA (`sia` MCP server) failed to connect this session (reported connection failure, not a
missing capability), so no start-of-task recall or end-of-task note could be written through it.
Recorded here so a future session knows to leave the durable note once SIA is reachable.
