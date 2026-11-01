**REJECT — IPC-DIAGNOSTIC-COMPOSITION revision 1**, including admission for the proposed single nominal diagnostic.

**OBSERVED:** Judge packet SHA-256 matches `e3e4c1f914cbff98be58b152d80350fb13e9d6bf7c983fc8033e874f56c6a182`. All seven direct references and 29 linked composition references match their recorded sizes and hashes. I inspected the consumer source and recorded tool outputs; I did not independently rerun the synthetic cases.

The four counterexamples are supported by the recorded tests and source:

1. Embedded LF allows multiple records inside one retained row, defeating the claimed unique complete FD-row join.
2. The 7,996-byte malformed stdout causes an uncaught summary-size exception. The unchanged terminal return expression does not preserve finalization when execution never reaches it or `result.json`.
3. `getmembers()` checks count after enumeration; member selection also permits the demonstrated unlisted 33 MiB member. Compressed-size and selected-stream bounds do not establish bounded archive parsing or complete inventory correspondence.
4. Python equality accepts integer `3` and float `3.0` as identical, violating type-sensitive optional-result consistency.

**Preserved dissent:** Astra’s conditional approval remains recorded. Its fixed, authentic, bounded-producer assumption meaningfully limits reachability: these tests do not demonstrate that the pinned normal producer emits malformed rows or oversized errors, or that authentic restoration accepts the synthetic archives. Sol’s results establish consumer counterexamples, not a live producer failure or receipt forgery. Nevertheless, the packet explicitly requires malformed-input handling, bounded parsing, unique correlation and preserved finalization. Conditional producer assumptions cannot waive those checks. This decision is requirements-based, not a vote.

**Sole allowed revision boundary:** Consume the composition dossier’s one evidence-driven revision to repair the diagnostic consumer and its necessary failure-containment integration, with regression evidence for all four defects. Preserve the pinned v3 probe, fixed guard behavior, selector/topology, original operational predicates, resource ceilings, retention/restoration, cleanup, failure precedence and historical receipts. No budget reset, probe revision, operational workaround or unchanged launch is authorized.

Required acceptance evidence: exact revised source/package hashes; four counterexample regressions plus existing cases; bounded archive scanning with inventory correspondence; bounded malformed-input summaries that cannot prevent parent finalization; type-sensitive comparison; preservation checks; fresh paired review and separate judgment. Only an approved revision may proceed to separate fresh source/tool/runtime/resource admission and explicit owner handoff for one nominal diagnostic.

Actual execution remains **UNRUN**. D155 probe v3 remains separate with revision allowance **0**. Historical failures remain failures; their unknown causes remain unknown. No formal proof, mechanism qualification, product acceptance, Phase One acceptance or F7 credit is established.

No files were written, and no mains, guard, probe, IPC, mount, compiler, storage operation or network request ran.