# Recovery packet replay cannot reproduce fresh evaluation records (pre-existing Source20 design gap)

Observed (test_transaction.CollapseTransactionTests.test_clean_commit_exchanges_mapping_and_links_receipt, release library,
after fixes f484b29, 41e6f43, c8049f1, 875d6e6): the commit's recovery packet (11.8 MB, packet-001.bin) is refused by
Recovery_Packet.Inspect with SELECTION_CONFLICT. Instrumented replay chain (instrumented-recovery_material_replay.adb.txt):
Rebuild -> Collect -> Classify_Finalization -> Read_Result (Finalization => True) -> Owned_Matches -> Raw_Equal = False
for the second finalization row: stored wire record and the replay's re-derivation differ in exactly one byte,
report fact 12 = Status_Rederived_Fact (stored 1, re-derived 0); Report_Based = 0 in both.

Cause: the finalization writer stores `wire = evaluation_wire.record(value, declared)` = native
Evaluation_Producer.Derive over the five operands built by evaluation_producer.operands(result, declared):
  expected = encode(result['engineInvocationObservation']); acquired = encode(payload_acquisitions(result['engineRawObservations']));
  returned = encode(dict(result)); declared = encode(declared); terminal = manager-return terminalBytes
  (or finalization encode of terminalCapture), where encode = raw_json(capture(value)).
Derive's fresh path (sources present) sets Status_Rederived from the agent/wait status
(Status = 1 and status "PASS", or 2 and "FAIL"). The replay's Derive_Original instead calls
EP.Original_Projection (Project_Original), the no-source projection, which sets Status_Rederived only for
report-based rows. The two can never agree on fresh agent rows, so no fresh evaluation can be committed
through the packet relation.
