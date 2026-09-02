# Corrections required in the long-form documents

`~/Documents/WORLDLINE-Whitepaper.pdf` and `~/Documents/WORLDLINE-User-Manual.pdf` are PDFs and
cannot be edited from the repository, so the claim defects found in the 2026-09-02 audit passes
are itemized here with exact replacement wording. Apply them at the next regeneration.

Every quote below was extracted verbatim from the published PDFs (`pdftotext -layout`) and each
verdict was checked against the code with a file:line citation.

---

## 1. Whitepaper p.3 §1, Executive summary — **highest priority**

This is where a reader forms their model of what "formally verified" buys.

> Every state transition, parent relationship, and collapse authorization decision is computed
> in Ada 2022 / SPARK code whose absence of runtime error and functional contracts are
> discharged by proof before the library is installed.

Two of the three clauses are false. `nm -D --defined-only lib/libworldline_core.so` exports
exactly seven symbols and none is for ancestry; `core/worldline-c_api.adb` withs only
`Causal_Graph, Collapse, Receipts, Transitions`. The parent-relationship check that actually
runs is `transaction.py:_is_ancestor` — a Python parent-pointer loop. The transaction lifecycle
enforced at runtime is `_TRANSACTION_TRANSITIONS` in `transaction.py` plus a SQLite CHECK;
`Transitions.Transaction_Allowed` is proved and never called.

**Replace with:**

> World-state transitions, the collapse authorization decision, and every identity and chain
> hash are computed in Ada 2022 / SPARK code whose absence of runtime error and functional
> contracts are discharged by proof before the library is installed. The transaction lifecycle
> and the fork-ancestry check are enforced in Python against the same rules; the corresponding
> proved units (`Worldline.Transitions.Transaction_Allowed`, `Worldline.Ancestry`) are proved
> but not yet exported through the C ABI.

## 2. Whitepaper p.16, call-out "Why permissive inner flags are acceptable here"

> Each agent runs with its own approval prompts disabled because Bubblewrap is the mandatory
> outer write boundary. The agent cannot reach the canonical reality regardless of what it
> decides to do; the only path back to PRIME is an authorized collapse.

True of the filesystem only. `namespaces.py` emits `--share-net` and `--ro-bind`s the agent's
real credential file.

**Append after the first sentence:**

> That boundary does not cover the network. The world shares the host network namespace and the
> agent's real credential file is projected into it, so a prompt-injected agent retains its full
> network reach and its own credential. Treat disabled inner prompts as safe against filesystem
> damage, not against exfiltration.

## 3. `simulate` — "nothing on the host changes"

Manual p.4 Table 2 and p.11 §6.7; Whitepaper p.15 §11. `simulation.py` sets
`allow_system_roots=True` over `/usr,/etc,/var,/opt,/boot` and shares the same sandbox builder,
so `--share-net` applies.

**Manual Table 2, Effect cell:**

> Nothing on the host filesystem; the command runs in a disposable system future with writable
> overlays over /usr, /etc, /var, /opt, /boot. The future shares the host network, so any network
> side effect the command has is real and not counterfactual.

**Whitepaper p.15:** change "nothing on the host changes" to *"the host filesystem is not
touched … network side effects are not contained."*

## 4. Whitepaper p.14 §9, final bullet

> worldline log --verify replays the complete causal and receipt chains through the proved
> library, so a tampered or reordered history fails verification rather than displaying plausibly.

`store.py:verify_chains` recomputes from owner-writable files and rows seeded at a constant
zero-hash; there is no signature anywhere in `runtime/` or `core/`.

**Append:**

> The chains are SHA-256 hash chains with no asymmetric signature and no external anchor, so
> this detects inconsistent tampering — a partial edit, a reorder, a deletion — and detects
> anything the sandboxed agent could do, since it cannot reach the store. It does not detect a
> consistent rewrite by a process running as you outside the sandbox.

## 5. Whitepaper p.18 §14, "Threats not addressed" — names the wrong actor

The bullet names *"a malicious agent binary exfiltrating data over the shared network"*, a
supply-chain framing. The real adversary is a **legitimate** binary given hostile instructions.
The adjacent "Threats addressed" bullet lists "credential leakage into captured state", which is
about manifests — not the live credential mounted into the world. The reachable path falls in
the gap between the two bullets.

**Split into its own bullet:**

> a coding agent inside a world — trusted binary or not — that is prompt-injected by its mission
> or by repository content and uses the shared host network to exfiltrate the credential file
> projected into its world, or to reach host-local and LAN services. There is no egress filter
> today. "Credential leakage into captured state" above refers to manifests, payloads, and
> receipts, not to what a running agent can read and send.

## 6. Whitepaper Table 9 / `diagnostics.md`: `OWNER_MISMATCH` cannot be returned

Both `collapse_decide` call sites pass the same owner value on both sides
(`transaction.py` prepare and `_authorize`), so this decision code is unreachable from the
shipped runtime.

**Annotate the row:**

> Reserved. The runtime currently supplies the same owner identity on both sides of this
> comparison, so this code cannot be returned by the shipped call sites.

## 7. Whitepaper Table 4 / Table 19 / Manual Figure 1 — stale metrics

Measured on the 1.0.0 import (`git archive d88a451`): runtime **9863 lines / 58 files** (doc says
9,859 / 59); **44** test methods across **26** modules (doc says 43 / 27); QML **1032 lines / 4
files** (doc says 1,007 / 4). Kernel figures reproduce exactly (`core/` = 941 lines;
`tests/*.adb` = 325 across 2) and the proof figures need no change.

Regenerate against the released tree, or footnote: *"Counts measured at the 1.0 release tree;
see CHANGELOG for the current suite size."* (The suite is 58 tests as of 1.0.2.)

## 8. Manual — network is never mentioned

`grep` for network/egress across the manual returns nothing. Table 2's "Nothing outside the
world's own overlay" is correctly scoped three times over to *your files*, but the same row then
appends a non-file effect ("also spends external model quota"), muddying its own scoping.

Fold the scoping into one clause and add the pointer:

> …and WORLDLINE never copies anything off this machine. (The coding agents it launches do reach
> the network — see §2.)

---

## Already corrected in the repository (no action needed)

`SKILL.md` containment/unattended-run guidance, the kernel-authority sentence, the `simulate`
claim, the health-check assertion count (25, not 26), `SECURITY.md` on what of `$HOME` is
projected into a world, and the sandbox uid description. See CHANGELOG 1.0.2.
