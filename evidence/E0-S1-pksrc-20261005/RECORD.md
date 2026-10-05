# E0 step S-1 (P-KSRC): running kernel ↔ package binding — PARTIAL OBSERVATION, not a discharge

**Who/when.** Lead (claude-opus-4-8), 2026-10-05 ~21:38Z. This is a lead-executable E0 step (unprivileged, read-only,
non-mutating, no prover). It is NOT acceptance and NOT an established premise; E0 evidence is subject to the
premise-discharge independent review (W-1 §13.2 / W1-V9-PREMISE-ORDER) before O-1.

**Observations** (raw in `S1-pksrc-observations.txt`, sha256 `34128fb4…`):
- Running kernel `uname -r` = **7.2.6-1-aarch64-ARCH**; `/proc/version` build Mon Sep 14 19:31:34 UTC 2026, gcc 16.1.1.
- Installed package `linux-aarch64` **Version 7.2.6-1**, Architecture aarch64, **Validated By: Signature**, Build Date
  Mon 14 Sep 2026.
- Running-kernel version == package version. ✓
- `.config` premise pins match the design's assumptions: CONFIG_SECCOMP_FILTER=y, CONFIG_USER_NS=y, CONFIG_IO_URING=y,
  CONFIG_AIO=y, CONFIG_USERFAULTFD **not set**, CONFIG_BPF_LSM **not set**.

**Honest gap — why this is PARTIAL, not a discharge.**
- `pacman -Qkk linux-aarch64` reports **5194 of 5975 files altered**, as "Modification time mismatch." mtime mismatch is
  a benign class (install/extraction re-stamps mtimes) and `-Qkk` without the package file checks only size/mtime/mode
  from the local DB — it does NOT verify file content.
- So P-KSRC (the installed source and the RUNNING kernel image are the package's bytes) is **not** established by this
  step. What remains for a full S-1 discharge: (a) a content-level verification of the installed kernel tree against the
  signed package file (`pacman -Qkk <pkgfile>` or sha256 against the package payload); (b) binding the RUNNING image's
  build-id to the on-disk image; (c) confirming the Arch Linux ARM PKGBUILD commit and checksums; then (d) the
  independent E0-discharge review.

**Disposition.** P-KSRC stays NAMED_UNESTABLISHED. This record is the first E0 evidence, honestly partial. It does not
move any W-1 obligation to established; it is offered to the premise-discharge review as a starting observation.
