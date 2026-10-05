# Appendix A to D1 DESIGN v5: Python decimal-integer conversion surface (OD-2 input), corrected census

Status: **DRAFT for independent review.** Nothing here was executed, reviewed or accepted. O-PYTHON, O-PY-AUDIT and
O-PY-COST stay OPEN. No OD-2 option is selected. This appendix is part of the D1 DESIGN v5 package (`DESIGN.md` in this
directory cites its sha256). It reproduces the v4 Appendix A, which the v4 review accepted, with the two v5 changes
listed in A.0. No census was re-run for v5; every count is v4's.

Evidence labels follow `DESIGN.md` §2: **[OBS]** observed, **[JKL K-nn]** a JACKAL result recorded in `jackal.json`
(K-01..K-212 in v4's `jackal.json`, K-213 onwards in v5's), **[LEAD]** unverified lead reasoning, **[DOC]**
documentation text.

## A.0 What this revision answers

v5 changes (V4-RC2):

| Review item | Change in this appendix |
|---|---|
| V4-RC2 (g): complete C12's operand inventory (`CalledProcessError` return code at `native/build_guard.py:44-45`) | A.5's note on rows 160-162 now lists every integer-to-decimal conversion in the file, including the `CalledProcessError` message and interpreter diagnostics of uncaught exceptions, each with its bound; A.9 points to it |
| V4-RC2 (f): R-OVR pre-scan conditions | A.5's settings paragraph records that no routed site passes `default=` or `cls=` (as v4's census found), which is R-OVR's condition 2 (`DESIGN.md` §11.4.2) |

v4 changes, carried:

| Review item | Correction in this appendix |
|---|---|
| V3-F2 / V3-RC1 (aliased JSON call; direct-name scan not a census) | A.2 defines a scope-aware semantic census; A.3 reports it over all 300 Python files; A.5 adds the alias site `scripts/decisive_evaluation_test.py:264` (row 193) with its operands |
| V3-F3 / V3-RC1 (C4/C5 byte identity false for `proof_manifest.py`) | A.1 records the actual delta: C5 appends lines 1024-1029 to C4's 1023 lines; lines 1-1023 are identical, so the site at `:921` is unchanged but the file is not byte-identical |
| V3-RC1 (exclusions as absolute-magnitude and lexical digit-count bounds) | A.4 states both criteria |
| V3-RC1 (`native/build_guard.py` interpreter) | A.5 rows 160-162 carry the reviewed bound; `DESIGN.md` §11.3 class C12 gives the E1 disposition |
| Census gaps found while repairing V3-F2 | A.3/A.7: root tools (2 operations) and `tests/` (254 operations, original controls) are inside the universe; A.8 enumerates stdlib text parsers and source compilation that v3 left as uncounted categories |

## A.1 Source identities and C4/C5 identity (corrected)

- `C5` = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source`.
  `C4` = `.../work/reviewed-common-proof-source-composition-v4/source`.
- **Universe.** 300 Python files: every regular file under `C5` (excluding `.git`) whose name ends in `.py`, plus the
  three python-shebang scripts `cli/worldline`, `cli/worldline-relocate` and `daemon/worldlined` [OBS read-only walk;
  total JKL K-84]. Per top-level directory: `runtime` 121, `scripts` 14, `protected-startup` 5,
  `protected-resource` 4, `cli` 2, `protected-runtime` 2, `daemon` 1, `native` 1 (v3's universe, 150 files
  [K-83]); repository root 2 (`refresh_contract_pins.py`, `verify_proof_manifest.py`); `protected-lab` 2; `tests` 146.
- **C4/C5 identity (V3-F3 corrected).** 299 of the 300 files are byte-identical between C4 and C5; exactly one differs
  [OBS sha256 comparison; K-91]:

| File | C4 sha256 (lines) | C5 sha256 (lines) | Delta [OBS `diff`] |
|---|---|---|---|
| `runtime/worldline/proof_manifest.py` | `8ae6c3c14b835af3825acca806649b11daeb839b45a6506a5fbd29732bbfcd23` (1023) | `51dd30d1a2c19cea4b9794e869400c5cb7c4193043f66678e62efa695b058fcb` (1029) | C5 appends lines 1024-1029 (6 lines [K-93]): a blank line, a comment, `CONTRACT_PINS.update({...})` with three string pins of the explicit-recovery-marker files, a blank line, a comment, and `CONTRACT_PINS.update({...})` with the normalized pins of the claude-composition-v5-beta composed source. Lines 1-1023 are identical. The appended statements contain only string literals: no JSON call and no decimal conversion |

  The v3 statement "none of the listed Python files differs between v4 and v5-beta" is withdrawn. The JSON site
  `proof_manifest.py:921` (`json.loads` in `load_manifest`) is textually unchanged; the file's identity is C5's.
  Of the 126 files that contain a JSON operation, 125 are byte-identical and this one is not [K-92].
- **Identities of files cited for new findings** [OBS `sha256sum`]:

| File | sha256 |
|---|---|
| `scripts/decisive_evaluation_test.py` | `559e72a5ccce331da79a9e67c8698c8599b31688f5b253abffde0c600932daa1` |
| `native/build_guard.py` | `949f917d8a194c41d94ba6ea262d1758c3803c58bac4d18f22604524ee8d07d7` |
| `runtime/worldline/environment.py` | `22afe46da5bf2c96ac42ac901cc643b0c6a26d28f95377bc23e4c4c20c8e2456` |
| `refresh_contract_pins.py` | `0ead9969da3c4efc521e92c196efb4943870ceca2f6f9e6845d69035d8f12eb8` |
| `verify_proof_manifest.py` | `9b5bcbae627fe755eada5ca7e1cd503144a87e89ebf5208af6d972b98df02a9f` |
| `runtime/worldline/checks.py` | `110d95f7f0146c0c8e97b0c43807b9ea18f30ba48cb62b71cccd8d9ed46af565` |
| `runtime/worldline/canonical.py` | `d80f79bcedace5364d2e9a238ab05b48250660d86cfb4c14aa5393f4b37952af` |
| `tests/diagnostic_value_stream.py` | `d1ea8fb9397e76c478f93f72d2e29deed625a2871198c94a2f86e5287b1256c5` |
| `/usr/lib/python3.14/json/encoder.py` | `d68a4d04d2cfd95897498307f29349058b42c3f48ea6aa6739714a09200a7d01` |
| `/usr/lib/python3.14/json/decoder.py` | `dc98d3e677612ea7311303f06a144cec6b91ebadc7ec037d1777501647578a07` |
| `/usr/lib/python3.14/json/scanner.py` | `572958017eae8842eeddd0e3d18d3c56cc0a197348224915e1d87ce937841764` |
| `/usr/lib/python3.14/json/__init__.py` | `2dd10f1bf4c9ea5478e589216805e7f279d0e4bce134a19efa297404fb87407d` |
| `/usr/lib/python3.14/tomllib/_re.py` | `e0d6f33e345e0a43a55f3965d6c3eef89b69ec4767478e30dbba80458d80854d` |
| `/usr/include/python3.14/internal/pycore_long.h` | `2705119761c8a877f277fe34773a1117d6b4c0cd4b39c7823a019f3ba44c6f0f` |
| `/usr/include/python3.14/internal/pycore_ceval.h` | `8f46d9b4b75258141e3ef9f229091497d4cb551318843caee40245eaaa49206d` |

v5 read `/usr/lib/python3.14/subprocess.py:132-155` (`CalledProcessError`) and `:1996-2003` (`_handle_exitstatus`)
for V4-RC2 (g); its sha256 in this session is `6628ffdd65c093a6c08cae01ffe82877d3ced515aac9e7be0cff16512c30a7d9`
[OBS `sha256sum`].

## A.2 Census method (semantic, stronger than direct-name matching)

The census was a read-only Python `ast` analysis of source text, run in the v4 drafting session. No WORLDLINE module
was imported or executed [OBS]. It is stronger than v3's direct-name match in five ways:

1. **Universe.** All 300 files of A.1, not v3's eight directories. Every file parsed under the installed Python 3.14
   grammar with zero syntax errors. String constants containing `import` and a newline were also parsed as inline
   sources. 152 such constants parsed and were analysed. Five are outside `tests/`:
   `runtime/worldline/finalize.py:35`, `runtime/worldline/linux/netguard.py:39`,
   `runtime/worldline/simulation.py:30` (two JSON sites) and `scripts/decisive_evaluation_test.py:64, :100`. The other
   147 are inside `tests/`. 9 string constants that mention `json` but do not parse as Python are listed in A.7; all
   are inside `tests/`.
2. **Scope-aware bindings.** Per module, function, lambda and class scope (class scopes are skipped for nested
   function lookup, as Python does), the scan records every name bound to:
   - the `json` package or a submodule: `import json`, `import json as X`, `import json.decoder`,
     `from json import decoder`, `X = json`, `importlib.import_module('json…')`, `__import__('json')`;
   - a JSON function: `from json import dumps [as d]`, `d = json.dumps`, `d = X.dumps`,
     `functools.partial(json.dumps, …)`;
   - an encoder or decoder class or instance: `json.JSONEncoder`, `json.JSONDecoder`, and names assigned from their
     instantiation;
   - `from json import *` and the libraries `simplejson`, `orjson`, `ujson`, `rapidjson`, `hyperjson`, `msgspec`.
   Assignment aliases are resolved to a fixpoint. Ambiguous rebinding is treated conservatively, as a JSON binding.
3. **Reference classes.** Every use is classified: CALL-DIRECT (`json.f(...)` with the canonical name, v3's only
   class), CALL-ALIAS (a call through any alias, from-import or assigned name), CALL-PARTIAL, CLASS-INSTANTIATE,
   INSTANCE-METHOD (a method called on an encoder or decoder instance), REF-FORWARD (a JSON function or class used
   other than as a callee: assigned, passed, stored or returned), MODULE-ESCAPE (the module object passed as an
   argument), DYNAMIC (`getattr` on a module alias), SUBCLASS, STAR and OTHER-LIBRARY. Calls with `*args` or
   `**kwargs` (forwarded settings) are flagged.
4. **Textual cross-check.** Every textual occurrence of `.dumps(`, `.loads(`, `.dump(`, `.load(`, `dumps(` and
   `loads(` that the AST census did not account for was listed. Outside `tests/`, the residue is entirely non-JSON:
   - `marshal.dumps` (`protected-runtime/approved_source_loader.py:84`);
   - `ast.dump` (`refresh_contract_pins.py:61`);
   - `tomllib.loads` (`runtime/worldline/environment.py:217, 236`; see A.8);
   - WORLDLINE `GlobalConfig.load`, `ProjectConfig.load` and `Manifest.load` methods, whose JSON operations are the
     counted sites inside their bodies.
5. **Library internals.** JSON use inside the standard library is out of a call census by construction. Stdlib text
   parsers that perform decimal conversions internally are enumerated separately in A.8.

Limits [LEAD]: the census is static. It cannot see:

- a module object held as an object attribute;
- `eval`/`exec` of non-constant text;
- data-dependent `getattr` names;
- C extensions (the only one, `native/examiner_guard.c`, calls `PyLong_AsInt` at `:2230` and no decimal C-API
  conversion [OBS grep]).

It is a stronger minimum census, not a data-flow proof. PY-13 (`DESIGN.md` §12.5) re-runs it on the exact source
identity.

## A.3 Census results and scope partition

**v3 universe (150 files) [OBS census]:**

- CALL-DIRECT: 192. This reproduces v3 and the review exactly, including the two inline-child sites of
  `runtime/worldline/simulation.py:30`.
- CALL-ALIAS: 1, the omitted site `scripts/decisive_evaluation_test.py:264` (`_json.dumps`, alias bound by
  `import json as _json` at `:260`).
- Zero: partials, forwarded references, module escapes, dynamic `getattr`, subclasses, star imports, other JSON
  libraries, and forwarded `*args`/`**kwargs`.
- Total 193 [K-79]. Outside `runtime/`: 69 [K-82].

**Extended universe (300 files) [OBS census]:**

- Repository root: 2 CALL-DIRECT.
- `protected-lab`: 0.
- `tests/`, 61 files: 250 CALL-DIRECT (36 of them inside inline test sources), 1 CLASS-INSTANTIATE and 3
  INSTANCE-METHOD calls; 254 operations [K-85]. The last four are in `tests/diagnostic_value_stream.py`:
  `_JSON = json.JSONEncoder(ensure_ascii=True, allow_nan=False, separators=(',', ':'))` at `:31`, and
  `_JSON.encode` at `:43` and `:98`, `_JSON.iterencode` at `:153`.

| Scope | Meaning | Operations | Disposition class |
|---|---|---|---|
| PROD-RUNTIME | `runtime/` production code | 122 | routed or bounded |
| INLINE-CHILD | source executed by a `-I -S` child (`simulation.py:30`) | 2 | routed (inlined codec) or bounded |
| PROD-PROTECTED | protected-service entry code outside `runtime/` | 10 [K-55] | routed or bounded (operator custody) |
| ORIGINAL-CONTROL | `*/controls/` campaign and test code | 25 [K-56] | byte-identical, unchanged |
| BUILD-TOOL | `native/build_guard.py` | 3 | reviewed bound (A.5 rows 160-162) |
| INSTALL-RELEASE-SCRIPT | `scripts/`, including the alias site | 31 [K-80] | routed or bounded |
| ROOT-TOOL | `refresh_contract_pins.py:82`, `verify_proof_manifest.py:92` | 2 | routed, bounded or configured |
| ORIGINAL-TEST | `tests/` | 254 [K-85] | byte-identical, unchanged |

Totals:

- v3-universe partition: 122 + 2 + 10 + 25 + 3 + 31 = 193 [K-81].
- Routed or bounded scopes: 170 [K-86].
- Original controls and tests, unchanged: 279 [K-87].
- All JSON operations: 449 [K-88]; cross-checked by directory group, 193 + 2 + 254 = 449 [K-89].

## A.4 Disposition rules under each OD-2 option (exclusion precision)

- **E0 (no decision).** Every site keeps today's behaviour. A decimal integer beyond the configured limit raises
  `ValueError`, or another class where a parser wraps it. That is an OPEN failure, never an accepted refusal.
- **E1 (interpreter-wide unlimited).** A site is covered only if its interpreter belongs to a process class that
  `DESIGN.md` §11.3 shows is configured before the site's first relevant conversion. Classes C12 (build tool), C13
  (root tools) and C14 (test runners) were added in v4.
- **E2 (scoped codec).** Every routed-scope operation moves to the codec, with every existing keyword setting
  preserved, or carries a reviewed demonstration of the following form. "Below 10**640" alone no longer suffices.
  - **Formatting** (`int` to decimal text: JSON values and keys, `str`, `repr`, `format`, f-string fields,
    `%`-format, lazy `logging` arguments, exception messages formatted while unwinding): an **absolute-magnitude
    bound**. Every integer reaching the conversion satisfies `-10**640 < v < 10**640`, that is, the decimal digit
    count of `|v|` is at most 640. The sign is not counted [DOC Python documentation, integer string conversion length
    limitation]. A one-sided `v < 10**640` is insufficient: large negative values exist.
  - **Parsing** (decimal text to `int`: `json.loads` integers, `int(s)`, `int(s, 10)`, `int(s, 0)` on decimal
    text, `argparse` `type=int`, `tomllib` integers, Python-source literals): a **lexical digit-count bound**. Every
    admitted input text reaching the conversion has at most 640 decimal-digit characters in the converted literal.
    Leading zeros count. The sign, surrounding whitespace and PEP 515 underscores do not. For non-JSON `int()`, the
    Unicode decimal digits that `int` accepts count [DOC]. A bound on the parsed **value** is insufficient: `'0'*640
    + '1'` has value 1 and 641 digit characters [K-98]. For JSON literals the scanner admits no leading zeros, but
    the bound must still hold for every admitted input byte string, including peer, candidate and tampered inputs,
    not for a producer's intention.
  - 640 is used because it is the minimum admitted limit (`pycore_long.h:42` `_PY_LONG_MAX_STR_DIGITS_THRESHOLD`;
    0 or at least 640 are admitted [F25]). A demonstration meeting either criterion holds under every admitted
    configuration.
  - Such a demonstration is an audit result about where a value or text comes from. It is never a cap, and it
    never filters inputs.
  - INLINE-CHILD sites need the codec text inlined, because trusted helpers import the standard library only
    (`runtime/worldline/trusted.py:31-33`), or such a demonstration.
  - ORIGINAL-CONTROL and ORIGINAL-TEST files stay byte-identical. Additive PY controls exercise the large-integer
    cases instead.
- No site is excluded by module role alone.

## A.5 Site list, v3 universe plus root tools

Columns: number, scope, `file:line` (under `C5`), operation, enclosing function, keyword settings as written. Rows 1-192
are v3's rows, unchanged; v3's census reproduced them exactly. Rows 193-195 were added in v4. Every listed setting must
be preserved byte-for-byte by an E2 codec. `parse_int` is used at no site today.

| # | Scope | Site | Call | Enclosing | Settings |
|---|---|---|---|---|---|
| 1 | PROD-RUNTIME | `runtime/worldline/admission.py:430` | `json.loads` | `_load` | (defaults) |
| 2 | PROD-RUNTIME | `runtime/worldline/admission.py:477` | `json.dumps` | `_store` | indent=2 |
| 3 | PROD-RUNTIME | `runtime/worldline/anchor.py:343` | `json.loads` | `read_pin` | (defaults) |
| 4 | PROD-RUNTIME | `runtime/worldline/canonical.py:43` | `json.dumps` | `canonical_bytes` | ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':') |
| 5 | PROD-RUNTIME | `runtime/worldline/canonical.py:54` | `json.loads` | `parse_canonical` | (defaults); argument `data.decode("utf-8", "strict")` |
| 6 | PROD-RUNTIME | `runtime/worldline/causal.py:277` | `json.loads` | `why` | (defaults) |
| 7 | PROD-RUNTIME | `runtime/worldline/checks.py:878` | `json.loads` | `_parse` | (defaults) |
| 8 | PROD-RUNTIME | `runtime/worldline/cli_main.py:105` | `json.dumps` | `_emit` | indent=2, sort_keys=True, ensure_ascii=False |
| 9 | PROD-RUNTIME | `runtime/worldline/cli_main.py:109` | `json.dumps` | `_emit` | indent=2, sort_keys=True, ensure_ascii=False |
| 10 | PROD-RUNTIME | `runtime/worldline/cli_main.py:654` | `json.dumps` | `main` | sort_keys=True |
| 11 | PROD-RUNTIME | `runtime/worldline/client.py:61` | `json.loads` | `request` | (defaults) |
| 12 | PROD-RUNTIME | `runtime/worldline/client_peer.py:115` | `json.loads` | `__init__` | (defaults) |
| 13 | PROD-RUNTIME | `runtime/worldline/client_peer.py:137` | `json.loads` | `observation` | (defaults) |
| 14 | PROD-RUNTIME | `runtime/worldline/client_peer.py:220` | `json.loads` | `preparer_observations` | (defaults) |
| 15 | PROD-RUNTIME | `runtime/worldline/client_peer_relay.py:95` | `json.loads` | `receive_request_peer` | object_pairs_hook=unique |
| 16 | PROD-RUNTIME | `runtime/worldline/client_peer_relay.py:102` | `json.loads` | `receive_request_peer` | (defaults) |
| 17 | PROD-RUNTIME | `runtime/worldline/config.py:83` | `json.loads` | `load` | (defaults) |
| 18 | PROD-RUNTIME | `runtime/worldline/controller.py:1208` | `json.loads` | `_manifest_origin` | (defaults) |
| 19 | PROD-RUNTIME | `runtime/worldline/daemon.py:304` | `json.loads` | `_dispatch_line` | (defaults); request `id` may be any non-Boolean `int` (`:309-311`) |
| 20 | PROD-RUNTIME | `runtime/worldline/environment.py:140` | `json.loads` | `capture_workspace` | (defaults) |
| 21 | PROD-RUNTIME | `runtime/worldline/environment.py:227` | `json.loads` | `_parse_dependency_group` | (defaults) |
| 22 | PROD-RUNTIME | `runtime/worldline/evaluation_pending.py:75` | `json.dumps` | `canonical` | ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False |
| 23 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:122` | `json.loads` | `bytes_value` | (defaults) |
| 24 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:150` | `json.loads` | `decode_payload` | (defaults) |
| 25 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:568` | `json.loads` | `_observe` | (defaults) |
| 26 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:614` | `json.loads` | `observe_raw` | (defaults) |
| 27 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:657` | `json.loads` | `_captured_observation_events_locked` | (defaults) |
| 28 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:685` | `json.loads` | `_captured_stream_locked` | (defaults) |
| 29 | PROD-RUNTIME | `runtime/worldline/install_config.py:31` | `json.loads` | `patch_shell` | (defaults) |
| 30 | PROD-RUNTIME | `runtime/worldline/install_config.py:58` | `json.dumps` | `patch_shell` | ensure_ascii=False, indent=2 |
| 31 | PROD-RUNTIME | `runtime/worldline/project.py:106` | `json.loads` | `load` | (defaults) |
| 32 | PROD-RUNTIME | `runtime/worldline/proof.py:129` | `json.loads` | `_inspect` | (defaults) |
| 33 | PROD-RUNTIME | `runtime/worldline/proof.py:165` | `json.loads` | `_inspect` | (defaults) |
| 34 | PROD-RUNTIME | `runtime/worldline/proof_manifest.py:921` | `json.loads` | `load_manifest` | (defaults); file identity is C5's (A.1) |
| 35 | PROD-RUNTIME | `runtime/worldline/protected_owner.py:35` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False |
| 36 | PROD-RUNTIME | `runtime/worldline/protected_owner.py:43` | `json.loads` | `exact` | object_pairs_hook=pairs |
| 37 | PROD-RUNTIME | `runtime/worldline/protected_recovery_capture.py:58` | `json.loads` | `exact_json` | object_pairs_hook=pairs |
| 38 | PROD-RUNTIME | `runtime/worldline/protected_startup.py:36` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False |
| 39 | PROD-RUNTIME | `runtime/worldline/protected_startup.py:47` | `json.loads` | `exact_json` | object_pairs_hook=pairs, parse_constant=(refusing lambda) |
| 40 | PROD-RUNTIME | `runtime/worldline/relocate.py:454` | `json.loads` | `_plan_transaction_records` | (defaults) |
| 41 | PROD-RUNTIME | `runtime/worldline/relocate.py:1124` | `json.loads` | `main` | (defaults) |
| 42 | PROD-RUNTIME | `runtime/worldline/relocate.py:1134` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 43 | PROD-RUNTIME | `runtime/worldline/relocate.py:1140` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 44 | PROD-RUNTIME | `runtime/worldline/relocate.py:1142` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 45 | PROD-RUNTIME | `runtime/worldline/report.py:74` | `json.dumps` | `prepare_private_report` | sort_keys=True, separators=(',', ':') |
| 46 | PROD-RUNTIME | `runtime/worldline/report.py:118` | `json.loads` | `collect_private_report` | (defaults) |
| 47 | PROD-RUNTIME | `runtime/worldline/report.py:193` | `json.loads` | `_collect_private_report_observed` | (defaults) |
| 48 | PROD-RUNTIME | `runtime/worldline/returning.py:182` | `json.loads` | `_receipt_with_before_root` | (defaults) |
| 49 | PROD-RUNTIME | `runtime/worldline/runner.py:844` | `json.loads` | `read_stdout` | (defaults) |
| 50 | INLINE-CHILD | `runtime/worldline/simulation.py:30` (inline source, line 8) | `json.loads` | child `-I -S` interpreter | (defaults) |
| 51 | INLINE-CHILD | `runtime/worldline/simulation.py:30` (inline source, line 24) | `json.dumps` | child `-I -S` interpreter | sort_keys=True, separators=(',', ':') |
| 52 | PROD-RUNTIME | `runtime/worldline/simulation.py:238` | `json.loads` | `run` | (defaults) |
| 53 | PROD-RUNTIME | `runtime/worldline/store.py:211` | `json.loads` | `_json_load` | (defaults) |
| 54 | PROD-RUNTIME | `runtime/worldline/store.py:887` | `json.loads` | `causal_events_for_world` | (defaults) |
| 55 | PROD-RUNTIME | `runtime/worldline/store.py:1005` | `json.loads` | `receipt_for_transaction` | (defaults) |
| 56 | PROD-RUNTIME | `runtime/worldline/store.py:1010` | `json.loads` | `receipt_for_candidate` | (defaults) |
| 57 | PROD-RUNTIME | `runtime/worldline/store.py:1063` | `json.loads` | `verify_chains` | (defaults) |
| 58 | PROD-RUNTIME | `runtime/worldline/store.py:1085` | `json.loads` | `verify_chains` | (defaults) |
| 59 | PROD-RUNTIME | `runtime/worldline/store.py:1174` | `json.loads` | `last_receipt` | (defaults) |
| 60 | PROD-RUNTIME | `runtime/worldline/transaction.py:552` | `json.loads` | `listing` | (defaults) |
| 61 | PROD-RUNTIME | `runtime/worldline/transaction.py:791` | `json.loads` | `_authorize` | (defaults) |
| 62 | PROD-RUNTIME | `runtime/worldline/transaction.py:810` | `json.loads` | `_observe_authorization` | (defaults) |
| 63 | PROD-RUNTIME | `runtime/worldline/transaction.py:1918` | `json.loads` | `_marker` | (defaults) |
| 64 | PROD-RUNTIME | `runtime/worldline/transaction.py:1933` | `json.loads` | `_load_record` | (defaults) |
| 65 | PROD-RUNTIME | `runtime/worldline/agents/pi.py:52` | `json.loads` | `_declares_provider` | (defaults) |
| 66 | PROD-RUNTIME | `runtime/worldline/linux/criu.py:72` | `json.loads` | `restore` | (defaults) |
| 67 | PROD-RUNTIME | `runtime/worldline/linux/docker.py:86` | `json.loads` | `capture` | (defaults) |
| 68 | PROD-RUNTIME | `runtime/worldline/linux/examiner_loader.py:285` | `json.loads` | `decode_policy` | object_pairs_hook=_unique, parse_constant=_nonfinite |
| 69 | PROD-RUNTIME | `runtime/worldline/linux/hyprland.py:36` | `json.loads` | `query` | (defaults) |
| 70 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:445` | `json.loads` | `_retain` | (defaults) |
| 71 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:445` | `json.dumps` | `_retain` | (defaults) |
| 72 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:580` | `json.loads` | `_namespace_anchor` | object_pairs_hook=unique |
| 73 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:911` | `json.dumps` | `_mount_handle` | (defaults) |
| 74 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1061` | `json.dumps` | `_acknowledgement` | (defaults) |
| 75 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1117` | `json.loads` | `_native_json` | object_pairs_hook=unique, parse_constant=invalid, parse_float=finite |
| 76 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1121` | `json.dumps` | `_native_reply` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 77 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1370` | `json.loads` | `_entry_preparation` | object_pairs_hook=unique_fields, parse_constant=invalid_constant, parse_float=finite_float |
| 78 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1395` | `json.loads` | `_entry_preparation` | object_pairs_hook=unique_fields, parse_constant=invalid_constant, parse_float=finite_float |
| 79 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1455` | `json.dumps` | `_entry_preparation` | (defaults) |
| 80 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1503` | `json.loads` | `_observe` | object_pairs_hook=unique_fields |
| 81 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1535` | `json.loads` | `_observe` | (defaults) |
| 82 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:176` | `json.dumps` | `send_packet` | sort_keys=True |
| 83 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:204` | `json.loads` | `receive_packet` | object_pairs_hook=unique |
| 84 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:565` | `json.dumps` | `_seed` | sort_keys=True |
| 85 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:606` | `json.dumps` | `_quota_reader` | sort_keys=True |
| 86 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:707` | `json.dumps` | `_descriptor_reader` | sort_keys=True |
| 87 | PROD-RUNTIME | `runtime/worldline/linux/native_lifetime.py:676` | `json.dumps` | `receive` | sort_keys=True, separators=(',', ':') |
| 88 | PROD-RUNTIME | `runtime/worldline/linux/native_lifetime.py:711` | `json.dumps` | `receive` | sort_keys=True, separators=(',', ':') |
| 89 | PROD-RUNTIME | `runtime/worldline/linux/private_case_copy.py:260` | `json.dumps` | `copy_case_tree` | sort_keys=True, separators=(',', ':') |
| 90 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:445` | `json.loads` | `_send_entry_preparation` | (defaults) |
| 91 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:445` | `json.dumps` | `_send_entry_preparation` | allow_nan=False |
| 92 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:454` | `json.dumps` | `_send_entry_preparation` | allow_nan=False, separators=(',', ':') |
| 93 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:462` | `json.dumps` | `_send_entry_preparation` | (defaults) |
| 94 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:491` | `json.loads` | `_send_entry_preparation` | object_pairs_hook=_unique_role_fields |
| 95 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:578` | `json.dumps` | `_send` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 96 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:601` | `json.loads` | `_receive` | object_pairs_hook=_unique_role_fields |
| 97 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:671` | `json.dumps` | `retain_read` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 98 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:797` | `json.loads` | `compile_entry` | object_pairs_hook=_unique_role_fields |
| 99 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:993` | `json.dumps` | `copy_frozen_tree` | sort_keys=True, ensure_ascii=True |
| 100 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1224` | `json.loads` | `_native_artifact` | object_pairs_hook=_unique_role_fields |
| 101 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1368` | `json.dumps` | `_loader_policy` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 102 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1535` | `json.dumps` | `_launch_and_collect` | (defaults) |
| 103 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1596` | `json.loads` | `_collect_launched` | (defaults) |
| 104 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1666` | `json.loads` | `_collect_observed` | (defaults) |
| 105 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1782` | `json.dumps` | `_sandbox` | (defaults) |
| 106 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1866` | `json.loads` | `_run_role` | (defaults) |
| 107 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1939` | `json.loads` | `_read_message` | (defaults) |
| 108 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1977` | `json.loads` | `_bootstrap` | (defaults) |
| 109 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2026` | `json.dumps` | `_bootstrap` | (defaults) |
| 110 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2297` | `json.dumps` | `worker_broker` | (defaults) |
| 111 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2304` | `json.dumps` | `worker_broker` | (defaults) |
| 112 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2308` | `json.dumps` | `worker_broker` | (defaults) |
| 113 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2503` | `json.dumps` | `broker` | (defaults) |
| 114 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2507` | `json.dumps` | `broker` | (defaults) |
| 115 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2540` | `json.dumps` | `broker` | (defaults) |
| 116 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2544` | `json.dumps` | `broker` | (defaults) |
| 117 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2609` | `json.dumps` | `_bootstrap` | indent=2 |
| 118 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2616` | `json.dumps` | `_candidate_request` | (defaults) |
| 119 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2681` | `json.dumps` | `_role` | (defaults) |
| 120 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2692` | `json.loads` | `_role` | object_pairs_hook=_unique_role_fields |
| 121 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2714` | `json.dumps` | `_role` | (defaults) |
| 122 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2759` | `json.loads` | `<module>` (`__main__` role entry) | (defaults) |
| 123 | PROD-RUNTIME | `runtime/worldline/linux/systemd.py:265` | `json.loads` | `launch_private_evaluator` | (defaults) |
| 124 | PROD-RUNTIME | `runtime/worldline/linux/systemd.py:593` | `json.loads` | `journal_events` | (defaults) |
| 125 | PROD-PROTECTED | `protected-resource/gate_bridge.py:16` | `json.loads` | `detached` | (defaults) |
| 126 | PROD-PROTECTED | `protected-resource/gate_bridge.py:31` | `json.loads` | `gate_bytes` | (defaults) |
| 127 | PROD-PROTECTED | `protected-resource/gate_bridge.py:156` | `json.loads` | `_rpc` | (defaults) |
| 128 | PROD-PROTECTED | `protected-resource/gate_bridge.py:270` | `json.loads` | `submit_from_existing_gate` | (defaults) |
| 129 | PROD-PROTECTED | `protected-resource/gate_bridge.py:290` | `json.loads` | `main` | (defaults) |
| 130 | PROD-PROTECTED | `protected-resource/run_service.py:23` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False |
| 131 | PROD-PROTECTED | `protected-resource/run_service.py:51` | `json.loads` | `parse_canonical` | (defaults) |
| 132 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:32` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False |
| 133 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:39` | `json.loads` | `parse` | object_pairs_hook=pairs, parse_constant=(refusing lambda) |
| 134 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:108` | `json.loads` | `checked_descriptor` | (defaults) |
| 135 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:134` | `json.dumps` | `execute_case` | (defaults) |
| 136 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:176` | `json.dumps` | `main` | (defaults) |
| 137 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:180` | `json.dumps` | `<module>` | (defaults) |
| 138 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:17` | `json.loads` | `fixture` | (defaults) |
| 139 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:51` | `json.dumps` | `test_exact_committed_duplicate_and_recover_return_original_result_without_append` | sort_keys=True |
| 140 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:56` | `json.dumps` | (same test) | sort_keys=True |
| 141 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:66` | `json.dumps` | `test_committed_lost_ack_after_restart_reconciles_once` | sort_keys=True |
| 142 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:68` | `json.dumps` | (same test) | sort_keys=True |
| 143 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:73` | `json.loads` | `test_same_id_changed_complete_packet_or_owner_refuses_without_mutation` | (defaults) |
| 144 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:73` | `json.dumps` | (same test) | (defaults) |
| 145 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:105` | `json.dumps` | `test_legacy_result_import_preserves_complete_original_row` | sort_keys=True |
| 146 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:108` | `json.dumps` | (same test) | sort_keys=True |
| 147 | PROD-PROTECTED | `protected-startup/launcher.py:26` | `json.loads` | `main` | (defaults) |
| 148 | PROD-PROTECTED | `protected-startup/launcher.py:41` | `json.dumps` | `main` | sort_keys=True |
| 149 | PROD-PROTECTED | `protected-startup/owner_provision_bootstrap.py:24` | `json.loads` | `provision` | (defaults) |
| 150 | ORIGINAL-CONTROL | `protected-startup/controls/additional_startup_controls.py:13` | `json.loads` | `fixture` | (defaults) |
| 151 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:41` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False |
| 152 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:47` | `json.loads` | `parse` | object_pairs_hook=pairs, parse_constant=(refusing lambda) |
| 153 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:157` | `json.dumps` | `execute_case` | sort_keys=True |
| 154 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:191` | `json.dumps` | `main` | sort_keys=True |
| 155 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:195` | `json.dumps` | `<module>` | (defaults) |
| 156 | ORIGINAL-CONTROL | `protected-startup/controls/test_protected_startup_v1.py:28` | `json.loads` | `test_missing_prior_lock_does_not_regenerate` | (defaults) |
| 157 | ORIGINAL-CONTROL | `protected-startup/controls/test_protected_startup_v1.py:36` | `json.loads` | `test_legacy_endpoint_refuses_without_removing_it` | (defaults) |
| 158 | ORIGINAL-CONTROL | `protected-runtime/controls/loader_probe.py:51` | `json.loads` | `main` | (defaults) |
| 159 | ORIGINAL-CONTROL | `protected-runtime/controls/loader_probe.py:58` | `json.dumps` | `main` | sort_keys=True |
| 160 | BUILD-TOOL | `native/build_guard.py:33` | `json.dumps` | `main` | (defaults); integers: three `st_size` values only (reviewed bound below) |
| 161 | BUILD-TOOL | `native/build_guard.py:50` | `json.dumps` | `main` | indent=2, sort_keys=True; integers: artifact `st_size` and `compilerReturncode` (always 0 here) |
| 162 | BUILD-TOOL | `native/build_guard.py:51` | `json.dumps` | `main` | (defaults); same `result` as row 161 |
| 163 | INSTALL-RELEASE-SCRIPT | `scripts/assurance.py:140` | `json.loads` | `proof_facts` | (defaults) |
| 164 | INSTALL-RELEASE-SCRIPT | `scripts/assurance.py:371` | `json.dumps` | `run` | indent=2, sort_keys=True |
| 165 | INSTALL-RELEASE-SCRIPT | `scripts/backup_manifest.py:53` | `json.dumps` | `main` | indent=2 |
| 166 | INSTALL-RELEASE-SCRIPT | `scripts/engine_codes.py:350` | `json.dumps` | `main` | indent=2 |
| 167 | INSTALL-RELEASE-SCRIPT | `scripts/evaluation_domain_gate.py:47` | `json.loads` | `run` | (defaults) |
| 168 | INSTALL-RELEASE-SCRIPT | `scripts/plugin_compat.py:53` | `json.loads` | `named_commit` | (defaults) |
| 169 | INSTALL-RELEASE-SCRIPT | `scripts/plugin_compat.py:85` | `json.loads` | `main` | (defaults) |
| 170 | INSTALL-RELEASE-SCRIPT | `scripts/plugin_compat.py:89` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 171 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:125` | `json.loads` | `prepared_transactions` | (defaults) |
| 172 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:177` | `json.dumps` | `main` | indent=2 |
| 173 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:206` | `json.loads` | `main` | (defaults) |
| 174 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:274` | `json.loads` | `main` | (defaults) |
| 175 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:350` | `json.loads` | `main` | (defaults) |
| 176 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:391` | `json.dumps` | `main` | indent=2 |
| 177 | INSTALL-RELEASE-SCRIPT | `scripts/prune_backups.py:62` | `json.dumps` | `main` | indent=2 |
| 178 | INSTALL-RELEASE-SCRIPT | `scripts/prune_backups.py:92` | `json.dumps` | `main` | indent=2 |
| 179 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:234` | `json.loads` | `main` | (defaults) |
| 180 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:242` | `json.loads` | `main` | (defaults) |
| 181 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:244` | `json.loads` | `main` | (defaults) |
| 182 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:265` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 183 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:266` | `json.dumps` | `main` | indent=2 |
| 184 | INSTALL-RELEASE-SCRIPT | `scripts/release_notes.py:41` | `json.loads` | `main` | (defaults) |
| 185 | INSTALL-RELEASE-SCRIPT | `scripts/release_notes.py:42` | `json.loads` | `main` | (defaults) |
| 186 | INSTALL-RELEASE-SCRIPT | `scripts/verify_install.py:88` | `json.loads` | `main` | (defaults) |
| 187 | INSTALL-RELEASE-SCRIPT | `scripts/verify_install.py:143` | `json.loads` | `main` | (defaults) |
| 188 | INSTALL-RELEASE-SCRIPT | `scripts/verify_install.py:205` | `json.dumps` | `main` | indent=2 |
| 189 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:36` | `json.dumps` | `problems` | sort_keys=True, separators=(',', ':'), ensure_ascii=True |
| 190 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:66` | `json.loads` | `main` | (defaults) |
| 191 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:66` | `json.loads` | `main` | (defaults; second call on the same line) |
| 192 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:70` | `json.dumps` | `main` | sort_keys=True |
| 193 | INSTALL-RELEASE-SCRIPT | `scripts/decisive_evaluation_test.py:264` (call spans `:264-275`) | `_json.dumps` (CALL-ALIAS; `import json as _json` at `:260`) | `main` | indent=2 |
| 194 | ROOT-TOOL | `refresh_contract_pins.py:82` | `json.dumps` | `main` | indent=2 |
| 195 | ROOT-TOOL | `verify_proof_manifest.py:92` | `json.loads` | `main` | (defaults); argument `manifest_path.read_text(encoding="utf-8")` |

Operand notes for the rows that v4 added or re-qualified, and v5's completion of rows 160-162 [OBS source; LEAD for
the bound arguments]:

- **Row 193 (alias).** Integer operands:
  - the literal `1` (`"schemaVersion": 1`, `:265`).
  The Boolean fields `allHold`, `ranAtAll`, `holds`, `fabricatedOutputAccepted` and `trustedExaminerRan` encode as
  `true`/`false`. The strings are `properties[*].detail`, `sorted(set(owned))` and `recordedStdout`
  (`stdout[:4000]`). Reviewed absolute-magnitude bound: `|1| < 10**640`. The `detail` strings are built by f-strings
  (`:231-235`) that format values from the evaluation result (`result.get('status')`, `result.get('reason')`). Those
  fields are non-JSON formatting candidates (A.8), classification OPEN. The script runs as
  `decisive_test.py --engine <runtime dir>` (docstring, `:20`). It belongs to class C10 in `DESIGN.md` §11.3.
- **Row 194.** `report` (`refresh_contract_pins.py:65-69`) holds strings, Booleans and `changes`, a list of dicts with
  string fields `path`, `stored`, `derived`, `sourceSha256` (`:37-39`). It has **no integer operand**, so the site
  performs no integer formatting. Its `ast.literal_eval` at `:30` and `ast.parse` at `:23` and `:55` are A.8
  source-compilation sites.
- **Row 195.** Parses `proof-manifest.json` under the `root` argument. It catches `OSError`, `UnicodeError`,
  `json.JSONDecodeError` and `RecursionError` (`:93`), not `ValueError`. A decimal literal over the limit escapes
  uncaught (E0 OPEN). No lexical bound is established for an arbitrary `root`, so the site must be routed or
  configured (class C13).
- **Rows 160-162 and the whole file (reviewed absolute-magnitude bound; inventory completed in v5, V4-RC2 g).** Every
  integer-to-decimal conversion that can occur in a `native/build_guard.py` process [OBS `native/build_guard.py:1-55`;
  `/usr/lib/python3.14/subprocess.py:132-155, 1996-2003`]:
  1. `item.stat().st_size` for three source inputs (`:14-16`) and the artifact (`:47`), formatted by `json.dumps` at
     `:33-35` and `:50-51`. CPython builds these from the platform `off_t`, which on this aarch64 glibc is the 64-bit
     `__SLONGWORD_TYPE` (`/usr/include/bits/typesizes.h:41`). Hence `|v| <= 2**63 - 1 < 10**19` [K-11, K-94]: at
     most 19 digits [K-95], 621 digits inside the minimum limit [K-96].
  2. `compilerReturncode` (`child.returncode`) at `:48`, which is 0 wherever it is serialized, because `:37-38` exit
     on any nonzero code.
  3. **(new in v5)** `subprocess.run([... '/usr/bin/readelf' ...], env=environment, check=True)` at `:44-45` raises
     `CalledProcessError` on a nonzero readelf status. Uncaught, the interpreter prints its traceback, which calls
     `CalledProcessError.__str__` (`subprocess.py:145-155`): `"Command '%s' returned non-zero exit status %d."`, or
     for a negative code `"... died with %r."` (a `signal.Signals` member) or `"... died with unknown signal %d."`.
     `returncode` is set by `_handle_exitstatus` (`:1996-2003`) to `waitstatus_to_exitcode (sts)` (an exit status of
     0..255, or the negated terminating signal number) or to `-WSTOPSIG (sts)`. So `|returncode| ≤ 255 < 10**3`
     (`10**3 − 255 = 745` [K-240]): at most 3 digits, 637 inside the minimum limit [K-241].
  4. `SystemExit (child.returncode)` at `:37-38` hands an `int` exit status to the interpreter; no decimal text is
     produced from it by this script.
  5. **(new in v5)** Interpreter-generated text of any other uncaught exception, for example an `OSError` from
     `stat`, `read_bytes` or `mkdir` (`[Errno n] …`), and the traceback's line numbers. These integers come from C
     `int` values [LEAD], so `|v| ≤ 2**31 < 10**10` (`10**10 − 2**31 = 7852516352` [K-249]): at most 10 digits, 630
     inside the minimum limit [K-250].
  No decimal parse occurs in the file. Its four `str()` calls take `Path` objects (`:29, :31, :44, :46`). The
  `SystemExit` messages at `:11, :22, :24, :42` are literal strings. The bound holds under every admitted interpreter
  configuration, so the site needs neither routing nor configuration [LEAD; review required]. PY-10 probes items 1, 3
  and 5 (`DESIGN.md` §12.5).

Distinct `json.dumps` setting combinations an E2 serializer must reproduce in routed scopes (unchanged from v3; rows
193-194 add none new): (defaults); `indent=2`; `indent=2, sort_keys=True`; `indent=2, sort_keys=True,
ensure_ascii=False`; `ensure_ascii=False, indent=2`; `sort_keys=True`; `sort_keys=True, separators=(',', ':')`;
`sort_keys=True, separators=(',', ':'), allow_nan=False`; `sort_keys=True, separators=(',', ':'), ensure_ascii=True`;
`sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False`; `sort_keys=True, separators=(',', ':'),
ensure_ascii=False, allow_nan=False` (also in another keyword order); `ensure_ascii=True, sort_keys=True,
separators=(',', ':'), allow_nan=False`; `sort_keys=True, ensure_ascii=True`; `allow_nan=False`; `allow_nan=False,
separators=(',', ':')`. `json.loads` keyword sets: (defaults); `object_pairs_hook`; `object_pairs_hook` with
`parse_constant`; `object_pairs_hook` with `parse_constant` and `parse_float`. An E2 parser adds `parse_int` without
disturbing any of them.

**R-OVR condition 2 (V4-RC2 f).** No routed `json.dumps` site passes `default=` or `cls=`, and the census found no
forwarded `*args`/`**kwargs` (A.3). R-OVR's pre-scan is sound only while that remains true; PY-13 re-checks it on the
exact identity, and a site that gains `default`, `cls` or forwarded keywords suspends R-OVR there until it is
re-evaluated (`DESIGN.md` §11.4.2).

## A.6 Interpreter path used by each operation today [OBS installed stdlib]

- `json.dumps` builds `JSONEncoder(...).encode(o)`, which calls `iterencode(o, _one_shot=True)`. In Python 3.14 that
  selects the **C encoder** whenever `_json.make_encoder` exists, **including with `indent`**
  (`/usr/lib/python3.14/json/encoder.py:249-257`). The pure-Python `_make_iterencode` (`:265-454`) runs only for
  `iterencode` without `_one_shot`; `tests/diagnostic_value_stream.py:153` is an example.
- In the Python encoder, `sort_keys` sorts the **original** `(key, value)` items with `sorted(dct.items())` (`:357-358`)
  **before** key coercion (`:361-382`). Integer keys therefore sort numerically. Mixed incomparable keys raise
  `TypeError` from the sort, before any key is converted.
- `json.loads` with any non-default keyword constructs `cls(**kw).decode(s)` (`json/__init__.py:349-365`). The decoder
  stores `parse_int or int` (`decoder.py:329`) and uses `make_scanner = c_make_scanner or py_make_scanner`
  (`scanner.py:73`). Supplying `parse_int` keeps the C scanner.
- C-level recursion protection in 3.14 is stack-address based (`pycore_ceval.h:238-245`, `c_stack_soft_limit`). The
  Python frame limit is separate (`cpython/pystate.h:121-123`). The two encoders therefore have different depth
  thresholds [OBS headers; the C encoder's own guard code is not installed as source].

## A.7 ORIGINAL-TEST census (`tests/`, byte-identical original controls) [OBS census]

| File | Operations (inline) | File | Operations (inline) |
|---|---|---|---|
| `anchor_support.py` | 8 (0) | `test_owner_retry_audit.py` | 1 (0) |
| `diagnostic_value_stream.py` | 4 (0): 1 encoder instantiation, 3 instance calls | `test_owner_transitions.py` | 1 (0) |
| `freshness_support.py` | 14 (12) | `test_preflight.py` | 6 (0) |
| `native_lifetime_controls.py` | 11 (0) | `test_private_benchmark.py` | 8 (3) |
| `native_workload_controls.py` | 4 (0) | `test_private_case_lease.py` | 3 (2) |
| `test_admission.py` | 3 (0) | `test_private_evaluator.py` | 4 (0) |
| `test_admission_regressions.py` | 2 (0) | `test_private_lease_fault_campaign.py` | 9 (1) |
| `test_agents.py` | 1 (0) | `test_private_lease_protocol_campaign.py` | 7 (5) |
| `test_anchor_rotation_control.py` | 2 (0) | `test_private_world_flow.py` | 1 (0) |
| `test_anchor_witness.py` | 2 (0) | `test_project.py` | 4 (0) |
| `test_boundaries.py` | 11 (1) | `test_proof_manifest_shapes.py` | 2 (0) |
| `test_client_content.py` | 2 (2) | `test_protected.py` | 1 (0) |
| `test_client_peer_producer.py` | 2 (0) | `test_prune_backups.py` | 1 (0) |
| `test_core_abi.py` | 2 (0) | `test_race.py` | 2 (1) |
| `test_diagnostic_value_stream.py` | 2 (0) | `test_raw_observation.py` | 5 (1) |
| `test_docker.py` | 3 (0) | `test_release_gate.py` | 5 (0) |
| `test_e2e.py` | 4 (1) | `test_release_pair_report.py` | 1 (0) |
| `test_engine_code_inventory.py` | 1 (0) | `test_relocate.py` | 10 (0) |
| `test_evaluation_lifecycle_promotion.py` | 2 (0) | `test_reservation_lifecycle.py` | 1 (0) |
| `test_examiner_bound_loader.py` | 16 (2) | `test_resource_headroom.py` | 1 (0) |
| `test_examiner_entry_code.py` | 3 (0) | `test_resource_kernel.py` | 1 (0) |
| `test_examiner_entry_retention.py` | 6 (0) | `test_resource_ledger.py` | 2 (0) |
| `test_examiner_native_guard.py` | 6 (2) | `test_resource_policy.py` | 3 (0) |
| `test_finalization_kernel.py` | 2 (0) | `test_result_channel.py` | 1 (1) |
| `test_freshness.py` | 13 (0) | `test_resulting_requirement_caller.py` | 3 (0) |
| `test_install_config.py` | 2 (0) | `test_revalidation_binding.py` | 3 (0) |
| `test_lifecycle_integrity.py` | 13 (2) | `test_rollback.py` | 3 (0) |
| `test_namespace_lifetime.py` | 2 (0) | `test_root_resolution.py` | 1 (0) |
| `test_supervision.py` | 1 (0) | `test_tagged_object_cursor.py` | 4 (0) |
| `test_transaction.py` | 2 (0) | `test_typed_absence.py` | 12 (0) |
| `test_verification_reporting.py` | 2 (0) | | |

61 files, 254 operations, 36 inside parsed inline sources [K-85].

The 9 string constants that mention `json` but do not parse as Python are left for manual classification. All are
original-test text: `test_admission.py:108`, `test_boundaries.py:499`, `test_examiner_native_guard.py:538`,
`test_private_case_lease.py:28`, `test_private_lease_fault_campaign.py:114, :119, :281, :428`, and
`test_transaction.py:306`.

No WORLDLINE source mentions `int_max_str_digits`, `set_int_max_str_digits`, `PYTHONINTMAXSTRDIGITS` or the limit
message, and no Python file contains a decimal-literal fixture of thousands of digits [OBS literal search over C5]. No
original control is known to assert the interpreter limit, so E1/E2 are not known to contradict an original control
expectation. This is a literal-search observation, not a proof.

## A.8 Non-JSON decimal-conversion candidate universe (extended; classification OPEN)

Counts come from the same read-only scan, inline sources included. Each node is a **candidate**: a count does not show
that a workload-derived integer can reach it. The v3 rules reproduce v3's numbers. The runtime `int(x)` row counts
167 calls in 40 files, or 41 sources when the inline child source of `linux/netguard.py:39`, which contains one call,
is counted separately as v3 did.

| Directory | `int(x)` base 10, non-literal | `str(x)`, non-literal | `repr(x)` | `format(x)` | f-string fields | `%` format | lazy `logging` `%` with args | `.format()` non-literal |
|---|---|---|---|---|---|---|---|---|
| `runtime/` (121) | 167 in 40 | 582 in 73 | 22 in 8 | 0 | 1017 in 61 | 1 in 1 | 19 in 6 | 0 |
| `protected-resource/` (4) | 0 | 15 in 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `protected-startup/` (5) | 0 | 28 in 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `protected-runtime/` (2) | 0 | 2 in 1 | 0 | 1 in 1 | 0 | 0 | 0 | 0 |
| `native/` (1) | 0 | 4 in 1 (all `Path`) | 0 | 0 | 0 | 0 | 0 | 0 |
| `scripts/` (14) | 2 in 1 | 56 in 10 | 0 | 0 | 231 in 12 | 0 | 0 | 0 |
| `cli/` (2 scripts) | 0 | 2 in 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `daemon/` (1 script) | 0 | 1 in 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| repository root (2) | 0 | 4 in 2 | 0 | 0 | 7 in 1 | 0 | 0 | 0 |
| `protected-lab/` (2) | 0 | 2 in 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `tests/` (146, original) | 34 in 18 | 785 in 105 | 34 in 16 | 0 | 244 in 51 | 11 in 4 | 0 | 3 in 2 |

Categories enumerated in v4, which v3 listed as uncounted:

- **Stdlib text parsers with an internal decimal conversion** (11 sites [K-90]):
  - `tomllib.loads` at `runtime/worldline/environment.py:217` (`Cargo.toml`) and `:236` (`pyproject.toml`) of the
    captured workspace. TOML integers are converted by `int(match.group(), 0)` (`/usr/lib/python3.14/tomllib/_re.py:110-113`).
    `tomllib` offers no integer hook, only `parse_float`. A workspace file with a long decimal integer anywhere fails
    the whole parse. **E2 cannot route these sites with a hook** (`DESIGN.md` §11.4.5, E2-T).
  - `ast.literal_eval` at `refresh_contract_pins.py:30` and `runtime/worldline/examiner_audit.py:403`. The latter
    catches `ValueError` and marks the export dynamic.
  - `argparse` `type=int` at `runtime/worldline/cli_main.py:371, 380, 414, 415`, `scripts/prune_backups.py:47` and
    `scripts/release_gate.py:226, 227`. These parse operator command-line text with `int()`'s full base-10 grammar.
- **Python-source compilation of decimal literals** (14 calls [K-190]):
  - `ast.parse` at `refresh_contract_pins.py:23, 55`, `scripts/engine_codes.py:47`,
    `runtime/worldline/examiner_audit.py:382, 459` and `runtime/worldline/executed.py:369`;
  - `compile` at `runtime/worldline/linux/private_evaluator.py:342, 367, 814`;
  - `exec` at `private_evaluator.py:383, 814, 849`. Two further `exec` calls are in the original control campaigns,
    `protected-resource/controls/run_campaign.py:130` and `protected-startup/controls/run_campaign.py:153`.
- **`decimal`**: `Decimal(str(value[...]))` at `runtime/worldline/checks.py:888-889` formats a JSON-parsed benchmark
  number with `str()` before `Decimal` parses it. The `str()` of a workload integer is a formatting candidate that
  must be routed or bounded. `Decimal(100)` at `:899` is a literal.
- **Excluded by rule:** `int(x, 16)` and `int(x, 8)` (15 sites in `runtime/` and `protected-runtime/`), `hex`/`oct`/
  `bin`, and `int.to_bytes`/`int.from_bytes`. They use power-of-two bases, outside Python's limit [DOC].

Categories still not enumerated (O-PY-AUDIT):

- `int.__format__` reached through other formatting paths;
- `print` of integers through `%`/f-strings already counted;
- interpreter-generated exception and traceback text in processes other than C12 (v5 inventoried it for C12 only,
  A.5 rows 160-162 item 5);
- third-party serializers (none are imported by C5 production code [OBS census, OTHER-LIBRARY = 0]).

## A.9 Interpreter entries (E1 coverage map)

Every interpreter that executes a routed-scope operation belongs to one class of `DESIGN.md` §11.3:

| Classes | Interpreters |
|---|---|
| C1 to C11 | as in v3 |
| C12 | `native/build_guard.py`, the Root native-build action (reviewed bound over the five-item inventory of A.5 rows 160-162; no change needed) |
| C13 | `refresh_contract_pins.py` and `verify_proof_manifest.py`, developer, CI and release tools |
| C14 | original test runners: unchanged, and not configured by E1 |

The examiner restoration (C6) and the candidate payloads (C7) are as in v3.

_End of Appendix A._
