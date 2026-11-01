**Append-only correction:** the original framing allowance was understated. Preserve that report and attach this correction.

Define **32,768 as the maximum descendant entries, excluding one archive-root directory header**. For uncompressed USTAR with 512-byte blocks and 10,240-byte records, reserve:

```text
32768 × (512-byte header + 511-byte maximum payload padding)
+ 512-byte root header
+ 1024-byte two-block end marker
+ 10239-byte maximum final record padding
= 33,533,439 bytes
```

The original **33,531,904-byte** allowance omitted explicit root/end accounting and is **1,535 bytes too small** under this conservative convention. Merely including root within the 32,768 count would not fix the original end/padding accounting.

Use **33,533,439 bytes per archive/restore framing allowance**, increasing the previously proposed combined allowance by **3,070 bytes**. This remains a conservative, **UNMEASURED** bound conditional on strict USTAR, representable paths, no extensions/compression, and the stated record size. Actual native-tool format and restore behavior remain unqualified.

No writes, builds or archive executions occurred. This correction supplies neither launch approval nor a review-budget reset.