# Shared JSON parser controls — source-only candidate

**UNAPPLIED / UNVERIFIED / NOT COMPILED / NOT TESTED / NOT PROVED.**
This directory supplies deterministic Ada assertion fixtures and a candidate-only
project for the immutable `shared-json-parser-candidate-v1` proposal. It contains
no new production implementation and does not change the earlier proposal,
original tests, accepted cases, public contracts, deadlines or proof scope.
The coordinator owns review, copying to fresh records and every execution.

Formation command, from the owned worktree root:

```text
python3 -B scratch/acquisition2/resume-20261015-v1/shared-json-parser-controls-v1/prepare_receipt.py
```

That command only reads and snapshots source bytes, checks their exact identities,
records the explicit application dependency inventory and hashes the configured
external Ada source universes. It imports only Python standard-library modules;
it never imports candidate/product code, runs the controls or invokes an Ada tool.
The exclusive preparation receipt records the exact observed source epoch, command
and outputs. Its measurements are not program correctness evidence.

## Explicit source epoch and dependency choice

The coordinator explicitly selected current source epoch
`4ff3bf48b4323c051ffa8cf04ba4787982111f6d`. The current core snapshots are checked
against that commit's actual file bytes. This is an explicit source-epoch change
from the earlier proposal, not a silent resource-body replacement. The shared
parser proposal receipt remains exactly
`4a78d4fd3fe9233bfbeb71d6a85e4ecab7dc97d7452a38a6d60b9f8e8dc449df`.
All copied proposal sources must match their immutable receipt.

`WORLDLINE_PARSER_RESOURCE_BODY=current_D56` is the default. It selects the
current `Resource_Quantities` body
`23e67ed2f9fbb65741e5ddfab10fbde101a719feeb649a2bf1c9ae8052421a1a`.
The earlier body
`127aea76bb983d83506beb20954ab83264f7b8185b2a2e74ecca8684ce47635d`
is retained only under the explicitly optional `historical_original` scenario.
No unchanged replay of its known failed cursor closure is proposed. Separate
object/executable directories prevent accidental scenario artifact reuse.

Retained `docs/decisions.md` D53/D56 reports the earlier complete cursor closure
failure at `Resource_Quantities.Capacity_Fits` (`Residue < Place`), then the
qualified existing `Column_Bounds` ghost call under unchanged bounds. D56's
isolated cursor closure passed with the new body and root recorded the exact
core application. That retained result does **not** prove this new shared-parser
project, unchanged numeric/render consumers, production integration or full
WORLDLINE closure. The copied cursor spec's original preparation comment is
preserved verbatim; the later D53/D56 evidence lives in root's retained records.

## Fixture oracles and scope

Both mains use enabled `pragma Assert` with literal expected values or directly
stated coordinate properties. They do not call a reference decoder, Python JSON
parser or candidate implementation to manufacture expected results. Candidate
calls are the operations under test. No replacement numeric renderer or model
stands in for the actual dependencies.

| Source | Proposed independent fixture coverage |
| --- | --- |
| `string_parser_controls.adb` | Every original top-level syntax alternative; signs, fraction and exponent branches; original NaN/Infinity spellings; all simple escape branches, hex escape, surrogatepass; ASCII/multibyte/raw control and malformed UTF8; arrays/objects/nesting; original whitespace; missing/truncated/malformed tokens and complete-consumption refusals; shifted and endpoint String origins. |
| Same String main | Original public selectors and convenience APIs; duplicate and escaped-equivalent keys, last-key-wins, unique counts and member order; Standard_JSON/Duplicate_Free/Original_Exact distinctions; decoded Text, numeric-kind/token-sensitive Equal, Truth and decimal predicates; actual exact-decimal/binary64 Number_Image and JSON/Python render paths. |
| `wide_parser_controls.adb` | UTF8/16/32 BOM and original BOMless detection paths, both endian orders, original two-byte heuristic; UTF8/16/32 surrogatepass and paired UTF16; maximum codepoint and invalid ceiling; encoded escapes/nonfinite syntax; duplicate object syntax; malformed suffixes, invalid/truncated scalar units, empty/BOM-only input and invalid spans. |
| Same wide main | Explicit BOM-relative byte offsets and whitespace outside returned node; shifted arena and inner span; small arrays whose absolute last index is Byte_Count'Last; direct generic nonaligned source-relative start and invalid starting offset. |

These are finite branch-oriented fixtures, not a machine-measured exhaustive
coverage claim. Endpoint-origin fixtures allocate only their small stated
extents; they do not execute a giant archive, prove allocation feasibility or
establish an arbitrary-length theorem. Wide tests cover syntax nodes only:
there are no wide value selectors, duplicate predicates, exact numeric values,
decoded Text or materializing renderers in the proposal yet.

Public String `Equal` deliberately preserves the original implementation's
same-kind and raw numeric-token comparison: `1` and `1.0`, and `0` and `-0`,
are unequal in that API. The fixtures do not substitute Python numerical
equality. Ordinary Parse continues accepting duplicate keys/nonfinite syntax;
stricter admission predicates remain distinct. String Parse keeps its original
UTF8 treatment without BOM stripping. The wide adapter retains original raw
encoding detection before feeding the shared grammar.

## Dependency inventory and proof boundary

`dependency-manifest.json` records actual copied application specs/bodies,
imports, hashes, origins and current-commit equality. The candidate project
contains the real Resource_Quantities, Archive_Text, SHA256, Evaluation_Epoch,
Evaluation_Pending, Exact_Decimal, Decimal_Binary64, Producer_Render and Unicode
sources, as well as the unchanged public Producer_Values spec, proposed body,
shared grammar and scalar cursor. Spec-only packages are the inspected existing
expression/type units; no body stub is introduced. Mutual Producer_Values and
Producer_Render dependencies are retained.

The explicit application context frontier is Interfaces and SPARK.Big_Integers.
The latter is the existing full-library rename to
Ada.Numerics.Big_Numbers.Big_Integers. `external-source-identities.json` records
the actual configured private full SPARK library source universe, project files
and prebuilt archive, plus the configured GNAT Ada runtime source universe.
This inclusive source inventory retains actual dependency bodies rather than
inventing wrappers or trusted substitutes. Those external source files are not
copied into Source_Dirs to override the installed runtime.

**Limits:** textual import/parent traversal is not compiler dependency
resolution. Generic formal contract legality, discriminated result-component
uses, complete interface compatibility and compiler/binder-selected runtime
closure remain UNVERIFIED. Implicit native runtime/C/GMP/linker closure is not
established by an Ada source inventory. The existing private SPARK library's
externally-built proof boundary remains explicit; this project does not claim
GNATprove analyzes every inventoried runtime/library body. The exact original
full WORLDLINE proof/build projects and their assurance rules remain mandatory.

The source-only controls use unchanged public contracts. Proving their semantic
assertions may expose missing truthful postconditions or other existing proof
work. Do not disable assertions, hide failed obligations, replace the actual
dependencies or treat runtime success as universal grammar/value equivalence.

## Proposed coordinator payloads — not executed here

Run only from a fresh coordinator-owned immutable copy after exact source/method
review, through the existing reviewed shared-lock/memory/storage admission and
own systemd 8G/swap0 wrapper. Do not launch these bare commands outside that
wrapper. Preserve original failed evidence and record every step separately.
The existing wrapper must record tool versions/hashes, source identities before
and after, actual scope limits/cleanup and unchanged private library artifacts.

Use the configured GNAT environment and prepend the already-qualified private
library project directory to GPR_PROJECT_PATH:

```text
/home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z/scratch/old-analysis/private-sparklib-experiment/lib/gnat
```

Exact proposed payload argument vectors in the copied candidate directory:

```text
gprbuild -p -P shared_json_parser_controls.gpr -j2 -XWORLDLINE_PARSER_RESOURCE_BODY=current_D56 -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True -XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True
gnatprove -P shared_json_parser_controls.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on --memlimit=1024 --timeout=60 -j2 -XWORLDLINE_PARSER_RESOURCE_BODY=current_D56 -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True -XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True
./bin-current-D56/string_parser_controls
./bin-current-D56/wide_parser_controls
```

Only execute a main if build succeeded. Inspect both main ALI files for enabled
assertions and retain the complete proof output and per-unit analysis inventory,
not just exit codes or selected cursor checks. Full candidate closure may fail
in original untouched consumers; that remains a failure, not an exclusion.

Success would establish only the exact measured/tested/proved candidate scope.
It would not complete Raw_JSON integration, full-value authority, Old retirement,
acquisition, any full WORLDLINE gate or independent acceptance. The consumed
isolated positive diagnostic is not repeated and its timeout is not classified
from these unrelated controls. Production Raw_JSON representation work remains
open until the remaining shared grammar consumers and original full-path gates
are implemented and verified.
