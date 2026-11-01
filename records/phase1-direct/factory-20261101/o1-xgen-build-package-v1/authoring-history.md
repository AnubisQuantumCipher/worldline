# Preparation history

This is initial source preparation, not independent review or an IPC revision.

- Early unexecuted recovery draft placed full-sized recovery streams in the archive budget class; author feedback identified that mismatch. Before any test or operational execution, logs moved to W/control with four strict256KiB captures. The archive budget contains only live.tar. The retained before-review source snapshot is after that correction; no claim is made that it preserves the earlier unexecuted draft byte-for-byte.
- Registration framing estimate8390656 is retained as historical input; an append-only package correction counts the root header/end blocks/final record padding (8392191), inside unchanged16MiB allowance.
- Attempt01:49tests, one fixture failure. A mocked PID was not JSON serializable, so the real guard receipt code failed closed and returned125. The exact five first-run sources and all output remain in attempt01-*.txt/test-attempt-01.*. Fixture changed to a numeric PID.
- Attempt02:52tests pass. Read-only01:28tests pass. Attempt03:56tests pass. No execution-time source hash was captured for these three attempts; outputs remain and they are superseded by pinned final tests.
- First pinned final:61full/33read-only pass. After adding terminal receipt ControlGroup binding, final2:62full/34read-only pass. Both pinned before/after hash receipts and complete outputs remain. No source code changed after final2.
- Native scope collection distinction was requested by root based on its separate read-only historical observation. This author did not run systemctl or claim that observation as a new diagnostic qualification.
- No compiler, generator, proof, operational main, mount, lock, service, native archive or network execution occurred. No acquisition/product/inherited helper source was edited; no artifact was retired.
