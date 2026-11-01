# Bounded diagnostic contract

This revision fixes the two mandatory defects in decision
`3351c87d570880a9de5444331ab7aae0a25f256d956791f69f6e3bba080e54ab`.
It is not another initial decision or an IPC reset. V1 remains rejected and
immutable; this document claims neither native execution nor current admission.

## Complete files before interpretation

Build children keep the original hard64MiB per-file limit and direct complete
stdout/stderr files. An exact-limit file is conservatively ambiguous and fails.
Recovery retains its independent archive child file limit; its parent captures
each complete stream through the original bounded pipe reader, strictly below
256KiB, under W/control. Overflow and partial captures remain explicit failure/
evidence loss. No diagnostic bytes are silently trimmed to create a passing log.

After exit0/full capture, validation opens each regular file without following
links, validates its declared length/hash schema, reads it in at most64KiB chunks
and recomputes SHA256 across the entire captured file. Every nonempty read has at
least one byte, so the loop has a finite `limit+1` iteration bound even with short
reads. Declared counts are exact integers, never bool/float/string; hashes are
64lowercase hexadecimal characters. Missing, changed, oversized or malformed
evidence cannot pass. EOF length/fstat/hash must agree. Both streams are checked
even when one has an ordinary diagnostic-validation failure. Real I/O/resource
failure can prevent complete validation; it then fails, not succeeds.

Interpretation holds at most4096pending bytes and8192records; it stops accepting
records after an invalid record but continues hashing the remaining complete log.
Only printable ASCII and LF framing are admitted. CR, tab, NUL, escapes, DEL,
non-ASCII, excessive/incomplete records and missing final LF fail. The file itself
is never rewritten. These parser limits are additional conservative rejection
conditions, not expanded output/resource budgets. JSON policy allocation is
bounded512KiB and4096literal records per stage; functions stay<=60lines.

## Exact finite stdout progress

Build stderr is empty. Build stdout is either empty or a sequence of exact
registered records in `progress-policy.json`. No regex prefix, suffix, wildcard,
case-insensitive diagnostic match or substring exception is used. In particular,
adding warning text to an allowed line makes a different, rejected record.

The recorded stage counts are not an authority rule: the generated roster contains
49minimal,276core and63helpers records (388stage-local records). Its construction
is executable, pure and pinned in `progress_policy_source.py`:

- Fixed phase headers: Setup, Compile, Bind, Link, Build Libraries.
- Fixed-width tags `[Ada]`, `[C]`, `[Asm]` joined to exact selected source
  basenames from the342frozen input destinations. Minimal selects minimal;
  core selects GNATcoll; helpers selects the frozen Spark/xgen/Why inputs.
- Setup directory records use only the frozen GPR project identifiers
  GNATCOLL_Minimal, GNATCOLL_Core and Helpers, with explicit source/canonical
  lowercase spellings. Only object/library directory roles are registered.
- Static library records join fixed gprlib/archive/index tags to the declared
  gnatcoll_minimal/gnatcoll_core library names; helper project/main archive names
  are explicitly helpers/xtree. Helper binder/link names are xtree.bexch,
  xtree.ali and xtree.adb; the finite binder-source candidates are
  b__xtree.ads/adb and b~xtree.ads/adb. These are named candidates, not wildcards.

The two bind-source spellings and source/lowercase project spellings are explicit
finite protocol choices. There is no claim all will be emitted by the pinned
tools, or that all legitimate normal output is admitted. Unknown ordinary output
fails closed and remains available for review. A failure cannot authorize an
automatic whitelist expansion or another revision. The native output-format fit
of this new recipe is UNRUN; no optional help/version/tool invocation was used.

Historical carrier logs establish examples of fixed progress records interleaved
with warnings. They do not qualify current source or establish a complete native
format specification. Warning preservation follows from unchanged full capture
and no quiet/suppression flags; acceptance is the narrow registered output
protocol, not a claim that a general warning recognizer understands every tool.

The existing target/version stages retain their exact future commands and require
one stdout record respectively aarch64-linux-gnu or16.1.0, with empty stderr.
Both generator streams remain empty. Existing exact output/template/determinism
checks remain in force.

## Recovery and final guard receipt

Both native create/extract streams must be empty. Recovery captured-byte counters
must match each strict declared identity, then both complete files are rehashed
and validated. Nonzero native status, warning/informational output, overflow,
missing evidence or hash drift fails. No claim is made that the mocked native
tools ran; raw logs and partial archive objects remain retained on failure.

The guard final-result `best_effort_record` return is now checked. A final
write/flush/short-write/budget failure turns an otherwise zero result into125.
Existing nonzero exits remain nonzero and retain their original code. A final
receipt failure on an otherwise normal path triggers one existing bounded owned
cleanup attempt; already failed monitor paths do not receive a second attempt.
Cleanup never depends on successful logging. No extra retry, timeout, broad kill,
fallback authority receipt or cleanup deadline is introduced. Earlier terminal
observations cannot substitute for successful final result retention. A close
failure also prevents successful process termination; flush is not fsync proof.
