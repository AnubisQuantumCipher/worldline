# Canonical effect material: fixed-interface conflict

Source-only assessment; no patch, build, proof or runtime was run. The exact current/baseline bytes, source commands, caller locations and limitations are in `inventory.json`. Source hashes are MEASURED; the semantic conclusions below are UNVERIFIED static analysis pending actual GPT-6.1 review.

## Result

No safe repair meeting the entire fixed conjunction was identified. The original positive fixtures require historical effect acceptance while supplying empty `Effect_Material`. The existing public native relations require complete material for precisely those decisions. These fixture/spec/body bytes are unchanged from original `a1bda52`; the conflict was not introduced by the current engineering changes.

A separately proved structural helper is compatible with the guarantee only if the existing public `Chain_Effect`, `Reference` and `Decide` still require `Operation_Result_Relations.Matches`. That extraction cannot make the unchanged positive fixtures pass. Making the existing public entrypoints structural and adding an authoritative wrapper would change their existing complete-value semantics and move the proof boundary. Retaining the spelling `Post => Decide'Result = Reference(...)` while weakening the executable Reference does not preserve its original meaning.

## Decisive source chain

- `canonical-exchange-tests/canonical_exchange_controls.adb:31` sets empty material. Its local helper calls `Canonical_Exchange.Decide` at line 84. Historical settlement at line 117 and replay at line 119 expect success. `canonical_exchange.adb:36` and `:39` call the complete authority decision for those outcomes.
- `canonical-owner-completion-tests/canonical_owner_completion_controls.adb:34` sets empty material. Its helper at line 91 calls `Canonical_Owner_Completion.Decide`; line 126 expects `Resolve_Effect`. The effect branch in `canonical_owner_completion.adb:35` requires `A.Chain_Effect`.
- `operation_authority.adb:76` unconditionally conjoins `Operation_Result_Relations.Matches`. The latter's public postcondition and body require capture, result, and every original payload relation. `Capture_Source_Reference` rejects invalid material at `operation_result_relations.adb:376`; empty spans fail the archive decoder, whose terminal header rejects `Sequence.Length < 2` at `archive_envelope.adb:161`. `Operation_Archive.Valid` rejects Invalid at line 528. No data is manufactured from matching digests.
- `operation_authority.ads:170` explicitly allows absence only for commands that do not claim an observed effect. The complete reference models are expressly not root-only predicates (`operation_result_relations.ads:11`).
- Baseline `prepared-wire-controls/operation_authority_controls.adb:102` expressly treats the former matching-root construction without full material as a bug-negative. Its effect positives at lines 87–91 load genuine complete material through `Operation_Effect_Fixtures`. This test is also unchanged from the baseline. A blanket weaker Chain_Effect would conflict with that existing negative.
- Baseline `prepared_operation_heads_controls.adb:82` also expects effect acceptance with the default empty material. Its later settle/replay positives share the same conflict. This is another fixed fixture obligation, not permission to waive the material checks.

The statement that the value rules confer no custody (`canonical_exchange.ads:24`) separates value interpretation from independent producer authenticity. It does not make complete value interpretation optional. The owner-completion spec likewise requires authenticated histories independently; it does not introduce a model-only execution mode.

## Caller closure relevant to a proposed split

The detailed inventory includes every qualified source occurrence found in tracked ordinary Ada source by package-alias inspection, plus the implicit child-package Matches call and internal reference dependencies. It is not a compiler reachability certificate.

| Existing route | Exact relevant source |
| --- | --- |
| Operation C export | `c_api.adb:7136` → `Native_Execution_Capture.Operation_Decide` → `native_execution_capture.adb:166` → `native_execution_views.adb:218` → `Operation_Authority.Decide` |
| Native expected model | `native_execution_views.adb:178` → `Operation_Authority.Reference`; transport postconditions bind actual to expected |
| Exchange C export | `c_api.adb:7413` → existing `Canonical_Exchange.Decide` |
| Owner completion C export | `c_api.adb:7581` → existing `Canonical_Owner_Completion.Decide` |
| Retained replay | `retained_evidence_replay.adb:534`, `:2656`, `:2694` invoke those same operation/exchange/owner native decisions |
| Actor/child execution | `resource_actor_execution.adb:16`, `:55`; `resource_child_execution.adb:13`, `:47` and its spec line 182 invoke existing authority execution decisions |
| Reservation-only uses | `canonical_operation.adb:10`; `custody_v2_prepared.ads:33`, `:35` use Reserve_Use, where missing effect is intentionally permitted |
| Independent complete material view | `operation_result_view.adb:27`, `:51` call `Operation_Result_Relations.Assess` |
| Typed controls | Both requested canonical fixtures, operation-authority controls and prepared-operation-heads controls call the same public packages; no separate pure-model selector is present |

Python production adapters marshal full material and raw rosters and call the actual native exports (`operation_authority_kernel.py:93–100`, `:124`; `canonical_exchange_kernel.py:66`; `canonical_owner_completion_kernel.py:51`). `canonical_operation_chains.py:208` retains the original material archive; `:214–219` independently asks the native OperationResultRelation to interpret it. Protected owner and full-broker routes authenticate their sources and use these native decisions. A check added solely to C API would not cover direct native replay/resource callers, and migrating all such callers would still change the existing typed API semantics.

## Candidate disposition

No production patch is proposed. A structural helper may be a valid refactor, but it is not a repair for the fixed positives. A public pure relation plus mandatory complete wrapper is an architecture change that requires an explicit changed interface contract; it is not established as a semantics-preserving implementation of the current functions. The current assignment forbids that relaxation, empty-material fallback, fixture changes and new proof boundaries.

The precise open issue is a baseline fixture/interface inconsistency: acceptance assertions demand outcomes excluded by the existing complete public reference relation for the supplied material. This analysis does not claim a universal impossibility of other architectures and does not identify the first dynamic assertion reached in the old failing binaries. Preserve the original failures and obtain actual reviewer judgment on the fixed conjunction before any proposed implementation change.
