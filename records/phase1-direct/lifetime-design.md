# D129 — lifetime bounds and termination

This is a non-final direct Phase One checkpoint. No OMP session was resumed.

The original Byte_At expression overflowed for a valid one-byte String whose lower bound is Positive Last. The parser now adds the logical offset before adding the physical lower bound. Its cursor denotes the last consumed byte, eliminating a past-the-end sentinel that cannot always be represented. Read and Element establish actual returned bounds; Equal and Complete recurse only on valid strictly smaller children. No encoded length, payload, tuple count, nesting domain or public precondition was capped.

Bytes returns the empty payload before constructing a past-the-end slice. Payload checks use subtraction after ordered bounds checks; Text allocates from validated bounds, initializes its output and proves each emission fits. Public malformed-node accessors safely reject invalid payload bounds. Valid integer encoding, UTF-32 interpretation including surrogate handling, wire tags and tuple grammar remain unchanged. These statements about preserved behavior are supported by tests; the proof establishes safety and the written bounds contracts, not a complete semantic equivalence theorem.

The four scoped-ledger array decoders now use direct iterated aggregates. Their original First, Length and element-equality postconditions remain unchanged and were proved. Runtime checks include null arrays rebased to 7..6. SQLite changes add loop variants, a leading-zero counter invariant and deliberate unused output markers; they do not change conversion formulas or precision domains. The transaction archive wrapper marks its final local write cursor as intentionally discarded; its renderer remains unchanged.

Negative evidence is retained. A first whole lifetime proof timed out without a completed report. A test visibility error was repaired. Building only the test project left the aggregate shared library stale; a debugger located the old Bytes overflow. The final test used the full aggregate build. A missing WORLDLINE_CORE_LIB prevented the resource-history group from starting; its separate rerun passed against the same library. Other completed groups were not rerun unnecessarily.

See lifetime-verification-summary.json for exact scope and raw evidence. Whole Phase One remains unaccepted: recovery-material flow findings, full strict proof/runtime, full-domain successor arithmetic, implicit Old retirement, protected/actor evidence and independent F7 acceptance are still required.
