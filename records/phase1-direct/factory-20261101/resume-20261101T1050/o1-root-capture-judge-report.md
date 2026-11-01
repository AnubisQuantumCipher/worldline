**REJECT — D159 initial operational envelope.**

The exact envelope does not establish its registered complete-capture failure contract. The independent approval’s postchecks cannot detect the adversary’s source-derived first-write failure scenario.

- **OBSERVED:** `scripts/phase1_heavy.py:127,132` invokes cleanup subprocesses with inherited root streams and discards their exit statuses. AST inspection confirmed both calls are discarded expression results.
- **OBSERVED:** heavy returns the worker result at line 138. Guard `wrapper_terminal` checks terminal receipts and scope state; it does not establish successful diagnostic writes by those cleanup subprocesses.
- **Source-derived counterexample:** a cleanup diagnostic’s first write fails, its subprocess returns nonzero, and the discarded result leaves no capture bytes. If the scope subsequently terminates and worker result is zero, root exit and terminal evidence can still satisfy the proposed checks. Empty-file hashes cannot distinguish this failure from genuinely empty output.
- **UNRUN:** native fault injection. This is a demonstrated source-level observability gap, not a claimed reproduced native failure.

This is a **D159 capture defect**. It neither disproves nor strengthens D158’s existing cleanup guarantee. Cleanup can succeed in the counterexample; unverified cleanup still forbids a successor. Sealed D158 manifest remains `561833c2cfed7979a2148ab0151329ee3c58752aacfa3586c5ddc0c17b0e541e`, with **zero source revisions remaining**.

**Integrity OBSERVED before and after:** all **7 judge references and 54 review references** matched sizes and SHA-256 values; carrier HEAD remained `7a3127281389f58f2291c86d123ec1f920cee6b7`. Judge packet remained `a608fd09968149223a4933e0d8af1ee470c6e5bf2212d35033cbb97930f9760a`; review packet remained `705d1623fa8307dbd6bf75108c40a970790c78dfd781e6b78f3ee5c57978fbf5`. Commands and outputs are retained in this public tool transcript. No filesystem writes or operational execution occurred.

**Smallest permitted next action:** prepare D159’s one remaining operational revision proposing a bounded native capture boundary that independently checks capture output and write/close failures. Do not implement it under this review or edit sealed D158. Review evidence must address first-write and partial-write failures, overflow, failed redirection, nonzero/signal exit, and exact ownership/terminal reconciliation. An unresolved revision remains BLOCKED.

Internal judgment only; requested Astra/medium identity has no independent backend attestation here. DUAT remains paused/released; no runtime admission, O1 qualification, F7 or Phase One acceptance is granted.