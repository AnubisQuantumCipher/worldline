from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any, Sequence
import uuid

from .environment import safe_environment
from .errors import WorldlineError
from .linux.namespaces import BubblewrapSandbox, SandboxSpec
from .admission import Gate
from .linux.systemd import SystemdAdapter, SystemdProcess
from .model import World
from .paths import WorldlinePaths
from .payload import materialize_payload_view
from .project import ProjectConfig, ServiceSpec
from .store import StateStore


class ServiceManager:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        sandbox: BubblewrapSandbox,
        systemd: SystemdAdapter,
        gate: "Gate",
    ) -> None:
        self.paths = paths
        self.store = store
        self.sandbox = sandbox
        self.systemd = systemd
        self.gate = gate
        self._processes: dict[str, SystemdProcess] = {}

    def start_declared(self, world: World, project: ProjectConfig) -> list[dict[str, Any]]:
        started: list[dict[str, Any]] = []
        for service in project.services:
            started.append(self._start(world, service))
        return started

    def _start(self, world: World, service: ServiceSpec) -> dict[str, Any]:
        roots = self.store.roots()
        primary = next(root for root in roots if root["primary_root"])
        payload = Path(world.payload_path)
        instance = str(uuid.uuid4())
        lower = materialize_payload_view(
            payload,
            roots,
            self.paths.overlays / instance / "service-lower",
            self.store.core,
        )
        overlays = self.sandbox.overlay_roots(
            instance,
            [
                (
                    root["root_key"],
                    lower / root["root_key"],
                    Path(os.fsdecode(bytes(root["path"]))),
                )
                for root in roots
            ],
        )
        primary_target = Path(os.fsdecode(bytes(primary["path"])))
        runtime = self.paths.overlays / instance / "service-runtime"
        environment = {**safe_environment(), **service.env}
        spec = SandboxSpec(
            instance_id=instance,
            argv=service.argv,
            cwd=primary_target / service.cwd,
            environment=environment,
            roots=overlays,
            runtime=runtime,
        )
        raw_path = self.paths.logs / f"{world.instance_id}.service-{service.id}.jsonl"
        job_id = str(uuid.uuid4())
        self.store.create_job(
            job_id=job_id,
            world_instance=world.instance_id,
            state="STARTING",
            raw_event_path=raw_path,
            sandbox={"backend": "overlayfs+bubblewrap", "service": service.id},
        )
        stderr_file = open(self.paths.logs / f"{world.instance_id}.service-{service.id}.stderr", "ab", buffering=0)
        stdout_file = open(raw_path, "ab", buffering=0)
        try:
            # A declared service is supervised work like any other: it reserves before it runs
            # and is released when it is stopped. The reservation id travels with the record so
            # a stop in another call can release it, and `reconcile` catches anything that dies
            # without one.
            decision = self.gate.admit(f"service:{world.alias}/{service.id}")
            if not decision.admitted:
                raise WorldlineError(decision.outcome, decision.reason, decision.as_dict())
            process = self.systemd.launch(
                instance,
                self.sandbox.build_argv(spec),
                description=f"WORLDLINE {world.alias} service {service.id}",
                restart=service.restart,
                resource_properties=self.gate.unit_properties(),
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
            )
        except BaseException:
            stdout_file.close()
            stderr_file.close()
            self.gate.authority.release(decision.reservation_id)
            raise
        stdout_file.close()
        stderr_file.close()
        # The reservation now names the unit, which is what makes it self-releasing: admission
        # ignores a reservation whose unit the manager no longer has, and `reconcile` removes it.
        # A service that dies without anyone watching does not hold capacity forever.
        self.gate.authority.attach_unit(decision.reservation_id, process.unit)
        self._processes[job_id] = process
        self.store.update_job(
            job_id,
            state="RUNNING",
            systemd_unit=process.unit,
            pid=process.pid,
        )
        health = self._health(world, service, payload, roots, primary_target, environment)
        if health["status"] != "PASS":
            self.systemd.stop(process.unit)
            process.launcher.wait(timeout=15)
            self._processes.pop(job_id, None)
            self.store.update_job(
                job_id,
                state="DEGRADED",
                error={"code": "SERVICE_HEALTH_FAILED", "message": health["stderr"]},
                ended=True,
            )
        return {
            "id": service.id,
            "jobId": job_id,
            "unit": process.unit,
            "pid": process.pid,
            "health": health,
        }

    def _health(
        self,
        world: World,
        service: ServiceSpec,
        payload: Path,
        roots: list[dict[str, Any]],
        primary_target: Path,
        environment: dict[str, str],
    ) -> dict[str, Any]:
        instance = str(uuid.uuid4())
        lower = materialize_payload_view(
            payload,
            roots,
            self.paths.overlays / instance / "health-lower",
            self.store.core,
        )
        overlays = self.sandbox.overlay_roots(
            instance,
            [
                (
                    root["root_key"],
                    lower / root["root_key"],
                    Path(os.fsdecode(bytes(root["path"]))),
                )
                for root in roots
            ],
        )
        spec = SandboxSpec(
            instance_id=instance,
            argv=service.health_argv,
            cwd=primary_target / service.cwd,
            environment=environment,
            roots=overlays,
            runtime=self.paths.overlays / instance / "service-health-runtime",
        )
        with self.gate.guard(f"service-health:{world.alias}/{service.id}"):
            process = self.systemd.launch(
                instance,
                self.sandbox.build_argv(spec),
                description=f"WORLDLINE {world.alias} service health {service.id}",
                resource_properties=self.gate.unit_properties(),
            )
            stdout, stderr = process.launcher.communicate(timeout=30)
        return {
            "status": "PASS" if process.launcher.returncode == 0 else "FAIL",
            "exitCode": process.launcher.returncode,
            "stdout": stdout.decode("utf-8", "replace"),
            "stderr": stderr.decode("utf-8", "replace"),
        }

    def stop_world(self, world_instance: str) -> None:
        for job in self.store.jobs():
            if (
                job["world_instance"] != world_instance
                or job["state"] not in {"STARTING", "RUNNING", "FINALIZING"}
            ):
                continue
            process = self._processes.pop(job["job_id"], None)
            if process is not None:
                process.stop()
                process.launcher.wait(timeout=15)
            elif job.get("systemd_unit"):
                self.systemd.stop(job["systemd_unit"])
            self.store.update_job(job["job_id"], state="STOPPED", ended=True)

    def stop_orphans(self) -> list[str]:
        stopped: list[str] = []
        for job in self.store.jobs():
            if job["state"] not in {"STARTING", "RUNNING", "FINALIZING"}:
                continue
            unit = job.get("systemd_unit")
            if unit:
                try:
                    self.systemd.stop(unit)
                except WorldlineError:
                    pass
            stopped.append(job["job_id"])
        return stopped
