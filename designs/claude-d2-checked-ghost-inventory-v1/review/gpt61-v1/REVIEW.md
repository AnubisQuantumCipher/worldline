# Independent review: WORLDLINE Phase One D2 CHECKED-GHOST COST INVENTORY v1

**Verdict: ACCURATE_WITH_CORRECTIONS.** The central exponential replay hazard, high-order quantity/arena work, and installed-source representation cliff are supported. Corrections below cover composite costs, valid base cases, packet reachability, runtime/allocation wording, evidence locations and approval boundaries. All original Phase One obligations, including D2, remain OPEN. No acceptance is granted.

Reviewer actual model selection: gpt-6.1-sol. Different from author: true. Author under review: Claude Code lead claude-opus-5-5 (analysis subagent). The reviewer authored none of the inventory or packets under review.

Analysis: /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-d2-checked-ghost-inventory-v1/INVENTORY.md

Verified analysis sha256: e5b9984d2beadf12f35e3018aff33c23a47d93adea7bd886abe8df2db46574b6

Verified inventory.json sha256: a7b43eb71220349dcb9e07772b51f8664d9f9bb8354a3939f3825a6683b81f62

Method: passive source/document reading and hashing, JACKAL MCP arithmetic, and create-only local review artifacts. No WORLDLINE import/execution, compiler/prover/build/test/benchmark/service invocation, runtime measurement, SIA note or outside-directory filesystem write was issued.

Evidence path aliases:

- S = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source; unprefixed Ada filenames in a numbered section are under S/core unless an immediately identified packet/runtime filename is used.
- B = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/reviewed-common-proof-source-composition-v4/source.
- G = /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1; RT = /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude.
- H = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004/HANDOFF.md; original Phase One prompt = /home/sicarii/Documents/complete-phase1-prompt.txt.
- D1 = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-native-bigint-d1-design-v2/review/gpt61-v1.
- P12 = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-workflow-v1/packets/12-iterative-body-local-witnesses; P13 = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/13-iterative-prefix-tail; P14 = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/14-chain-replay-reference-lemmas. Bare P13/P14 line citations identify their sole packet body; P12 filenames distinguish its bodies.
- INVENTORY.md and inventory.json refer to the pinned analysis and data above.

Source-observed text and hashes, unverified reviewer recurrence/complexity reasoning, and JACKAL exact informational arithmetic are distinct evidence classes. Neither static hashing nor exact mathematics establishes physical native behavior, full proof, source admission, or Phase One acceptance.

## 1. Checked evaluation structure and hazard-by-hazard ruling

The checks scenario enables `-gnata` by default (`S/core/worldline_core_sources.gpr:8-19`; the Attest project has the same selection). The installed GNAT manual explicitly maps Ghost, Pre, Post, Assert, Loop_Invariant, Loop_Variant and Subprogram_Variant to Check (`G/share/info/gnat_ugn.info:9396-9436`). The inspected core has no overriding policy. These are source-semantic evaluations on normally completing, applicable paths, with short-circuit conditions and selected branches respected. A Post does not run after exceptional completion. The switch documentation supports the model; this review has no compiler-output evidence about nested-contract expansion, optimization, literal placement, or elision.

| Hazard | Independent ruling and file:line evidence |
|---|---|
| H1 | Correct exponential reference structure. The body calls Prefix_Reference at Count minus one (`worldline-chain_authority.adb:11-12`), and the normal Post evaluates another at Count minus one before Prefix_Step (`worldline-chain_authority.ads:80-86`). Post short-circuiting does not skip it when the preceding bound holds, including row-mismatch results. Replay_Reference evaluates the complete prefix in body and Post (`adb:54-55`, `ads:102-105`). Replay adds its own Post (`ads:112-114`); Wire.Decide evaluates Replay_Reference in its result-field conjuncts (`worldline-chain_authority_wire.ads:61-72`). The executable path is C wrapper → Wire.Decide → Replay (`worldline-chain_authority_c_api.adb:99`, `worldline-chain_authority_wire.adb:3-5`). Python's only observed retained-store integration definition is `runtime/worldline/store.py:1104`; passive search found no in-tree invocation. |
| H2 | Correct whole-output/arena hazard. Prefix_Total's body invokes a worker correspondence lemma and the worker, while its Post recursively calls the predecessor (`resource_ledger.adb:832-837`, `ads:138-142`). Worker and correspondence lemma assertions/Post run too (`adb:501-564`); the lemma repeats workers but introduces no second public Prefix_Total recursion. Processed_Conforms repeats earlier Prefix_Total and radix evaluations (`adb:1399-1410`), and Compute repeats that relation (`adb:1444-1447,1505-1514`). The total workspace feeds Binary (`adb:1484-1485`). **C-SLOT:** Storage_Sufficient's earlier-slot invariant (`adb:848-854`), body (`adb:862-863`) and Post (`ads:153-158`) make its independent uniform-slot term quadratic in rows, not linear. The Python-sized bounded-value family remains the inventory's dominant class. |
| H3 | Correct nested quantity structure. Power_Reference and Prefix_Reference each have a single recursive body call and nonrecursive sign Post (`resource_quantities.ads:40-56`). Radix_Power and Prefix_Value have iterative worker bodies and a single predecessor call in their public Posts (`ads:58-83`, `adb:97-208`). Those calls recursively incur worker invariants, post-loop assertions and worker Posts. Magnitude evaluates Prefix_Value in body and applicable Post; Value evaluates Magnitude in body and Post (`adb:210-226`, `ads:85-96`). Equal nonnegative Compare's inventory multiplicities reproduce in exact JACKAL arithmetic: fixed term 42, iteration term 8; top-byte Greater/ Less terms 50/42. Source: `adb:350-399`, `ads:110-117`. Reservation-transition Zero_Prefix recurses with Prefix_Value at each return and runs per column (`resource_reservation_transition.adb:484-503,609-617`), supporting its stronger successor amplification. |
| H4 | Check reaches Exact_Value, Sum, Conserved and Contained and repeats reference work in its Post (`resource_run_ledger.adb:144-210`, `ads:377-457`). Exact_Value's body has the invariant reference calls and a Value Post (`adb:19-35`, `ads:185-186`). Sum_Reference has a single recursive body call and no Post (`ads:200-209`). **C-SUM:** Sum alone has quadratic worst-case Value evaluations (`adb:54-63`); Contained can be cubic with duplicate parent identities (`adb:81-87`). Shape establishes reservation uniqueness on the successful Check path (`ads:233-235`), which makes the inventory's restricted Check-path distinction sound. Excluded rows and identity scans remain costs even when there are no included rows. |
| H5 | Worldline.Resources has the simpler single-body-recursion radix and prefix functions; Prefix_Value's Post adds radix evaluation (`worldline-resources.ads:29-46`). Can_Reserve's checked column witnesses and invariants, its Post's Fits_By_Addition, and that function's own checked body/Post all run (`adb:787-921`, `ads:78-90`; Wire Post `worldline-resource_wire.ads:11-16`). Try_Reserve calls Matching_Prefix both through Reserve_Prefix_Step and directly (`worldline-resources.adb:663,1020-1024`), supporting the quoted capacity amplification. Sum_Equals's headline assumes successful column traversal: a mismatch calls Mismatching_Sum_Column → Value_Modulus → recursive Prefix_Modulus/Prefix_Quotient (`adb:943,693-695,264-274,239-262`); a blanket full-domain class is not established by that success-path headline. |
| H6 | The per-disk and prior-disk reevaluations are present (`resource_admission.adb:237-264`), with each reference's own Post (`ads:118-129`). Admit also evaluates Capacity and its Decision_Conforms Post (`adb:270-276`, `ads:199-201`). **C-EMPTY:** an empty disk array still executes the memory-capacity relation; the disk-only formula needs that fixed term or a nonempty comparable-extents qualification. |
| H7 | Journal_Valid has per-row successor/epoch comparisons and identity uniqueness (`evaluation_pending.ads:84-101`); completion rescans earlier Same_Binding/Same_Result (`evaluation_completion.adb:15-18,32-34`); History_Valid has per-row successors and nested identities (`evaluation_history.ads:203-217`). **C-OWNER:** whole owner/retry exports are not fixed multiples of one epoch comparison. Retry_Holds, Retry_Reference and Retry_Equation call History_Valid (`worldline-owner_transitions.adb:23,50`, `ads:137`). Audit Same_Prefix calls Same_Row per row, whose body calls Same_Epoch (`worldline-owner_retry_audit.ads:38-42`, `adb:26-28`), and audit also checks History_Valid (`adb:69`). These paths reach the C exports (`worldline-c_api.adb:1015,1112-1152`). Appendix A's O(H·id) Retry_Equation classification must also be corrected. The inventory's explicitly untraced completion/finalization exports remain unverified. |
| H8 | The processed-prefix and nested quantifiers exist at the cited sites: `evaluation_completion_roster.adb:57-63`, `evaluation_raw_roster.adb:56-57,71-72`, `evaluation_finalization.adb:35-37,110-111,241-243`, `resource_run_ledger_wire.adb:7,18`, `resource_reservation_lifecycle.adb:18-25`, and the listed evaluation/owner/recovery wire loops. Their source worst-case component growth is supported; short-circuit and identity/row extents must be retained. Initialized assertions should not be treated as runtime initialization evidence; the repeated equality/Decode calls independently supply the cost. |
| H9 | The Ghost arena snapshots and per-step assignments exist (`resource_ledger.adb:1144,1203,1424,1456`; `worldline-resources.adb:973,989,1001`). Old captures are present in the cited public Posts (`worldline-resources.ads:153-155`, `evaluation_completion.ads:422`). Source recursion depth is supported. Native frame sizes, primary/secondary stack allocation, peak live heap, copy elision and catchable exhaustion are unverified; the live-heap estimate remains reasoning-only. |
| H10 | The cited C handlers map propagated exceptions to generic error codes (`worldline-chain_authority_c_api.adb:102`, `resource_run_ledger_c_api.adb:222`, `worldline-resource_ledger_c_api.adb:176,223`, `worldline-resources_c_api.adb:64`, `worldline-resource_policy_c_api.adb:182`). Process/stack failure catchability is not established. This cannot be credited as a semantic accepted refusal. |
| H11 | Prefix's normal Post and variants/invariants check bounded-size fields (`canonical_artifacts.ads:34-39`, `adb:175-177,195-197,229-230`). Tagged_Matches's checked invariants also use bounded-size fields (`adb:506-510,529-544`); its recursive calls remain executable (`adb:512-514,558-559`). The inspected checked overhead is a source-model constant factor. This is not a total parser complexity or native stack guarantee. |

All source references in this table are under S/core unless another prefix is shown. Growth language describes conditional worst-case source cost families, not measured time, a bound across every early return, or an asymptotic completion claim beyond the installed finite Bignum limit. Every hazard stays OPEN.


The retained export traces are explicit: ledger compute/headroom → L.Compute/L.Compute_Headroom (`worldline-resource_ledger_c_api.adb:162,212`); run-ledger export → W.Decide → L.Check (`resource_run_ledger_c_api.adb:219`, `resource_run_ledger_wire.adb:24-30`); resource reserve export → Resource_Wire.Can_Reserve (`worldline-resources_c_api.adb:53-58`); policy export → P.Admit (`worldline-resource_policy_c_api.adb:169`); history export → H.Select_Evidence (`worldline-evaluation_history_c_api.adb:179`); recovery V3 export → W.Decide (`worldline-recovery_authorization_v3_c_api.adb:163`). Each path's checked callee/Post work remains included. Direct exported Ada operations still need their specified Ghost/caller context; a Library_Interface declaration is not evidence of a production invocation. H8/H9 overlap these paths and the specifically named completion/finalization/lifecycle consumers. Complete tracing of other exports remains OPEN, as the inventory expressly records (`INVENTORY.md:834-835`).


## 2. Closed forms, instances, growth and installed runtime

**Ruling: the main invocation formulas and all successful exact-arithmetic instance claims reproduce; allocation wording and some composite cost terms need correction.** The mathematical recurrence arguments below are independent reviewer reasoning from source, not a machine-checked program proof. JACKAL supplies every derived numerical coefficient, residual and instance reported here.

For the chain reference, the observed body and Post give P(0)=1 and P(n)=1+2P(n-1) on normal completion (`S/core/worldline-chain_authority.adb:7-12`, `ads:80-86`). Substituting the proposed P(n)=2^(n+1)-1 satisfies that recurrence algebraically. Replay's loop checks P(c) for c from zero through the predecessor of n, and its Post pays two complete prefix trees; Wire.Decide's successful result conjunction adds three Replay_Reference calls, each paying two complete trees (`adb:87-92`, `ads:112-114`, `worldline-chain_authority_wire.ads:61-72`). Thus the independent source expression is sum[P(c), c<n]+8P(n), with sum[P(c), c<n]=2^(n+1)-2-n, giving **9*2^(n+1)-n-10**. JACKAL exact coefficient arithmetic returns 9 from parsed=1+8 and -10 from parsed=-2-8. The direct Ada Replay expression uses two complete trees, giving **3*2^(n+1)-n-4**; JACKAL returns 3 from parsed=1+2 and -4 from parsed=-2-2. The invocation growth is exponential; successful nonbase Prefix_Reference also evaluates Link in its body and Prefix_Step. This is conditional source evaluation, not observed native SHA work.

For quantity references, let p(e) count Power_Reference calls in one Power_Reference evaluation, and r(c) count those calls inside Prefix_Reference. The single-body recurrences and nonrecursive sign Posts give p(e)=e+1 and r(c)=c(c+1)/2 (`resource_quantities.ads:40-56`). A checked radix worker pays its current-index invariant sum, predecessor-index invariant sum, two final predecessor evaluations and its Post. This yields **w(e)=e²+3e+1**, including the separate base case (`adb:97-137`). The public radix Post adds its predecessor's entire checked evaluation, p(e), and p(e-1), so **RP(e)-RP(e-1)=e²+5e+2**, RP(0)=2, and **RP(e)=(e³+9e²+14e+6)/3** (`ads:58-67`). The independent coefficient residuals parsed=3/3-1, parsed=(-3+2*9)/3-5 and parsed=(1-9+14)/3-2 all return exact 0. They check the coefficient arithmetic in the finite-difference argument; they are not JACKAL symbolic identity certificates.

Let S(c)=sum[r(k)+p(k), k<c]. Its proposed closed form is (c³-c)/6+(c²+c)/2. For positive c, the prefix worker pays S(c)+S(c-1)+2r(c-1)+2p(c-1)+r(c), producing **PVW(c)=(c³+6c²+5c)/3**, with PVW(0)=0 (`adb:147-203`). The public Post adds PV(c-1)+RP(c-1)+r(c)+r(c-1)+p(c-1), giving **PV(c)-PV(c-1)=(2c³+15c²+7c)/3**, PV(0)=0, and **PV(c)=c(c+1)(c²+11c+12)/6** (`ads:69-83`). Independent JACKAL arithmetic checks the expanded coefficients (parsed=11+1 → exact 12; parsed=12+11 → exact 23); the finite-difference residuals parsed=4/6-2/3, parsed=(-6+3*(11+1))/6-15/3, parsed=(4-3*(11+1)+2*(12+11))/6-7/3, and parsed=(-1+11+1-(12+11)+12)/6 each return exact 0. Separate source-recurrence substitutions at the displayed small prefix cases also return exact 0; their complete parsed expressions are retained in the JACKAL appendix and checks.json.

| Source-model count | JACKAL status | parsed= | exact result | Reproduces |
|---|---|---|---|---|
| C chain, n=10 | exact | 9*2^11-10-10 | 18412 | yes |
| C chain, n=30 | exact | 9*2^31-30-10 | 19327352792 | yes |
| Ada Replay, n=30 | exact | 3*2^31-30-4 | 6442450910 | yes |
| PV(0) | exact | 0*(0+1)*(0^2+11*0+12)/6 | 0 | yes |
| PV(1) | exact | 1*(1+1)*(1^2+11*1+12)/6 | 8 | yes |
| PV(2) | exact | 2*(2+1)*(2^2+11*2+12)/6 | 38 | yes |
| PV(8) | exact | 8*(8+1)*(8^2+11*8+12)/6 | 1968 | yes |
| PV(32) | exact | 32*(32+1)*(32^2+11*32+12)/6 | 244288 | yes |
| PV(128) | exact | 128*(128+1)*(128^2+11*128+12)/6 | 48996608 | yes |
| PV(803) | exact | 803*(803+1)*(803^2+11*803+12)/6 | 70334477708 | yes |

Magnitude's body/Post each call Prefix_Value; Value's body/Post each call Magnitude (`adb:210-226`, `ads:85-96`). Their factors reproduce. Equal nonnegative Compare pays the fixed and per-iteration PV terms described in item 1; its PV-term instances and the inventory's remaining successful exact-arithmetic instances reproduce independently. These are evaluation counts, not the values of the quantities themselves.

The stated primitive growth classes follow in the source limb-work model: Power_Reference Θ(e²), Prefix_Reference Θ(c³), radix worker Θ(e³), public Radix_Power Θ(e⁴), prefix worker Θ(c⁴), public Prefix_Value/Magnitude/Value Θ(c⁵), and worst-case successful Compare Θ(L⁶). Multiplication by a fixed one-digit radix costs work proportional to the growing operand length, as supported by the installed nested multiplication loops (`RT/s-genbig.adb:579-615`). The extra exponent in limb work is not inferred merely by multiplying the invocation count by the maximum exponent: the sums contain growing-index evaluations that supply the corresponding lower-bound family. These complexity arguments are unverified reviewer reasoning; JACKAL exact arithmetic does not certify them. Installed finite resource failures truncate evaluations, so these are growth models for normally completed reference work, not literal completion asymptotics across arbitrarily large inputs on this runtime. Composite classes additionally require the successful-path, uniqueness and comparable-extent qualifications in item 1.

**C-UNIT:** `INVENTORY.md:114,125-129` overstates the allocation unit. Boolean comparisons have no Big_Integer result allocation (`RT/a-nbnbin.adb:106-145`), while multiplication does allocate through Big_Mul (`:502-507`). The exponent-zero PR body has no multiplication, and nonzero bodies also convert the radix (`resource_quantities.ads:40-45`). Controlled adjustment/finalization and predicates add costs (`RT/a-nbnbin.adb:604-620`, `a-nbnbin.ads:35-62`). The polynomial allocation estimate can remain a source-model estimate; the exact PR count must not be advertised as an exact count of allocations, literal conversions or machine operations.

**Representation cliff: supported conditionally on the inspected runtime implementation, not measured.** The inspected rename uses Ada.Numerics.Big_Numbers.Big_Integers (`S/core/spark-big_integers.ads:30`). Digits are base 2^32 (`RT/s-shabig.ads:46-55`), and Normalize rejects when its significant-digit count minus one exceeds Bignum_Limit=200 (`RT/s-genbig.adb:1176-1194`). Fresh exact JACKAL results are: parsed=200+1 → 201 permitted significant words; parsed=804*8 → 6432; parsed=32*201 → 6432; parsed=6432/32+1 → 202 needed words for 2^6432; parsed=803*8 → 6424; parsed=6424/32 → 803/4. Thus the power at exponent 804 exceeds this limit, whereas the exponent-803 power does not exceed this particular limit. “Fits” means the digit limit only: it establishes neither stack nor heap sufficiency.

Prefix_Value_Worker multiplies Place to the full radix power after the final digit (`resource_quantities.adb:179-181`), so even small numeric values in a valid, sufficiently long zero-padded span reach this power construction. Prefix_Reference instead reaches the predecessor exponent (`ads:51-53`). The author's differing boundary statements for those routines are therefore structurally supported. Python ledger capacities use the observed max-length-plus-one provisioning and accumulate them into the total workspace; headroom uses max-length-plus-two (`runtime/worldline/resource_ledger.py:161-172,237-247`). JACKAL exact parsed=804/2 returns 402 and parsed=804-2 returns 802. Those are conditional reachability thresholds, not assurances that every such input reaches the same line before any other failure.

Propagated exceptions are caught as -1 by chain and run-ledger C wrappers, and as 255 by ledger, resources and resource policy (`worldline-chain_authority_c_api.adb:99-102`, `resource_run_ledger_c_api.adb:219-222`, `worldline-resource_ledger_c_api.adb:176,223`, `worldline-resources_c_api.adb:64`, `worldline-resource_policy_c_api.adb:182`). The Python ledger wrapper converts its nonzero transport return to CoreUnavailable (`resource_ledger.py:180-181,245-247`). **C-LOC:** the inventory's chain call/handler line numbers and run-ledger handler line number are wrong in its own hash-matched source. The generic-mapping conclusion remains correct. Actual linked runtime identity, exception/catch behavior after physical exhaustion, native wall time and stack/heap bounds remain OPEN.

**JACKAL boundary.** Successful numerical reproductions have status **exact**, assurance “exact rational arithmetic (not yet checker-covered)”, formal=false, and these verbatim non_claims:

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

The arithmetic supports informational conclusions about the stated counts; it does not certify program correctness or native behavior. Independent jackal_poly_eq attempts were rejected with “MCP tool call requires approval, but approval policy is never”. This is an environment approval block, not a mathematical refusal. No blocked symbolic result is counted as a reproduction or replaced by a purported certificate. The algebraic recurrence derivations above are explicitly unverified reviewer reasoning. Full fresh inputs, parsed forms, statuses, non_claims and errors are retained in checks.json.
Zero numeric/arena extents also need base terms in generic composite cost expressions; a success-path assumption does not itself exclude valid empty inputs. The displayed families do not discharge those cases.


## 3. Packet deltas and base comparison

**Ruling: packet identities and the main cost changes reproduce statically. P13 changes its local polynomial classes; P12 and P14 retain their reported dominant classes. Equal-endpoint and nested-call wording needs correction.** None of these packets is executed, proved, composed or accepted by this review.

The packet bodies and metadata were read and hashed. P13's result is 5f106d5e711d14c5a7a0ac7ddc2f00136b4b5b180d63a6d0ad1868f53f5b9208; P14's is d003cd49ca418ab5b721bb241edf932aeab5e43f7394df1e1018804f93351a56. P12's two epoch copies are byte-identical at 3131f36c77e458ecbe2adc71d648ed15adf7418cd5cf1d9a961ac1b81fd0fcaa; its resources body is c16618a47dfcf7330d0846ff0f6e3ef032071551abf4d5c1cd5ca901efb86f44. The declared stack hashes match S; P14's empty stacks_on declaration is supplemented by a passive diff against S showing its reference definitions unchanged. The complete hashes and comparisons are retained in checks.json.

**P14.** The new successful-iteration assertion evaluates P(Count+1); the adjacent Link assertion adds fixed-size hashing (`P14/files/core/worldline-chain_authority.adb:165-181`). Sum[P(k), k from one through n] is therefore added to the original C success count. Independent coefficient arithmetic gives status=exact, parsed=9+2 → 11 and parsed=-10-4 → -14, yielding **11*2^(n+1)-2n-14**. At n=3, the direct added-prefix sum and the difference between closed forms both reproduce: status=exact, parsed=2^2-1+2^3-1+2^4-1 → 25 and parsed=11*2^4-2*3-14-(9*2^4-3-10) → 25. The author's totals at n=3,10,20,30 independently reproduce in the JACKAL appendix. Exponential growth remains.

For an early non-Ready return, Prefix_Settled's conditional Post evaluates its From prefix in the condition and again in the equality, plus its To prefix; the recursive body decrements To (`P14:71-86`). The preceding assertion adds another From evaluation (`P14:123-165,171-177`). Thus the displayed additional reference count, (2(n-c)+1)P(c+1)+sum[P(To), c+1<=To<=n], is supported on the stated applicable path. Fresh JACKAL exact closed-form and enumerated expressions reproduce the author's 46 at n=3,c=0. This counts Prefix_Reference invocations; extra fixed Link assertions are separate. The reference's own recursive Post remains unchanged. No claim of notice removal or proof is made.

**P13.** The original relative-power recursive tail has a nonrecursive sign Post (`S/core/resource_reservation_transition.adb:85-95`). The new loop instead evaluates absolute Prefix_Reference values and calls the existing recursive Power_Factor per reached position (`P13:103-130`), and its Post adds the full decomposition (`:95-98`). For a nonzero ordered gap m=Stop-First and S=Stop, the inventory's **Θ(m*S³+m²*S²)** source limb-work envelope is supported. The new Prefix_Decomposition retains recursion and repeats the now more expensive tail in assertions, cancellation actuals and its Post (`P13:139-143,407-438`), supporting **Θ(m²*S³)** for that regime, versus the old **Θ(m*S³)** envelope. Consequently these local classes increase, as inventory.json correctly states; a blanket “cost changes but class does not” would be wrong.

The changed tail removes its own recursion, while absolute reference and Power_Factor chains remain. The increment contributed through mismatch helpers is bounded by the displayed local maximum degree under the caller extents; the inventory's dominant normal caller classes are not reduced. The mismatch helper root is selected at a mismatch, but Addition_Mismatch evaluates tails for several quantities and calls several Magnitude_Columns (`S/core/resource_reservation_transition.adb:403-413`). “Once” cannot mean one invocation of every changed witness.

**C-PACKET-GAP:** at First=Stop, the original tail returned zero with only its sign Post, while the new tail evaluates absolute prefix references in its Post (`P13:95-98,103,133`). The new and old decomposition base also pay absolute-position Post costs; the new base additionally calls the strengthened tail (`P13:139-143,433-437`). These valid equal-endpoint cases must remain in the model. Keeping a base term gives a suitable source-model envelope for the new tail of Θ((m+1)*(S+1)³ + m²*(S+1)²) and for the new decomposition of Θ((m+1)²*(S+1)³); those expressions are unverified reviewer complexity reasoning, not JACKAL certificates. Alternatively qualify the inventory's formulas explicitly as ordered nonzero-gap classes and describe the base separately.

**P12.** The epoch and resources witness bodies replace single recursive calls with loops, keep the original Pre/Post predicates, and move the termination obligation to a loop variant (`P12/files/core/evaluation_epoch.adb:144-207`, `P12/files/core/worldline-resources.adb:9-72`). Loop invariant references replace repeated per-recursion Post references, and the resources prefix quotient adds Prefix_Step per iteration (`:58`). For an ordered nonzero gap, the inventory's standalone classes before/after are supported: epoch Power_Factor Θ(gap*H⁴), epoch Prefix_Tail Θ(gap*H⁵), resources Power_Quotient Θ(gap*H²), resources Prefix_Quotient Θ(gap*H³). These are source-cost arguments only. Their unchanged Posts retain absolute radix/prefix cost at Low=High, so a gap-only expression cannot describe every allowed input. Conditional epoch Low>High branches are separate early paths, not negative-cost cases.

**C-P12-REACH:** the resources witness is not called only once per public mismatch. Unchanged Prefix_Modulus evaluates Prefix_Quotient before each recursive descent (`S/core/worldline-resources.adb:247-250`), and Value_Modulus selects that routine for nonempty tails (`:269-274`). Mismatching_Sum_Column calls Value_Modulus on several operands (`:693-695`). P12 removes inner witness recursion but does not remove containing recursion, reference recursion, or those repeated evaluations. This also limits a success-path Sum_Equals headline; it is not a full-domain mismatch cost guarantee.

**Base versus candidate.** Passive byte comparisons confirm each file the inventory calls identical (`INVENTORY.md:811-816`). The inspected changed references retain their dominant recursive structures. **C-BASE:** the claim that the remaining diffs “consist of” the listed transformations is incomplete (`INVENTORY.md:818-822`). Default initialization removal, predicated-to-unpredicated Ghost local changes (`S/core/resource_ledger.adb:1142-1148`, `worldline-resources.adb:867-874`), extra prefix assertions (`worldline-resources.adb:648-662,721-735`), a Canonicalize Ghost slot constant (`resource_ledger.adb:1013-1038`), and a Tagged_Matches guard (`canonical_artifacts.adb:503`) are also present. The case range qualification also replaces the old Invalid_Value branch (`:474-482,576-578`). No new dominant cost class was found in those changes; that cost finding is not an equivalence, legality, proof, or admission ruling.

Every exact JACKAL result in this item carries the same formal=false and verbatim non_claims stated in item 2; complete parsed inputs are retained in the appendix and checks.json. All packet and source obligations remain OPEN.

## 4. Repair ownership, approval boundaries and forbidden routes

**Ruling: the main L/R/O distinctions and forbidden-route list are sound, with corrections to pinned-text adoption, copy narrowing, and observable failure-code changes. No repair direction is adopted or authorized here.**

A lead can prepare a body-only implementation that preserves all original predicates, domains, caller behavior and accepted cases. Replacing an existing checked assertion/invariant needs a different-author ruling establishing the original obligation is retained; it cannot mean deletion of the obligation after a proof-only argument (`INVENTORY.md:712-713,758-767`; `H:129-131,153-161`; original Phase One prompt `:32-34,64-66`). Public contract/reference/API/ABI, build selection, runtime identity and toolchain changes require the concrete operator package. The sealed D1 review likewise distinguishes body-only/internal proof work from operator-owned runtime and public packages (`D1/REVIEW.md:135-157`). Operator approval alone never supplies native or formal evidence.

**C-PINS:** the inventory correctly identifies whole-file enrollments but its L shorthand must not authorize changing pinned text. Relevant entries are actually present in CONTRACT_PINS (`S/runtime/worldline/proof_manifest.py:329-364,403`). Under the requested pinned-text boundary, adopting a concrete change to enrolled pinned text requires O-PINS operator approval plus independent review, effective pin regeneration and matching-source qualification. Implementation ownership can still be lead-only; permissions over the protected text/pin package are separate. The handoff requires reviewed deltas, recomputed effective normalized pins, preserved policy prefix and complete enrollment (`H:153-161`). The pin dictionary proves enrollment, not approval, correctness, or proof. No regeneration, pin relaxation or source mutation is performed in this review.

| Repair direction | Ruling and evidence |
|---|---|
| H1 iterative reference body, unchanged public Post | Legitimate lead preparation in principle, with proof/equivalence and applicable source/pin review. The recursive Post still traverses predecessors: source reasoning supports the proposed polynomial rather than exponential evaluation shape (`worldline-chain_authority.ads:80-86`, `adb:87-92`; `INVENTORY.md:718-720`). Proof feasibility and full-domain native costs remain unverified. A new public reference or revised Wire Post crosses the respective O/R boundary (`INVENTORY.md:721-724`). |
| H2 canonical-span assertions and workspace provisioning | L+R for a body formulation only if it preserves the whole-output value, zero padding, canonicality and frame facts currently checked (`resource_ledger.adb:1305-1340`). Canonical span alone cannot silently omit those facts. Python storage provisioning can be explored with exact sufficient-space correspondence, every ordered partial sum and accepted case preserved, and no Python authorization definition (`INVENTORY.md:727-732`; Phase One prompt `:32-34`). Public Storage_Sufficient/Processed_Conforms changes are O. |
| H3 cheaper worker invariants / reference hierarchy | Incremental checked witnesses may be prepared as L+R; reference-equivalent checked facts must remain (`resource_quantities.adb:108-116,161-175`). Unchanged public Posts still incur reference work, so the proposed lower-cost direction is not closure (`ads:58-83`). Redesigning pinned public reference text is O (`INVENTORY.md:735-738`). |
| H3 rebuilt bignum runtime | O, with a complete source/model/runtime/relink/loaded-identity and physical-resource package. Removing Normalize's limit alone neither certifies layout/length arithmetic nor removes stack/heap failure (`RT/s-shabig.ads:46-71`, `s-genbig.adb:579-580,1176-1194`; `D1/REVIEW.md:142`). The inventory correctly refers to a repaired evidence package rather than adopting this option (`INVENTORY.md:739-740`). |
| H4–H8 cached/incremental relation work | L+R in principle when the original full relations and caller obligations are preserved. Public/reference changes remain O. Sum caching must account for exclusions, uniqueness, identity lengths and whole-history work identified in item 1 (`resource_run_ledger.adb:49-89`; `INVENTORY.md:743-749`). D1's ordinary-body arithmetic direction cannot close D2 while checked references remain (`D1/REVIEW.md:121-126`). |
| H9 narrowed snapshots | **C-COPY:** arena-to-slot narrowing is not necessarily a constant factor in the copy component when extents vary (`resource_ledger.adb:1144,1203,1424,1456`). The full snapshots feed equal-prefix/written-prefix and arena-frame relations (`:1310-1314,1469-1473`). Preserving or replacing those checked facts requires the applicable R ruling; pinned/public changes retain O. Physical stack/heap and copy-elision effects stay unverified. |
| H10 distinguish infrastructure failure | **C-ABI:** internal diagnostics preserving the interface may be L+R. A changed public transport code or interpretation is an API/ABI change and requires O under the inventory's own rule (`INVENTORY.md:714-715,755-756`; `D1/REVIEW.md:157`). The current generic handlers cannot be relabelled as accepted semantic refusals (`worldline-chain_authority_c_api.adb:102`, `worldline-resource_ledger_c_api.adb:176,223`; `H:129-131`). |

The forbidden routes requested in the brief are expressly identified in `INVENTORY.md:758-767`: new Count/Length/row/arena caps or restrictive Pres; counting native exception/error/-1/255/False/CoreUnavailable outcomes as accepted refusals; a proof-only light bignum library; suppressing Ghost, Post, invariants or checks through policy/levels/Suppress; release selection as D2 closure; weakened/removed reference predicates; and Off wrappers or renamed-library escape. This is consistent with the native rule (`H:129-131`) and the full unchanged proof/caller/accepted-case target (Phase One prompt `:32-34,64-66`). Equal-endpoint, empty-roster, non-default-bound, padded and long-span cases remain required where originally admitted. An approval, finite fixture, resource-failure classification or documented limitation cannot lower that target.

These are classifications of proposed work, not reviewer approval of a specific rewrite. All engineering and acceptance obligations remain OPEN.

## 5. Evidence status, fixed guarantees and final disposition

**Verdict: ACCURATE_WITH_CORRECTIONS.** The principal checked-reference hazards, primitive recurrences, reproduced instance arithmetic and installed-source digit-limit mechanism are supported. The inventory is useful static analysis after the corrections recorded below; it supplies no proof, native or Phase One acceptance.

The inventory expressly says draft, unmeasured, unproved and nonclosing (`INVENTORY.md:3-10`). Its unresolved section correctly retains actual time/heap/stacks, optimizer behavior, deployed assertion scenario, linked/loaded runtime, production extents, untraced exports and repair provability (`:826-838`). Its JACKAL section carries exact/formal=false and the lane non_claims (`:842-849`; inventory.json jackal_common/non_claims). No timing or formal program proof is presented as obtained. The author’s asserted method is read as an artifact statement; passive text/hashes cannot attest to all actions in another session.

The candidate author-freeze, composition and source-inventory hashes match the inventory's identity claims (`INVENTORY.md:19-21`). The candidate review.json matches its review-freeze and says QUALIFIED_SOURCE_COMPOSITION, with proof_acceptance=false and phase_acceptance=false; its EXACT_NATIVE_MODEL_CHECKED_GHOST_COST entry remains OPEN. The D1 v2 review.json likewise matches its review-freeze, says NOT_ENDORSED, and retains O-GHOST and the remaining native/proof/source obligations (`D1/REVIEW.md:115-142,190`). These metadata observations are not new acceptance or verification of the actual loaded binary.

The corrections prevent stronger unsupported interpretations:

- Primitive invocation counts are source semantic counts; exact allocation counts, machine instructions, optimizer-expanded code, native completion costs and catchable physical exhaustion are not established (C-UNIT, C-LOC; `INVENTORY.md:104-107,648-684`).
- Standalone and composite growth must retain actual path/domain conditions, empty/equal-endpoint work, excluded rows, identity lengths and whole-history traversals (C-SLOT, C-SUM, C-OWNER, C-EMPTY, C-PACKET-GAP, C-P12-REACH).
- P13 changes the local witness classes; P12/P14 retain the stated dominant classes under their stated regimes. Iteration does not remove nested reference/caller recursion (`P13:95-130,407-438`; unchanged containing Prefix_Modulus at `S/core/worldline-resources.adb:239-262`).
- The base-delta list is incomplete even though the inspected dominant growth structures remain (C-BASE).
- Pin adoption, narrowed frame snapshots and public transport semantics retain their proper approval/review/evidence boundaries (C-PINS, C-COPY, C-ABI).

The source-cost argument for the digit cliff does not mean every valid long span reaches Normalize before some other failure, that shorter spans complete, or that this installed source is the actual linked runtime. A generic error code or negative Boolean cannot be credited as an accepted refusal. No larger finite cap, release-only escape, light library, waived warning, Off wrapper, missing caller, disabled checked Ghost or removed accepted case is eligible closure (`H:129-131,153-167`; Phase One prompt `:32-34,64-66,78`).

Every original obligation is retained **OPEN in this review**. review.json enumerates all observed original-register IDs and the related source/D1 open-obligation IDs, plus D1/D2 and this review's unresolved native/symbolic scope; their original targets are preserved by the referenced register and review hashes. This is a nonclosing review disposition, not an edit to the historical register or any project's status files. Required complete source qualification, strict matching-source proof, authentic faithful producer/caller coverage, original ordinary/lifetime/fault/positive controls, execution admission/custody, actual runtime/resource correspondence, independent acceptance and applicable hosted/publication/deployment work remain required (`H:153-167`; Phase One prompt `:32,64-66,78`).

For this review, only passive text reading, hashing, JACKAL MCP arithmetic and creation of the requested local review/checkpoint artifacts were performed. WORLDLINE code was never imported or executed; no compilers, provers, builds, tests, benchmarks, services or measurements were run. No SIA note or outside-directory file mutation was issued. Symbolic JACKAL operations were approval-blocked as documented in item 2; their general algebraic identities are not independently tool-certified here. The surviving recurrence reasoning is explicitly unverified, with exact informational arithmetic only.

proof_acceptance=false; native_acceptance=false; phase_acceptance=false. No acceptance is granted.

## Corrections to apply to the inventory

### C-SLOT

Claim: INVENTORY.md:278 gives the Storage_Sufficient slot term as Θ(N·S⁴).

Correction: The successful invariant checks each earlier slot again, in addition to the body and Post. The slot term is Θ(N²·S⁴) for uniform independently varying slot length S. This does not change the dominant Θ(N⁶) Python-sized, bounded-value family.

Evidence: `S/core/resource_ledger.adb:848-854`; `S/core/resource_ledger.adb:862-863`; `S/core/resource_ledger.ads:153-158`; `JACKAL R-SLOT-N3`.

### C-SUM

Claim: H4 / INVENTORY.md:693 and inventory.json hazards group direct Contained/Sum as Θ(N³·L⁵).

Correction: Sum alone performs quadratic, not cubic, worst-case Value work through its processed-prefix invariant. Cubic Value work belongs to Contained with repeated parent identities. The Check-path distinction based on Shape uniqueness is sound. Sum_Reference also scans excluded rows and identity bytes, so its cost cannot depend only on the number of included rows.

Evidence: `S/core/resource_run_ledger.adb:49-64`; `S/core/resource_run_ledger.adb:70-89`; `S/core/resource_run_ledger.ads:195-209`; `S/core/resource_run_ledger.ads:229-235`.

### C-OWNER

Claim: H7 / INVENTORY.md:617,696 summarize owner/retry exports as fixed Θ(L⁶); Appendix A:916 labels Retry_Equation O(H·id).

Correction: Individual epoch comparisons have fixed multiplicity, but retry authorization and audit traverse whole histories. Retry_Holds, Retry_Reference and Retry_Equation call History_Valid, and audit Same_Prefix calls Same_Row with Same_Epoch per row. The whole exported paths require history-dependent terms and a full trace; they are not fixed Θ(L⁶) or O(H·id).

Evidence: `S/core/worldline-owner_transitions.adb:21-38`; `S/core/worldline-owner_transitions.adb:48-50`; `S/core/worldline-owner_transitions.ads:134-151`; `S/core/worldline-owner_retry_audit.ads:38-42`; `S/core/worldline-owner_retry_audit.adb:26-28`; `S/core/worldline-owner_retry_audit.adb:61-69`; `S/core/evaluation_history.ads:203-217`; `S/core/worldline-c_api.adb:1015`; `S/core/worldline-c_api.adb:1112-1152`.

### C-EMPTY

Claim: H6 / INVENTORY.md:595 states Θ(D²·L⁵ + D·L⁶) without a nonempty-disk qualification.

Correction: Empty disk rosters still execute Check_Capacity and its checked numeric relation. Include that fixed memory-quantity cost or state explicitly that the displayed class is a nonempty, comparable-extent worst-case envelope. Similar composite Θ expressions are not equalities for every short-circuit path.

Evidence: `S/core/resource_admission.adb:233-276`; `S/core/resource_admission.adb:180-206`; `S/core/resource_admission.ads:130-151`.

### C-UNIT

Claim: INVENTORY.md:114 says every Big_Integer operation allocates its result; :125-129 describes each PR invocation as exactly one multiply/result allocation/Post literal/variant.

Correction: Comparisons return Boolean without allocating a Big_Integer result. PR invocations remain a valid source call-count unit, but the exponent-zero body has no multiply, nonzero bodies also convert 256, and predicates/controlled copies add work. Do not report the invocation count as an exact allocation or machine instruction count. The stated polynomial limb-work classes remain conditional source-model reasoning.

Evidence: `G/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/a-nbnbin.adb:106-145`; `G/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/a-nbnbin.adb:502-507`; `S/core/resource_quantities.ads:40-45`; `G/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/a-nbnbin.adb:604-620`.

### C-LOC

Claim: INVENTORY.md:372-373,673-674 cites chain C API call/handler at lines 114/117 and run-ledger handler at 221.

Correction: In the hash-matched candidate, the chain W.Decide call is line 99 and exception handler line 102. The run-ledger handler is line 222; line 221 is the normal return 0. The failure-mapping conclusion survives, but these evidence locations must be repaired.

Evidence: `S/core/worldline-chain_authority_c_api.adb:99-102`; `S/core/resource_run_ledger_c_api.adb:219-222`.

### C-PACKET-GAP

Claim: INVENTORY.md:785-788,800-803 gives gap-multiplied cost classes without an ordered nonzero-gap qualification.

Correction: Allowed zero-gap calls still evaluate Posts over absolute positions. Packet 13 Prefix_Tail gains an absolute Prefix_Reference Post even when First=Stop; Prefix_Decomposition also has absolute reference work at its base. Packet 12's unchanged Posts retain radix/prefix cost at Low=High. Use nonzero-gap qualifications or retain these base terms; do not discard equal-endpoint cases.

Evidence: `P13/files/core/resource_reservation_transition.adb:94-98`; `P13/files/core/resource_reservation_transition.adb:139-143`; `P13/files/core/resource_reservation_transition.adb:433-437`; `P12/files/core/evaluation_epoch.adb:146-154`; `P12/files/core/evaluation_epoch.adb:175-183`; `P12/files/core/worldline-resources.adb:11-13`; `P12/files/core/worldline-resources.adb:37-39`.

### C-P12-REACH

Claim: INVENTORY.md:807 / inventory.json packet 12 says the changed witnesses are reached only on mismatch lemmas, once per call.

Correction: One outer mismatch can trigger many nested witness evaluations. The unchanged Worldline.Resources Prefix_Modulus calls Prefix_Quotient at every recursive level; a Mismatching_Sum_Column invokes Value_Modulus for multiple operands. Looping the inner witness removes its own recursion, not the containing recursion or repeated calls. The advertised standalone polynomial classes remain conditional worst-case classes before and after.

Evidence: `S/core/worldline-resources.adb:239-262`; `S/core/worldline-resources.adb:269-274`; `S/core/worldline-resources.adb:693-695`; `P12/files/core/worldline-resources.adb:46-70`.

### C-BASE

Claim: INVENTORY.md:818-822 says base-to-candidate diffs consist of parenthesization, nonrecursive contradiction lemmas, and a canonical invariant/case subtype.

Correction: The textual delta description is incomplete. It also changes default initializations and predicated Ghost local types, adds column/prefix assertions, introduces a Canonicalize Ghost slot constant, and adds an array-length guard in Tagged_Matches while removing the Invalid_Value case. These inspected changes do not alter the dominant cost classes identified here, but the narrower textual description is false; semantic equivalence and source qualification remain separate obligations.

Evidence: `B/core/resource_ledger.adb:949-977`; `S/core/resource_ledger.adb:1013-1038`; `S/core/resource_ledger.adb:1142-1148`; `S/core/worldline-resources.adb:648-662`; `S/core/worldline-resources.adb:867-874`; `S/core/canonical_artifacts.adb:134-159`; `S/core/canonical_artifacts.adb:474-503`; `S/core/canonical_artifacts.adb:576-578`.

### C-PINS

Claim: INVENTORY.md:708-710 labels whole-file-pinned body changes L plus reviewed pin regeneration, while :714-715 reserves O for public spec/reference/contract/API/ABI/runtime/build changes.

Correction: Keep implementation ownership distinct from permission to change pinned text. Under this review's requested pinned-text boundary, a concrete change to enrolled pinned text must carry O-PINS operator approval as well as independent review and regenerated effective pins. Body-only implementation work can be lead-owned; that label does not authorize changing the protected pin package, weakening its keyset, or adopting a changed pinned contract/reference. This review authorizes none of those actions.

Evidence: `INVENTORY.md:708-715`; `S/runtime/worldline/proof_manifest.py:329-364`; `S/runtime/worldline/proof_manifest.py:403`; `H:153-161`; `/home/sicarii/Documents/complete-phase1-prompt.txt:34`; `user review item 4: operator approval for pinned text or public contract`.

### C-COPY

Claim: INVENTORY.md:752 labels narrower Ghost copies L and says constant-factor only.

Correction: Narrowing an arena snapshot to a changing slot can change the copy component's growth when arena and slot extents vary independently, although a dominant arithmetic class may remain. It also needs a reviewed way to preserve the original whole-arena frame relations. If existing assertions/relations are replaced, R is required; pinned-text or public-contract changes retain their O boundary. Native allocation/copy-lifetime improvement is not established statically.

Evidence: `S/core/resource_ledger.adb:1144`; `S/core/resource_ledger.adb:1203`; `S/core/resource_ledger.adb:1310-1314`; `S/core/resource_ledger.adb:1424`; `S/core/resource_ledger.adb:1456-1473`; `INVENTORY.md:712-715`.

### C-ABI

Claim: INVENTORY.md:755-756 labels failure-code differentiation L+R, ABI review, possibly O.

Correction: Internal diagnostics that preserve the public interface can be L+R. A changed public transport code, meaning, layout, or caller protocol is an API/ABI package and requires O, not discretionary 'possibly O'. All original accepted cases and native success obligations remain fixed; a clearer failure classification supplies no native acceptance.

Evidence: `INVENTORY.md:714-715`; `S/core/worldline-resource_ledger_c_api.adb:176`; `S/core/worldline-chain_authority_c_api.adb:102`; `D1/REVIEW.md:135-157`; `H:119-121,129-131`.

## Fresh JACKAL reproduction records

Every successful row below has status=exact, formal=false and the verbatim rat-lane non_claims in item 2. No row certifies program correctness, growth, compiled evaluation or native completion. All nontrivial parsed inputs are shown. The blocked requests have no mathematical status or parsed result.

| ID | status | parsed= | exact result | Author instance reproduced |
|---|---|---|---|---|
| R-CHAIN-BRANCHES | exact | `1+1` | 2 | independent arithmetic |
| R-CHAIN-POSTS | exact | `2*(1+3)` | 8 | independent arithmetic |
| R-CHAIN-N10 | exact | `9*2^11-10-10` | 18412 | independent arithmetic |
| R-CHAIN-N30 | exact | `9*2^31-30-10` | 19327352792 | independent arithmetic |
| R-PV-L1 | exact | `1*(1+1)*(1^2+11*1+12)/6` | 8 | independent arithmetic |
| R-PV-L2 | exact | `2*(2+1)*(2^2+11*2+12)/6` | 38 | independent arithmetic |
| R-VALUE-PV | exact | `2*2` | 4 | independent arithmetic |
| R-COMPARE-FIXED | exact | `3+3+8+12+16` | 42 | independent arithmetic |
| R-COMPARE-ITERATION | exact | `2*2+2*2` | 8 | independent arithmetic |
| R-COMPARE-TOP-GREATER | exact | `3+3+8+12+4+4+16` | 50 | independent arithmetic |
| R-COMPARE-TOP-LESS | exact | `3+3+8+12+4+4+8` | 42 | independent arithmetic |
| R-SLOT-N3 | exact | `3*(3-1)/2+2*3` | 9 | independent arithmetic |
| REPRO-J03 | exact | `2^1-1+2^2-1+2^3-1+2^4-1+2^5-1` | 57 | yes |
| REPRO-J04 | exact | `2^6-2-5` | 57 | yes |
| REPRO-J05 | exact | `2^1-1+2^2-1+2^3-1+8*(2^4-1)` | 131 | yes |
| REPRO-J07 | exact | `2^1-1` | 1 | yes |
| REPRO-J08 | exact | `9*2^4-3-10` | 131 | yes |
| REPRO-J09 | exact | `2^1-1+2^2-1+2^3-1+2*(2^4-1)` | 41 | yes |
| REPRO-J10 | exact | `3*2^4-3-4` | 41 | yes |
| REPRO-J11 | exact | `2^1-1+2^2-1+2^3-1+2^2-1+2^3-1+2^4-1+8*(2^4-1)` | 156 | yes |
| REPRO-J12 | exact | `11*2^4-2*3-14` | 156 | yes |
| REPRO-J13 | exact | `9*2^2-1-10` | 25 | yes |
| REPRO-J14 | exact | `9*2^11-10-10` | 18412 | yes |
| REPRO-J15 | exact | `9*2^21-20-10` | 18874338 | yes |
| REPRO-J16 | exact | `9*2^31-30-10` | 19327352792 | yes |
| REPRO-J17 | exact | `9*2^41-40-10` | 19791209299918 | yes |
| REPRO-J18 | exact | `9*2^65-64-10` | 332041393326771929014 | yes |
| REPRO-J19 | exact | `11*2^11-2*10-14` | 22494 | yes |
| REPRO-J20 | exact | `11*2^21-2*20-14` | 23068618 | yes |
| REPRO-J21 | exact | `11*2^31-2*30-14` | 23622320054 | yes |
| REPRO-J22 | exact | `3*2^31-30-4` | 6442450910 | yes |
| REPRO-J23 | exact | `2*(2^2-1)` | 6 | yes |
| REPRO-J24 | exact | `2^3-2` | 6 | yes |
| REPRO-J32 | exact | `(0^3+9*0^2+14*0+6)/3` | 2 | yes |
| REPRO-J33 | exact | `1*(1+1)*(1^2+11*1+12)/6` | 8 | yes |
| REPRO-J34 | exact | `2*(2+1)*(2^2+11*2+12)/6` | 38 | yes |
| REPRO-J35 | exact | `8*(8+1)*(8^2+11*8+12)/6` | 1968 | yes |
| REPRO-J36 | exact | `32*(32+1)*(32^2+11*32+12)/6` | 244288 | yes |
| REPRO-J37 | exact | `128*(128+1)*(128^2+11*128+12)/6` | 48996608 | yes |
| REPRO-J38 | exact | `803*(803+1)*(803^2+11*803+12)/6` | 70334477708 | yes |
| REPRO-J39 | exact | `20*(20+1)*(20^2+11*20+12)/6` | 44240 | yes |
| REPRO-J40 | exact | `100*(100+1)*(100^2+11*100+12)/6` | 18705200 | yes |
| REPRO-J41 | exact | `200*(200+1)*(200^2+11*200+12)/6` | 282820400 | yes |
| REPRO-J42 | exact | `3+3+8+12+16` | 42 | yes |
| REPRO-J43 | exact | `4*1968` | 7872 | yes |
| REPRO-J44 | exact | `4*244288` | 977152 | yes |
| REPRO-J45 | exact | `4*70334477708` | 281337910832 | yes |
| REPRO-J46 | exact | `(8*8+42)*1968` | 208608 | yes |
| REPRO-J47 | exact | `(8*32+42)*244288` | 72797824 | yes |
| REPRO-J48 | exact | `(8*803+42)*70334477708` | 454782732859928 | yes |
| REPRO-J49 | exact | `804*8` | 6432 | yes |
| REPRO-J50 | exact | `32*201` | 6432 | yes |
| REPRO-J51 | exact | `803*8` | 6424 | yes |
| REPRO-J52 | exact | `200+1` | 201 | yes |
| REPRO-J53 | exact | `804/2` | 402 | yes |
| REPRO-J54 | exact | `2*4+3*4` | 20 | yes |
| REPRO-J55 | exact | `6+8+12+4+4+16` | 50 | yes |
| REPRO-J56 | exact | `6+8+12+4+4+8` | 42 | yes |
| REPRO-J57 | exact | `3*4` | 12 | yes |
| REPRO-J58 | exact | `2*2+2*2` | 8 | yes |
| REPRO-J59 | exact | `1+2+1+2+2+3` | 11 | yes |
| REPRO-J60 | exact | `2^2+3*2+1` | 11 | yes |
| REPRO-J61 | exact | `0+1+1+2+0+1+2*1+2*2+3` | 14 | yes |
| REPRO-J62 | exact | `(2^3+6*2^2+5*2)/3` | 14 | yes |
| REPRO-J63 | exact | `(1^3+9*1^2+14*1+6)/3` | 10 | yes |
| REPRO-J64 | exact | `1^2+3*1+1+2+1+1+1` | 10 | yes |
| REPRO-J66 | exact | `2*(2+4)` | 12 | yes |
| REPRO-J67 | exact | `12*4` | 48 | yes |
| REPRO-J68 | exact | `(0^3-0)/6+(0^2+0)/2` | 0 | yes |
| REPRO-J69 | exact | `0*(0+1)*(0^2+11*0+12)/6` | 0 | yes |
| REPRO-J70 | exact | `(0+1)^2` | 1 | yes |
| REPRO-J71 | exact | `(0^3+6*0^2+5*0)/3` | 0 | yes |
| REPRO-J72 | exact | `6432/32+1` | 202 | yes |
| REPRO-J73 | exact | `6424/32` | 803/4 | yes |
| REPRO-J74 | exact | `804-2` | 802 | yes |
| REPRO-J79 | exact | `1+1` | 2 | yes |
| REPRO-J80 | exact | `2*(1+3)` | 8 | yes |
| REPRO-J81 | exact | `2*2` | 4 | yes |
| REPRO-J82 | exact | `4*4` | 16 | yes |
| REPRO-J83 | exact | `2+4` | 6 | yes |
| REPRO-J84 | exact | `(2*3+1)*(2^2-1)+2^5-2^2-3` | 46 | yes |
| REPRO-J85 | exact | `2^2-1+2*(2^2-1)+2^4-1+2*(2^2-1)+2^3-1+2*(2^2-1)+2^2-1` | 46 | yes |
| R-RP-DIFF-QUADRATIC | exact | `3/3-1` | 0 | independent arithmetic |
| R-RP-DIFF-LINEAR | exact | `(-3+2*9)/3-5` | 0 | independent arithmetic |
| R-RP-DIFF-CONSTANT | exact | `(1-9+14)/3-2` | 0 | independent arithmetic |
| R-PV-EXPANDED-CUBIC | exact | `11+1` | 12 | independent arithmetic |
| R-PV-EXPANDED-QUADRATIC | exact | `12+11` | 23 | independent arithmetic |
| R-PV-DIFF-CUBIC | exact | `4/6-2/3` | 0 | independent arithmetic |
| R-PV-DIFF-QUADRATIC | exact | `(-6+3*(11+1))/6-15/3` | 0 | independent arithmetic |
| R-PV-DIFF-LINEAR | exact | `(4-3*(11+1)+2*(12+11))/6-7/3` | 0 | independent arithmetic |
| R-PV-DIFF-CONSTANT | exact | `(-1+11+1-(12+11)+12)/6` | 0 | independent arithmetic |
| R-RP-WORKER-RECURRENCE | exact | `(2^3+9*2^2+14*2+6)/3-((1^3+9*1^2+14*1+6)/3+2^2+3*2+1+2+1+2)` | 0 | independent arithmetic |
| R-PV-RECURRENCE-L1 | exact | `1*(1+1)*(1^2+11*1+12)/6-(0+(1^3+6*1^2+5*1)/3+(0^3+9*0^2+14*0+6)/3+1*(1+1)/2+0*(0+1)/2+1)` | 0 | independent arithmetic |
| R-PV-RECURRENCE-L2 | exact | `2*(2+1)*(2^2+11*2+12)/6-(1*(1+1)*(1^2+11*1+12)/6+(2^3+6*2^2+5*2)/3+(1^3+9*1^2+14*1+6)/3+2*(2+1)/2+1*(1+1)/2+2)` | 0 | independent arithmetic |
| R-PV-RECURRENCE-L3 | exact | `3*(3+1)*(3^2+11*3+12)/6-(2*(2+1)*(2^2+11*2+12)/6+(3^3+6*3^2+5*3)/3+(2^3+9*2^2+14*2+6)/3+3*(3+1)/2+2*(2+1)/2+3)` | 0 | independent arithmetic |
| R-RP-RECURRENCE-L3 | exact | `(3^3+9*3^2+14*3+6)/3-((2^3+9*2^2+14*2+6)/3+3^2+3*3+1+3+1+3)` | 0 | independent arithmetic |
| R-CHAIN-C-COEFFICIENT | exact | `1+8` | 9 | independent arithmetic |
| R-CHAIN-C-CONSTANT | exact | `-2-8` | -10 | independent arithmetic |
| R-CHAIN-ADA-COEFFICIENT | exact | `1+2` | 3 | independent arithmetic |
| R-CHAIN-ADA-CONSTANT | exact | `-2-2` | -4 | independent arithmetic |
| R-P14-COEFFICIENT | exact | `9+2` | 11 | independent arithmetic |
| R-P14-CONSTANT | exact | `-10-4` | -14 | independent arithmetic |
| R-P14-N3-DELTA | exact | `11*2^4-2*3-14-(9*2^4-3-10)` | 25 | independent arithmetic |
| R-P14-N3-ADDED-PREFIX-SUM | exact | `2^2-1+2^3-1+2^4-1` | 25 | independent arithmetic |

Blocked symbolic requests:

- R-SUM-PREFIX-COUNT, jackal_poly_eq, requested input=`{"lhs":"x*(x+1)/2-(x-1)*x/2","rhs":"x"}`: MCP tool call requires approval, but approval policy is never. No mathematical result.
- R-SLOT-COUNT, jackal_poly_eq, requested input=`{"lhs":"x*(x-1)/2+2*x","rhs":"(x^2+3*x)/2"}`: MCP tool call requires approval, but approval policy is never. No mathematical result.
- R-CHAIN-SUBSTITUTION, jackal_poly_eq, requested input=`{"lhs":"x-2+8*(x-1)","rhs":"9*x-10"}`: MCP tool call requires approval, but approval policy is never. No mathematical result.
- R-CHAIN-INDUCTION, jackal_poly_eq, requested input=`{"lhs":"1+2*(2*x-1)","rhs":"4*x-1"}`: MCP tool call requires approval, but approval policy is never. No mathematical result.

