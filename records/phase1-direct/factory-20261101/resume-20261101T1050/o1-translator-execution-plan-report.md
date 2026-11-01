**A sealed candidate plus complete successful-exec trace can support bounded execution provenance, conditionally. Exec-only tracing plus pre/post hashes alone is insufficient.** No launch is authorized or performed.

Verified read-only on carrier `aad6dadd56d794940702a54187eafb4d7800ca63`:

- Retained main source prepends GNSA tools, then installed SPARK tools, then incoming PATH.
- Both retained action bodies select `gnat2why`; `Compute_Command` also runs for signature calculation, so action creation proves no execution.
- Installed translator: SHA256 `375d0100954a66c78bace00d2229c9b96a30b6cf28845e00c4db220ba1efddb5`, 106334584 bytes, device `64768`, inode `4375042`.
- `stat`, `sha256sum`, `readelf`, and `gdb` exist. `strace`, `perf`, and `bpftrace` were absent from PATH and inspected conventional locations; local strace documentation and installed-package description were absent. No native tool operational test occurred.

Smallest prospective mechanism, using the existing launcher:

1. **Bind identity before launch.** Freeze exact unchanged D47 inputs, driver/configuration identities, candidate build receipt and hash, environment, fresh output location, and expected unit/phase coverage. Candidate must be a regular ELF at canonical `PREFIX/bin/gnat2why`. Record device/inode/mode/owner/link count/hash and every ancestor’s identity and permissions.
2. **Establish actual sealing.** The runtime prefix, parents and candidate inode must resist replacement and modification throughout execution, including writable hard-link aliases. `chmod 0555` under the same writable owner is an operational assumption, not adversarial immutability. Pre/post equality cannot detect replace-and-restore during execution.
3. **Trace from the initial driver.** Follow every descendant; capture successful and failed `execve`/`execveat`, complete argv, timestamps, process creation and exit. Add `clone`, `clone3`, `fork`, `vfork` for ancestry: exec-only records cannot establish the parent graph. Register argv/trace-size/process-count/deadline limits; truncation, ENOSPC, tracer failure, detachment, unresolved ancestry or limit exhaustion invalidates provenance.
4. **Join observed executions.** Require every translator success to resolve to the sealed candidate identity. Retain failed PATH attempts but reject any successful installed/other translator, mixed phases, unresolved relative paths or unresolved fd-based `execveat`. A successful exec proves image activation, not completed translation; join child termination and fresh phase artifacts.
5. **Establish both phases and real work.** Source distinguishes Global_Gen by its `-gnatis` construction and Translation by `-gnateO=`, but both use `-gnates=<options file>`. Retain those actual option files and establish their phase encoding before trusting a unit/phase join. Check expected unit coverage, fresh outputs and complete unchanged D47 results—including its expected static `.spark` leak failures. A zero-execution cached result fails provenance even if the driver exits successfully.
6. **Close identities afterward.** Recheck sealed prefix/candidate, driver and immutable inputs; hash complete trace and artifacts. This establishes a bounded observed-run claim, not compiler correctness, source/binary correspondence or Phase One acceptance.

Meaningful prospective negative controls:

| Control | Required rejection |
|---|---|
| Missing/non-executable candidate in a disposable control prefix | Installed fallback success cannot qualify |
| Installed translator substituted for one phase | Mixed candidate/installed phase coverage rejected |
| Cached/no-work replay | Zero or incomplete required phase executions rejected |
| Truncated trace, missing successful exec, orphan PID or unresolved `execveat` | Provenance rejected |
| Candidate hash/inode mismatch | Identity rejected |
| Genuine candidate exec followed by translator failure | Selection observed; translation/proof result remains failed |

The trace trusts the kernel, tracer and collector. Ordinary syscall trace does not directly certify executable content hash or inode; the immutable pathname-to-inode binding supplies that bridge. Dynamically loaded dependencies remain outside a translator-file-only identity claim unless separately inventoried and constrained.

**Smallest unresolved blocker:** obtain and pin an available tracer and its local documentation through a separately registered acquisition; strace is currently unavailable in inspected locations. Candidate build identity, effective sealing and option-file phase mapping also remain UNPROVEN. Then register one bounded tracer negative-control qualification before any D47 launch. Preserve 8 GiB, swap 0, post-lock 14 GiB admission, one heavy job and 10 GB reserve; all additional ceilings and deadlines require later registration.

No files were written; no generator v2 WIP or peer verdicts were reviewed.

<oai-mem-citation>
<citation_entries>
MEMORY.md:701-710|note=[carrier isolation and bounded evidence discipline]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>