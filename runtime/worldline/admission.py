"""Resource admission: may WORLDLINE responsibly start this workload right now?

Three things are kept apart here, and keeping them apart is the point of the module.

**Admission state** is what the machine looks like at the instant of the request — MemAvailable,
swap headroom, pressure, disk bytes and inodes, and WORLDLINE's own outstanding reservations. It
decides whether work may start. It is *never* hashed: two runs on otherwise equivalent machines
must not stale each other's evidence because one had 21 GB free and the other 32 GB.

**Enforced resource policy** is what a workload is permitted to consume. It belongs in the
execution context and therefore in `requirementHash`, because changing a ceiling changes what the
workload was allowed to do and so changes what its evidence means.

**Observed telemetry** is what actually happened. It is recorded on the evidence and never
hashed, so a fluctuation cannot invalidate an otherwise identical verification.

A snapshot is not a reservation. Two requests that each observe 20 GB free and each take 16 GB is
the failure this module exists to prevent, so admission is a transaction rather than a probe:

    observe -> lock -> account outstanding reservations -> reserve -> authorize -> unlock

The reservation exists before the workload is spawned and is released deterministically when it
terminates, including when the daemon never saw it terminate — `reconcile` drops any reservation
whose unit the service manager no longer has.

Refusal is an answer. `RESOURCE_STATE_UNKNOWN` is never reported as `RESOURCES_UNAVAILABLE`: a
thing we could not measure is not a thing we measured and found wanting.
"""
from __future__ import annotations

import fcntl
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .errors import WorldlineError

ADMITTED = "ADMITTED"
RESOURCES_UNAVAILABLE = "RESOURCES_UNAVAILABLE"
RESOURCE_STATE_UNKNOWN = "RESOURCE_STATE_UNKNOWN"
RESOURCE_POLICY_INVALID = "RESOURCE_POLICY_INVALID"
RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
OUTCOMES = (ADMITTED, RESOURCES_UNAVAILABLE, RESOURCE_STATE_UNKNOWN, RESOURCE_POLICY_INVALID, RESOURCE_LIMIT_EXCEEDED)

MIB = 1024 * 1024
GIB = 1024 * MIB

# Ceilings a policy may not exceed. An absurd value is a configuration error, not a licence.
MAX_MEMORY_BYTES = 1 << 44          # 16 TiB
MAX_TASKS = 1 << 20
MAX_TIMEOUT_SECONDS = 30 * 24 * 3600
MAX_CONCURRENT = 4096


# ---------------------------------------------------------------------------------------------
# Enforced resource policy — hashed
# ---------------------------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ResourcePolicy:
    """The ceilings a workload is PERMITTED to use.

    This is the only one of the three concerns that enters `requirementHash`. Every field is an
    exact integer: a policy expressed as a fraction of the current machine would smuggle
    admission state into the hash, which is exactly what must not happen.
    """

    memory_max_bytes: int | None = None
    memory_high_bytes: int | None = None
    memory_swap_max_bytes: int | None = None
    cpu_quota_percent: int | None = None
    cpu_weight: int | None = None
    tasks_max: int | None = None
    disk_growth_max_bytes: int | None = None
    timeout_seconds: int | None = None
    max_concurrent_workloads: int | None = None
    enforcement: str = "cgroup2"

    @staticmethod
    def _positive(value: Any, name: str, ceiling: int) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"limits.{name} must be null or an integer")
        if value <= 0:
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"limits.{name} must be positive, got {value}")
        if value > ceiling:
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"limits.{name} exceeds the permitted maximum {ceiling}: {value}")
        return value

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "ResourcePolicy":
        value = dict(value or {})
        known = {"memoryMaxBytes", "memoryHighBytes", "memorySwapMaxBytes", "cpuQuotaPercent",
                 "cpuWeight", "tasksMax", "diskGrowthMaxBytes", "timeoutSeconds",
                 "maxConcurrentWorkloads", "enforcement"}
        unknown = sorted(set(value) - known)
        if unknown:
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"unknown resource policy fields: {', '.join(unknown)}")
        enforcement = value.get("enforcement", "cgroup2")
        if enforcement not in ("cgroup2", "none"):
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"limits.enforcement must be cgroup2 or none, got {enforcement!r}")
        weight = cls._positive(value.get("cpuWeight"), "cpuWeight", 10_000)
        if weight is not None and weight < 1:
            raise WorldlineError(RESOURCE_POLICY_INVALID, "limits.cpuWeight must be between 1 and 10000")
        policy = cls(
            memory_max_bytes=cls._positive(value.get("memoryMaxBytes"), "memoryMaxBytes", MAX_MEMORY_BYTES),
            memory_high_bytes=cls._positive(value.get("memoryHighBytes"), "memoryHighBytes", MAX_MEMORY_BYTES),
            memory_swap_max_bytes=cls._positive(value.get("memorySwapMaxBytes"), "memorySwapMaxBytes", MAX_MEMORY_BYTES),
            cpu_quota_percent=cls._positive(value.get("cpuQuotaPercent"), "cpuQuotaPercent", 100 * 4096),
            cpu_weight=weight,
            tasks_max=cls._positive(value.get("tasksMax"), "tasksMax", MAX_TASKS),
            disk_growth_max_bytes=cls._positive(value.get("diskGrowthMaxBytes"), "diskGrowthMaxBytes", MAX_MEMORY_BYTES),
            timeout_seconds=cls._positive(value.get("timeoutSeconds"), "timeoutSeconds", MAX_TIMEOUT_SECONDS),
            max_concurrent_workloads=cls._positive(value.get("maxConcurrentWorkloads"), "maxConcurrentWorkloads", MAX_CONCURRENT),
            enforcement=enforcement,
        )
        if policy.memory_high_bytes and policy.memory_max_bytes and policy.memory_high_bytes > policy.memory_max_bytes:
            raise WorldlineError(RESOURCE_POLICY_INVALID,
                                 "limits.memoryHighBytes must not exceed limits.memoryMaxBytes")
        return policy

    def canonical(self) -> dict[str, Any]:
        """What goes into requirementHash. Sorted, exact, and free of anything host-dependent."""
        return {
            "memoryMaxBytes": self.memory_max_bytes,
            "memoryHighBytes": self.memory_high_bytes,
            "memorySwapMaxBytes": self.memory_swap_max_bytes,
            "cpuQuotaPercent": self.cpu_quota_percent,
            "cpuWeight": self.cpu_weight,
            "tasksMax": self.tasks_max,
            "diskGrowthMaxBytes": self.disk_growth_max_bytes,
            "timeoutSeconds": self.timeout_seconds,
            "maxConcurrentWorkloads": self.max_concurrent_workloads,
            "enforcement": self.enforcement,
        }

    def unit_properties(self) -> list[str]:
        """systemd properties that put these ceilings on the unit's cgroup.

        They are applied to the UNIT, so every descendant inherits them: an agent that spawns
        Python that spawns a test suite that launches a prover stays inside one boundary.
        Accounting is always on, because telemetry that was never collected is not evidence.
        """
        if self.enforcement != "cgroup2":
            return []
        properties = ["MemoryAccounting=yes", "CPUAccounting=yes", "TasksAccounting=yes", "IOAccounting=yes"]
        if self.memory_max_bytes is not None:
            properties.append(f"MemoryMax={self.memory_max_bytes}")
        if self.memory_high_bytes is not None:
            properties.append(f"MemoryHigh={self.memory_high_bytes}")
        if self.memory_swap_max_bytes is not None:
            properties.append(f"MemorySwapMax={self.memory_swap_max_bytes}")
        if self.cpu_quota_percent is not None:
            properties.append(f"CPUQuota={self.cpu_quota_percent}%")
        if self.cpu_weight is not None:
            properties.append(f"CPUWeight={self.cpu_weight}")
        if self.tasks_max is not None:
            properties.append(f"TasksMax={self.tasks_max}")
        return properties


# ---------------------------------------------------------------------------------------------
# Admission state — never hashed
# ---------------------------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Floors:
    """How much of the machine WORLDLINE refuses to consume, whatever is asked of it."""
    min_free_memory_bytes: int = 2 * GIB
    min_free_disk_bytes: int = 2 * GIB
    min_free_inodes: int = 10_000
    max_memory_pressure_avg10: float = 50.0

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "Floors":
        value = dict(value or {})
        known = {"minFreeMemoryBytes", "minFreeDiskBytes", "minFreeInodes", "maxMemoryPressureAvg10"}
        unknown = sorted(set(value) - known)
        if unknown:
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"unknown admission floor fields: {', '.join(unknown)}")
        def integer(name: str, default: int) -> int:
            item = value.get(name, default)
            if isinstance(item, bool) or not isinstance(item, int) or item < 0:
                raise WorldlineError(RESOURCE_POLICY_INVALID, f"admission.{name} must be a non-negative integer")
            return item
        pressure = value.get("maxMemoryPressureAvg10", 50.0)
        if isinstance(pressure, bool) or not isinstance(pressure, (int, float)) or not (0 <= float(pressure) <= 100):
            raise WorldlineError(RESOURCE_POLICY_INVALID, "admission.maxMemoryPressureAvg10 must be between 0 and 100")
        return cls(
            min_free_memory_bytes=integer("minFreeMemoryBytes", 2 * GIB),
            min_free_disk_bytes=integer("minFreeDiskBytes", 2 * GIB),
            min_free_inodes=integer("minFreeInodes", 10_000),
            max_memory_pressure_avg10=float(pressure),
        )


def _read_meminfo(root: Path) -> dict[str, int]:
    text = (root / "proc/meminfo").read_text(encoding="utf-8")
    values: dict[str, int] = {}
    for line in text.splitlines():
        name, separator, rest = line.partition(":")
        if not separator:
            continue
        parts = rest.split()
        if parts and parts[0].isdigit():
            values[name] = int(parts[0]) * 1024 if len(parts) > 1 and parts[1] == "kB" else int(parts[0])
    for required in ("MemTotal", "MemAvailable"):
        if required not in values:
            raise ValueError(f"/proc/meminfo has no {required}")
    return values


def _read_pressure(path: Path) -> dict[str, float]:
    """`some avg10=0.00 avg60=0.00 avg300=0.00 total=0`. A file we cannot parse is UNKNOWN."""
    values: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts or parts[0] not in ("some", "full"):
            continue
        for item in parts[1:]:
            key, separator, raw = item.partition("=")
            if not separator:
                continue
            if key.startswith("avg"):
                values[f"{parts[0]}.{key}"] = float(raw)
    if "some.avg10" not in values:
        raise ValueError(f"{path} has no `some avg10=`")
    return values


@dataclass(frozen=True, slots=True)
class AdmissionState:
    state: str                      # OBSERVED | UNKNOWN
    reason: str | None = None
    mem_total_bytes: int | None = None
    mem_available_bytes: int | None = None
    swap_free_bytes: int | None = None
    memory_pressure_avg10: float | None = None
    cpu_pressure_avg10: float | None = None
    io_pressure_avg10: float | None = None
    disk: dict[str, dict[str, int]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state, "reason": self.reason,
            "memTotalBytes": self.mem_total_bytes, "memAvailableBytes": self.mem_available_bytes,
            "swapFreeBytes": self.swap_free_bytes,
            "pressure": {"memoryAvg10": self.memory_pressure_avg10,
                         "cpuAvg10": self.cpu_pressure_avg10, "ioAvg10": self.io_pressure_avg10},
            "disk": self.disk,
        }


def observe(paths: Mapping[str, Path] | None = None, *, root: Path = Path("/")) -> AdmissionState:
    """Measure the machine. Anything unreadable or unparseable makes the whole state UNKNOWN,
    because a partially observed machine is not a machine we may reason about."""
    try:
        meminfo = _read_meminfo(root)
    except (OSError, ValueError) as exc:
        return AdmissionState(state="UNKNOWN", reason=f"/proc/meminfo: {exc}")
    pressures: dict[str, float | None] = {}
    for name in ("memory", "cpu", "io"):
        path = root / f"proc/pressure/{name}"
        try:
            pressures[name] = _read_pressure(path)["some.avg10"]
        except FileNotFoundError:
            # Pressure accounting compiled out is a known shape, not a broken read. Memory
            # pressure is the one this engine gates on, so only that absence is fatal.
            if name == "memory":
                return AdmissionState(state="UNKNOWN", reason=f"{path} is absent: no memory pressure accounting")
            pressures[name] = None
        except (OSError, ValueError) as exc:
            return AdmissionState(state="UNKNOWN", reason=f"{path}: {exc}")
    disk: dict[str, dict[str, int]] = {}
    for name, path in dict(paths or {}).items():
        try:
            stat = os.statvfs(path)
        except OSError as exc:
            return AdmissionState(state="UNKNOWN", reason=f"statvfs({path}): {exc}")
        disk[name] = {"freeBytes": stat.f_bavail * stat.f_frsize, "freeInodes": stat.f_favail,
                      "totalBytes": stat.f_blocks * stat.f_frsize}
    return AdmissionState(
        state="OBSERVED",
        mem_total_bytes=meminfo["MemTotal"],
        mem_available_bytes=meminfo["MemAvailable"],
        swap_free_bytes=meminfo.get("SwapFree"),
        memory_pressure_avg10=pressures["memory"],
        cpu_pressure_avg10=pressures["cpu"],
        io_pressure_avg10=pressures["io"],
        disk=disk,
    )


# ---------------------------------------------------------------------------------------------
# The reservation ledger
# ---------------------------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Reservation:
    reservation_id: str
    workload: str
    unit: str | None
    memory_bytes: int
    tasks: int
    created_at: float
    owner_pid: int

    def as_dict(self) -> dict[str, Any]:
        return {"reservationId": self.reservation_id, "workload": self.workload, "unit": self.unit,
                "memoryBytes": self.memory_bytes, "tasks": self.tasks,
                "createdAt": self.created_at, "ownerPid": self.owner_pid}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Reservation":
        return cls(reservation_id=str(value["reservationId"]), workload=str(value.get("workload", "")),
                   unit=value.get("unit"), memory_bytes=int(value.get("memoryBytes", 0)),
                   tasks=int(value.get("tasks", 0)), created_at=float(value.get("createdAt", 0.0)),
                   owner_pid=int(value.get("ownerPid", 0)))


class Ledger:
    """Reservations, on disk, guarded by an exclusive file lock.

    On disk because a daemon restart must not lose track of workloads that are still running, and
    in the runtime directory because a reboot legitimately clears both the workloads and their
    reservations. Locked with `flock` because the window between observing free memory and taking
    it is exactly where two admissions can both succeed — and because a second WORLDLINE instance
    (the health check, a test harness) must contend for the same ledger rather than keep its own.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "admission-ledger.json"
        self.lock_path = self.directory / "admission.lock"

    class _Locked:
        def __init__(self, ledger: "Ledger") -> None:
            self.ledger = ledger
            self.handle = None

        def __enter__(self) -> "Ledger._Locked":
            self.handle = open(self.ledger.lock_path, "a+b")
            try:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
            except OSError:
                self.handle.close()
                raise
            return self

        def __exit__(self, *exc: Any) -> None:
            if self.handle is not None:
                try:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
                finally:
                    self.handle.close()
                    self.handle = None

    def locked(self) -> "Ledger._Locked":
        return Ledger._Locked(self)

    def _load(self) -> list[Reservation]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (OSError, json.JSONDecodeError) as exc:
            # A ledger we cannot read is not an empty ledger. Treating it as empty would admit
            # everything at exactly the moment the accounting broke.
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, f"the admission ledger is unreadable: {exc}") from exc
        if not isinstance(raw, dict) or not isinstance(raw.get("reservations"), list):
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, "the admission ledger has an unexpected shape")
        out: list[Reservation] = []
        for item in raw["reservations"]:
            try:
                out.append(Reservation.from_dict(item))
            except (KeyError, TypeError, ValueError) as exc:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN, f"the admission ledger holds a bad record: {exc}") from exc
        return out

    def _store(self, reservations: Sequence[Reservation]) -> None:
        document = {"schemaVersion": 1, "updatedAt": time.time(),
                    "reservations": [r.as_dict() for r in reservations]}
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, self.path)

    # -- operations, each taking the lock unless one is already held -----------------------------
    def outstanding(self) -> list[Reservation]:
        with self.locked():
            return self._load()

    def add(self, reservation: Reservation) -> None:
        with self.locked():
            self._store([*self._load(), reservation])

    def release(self, reservation_id: str) -> bool:
        with self.locked():
            current = self._load()
            remaining = [r for r in current if r.reservation_id != reservation_id]
            if len(remaining) == len(current):
                return False
            self._store(remaining)
            return True

    def attach_unit(self, reservation_id: str, unit: str) -> None:
        with self.locked():
            current = self._load()
            self._store([
                Reservation(r.reservation_id, r.workload, unit, r.memory_bytes, r.tasks, r.created_at, r.owner_pid)
                if r.reservation_id == reservation_id else r
                for r in current
            ])

    def reconcile(self, is_live: Callable[[Reservation], bool]) -> list[Reservation]:
        """Drop reservations whose workload is gone. This is what makes a reservation survive a
        daemon that died between spawning and releasing: the truth is the service manager's, not
        ours, so anything it no longer has is released here rather than held forever."""
        with self.locked():
            current = self._load()
            live = [r for r in current if is_live(r)]
            dropped = [r for r in current if r not in live]
            if dropped:
                self._store(live)
            return dropped


# ---------------------------------------------------------------------------------------------
# The admission authority
# ---------------------------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Decision:
    outcome: str
    reason: str
    reservation_id: str | None = None
    arithmetic: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)

    @property
    def admitted(self) -> bool:
        return self.outcome == ADMITTED

    def as_dict(self) -> dict[str, Any]:
        return {"outcome": self.outcome, "reason": self.reason, "reservationId": self.reservation_id,
                "arithmetic": self.arithmetic, "admissionState": self.state, "enforcedPolicy": self.policy,
                "nonClaims": [
                    "Admission reserves against WORLDLINE's own ledger and the machine's observed"
                    " state. Another process may take the memory a microsecond later, so this"
                    " reduces the chance of starting work that cannot finish; it does not"
                    " guarantee completion.",
                    "WORLDLINE governs the workloads it starts. It does not police the host and"
                    " will not stop anything it did not start.",
                ]}


class AdmissionAuthority:
    """The one place that answers "may this start?".

    Every expensive operation asks here before executing, and nothing spawns supervised work
    without holding a reservation. The lock is held across observe-account-reserve so the answer
    cannot be overtaken between being computed and being acted on.
    """

    def __init__(self, ledger: Ledger, floors: Floors, *, paths: Mapping[str, Path] | None = None,
                 observer: Callable[[], AdmissionState] | None = None,
                 usage: Callable[[Reservation], int | None] | None = None,
                 is_live: Callable[[Reservation], bool] | None = None) -> None:
        self.ledger = ledger
        self.floors = floors
        self.paths = dict(paths or {})
        self._observer = observer or (lambda: observe(self.paths))
        # How much of a reservation is already reflected in MemAvailable. Counting a running
        # workload's reservation in full on top of the memory it has already taken would refuse
        # work the machine can actually do; counting none of it would overcommit. Only the
        # UNUSED part of a reservation is withheld.
        self._usage = usage or (lambda reservation: None)
        self._is_live = is_live or (lambda reservation: True)

    def outstanding_withheld(self, reservations: Sequence[Reservation]) -> tuple[int, list[dict[str, Any]]]:
        total = 0
        detail: list[dict[str, Any]] = []
        for reservation in reservations:
            used = self._usage(reservation)
            withheld = reservation.memory_bytes if used is None else max(0, reservation.memory_bytes - used)
            total += withheld
            detail.append({"reservationId": reservation.reservation_id, "workload": reservation.workload,
                           "reservedBytes": reservation.memory_bytes,
                           "observedUsageBytes": used, "withheldBytes": withheld})
        return total, detail

    def admit(self, *, workload: str, policy: ResourcePolicy, memory_bytes: int | None = None) -> Decision:
        """observe -> lock -> account -> reserve -> authorize. The lock spans all four."""
        if not isinstance(workload, str) or not workload:
            return Decision(RESOURCE_POLICY_INVALID, "a workload name is required")
        request_bytes = memory_bytes if memory_bytes is not None else policy.memory_max_bytes
        if request_bytes is None:
            return Decision(RESOURCE_POLICY_INVALID,
                            "no memory ceiling: admission cannot account for a workload whose"
                            " appetite is undeclared. Set limits.memoryMaxBytes.",
                            policy=policy.canonical())
        if isinstance(request_bytes, bool) or not isinstance(request_bytes, int) or request_bytes <= 0:
            return Decision(RESOURCE_POLICY_INVALID, f"requested memory must be a positive integer, got {request_bytes!r}",
                            policy=policy.canonical())
        if request_bytes > MAX_MEMORY_BYTES:
            return Decision(RESOURCE_POLICY_INVALID, f"requested memory exceeds the permitted maximum: {request_bytes}",
                            policy=policy.canonical())

        state = self._observer()
        if state.state != "OBSERVED":
            return Decision(RESOURCE_STATE_UNKNOWN,
                            f"the machine's resource state could not be observed: {state.reason}",
                            state=state.as_dict(), policy=policy.canonical())

        with self.ledger.locked() as handle:
            try:
                current = [r for r in self.ledger._load() if self._is_live(r)]
            except WorldlineError as exc:
                return Decision(RESOURCE_STATE_UNKNOWN, str(exc.args[1] if len(exc.args) > 1 else exc),
                                state=state.as_dict(), policy=policy.canonical())
            withheld, detail = self.outstanding_withheld(current)
            assert state.mem_available_bytes is not None
            headroom = state.mem_available_bytes - withheld - self.floors.min_free_memory_bytes
            arithmetic = {
                "requestedBytes": request_bytes,
                "memAvailableBytes": state.mem_available_bytes,
                "withheldByReservationsBytes": withheld,
                "reservations": detail,
                "floorBytes": self.floors.min_free_memory_bytes,
                "headroomBytes": headroom,
                "outstandingCount": len(current),
            }

            limit = policy.max_concurrent_workloads
            if limit is not None and len(current) >= limit:
                return Decision(RESOURCES_UNAVAILABLE,
                                f"{len(current)} workloads already admitted and the concurrency ceiling is {limit}",
                                arithmetic=arithmetic, state=state.as_dict(), policy=policy.canonical())

            if state.memory_pressure_avg10 is not None and state.memory_pressure_avg10 > self.floors.max_memory_pressure_avg10:
                return Decision(RESOURCES_UNAVAILABLE,
                                f"memory pressure avg10 is {state.memory_pressure_avg10:.2f}, above the"
                                f" configured ceiling of {self.floors.max_memory_pressure_avg10:.2f}",
                                arithmetic=arithmetic, state=state.as_dict(), policy=policy.canonical())

            for name, values in state.disk.items():
                if values["freeBytes"] < self.floors.min_free_disk_bytes:
                    return Decision(RESOURCES_UNAVAILABLE,
                                    f"{name} has {values['freeBytes']} bytes free, below the floor of"
                                    f" {self.floors.min_free_disk_bytes}",
                                    arithmetic=arithmetic, state=state.as_dict(), policy=policy.canonical())
                if values["freeInodes"] < self.floors.min_free_inodes:
                    return Decision(RESOURCES_UNAVAILABLE,
                                    f"{name} has {values['freeInodes']} inodes free, below the floor of"
                                    f" {self.floors.min_free_inodes}",
                                    arithmetic=arithmetic, state=state.as_dict(), policy=policy.canonical())

            if request_bytes > headroom:
                return Decision(RESOURCES_UNAVAILABLE,
                                f"{request_bytes} bytes requested but only {headroom} are free to promise:"
                                f" {state.mem_available_bytes} available, {withheld} withheld by"
                                f" {len(current)} outstanding reservation(s), {self.floors.min_free_memory_bytes} held back as the floor",
                                arithmetic=arithmetic, state=state.as_dict(), policy=policy.canonical())

            reservation = Reservation(
                reservation_id=str(uuid.uuid4()), workload=workload, unit=None,
                memory_bytes=request_bytes, tasks=policy.tasks_max or 0,
                created_at=time.time(), owner_pid=os.getpid(),
            )
            self.ledger._store([*current, reservation])

        return Decision(ADMITTED, f"{request_bytes} bytes reserved against {headroom} of headroom",
                        reservation_id=reservation.reservation_id, arithmetic=arithmetic,
                        state=state.as_dict(), policy=policy.canonical())

    def release(self, reservation_id: str | None) -> bool:
        return bool(reservation_id) and self.ledger.release(str(reservation_id))

    def attach_unit(self, reservation_id: str | None, unit: str) -> None:
        if reservation_id:
            self.ledger.attach_unit(str(reservation_id), unit)

    def reconcile(self) -> list[Reservation]:
        return self.ledger.reconcile(self._is_live)

    def report(self, policy: ResourcePolicy) -> dict[str, Any]:
        """What `doctor` shows: the inputs, the floors, and whether work would be admitted now."""
        state = self._observer()
        try:
            current = self.ledger.outstanding()
            ledger_error = None
        except WorldlineError as exc:
            current, ledger_error = [], str(exc.args[1] if len(exc.args) > 1 else exc)
        withheld, detail = self.outstanding_withheld(current)
        headroom = None
        if state.state == "OBSERVED" and state.mem_available_bytes is not None:
            headroom = state.mem_available_bytes - withheld - self.floors.min_free_memory_bytes
        return {
            "state": state.as_dict(),
            "floors": {"minFreeMemoryBytes": self.floors.min_free_memory_bytes,
                       "minFreeDiskBytes": self.floors.min_free_disk_bytes,
                       "minFreeInodes": self.floors.min_free_inodes,
                       "maxMemoryPressureAvg10": self.floors.max_memory_pressure_avg10},
            "enforcedPolicy": policy.canonical(),
            "outstandingReservations": detail,
            "withheldBytes": withheld,
            "headroomBytes": headroom,
            "ledgerError": ledger_error,
            "wouldAdmitNow": None if state.state != "OBSERVED" or ledger_error else (
                policy.memory_max_bytes is not None and headroom is not None
                and policy.memory_max_bytes <= headroom),
        }
