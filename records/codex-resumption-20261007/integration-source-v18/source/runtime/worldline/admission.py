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

    lock -> observe -> account outstanding reservations -> reserve -> authorize -> unlock

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
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .errors import CoreUnavailable, WorldlineError
from .resource_ledger import compute_ledger as kernel_compute_ledger
from .resource_ledger import compute_headroom as kernel_compute_headroom
from .resource_policy import PolicyDecision, decide_policy as kernel_decide_policy

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

        They are applied to the UNIT, so a cooperative process tree inherits them: an agent that
        spawns Python that spawns a test suite that launches a prover stays inside one boundary.
        Accounting is always on, because telemetry that was never collected is not evidence.

        What this is NOT, measured rather than assumed: `systemd-run --user` places the unit
        under a slice systemd delegates to the invoking uid, so a workload running as that uid
        can create a sibling cgroup beside its own unit and move itself into it, escaping the
        ceiling and the accounting both. Every shipped call site puts the workload inside the
        bubblewrap sandbox, where /sys is read-only, user namespaces are disabled and the
        session bus is absent, and a control shows the escape fails there. So the cgroup is the
        budget for a workload that is not trying to leave it, and the sandbox is what stops one
        that is. Neither alone is the boundary.
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
    # Pressure in hundredths of a percent, as an integer. The wire protocol is canonical JSON,
    # which has no float: a value that cannot be represented exactly has no business being an
    # identity or a threshold.
    max_memory_pressure_hundredths: int = 5000

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "Floors":
        value = dict(value or {})
        known = {"minFreeMemoryBytes", "minFreeDiskBytes", "minFreeInodes", "maxMemoryPressureHundredths"}
        unknown = sorted(set(value) - known)
        if unknown:
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"unknown admission floor fields: {', '.join(unknown)}")
        def integer(name: str, default: int) -> int:
            item = value.get(name, default)
            if isinstance(item, bool) or not isinstance(item, int) or item < 0:
                raise WorldlineError(RESOURCE_POLICY_INVALID, f"admission.{name} must be a non-negative integer")
            return item
        pressure = value.get("maxMemoryPressureHundredths", 5000)
        if isinstance(pressure, bool) or not isinstance(pressure, int) or not (0 <= pressure <= 10_000):
            raise WorldlineError(RESOURCE_POLICY_INVALID,
                                 "admission.maxMemoryPressureHundredths must be an integer between 0 and 10000")
        return cls(
            min_free_memory_bytes=integer("minFreeMemoryBytes", 2 * GIB),
            min_free_disk_bytes=integer("minFreeDiskBytes", 2 * GIB),
            min_free_inodes=integer("minFreeInodes", 10_000),
            max_memory_pressure_hundredths=pressure,
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


def _read_pressure(path: Path) -> dict[str, int]:
    """`some avg10=0.00 avg60=0.00 avg300=0.00 total=0`, read as integer hundredths of a percent.
    A file we cannot parse is UNKNOWN."""
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts or parts[0] not in ("some", "full"):
            continue
        for item in parts[1:]:
            key, separator, raw = item.partition("=")
            if not separator:
                continue
            if key.startswith("avg"):
                reading = float(raw)
                if reading != reading or reading in (float("inf"), float("-inf")) or not (0.0 <= reading <= 100.0):
                    raise ValueError(f"pressure {key}={raw} is not a percentage")
                values[f"{parts[0]}.{key}"] = round(reading * 100)
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
    memory_pressure_hundredths: int | None = None
    cpu_pressure_hundredths: int | None = None
    io_pressure_hundredths: int | None = None
    disk: dict[str, dict[str, int]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state, "reason": self.reason,
            "memTotalBytes": self.mem_total_bytes, "memAvailableBytes": self.mem_available_bytes,
            "swapFreeBytes": self.swap_free_bytes,
            "pressureHundredths": {"memoryAvg10": self.memory_pressure_hundredths,
                                   "cpuAvg10": self.cpu_pressure_hundredths,
                                   "ioAvg10": self.io_pressure_hundredths},
            "disk": self.disk,
        }


def observe(paths: Mapping[str, Path] | None = None, *, root: Path = Path("/")) -> AdmissionState:
    """Measure the machine. Anything unreadable or unparseable makes the whole state UNKNOWN,
    because a partially observed machine is not a machine we may reason about."""
    try:
        meminfo = _read_meminfo(root)
    except (OSError, ValueError, ArithmeticError) as exc:
        return AdmissionState(state="UNKNOWN", reason=f"/proc/meminfo: {exc}")
    # A reading that cannot be true is not a measurement. A corrupt MemAvailable of 1 PiB on a
    # 31 GiB machine licensed an 8 TiB admission, so implausibility is refused as UNKNOWN rather
    # than trusted because it happened to parse.
    if meminfo["MemTotal"] <= 0 or not (0 <= meminfo["MemAvailable"] <= meminfo["MemTotal"]):
        return AdmissionState(state="UNKNOWN",
                              reason=f"/proc/meminfo is not plausible: MemAvailable={meminfo['MemAvailable']}"
                                     f" of MemTotal={meminfo['MemTotal']}")
    pressures: dict[str, int | None] = {}
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
        except (OSError, ValueError, ArithmeticError) as exc:
            # ArithmeticError covers OverflowError, which `inf` and an overflowing exponent raise
            # out of round() — those escaped as tracebacks rather than refusals.
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
        memory_pressure_hundredths=pressures["memory"],
        cpu_pressure_hundredths=pressures["cpu"],
        io_pressure_hundredths=pressures["io"],
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
    created_at_ms: int
    owner_pid: int
    workload_identity: dict[str, str] | None = None

    def as_dict(self) -> dict[str, Any]:
        result = {"reservationId": self.reservation_id, "workload": self.workload, "unit": self.unit,
                "memoryBytes": self.memory_bytes, "tasks": self.tasks,
                "createdAtMs": self.created_at_ms, "ownerPid": self.owner_pid}
        if self.workload_identity is not None:
            result["workloadIdentity"] = self.workload_identity
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Reservation":
        return cls(reservation_id=str(value["reservationId"]), workload=str(value.get("workload", "")),
                   unit=value.get("unit"), memory_bytes=int(value.get("memoryBytes", 0)),
                   tasks=int(value.get("tasks", 0)), created_at_ms=int(value.get("createdAtMs", 0)),
                   owner_pid=int(value.get("ownerPid", 0)),
                   workload_identity=value.get("workloadIdentity"))


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
            descriptor = os.open(self.ledger.lock_path, os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_CLOEXEC, 0o600)
            try:
                os.fchmod(descriptor, 0o600)  # also a lock left 0644 by an older build
                self.handle = os.fdopen(descriptor, "a+b")
                descriptor = None  # the stream owns the lock descriptor
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
            except BaseException as primary:
                try:
                    if self.handle is not None:
                        self.handle.close()
                    elif descriptor is not None:
                        os.close(descriptor)
                except BaseException as cleanup:
                    primary.add_note("admission lock close also failed: " + str(cleanup))
                self.handle = None
                raise
            return self

        def __exit__(self, *exc: Any) -> None:
            if self.handle is not None:
                primary = exc[1] if len(exc) > 1 else None
                cleanup_primary = None
                try:
                    try:
                        fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
                    except BaseException as cleanup:
                        if primary is not None:
                            primary.add_note("admission unlock also failed: " + str(cleanup))
                        else:
                            cleanup_primary = cleanup
                finally:
                    try:
                        self.handle.close()
                    except BaseException as cleanup:
                        retained = primary if primary is not None else cleanup_primary
                        if retained is not None:
                            retained.add_note("admission lock close also failed: " + str(cleanup))
                        else:
                            cleanup_primary = cleanup
                    self.handle = None
                if primary is None and cleanup_primary is not None:
                    raise cleanup_primary

    def locked(self) -> "Ledger._Locked":
        return Ledger._Locked(self)

    def _load(self) -> list[Reservation]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        # Deliberately broad. A ledger is an untrusted file on disk, and three shapes escaped a
        # narrower guard as tracebacks rather than refusals: invalid UTF-8 (UnicodeDecodeError),
        # a JSON `Infinity` (OverflowError once used), and a deeply nested document
        # (RecursionError). An exception that is not a refusal is not an answer.
        except RecursionError as exc:
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, f"the admission ledger is too deeply nested: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            # A ledger we cannot read is not an empty ledger. Treating it as empty would admit
            # everything at exactly the moment the accounting broke.
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, f"the admission ledger is unreadable: {exc}") from exc
        if not isinstance(raw, dict) or not isinstance(raw.get("reservations"), list):
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, "the admission ledger has an unexpected shape")
        out: list[Reservation] = []
        for item in raw["reservations"]:
            try:
                reservation = Reservation.from_dict(item)
            except RecursionError as exc:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN, f"an admission record is too deeply nested: {exc}") from exc
            except Exception as exc:  # noqa: BLE001
                raise WorldlineError(RESOURCE_STATE_UNKNOWN, f"the admission ledger holds a bad record: {exc}") from exc
            # A negative reservation manufactures headroom: withholding -12 GiB turns a correct
            # refusal into an admission. A record that cannot be true is a broken ledger.
            if reservation.memory_bytes < 0 or reservation.tasks < 0:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN,
                                     f"admission record {reservation.reservation_id} holds a negative quantity")
            if reservation.memory_bytes > MAX_MEMORY_BYTES:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN,
                                     f"admission record {reservation.reservation_id} reserves an impossible"
                                     f" {reservation.memory_bytes} bytes")
            if reservation.unit is not None and not isinstance(reservation.unit, str):
                raise WorldlineError(RESOURCE_STATE_UNKNOWN, "an admission record names a non-string unit")
            out.append(reservation)
        seen = [r.reservation_id for r in out]
        if len(set(seen)) != len(seen):
            # Two records with one id: releasing either removed both, and 4 GiB of accounting
            # vanished on a single release.
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, "the admission ledger holds duplicate reservation ids")
        return out

    def _store(self, reservations: Sequence[Reservation]) -> None:
        document = {"schemaVersion": 1, "updatedAtMs": int(time.time() * 1000),
                    "reservations": [r.as_dict() for r in reservations]}
        # Serialize before acquiring a temporary file. Success requires both
        # the new file and the replacement directory entry to be flushed.
        content = json.dumps(document, indent=2) + "\n"
        directory = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        temporary = None
        descriptor = None
        stream = None
        primary = None
        try:
            descriptor, temporary = tempfile.mkstemp(prefix=".admission-ledger-", dir=self.directory)
            os.fchmod(descriptor, 0o600)
            stream = os.fdopen(descriptor, "w", encoding="utf-8")
            descriptor = None  # stream now owns it, including failed flushes
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            stream.close()
            stream = None
            os.replace(temporary, self.path)
            temporary = None  # replacement may be uncertain if directory fsync fails
            os.fsync(directory)
        except BaseException as error:
            primary = error
            raise
        finally:
            cleanup_primary = None
            def cleanup(operation, description):
                nonlocal cleanup_primary
                try:
                    operation()
                except BaseException as error:
                    retained = primary if primary is not None else cleanup_primary
                    if retained is not None:
                        retained.add_note(description + " also failed: " + str(error))
                    else:
                        cleanup_primary = error
            if stream is not None:
                cleanup(stream.close, "admission temporary stream close")
            if descriptor is not None:
                cleanup(lambda: os.close(descriptor), "admission temporary descriptor close")
            if temporary is not None:
                cleanup(lambda: os.unlink(temporary), "admission temporary removal")
            cleanup(lambda: os.close(directory), "admission directory close")
            if primary is None and cleanup_primary is not None:
                raise cleanup_primary

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

    def release_exact(self, reservation_id: str) -> bool:
        """Kernel-backed path for the authority's already-normalized string ID.

        The original direct release API below its own lock remains unchanged;
        custom Python equality is a separate unresolved authority domain.
        """
        from .reservation_lifecycle import release_plan
        with self.locked():
            current = self._load()
            try:
                removed = release_plan([r.reservation_id for r in current], reservation_id)
            except CoreUnavailable as exc:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN,
                                     f"reservation release plan unavailable: {exc}") from exc
            if not any(removed):
                return False
            self._store([r for r, drop in zip(current, removed) if not drop])
            return True

    def attach_unit(self, reservation_id: str, unit: str) -> None:
        if not isinstance(unit, str) or not unit or "\n" in unit or "/" in unit:
            raise WorldlineError(RESOURCE_POLICY_INVALID, f"a reservation cannot name this unit: {unit!r}")
        with self.locked():
            current = self._load()
            self._store([
                Reservation(r.reservation_id, r.workload, unit, r.memory_bytes, r.tasks, r.created_at_ms, r.owner_pid,
                            r.workload_identity if r.unit == unit else None)
                if r.reservation_id == reservation_id else r
                for r in current
            ])

    def attach_process_identity(self, reservation_id: str, identity: Any) -> None:
        from .linux.systemd import WorkloadIdentity
        if not isinstance(identity, WorkloadIdentity):
            raise WorldlineError(RESOURCE_STATE_UNKNOWN, "check workload identity was not observed")
        with self.locked():
            current = self._load()
            matching = [r for r in current if r.reservation_id == reservation_id]
            if len(matching) != 1 or matching[0].unit != identity.unit:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN, "check reservation/unit identity differs")
            witness = {"unit": identity.unit, "invocationId": identity.invocation_id,
                       "controlGroup": identity.control_group}
            self._store([
                Reservation(r.reservation_id, r.workload, r.unit, r.memory_bytes, r.tasks,
                            r.created_at_ms, r.owner_pid, witness)
                if r.reservation_id == reservation_id else r for r in current
            ])

    def reconcile(self, is_live: Callable[[Reservation], bool | None]) -> list[Reservation]:
        """Drop reservations whose workload is gone. This is what makes a reservation survive a
        daemon that died between spawning and releasing: the truth is the service manager's, not
        ours, so anything it no longer has is released here rather than held forever."""
        with self.locked():
            current = self._load()
            # Three answers, not two. `None` means the manager could not tell us, and a
            # reservation we cannot ask about is KEPT: freeing it would promise a running
            # workload's memory to somebody else. A callback that raises is the same as None —
            # a foreign unit name in the ledger used to wedge reconcile permanently.
            def verdict(reservation: Reservation) -> bool | None:
                try:
                    return is_live(reservation)
                except Exception:  # noqa: BLE001
                    return None
            observations = [verdict(r) for r in current]
            from .reservation_lifecycle import reconcile_plan
            try:
                removed = reconcile_plan([r.reservation_id for r in current], observations)
            except CoreUnavailable as exc:
                raise WorldlineError(RESOURCE_STATE_UNKNOWN,
                                     f"reservation reconciliation plan unavailable: {exc}") from exc
            dropped = [r for r, drop in zip(current, removed) if drop]
            live = [r for r, drop in zip(current, removed) if not drop]
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
        observed = []
        detail: list[dict[str, Any]] = []
        for reservation in reservations:
            used = self._usage(reservation)
            observed.append((reservation.memory_bytes, used))
            detail.append({"reservationId": reservation.reservation_id, "workload": reservation.workload,
                           "reservedBytes": reservation.memory_bytes,
                           "observedUsageBytes": used, "withheldBytes": None})
        try:
            projection = kernel_compute_ledger(observed)
        except CoreUnavailable as exc:
            # Keep observations already gathered, but no guessed accounting.
            raise CoreUnavailable(exc.message, **{**exc.details, "reservations": detail}) from exc
        for item, withheld in zip(detail, projection.withheld):
            item["withheldBytes"] = withheld
        return projection.total, detail

    def _numeric_policy(self, state: AdmissionState, policy: ResourcePolicy,
                        outstanding_count: int, withheld: int,
                        requested: int) -> tuple[PolicyDecision, tuple[tuple[str, int, int], ...]]:
        # Preserve the original filesystem iteration order and the exact values
        # used to format a returned refusal. A stable producer snapshot remains
        # an independent obligation; this copy alone does not establish it.
        rows = tuple((name, values["freeBytes"], values["freeInodes"])
                     for name, values in state.disk.items())
        numeric = kernel_decide_policy(
            outstanding_count=outstanding_count,
            concurrency_limit=policy.max_concurrent_workloads,
            memory_pressure=state.memory_pressure_hundredths,
            memory_pressure_ceiling=self.floors.max_memory_pressure_hundredths,
            disks=tuple((free_bytes, free_inodes) for _, free_bytes, free_inodes in rows),
            disk_byte_floor=self.floors.min_free_disk_bytes,
            disk_inode_floor=self.floors.min_free_inodes,
            available_memory=state.mem_available_bytes,
            withheld_memory=withheld, memory_floor=self.floors.min_free_memory_bytes,
            requested_memory=requested)
        return numeric, rows

    def _numeric_refusal_reason(self, numeric: PolicyDecision,
                                rows: tuple[tuple[str, int, int], ...],
                                state: AdmissionState, policy: ResourcePolicy,
                                outstanding_count: int, withheld: int,
                                requested: int, headroom: int) -> str:
        # This dispatch formats the kernel's result; it never compares a resource
        # quantity to grant/refuse admission. The binding validates the full schema.
        if numeric.gate == "CONCURRENCY":
            return (f"{outstanding_count} workloads already admitted and the concurrency ceiling is "
                    f"{policy.max_concurrent_workloads}")
        if numeric.gate == "PRESSURE":
            return (f"memory pressure avg10 is {state.memory_pressure_hundredths / 100:.2f}%, above the"
                    f" configured ceiling of {self.floors.max_memory_pressure_hundredths / 100:.2f}%")
        if numeric.gate == "DISK_BYTES":
            name, free_bytes, _ = rows[numeric.disk_index]
            return (f"{name} has {free_bytes} bytes free, below the floor of"
                    f" {self.floors.min_free_disk_bytes}")
        if numeric.gate == "DISK_INODES":
            name, _, free_inodes = rows[numeric.disk_index]
            return (f"{name} has {free_inodes} inodes free, below the floor of"
                    f" {self.floors.min_free_inodes}")
        if numeric.gate == "CAPACITY":
            return (f"{requested} bytes requested but only {headroom} are free to promise:"
                    f" {state.mem_available_bytes} available, {withheld} withheld by"
                    f" {outstanding_count} outstanding reservation(s), {self.floors.min_free_memory_bytes} held back as the floor")
        raise WorldlineError(RESOURCE_STATE_UNKNOWN, "resource policy result has no known refusal reason")

    def admit(self, *, workload: str, policy: ResourcePolicy, memory_bytes: int | None = None) -> Decision:
        """lock -> observe -> account -> reserve -> authorize -> unlock."""
        if not isinstance(workload, str) or not workload:
            return Decision(RESOURCE_POLICY_INVALID, "a workload name is required")
        # A policy with no declared ceiling is the default, and refusing it would stop every
        # existing installation from forking anything. So an undeclared appetite is admitted
        # UNMETERED rather than refused: the workload reserves nothing, because inventing a
        # number would be a guess dressed as accounting, and every other gate still applies —
        # the machine must still have free memory, tolerable pressure and disk headroom. The
        # decision says `accounted: false` so nobody mistakes this for a budget.
        # memoryHigh is a ceiling too — a policy that declares only a high watermark was being
        # admitted unmetered while the kernel was handed a real MemoryHigh, so the decision said
        # "nothing is enforced" about a unit that was being throttled.
        declared = policy.memory_max_bytes if policy.memory_max_bytes is not None else policy.memory_high_bytes
        unmetered = memory_bytes is None and declared is None
        request_bytes = 0 if unmetered else (memory_bytes if memory_bytes is not None else declared)
        if unmetered:
            pass
        elif isinstance(request_bytes, bool) or not isinstance(request_bytes, int) or request_bytes <= 0:
            return Decision(RESOURCE_POLICY_INVALID, f"requested memory must be a positive integer, got {request_bytes!r}",
                            policy=policy.canonical())
        elif request_bytes > MAX_MEMORY_BYTES:
            return Decision(RESOURCE_POLICY_INVALID, f"requested memory exceeds the permitted maximum: {request_bytes}",
                            policy=policy.canonical())

        with self.ledger.locked() as handle:
            # Observe only after acquiring the same lock as ledger accounting
            # and reservation. A pre-lock snapshot cannot be combined with
            # newly sampled usage after waiting for another admission.
            state = self._observer()
            if state.state != "OBSERVED":
                return Decision(RESOURCE_STATE_UNKNOWN,
                                f"the machine's resource state could not be observed: {state.reason}",
                                state=state.as_dict(), policy=policy.canonical())
            try:
                loaded = self.ledger._load()
            except WorldlineError as exc:
                return Decision(RESOURCE_STATE_UNKNOWN, str(exc.args[1] if len(exc.args) > 1 else exc),
                                state=state.as_dict(), policy=policy.canonical())
            # Liveness filters the ARITHMETIC, never the file. Writing the filtered list back was
            # a persistent deletion: one ordinary admission during a service-manager outage
            # destroyed the accounting for every workload that was still running, and promised
            # their capacity to someone else. Reconciliation is the only thing that removes a
            # record, and it refuses to act on an answer it did not get.
            current = [r for r in loaded if self._is_live(r) is not False]
            try:
                withheld, detail = self.outstanding_withheld(current)
            except CoreUnavailable as exc:
                return Decision(RESOURCE_STATE_UNKNOWN,
                                f"resource ledger kernel could not account reservations: {exc}",
                                arithmetic={"kernelError": str(exc),
                                            "reservations": exc.details.get("reservations", []),
                                            "withheldByReservationsBytes": None,
                                            "headroomBytes": None},
                                state=state.as_dict(), policy=policy.canonical())
            assert state.mem_available_bytes is not None
            try:
                headroom = kernel_compute_headroom(
                    state.mem_available_bytes, withheld, self.floors.min_free_memory_bytes)
            except CoreUnavailable as exc:
                return Decision(RESOURCE_STATE_UNKNOWN,
                                f"resource headroom kernel could not account capacity: {exc}",
                                arithmetic={"requestedBytes": request_bytes,
                                            "memAvailableBytes": state.mem_available_bytes,
                                            "withheldByReservationsBytes": withheld,
                                            "reservations": detail,
                                            "floorBytes": self.floors.min_free_memory_bytes,
                                            "headroomBytes": None,
                                            "outstandingCount": len(current),
                                            "accounted": not unmetered,
                                            "kernelError": str(exc)},
                                state=state.as_dict(), policy=policy.canonical())
            arithmetic = {
                "requestedBytes": request_bytes,
                "memAvailableBytes": state.mem_available_bytes,
                "withheldByReservationsBytes": withheld,
                "reservations": detail,
                "floorBytes": self.floors.min_free_memory_bytes,
                "headroomBytes": headroom,
                "outstandingCount": len(current),
                "accounted": not unmetered,
            }

            try:
                numeric, disk_rows = self._numeric_policy(
                    state, policy, len(current), withheld, request_bytes)
            except (WorldlineError, ValueError, TypeError, KeyError, OverflowError, MemoryError) as exc:
                return Decision(RESOURCE_STATE_UNKNOWN,
                                f"resource kernel could not decide admission: {exc}",
                                arithmetic=arithmetic, state=state.as_dict(),
                                policy=policy.canonical())
            if not numeric.ready:
                return Decision(RESOURCES_UNAVAILABLE,
                                self._numeric_refusal_reason(
                                    numeric, disk_rows, state, policy, len(current),
                                    withheld, request_bytes, headroom),
                                arithmetic=arithmetic, state=state.as_dict(), policy=policy.canonical())

            reservation = Reservation(
                reservation_id=str(uuid.uuid4()), workload=workload, unit=None,
                memory_bytes=request_bytes, tasks=policy.tasks_max or 0,
                created_at_ms=int(time.time() * 1000), owner_pid=os.getpid(),
            )
            self.ledger._store([*loaded, reservation])

        enforced = policy.enforcement == "cgroup2" and bool(policy.unit_properties())
        reason = ((f"{request_bytes} bytes reserved against {headroom} of headroom"
                   + ("" if enforced else "; NOTHING is enforced on the workload because"
                                         f" limits.resources.enforcement is {policy.enforcement!r}"))
                  if not unmetered else
                  "admitted UNMETERED: this policy declares no memory ceiling, so nothing was"
                  f" reserved and nothing is enforced. {headroom} bytes of headroom were free."
                  " Set limits.resources.memoryMaxBytes to make this a budget.")
        return Decision(ADMITTED, reason,
                        reservation_id=reservation.reservation_id, arithmetic=arithmetic,
                        state=state.as_dict(), policy=policy.canonical())

    def release(self, reservation_id: str | None) -> bool:
        if not bool(reservation_id):
            return False
        normalized = str(reservation_id)
        if type(normalized) is str:
            return self.ledger.release_exact(normalized)
        # Preserve the existing custom-comparison domain if __str__ returned
        # a string subclass. This legacy path remains an authority obligation;
        # it is never selected as a fallback after a kernel refusal.
        return self.ledger.release(normalized)

    def attach_unit(self, reservation_id: str | None, unit: str) -> None:
        if reservation_id:
            self.ledger.attach_unit(str(reservation_id), unit)

    def attach_process_identity(self, reservation_id: str | None, identity: Any) -> None:
        if reservation_id:
            self.ledger.attach_process_identity(str(reservation_id), identity)

    def reconcile(self) -> list[Reservation]:
        return self.ledger.reconcile(self._is_live)

    def report(self, policy: ResourcePolicy) -> dict[str, Any]:
        """What `doctor` shows: the inputs, the floors, and whether work would be admitted now."""
        state = self._observer()
        try:
            loaded = self.ledger.outstanding()
            current = [r for r in loaded if self._is_live(r) is not False]
            ledger_error = None
        except WorldlineError as exc:
            current, ledger_error = [], str(exc.args[1] if len(exc.args) > 1 else exc)
        kernel_error = None
        withheld, detail = None, []
        if ledger_error is None:
            try:
                withheld, detail = self.outstanding_withheld(current)
            except CoreUnavailable as exc:
                withheld, detail = None, exc.details.get("reservations", [])
                kernel_error = str(exc)
        headroom = None
        if state.state == "OBSERVED" and state.mem_available_bytes is not None and withheld is not None:
            try:
                headroom = kernel_compute_headroom(
                    state.mem_available_bytes, withheld, self.floors.min_free_memory_bytes)
            except CoreUnavailable as exc:
                kernel_error = str(exc)
        would_admit = None
        if state.state == "OBSERVED" and not ledger_error and kernel_error is None and headroom is not None:
            try:
                declared = (policy.memory_max_bytes if policy.memory_max_bytes is not None
                            else policy.memory_high_bytes)
                requested = 0 if declared is None else declared
                # These are the same request-representation/policy checks as
                # admit(), not an alternate numerical resource decision.
                if declared is not None:
                    if isinstance(requested, bool) or not isinstance(requested, int) or requested <= 0:
                        raise ValueError(f"requested memory must be a positive integer, got {requested!r}")
                    if requested > MAX_MEMORY_BYTES:
                        raise ValueError(f"requested memory exceeds the permitted maximum: {requested}")
                numeric, _ = self._numeric_policy(state, policy, len(current), withheld, requested)
                would_admit = numeric.ready
            except (WorldlineError, ValueError, TypeError, KeyError, OverflowError, MemoryError) as exc:
                kernel_error = str(exc)
        return {
            "state": state.as_dict(),
            "floors": {"minFreeMemoryBytes": self.floors.min_free_memory_bytes,
                       "minFreeDiskBytes": self.floors.min_free_disk_bytes,
                       "minFreeInodes": self.floors.min_free_inodes,
                       "maxMemoryPressureHundredths": self.floors.max_memory_pressure_hundredths},
            "enforcedPolicy": policy.canonical(),
            "outstandingReservations": detail,
            "withheldBytes": withheld,
            "headroomBytes": headroom,
            "ledgerError": ledger_error,
            "resourceDecisionError": kernel_error,
            "unmetered": policy.memory_max_bytes is None and policy.memory_high_bytes is None,
            "enforced": policy.enforcement == "cgroup2" and bool(policy.unit_properties()),
            # The same complete numeric policy admit() uses, including all earlier
            # gates and an unmetered request. This read-only observation is not a reservation.
            "wouldAdmitNow": would_admit,
        }


class Gate:
    """An authority bound to the policy in force, with the reservation's lifetime as a block.

    Every place that spawns supervised work holds one of these, and holds it as a context
    manager, so the reservation exists before the workload does and is released on every exit
    path once its owned workload is known to have ended. Unsettled check cleanup retains capacity.
    Anything that still escapes — a daemon killed
    mid-run — is caught by `reconcile`, because the service manager knows what is running and
    the ledger does not.

    Passed explicitly rather than defaulted: a component that can be constructed without a gate
    is a component that can spawn work nobody accounted for.
    """

    def __init__(self, authority: AdmissionAuthority, policy: ResourcePolicy) -> None:
        self.authority = authority
        self.policy = policy

    def unit_properties(self) -> list[str]:
        return self.policy.unit_properties()

    def admit(self, workload: str, *, memory_bytes: int | None = None) -> Decision:
        return self.authority.admit(workload=workload, policy=self.policy, memory_bytes=memory_bytes)

    def guard(self, workload: str, *, memory_bytes: int | None = None) -> "_Guard":
        return _Guard(self, workload, memory_bytes)


class _Guard:
    def __init__(self, gate: Gate, workload: str, memory_bytes: int | None) -> None:
        self.gate = gate
        self.workload = workload
        self.memory_bytes = memory_bytes
        self.decision: Decision | None = None
        self._release_deferred = False
        self._after_process_failure = False

    def __enter__(self) -> Decision:
        decision = self.gate.admit(self.workload, memory_bytes=self.memory_bytes)
        if not decision.admitted:
            # A refusal is an answer: it names which outcome, and carries the arithmetic that
            # produced it so the operator is not left guessing what the machine looked like.
            raise WorldlineError(decision.outcome, decision.reason, decision.as_dict())
        self.decision = decision
        return decision

    def attach_unit(self, unit: str) -> None:
        if self.decision is not None:
            self.gate.authority.attach_unit(self.decision.reservation_id, unit)

    def attach_process(self, process: Any) -> None:
        """Retain the actual acquired manager unit before consuming its result.

        Once a process exists, an exceptional path cannot release capacity
        without an observed terminal wait. Unsettled failed persistence leaves
        the reservation held; it does not invent a successful attachment.
        """
        self._release_deferred = True
        try:
            from .linux.systemd import SystemdProcess
            if isinstance(process, SystemdProcess):
                process.capture_workload_identity()
            self.attach_unit(process.unit)
            if isinstance(process, SystemdProcess):
                if process.workload_identity is not None:
                    self.gate.authority.attach_process_identity(
                        self.decision.reservation_id, process.workload_identity)
        except BaseException as primary:
            self._stop_after_failure(process, primary)
            raise

    def process_settled(self, process: Any, *, primary: BaseException | None = None,
                        after_failure: bool = False) -> None:
        # --pipe normally waits for the actual service. An exceptional path
        # requires separate matching unit/cgroup facts, even if the launcher
        # has a returncode. None of these observations is a numeric grant or
        # a protected complete-descendant-custody witness.
        self._after_process_failure |= after_failure
        from .linux.systemd import SystemdProcess, WorkloadTerminalObservation
        if not isinstance(process, SystemdProcess):
            return
        try:
            observed = process.manager.terminal_observation(
                process, after_failure=self._after_process_failure)
        except BaseException as cleanup:
            if primary is not None:
                primary.add_note("admitted check terminal observation also failed: " + str(cleanup))
            return
        if (isinstance(observed, WorkloadTerminalObservation) and observed.unit == process.unit
                and observed.launcher_returncode == process.launcher.returncode
                and observed.state in {"NORMAL_PIPE_COMPLETION", "MANAGER_CGROUP_EMPTY", "MANAGER_CGROUP_REMOVED"}):
            self._release_deferred = False

    def _stop_after_failure(self, process: Any, primary: BaseException) -> None:
        self._after_process_failure = True
        try:
            process.stop()
        except BaseException as cleanup:
            primary.add_note("admitted check stop also failed: " + str(cleanup))
        try:
            process.launcher.communicate(timeout=20)
        except BaseException as cleanup:
            primary.add_note("admitted check terminal wait also failed: " + str(cleanup))
        self.process_settled(process, primary=primary, after_failure=True)

    @contextmanager
    def owned_process(self, process: Any):
        self.attach_process(process)
        primary = None
        try:
            yield process
        except BaseException as error:
            primary = error
            self._stop_after_failure(process, error)
            raise
        finally:
            self.process_settled(process, primary=primary)

    def release(self) -> None:
        if self.decision is not None and not self._release_deferred:
            self.gate.authority.release(self.decision.reservation_id)
            self.decision = None

    def __exit__(self, *exc: Any) -> None:
        primary = exc[1] if len(exc) > 1 else None
        try:
            self.release()
        except BaseException as cleanup:
            if primary is None:
                raise
            primary.add_note("admission reservation release also failed: " + str(cleanup))
