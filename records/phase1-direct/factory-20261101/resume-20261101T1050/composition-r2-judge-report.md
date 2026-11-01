**BLOCK — IPC-DIAGNOSTIC-COMPOSITION revision 2. Diagnostic launch prohibited.**

Verified the judge packet SHA256 `6699bdddba34f2d8b3e82e9cd04a22da25bc8e3feaef5e89f441420c827c12d9`, all eight direct references and all 62 revision-packet references. Final readback matched. Read applicable instructions, both reports, relevant source and retained public tool evidence.

**Independently TESTED:** bounded, pure in-memory reproduction completed in **0.062 seconds**, using `timeout 15s python -B -W error`. Starting from the synthetic normal report, changing only the first candidate ID and recomputing the complete candidate digest produced:

| Candidate IDs | Consumer interpretation |
|---|---|
| `1,2,3` | Unique join |
| `03,2,3` | **Unique join incorrectly asserted** |
| `0003,2,3` | **Unique join incorrectly asserted** |
| `3,2,3` | `UNPROVEN`: ambiguous |

All four candidate digests verified. The two noncanonical cases contain two numeric identities equal to opened FD mount ID `3`.

**Source-confirmed cause:** `ram_qualification_v6.py:953` admits leading-zero decimal IDs; line 1014 compares raw strings. Consequently, the required unique numeric FD-row correlation is not established. This directly violates the retained requirement and malformed-input ambiguity refusal obligation. It cannot be waived by relabeling the guarantee as textual matching.

The two reviewers’ evidence supports the four original repairs. Those passing regressions do not discharge this additional mandatory defect. Preserve the preparation approval, dissent, prior failures and counterexamples unchanged; this decision follows the demonstrated requirement failure rather than reviewer voting.

**Reachability limit:** this is a synthetic malformed-consumer counterexample. It does **not** demonstrate that the authentic fixed producer emits noncanonical IDs, that forgery is reachable, or that operational authority was bypassed. That caveat limits the consequence claimed; it does not satisfy the missing mandatory consumer guarantee.

No operational main, IPC, mount, compiler, proof, network or storage-management action ran. No files or pycache were written. Whole-system correctness remains **UNPROVEN**.

The sole revision allowance is exhausted: **no further revision or review reset**. Smallest sound next step: the integrator retains this decision and reproducer evidence, records the mandatory issue as unresolved, and continues separately authorized independent work. Any future acceptance would require separately authorized work and independent evidence establishing the unchanged uniqueness obligation; this decision grants none.

Actual diagnostic **UNRUN**; storage window **NOT_GRANTED**; no mechanism, product or Phase One credit; F7 **NOT PERFORMED**.
