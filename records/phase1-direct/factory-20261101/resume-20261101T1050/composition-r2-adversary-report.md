**REJECT / BLOCK — IPC-DIAGNOSTIC-COMPOSITION revision 2.** One malformed-input ambiguity remains in the required unique FD-row correlation.

Packet SHA256 is `1454c038af90a356ba46761520c7d4469b4ae260ba6232a0e076dada4c9e6deb`. All 62 references matched their sizes/hashes initially and at final readback.

**TESTED counterexample:** starting with the normal synthetic report, change only the first retained row’s mount ID from `1` to `03`, then recompute `candidate_lines_joined_LF_sha256`. Counts, indices and all other evidence remain coherent. The admitted candidate IDs are numerically `[3,2,3]`, but the consumer returns:

```json
{
  "candidate_digest_verified": true,
  "interpretation": "UNIQUE_RETAINED_FD_JOIN_ONLY_NOT_QUALIFICATION",
  "fd_join": {
    "opened_fd_mount_id": "3",
    "retained_line_index": 2,
    "selected_matches_opened": true
  }
}
```

`0003` produces the same false uniqueness. [ram_qualification_v6.py:953](/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/ram_qualification_v6.py:953) accepts noncanonical decimal spellings; [line 1014](/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/ram_qualification_v6.py:1014) compares raw strings. Under numeric mount-ID identity, two retained candidates therefore denote opened ID3. The packet supplies neither canonical-decimal rejection nor canonical numeric uniqueness.

Exact mutation used after loading the inspected `source_tests.py` definitions and collector:

```python
facts = copy.deepcopy(normal)
rows = facts["mount_evidence"]["rows"]
rows[0]["raw"] = "03" + rows[0]["raw"][1:]
facts["mount_evidence"]["candidate_lines_joined_LF_sha256"] = (
    hashlib.sha256(
        "\n".join(row["raw"] for row in rows).encode("ascii")
    ).hexdigest()
)
result = tests.evaluate(collector, tests.fixture(facts))
```

This is **synthetic malformed-consumer evidence**. It does not establish that the fixed producer emits noncanonical IDs, receipt forgery, or an operational authority bypass. Nevertheless, the packet requires malformed-input ambiguity refusal before claiming a unique correlation.

The four original repairs passed their exact regressions:

- Embedded record boundaries refuse before candidate correlation.
- The 7,996-byte malformed stdout returns a bounded `UNPROVEN` summary.
- The unlisted 33 MiB member refuses after **3,584 expanded bytes**.
- Optional integer `3` versus float `3.0` reports disagreement.

Additional **TESTED** evidence: 42 existing cases; 13 scanner controls; six delimiter controls; seven field/nonfinite controls and generation/I/O containment; 79 additional malformed/type/finite controls; 14 additional archive controls; every truncated prefix of an 800-byte synthetic archive; six malformed-tool summaries; two zero-exit cases; exact 1,023-entry and 32 MiB acceptance with corresponding ceiling-plus-one refusals. The historical 485-byte archive remains scanner-compatible and preserves stdout hash `5cbae8de9c3d5f28a20645a57f6ab04cfd1aade4fb6754aba486eec643a1752a` and its original failure.

One initial reviewer assertion incorrectly required rejection of nullable `stage`; source explicitly permits it. That test expectation was corrected without changing any source. Aggregate test execution remained below two seconds.

**SOURCE-INSPECTED preservation:** inherited collector functions are AST-identical except the declared parent additions; terminal return remains unchanged; guard changes are exactly four literals; maximum collector function length is 54. Operational predicates, retention/restoration, cleanup, lock and resource ceilings remain preserved. Diagnostic exception containment precedes the mandatory result attempt at lines 443–450; genuine mandatory-write failure remains possible.

No files, pycache or receipts were written. No operational main, IPC, mount, compiler, proof, network or storage action ran.

The sole revision allowance is consumed. Smallest sound next step: retain this counterexample and rejection, keep this diagnostic launch blocked, and return to the sole integrator for separately permitted work. Actual execution remains **UNRUN**; mechanism/product/Phase One acceptance remains unproved, and F7 **NOT PERFORMED**.

<oai-mem-citation>
<citation_entries>
MEMORY.md:613-615|note=[background carrier and acceptance boundaries rechecked against current packet]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>
