# Independent review — WORLDLINE operator decision package DRAFT v6 / W-1 v3

**Verdict: NOT_READY.** This is an independent, different-author passive review by actual model selection `gpt-6.1-sol`. The author is the Claude Code lead `claude-opus-5-5`; W-1 v3 was drafted by an author-role Claude subagent for that lead. I authored none of the material under review. Model selection is recorded here; it is not provider backend attestation.

The targeted factual, OD-2 and correction-status repairs are complete at text level, and the staged resource allowance specification is complete. W-1 still contains conflicting ordering, commitment, custody, recovery and setup/rollback rules. A complete coherent specification is required before forwarding this as a ready operator decision package. Concrete code, installed identities, probes, capacity, backup and acceptance evidence are expected future work; their absence alone is not the reason for NOT_READY.

No approval, exception, proof acceptance, source acceptance or Phase One acceptance is granted. Every original obligation remains OPEN. CLOSED below means only the named specification/text correction is closed; it supplies no execution or acceptance credit.

## Inputs and evidence convention

| Input | Independently computed SHA256 | Observed bytes |
|---|---|---|
| Package and byte-identical frozen copy | `106dea2c460044b0d586b0107f4060c7284f9599197feed86164e4d53b8769fc` | 56918 |
| W-1 v3 and byte-identical frozen copy | `97f39c8967ec32538474827256271e65ab8ee0347165aa971b5887608e02ed8c` | 193544 |
| W-1 v3 support/jackal.json | `6b0853230bf777c9861a0b1f71cdfdd875d315eca7ddac725aeeca2243fcc86b` | 9329 |
| Runbook Gate 0 v4.3 | `d7db4439c75e664bc20022b01bc49a68be4c7f1b8316f90a80aaf225258f7201` | 10114 |

These identities were verified before substantive content review and again during the passive inventory. All requested sealed reports were checked against their review-freeze members, sizes, modes and recorded actual-model/different-author fields: frame v5, D1 v2/v3, C-API v2/v3, D2, root-worker seam, commonV5 alpha/beta, and package v4/v5 reviews. `freeze-checks.json` records full results; `passive-unique-notices-modes.json` normalizes the older numeric mode encodings. No mismatch was observed. Hashing verifies the retained seal, not the truth of its producer's claims.

File:line references below use these absolute paths; a hyphen in the line suffix denotes a range in the report, not a claimed code execution:

| Alias | Absolute path |
|---|---|
| P | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-operator-decision-package-v1/DRAFT-v6.md |
| W1 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/proposal/ISOLATION-STORAGE-PROPOSAL-v3.md |
| G0 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/RUNBOOK-first-proof-iteration.md |
| Prior | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/package-review/gpt61-v2/REVIEW.md |
| F5 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v5/review/gpt61-v1/REVIEW.md |
| S | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v5/scratch.py |
| S6 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v6/scratch.py |
| H | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004/HANDOFF.md |
| START | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004/START-CLAUDE.txt |
| OB | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004/OBLIGATIONS-v2.json |
| Target | /home/sicarii/Documents/complete-phase1-prompt.txt |
| D1 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-native-bigint-d1-design-v3/review/gpt61-v1/REVIEW.md |
| D1D | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-native-bigint-d1-design-v3/DESIGN.md |
| D2 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1/REVIEW.md |
| S5 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source |
| PLAN | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/frame-v6-PLAN.md |
| Self | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/frame-v6-selfcheck/RESULTS.md |
| Proto | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/frame-v6w1-proto/RESULTS.md |
| Dev | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/deviations/capi-v4-author-taskstop/NOTE.md |
| Recovery | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/review-monitoring/d1-v4-review-recovery-proposal.md |
| Isolation | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/ISOLATION.md |
| Index | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/STATUS.md |
| Transcript | /home/sicarii/.claude/projects/-home-sicarii/0e157c30-4700-4604-ab0e-cc6c3b9c6c37.jsonl |

The numbered-item checkpoints were written create-only on completion and never rewritten. Late passive supplements are named separately. I used standard-library read/hash/AST operations and actual JACKAL MCP only; I did not import or execute WORLDLINE/frame code or run a compiler, prover, build, test, privileged/setup/service/vault/window/reservation action. No process or tool was interrupted. No forbidden home-root/FUSE/SIA-brain path was listed or read. Persistent memory was used only for routing and preserving evidence boundaries; all conclusions below were checked against named review inputs.

## 1. Prior-correction and W-1 gap closure

The closure authority is Prior:308-316 and the complete section-3 list at Prior:213-230. The following are current independent findings, not adoption of W1:1704-1759's author assessments.

| Prior required correction | Current closure | Quoted v6 / W-1 v3 text and remaining gap |
|---|---|---|
| W1-CUSTODY | NOT_CLOSED | “This is the last mutation of P_adm(g), ever” is a useful partition correction, but D11 seals stream inodes before D12 creates them; materialize pin/schema and channel states conflict. Baseline references and image routing remain incomplete. W1:303-343,368-371,410-412,460-469,501-520,1927-1931,1970-1973. |
| W1-SETUP | NOT_CLOSED | “A dangling symlink, any other type or a permission error is ‘present’ and refuses” is not implemented by the shown test -e/-L absence helper. “the script undoes exactly that change” is false for sequential account/group creation. Probe errnos contradict the ACL matrix; mutable directory seals and ACL restore format are unresolved. W1:1158-1166,1236-1265,1366-1371,1473-1488,1612-1616. |
| W1-RESOURCES | CLOSED | “before every materialize and every dispatch” plus setup/selftest stage budgets now cover retained inputs/messages, exports, retries, fallback, temporaries, journal effects, restore and ambient allowances. “Satisfying the inequality is not a safe-capacity argument.” Arithmetic reproduces; installed capacity and image geometry remain OPEN. W1:1501-1588; P:123-153. |
| W1-LIFETIME-ROLLBACK | NOT_CLOSED | “A record is committed exactly when its marker is committed” fixes existence-as-commit in principle. Mutable fallback bytes versus immutable digest/readback, export mode/journal-prefix joins, complete W-death scans, durability-only release hold and headerless ACL restoration still conflict. W1:741-745,1011-1057,1081-1149,1594-1616,1633-1642. |
| OD2-CONSEQUENCES | CLOSED | “with the complete class table” now carries C1–C11, OPEN build_guard, early flags/custody/examiner restoration and unchanged controls. “The full semantic obligations” carries E2 settings/hooks/key-order/failure/encoding and unbounded correspondence limits. V3-RC1 re-review remains required; no architecture is chosen. P:676-745; D1:121-135; D1D:1702-1785. |
| PKG-V5-FACTS | CLOSED | “A candidate, not shown to work”; “whole-tree du -sb difference”; “retained at 23:23:50.591Z ... file mtime of 23:22Z” correct the specified v5 attributions without lowering allowances. Independently hashed/read sources and JACKAL reproduce them. P:98-103,115-121,218-224; PLAN:88; G0:62-66; Transcript:6066-6067,9492. |
| PKG-CLOSURE-STATUS | CLOSED | “None is called closed until a sealed review says so” and “the next sealed review rules on it” correctly distinguish author claims from prior sealed statuses. W-1 v3’s CLOSED-AT-SPEC-LEVEL wording is explicitly an author claim. P:860-892; W1:1704-1759. This review supplies the independent statuses below. |

Every section-3 gap is accounted for:

| Section-3 gap | Current closure | Text, disposition and evidence |
|---|---|---|
| generation-order | NOT_CLOSED | “stream-file descriptors” in launcher-intent require existing dev/ino before D12 creates streams. M4 has only generation.json while B.3 demands materialization pins; materialize/seal-front/failure states and adoption location are incomplete. W1:303-343,368-371,410-412,1662-1674,1927-1931,1955-1973. |
| lease-and-writer-authority | NOT_CLOSED | “opened O_RDONLY” / “no byte write” lock establishment is coherent, but “may only create new records ... front/” does not specify complete W-death recovery authority; optional records-image writes conflict with the complete mutation list. W1:475-520,1050-1056,1578-1582. |
| per-entry-modes-acls | NOT_CLOSED | “never placing an ACL on a recipe object” preserves originals, but export files become 0640 after the named-user ACL while generic commits write/check 0600. Bind final ACL/mode before marker and consumer readback. W1:556-610,1081-1089,1633-1642. |
| channel-and-dumpability | NOT_CLOSED | “integrity is not sender authentication” and prctl set/readback correct important limits; “the keys each needs” and one state chain through RESERVE/RUNNING for materialize are not exact verb schemas/states. W1:684-776,1944-1973. |
| prestate-and-installation | NOT_CLOSED | Protected reviewed-byte root staging and fail-closed validation are improvements. The shown absence helper cannot distinguish ENOENT from errors, partial scripts are not all undone, and “for every setup object ... link count, size” needs mutable-field treatment. W1:1158-1166,1192-1239,1243-1288,1366-1371. |
| exposure-options | CLOSED | Option A labels excluded exposure UNKNOWN; Option B specifies private propagation, reachable read-only toolchain, FD/capability/group/uid drop, NNP, exact environment and later reviewed code/inventory. No complete inspected set or installed sufficiency claimed. W1:1396-1442; P:299-302. |
| fresh-identities-and-vault | CLOSED | Fresh role/runtime/module/manager/stdio/environment observations, real non-isolated F, original target/caps and raw outer waits are specified. “F pins and backs up only ... P_exp”; V-VAULT remains future authentic-front evidence. W1:782-877,902-929. Custody/protocol joins remain under the open gaps, not supplied by these identities. |
| denial-probes | NOT_CLOSED | “the exact syscall and absolute operands” is a recorded field, not a complete operand table. “For A1 below g the first denial is the path search” conflicts with A1’s traverse/source read access; P-ALIAS’s recipe EACCES is inconsistent. W1:620-635,1457-1488. |
| resources-and-images | CLOSED | Explicit stage allowances/full restore, monotonic inputs, payload-only image equality, physical geometry later and compatible executable/native controls satisfy this resource-specification correction. Optional-image location custody remains NOT_CLOSED under writer authority and W1-IMAGE-TREE. W1:1501-1588; P:123-153. |
| commits-and-durable-channel | NOT_CLOSED | The initial zero-filled journal is “marker committed” and later pwrite changes it; universal unchanged-record joins have no allocation/append distinction. Short writes/torn occupied slots, truncated payload consumption and finite export/freeze prefix need definitions. W1:424-428,741-745,1081-1149,1633-1642. |
| participants-and-recovery | NOT_CLOSED | “not adversaries by assumption”, unreadable sd-pam acceptance and invisible queued references do not establish complete custody/terminal scans. W-death SCAN-UNITS/REFS and W2 authority are incomplete; no CHILD_START is not no spawn. W1:148-150,201-209,995-1056. Boot-bound non-success rules are present but depend on corrected records/setup interpretation: W1:1064-1075. |
| rollback-and-evidence | NOT_CLOSED | Revoke-first and pending-sudo reconciliation are substantive repairs. “setfacl --restore= from the P21 dump” conflicts with P21’s getfacl -c; export/freeze cannot self-include its moving journal and misses later W2 terminal evidence. W1:1192-1213,1594-1629,1633-1658. |

Every original W-1 subgap is accounted for, including those still NOT_CLOSED:

| W-1 subgap | Current closure | Text and remaining obligation |
|---|---|---|
| W1-CUSTODY | NOT_CLOSED | Final custody depends on the open generation, terminal-reference and image-tree specifications. “custody ... five facts” includes baseline no-reference premises still unresolved. W1:439-469,995-1028. |
| W1-FINAL-PASS | CLOSED | “every leaf” includes excluded generated leaves and exact metadata/named-entry joins; original CLOSED specification carried. Self-check remains ENGINEERING_ONLY. W1:439-459; P:319-323; Self:58-75. |
| W1-CLOSURE | NOT_CLOSED | “fresh role identities” are specified but no coherent materialize/dispatch/seal-front/adoption and mutable setup-directory pin interpretation closes the full join. W1:782-802,1366-1371,1662-1674,1927-1931,1970-1973. |
| W1-CHANNEL | NOT_CLOSED | “the keys each needs” and the generic state sequence do not define exact verb/control/failure schemas. W1:1955-1973. |
| W1-WRITE-AUTHORITY | NOT_CLOSED | “may only create ... front/” and the only-under-runs rule need coherent W2/recovery and optional-image routing. W1:501-520,1050-1056,1578-1582. |
| W1-READ-ACCESS | CLOSED | “streamed ... verified bytes” keeps frozen 0600 originals and no writer-home ACL; original CLOSED specification carried. W1:322-339,841-877. |
| W1-READ-EXPOSURE | CLOSED | “UNKNOWN elsewhere” replaces the falsely exact exposure claim; Option B privilege/namespace/FD design is specified, concrete review later. W1:191-196,1396-1442. |
| W1-PREFLIGHT-IDENTITY | CLOSED | “real ... front invocation” and export-only authentic-front vault scope specify the previously missing complete context/read access; implementation and vault verification remain future. W1:782-877. |
| W1-SETUP-PRESTATE | NOT_CLOSED | “requires ENOENT” conflicts with the test-only absence helper; mutable directory fields and required restore input are unresolved. W1:1158-1166,1192-1213,1243-1248,1366-1371. |
| W1-SETUP-ORDER | CLOSED | Review design/code/inventory, fresh setup Gate 0, operator setup, selftests, installed review/adoption, fresh materialize/dispatch gates are ordered explicitly. “No step authorizes the next by inference.” Original CLOSED item carried. W1:1662-1676. |
| W1-SETUP-EXACTNESS | NOT_CLOSED | “the script undoes exactly that change” is not shown for partial S-A/S-B; shown templates must be logically consistent before concrete filled inventory. W1:1236-1288,1366-1371. |
| W1-IMAGE-GEOMETRY | CLOSED | “payload allowances, not image sizes” and measured usable/inode/reserved/journal geometry remain explicit future work; original CLOSED geometry-spec correction carried. Routing is a separate open issue. W1:1562-1588. |
| W1-IMAGE-COMPATIBILITY | CLOSED | “noexec” does not discard original built-executable/native controls; a compatible independently admitted frame remains necessary. Original CLOSED text item carried. W1:1562-1588; H:162-164. |
| W1-VERIFICATION-PROBES | NOT_CLOSED | “first denial ... path search” and exact recipe-link errno conflict with specified source traversal; fully concrete operands/preconditions need specification. W1:620-635,1468-1488. |
| W1-FAILURE-LEASE | NOT_CLOSED | “front-only” retains window-owner joins but full W-death scans/release records and the no-committable-intent hold conflict remain. W1:516-520,1011-1057. |
| W1-FAILURE-RECORDS | NOT_CLOSED | “committed exactly when its marker ...” does not reconcile the mutable fallback record, consumer schemas and export modes/prefix. W1:1081-1149,1633-1642. |
| W1-REBOOT-RECOVERY | NOT_CLOSED | “no ... stale credit” and old-boot non-success rules are present; immutable versus appended journal data and dynamic setup-directory identities still lack consistent recovery interpretation. W1:1064-1075,1104-1120,1366-1371. |
| W1-ROLLBACK | NOT_CLOSED | “restore ... P21 dump” requires a headed getfacl backup, while P21 uses -c; retain comparison text separately, preserve rollback captures and exact concurrent-change check. W1:1192-1213,1612-1616. |
| W1-EVIDENCE | NOT_CLOSED | “every committed record, marker ...” needs a finite sealed export prefix plus final-mode and later W2/late-error record routing. W1:1633-1658,1936-1942. |
| W1-NONCLAIMS | CLOSED | “not ... proof or acceptance” is explicit throughout and original CLOSED item carried. W1:5-18,1704-1708,1805-1819; P:7-20,844-856. |

## 2. Facts, hashes and numbers

**Relied-on scalar arithmetic reproduces.** Every successful response used here is actual JACKAL MCP `jackal_exact`, class `exact`, `formal=false`, lane `rat`, assurance `exact rational arithmetic (not yet checker-covered)`. The evaluator identity returned was `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`. No mathematical refusal or tool-layer rejection occurred in these replays. Calls were sequential, not a large concurrent batch.

The complete response non_claims, carried verbatim, are:

- `NOT formal-bounded: this lane carries no Lean-checked certificate`
- `The epistemic class above is the STRONGEST claim this result supports`
- `exact rational arithmetic (not yet checker-covered)`

No consequence_ceiling field was returned. These results are used as informational arithmetic only: no program-correctness, bounded storage, time, source/native-cost, custody or acceptance conclusion follows. `exact` is not `formal-bounded`. Complete raw MCP responses and parsed inputs are retained in the named `jackal-*.json` files and checks.json; no convenience ledger is cited as evidence.

**Observed facts independently rechecked:**

- Effective `CONTRACT_PINS` and top-level update order were reconstructed from the manifest AST without execution. The observed effective count is 169, all normalized source pins match, and the ordered required-name count is 535. The normalization text was read at S5/runtime/worldline/proof_manifest.py:420-450; manifest entries and updates are at :329,418,925-1029. Every named lead-packet replacement payload was separately enumerated and hashed, and its relative key is an effective pin. Packet membership is neither adoption nor qualification (P:385-395).
- Raw diagnostic files were hashed and their actual `warn_error` message.text entries checked. Deduplication observes 25 unique notices, including 19 spec notices on 11 declarations, with the body-level Prefix_Tail and witness categories carried at P:455-462. The first passive accessor compared the nested message dictionary with the text, yielding false matches; the create-only `passive-notice-checks.json` and `passive-unique-notices-modes.json` explicitly correct that accessor interpretation. No raw source hash failed.
- The directly named JSON AST sites match the recorded production/protected/control/build/script partitions; the embedded simulation sites and `_json.dumps` alias at S5/scripts/decisive_evaluation_test.py:264 were checked. The 193 figure is a demonstrated minimum, not exhaustive aliased/forwarded or non-JSON data flow (P:738-743; D1:127-135).
- The original frame member byte sizes, base descriptor identities, lead module and sealed review-member roster inputs were independently read/hashed. The recipe’s original mode rows support the no-ACL preservation direction; the arithmetic sum of its file-mode counts reproduces. Inputs remain observations, not guaranteed future sizes (W1:556-571,1511-1522).
- O1 is the retained whole-tree difference, not an obj-only measurement: the original single command and output are Transcript:6066-6067. Its equality to the retained named subdirectory sum also reproduces. O4's full-stamp interval and whole-second proxy reproduce; neither is recorded target spawn-to-exit time (G0:62-66, P:115-134).
- The retained rollout reading at Transcript:9492 has timestamp 23:23:50.591Z, with the listed file mtime corresponding to 23:22Z. The v6 distinction is accurate (P:98-103). No current file growth attribution or database-per-review bound is established.
- The 02:01:52Z free/reserve/failed-backup/queue observation is supported by Transcript:10554. Earlier named history lines and retained direct evidence hashes match. These are historical observations; no live host capacity or full backup/recovery was queried. P:68-89 properly separates observations from derived declines and states that they bound nothing.
- Self/Proto results and raw JSON records agree with the reported final-pass, regression, writer-side and subordinate-UID DAC observations. The reported counts are observed author records, not independent tests. The v6 working copy source hashes to `2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84`; frozen v5 to `f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86`. Neither result tests full installed W-1 custody, adoption, launch or Phase One proof. The subordinate identities are explicitly no boundary against sicarii (P:844-856; Self:58-75; Proto:54-70).

**Remaining operator-text issues:** P:304-334 explicitly labels its two-group/direct-UID-ACL account description a v2 summary, so I do not call that a false historical fact. It is nevertheless not the v3 setup offered for later approval: W1:213-225 requires three groups and W1:597-610 grants gate-group access. The current summary must make the distinction concrete. P:107-111 is a timed approximate activity snapshot; Index:168 and Dev:32 describe the C-API drafter finishing around the same time, so the coarse timestamp alone is not proof that the snapshot was false. Treat the index as a live historical observation, not a seal or acceptance. The no-interruption/TaskStop and R2 consequence omissions require the corrections below.

**Stage conclusions:** the full unchanged runbook unit allowance is `9304350902252/1397`; W-1’s materialize/dispatch allowance is `15368462701360/1397`, setup `2027732564230/1397`, and selftests `1843272351744/1397`. The W-1 addition is `4340810164`. At the retained 02:01:52Z reading the unit margin is `-8787102018540/1397`, and W-1 materialize/dispatch margin `-14851213817648/1397`. Their exact JACKAL inputs/results are in the table below. These negative historical margins justify the stated deferral at those readings; no present-stage capacity is established. No allowance can be lowered because a past run used less, and even a passing fresh inequality would not close the safe-capacity obligation (W1:1501-1558; P:123-153).

The ideal image-payload identity reproduces with exact difference zero; physical allocated/usable/inode/reserved/journal overhead is not proved equal or measured. Image ENOSPC is failure and never an accepted case or sufficient capacity. Conditional source-cost formulas and asymptotic descriptions are retained as sealed source reasoning/hypotheses; reproduced scalar examples certify only the substituted arithmetic, not universal program correspondence, native copies/allocation, or termination (P:521-546,557-559; D2; Prior:195).

### JACKAL reproduction record

Each row's status is `exact` and the non_claims above apply to every row. `parsed=` is the tool-returned expression, not a reconstructed input. Yes means the relied-on value reproduces; display rows compare the exact quotient and returned approx with the quoted coarse decimal rendering.

| Id / source | Tool returned parsed= | Tool returned exact= | Reproduces |
|---|---|---|---|
| W1:v5 frame member total; W1:1983 | `13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891` | `38434397` | Yes |
| W1:v5 frame review roster; W1:1984 | `49133+602614+68556+250916+8543` | `979762` | Yes |
| W1:base descriptors; W1:1985 | `1735+105491+1542` | `108768` | Yes |
| W1:recipe file-mode rows; W1:1986 | `617+18` | `635` | Yes |
| W1:A_idf; W1:1987 | `2*3*25492333` | `152953998` | Yes |
| W1:A_in, A_jrnl; W1:1988 | `128*2^20` | `134217728` | Yes |
| W1:A_fb, A_setuprec; W1:1989 | `16*2^20` | `16777216` | Yes |
| W1:A_tmp; W1:1990 | `256*2^20` | `268435456` | Yes |
| W1:A_selftest, MAX_FRAME; W1:1991 | `64*2^20` | `67108864` | Yes |
| W1:A_homes; W1:1992 | `1*2^20` | `1048576` | Yes |
| W1:A_install; W1:1993 | `3*38434397` | `115303191` | Yes |
| W1:A_exp, A_retry; W1:1994 | `545393048+152953998+134217728` | `832564774` | Yes |
| W1:X; W1:1995 | `2*545393048+3*152953998+3*134217728+16777216` | `1969078490` | Yes |
| W1:X check; W1:1996 | `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` | `0` | Yes |
| W1:W-1 dispatch addition; W1:1997 | `2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` | `4340810164` | Yes |
| W1:Required, dispatch; W1:1998 | `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` | `15368462701360/1397` | Yes |
| W1:addition check; W1:1999 | `15368462701360/1397-9304350902252/1397-4340810164` | `0` | Yes |
| W1:Required, setup; W1:2000 | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` | `2027732564230/1397` | Yes |
| W1:Required, selftest; W1:2001 | `2*67108864+134217728+1468268019712/1397` | `1843272351744/1397` | Yes |
| W1:historical margin, dispatch; W1:2002 | `10460753920-10000000000-15368462701360/1397` | `-14724789475120/1397` | Yes |
| W1:historical margin, setup; W1:2003 | `10460753920-10000000000-2027732564230/1397` | `-1384059337990/1397` | Yes |
| W1:historical margin, selftest; W1:2004 | `10460753920-10000000000-1843272351744/1397` | `-1199599125504/1397` | Yes |
| W1:records payload with images; W1:2005 | `545393048+1969078490` | `2514471538` | Yes |
| W1:ideal payload identity; W1:2006 | `16777216+2242440646+545393048+1969078490+16777216+2242440646+545393048+1969078490+1468268019712/1397+268435456+134217728-15368462701360/1397` | `0` | Yes |
| W1:CHUNK; W1:2007 | `4*2^20` | `4194304` | Yes |
| W1:frame headroom; W1:2008 | `67108864-4*(4194304+2)/3` | `61516456` | Yes |
| W1:fallback slots; W1:2009 | `16*2^20/(64*2^10)` | `256` | Yes |
| W1:slot size; W1:2010 | `64*2^10` | `65536` | Yes |
| W1:new groups; W1:2011 | `1+1+1` | `3` | Yes |
| W1:new users; W1:2012 | `1+1` | `2` | Yes |
| W1:last id of `sicarii`'s subordinate range; W1:2013 | `100000+65536-1` | `165535` | Yes |
| Prior:S-MARGIN; Prior:144 | `10460753920-10000000000` | `460753920` | Yes |
| Prior:S-RATE1; Prior:145 | `(11185594368-10592727040)/(20*3600+37*60+33-(18*3600+49*60+3))` | `296433664/3255` | Yes |
| Prior:S-RATE2; Prior:146 | `(10592727040-10550894592)/(21*3600+2*60+25-(20*3600+37*60+33))` | `10458112/373` | Yes |
| Prior:S-RATE3; Prior:147 | `(10550894592-10516545536)/(22*3600+6*60+53-(21*3600+2*60+25))` | `8587264/967` | Yes |
| Prior:S-RATE4; Prior:148 | `(10516545536-10460753920)/(23*3600+32*60+6-(22*3600+6*60+53))` | `55791616/5113` | Yes |
| Prior:S-RATE4-KB; Prior:149 | `55791616/5113/1000` | `6973952/639125` | Yes |
| Prior:G-OBJ; Prior:150 | `2*1121220323` | `2242440646` | Yes |
| Prior:G-RECORDS; Prior:151 | `2*3*(25492333+5582338+3198141+701976)+256*2^20+64*2^20` | `545393048` | Yes |
| Prior:G-O1-GROWTH; Prior:152 | `1129239130-8018807` | `1121220323` | Yes |
| Prior:G-DURATION; Prior:153 | `15*3600+55*60+10-(14*3600+54*60+38)` | `3632` | Yes |
| Prior:G-DURATION-FULL; Prior:154 | `15*3600+55*60+10+112498/1000000-(14*3600+54*60+38+833395/1000000)` | `3631279103/1000000` | Yes |
| Prior:G-AMBIENT-RATE; Prior:155 | `(11289907200-11188842496)/(18*3600+44*60+45-(17*3600+58*60+11))` | `50532352/1397` | Yes |
| Prior:G-AMBIENT; Prior:156 | `4*3632*2*50532352/1397` | `1468268019712/1397` | Yes |
| Prior:G-RESTORE; Prior:157 | `16777216+2*1121220323+545393048` | `2804610910` | Yes |
| Prior:G-REQUIRED; Prior:158 | `2*(16777216+2*1121220323+545393048)+1468268019712/1397` | `9304350902252/1397` | Yes |
| Prior:G-MARGIN-LATEST; Prior:159 | `10460753920-10000000000-(2*(16777216+2*1121220323+545393048)+1468268019712/1397)` | `-8660677676012/1397` | Yes |
| Prior:G-MARGIN-W1; Prior:160 | `10516545536-10000000000-(2*(16777216+2*1121220323+545393048)+1468268019712/1397)` | `-8582736788460/1397` | Yes |
| Prior:G-MARGIN-RUNBOOK; Prior:161 | `11185594368-10000000000-(2*(16777216+2*1121220323+545393048)+1468268019712/1397)` | `-7648075570156/1397` | Yes |
| Prior:W-PAYLOAD-WORK; Prior:162 | `16777216+2*1121220323` | `2259217862` | Yes |
| Prior:W-IDEAL-EQUALITY; Prior:163 | `2259217862+545393048+16777216+2242440646+545393048+1468268019712/1397-(2*(16777216+2242440646+545393048)+1468268019712/1397)` | `0` | Yes |
| Prior:R-NOTICES; Prior:165 | `19+2+4` | `25` | Yes |
| Prior:R-SPEC-NOTICES; Prior:166 | `1+2+2+2+2+2+1+2+1+2+2` | `19` | Yes |
| Prior:R-SPEC-DECLARATIONS; Prior:167 | `1+1+1+1+1+1+1+1+1+1+1` | `11` | Yes |
| Prior:R-EXP10; Prior:168 | `10+1` | `11` | Yes |
| Prior:R-EXP30; Prior:169 | `30+1` | `31` | Yes |
| Prior:N-MINIMUM-CENSUS; Prior:170 | `192+1` | `193` | Yes |
| Prior:N-DIRECT-CENSUS; Prior:171 | `122+2+10+25+3+30` | `192` | Yes |
| Prior:P-EFFECTIVE-KEYS; Prior:172 | `82+8+8+6+4+6+10+0+0+4+0+38+0+1+0+2+0` | `169` | Yes |
| Prior:C-ORDERED-PREFIX; Prior:173 | `280+11+4+5+8+31+34+46+1+115` | `535` | Yes |
| Prior:G-STREAM-FACTOR; Prior:174 | `256*2^20/1170572` | `67108864/292643` | Yes |
| Prior:G-GB; Prior:175 | `9304350902252/1397/1000000000` | `2326087725563/349250000000` | Yes |
| Prior:G-LATEST-GB; Prior:176 | `-8660677676012/1397/1000000000` | `-2165169419003/349250000000` | Yes |
| Prior:R-CHAIN10; Prior:177 | `9*2^11-10-10` | `18412` | Yes |
| Prior:R-CHAIN30; Prior:178 | `9*2^31-30-10` | `19327352792` | Yes |
| Prior:R-PACKET14-10; Prior:179 | `11*2^11-2*10-14` | `22494` | Yes |
| Prior:R-PACKET14-30; Prior:180 | `11*2^31-2*30-14` | `23622320054` | Yes |
| Prior:G-STREAM-ILLUSTRATION-DIFFERENCE; Prior:182 | `256*2^20/1170572-200` | `8580264/292643` | Yes |
| P-NEW-MARGIN; P:82 | `10370256896-10000000000` | `370256896` | Yes |
| P-NEW-RATE; P:88 | `(10460753920-10370256896)/(24*3600+2*3600+1*60+52-(23*3600+32*60+6))` | `45248512/4493` | Yes |
| P-NEW-G0-MARGIN; P:136 | `10370256896-10000000000-9304350902252/1397` | `-8787102018540/1397` | Yes |
| P-NEW-W1-MARGIN; P:147 | `10370256896-10000000000-15368462701360/1397` | `-14851213817648/1397` | Yes |
| O1-SUBDIR-SUM; P:117 | `4676666+1116543657` | `1121220323` | Yes |
| MEMORY-CAP; W1:823 | `8*2^30` | `8589934592` | Yes |
| P-W1-SUBGAP-TOTAL; P:238 | `6+14` | `20` | Yes |
| P-PRIOR-CORRECTIONS; P:17 | `5+2` | `7` | Yes |
| P-V5-CLOSED; P:17 | `9-5` | `4` | Yes |
| P-DISPLAY-RATE; P:88 | `45248512/4493/1000` | `5656064/561625` | Yes |
| P-DISPLAY-G0; P:136 | `-8787102018540/1397/1000000000` | `-439355100927/69850000000` | Yes |
| P-DISPLAY-DISPATCH; P:143 | `15368462701360/1397/1000000000` | `192105783767/17462500000` | Yes |
| P-DISPLAY-SETUP; P:144 | `2027732564230/1397/1000000000` | `202773256423/139700000000` | Yes |
| P-DISPLAY-SELFTEST; P:145 | `1843272351744/1397/1000000000` | `3600141312/2728515625` | Yes |
| P-DISPLAY-W1-MARGIN; P:147 | `-14851213817648/1397/1000000000` | `-928200863603/87312500000` | Yes |

## 3. Capability of W-1 v3 as specified

W-1 v3 offers a plausible custody architecture: protected ancestors, separate nondelegated identities, a root-owned flock-only lock, preserved recipe modes, and gate-bearing launchers with inherited no_new_privs/seccomp could support V5-B01/V5-B02 after successor implementation and installed verification. It cannot be judged capable as specified yet: generation/stream ordering, commit/export interpretation, asynchronous terminal custody and recovery, setup/probe/rollback consistency, optional-image routing, and durability/release semantics need correction without new assumptions or weaker controls; neither blocker is closed.

| Mechanism | Independent assessment | Evidence |
|---|---|---|
| gate-group/no_new_privs/seccomp anti-setid | Plausible conditional measure. Gate membership is not given to the manager/baseline; NNP alone does not prohibit minting a setid leaf, so the added native-aarch64 mode-bit filter and blocked indirect creation interfaces address that route. No executable filter, readback or installed compatibility result exists. Baseline-service assumption, unreadable references and queued descriptors still defeat the unconditional final-pass/terminal argument. | W1:213-225; W1:977-1001; W1:148-150; W1:201-209 |
| no-ACL recipe modes with export copies | Source/snapshot/review originals retain recipe/original modes and no new default ACL. Access ACLs are on new ancestors, partition roots and export copies. This repairs recipe mode contamination as a design choice, but post-ACL export mode and commitment expectations remain inconsistent or unspecified. | W1:329-339; W1:556-643; W1:1081-1089; W1:1633-1642 |
| root-owned 0440 flock-only writer.lock | The protected root-owned inode, O_RDONLY no-create/no-write open, regular/single-link identity and exclusive nonblocking flock are coherent on the stated local-lock compatible filesystem. Writers cannot rename/change the lock; installed tests remain required. This writer lock does not strengthen the original cooperating shared-window lock ceiling. | W1:475-499; W1:1270-1288; W1:1033-1036 |
| separate markers and in-generation fallback journal | Markers correctly distinguish syntactically complete raw bytes from committed primary/retry. Initial whole-journal immutable digest versus later slot writes and universal re-read joins need reconciliation, including short writes/torn occupied slots and truncated payload consumers. P-ENOSPC is labelled optional although the fallback allocation premise must be evidenced before relying on that durability claim. | W1:741-745; W1:1081-1138; W1:1487; W1:1936-1942 |
| late-launch gating | GO then committed SPAWN_OK is a useful permit chain; a live C retaining a permit is a gate holder. It does not by itself establish complete terminality from asynchronous /proc snapshots plus baseline-service assumptions and invisible queued descriptors. Missing CHILD_START is not absence of spawn; W-death full SCAN-UNITS/REFS authority and record flow are incomplete. | W1:977-1028; W1:1050-1056; W1:516-520 |
| front-only release | The reserving F retains original holder/candidate/token/flock joins and other holders cannot be released. F death explicitly holds for manual resolution and is disclosed as more conservative; original lifetime controls must validate this new role mapping. Mandatory durable release intent contradicts the explicit archival-UNKNOWN ruling, and W-death recovery is underspecified. | W1:1030-1057; W1:1122-1138; W1:1774-1785 |
| residuals and compatibility | Original narrow residuals are reproduced verbatim; no target/recipe/controls may be narrowed to make sudo/group/scope/NNP/seccomp/partition-root/toolchain/fallback hypotheses pass. Newly unreadable sd-pam and nonadversarial baseline-service assumptions are not inherited exceptions. Concrete installed evidence is properly future work but cannot repair logically conflicting text by itself. | W1:1843-1882; W1:191-209; W1:818-831; W1:636-643; W1:1774-1803 |

The useful mechanism descriptions cannot repair the following concrete conflicts by implication:

**Creation and sealed schemas.** M4 binds only generation.json; B.3 requires both generation/materialization marker fields. D11 commits launcher-intent including actual stream dev/ino; D12 creates those streams only afterwards. B.4 routes materialize through parent/gate/reserve/launch states despite M9’s MATERIALIZED/BYE path, and does not supply an exact seal-front/failure state/keyset. Installed adoption is required but its authorized protected destination/writer is not specified. These are executable-order/schema gaps, not requests to install before reviewing (W1:313-342,368-371,410-412,516-520,1662-1674,1927-1931,1955-1973; S:816-837).

**Commits and exports.** The fallback file is initially committed with a whole-file digest, then changed by slot writes; “every journaled record unchanged” has no allocation-descriptor versus append-content exception/interpretation. One pwrite can be short; a nonzero torn occupied slot must not be treated as a reusable zero slot or a valid payload, and truncated values need explicit consumer semantics. Export ACLs change their final mode relative to the generic 0600 commitment path. Exporting every marker while generating more markers needs an explicit finite source-prefix cut and later evidence routing; F's post-W terminal record through W2 occurs after the earlier export/freeze. Every raw/marker/retry/slot/late-error outcome must remain reconstructible without false success credit (W1:424-428,741-745,1081-1149,1633-1642,1936-1942).

**Complete terminal custody.** A3's benign-service premise and R7’s unreadable fd exception are not inherited accepted residuals. R9 expressly recognizes unreceived descriptors as invisible and not an accepted exception; the design must enforce quiescence or provide an equally strong reviewed complete argument, not use a snapshot as proof of no later relevant activity. GO/SPAWN_OK narrows pending launch permits, but does not cure reference queues or the recovery observer gap. F cannot perform C/O-only units/refs scans as specified after W death; W2’s narrow verb/capability/record scope has no complete replacement flow. The “C ... dies before spawn” failure row must distinguish actual refused-before-spawn evidence from missing CHILD_START (W1:148-150,201-209,995-1056,516-520).

**Setup, probes and rollback.** The shown absence helper cannot distinguish permission/stat failure from ENOENT despite claiming to do so; sequential groupadd/useradd under sh -e can leave partial state without the asserted undo. The recipe is traversable/readable by sicarii, so P-MUT/P-ALIAS cannot expect the claimed search EACCES for every recipe operand. Exact syscall/operand/precondition tables are still needed. Setup identity must distinguish pinned and intentionally changing fields of runs/tmp/home directories across generations and reboot. P21’s getfacl -n -c -p comparison output omits the file header required for --restore; preserve a separate full headed restore dump and detect concurrent changes. This was checked against the installed read-only getfacl/setfacl manuals, not by running either tool (W1:1158-1166,1192-1213,1236-1288,1366-1371,1473-1488,1612-1616; /usr/share/man/man1/getfacl.1.gz decompressed lines 111-112; /usr/share/man/man1/setfacl.1.gz decompressed lines 110-114).

**Optional image location.** W1:501-514 categorically confines writer mutations to runs/g, while W1:1578-1582 places records in a second records/g mount. Specify the protected intended run tree, anchors, generation/attempt/marker/export routing and missing-mount identity checks without granting new outside-tree effects. Payload geometry arithmetic alone supplies none of that custody (W1:247-274,501-514,1578-1582,1633-1642).

## 4. Criteria, ineligibility and authority

Verbatim original target and V5-B01/B02 are carried, with complete narrow residual blocks byte-equal in W-1 Appendix A. Counts, release configuration and source-only review are not substitutes for the unchanged strict command, floor, full bodies/callers, accepted cases, controls and evidence. Evidence: P:26-45; P:187-211; P:477-499; P:544-560; W1:1821-1883; H:153-177.

Lower reserve, narrower scope/domain, changed references and warning waiver are expressly ineligible for original closure. Routine preserving pinned implementation changes need explicit reviewed deltas and repinning, not O-PINS permission solely for pinning. Reference semantics, material API/ABI/owner policy, custody/deployment and privileged/publication actions remain reserved. Evidence: P:34-45; P:164-174; P:364-377; P:397-447; P:485-499; P:548-559; P:588-619.

No-interruption and no alternate-tool guard bypass rules are not explicitly carried in the package. The package records the D1 reviewer untouched and the Bash deviation but omits the named TaskStop record. Repair disclosure and prohibition; recovery is neither automatic nor authorized by this review. Evidence: P:822-840; Dev:5-30; Dev:46-59; Transcript:9006.

The required committable release intent creates a durability-only hold despite the express no-release-effect/no-new-gate ruling. Fix the text without losing authentic terminal-ownership/UNKNOWN participant protection. The unreadable sd-pam exception and nonadversarial-baseline premise are new residual/assumption issues, not inherited accepted exceptions. Evidence: W1:1030-1041; W1:1122-1138; W1:148-150; W1:201-209.

The target command, protected floor, sole original worldline-c_api boundary, full ordered roster, required bodies/callers/flow/RTE/termination/native semantics/cost, complete ordinary roster and additive/lifetime/fault controls remain H:153-177's requirements. Zero unproved/justified/pragma Assume and resolved strict warnings remain completion conditions. This review authorizes no narrower formal/ordinary frame, changed actor fixture, native refusal cap, suppression or new trusted assumption. Original no-late-collector and narrow path/bootstrap/window-inode/timestamp ceilings remain ceilings, not proofs of stronger guarantees (F5:84-123; W1:1843-1882).

## 5. Choices, consequences and status tables

| Item / timing | Decision offered | Consequences, evidence and authority | Evidence |
|---|---|---|---|
| S-1 — NOW | Repair backup; human-owned non-task reclamation; consider reviewed preserving enforced limits; hold new engineering work; default defer proof runs. | Reserve unchanged; candidate recovery comparison before offload/removal; no current stage established; crossing the inequality alone is not capacity proof. Holding work must not silently interrupt ongoing tools. Lower reserve is explicitly ineligible. | P:64-176 |
| F-1 — OPTIONAL IN-PRINCIPLE NOW; PRIVILEGED SETUP LATER | Dedicated accounts acceptable in principle, or decline and continue design search; later choose concrete setup and exposure option after design/code/inventory/Gate 0. | No optional preference approves accounts, sudo, ACLs, mounts, code, adoption or dispatch. Installed verification and actual GPT-6.1 review remain required. Current role/ACL summary must agree with v3; criterion narrowing is ineligible. | P:218-225; P:229-377 |
| R-1/R-2 — LATER | Lead gathers P1-P3 under existing gates; human assesses demonstrated toolchain classification; references/assertion designs require concrete independently reviewed preserving evidence. | Strict command, all checked Posts/bodies/invariants/callers, warnings, original cases and cost obligations remain. Changing references or waiving warnings does not close original target; release assertions cannot be suppressed. | P:471-501; P:505-561 |
| C-1/C-2/C-3 — CONCRETE PACKET / DEPLOYMENT LATER; C-3 INFORMATION | Reviewed component-local transport route versus ineligible export reduction/no-mirror; reprovision loaded reviewed library identity or hold. | Complete component/source/link/symbol/profile/layout/positive/refusal evidence and exact mirror required. Sole boundary does not authorize excluded semantic bodies. Representation warnings remain strict obligations and changed ABI is reserved. | P:567-630 |
| N-1/OD-1 — LATER | Complete library/runtime/API architecture after concrete verified evidence; no choice/recommendation selected. | Preserving body route leaves checked references/cost/native obligations; owned model has no new axioms and all users reproved; separate bignum changes callers/types; runtime rebuilding is full layout/length/vector/multiplication/division/copy/cost plus loaded identity. Ghost retirement incompatible; additive API leaves originals executable/open. | P:657-674 |
| N-2/OD-2 — AFTER V3-RC1 CORRECTION AND SEALED RE-REVIEW | Interpreter-wide E1 or semantically equivalent scoped E2 codec; configuration remains proposal, costs uncapped. | Complete corrected C1-C11 classes, unresolved build_guard, early setting, examiner default restoration, unchanged payloads/original controls, protected reprovisioning, min census/aliases/non-JSON audit, absolute magnitude and lexical bounds, original key sort/failure/hooks/escaping/numeric/floating/NaN/recursion/validate-first behavior and unbounded correspondence are now carried. No cap/catch-and-refuse/per-call toggle allowed. | P:676-745; D1D:1702-1785; D1:121-135 |
| RW-1 / P-1 / N-3 — RW-1 LATER; OTHERS INFORMATION | Root-worker/material policy/privilege/fault/quota items after reviewed v2 designs; preserving pinned implementation and checked-cost preparation remain routine authorized engineering. | No root/lab/production/merge/release or actor authority granted; native checked costs stay OPEN. Every required independent review actual GPT-6.1 with different author. | P:431-447; P:747-817 |
| D1-v4 recovery — SEPARATE EXPLICIT HUMAN DECISION | R0 untouched; R1 preserved codex termination and same-thread resume; R2 preserved runner AND codex termination followed by new review. | No action performed. Incomplete old records earn no closure credit; deliberate termination is not a transport failure. Package summary must name the R2 termination and preserve no-interruption standing rule. | P:834-840; Recovery:44-65 |

Recommendations are explicitly marked lead recommendations and separated from observations/derived arithmetic; OD-1/OD-2 select no route. S-1 is the immediate choice, F-1’s account preference is optional now, and substantive privileged setup or architecture/adoption decisions remain later. P:860-892 accurately reports the prior sealed closures and leaves new author corrections awaiting review. W1:1704-1759 distinguishes author specification claims from independent closure. Nothing in either table closes an original obligation on the author’s word. The required current-summary/supervision repairs below remain necessary before this package is ready.

## 6. Paths that could weaken the target without a plain decision consequence

**New assumptions/residuals silently treated as original acceptance.** The package's blanket preservation/ineligibility clauses are good, but accepting nonadversarial target-account services or the unreadable sd-pam exception would add a premise to the custody/terminal argument. Unreceived references cannot be declared harmless merely because scans do not see them. No in-principle account choice can bless these gaps. Correction: W1-TERMINAL-CUSTODY. Evidence: P:26-45; W1:148-150; W1:201-209; W1:1017-1028; W1:1843-1882.

**False producer/durable/terminal credit.** A valid marker, parseable participant record, author self-check, returned zero, copied export, vault pin or old source qualification cannot substitute for complete authentic joins and evidence. The commit/export/fallback contradictions and W-death scan gap must be repaired; missing CHILD_START does not establish never spawned. Correction: W1-COMMIT-JOURNAL-EXPORT; W1-TERMINAL-CUSTODY. Evidence: P:7-20; P:844-856; W1:741-745; W1:1050-1056; W1:1081-1149; W1:1633-1658.

**Durability hold becomes added gate.** The committed release-intent prerequisite cannot override the supplied ruling that failed durability alone withholds success but not release. Original participant uncertainty holds are retained. Correction: W1-DURABILITY-RELEASE. Evidence: W1:1030-1041; W1:1122-1138.

**Hybrid old/new setup or outside-tree image authority.** Applying the historical UID ACL/two-group summary to the new gate-group design can erode its actual credential boundary. Optional records mounted outside the categorical allowed writer tree must be explicitly integrated into the intended protected run tree, without treating a storage choice as permission for new outside-tree writes. Correction: PKG-V6-OPERATOR-TEXT; W1-IMAGE-TREE. Evidence: P:304-334; W1:213-225; W1:247-274; W1:501-514; W1:1578-1582.

**Compatibility failure converted to lost accepted cases or skipped controls.** If allowlisted GNAT/original control work needs HOME writes, output-root removal, the filtered interfaces, or a different noexec geometry, redesign W-1 rather than reject the case, suppress checked code or shrink the roster. D1/C-API v4 author claims and INCOMPLETE reviews earn no acceptance. Startup/class/codec corrections remain future proof obligations, not operator waivers. Correction: Original obligations remain OPEN; no lowering authorized. Evidence: P:299-302; P:544-560; P:577-579; P:653-655; P:676-745; W1:636-643; W1:818-831; W1:1562-1588.

**Operator hold/recovery interpreted as tool interruption clearance.** The standing no-interruption/no alternate-tool bypass restrictions need explicit carriage; current package choices grant no action. Recovery, deliberate termination and any separately authorized privilege remain concrete human decisions with retained INCOMPLETE evidence. Correction: PKG-SUPERVISION-RECORD; PKG-V6-OPERATOR-TEXT. Evidence: P:171-172; P:822-840; Recovery:44-65; Dev:22-30.

The fixed-target clauses themselves grant no weakening. Their supporting specification must be repaired so an optional account/storage choice cannot silently introduce the new assumption, skipped join, broadened writer location or durability-only hold identified here. All compatibility failures require preserving redesign, not a new rejection of an original successful case or an omitted control.

## Required corrections before a READY review

**W1-GENERATION-PROTOCOL (item 3).** Make create-only ordering, verb-specific exact schemas and state transitions executable as one coherent specification: open and bind stream inodes before sealing launcher-intent; distinguish materialize versus dispatch generation_pins; define materialize, seal-front and failure channel states/keysets; specify the authorized destination and writer for the fresh installed-frame adoption record. Do not relax any original admission join.

Evidence: W1:303-343; W1:368-371; W1:410-412; W1:516-520; W1:1662-1674; W1:1927-1931; W1:1955-1973; S:816-837.

**W1-COMMIT-JOURNAL-EXPORT (item 3).** Separate the immutable fallback allocation descriptor from the append-only slot content; specify short-write/torn-slot interpretation and all commit consumers. Apply and read back export ACLs before recording final export mode/digest expectations. Define a finite journal prefix for export/freeze, export the necessary markers and the later W2 terminal evidence, and preserve raw failed-record interpretation without success credit.

Evidence: W1:424-428; W1:741-745; W1:1081-1120; W1:1633-1642; W1:1936-1942.

**W1-TERMINAL-CUSTODY (item 3).** Close, rather than assume away, baseline-service references and descriptor queues before asserting final-pass custody or known-terminal ownership. Unreadable relevant references remain UNKNOWN; specify enforced quiescence or an equally strong reviewed argument for asynchronous manager/bus activity. Make the W-death recovery path obtain complete units/refs scans within a permitted W2/observer authority, and do not infer nothing-started from missing child-start evidence.

Evidence: W1:148-150; W1:201-209; W1:460-469; W1:516-520; W1:995-1041; W1:1050-1056.

**W1-DURABILITY-RELEASE (item 4).** Reconcile the mandatory committed release-intent/no-committable-intent hold with the explicit failed-durability ruling. Archival UNKNOWN must withhold success and preserve uncertainty, while authentic independently established known-terminal ownership governs release; no new window hold or approval gate solely from failed durability. Keep all participant UNKNOWN holds and original holder/candidate/token checks.

Evidence: W1:1030-1041; W1:1122-1138; Prior:230.

**W1-SETUP-PROBES-ROLLBACK (item 3).** Use absence checks that distinguish ENOENT from errors, explicit probe operand/precondition tables with errno compatible with the ACL matrix, and accurate partial-setup handling. Preserve a full getfacl restore dump with file headers, not only the -c comparison text. Define pinned versus intentionally mutable fields of setup-directory identities for later invokes/reboot. Keep concrete inventory and installed evidence deferred, but repair these logical template conflicts now.

Evidence: W1:620-635; W1:1158-1166; W1:1236-1239; W1:1243-1288; W1:1366-1371; W1:1473-1488; W1:1612-1616.

**W1-IMAGE-TREE (item 3).** Make the optional-image record tree part of an explicitly protected intended run tree without extending original outside-tree authority. Specify its anchors, generation/attempt/marker/export routing and missing-mount checks consistently with the immutable partitions and complete writer mutation list. The current second records mount conflicts with the categorical only-under-runs rule.

Evidence: W1:247-274; W1:501-514; W1:1578-1582; W1:1633-1642.

**PKG-V6-OPERATOR-TEXT (item 5).** Update or unmistakably label the historical v2 summary: the current proposal requires two users and three groups, and Option A grants home traversal to wlscratch-gate rather than directly to wlscratch-run. State the current gate-bearing and no-ACL recipe consequences as the concrete route now offered for optional preparatory choice. Make the recovery summary explicitly disclose that R2 first terminates both the runner and codex, preserves the INCOMPLETE review, and starts a fresh actual GPT-6.1 review only after an explicit human decision; refresh/qualify the timed C-API drafting snapshot.

Evidence: P:304-334; P:107-111; P:839-840; W1:213-225; W1:597-610; Recovery:44-53; Index:168-183.

**PKG-SUPERVISION-RECORD (item 4).** Carry the standing prohibition on interrupting any ongoing tools, and the explicit isolation rule forbidding alternate-tool bypass after a guard refusal. Disclose the C-API v4 drafting agent's TaskStop and the lead's two historical TaskStops, with the source-record distinctions about which predated the first no-interruption ruling; do not imply those records authorize repeats or change the untouched D1 reviewer. Bind the existing recovery proposal to a separate explicit human decision without inventing a new routine-engineering gate.

Evidence: P:822-840; Dev:5-30; Dev:47-59; Transcript:9006; Isolation:92-113.

These corrections refine the remaining prior W1-CUSTODY, W1-SETUP and W1-LIFETIME-ROLLBACK targets and identify the new package/supervision conflicts. Re-review exact changed bytes by actual different-author gpt-6.1-sol; preserve prior drafts, records, checkpoints and sealed outcomes. Routine preserving corrections need no new operator permission solely for pinning. Concrete privileged setup, real recovery interruption or reserved semantic/API/policy/deployment choices retain their existing operator boundary.

## Original obligations and review limits

The original OBLIGATIONS-v2.json was read and hashed; all 219 observed entries have status OPEN. review.json retains each original id, target and dependencies with OPEN status and no closure credit. V5-B01, V5-B02, Gate 0 capacity, backup/restoration, full formal/ordinary/native/custody/cost/caller/fault/hosted/deployment and Phase One obligations remain OPEN. No source-only endorsement, author self-check, exact arithmetic, future inventory, timed index or incomplete reviewer earns acceptance.

All final files are create-only, mode 0600 and fsynced. review-freeze.json is written last and seals exactly REVIEW.md, review.json and checks.json. The hashes of these final artifacts are recorded in the freeze and final response.
