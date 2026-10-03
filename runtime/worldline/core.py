from __future__ import annotations

import ctypes
from dataclasses import dataclass
import os
from pathlib import Path
from threading import Lock
from typing import Iterable, Mapping, Sequence

from .errors import CoreUnavailable, WorldlineError

HASH_BYTES = 32

STATE_CODES: dict[str, int] = {
    "MUTABLE": 0,
    "FINALIZING": 1,
    "VALID": 2,
    "DEGRADED": 3,
    "DEAD": 4,
    "ARCHIVED": 5,
    "COLLAPSED": 6,
}

# Transaction lifecycle codes, in the declaration order of Worldline.Transitions.Transaction_State.
TRANSACTION_STATE_CODES: dict[str, int] = {
    "PREPARED": 0,
    "AUTHORIZED": 1,
    "DENIED": 2,
    "COMMITTED": 3,
    "ABORTED": 4,
}

COLLAPSE_DECISIONS: dict[int, str] = {
    0: "AUTHORIZED",
    1: "INVALID_CANDIDATE",
    2: "PARENT_MISMATCH",
    3: "OWNER_MISMATCH",
    4: "BASE_MISMATCH",
    5: "DELTA_MISMATCH",
    6: "ROOT_SET_MISMATCH",
    7: "STAGED_ROOT_MISMATCH",
    8: "CONFLICT",
    9: "FOREIGN_MANAGED_WRITE",
    10: "VALIDATION_CONTEXT_MISMATCH",
    11: "STAGED_UNTESTED",
    12: "EXECUTION_EVIDENCE_INCOMPLETE",
    13: "VERIFIER_EXECUTION_IDENTITY_MISMATCH",
    14: "CHECKPOINT_UNWITNESSED",
    15: "IDENTITY_ABSENT",
    16: "MEASUREMENT_ABSENT",
    17: "PRIME_CHANGED",
    18: "WATCH_INCOMPLETE",
    19: "CHECKPOINT_MISMATCH",
    20: "EVIDENCE_SUBJECT_MISMATCH",
    255: "INVALID_REQUEST",
}

# The ABI generation this runtime was written against (wl_abi_version). Record layouts and the
# meaning of every exported code belong to it; a library reporting another is refused at load.
ABI_VERSION = 5

# Which evidence speaks for the bytes that would become live (Worldline.Collapse.Evaluation_Mode).
EVALUATION_MODES = {"CANDIDATE_EVALUATION": 0, "CHECKPOINT_RETURN": 1}
COLLAPSE_PHASES = {"COMMIT": 0, "PREPARE": 1}
# A measurement the runtime made, or could not make (Worldline.Collapse.Measurement).
MEASUREMENTS = {"UNMEASURED": 0, "NONE_FOUND": 1, "FOUND": 2}
ROSTER_MAX = 4096

# The declaration order is part of the new C ABI. Unknown raw observations
# remain explicit categories; Python never guesses that they mean completion.
EVALUATION_ORIGINS = {"engine": 0, "agent": 1, "external": 2}
EVALUATION_STATUSES = {"ABSENT": 0, "PASS": 1, "FAIL": 2, "UNASSESSED": 3, "OTHER": 4}
EVALUATION_CHANNELS = {"ABSENT": 0, "EMPTY": 1, "ACCEPTED": 2,
                       "REJECTED": 3, "OTHER": 4, "MALFORMED": 5}
EVALUATION_STAGES = {"ABSENT": 0, "SANDBOX_NEVER_STARTED": 1,
                     "STOPPED_BY_MANAGER": 2, "HARNESS_SIGNALLED": 3, "OTHER": 4}
EVALUATION_SUPERVISION = {"ABSENT": 0, "SUPERVISED": 1, "STOPPED": 2, "OTHER": 3}
EVALUATION_EXECUTIONS = ("NOT_ATTEMPTED", "PREPARED", "STARTED", "INTERRUPTED",
                         "ERROR_BEFORE_EXAMINER", "INCOMPLETE_UNKNOWN",
                         "EVALUATOR_INCOMPLETE", "UNCLASSIFIED", "COMPLETED")
EVALUATION_OUTCOMES = ("NONE", "PASS", "FAIL")
EVALUATION_BUNDLES = ("NOT_COVERED", "VERIFIED", "COMPROMISED", "UNKNOWN")
EVALUATION_REPORTS = {"NOT_APPLICABLE": 0, "VERIFIED": 1, "UNTRUSTED": 2}

_ERROR_NAMES = {
    1: "INVALID_ARGUMENT",
    2: "IO",
    3: "TOO_LARGE",
    4: "INTERNAL",
}

C_HASH = ctypes.c_uint8 * HASH_BYTES


class COptionalHash(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("value", C_HASH)]


class COptionalCounter(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("value_le", ctypes.c_uint8 * 8)]


# Layout 5 (1.9.0), in the order of Worldline.Collapse_Wire.Raw_Request.
COLLAPSE_HASH_FIELDS = (
    "expected_parent",
    "candidate_parent",
    "expected_subject",
    "evidence_subject",
    "expected_base",
    "candidate_base",
    "expected_delta",
    "candidate_delta",
    "expected_root_set",
    "candidate_root_set",
    "expected_staged_root",
    "actual_staged_root",
    "staged_content_root",
    "tested_root",
    "current_requirement",
    "evaluated_requirement",
    "declared_verifiers",
    "executed_verifiers",
    "staged_evaluated_requirement",
    "staged_executed_verifiers",
    "staged_examined_root",
    "expected_checkpoint",
    "witnessed_checkpoint",
    "registered_watch_set",
    "watched_set",
)


class CCollapseRequest(ctypes.Structure):
    _fields_ = [
        ("candidate_state", ctypes.c_uint8),
        ("phase", ctypes.c_uint8),
        ("evaluation_mode", ctypes.c_uint8),
        ("conflicts", ctypes.c_uint8),
        ("foreign_writes", ctypes.c_uint8),
        ("roster_complete", ctypes.c_uint8),
        ("staged_roster_complete", ctypes.c_uint8),
        *[(name, COptionalHash) for name in COLLAPSE_HASH_FIELDS],
        ("generation_before", COptionalCounter),
        ("generation_after", COptionalCounter),
    ]


class CEvaluationObservations(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint8) for name in (
        "source", "status", "channel", "stage", "exit_present", "exit_integer",
        "supervisor", "supervisor_stopped", "bundle_present", "bundle_is_mapping",
        "bundle_stable", "bundle_changed", "unsatisfied_imports",
    )]


class CEvaluationClassification(ctypes.Structure):
    _fields_ = [("execution", ctypes.c_uint8), ("outcome", ctypes.c_uint8),
                ("bundle", ctypes.c_uint8)]


class CEvidencePresence(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint8) for name in (
        "record_identified", "verdict_recorded", "binding_established",
        "declaration_matches", "bundle_identified",
    )]


# wl_layout_size selectors, and the ctypes record each one must match byte for byte.
_LAYOUTS = ((0, CCollapseRequest), (1, CEvaluationObservations),
            (2, CEvaluationClassification), (3, CEvidencePresence),
            (4, COptionalHash), (5, COptionalCounter))


@dataclass(frozen=True, slots=True)
class EvaluationFacts:
    source: str
    status: str
    channel: str
    stage: str
    exit_present: bool
    exit_integer: bool
    supervisor: str
    supervisor_stopped: bool
    bundle_present: bool
    bundle_is_mapping: bool
    bundle_stable: bool
    bundle_changed: bool
    unsatisfied_imports: bool


@dataclass(frozen=True, slots=True)
class EvaluationClassification:
    execution: str
    outcome: str
    bundle: str


@dataclass(frozen=True, slots=True)
class EvidencePresence:
    """Typed per-check evidence presence (Worldline.Evaluation.Evidence_Presence).

    Each field is a fact the caller established, never a truthiness test on the record. The
    kernel admits a check only when every one of them holds.
    """
    record_identified: bool
    verdict_recorded: bool
    binding_established: bool
    declaration_matches: bool
    bundle_identified: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CollapseInput:
    """Every input of the collapse decision, with no defaults (1.9.0).

    An identity is 32 bytes or None, and None means ABSENT: the kernel never treats two absent
    values as equal, and a zero digest is refused before it reaches the kernel, so no sentinel
    can stand in for a value. Each pair is produced from two different sources; the kernel's
    Collapse_Request comments name them.
    """

    candidate_state: str
    phase: str
    mode: str
    conflicts: str
    foreign_writes: str
    roster_complete: bool
    staged_roster_complete: bool
    expected_parent: bytes | None
    candidate_parent: bytes | None
    expected_subject: bytes | None
    evidence_subject: bytes | None
    expected_base: bytes | None
    candidate_base: bytes | None
    expected_delta: bytes | None
    candidate_delta: bytes | None
    expected_root_set: bytes | None
    candidate_root_set: bytes | None
    expected_staged_root: bytes | None
    actual_staged_root: bytes | None
    staged_content_root: bytes | None
    tested_root: bytes | None
    current_requirement: bytes | None
    evaluated_requirement: bytes | None
    declared_verifiers: bytes | None
    executed_verifiers: bytes | None
    staged_evaluated_requirement: bytes | None
    staged_executed_verifiers: bytes | None
    staged_examined_root: bytes | None
    expected_checkpoint: bytes | None
    witnessed_checkpoint: bytes | None
    registered_watch_set: bytes | None
    watched_set: bytes | None
    generation_before: int | None
    generation_after: int | None


def _package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def runtime_installed() -> bool:
    """Whether this runtime runs from an installed tree rather than a source checkout (1.9.2).

    Both installers put the library BESIDE runtime/ (install.sh: ~/.local/lib/worldline,
    PKGBUILD: /usr/lib/worldline); a source checkout keeps it under lib/. Judged from the file
    layout, which the same account can change (ASSUMED, SECURITY.md): an installed runtime
    refuses a library chosen by WORLDLINE_CORE_LIB and ignores every test-only seam."""
    return (_package_root() / "libworldline_core.so").exists()


def _library_sources() -> Iterable[tuple[Path, str]]:
    """Each candidate library with how it was selected: "environment" (WORLDLINE_CORE_LIB, a
    test build's seam), "package" (beside or under this runtime's own tree) or "home"."""
    configured = os.environ.get("WORLDLINE_CORE_LIB")
    if configured:
        yield Path(configured).expanduser(), "environment"
    # Resolve relative to this module so an alternate HOME cannot hide the proved library:
    # runtime/worldline/core.py sits under the source tree (lib/ sibling of runtime/) and under
    # the installed tree (library beside runtime/).
    package_root = _package_root()
    yield package_root / "lib/libworldline_core.so", "package"
    yield package_root / "libworldline_core.so", "package"
    yield Path.home() / ".local/lib/worldline/libworldline_core.so", "home"


def _library_candidates() -> Iterable[Path]:
    for path, _source in _library_sources():
        yield path


def hash_bytes_from_id(value: str) -> bytes:
    if not value.startswith("sha256:"):
        raise WorldlineError("INVALID_HASH", f"expected sha256 identity: {value}")
    try:
        result = bytes.fromhex(value.removeprefix("sha256:"))
    except ValueError as exc:
        raise WorldlineError("INVALID_HASH", f"invalid SHA-256 identity: {value}") from exc
    if len(result) != HASH_BYTES:
        raise WorldlineError("INVALID_HASH", f"invalid SHA-256 identity length: {value}")
    return result


def hash_id(value: bytes) -> str:
    if len(value) != HASH_BYTES:
        raise WorldlineError("INVALID_HASH", "digest is not 32 bytes")
    return f"sha256:{value.hex()}"


class Core:
    _shared: "Core | None" = None
    _shared_lock = Lock()

    def __init__(self, library: Path | None = None) -> None:
        selected = library
        # How the library was chosen (1.9.2, OB-084): an environment-selected library is a test
        # build's and never yields PROVED; an installed runtime refuses to promote with one.
        self.library_source = "explicit"
        if selected is None:
            selected, self.library_source = next(
                ((path, source) for path, source in _library_sources() if path.is_file()), (None, "none"))
        if selected is None:
            raise CoreUnavailable(
                "libworldline_core.so was not found",
                searched=[str(path) for path in _library_candidates()],
            )
        try:
            self.library_path = selected.resolve(strict=True)
            self._lib = ctypes.CDLL(str(self.library_path), use_errno=True)
        except (OSError, RuntimeError) as exc:
            raise CoreUnavailable("libworldline_core.so could not be loaded", path=str(selected), error=str(exc)) from exc
        self._configure()

    @classmethod
    def shared(cls) -> "Core":
        with cls._shared_lock:
            if cls._shared is None:
                cls._shared = cls()
            return cls._shared

    def _configure(self) -> None:
        pointer = ctypes.c_void_p
        self._lib.wl_hash_file.argtypes = [pointer, ctypes.c_size_t, pointer]
        self._lib.wl_hash_file.restype = ctypes.c_int
        self._lib.wl_hash_bytes.argtypes = [pointer, ctypes.c_size_t, pointer]
        self._lib.wl_hash_bytes.restype = ctypes.c_int
        self._lib.wl_world_id.argtypes = [pointer] * 7
        self._lib.wl_world_id.restype = ctypes.c_int
        self._lib.wl_causal_link.argtypes = [pointer, pointer, pointer]
        self._lib.wl_causal_link.restype = ctypes.c_int
        self._lib.wl_receipt_link.argtypes = [pointer, pointer, pointer]
        self._lib.wl_receipt_link.restype = ctypes.c_int
        self._lib.wl_transition_allowed.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
        self._lib.wl_transition_allowed.restype = ctypes.c_uint8
        self._lib.wl_collapse_decide.argtypes = [ctypes.POINTER(CCollapseRequest)]
        self._lib.wl_collapse_decide.restype = ctypes.c_uint8
        # The transaction lifecycle (PREPARED -> AUTHORIZED -> COMMITTED, with DENIED sticky)
        # is a proved unit; before 1.1 it was only mirrored by a Python table. Refuse a library
        # that predates the export rather than silently falling back to the mirror.
        try:
            function = self._lib.wl_transaction_transition_allowed
        except AttributeError as exc:
            raise CoreUnavailable(
                "libworldline_core.so predates the transaction-lifecycle export; rebuild and reinstall",
                path=str(self.library_path),
            ) from exc
        function.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
        function.restype = ctypes.c_uint8
        # The runtime requires the Phase 1 classifier and refuses an older core.
        # It must not silently restore Python's former admission predicate.
        try:
            classify = self._lib.wl_evaluation_classify
            admissible = self._lib.wl_evaluation_admissible
        except AttributeError as exc:
            raise CoreUnavailable(
                "libworldline_core.so lacks the Phase 1 evaluation authority exports",
                path=str(self.library_path),
            ) from exc
        classify.argtypes = [ctypes.POINTER(CEvaluationObservations),
                             ctypes.POINTER(CEvaluationClassification)]
        classify.restype = ctypes.c_uint8
        # 1.8.0: the ABI generation and every record layout are checked before any decision is
        # asked for. A library built for another layout would read these structures at the
        # wrong offsets and answer questions nobody asked.
        try:
            abi_version = self._lib.wl_abi_version
            layout_size = self._lib.wl_layout_size
            layout_offset = self._lib.wl_layout_offset
            transition = self._lib.wl_evaluation_transition_allowed
            advance = self._lib.wl_evaluation_advance
            roster = self._lib.wl_evaluation_roster_complete
        except AttributeError as exc:
            raise CoreUnavailable(
                "libworldline_core.so predates ABI generation 4 (the 1.8.0 evaluation authority);"
                " rebuild and reinstall", path=str(self.library_path),
            ) from exc
        abi_version.argtypes = []
        abi_version.restype = ctypes.c_uint32
        reported = int(abi_version())
        if reported != ABI_VERSION:
            raise CoreUnavailable(
                f"libworldline_core.so reports ABI generation {reported}; this runtime requires {ABI_VERSION}",
                path=str(self.library_path),
            )
        layout_size.argtypes = [ctypes.c_uint8]
        layout_size.restype = ctypes.c_size_t
        layout_offset.argtypes = [ctypes.c_uint8, ctypes.c_char_p, ctypes.c_size_t]
        layout_offset.restype = ctypes.c_size_t
        # Every field's offset BY NAME, not only each record's size: two equal-sized fields
        # swapped keep every size and every positional offset, and would put a decision input
        # where the kernel reads another.
        for selector, structure in _LAYOUTS:
            library_size = int(layout_size(selector))
            library_offsets = [int(layout_offset(selector, name.encode("ascii"), len(name)))
                               for name, _ in structure._fields_]
            here = [getattr(structure, name).offset for name, _ in structure._fields_]
            if library_size != ctypes.sizeof(structure) or library_offsets != here:
                raise CoreUnavailable(
                    f"record layout {structure.__name__} disagrees with the library"
                    f" ({ctypes.sizeof(structure)} bytes here, {library_size} in the library;"
                    f" field offsets {'agree' if library_offsets == here else 'differ'})",
                    path=str(self.library_path),
                )
        admissible.argtypes = [ctypes.POINTER(CEvaluationClassification),
                               ctypes.c_uint8, ctypes.POINTER(CEvidencePresence)]
        admissible.restype = ctypes.c_uint8
        transition.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
        transition.restype = ctypes.c_uint8
        advance.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8]
        advance.restype = ctypes.c_uint8
        roster.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint8]
        roster.restype = ctypes.c_uint8

    @staticmethod
    def _checked(code: int, operation: str) -> None:
        if code:
            name = _ERROR_NAMES.get(code, f"UNKNOWN_{code}")
            raise WorldlineError(f"CORE_{name}", f"proved core rejected {operation}", {"status": code})

    @staticmethod
    def _array(value: bytes) -> C_HASH:
        if len(value) != HASH_BYTES:
            raise WorldlineError("INVALID_HASH", "core input digest is not 32 bytes")
        return C_HASH.from_buffer_copy(value)

    def hash_bytes(self, data: bytes) -> bytes:
        output = C_HASH()
        if data:
            source = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
            address = ctypes.cast(source, ctypes.c_void_p)
        else:
            source = None
            address = ctypes.c_void_p()
        self._checked(self._lib.wl_hash_bytes(address, len(data), output), "byte hash")
        return bytes(output)

    def hash_file(self, path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> bytes:
        encoded = os.fsencode(path)
        source = (ctypes.c_uint8 * len(encoded)).from_buffer_copy(encoded)
        output = C_HASH()
        self._checked(
            self._lib.wl_hash_file(ctypes.cast(source, ctypes.c_void_p), len(encoded), output),
            "file hash",
        )
        return bytes(output)

    def world_id(self, components: Mapping[str, bytes]) -> bytes:
        names = ("parent", "filesystem", "config", "repository", "environment", "evidence")
        arrays = [self._array(components[name]) for name in names]
        output = C_HASH()
        self._checked(self._lib.wl_world_id(*arrays, output), "world identity")
        return bytes(output)

    def causal_link(self, previous: bytes, event_root: bytes) -> bytes:
        output = C_HASH()
        self._checked(
            self._lib.wl_causal_link(self._array(previous), self._array(event_root), output),
            "causal link",
        )
        return bytes(output)

    def receipt_link(self, previous: bytes, receipt_root: bytes) -> bytes:
        output = C_HASH()
        self._checked(
            self._lib.wl_receipt_link(self._array(previous), self._array(receipt_root), output),
            "receipt link",
        )
        return bytes(output)

    def transition_allowed(self, from_state: str, to_state: str) -> bool:
        try:
            source = STATE_CODES[from_state]
            target = STATE_CODES[to_state]
        except KeyError as exc:
            raise WorldlineError("INVALID_STATE", f"unknown world state: {exc.args[0]}") from exc
        return bool(self._lib.wl_transition_allowed(source, target))

    def transaction_transition_allowed(self, from_state: str, to_state: str) -> bool:
        try:
            source = TRANSACTION_STATE_CODES[from_state]
            target = TRANSACTION_STATE_CODES[to_state]
        except KeyError as exc:
            raise WorldlineError("INVALID_TRANSACTION_STATE", f"unknown transaction state: {exc.args[0]}") from exc
        return bool(self._lib.wl_transaction_transition_allowed(source, target))

    def evaluation_classify(self, facts: EvaluationFacts) -> EvaluationClassification:
        raw = CEvaluationObservations(
            EVALUATION_ORIGINS[facts.source], EVALUATION_STATUSES[facts.status],
            EVALUATION_CHANNELS[facts.channel], EVALUATION_STAGES[facts.stage],
            int(facts.exit_present), int(facts.exit_integer),
            EVALUATION_SUPERVISION[facts.supervisor], int(facts.supervisor_stopped),
            int(facts.bundle_present), int(facts.bundle_is_mapping),
            int(facts.bundle_stable), int(facts.bundle_changed),
            int(facts.unsatisfied_imports),
        )
        result = CEvaluationClassification()
        code = int(self._lib.wl_evaluation_classify(ctypes.byref(raw), ctypes.byref(result)))
        if code != 0:
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core rejected evaluation observations")
        try:
            return EvaluationClassification(EVALUATION_EXECUTIONS[result.execution],
                                            EVALUATION_OUTCOMES[result.outcome],
                                            EVALUATION_BUNDLES[result.bundle])
        except IndexError as exc:
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core returned an invalid classification") from exc

    @staticmethod
    def _flag(value: object, name: str) -> int:
        # A presence fact is a Boolean the caller established. 0/1 integers, None, or a record
        # are not facts; refusing them keeps a truthiness test from sneaking back in.
        if not isinstance(value, bool):
            raise WorldlineError("INVALID_EVALUATION", f"{name} must be a Boolean fact")
        return 1 if value else 0

    def evaluation_admissible(self, value: EvaluationClassification, *,
                              report_integrity: str, presence: EvidencePresence) -> bool:
        try:
            raw = CEvaluationClassification(EVALUATION_EXECUTIONS.index(value.execution),
                                            EVALUATION_OUTCOMES.index(value.outcome),
                                            EVALUATION_BUNDLES.index(value.bundle))
            report = EVALUATION_REPORTS[report_integrity]
        except (ValueError, KeyError) as exc:
            raise WorldlineError("INVALID_EVALUATION", "unknown evaluation classification") from exc
        if not isinstance(presence, EvidencePresence):
            raise WorldlineError("INVALID_EVALUATION", "evidence presence must be typed facts")
        raw_presence = CEvidencePresence(*(self._flag(getattr(presence, name), name)
                                           for name, _ in CEvidencePresence._fields_))
        code = int(self._lib.wl_evaluation_admissible(ctypes.byref(raw), report,
                                                     ctypes.byref(raw_presence)))
        if code not in (0, 1):
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core rejected evaluation admission")
        return code == 1

    def evaluation_transition_allowed(self, from_state: str, to_state: str) -> bool:
        try:
            source = EVALUATION_EXECUTIONS.index(from_state)
            target = EVALUATION_EXECUTIONS.index(to_state)
        except ValueError as exc:
            raise WorldlineError("INVALID_EVALUATION", "unknown evaluation state") from exc
        code = int(self._lib.wl_evaluation_transition_allowed(source, target))
        if code not in (0, 1):
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core rejected an evaluation transition")
        return code == 1

    def evaluation_advance(self, state: str, requested: str) -> str:
        try:
            current = ctypes.c_uint8(EVALUATION_EXECUTIONS.index(state))
            target = EVALUATION_EXECUTIONS.index(requested)
        except ValueError as exc:
            raise WorldlineError("INVALID_EVALUATION", "unknown evaluation state") from exc
        if int(self._lib.wl_evaluation_advance(ctypes.byref(current), target)) != 0:
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core rejected an evaluation advance")
        try:
            return EVALUATION_EXECUTIONS[current.value]
        except IndexError as exc:
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core returned an invalid state") from exc

    def evaluation_roster_complete(self, admitted: Sequence[bool], *, empty_declared: bool) -> bool:
        """The kernel's roster rule: every required check admitted, and an empty roster only
        when the policy explicitly declared that nothing is required."""
        flags = [self._flag(item, "roster admission") for item in admitted]
        if len(flags) > ROSTER_MAX:
            raise WorldlineError("ROSTER_TOO_LARGE", f"a roster of {len(flags)} checks exceeds {ROSTER_MAX}")
        buffer = (ctypes.c_uint8 * len(flags))(*flags) if flags else None
        address = ctypes.cast(buffer, ctypes.c_void_p) if buffer is not None else ctypes.c_void_p()
        code = int(self._lib.wl_evaluation_roster_complete(
            address, len(flags), self._flag(empty_declared, "empty roster declaration")))
        if code not in (0, 1):
            raise WorldlineError("CORE_INVALID_EVALUATION", "proved core rejected the roster")
        return code == 1

    @staticmethod
    def _optional_hash(value: bytes | None, name: str) -> COptionalHash:
        if value is None:
            return COptionalHash(0, C_HASH())
        if not isinstance(value, (bytes, bytearray)) or len(value) != HASH_BYTES:
            raise WorldlineError("INVALID_HASH", f"{name} is not a 32-byte identity")
        if not any(value):
            # A zero digest is the old sentinel for "nothing"; it must be stated as absent.
            raise WorldlineError("INVALID_HASH", f"{name} is an all-zero digest; pass None for absent")
        return COptionalHash(1, C_HASH.from_buffer_copy(bytes(value)))

    @staticmethod
    def _optional_counter(value: int | None, name: str) -> COptionalCounter:
        if value is None:
            return COptionalCounter(0, (ctypes.c_uint8 * 8)())
        if type(value) is not int or not 0 <= value < 2 ** 64:
            raise WorldlineError("INVALID_EVALUATION", f"{name} is not an unsigned 64-bit counter")
        return COptionalCounter(1, (ctypes.c_uint8 * 8)(*value.to_bytes(8, "little")))

    def collapse_decide(self, value: CollapseInput) -> str:
        if not isinstance(value, CollapseInput):
            raise WorldlineError("INVALID_EVALUATION", "collapse input must be a CollapseInput")
        try:
            state = STATE_CODES[value.candidate_state]
            phase = COLLAPSE_PHASES[value.phase]
            mode = EVALUATION_MODES[value.mode]
            conflicts = MEASUREMENTS[value.conflicts]
            foreign = MEASUREMENTS[value.foreign_writes]
        except KeyError as exc:
            raise WorldlineError("INVALID_EVALUATION", f"unknown collapse category: {exc.args[0]}") from exc
        request = CCollapseRequest(
            state, phase, mode, conflicts, foreign,
            self._flag(value.roster_complete, "roster completeness"),
            self._flag(value.staged_roster_complete, "staged roster completeness"),
            *[self._optional_hash(getattr(value, name), name) for name in COLLAPSE_HASH_FIELDS],
            self._optional_counter(value.generation_before, "generation_before"),
            self._optional_counter(value.generation_after, "generation_after"),
        )
        code = int(self._lib.wl_collapse_decide(ctypes.byref(request)))
        return COLLAPSE_DECISIONS.get(code, f"UNKNOWN_{code}")

    def _raw_collapse_request(self, value: CollapseInput):
        if not isinstance(value, CollapseInput):
            raise WorldlineError("INVALID_EVALUATION", "collapse input must be a CollapseInput")
        try:
            state = STATE_CODES[value.candidate_state]
            phase = COLLAPSE_PHASES[value.phase]
            mode = EVALUATION_MODES[value.mode]
            conflicts = MEASUREMENTS[value.conflicts]
            foreign = MEASUREMENTS[value.foreign_writes]
        except KeyError as exc:
            raise WorldlineError("INVALID_EVALUATION", f"unknown collapse category: {exc.args[0]}") from exc
        request = CCollapseRequest(
            state, phase, mode, conflicts, foreign,
            self._flag(value.roster_complete, "roster completeness"),
            self._flag(value.staged_roster_complete, "staged roster completeness"),
            *[self._optional_hash(getattr(value, name), name) for name in COLLAPSE_HASH_FIELDS],
            self._optional_counter(value.generation_before, "generation_before"),
            self._optional_counter(value.generation_after, "generation_after"),
        )
        return request

    def collapse_raw_dependencies(self, value: CollapseInput):
        from .evaluation_wire import Authority
        return Authority(self).dependencies(self._raw_collapse_request(value))

    def collapse_decide_with_evaluation(self, value: CollapseInput, *, primary, staged, agent) -> str:
        request = self._raw_collapse_request(value)
        from .evaluation_wire import Authority
        return Authority(self).decide(request, primary, staged, agent)
