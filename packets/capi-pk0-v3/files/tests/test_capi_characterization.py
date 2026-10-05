"""PK-0: original-behaviour characterization of the moving C-API exports.

Packet PK-0 of the C-API boundary design: packet table v3 DESIGN.md section 9.2; the
specification is v4 DESIGN.md section 9.6, carried unchanged into the endorsed v6. Revision
v3 answers review packets/capi-pk0-v2/review/claude-v1 (RC-v2-1 to RC-v2-4), on top of v2's
answers to packets/capi-pk0/review/gpt61-v1 (PK0-RC1 to PK0-RC5). Controls carried here
in baseline form: C-01, C-02, C-03, C-04, C-05, C-11, C-15 and C-16. C-06 is in
test_capi_diagnostics.py; C-07 and C-13 are in test_capi_layout_identity.py. C-12 is optional
and is not authored in PK-0. C-14 is proposed behaviour and is never a PK-0 pass condition.

The record is tests/capi_characterization.json. Each case there names a builder below, the
mutations that move the built call into one input class, optional guard placement (C-05) and
the defined effect. This module builds, calls and compares; it decides nothing itself.

* It asserts the ORIGINAL behaviour, including behaviour that is a defect. A baseline defect
  stays an original obligation: PK-0 cannot delete or redefine it.
* A class-H code is never an accepted semantic refusal, and no case asserts class H.
* Nothing is asserted for class X (foreign faults, violated documented premises).
* An expectation written RECORD_ON_L0 is a placeholder. It never passes. The case fails until a
  baseline run on L0, in an admitted frame, records the observed value through a reviewed
  change to the JSON. `--record` prints the observed values of placeholder cases as JSON on
  standard output. It writes no file and compiles nothing. Before importing anything outside
  the standard library, it refuses to start unless the interpreter was launched with
  bytecode writing disabled (-B or PYTHONDONTWRITEBYTECODE) (RC-v2-3).

Process boundary, as it actually is (PK0-RC5):

* Importing this module imports capi_guard_pages (which loads libc) and the runtime ctypes
  modules listed below. Importing a component module does not run its kernel constructor, so
  no layout check of pending, completion, finalization or recovery happens at import; Core
  validates only its own _LAYOUTS, when setUpClass constructs it.
* setUpClass constructs Core in the parent: the native library is loaded and its runtime
  initialized there, outside any fork.
* Each case's decision call, its relational oracle, its readiness probe and its guard pages
  run in a forked child (capi_guard_pages.run_forked) under the fatal-fault policy of that
  module (PK0-RC3); the parent requires a normal exit before it uses the report. Builders
  other than the child-only builders run in the parent before the fork; of them, b_chain
  calls the native hash exports Core.hash_bytes and Core.receipt_link there. The child-only
  builders (CHILD_BUILDERS) construct their inputs with the S5 runtime producers and S5 test
  fixtures, which call native exports; they run inside the child only.
* No deadline is set anywhere. A hung child blocks the parent. Supervision is a property the
  admitted launch must supply and evidence; it is not provided by this file.

The library is chosen the S5 way: Core(Path(os.environ['WORLDLINE_CORE_LIB'])). Exported
functions are fetched with core._lib[name], which returns a fresh function pointer, so this
module never changes argtypes that a runtime binding has set on the shared attributes.
"""
from __future__ import annotations

import ctypes as C
import dataclasses
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path


def require_output_only_launch():
    """--record writes no file (PK0-RC2): refuse unless the launch disabled bytecode writing."""
    if not sys.flags.dont_write_bytecode:
        sys.stderr.write("--record refused: launch the interpreter with -B or "
                         "PYTHONDONTWRITEBYTECODE=1 so that no bytecode file is written\n")
        sys.exit(2)


# RC-v2-3: the refusal precedes every import outside the standard library (below).
if __name__ == "__main__" and "--record" in sys.argv[1:]:
    require_output_only_launch()

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import capi_guard_pages as G  # noqa: E402
from worldline import chain_authority as CH  # noqa: E402
from worldline import completion_kernel as CK  # noqa: E402
from worldline import evaluation_context as EC  # noqa: E402
from worldline import evaluation_history as EH  # noqa: E402
from worldline import evaluation_wire as EW  # noqa: E402
from worldline import finalization_kernel as FK  # noqa: E402
from worldline import pending_kernel as PK1  # noqa: E402
from worldline import pending_kernel_v2 as PK2  # noqa: E402
from worldline import recovery_authority_kernel as RA2  # noqa: E402
from worldline import recovery_authority_kernel_v3 as RA3  # noqa: E402
from worldline import recovery_protocol_kernel as RP  # noqa: E402
from worldline import reservation_lifecycle as RL  # noqa: E402
from worldline import resource_ledger as LG  # noqa: E402
from worldline import resource_policy as PO  # noqa: E402
from worldline import resource_run_ledger as RR  # noqa: E402
from worldline.core import C_HASH, CCollapseRequest, COptionalHash, Core, HASH_BYTES  # noqa: E402
from worldline.core import EVALUATION_ORIGINS  # noqa: E402

RECORD_PATH = HERE / "capi_characterization.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
PLACEHOLDER = RECORD["placeholder_token"]
CONSTANTS = {name: entry["value"] for name, entry in RECORD["constants"].items()}

P, SZ, U8, U32, I64, INT, LONG = (C.c_void_p, C.c_size_t, C.c_uint8, C.c_uint32,
                                  C.c_int64, C.c_int, C.c_long)

# C signatures, transcribed from the S5 Ada specifications (External_Name declarations).
SIGNATURES = {
    "wl_resources_can_reserve": (U8, [
        ("available_negative", U8), ("available", P), ("available_length", SZ),
        ("withheld", P), ("withheld_length", SZ), ("floor", P), ("floor_length", SZ),
        ("requested", P), ("requested_length", SZ)]),
    "wl_recovery_select": (U8, [
        ("expected", P), ("expected_length", SZ), ("live_present", U8), ("live", P),
        ("live_length", SZ), ("prepared_present", U8), ("prepared", P), ("prepared_length", SZ)]),
    "wl_recovery_authorization_decide_v2": (INT, [
        ("input", P), ("input_length", SZ), ("output", P), ("output_length", SZ)]),
    "wl_recovery_authorization_decide_v3": (INT, [
        ("input", P), ("input_length", SZ), ("arena", P), ("arena_length", SZ),
        ("output", P), ("output_length", SZ)]),
    "wl_recovery_protocol_decide_v1": (INT, [
        ("input", P), ("input_length", SZ), ("output", P), ("output_length", SZ)]),
    "wl_reservation_lifecycle_plan": (U8, [
        ("data", P), ("data_length", SZ), ("rows", P), ("row_count", SZ), ("mode", U8),
        ("present", U8), ("requested_first", SZ), ("requested_length", SZ),
        ("removed", P), ("removed_length", SZ)]),
    "wl_resource_ledger_compute": (U8, [
        ("data", P), ("data_length", SZ), ("rows", P), ("row_count", SZ),
        ("detail_data", P), ("detail_length", SZ), ("total_data", P), ("total_length", SZ),
        ("details", P), ("result", P)]),
    "wl_resource_ledger_headroom": (U8, [
        ("data", P), ("data_length", SZ), ("available", P), ("withheld", P), ("floor", P),
        ("output", P), ("output_length", SZ), ("result", P)]),
    "wl_resource_policy_admit": (U8, [
        ("data", P), ("data_length", SZ), ("input", P), ("disks", P), ("disk_count", SZ),
        ("result", P)]),
    "wl_evaluation_history_select": (U8, [
        ("data", P), ("data_length", SZ), ("rows", P), ("row_count", SZ),
        ("final_present", U8), ("final_row", P), ("query", P), ("output", P)]),
    "wl_pending_decide_v1": (INT, [("input", P), ("output", P)]),
    "wl_pending_decide_v2": (INT, [("input", P), ("output", P)]),
    "wl_resource_run_ledger_check_v1": (INT, [
        ("input", P), ("input_length", SZ), ("arena", P), ("arena_length", SZ),
        ("before", P), ("before_count", SZ), ("proposed", P), ("proposed_count", SZ),
        ("native", P), ("native_count", SZ), ("output", P), ("output_length", SZ)]),
    "wl_chain_authority_replay_v1": (INT, [
        ("anchors", P), ("anchors_length", SZ), ("rows", P), ("rows_count", SZ),
        ("rows_length", SZ), ("output", P), ("output_length", SZ)]),
    "wl_completion_decide_v1": (INT, [("input", P), ("output", P)]),
    "wl_completion_raw_decide_v1": (INT, [
        ("input", P), ("raw_rows", P), ("confinements", P), ("output", P)]),
    "wl_completion_metadata_matches_v1": (INT, [("input", P), ("context", P)]),
    "wl_finalization_decide_v1": (INT, [("input", P), ("output", P)]),
    "wl_collapse_decide_finalization_v1": (U8, [
        ("collapse", P), ("primary_kind", U32), ("primary", P), ("primary_raw", P),
        ("primary_confinement", P), ("primary_context", P), ("staged_kind", U32),
        ("staged", P), ("staged_raw", P), ("staged_confinement", P), ("staged_context", P),
        ("agent", P), ("agent_confinement", U8)]),
}

# Layout queries used to compute "count beyond the stride limit" arguments at run time.
LAYOUT_QUERIES = {
    "wl_reservation_lifecycle_row_size": (SZ, []),
    "wl_resource_ledger_layout_size": (SZ, [U8]),
    "wl_resource_policy_layout_size": (SZ, [U8]),
    "wl_evaluation_history_layout_size": (SZ, [U8]),
    "wl_pending_layout_size_v1": (I64, [U32]),
    "wl_pending_layout_size_v2": (I64, [U32]),
    "wl_completion_layout_size_v1": (I64, [U32]),
    "wl_resource_run_ledger_layout_v1": (LONG, [U32, U32]),
    "wl_chain_authority_layout_v1": (LONG, [U32, U32]),
    "wl_finalization_layout_v1": (I64, [U32, U32]),
}

# Declaration orders read from S5 (positions are the tuple indexes).
LEDGER_STATUS = ("COMPUTED", "INVALID_INPUT", "INVALID_OUTPUT_LAYOUT", "INSUFFICIENT_STORAGE")
ENUMS = {
    "v2.action": RA2.ACTIONS, "v2.state": RA2.STATES,
    "v3.action": RA3.ACTIONS, "v3.state": RA3.STATES,
    "protocol.state": RP.STATES,
    "pending_v1.reason": PK1.Reason, "pending_v2.reason": PK2.Reason,
    "ledger.status": LEDGER_STATUS,
    "policy.status": PO._STATUS, "policy.gate": PO._GATES, "policy.field": PO._FIELDS,
    "history.reason": EH.REASONS, "history.source": EH.SOURCES,
    "run_ledger.status": RR.STATUS,
    "chain.disposition": CH.REASONS,
    "completion.reason": CK.REASONS, "completion.execution": CK.EXECUTION,
    "completion.outcome": tuple("NO_OUTCOME" if item is None else item for item in CK.OUTCOME),
    "completion.history": CK.HISTORY,
}


def to(name, offset=0):
    return {"to": name, "offset": offset}


NULL = {"null": True}


def new_scenario(export):
    restype, args = SIGNATURES[export]
    scenario = G.Scenario(export, restype)
    for name, ctype in args:
        scenario.arg(name, ctype, None)
    return scenario


def as_bytes(value):
    """JSON spelling of bytes: a text string (latin-1 code points) or {"hex": "..."}."""
    if value is None:
        return None
    if isinstance(value, dict):
        return bytes.fromhex(value["hex"])
    return value.encode("latin-1")


def place_output(scenario, name, ctype):
    scenario.add(name, C.sizeof(ctype), align=C.alignment(ctype), init=False)
    scenario.set_arg(name, to(name))
    scenario.output("arg:" + name, ctype)


def place_array(scenario, name, array, element):
    scenario.add(name, array, align=C.alignment(element), elem=C.sizeof(element))


# ----------------------------------------------------------------------------- builders

def b_resources(core, available="0a", withheld="03", floor="02", requested="05",
                negative=0, null=()):
    s = new_scenario("wl_resources_can_reserve")
    s.set_arg("available_negative", negative)
    for name, value in (("available", available), ("withheld", withheld),
                        ("floor", floor), ("requested", requested)):
        data = bytes.fromhex(value)
        s.add(name, data)
        s.set_arg(name, NULL if name in null else to(name))
        s.set_arg(name + "_length", len(data))
    return s


def b_recovery(core, expected="616263", live="616263", prepared="78797a"):
    s = new_scenario("wl_recovery_select")
    data = bytes.fromhex(expected)
    s.add("expected", data)
    s.set_arg("expected", to("expected"))
    s.set_arg("expected_length", len(data))
    for name, value in (("live", live), ("prepared", prepared)):
        if value is None:
            s.set_arg(name + "_present", 0)
            s.set_arg(name, NULL)
            s.set_arg(name + "_length", 0)
        else:
            data = bytes.fromhex(value)
            s.add(name, data)
            s.set_arg(name + "_present", 1)
            s.set_arg(name, to(name))
            s.set_arg(name + "_length", len(data))
    return s


def _identity(label):
    # S5 tests/test_recovery_witness_relation.py:24-25 (and _v3.py:24-25).
    return hashlib.sha256(label.encode("ascii")).digest()


def _bound_use(module, **changes):
    # S5 tests/test_recovery_witness_relation.py:28-31 (and _v3.py:28-31).
    base = module.BoundUse(mode="CANDIDATE",
                           **{name: _identity(name) for name in module.HASH_FIELDS},
                           policy_epoch=0, resource_epoch=0)
    return dataclasses.replace(base, **changes)


def _native(module, issued, which):
    if which == "after":
        return module.NativeObservation(live_mapping=issued.staged_mapping,
                                        live_root=issued.staged_root)
    return module.NativeObservation(live_mapping=issued.before_mapping,
                                    live_root=issued.before_root)


def b_recovery_v2(core, state="ISSUED", fresh="AUTHORIZED", historical="UNESTABLISHED",
                  grant=True, native="before"):
    issued = _bound_use(RA2)
    kernel = RA2.RecoveryAuthorityKernel
    request = RA2.Request(RA2.STATES.index(state), RA2.FRESH.index(fresh),
                          RA2.HISTORICAL.index(historical), int(grant),
                          kernel._binding(issued), kernel._binding(issued),
                          kernel._native(_native(RA2, issued, native)))
    s = new_scenario("wl_recovery_authorization_decide_v2")
    s.add("input", request)
    s.set_arg("input", to("input"))
    s.set_arg("input_length", C.sizeof(request))
    place_output(s, "output", RA2.Result)
    s.set_arg("output_length", C.sizeof(RA2.Result))
    return s


def b_recovery_v3(core, state="ISSUED", fresh="AUTHORIZED", historical="UNESTABLISHED",
                  grant=True, native="before", policy_epoch=0, resource_epoch=0,
                  recovered_high_byte=None):
    issued = _bound_use(RA3, policy_epoch=policy_epoch, resource_epoch=resource_epoch)
    kernel = RA3.RecoveryAuthorityKernelV3
    arena = bytearray()
    issued_raw = kernel._binding(issued, arena)
    recovered_raw = kernel._binding(issued, arena)
    if recovered_high_byte is not None:
        # S5 tests/test_recovery_witness_relation_v3.py:256-258 and :279-281.
        raw = recovered_raw.resource_epoch
        arena[raw.first + raw.length - 2] = recovered_high_byte
    request = RA3.Request(3, RA3.STATES.index(state), RA3.FRESH.index(fresh),
                          RA3.HISTORICAL.index(historical), int(grant), issued_raw,
                          recovered_raw, kernel._native(_native(RA3, issued, native)))
    s = new_scenario("wl_recovery_authorization_decide_v3")
    s.add("input", request)
    s.set_arg("input", to("input"))
    s.set_arg("input_length", C.sizeof(request))
    s.add("arena", bytes(arena))
    s.set_arg("arena", to("arena"))
    s.set_arg("arena_length", len(arena))
    place_output(s, "output", RA3.Result)
    s.set_arg("output_length", C.sizeof(RA3.Result))
    return s


def b_protocol(core, before="ISSUED", cause="FRESH_CLAIM"):
    request = RP.Request(RP.STATES.index(before), RP.EVENTS.index(cause))
    s = new_scenario("wl_recovery_protocol_decide_v1")
    s.add("input", request)
    s.set_arg("input", to("input"))
    s.set_arg("input_length", C.sizeof(request))
    place_output(s, "output", RP.Result)
    s.set_arg("output_length", C.sizeof(RP.Result))
    return s


def b_lifecycle(core, data="61", rows=((1, 1, 2),), mode=2, present=0, first=0, length=0,
                mask="09"):
    s = new_scenario("wl_reservation_lifecycle_plan")
    arena = bytes.fromhex(data)
    s.add("data", arena)
    s.set_arg("data", to("data"))
    s.set_arg("data_length", len(arena))
    array = (RL._Row * len(rows))(*(RL._Row(*row) for row in rows))
    place_array(s, "rows", array, RL._Row)
    s.set_arg("rows", to("rows"))
    s.set_arg("row_count", len(rows))
    for name, value in (("mode", mode), ("present", present), ("requested_first", first),
                        ("requested_length", length)):
        s.set_arg(name, value)
    removed = bytes.fromhex(mask)
    s.add("removed", removed)
    s.set_arg("removed", to("removed"))
    s.set_arg("removed_length", len(removed))
    s.output("arg:removed", C.c_uint8 * len(removed))
    return s


def _ledger_optional(spec):
    if spec is None:
        return LG._Optional(0, LG._Quantity(1, 0, 0))
    return LG._Optional(1, LG._Quantity(*spec))


def b_ledger(core, data="03", rows=(((1, 1, 0), None, 1, 2),), detail_length=2,
             total_length=2):
    s = new_scenario("wl_resource_ledger_compute")
    arena = bytes.fromhex(data)
    s.add("data", arena)
    s.set_arg("data", to("data"))
    s.set_arg("data_length", len(arena))
    array = (LG._Row * len(rows))(*(
        LG._Row(LG._Quantity(*reserved), _ledger_optional(used), first, length)
        for reserved, used, first, length in rows))
    place_array(s, "rows", array, LG._Row)
    s.set_arg("rows", to("rows"))
    s.set_arg("row_count", len(rows))
    for name, size in (("detail_data", detail_length), ("total_data", total_length)):
        s.add(name, size, init=False)
        s.set_arg(name, to(name))
        s.output("arg:" + name, C.c_uint8 * size)
    s.set_arg("detail_length", detail_length)
    s.set_arg("total_length", total_length)
    place_output(s, "details", LG._Quantity * len(rows))
    s.objects["details"].align = C.alignment(LG._Quantity)
    place_output(s, "result", LG._Result)
    return s


def b_headroom(core, data="0a0302", available=(1, 1, 0), withheld=(2, 1, 0),
               floor=(3, 1, 0), output_length=2):
    s = new_scenario("wl_resource_ledger_headroom")
    arena = bytes.fromhex(data)
    s.add("data", arena)
    s.set_arg("data", to("data"))
    s.set_arg("data_length", len(arena))
    for name, spec in (("available", available), ("withheld", withheld), ("floor", floor)):
        s.add(name, LG._Quantity(*spec))
        s.set_arg(name, to(name))
    s.add("output", output_length, init=False)
    s.set_arg("output", to("output"))
    s.set_arg("output_length", output_length)
    s.output("arg:output", C.c_uint8 * output_length)
    place_output(s, "result", LG._Result)
    return s


def b_policy(core, outstanding_count=0, concurrency_limit=None, memory_pressure=None,
             memory_pressure_ceiling=2, disks=(), disk_byte_floor=2, disk_inode_floor=2,
             available_memory=10, withheld_memory=3, memory_floor=2, requested_memory=5):
    # Packing mirrors S5 runtime/worldline/resource_policy.py:146-162; the S5 test base
    # values are tests/test_resource_policy.py:42-49.
    arena = bytearray()

    def quantity(value):
        magnitude = abs(value)
        raw = magnitude.to_bytes((magnitude.bit_length() + 7) // 8, "little")
        item = PO._Quantity(len(arena) + 1 if raw else 1, len(raw), int(value < 0))
        arena.extend(raw)
        return item

    def optional(value):
        return PO._Optional(0, PO._Quantity()) if value is None else PO._Optional(1, quantity(value))

    inputs = PO._Input(quantity(outstanding_count), optional(concurrency_limit),
                       optional(memory_pressure), quantity(memory_pressure_ceiling),
                       quantity(disk_byte_floor), quantity(disk_inode_floor),
                       quantity(available_memory), quantity(withheld_memory),
                       quantity(memory_floor), quantity(requested_memory))
    disk_values = (PO._Disk * len(disks))(*(PO._Disk(quantity(b), quantity(i)) for b, i in disks))
    s = new_scenario("wl_resource_policy_admit")
    s.add("data", bytes(arena))
    s.set_arg("data", to("data"))
    s.set_arg("data_length", len(arena))
    s.add("input", inputs)
    s.set_arg("input", to("input"))
    place_array(s, "disks", disk_values, PO._Disk)
    s.set_arg("disks", to("disks"))
    s.set_arg("disk_count", len(disks))
    place_output(s, "result", PO._Result)
    return s


def b_history(core, history=(), final=("subject", "content", "policy", "final-run", 0,
                                        "COMPLETED", "PASS"),
              query=("subject", "content", "policy", (0, "final-run"), (0, "final-run"))):
    # Packing mirrors S5 runtime/worldline/evaluation_history.py:148-185.
    arena = bytearray()

    def identity(value):
        if value is None:
            return EH._Identity(0, 0, 0)
        encoded = value.encode("utf-8", "surrogatepass")
        first = len(arena) + 1
        arena.extend(encoded)
        return EH._Identity(1, first, len(encoded))

    def epoch(value):
        if value is None:
            return EH._Epoch(0, 0, 0)
        encoded = value.to_bytes((value.bit_length() + 7) // 8, "little")
        first = len(arena) + 1
        arena.extend(encoded)
        return EH._Epoch(1, first, len(encoded))

    def cursor(value):
        if value is None:
            return EH._Cursor()
        return EH._Cursor(1, epoch(value[0]), identity(value[1]))

    def row(value):
        subject, content, requirement, run, sequence, state, outcome = value
        return EH._Row(identity(subject), identity(content), identity(requirement),
                       identity(run), epoch(sequence), EH.STATES.index(state),
                       EH.OUTCOMES.index(outcome))

    rows = (EH._Row * len(history))(*(row(value) for value in history))
    final_row = EH._Row() if final is None else row(final)
    packed_query = EH._Query(identity(query[0]), identity(query[1]), identity(query[2]),
                             cursor(query[3]), cursor(query[4]))
    s = new_scenario("wl_evaluation_history_select")
    s.add("data", bytes(arena))
    s.set_arg("data", to("data"))
    s.set_arg("data_length", len(arena))
    place_array(s, "rows", rows, EH._Row)
    s.set_arg("rows", to("rows"))
    s.set_arg("row_count", len(history))
    s.set_arg("final_present", 0 if final is None else 1)
    s.add("final_row", final_row)
    s.set_arg("final_row", to("final_row"))
    s.add("query", packed_query)
    s.set_arg("query", to("query"))
    place_output(s, "output", EH._Selection)
    return s


def _pending(module, version, rows, store, subject, content, run, authority, target,
             proposed, replay, requirement, with_requirement):
    # Packing order mirrors S5 runtime/worldline/pending_kernel.py:129-163 and
    # pending_kernel_v2.py:135-175.
    arena = bytearray()
    labels = {}

    def span(value, label=None):
        value = as_bytes(value)
        start = len(arena) + 1
        arena.extend(value)
        if label:
            labels[label] = (start, len(value))
        return module.Span(start, len(value))

    def cursor(value):
        if value is None:
            return module.Cursor(0, module.Span(1, 0), module.Span(1, 0))
        return module.Cursor(1, span(value[0]), span(value[1]))

    def optional(value, label):
        if value is None:
            return module.OptionalRequirement(0, module.Span(1, 0))
        return module.OptionalRequirement(1, span(value, label))

    wire = (module.Row * len(rows))()
    for index, row in enumerate(rows, 1):
        fields = [span(row[0]), span(row[1]), span(row[2]), span(row[3]),
                  span(row[4], f"row{index}.epoch"), cursor(row[5]), int(row[6])]
        if with_requirement:
            fields.append(optional(row[7], f"row{index}.requirement"))
        wire[index - 1] = module.Row(*fields)
    heads = [span(store), span(subject), span(content), span(run), span(proposed, "proposed"),
             cursor(authority), cursor(target)]
    if with_requirement:
        heads.append(optional(requirement, "required"))
    request = module.Request(version, int(replay), None, 0, None, len(rows), *heads)
    request.data_length = len(arena)
    s = new_scenario("wl_pending_decide_v2" if with_requirement else "wl_pending_decide_v1")
    s.labels.update(labels)
    s.add("input", request)
    s.set_arg("input", to("input"))
    s.add("data", bytes(arena))
    s.slot("input.data", to("data"))
    place_array(s, "rows", wire, module.Row)
    s.slot("input.rows", to("rows"))
    place_output(s, "output", module.Result)
    return s


def b_pending_v1(core, rows=(), store="", subject="", content="", run="", authority=None,
                 target=None, proposed="\u0001", replay=False):
    return _pending(PK1, 1, rows, store, subject, content, run, authority, target,
                    proposed, replay, None, False)


def b_pending_v2(core, rows=(), store="", subject="", content="", run="", authority=None,
                 target=None, proposed="\u0001", replay=False, requirement=None):
    return _pending(PK2, 2, rows, store, subject, content, run, authority, target,
                    proposed, replay, requirement, True)


def _run_ledger_material(case):
    # S5 tests/test_resource_run_ledger_v1.py:22-50 (helpers) and :59-69 (cases).
    scope = RR.RunContext(universe=b"universe", policy=b"policy", resource=b"memory",
                          unit=b"bytes", instance=b"instance", host=b"host", boot=b"boot",
                          authority=b"authority", policy_epoch=0)

    def row(name=b"row", *, epoch=0, amount=10, parent=None, kind="HELD_CAPACITY",
            state="RESERVED", effect=False):
        bound = RR.RunBinding(reservation=name, operation=b"op-" + name, owner=b"owner",
                              workload=b"work-" + name, universe_head=b"universe-head",
                              capability=b"cap-" + name, grant_use=b"use-" + name,
                              payload=b"payload-" + name, provenance=b"origin-" + name,
                              resource_epoch=epoch)
        unit = b"worldline-" + name + b".service"
        return RR.RunRow(scope=scope, bound=bound, parent=parent, kind=kind, state=state,
                         amount=amount, observed_usage=None,
                         planned_unit=unit if state != "RESERVED" else None,
                         actual_unit=unit if effect else None,
                         cgroup=b"/owned/" + name if effect else None,
                         invocation=b"invoke-" + name if effect else None)

    def state(epoch, *, held=0, charged=0, capacity=20, head=None):
        return RR.RunState(scope=scope, resource_epoch=epoch, universe_head=b"universe-head",
                           ledger_head=head or ("head-" + str(epoch)).encode(),
                           capacity=capacity, held_total=held, charged_total=charged)

    def observation(item, epoch, live="UNKNOWN"):
        return RR.RunObservation(scope=scope, resource_epoch=epoch, bound=item.bound,
                                 actual_unit=item.actual_unit, cgroup=item.cgroup,
                                 invocation=item.invocation,
                                 observation_head=b"native-observation", observed=live)

    def request(before, item):
        return RR.RunRequest(kind="RESERVE", scope=scope, expected_epoch=before.resource_epoch,
                             expected_ledger_head=before.ledger_head, request_id=b"request",
                             reservation=item.bound.reservation,
                             operation_id=item.bound.operation, requester=item.bound.owner,
                             bound=item.bound, new_row=item)

    if case == "genesis":
        before, first = state(0), row()
        return before, (), state(1, held=10), (first,), (), request(before, first)
    if case == "absent_epoch":
        before, first = state(None), row()
        return before, (), state(1, held=10), (first,), (), request(before, first)
    if case == "projected":
        one, two = row(b"one"), row(b"two", epoch=1)
        before = state(1, held=10)
        return (before, (one,), state(2, held=20), (one, two), (observation(one, 1),),
                request(before, two))
    raise KeyError(case)


def b_run_ledger(core, case="genesis"):
    before, before_rows, proposed, proposed_rows, observed, req = _run_ledger_material(case)
    # Packing mirrors S5 runtime/worldline/resource_run_ledger.py:228-240.
    arena = bytearray()
    intent = RR._marshal("Request", req, arena)
    if req.new_row is None:
        intent.new_row = RR._unused_row()
    packet = RR.RawPacket(1, RR._marshal("State", before, arena),
                          RR._marshal("State", proposed, arena), intent)
    raw_before = (RR.RawRow * len(before_rows))(*(RR._marshal("Row", r, arena) for r in before_rows))
    raw_proposed = (RR.RawRow * len(proposed_rows))(*(RR._marshal("Row", r, arena) for r in proposed_rows))
    raw_native = (RR.RawNative * len(observed))(*(RR._marshal("Native", r, arena) for r in observed))
    s = new_scenario("wl_resource_run_ledger_check_v1")
    s.add("input", packet)
    s.set_arg("input", to("input"))
    s.set_arg("input_length", C.sizeof(packet))
    s.add("arena", bytes(arena))
    s.set_arg("arena", to("arena"))
    s.set_arg("arena_length", len(arena))
    for name, array, element in (("before", raw_before, RR.RawRow),
                                 ("proposed", raw_proposed, RR.RawRow),
                                 ("native", raw_native, RR.RawNative)):
        place_array(s, name, array, element)
        s.set_arg(name, to(name))
        s.set_arg(name + "_count", len(array))
    place_output(s, "output", RR.RawResult)
    s.set_arg("output_length", C.sizeof(RR.RawResult))
    return s


def b_chain(core, case="empty"):
    genesis = bytes(HASH_BYTES)
    if case == "full":
        # S5 tests/test_chain_authority_native.py:15-23 (RECEIPT material).
        first_root = core.hash_bytes(b"first canonical control payload")
        first_head = core.receipt_link(genesis, first_root)
        second_root = core.hash_bytes(b"second canonical control payload")
        second_head = core.receipt_link(first_head, second_root)
        rows = [CH.ChainRow(genesis, first_root, first_root, first_head),
                CH.ChainRow(first_head, second_root, second_root, second_head)]
        anchors = CH.ChainAnchors("RECEIPT", genesis, genesis, second_head)
    else:
        rows = []
        anchors = CH.ChainAnchors("RECEIPT", genesis, genesis, genesis)
    owned_rows = (CH._Row * len(rows))(*(
        CH._Row(*(CH._digest(getattr(row, name)) for name, _ in CH._Row._fields_)) for row in rows))
    owned_anchors = CH._Anchors(CH.KINDS.index(anchors.kind), CH._digest(anchors.observed_genesis),
                                CH._digest(anchors.witnessed_genesis),
                                CH._digest(anchors.witnessed_head))
    s = new_scenario("wl_chain_authority_replay_v1")
    s.add("anchors", owned_anchors)
    s.set_arg("anchors", to("anchors"))
    s.set_arg("anchors_length", C.sizeof(owned_anchors))
    place_array(s, "rows", owned_rows, CH._Row)
    s.set_arg("rows", to("rows"))
    s.set_arg("rows_count", len(rows))
    s.set_arg("rows_length", C.sizeof(owned_rows))
    place_output(s, "output", CH._Result)
    s.set_arg("output_length", C.sizeof(CH._Result))
    s.values["genesis"] = genesis
    s.values["witnessed_head"] = anchors.witnessed_head
    return s


# Completion identities: S5 tests/test_evaluation_roster_d2.py:30-36.
BOUND = (("store_id", b"store"), ("subject", b"world"), ("content", b"content"),
         ("run", b"run"), ("sequence", b"\x01"), ("requirement", b"requirement"))
EMPTY = (1, 0)


class Packer:
    """A one-based byte arena with named spans."""

    def __init__(self):
        self.data = bytearray()
        self.labels = {}

    def span(self, value, label=None):
        first = len(self.data) + 1
        self.data += value
        if label:
            self.labels[label] = (first, len(value))
        return first, len(value)


def _cspan(pair):
    return CK.Span(*pair)


def _copt(pair):
    return CK.Optional_Span(0, CK.Span(*EMPTY)) if pair is None else CK.Optional_Span(1, CK.Span(*pair))


def _structural_binding():
    return CK.Binding(*(CK.Span(*EMPTY) for _ in range(5)), _copt(None))


def _structural_check_row():
    return CK.Check_Row(_structural_binding(), CK.Span(*EMPTY), CK.Span(*EMPTY), _copt(None),
                        _copt(None), 0, 0, CK.Span(*EMPTY), CK.Facts(), 0, CK.Presence(),
                        CK.Span(*EMPTY))


def _completion_parts(prefix, operation, state, outcome, current, retained, history,
                      captured, retained_rows, required, capture_store_first,
                      before_root_first, observed_subject, journal_rows):
    p = Packer()
    journal_spans = {name: p.span(value, f"{prefix}j.{name}") for name, value in BOUND}
    capture_spans = {name: p.span(value, f"{prefix}cap.{name}") for name, value in BOUND}
    cursor_sequence = p.span(b"\x01", f"{prefix}cur.sequence")
    cursor_run = p.span(b"run", f"{prefix}cur.run")
    source = p.span(b"owned-test-input", f"{prefix}source")
    context = p.span(b"context-input", f"{prefix}context")
    history_spans = []
    for index in range(1, len(history) + 1):
        history_spans.append({name: p.span(value, f"{prefix}h{index}.{name}")
                              for name, value in BOUND if name != "store_id"})
    observed = None if observed_subject is None else p.span(observed_subject.encode("latin-1"))
    data = bytes(p.data)

    def binding(spans, subject=None):
        return CK.Binding(_cspan(spans["store_id"]), _cspan(subject or spans["subject"]),
                          _cspan(spans["content"]), _cspan(spans["run"]),
                          _cspan(spans["sequence"]), _copt(spans["requirement"]))

    journal = (CK.Journal_Row * journal_rows)(*(
        CK.Journal_Row(binding(journal_spans), CK.Cursor(0, CK.Span(*EMPTY), CK.Span(*EMPTY)), 1)
        for _ in range(journal_rows)))
    capture = CK.Capture(binding(capture_spans), _cspan(source), _cspan(context),
                         CK.EXECUTION.index(state), CK.OUTCOME.index(outcome))
    if capture_store_first is not None:
        capture.bound.store_id.first = capture_store_first
    if current == "head":
        cursor = CK.Cursor(1, _cspan(cursor_sequence), _cspan(cursor_run))
    else:
        cursor = CK.Cursor(0, CK.Span(*EMPTY), CK.Span(*EMPTY))
    retained_record = (CK.Capture.from_buffer_copy(bytes(capture)) if retained == "same"
                       else CK.Capture())
    history_rows = (CK.History_Row * len(history))()
    for index, (row_state, row_outcome) in enumerate(history):
        spans = history_spans[index]
        history_rows[index] = CK.History_Row(
            _copt(spans["subject"]), _copt(spans["content"]), _copt(spans["requirement"]),
            _copt(spans["run"]), _copt(spans["sequence"]), CK.HISTORY.index(row_state),
            CK.OUTCOME.index(row_outcome))
    checks = (CK.Check_Row * captured)(*(_structural_check_row() for _ in range(captured)))
    retained_checks = (CK.Check_Row * retained_rows)(*(
        _structural_check_row() for _ in range(retained_rows)))
    plans = (CK.Required_Row * required)(*(
        CK.Required_Row(CK.Span(*EMPTY), CK.Span(*EMPTY)) for _ in range(required)))
    before_root = CK.Span(before_root_first, 1) if before_root_first is not None else CK.Span(*EMPTY)
    observed_binding = binding(capture_spans, observed)
    request = CK.Request(1, operation, None, len(data), None, journal_rows, cursor, capture,
                         None, captured, 1 if retained == "same" else 0, retained_record,
                         None, retained_rows, None, len(history), None, required, 0,
                         before_root, CK.Span(*EMPTY),
                         CK.Required_Row(CK.Span(*EMPTY), CK.Span(*EMPTY)), observed_binding)
    return data, request, journal, checks, retained_checks, history_rows, plans, p.labels


def _add_completion(s, prefix, parts):
    data, request, journal, checks, retained_checks, history_rows, plans, labels = parts
    s.labels.update(labels)
    s.add(prefix + "input", request)
    s.add(prefix + "data", data)
    s.slot(prefix + "input.data", to(prefix + "data"))
    for name, field, array, element in (
            ("journal", "journal", journal, CK.Journal_Row),
            ("captured", "captured_results", checks, CK.Check_Row),
            ("retained_rows", "retained_results", retained_checks, CK.Check_Row),
            ("history", "history", history_rows, CK.History_Row),
            ("required", "required", plans, CK.Required_Row)):
        place_array(s, prefix + name, array, element)
        s.slot(prefix + "input." + field, to(prefix + name))


def b_completion(core, raw=False, operation=0, state="Incomplete_Unknown", outcome=None,
                 current="head", retained=None, history=(), captured=0, retained_rows=0,
                 required=0, capture_store_first=None, before_root_first=None,
                 observed_subject=None, journal_rows=1):
    export = "wl_completion_raw_decide_v1" if raw else "wl_completion_decide_v1"
    s = new_scenario(export)
    parts = _completion_parts("", operation, state, outcome, current, retained,
                              [tuple(item) for item in history], captured, retained_rows,
                              required, capture_store_first, before_root_first,
                              observed_subject, journal_rows)
    _add_completion(s, "", parts)
    s.set_arg("input", to("input"))
    if raw:
        place_array(s, "raw_rows", (EW.Raw * captured)(), EW.Raw)
        s.set_arg("raw_rows", to("raw_rows"))
        s.add("confinements", bytes(captured), elem=1)
        s.set_arg("confinements", to("confinements"))
    place_output(s, "output", CK.Result)
    return s


def b_metadata(core, rows=0, original="c", owned="c", owned_execution=False, operation=0):
    left, right = bytearray(), bytearray()
    checks = (CK.Check_Row * rows)()
    metadata = (EC.MetadataRow * rows)()
    for index in range(rows):
        row = _structural_check_row()
        row.check_id = CK.Span(len(left) + 1, len(original))
        left += original.encode("latin-1")
        checks[index] = row
        metadata[index] = EC.MetadataRow(CK.Span(len(right) + 1, len(owned)), CK.Span(*EMPTY),
                                         CK.Span(*EMPTY), _copt(EMPTY if owned_execution else None),
                                         _copt(None))
        right += owned.encode("latin-1")
    request = CK.Request()
    request.version, request.operation = 1, operation
    request.data_length, request.captured_count = len(left), rows
    context = EC.MetadataContext(1, None, None, len(right), None, rows)
    s = new_scenario("wl_completion_metadata_matches_v1")
    s.add("input", request)
    s.set_arg("input", to("input"))
    s.add("data", bytes(left))
    s.slot("input.data", to("data"))
    place_array(s, "captured", checks, CK.Check_Row)
    s.slot("input.captured_results", to("captured"))
    s.add("context", context)
    s.set_arg("context", to("context"))
    s.add("meta_data", bytes(right))
    s.slot("context.data", to("meta_data"))
    place_array(s, "meta_rows", metadata, EC.MetadataRow)
    s.slot("context.rows", to("meta_rows"))
    return s


def _fin_start():
    return FK.Start(CK.Span(*EMPTY), CK.Span(*EMPTY), CK.Span(*EMPTY), CK.Span(*EMPTY),
                    _copt(None), CK.Span(*EMPTY), CK.Span(*EMPTY), CK.Span(*EMPTY),
                    FK.Digest(), FK.Digest(), FK.Digest(), CK.Span(*EMPTY), 0)


def _fin_row():
    return FK.Row(_fin_start(), CK.Span(*EMPTY), CK.Span(*EMPTY), _copt(None), _copt(None), 0, 0,
                  CK.Span(*EMPTY), CK.Span(*EMPTY), EW.Raw(), 0)


def _add_finalization(s, prefix, operation=0, rows=0, plans=0, rows_init=True,
                      start_store=None, parent_mismatch=False):
    start = _fin_start()
    if start_store is not None:
        start.store_id = CK.Span(*start_store)
    inputs = FK.Input(_fin_start(), CK.Span(*EMPTY), CK.Span(*EMPTY), FK.Digest(), FK.Digest(),
                      FK.Digest())
    if parent_mismatch:
        inputs.start.parent[0] = 1
    request = FK.Request(1, operation, None, 0, start, inputs, CK.Span(*EMPTY), CK.Span(*EMPTY),
                         None, rows, None, plans,
                         CK.Required_Row(CK.Span(*EMPTY), CK.Span(*EMPTY)), CK.Span(*EMPTY),
                         FK.Digest(), FK.Digest(), CK.Span(*EMPTY), CK.Span(*EMPTY),
                         CK.Span(*EMPTY), CK.Span(*EMPTY))
    s.add(prefix + "input", request)
    s.add(prefix + "data", b"")
    s.slot(prefix + "input.data", to(prefix + "data"))
    row_array = (FK.Row * rows)(*(_fin_row() for _ in range(rows)))
    if rows_init:
        place_array(s, prefix + "rows", row_array, FK.Row)
    else:
        # Rows that were never written: reading any of them would refuse (State 0xA5A5A5A5).
        s.add(prefix + "rows", C.sizeof(row_array), align=C.alignment(FK.Row),
              elem=C.sizeof(FK.Row), init=False)
    s.slot(prefix + "input.rows", to(prefix + "rows"))
    plan_array = (CK.Required_Row * plans)(*(
        CK.Required_Row(CK.Span(*EMPTY), CK.Span(*EMPTY)) for _ in range(plans)))
    place_array(s, prefix + "plans", plan_array, CK.Required_Row)
    s.slot(prefix + "input.required", to(prefix + "plans"))


def b_finalization(core, operation=0, rows=0, plans=0, rows_init=True, start_store=None,
                   parent_mismatch=False):
    s = new_scenario("wl_finalization_decide_v1")
    _add_finalization(s, "", operation, rows, plans, rows_init, start_store, parent_mismatch)
    s.set_arg("input", to("input"))
    place_output(s, "output", FK.Result)
    s.values["zero_digest"] = bytes(HASH_BYTES)
    return s


# A present, nonzero test identity: Hash_Well_Formed refuses a present all-zero digest
# (worldline-collapse_wire.ads:77-81).
DIGEST = bytes(range(1, HASH_BYTES + 1))


def b_mixed(core, mode=1, covers=True, phase=0, roster=0, staged_roster=0, primary_kind=7,
            staged_kind=7, primary="unneeded", staged="unneeded", agent=None,
            agent_confinement=0):
    collapse = CCollapseRequest()
    collapse.candidate_state, collapse.phase, collapse.evaluation_mode = 0, phase, mode
    collapse.conflicts, collapse.foreign_writes = 0, 0
    collapse.roster_complete, collapse.staged_roster_complete = roster, staged_roster
    if covers:
        # Primary_Covers is Same (Tested_Root, Staged_Content_Root) (worldline-collapse.ads:167-169).
        for name in ("tested_root", "staged_content_root"):
            setattr(collapse, name, COptionalHash(1, C_HASH.from_buffer_copy(DIGEST)))
    s = new_scenario("wl_collapse_decide_finalization_v1")
    s.add("collapse", collapse)
    s.set_arg("collapse", to("collapse"))
    s.set_arg("primary_kind", primary_kind)
    s.set_arg("staged_kind", staged_kind)
    for side, prefix, nested in (("primary", "p_", primary), ("staged", "s_", staged)):
        names = (side, side + "_raw", side + "_confinement", side + "_context")
        if nested == "null":
            for name in names:
                s.set_arg(name, NULL)
            continue
        rest = names[1:]
        if nested == "finalization_start":
            _add_finalization(s, prefix, operation=0)
            s.set_arg(side, to(prefix + "input"))
        elif nested == "raw_input_invalid":
            parts = _completion_parts(prefix, 2, "Incomplete_Unknown", None, "head", None, (),
                                      0, 0, 0, 100, None, None, 1)
            _add_completion(s, prefix, parts)
            s.set_arg(side, to(prefix + "input"))
        elif nested == "unneeded":
            rest = names
        else:
            raise KeyError(nested)
        for name in rest:
            # Never written: an unneeded input that is read would be 0xA5 bytes.
            s.add(name + "_fill", 512, align=16, init=False)
            s.set_arg(name, to(name + "_fill"))
    if agent is None:
        s.set_arg("agent", NULL)
    else:
        record = EW.Raw()
        if agent == "bad_source":
            record.observations[0] = 255
        s.add("agent_record", record)
        s.set_arg("agent", {"overflow": "agent_record", "back": 1} if agent == "overflow"
                  else to("agent_record"))
    s.set_arg("agent_confinement", agent_confinement)
    return s


# ------------------------------------------------- PK0-RC1: ready and authorized mixed paths
#
# The ready inputs are produced by the S5 runtime producers through the S5 test fixtures that
# drive them (tests/test_finalization_kernel.py:30-84, 224-255 for Kind 2;
# tests/test_raw_evaluation_default.py:25-69 with tests/test_evaluation_roster_d2.py:28-55
# for Kind 1). Those producers call native exports, so this builder runs in the case's forked
# child only (CHILD_BUILDERS). The bytes the producers make are copied unchanged into the
# child's guarded mapping; only pointer fields are rewritten to the copies (_adopt).
#
# The collapse request differs from the S5 fixtures' request in one field: the S5 candidate
# request leaves Resulting_Requirement absent (test_raw_evaluation_default.py:71-82,
# test_finalization_kernel.py:245-255), and Required_Present then fails for a candidate request
# (worldline-collapse.ads:139-156), so Decide can never be Authorized (:213-217). These cases
# set Resulting_Requirement = Current_Requirement so that the Authorized path, its context
# joins and its metadata joins are reachable. That is the shape of S5's own positive control
# test_collapse_recomputes_carried_roster (test_raw_evaluation_default.py:471-490,
# current_requirement = resulting_requirement = h(8), asserting AUTHORIZED). The S5 tests are
# not edited, and no case here asserts a code for the exact S5 absent-Resulting request: what
# the original AUTHORIZED controls mean is the separate F32-CONFLICT obligation (STATUS.md),
# which PK-0 does not decide.

MIXED_SIDES = ("primary", "staged")


def _h(value):
    # S5 tests/test_raw_evaluation_default.py:524 (def h).
    return bytes([value]) * 32


def _ready_request(shape):
    """The collapse question for each dependency shape (worldline-evaluation_authority.ads:23-38)."""
    import test_raw_evaluation_default as RED
    base = RED.RawDependencyControls.checkpoint()
    candidate = dict(mode="CANDIDATE_EVALUATION",
                     resulting_requirement=base.current_requirement,
                     evaluated_requirement=base.current_requirement,
                     executed_verifiers=base.declared_verifiers,
                     expected_checkpoint=None, witnessed_checkpoint=None)
    # Tested_Root differs from Staged_Content_Root, so Primary_Covers fails; the staged fields
    # make Staged_Covers hold once Staged_Roster_Complete is 1 (worldline-collapse.ads:166-182).
    staged = dict(tested_root=_h(11),
                  staged_evaluated_requirement=base.current_requirement,
                  staged_executed_verifiers=base.declared_verifiers,
                  staged_examined_root=base.staged_content_root)
    if shape == "primary":
        return dataclasses.replace(base, **candidate)
    if shape == "staged":
        return dataclasses.replace(base, **staged)
    if shape == "both":
        return dataclasses.replace(base, **candidate, **staged)
    raise KeyError(shape)


def _mixed_agent(kind):
    from worldline.evaluation_wire import record
    from worldline.finalize import ENGINE_DECLARATIONS
    if kind == "agent":
        # S5 tests/test_finalization_kernel.py:252-254 and test_raw_evaluation_default.py:76-78.
        return record({"id": "agent", "origin": "agent", "format": "exit", "status": "PASS",
                       "exitCode": 0, "supervision": {"kind": "SUPERVISED"},
                       "resources": {"ceilingFired": False}}, ENGINE_DECLARATIONS["agent"])
    if kind == "engine":
        # A well-formed Engine-origin record: the S5 finalization row wire
        # (tests/test_finalization_kernel.py:44-49).
        return record({"id": "protected-paths", "origin": "engine", "format": "engine",
                       "status": "PASS", "required": True}, ENGINE_DECLARATIONS["protected-paths"])
    raise KeyError(kind)


def _ready_kind2(core, request, agent, delta):
    import test_finalization_kernel as TFK
    from worldline.evaluation_context import RowMetadata
    fixture = TFK.FinalizationNativeControls(
        "test_additive_finalization_collapse_requires_full_context_and_metadata")
    fixture.core = core
    fixture.library = Path(os.environ["WORLDLINE_CORE_LIB"])
    fixture.kernel = FK.FinalizationKernel(fixture.library)
    prepared = fixture.kernel.prepare_finalization(fixture.sealed(fixture.capture()))
    changes = {}
    if delta == "binding_content":
        # S5 tests/test_finalization_kernel.py:271-272.
        changes["expected_binding"] = dataclasses.replace(prepared.capture.bound,
                                                          content=b"other-final-content")
    if delta == "metadata_payload":
        rows = tuple(RowMetadata(row.check, row.source, row.payload, row.execution,
                                 row.verifier) for row in prepared.typed_rows)
        changes["row_metadata"] = (dataclasses.replace(rows[0], payload=b"other-metadata-payload"),
                                   ) + rows[1:]
    fixture.joined(prepared, request, agent, **changes)
    return {"kind": 2, "input": prepared.native_request, "raw": None, "confinement": None,
            "prepared": prepared,
            "owners": (prepared.native_request,) + tuple(prepared.native_owners)}


def _ready_kind1(core, request, agent, delta):
    import test_raw_evaluation_default as RED
    from worldline.raw_completion_kernel import RawCompletionKernel
    fixture = RED.RawRequiredFailureControls("test_complete_owned_join_and_padded_epoch")
    library = Path(os.environ["WORLDLINE_CORE_LIB"]).resolve(strict=True)
    fixture.core = core
    fixture.kernel = CK.CompletionKernel(library)
    fixture.raw_kernel = RawCompletionKernel(library)
    fixture.setUp()
    # S5 tests/test_raw_evaluation_default.py:79-80.
    prepared = fixture.prepared((fixture.measured(b"required-check", "PASS"),
                                 fixture.measured(b"evaluation-complete", "PASS")))
    changes = {}
    if delta == "subject":
        # S5 tests/test_raw_evaluation_default.py:92-96.
        changes["expected_binding"] = dataclasses.replace(fixture.bound,
                                                          subject=b"other-full-subject")
    if delta == "metadata_payload":
        rows = prepared.test_only_metadata
        prepared.test_only_metadata = (dataclasses.replace(rows[0], payload=b"other-metadata-payload"),
                                       ) + tuple(rows[1:])
    fixture.joined(request, prepared, agent, **changes)
    return {"kind": 1, "input": prepared.request, "raw": prepared.raw,
            "confinement": prepared.confinement, "prepared": prepared,
            "owners": (prepared.request, prepared.raw, prepared.confinement) + tuple(prepared.owned)}


def _after_join(prepared, delta):
    """Deltas applied to the joined context or metadata, in the S5 tests' manner."""
    if delta == "field":
        # S5 tests/test_raw_evaluation_default.py:146-151.
        prepared.context.expected[0].value.first = 0
    elif delta == "row":
        prepared.context_owners[1][0].item.check_id.first = 0
    elif delta == "row_field":
        prepared.context_owners[1][0].observed[0] = CK.Optional_Span(1, CK.Span(0, 0))
    elif delta == "required":
        prepared.context_owners[2][0].check_id.first = 0
    elif delta == "metadata_row":
        prepared.metadata_owners[1][0].check_id.first = 0
    elif delta == "metadata_count":
        prepared.metadata_context.row_count = prepared.metadata_context.row_count - 1
    elif delta == "no_metadata":
        # S5 tests/test_finalization_kernel.py:264-266.
        prepared.metadata_context = None
    elif delta not in (None, "subject", "binding_content", "metadata_payload"):
        raise KeyError(delta)


def _pointer_fields(ctype, prefix=""):
    """Paths of every c_void_p field of a structure type; arrays of pointers are refused."""
    paths = []
    for name, field in getattr(ctype, "_fields_", ()):
        if field is C.c_void_p:
            paths.append(prefix + name)
        elif isinstance(field, type) and issubclass(field, C.Structure):
            paths.extend(_pointer_fields(field, prefix + name + "."))
        elif isinstance(field, type) and issubclass(field, C.Array):
            element = field._type_
            if element is C.c_void_p or (isinstance(element, type) and issubclass(element, C.Structure)
                                         and _pointer_fields(element)):
                raise G.PlacementError(f"pointer inside an array field {prefix}{name}")
    return paths


def _adopt(s, roots, owners):
    """Copy every object reachable from the roots into the scenario and slot each pointer.

    roots: [(name, ctypes object)]; owners: the ctypes objects the producers keep alive. Every
    non-null pointer must point into exactly one owner, or the case fails (PlacementError).
    """
    table = []
    for owner in owners:
        if isinstance(owner, (C.Structure, C.Array)) and all(owner is not o for o in table):
            table.append(owner)

    def owner_of(address):
        found = [o for o in table
                 if C.addressof(o) <= address < C.addressof(o) + C.sizeof(o)
                 or (C.sizeof(o) == 0 and address == C.addressof(o))]
        if len(found) != 1:
            raise G.PlacementError(f"pointer {address:#x} names {len(found)} owners")
        return found[0], address - C.addressof(found[0])

    named = {id(original): name for name, original in roots}
    queue = list(roots)
    index = 0
    while index < len(queue):
        name, original = queue[index]
        index += 1
        copy = type(original).from_buffer_copy(original)
        element = getattr(type(original), "_type_", None)
        if isinstance(original, C.Array):
            s.add(name, copy, align=C.alignment(element), elem=C.sizeof(element))
        else:
            s.add(name, copy, align=C.alignment(type(original)))
        if not isinstance(original, C.Structure):
            continue
        for path in _pointer_fields(type(original)):
            node, last = G.walk(copy, path)
            value = getattr(node, last)
            if value is None:
                continue
            owner, offset = owner_of(value)
            target = named.get(id(owner))
            if target is None:
                target = name + "_" + path.replace(".", "_")
                named[id(owner)] = target
                queue.append((target, owner))
            s.slot(name + "." + path, to(target, offset))


def b_mixed_ready(core, shape="primary", primary=None, staged=None, agent="agent",
                  confinement=None, p_delta=None, s_delta=None):
    """Ready Kind 1/2 sources, a well-formed agent record and joined contexts (PK0-RC1)."""
    request = _ready_request(shape)
    owned_agent = _mixed_agent(agent)
    sides = {"primary": (primary, p_delta, "p_"), "staged": (staged, s_delta, "s_")}
    collapse = core._raw_collapse_request(request)
    s = new_scenario("wl_collapse_decide_finalization_v1")
    roots, owners, built = [("collapse", collapse)], [], {}
    for side in MIXED_SIDES:
        kind, delta, prefix = sides[side]
        if kind is None:
            continue
        maker = {"k1": _ready_kind1, "k2": _ready_kind2}[kind]
        material = maker(core, request, owned_agent, delta)
        prepared = material["prepared"]
        _after_join(prepared, delta)
        built[side] = material
        roots.append((prefix + "input", material["input"]))
        if material["raw"] is not None:
            roots.append((prefix + "raw", material["raw"]))
            roots.append((prefix + "conf", material["confinement"]))
        if prepared.metadata_context is not None:
            roots.append((prefix + "meta", prepared.metadata_context))
        owners.extend(material["owners"])
        owners.extend(item for group in (prepared.context_owners, prepared.metadata_owners)
                      for item in group)
        if prepared.metadata_context is not None:
            owners.append(prepared.metadata_context)
    raw_agent = owned_agent.native()
    roots.append(("agent_record", raw_agent))
    _adopt(s, roots, owners)
    s.set_arg("collapse", to("collapse"))
    for side in MIXED_SIDES:
        prefix = sides[side][2]
        material = built.get(side)
        names = (side, side + "_raw", side + "_confinement", side + "_context")
        if material is None:
            # As S5 decide_mixed for an unneeded source (finalization_kernel.py:296-297).
            s.set_arg(side + "_kind", 0)
            for name in names:
                s.set_arg(name, NULL)
            continue
        s.set_arg(side + "_kind", material["kind"])
        s.set_arg(side, to(prefix + "input"))
        s.set_arg(side + "_raw", to(prefix + "raw") if material["raw"] is not None else NULL)
        s.set_arg(side + "_confinement",
                  to(prefix + "conf") if material["raw"] is not None else NULL)
        s.set_arg(side + "_context", to(prefix + "meta") if (prefix + "meta") in s.objects
                  else NULL)
    s.set_arg("agent", to("agent_record"))
    s.set_arg("agent_confinement", owned_agent.confinement if confinement is None else confinement)
    needs = {"primary": (1, 0), "staged": (0, 1), "both": (1, 1)}[shape]
    s.values["ready_flags"] = needs
    return s


BUILDERS = {
    "resources": b_resources, "recovery": b_recovery, "recovery_v2": b_recovery_v2,
    "recovery_v3": b_recovery_v3, "protocol": b_protocol, "lifecycle": b_lifecycle,
    "ledger": b_ledger, "headroom": b_headroom, "policy": b_policy, "history": b_history,
    "pending_v1": b_pending_v1, "pending_v2": b_pending_v2, "run_ledger": b_run_ledger,
    "chain": b_chain, "completion": b_completion, "metadata": b_metadata,
    "finalization": b_finalization, "mixed": b_mixed, "mixed_ready": b_mixed_ready,
}

# Builders that call native exports through S5 producers: they run in the forked child only,
# and their cases have no write expectation (the mixed entry writes nothing).
CHILD_BUILDERS = frozenset(("mixed_ready",))


# ------------------------------------------------------------------ mutation and oracles

def split_path(path):
    for index, char in enumerate(path):
        if char in ".[":
            return path[:index], path[index:].lstrip(".")
    return path, ""


def token(spec, scenario, library):
    if isinstance(spec, bool):
        raise TypeError("a boolean is not a C value in this record")
    if isinstance(spec, int) or G.is_target(spec):
        return spec
    if isinstance(spec, str):
        return CONSTANTS[spec]
    if "sizeof" in spec:
        return scenario.objects[spec["sizeof"]].size() + int(spec.get("plus", 0))
    if "over" in spec:
        limit, export, *args = spec["over"]
        restype, argtypes = LAYOUT_QUERIES[export]
        function = library[export]
        function.restype, function.argtypes = restype, argtypes
        stride = int(function(*args))
        if stride <= 0:
            raise AssertionError(f"{export}{tuple(args)} returned {stride}, not a stride")
        return CONSTANTS[limit] // stride + 1
    raise ValueError(f"unknown value spelling {spec!r}")


def mutate(scenario, operations, library):
    for operation in operations:
        kind = operation[0]
        if kind == "set":
            path, value = operation[1], token(operation[2], scenario, library)
            if path.startswith("arg:"):
                scenario.set_arg(path[4:], value)
            elif G.is_target(value):
                scenario.slot(path, value)
            else:
                name, field = split_path(path)
                G.assign(scenario.objects[name].value, field, value)
        elif kind == "bytes":
            obj = scenario.objects[operation[1]]
            obj.value, obj.init = bytes.fromhex(operation[2]), True
        elif kind == "object":
            spec = operation[2]
            if "hex" in spec:
                scenario.add(operation[1], bytes.fromhex(spec["hex"]), align=spec.get("align", 1))
            else:
                scenario.add(operation[1], spec["size"], align=spec.get("align", 1), init=False)
        else:
            raise ValueError(f"unknown mutation {operation!r}")


def build_scenario(core, case):
    """The builder's scenario for a case, checked against the case's export."""
    builder, kwargs = case["build"]
    scenario = BUILDERS[builder](core, **kwargs)
    if scenario.export != case["export"]:
        raise AssertionError(f"{case['id']}: builder {builder} makes {scenario.export}")
    return scenario


def _collapse_decide(library, bound):
    function = library["wl_collapse_decide"]
    function.restype, function.argtypes = C.c_uint8, [C.c_void_p]
    return int(function(C.addressof(bound)))


def oracle_collapse_zeroed(scenario, library):
    """wl_collapse_decide on the collapse request with both roster flags cleared.

    The mixed entry sets Roster_Complete and Staged_Roster_Complete to 0 when Agent_Ready is
    not 1 and then returns CW.Decide_Wire (Bound) (evaluation_finalization_c.adb:485-490);
    wl_collapse_decide returns CW.Decide_Wire (Request.all) (worldline-c_api.adb:331-342).
    """
    bound = CCollapseRequest.from_buffer_copy(bytes(scenario.objects["collapse"].value))
    bound.roster_complete = 0
    bound.staged_roster_complete = 0
    return _collapse_decide(library, bound)


def oracle_collapse_ready(scenario, library):
    """wl_collapse_decide on the collapse request with the roster flags of ready sources.

    With Agent_Ready = 1 the mixed entry sets Roster_Complete := P_Ready and
    Staged_Roster_Complete := S_Ready (evaluation_finalization_c.adb:485-486). The builder
    records the flags a ready needed source gives (Promotion 1; :384, :396); a source that is
    not needed keeps 0 (:427, :439). This oracle checks only the collapse half: that the request
    with those flags is Authorized (Authorized = 0, worldline-collapse.ads:79-80). It observes
    neither Read_Ready nor agent admission; those are observed per case by probe_readiness
    (RC-v2-2).
    """
    bound = CCollapseRequest.from_buffer_copy(bytes(scenario.objects["collapse"].value))
    bound.roster_complete, bound.staged_roster_complete = scenario.values["ready_flags"]
    return _collapse_decide(library, bound)


ORACLES = {"collapse_zeroed": oracle_collapse_zeroed, "collapse_ready": oracle_collapse_ready}

# Read_Ready's accepted Kind-1 reasons (evaluation_finalization_c.adb:381-382).
READY_REASONS = ("Retain_Terminal", "Already_Retained")


def _call(library, name, restype, argtypes, *args):
    function = library[name]
    function.restype, function.argtypes = restype, argtypes
    return int(function(*args))


def _probe_side(scenario, library, address, side):
    """Read_Ready (evaluation_finalization_c.adb:370-398), observed through the same exports.

    Kind 1: Raw_Decide is wl_completion_raw_decide_v1 (evaluation_completion_c.adb:529); valid
    when it returns 0 with a Retain_Terminal or Already_Retained reason and Promotion <= 1.
    Kind 2: Decide is wl_finalization_decide_v1 (evaluation_finalization_c.adb:121); valid when
    it returns 0 with Reason 0, Promotion <= 1 and the re-read header has Operation 3. The
    output records are local to this child; nothing in the guarded mapping is written.
    """
    kind = scenario.get_arg(side + "_kind")
    where = address(scenario.get_arg(side))
    if kind == 1:
        out = CK.Result()
        code = _call(library, "wl_completion_raw_decide_v1", C.c_int, [C.c_void_p] * 4, where,
                     address(scenario.get_arg(side + "_raw")),
                     address(scenario.get_arg(side + "_confinement")), C.addressof(out))
        reason = CK.REASONS[out.reason] if out.reason < len(CK.REASONS) else int(out.reason)
        valid = code == 0 and out.promotion <= 1 and reason in READY_REASONS
        return {"kind": 1, "code": code, "reason": reason, "promotion": int(out.promotion),
                "valid": int(valid), "ready": int(out.promotion) if valid else 0}
    if kind == 2:
        out = FK.Result()
        code = _call(library, "wl_finalization_decide_v1", C.c_int, [C.c_void_p] * 2, where,
                     C.addressof(out))
        operation = int(FK.Request.from_address(where).operation)
        valid = code == 0 and out.reason == 0 and out.promotion <= 1 and operation == 3
        return {"kind": 2, "code": code, "reason": int(out.reason),
                "promotion": int(out.promotion), "operation": operation, "valid": int(valid),
                "ready": int(out.promotion) if valid else 0}
    return {"kind": int(kind), "valid": 0, "ready": 0}


def _probe_agent(scenario, library, address):
    """Agent_Ready (evaluation_finalization_c.adb:453-470), observed through
    wl_evaluation_wire_admit, whose body is Confined_Admit_Wire on the same record bytes
    (worldline-c_api.adb:729-735); Source_Field is observation 0 (worldline-evaluation_wire.ads:20)."""
    where = address(scenario.get_arg("agent"))
    admit = _call(library, "wl_evaluation_wire_admit", C.c_uint8, [C.c_void_p, C.c_uint8],
                  where, scenario.get_arg("agent_confinement"))
    source = int(EW.Raw.from_address(where).observations[0])
    ready = 0 if admit == 255 or source != EVALUATION_ORIGINS["agent"] else admit
    return {"admit": admit, "source": source, "ready": ready}


def probe_readiness(scenario, library, address):
    """RC-v2-2: observe, in the case's own child, that each needed source is valid and ready
    and what the agent's readiness is, before the mixed entry is called."""
    primary, staged = scenario.values["ready_flags"]
    observed = {}
    if primary:
        observed["primary"] = _probe_side(scenario, library, address, "primary")
    if staged:
        observed["staged"] = _probe_side(scenario, library, address, "staged")
    observed["agent"] = _probe_agent(scenario, library, address)
    return observed


# ------------------------------------------------------------------------ expectations

def has_placeholder(spec):
    if spec == PLACEHOLDER:
        return True
    if isinstance(spec, dict):
        return any(has_placeholder(value) for value in spec.values())
    if isinstance(spec, list):
        return any(has_placeholder(value) for value in spec)
    return False


def plain(value):
    if isinstance(value, C.Structure):
        return {name: plain(getattr(value, name)) for name, _ in value._fields_}
    if isinstance(value, C.Array):
        if value._type_ is C.c_uint8:
            return bytes(value).hex()
        return [plain(item) for item in value]
    return value


def enum_code(reference):
    table_name, _, name = reference.partition(":")
    table = ENUMS[table_name]
    if isinstance(table, type):
        return int(table[name])
    return list(table).index(name)


def resolve(spec, scenario):
    if isinstance(spec, bool):
        raise TypeError("booleans are not used in expectations")
    if isinstance(spec, int):
        return spec
    if isinstance(spec, str):
        return enum_code(spec)
    if isinstance(spec, list):
        return [resolve(item, scenario) for item in spec]
    if "span" in spec:
        first, length = scenario.labels[spec["span"]]
        return {"first": first, "length": length}
    if "opt" in spec:
        if spec["opt"] is None:
            return {"present": 0, "value": {"first": 1, "length": 0}}
        return {"present": 1, "value": resolve({"span": spec["opt"]}, scenario)}
    if "hex" in spec:
        return spec["hex"]
    if "value_of" in spec:
        return scenario.values[spec["value_of"]].hex()
    return {key: resolve(value, scenario) for key, value in spec.items()}


def describe_changes(report):
    owners = report.get("objects", {})
    named = []
    for offset in report["changed"]:
        owner = next((name for name, (a, b) in owners.items() if a <= offset < b), "canary")
        named.append(f"{offset}:{owner}")
    return f"{report['changed_count']} changed byte(s), first {named}"


def run_case(library, core, case):
    """Fork one case. Child-only builders build inside the child; the others build here."""
    in_child = case["build"][0] in CHILD_BUILDERS
    scenario = None if in_child else build_scenario(core, case)
    guards = case.get("guard") or {}
    oracle = ORACLES.get(case.get("oracle"))
    readiness = "readiness" in case["expect"]

    def child():
        target = build_scenario(core, case) if in_child else scenario
        mutate(target, case.get("mut", ()), library)
        prelude = probe = None
        if oracle is not None:
            prelude = lambda region, base, address: oracle(target, library)  # noqa: E731
        if readiness:
            probe = lambda region, base, address: probe_readiness(target, library, address)  # noqa: E731
        return G.execute(library, target, guards, prelude, probe)

    status, report, raw = G.run_forked(child)
    return scenario, status, report, raw


def decoded_writes(scenario, report):
    answer = {}
    for pointer, window in report["windows"].items():
        if window["after"] is not None:
            ctype = scenario.outputs[pointer]
            answer[pointer] = plain(ctype.from_buffer_copy(bytes.fromhex(window["after"])))
    return answer


def assert_child_ok(test, label, status, report, raw):
    """The parent's first check on every forked case: a fault is never a code (PK0-RC3)."""
    test.assertTrue(G.normal_exit(status),
                    f"{label}: the child ended abnormally ({G.describe(status)}); a fault is "
                    f"never a refusal code. Report: {raw[:400]!r}")
    test.assertIsInstance(report, dict, f"{label}: no report")
    test.assertNotIn("child_error", report, f"{label}: {report.get('child_error')}")


def assert_ready(test, label, expected, observed):
    """RC-v2-2: the fixture's readiness, observed in the same child, is the declared one."""
    test.assertIsInstance(observed, dict, f"{label}: no readiness observation")
    for side, ready in expected.items():
        got = observed.get(side)
        test.assertIsNotNone(got, f"{label}: no readiness observation for {side}")
        if side == "agent":
            test.assertNotEqual(got["admit"], 255, f"{label}: agent record not well formed: {got}")
        else:
            test.assertEqual(got["valid"], 1, f"{label}: {side} source refused by Read_Ready: {got}")
        test.assertEqual(got["ready"], ready, f"{label}: {side} readiness: {got}")


class CapiCharacterization(unittest.TestCase):
    """One generated test per record case, plus checks of the record itself."""

    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        cls.lib = cls.core._lib

    def check_case(self, case):
        scenario, status, report, raw = run_case(self.lib, self.core, case)
        label = case["id"]
        assert_child_ok(self, label, status, report, raw)
        expect = case["expect"]
        if "readiness" in expect:
            assert_ready(self, label, expect["readiness"], report.get("probe"))
        code = expect["code"]
        if code == "oracle":
            self.assertIsNotNone(report["oracle"], f"{label}: no oracle value")
            self.assertNotEqual(report["oracle"], 255,
                                f"{label}: the zeroed collapse request must be well formed")
            self.assertEqual(report["code"], report["oracle"], f"{label}: mixed-entry decision")
        elif has_placeholder(code):
            self.fail(f"{label}: return code is {PLACEHOLDER}; observed {report['code']}")
        else:
            self.assertEqual(report["code"], code, f"{label}: return code")
        if "oracle_value" in expect:
            self.assertEqual(report["oracle"], expect["oracle_value"],
                             f"{label}: the fixture's relational oracle (ready-source rosters)")
        if guards_of(case):
            return  # C-05 asserts a normal exit and the expected code only (rule R14).
        self.assertEqual(report["changed"], [],
                         f"{label}: bytes outside the write set changed: {describe_changes(report)}")
        writes = expect.get("writes", "none")
        windows = report["windows"]
        if writes == "none":
            for pointer, window in windows.items():
                self.assertEqual(window["after"], window["before"],
                                 f"{label}: {pointer} written on a no-write path (C-01)")
            return
        for pointer, window in windows.items():
            if pointer not in writes:
                self.assertEqual(window["after"], window["before"],
                                 f"{label}: {pointer} is outside the expected write set")
        actual = decoded_writes(scenario, report)
        for pointer, spec in writes.items():
            self.assertIn(pointer, actual, f"{label}: no window for {pointer}")
            if has_placeholder(spec):
                self.fail(f"{label}: the write to {pointer} is {PLACEHOLDER} and needs a baseline "
                          f"run on L0; observed {actual[pointer]}")
            self.assertEqual(actual[pointer], resolve(spec, scenario),
                             f"{label}: exact write to {pointer}")

    def test_record_shape(self):
        """The record is complete and internally consistent (no library needed)."""
        exports = RECORD["exports"]
        self.assertEqual(set(SIGNATURES) | {"wl_native_diagnostic_control_v1"}, set(exports))
        ids = [case["id"] for case in RECORD["cases"]]
        self.assertEqual(len(ids), len(set(ids)), "case ids must be unique")
        for case in RECORD["cases"]:
            entry = exports[case["export"]]
            self.assertIn(case["build"][0], BUILDERS, case["id"])
            self.assertIn(case["class"], entry["classes"], case["id"])
            self.assertNotIn(case["class"], ("H", "X"),
                             f"{case['id']}: PK-0 asserts no class-H or class-X case")
            if case["class"] in ("R0", "R1", "R2") and not guards_of(case):
                self.assertEqual(case["expect"]["code"], entry["classes"][case["class"]]["code"],
                                 f"{case['id']}: refusal code differs from the class table")
                self.assertEqual(case["expect"].get("writes", "none"), "none", case["id"])
            if case["build"][0] in CHILD_BUILDERS:
                self.assertEqual(case["expect"].get("writes", "none"), "none", case["id"])
                readiness = case["expect"].get("readiness")
                self.assertIsInstance(readiness, dict, f"{case['id']}: readiness must be declared")
                self.assertIn("agent", readiness, case["id"])
                for value in readiness.values():
                    self.assertIn(value, (0, 1), case["id"])
            if "oracle_value" in case["expect"]:
                self.assertIn(case.get("oracle"), ORACLES, case["id"])
                self.assertIsInstance(case["expect"]["oracle_value"], int, case["id"])
        for name, entry in exports.items():
            self.assertEqual(entry["classes"]["X"]["asserted"], "nothing", name)
        self.assertEqual(CONSTANTS["I64_MAX"], (1 << (8 * C.sizeof(C.c_int64) - 1)) - 1)
        self.assertEqual(CONSTANTS["I64_MAX+1"], CONSTANTS["I64_MAX"] + 1)
        self.assertEqual(CONSTANTS["SIZE_MAX"], C.c_size_t(-1).value)
        self.assertEqual(CONSTANTS["U32_MAX"], C.c_uint32(-1).value)


class HarnessFaultControl(unittest.TestCase):
    """PK0-RC3 negative control. Harness only: no WORLDLINE export is called.

    Under the native runtime initialized in this process (Core), a forked child applies the
    fatal-fault policy and reads one byte of a PROT_NONE page placed by the helper's own
    layout code. The control requires that the child ends by SIGSEGV or SIGBUS, that it
    reports nothing, and that the parent's case check (assert_child_ok) fails on that status.
    It runs only when the admitted launch runs this suite; nothing runs it at import.

    RC-v2-4: on every path, passing included, it writes one JSON line with the observed wait
    status and signal directly to file descriptor 1, which the admitted launch captures; the
    line is written before any assertion, so a pass leaves it in the launch's stdout.
    """

    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))

    def test_protection_fault_is_never_a_code(self):
        status, report, raw = G.run_forked(G.protected_probe)
        signaled = os.WIFSIGNALED(status)
        line = json.dumps({"harness_fault_control": {
            "wait_status": status, "signaled": signaled,
            "signal": os.WTERMSIG(status) if signaled else None,
            "describe": G.describe(status), "report_bytes": len(raw)}}, sort_keys=True)
        view = memoryview((line + "\n").encode("ascii"))
        while view:
            view = view[os.write(1, view):]
        self.assertTrue(signaled,
                        f"the protected read did not end the child by a signal: {G.describe(status)}; "
                        f"report {raw[:200]!r}")
        self.assertIn(os.WTERMSIG(status), G.PROTECTION_SIGNALS, G.describe(status))
        self.assertEqual(raw, b"", "a faulted child must report nothing")
        self.assertIsNone(report)
        with self.assertRaises(self.failureException):
            assert_child_ok(self, "harness-protected-probe", status, report, raw)


def guards_of(case):
    return bool(case.get("guard"))


def _case_test(case):
    def test(self):
        self.check_case(case)
    test.__doc__ = f"{case['id']}: {case.get('title', '')}"
    return test


for _case in RECORD["cases"]:
    setattr(CapiCharacterization, "test_case_" + _case["id"].replace(".", "_").replace("-", "_"),
            _case_test(_case))


def record_main():
    """Print observed values for placeholder cases as JSON on standard output; write no file."""
    require_output_only_launch()
    core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
    observed = {}
    for case in RECORD["cases"]:
        if not has_placeholder(case["expect"]):
            continue
        scenario, status, report, raw = run_case(core._lib, core, case)
        entry = {"exit": G.describe(status)}
        if G.normal_exit(status) and isinstance(report, dict) and "child_error" not in report:
            entry["code"] = report["code"]
            entry["changed_count"] = report["changed_count"]
            entry["writes"] = {} if scenario is None else decoded_writes(scenario, report)
        else:
            entry["raw"] = raw[:400].decode("latin-1")
        observed[case["id"]] = entry
    json.dump({"record": "capi-characterization observed values (L0 baseline)",
               "observed": observed}, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if "--record" in sys.argv[1:]:
        record_main()
    else:
        unittest.main()
