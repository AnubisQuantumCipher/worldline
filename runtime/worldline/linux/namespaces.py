from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import shutil
import signal
import subprocess
import tempfile
from typing import Any, Mapping, Sequence
import uuid

from ..trusted import trusted_script
from ..errors import WorldlineError
from ..manifest import display_path
from ..paths import WorldlinePaths, secure_directory

_SYSTEM_READONLY = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc", "/sys", "/var", "/opt")


@dataclass(frozen=True, slots=True)
class OverlayRoot:
    root_key: str
    lower: Path
    upper: Path
    work: Path
    target: Path


@dataclass(frozen=True, slots=True)
class CredentialProjection:
    source: Path
    target: Path
    # A private copy is a per-world duplicate of a credential file that the agent must be able
    # to write (omp keeps its whole state, credentials included, in one SQLite file it opens
    # read-write). The runner materializes the copy under the world's agent runtime before the
    # sandbox starts; the host file is never bound. The copy dies with the world.
    private_copy: bool = False


@dataclass(frozen=True, slots=True)
class SandboxSpec:
    instance_id: str
    argv: tuple[str, ...]
    cwd: Path
    environment: Mapping[str, str]
    roots: tuple[OverlayRoot, ...]
    runtime: Path
    readonly_home_paths: tuple[Path, ...] = ()
    # (host source, path inside the sandbox). Used for the staged execution verifier set: the
    # bytes a check is identified by must be bytes the candidate has no path to write.
    readonly_mounts: tuple[tuple[Path, str], ...] = ()
    credential_mounts: tuple[CredentialProjection, ...] = ()
    # The HOME the sandbox sees, as an empty tmpfs. None means the daemon's own HOME: every
    # sandbox masks the account WORLDLINE runs as (1.6.0 defaulted to a fixed operator path, so
    # checks, services and simulate left a dedicated account's HOME visible).
    operator_home: Path | None = None
    # Network policy for this sandbox: "shared" (host namespace, the historical default),
    # "none" (empty namespace: loopback only), or "allowlist" (empty namespace plus the
    # netguard forwarder relaying to a Unix-socket proxy inside the runtime directory).
    network: str = "shared"
    # Host-side proxy socket (kept under $XDG_RUNTIME_DIR/worldline: AF_UNIX paths are limited to
    # 108 bytes and an overlay runtime path is longer) and where it is bound inside the world.
    netguard_source: Path | None = None
    netguard_socket: str = "/run/worldline-runtime/netguard.sock"
    netguard_port: int = 3128
    # Identity inside the user namespace. The real uid is the only one mapped either way, so
    # this changes what the process *sees*, not what it can reach. Agent worlds, checks, and
    # shells run as the real uid: Claude Code refuses `--dangerously-skip-permissions` when it
    # sees euid 0, which is why every builtin claude world on this machine had died. System
    # futures (`simulate`) keep namespace root deliberately, since they audition system commands.
    uid: int | None = None
    gid: int | None = None


@dataclass(slots=True)
class SandboxProcess:
    process: subprocess.Popen[bytes]
    spec: SandboxSpec
    bubblewrap_argv: tuple[str, ...]

    @property
    def pid(self) -> int:
        return self.process.pid

    def terminate_tree(self, timeout: float = 10.0) -> None:
        if self.process.poll() is not None:
            return
        try:
            os.killpg(self.process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait()


class BubblewrapSandbox:
    def __init__(self, paths: WorldlinePaths, executable: str | None = None) -> None:
        self.paths = paths
        self.executable = executable or shutil.which("bwrap") or ""
        if not self.executable:
            raise WorldlineError("BUBBLEWRAP_UNAVAILABLE", "bwrap is not installed")

    def overlay_roots(
        self,
        instance_id: str,
        roots: Sequence[tuple[str, Path, Path]],
        *,
        allow_system_roots: bool = False,
    ) -> tuple[OverlayRoot, ...]:
        try:
            parsed = uuid.UUID(instance_id)
        except ValueError as exc:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {instance_id}") from exc
        if parsed.version != 4 or str(parsed) != instance_id:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {instance_id}")
        base = self.paths.overlays / instance_id
        secure_directory(base)
        result: list[OverlayRoot] = []
        for root_key, lower_value, target_value in roots:
            lower = lower_value.resolve(strict=True)
            target = target_value.absolute()
            if not lower.is_dir():
                raise WorldlineError("INVALID_LOWERDIR", f"overlay lower root is not a directory: {lower}")
            if not target.is_absolute():
                raise WorldlineError("INVALID_SANDBOX_TARGET", f"managed target is not absolute: {target}")
            if not allow_system_roots:
                for readonly in _SYSTEM_READONLY:
                    if self._overlap(target, Path(readonly)):
                        raise WorldlineError(
                            "UNSANDBOXABLE_ROOT",
                            f"managed root overlaps a read-only system bind: {target}",
                        )
            root_base = base / root_key
            upper = secure_directory(root_base / "upper")
            work = secure_directory(root_base / "work")
            if any(upper.iterdir()) or any(work.iterdir()):
                raise WorldlineError("OVERLAY_NOT_EMPTY", f"overlay upper/work directory is not empty: {root_key}")
            shutil.copystat(lower, upper, follow_symlinks=False)
            if upper.stat().st_dev != work.stat().st_dev:
                raise WorldlineError("OVERLAY_DEVICE_MISMATCH", f"overlay upper/work devices differ: {root_key}")
            result.append(OverlayRoot(root_key, lower, upper, work, target))
        targets = [item.target for item in result]
        if len({str(path) for path in targets}) != len(targets):
            raise WorldlineError("OVERLAPPING_ROOT", "sandbox contains duplicate managed targets")
        return tuple(result)

    @staticmethod
    def _overlap(first: Path, second: Path) -> bool:
        try:
            common = Path(os.path.commonpath((first, second)))
        except ValueError:
            return False
        return common in (first, second)

    @staticmethod
    def _directory_arguments(path: Path, *, stop: Path | None = None) -> list[str]:
        if not path.is_absolute():
            raise WorldlineError("INVALID_SANDBOX_TARGET", f"sandbox path is not absolute: {path}")
        result: list[str] = []
        current = path
        chain: list[Path] = []
        while current != current.parent and current != stop:
            chain.append(current)
            current = current.parent
        for directory in reversed(chain):
            result.extend(("--dir", str(directory)))
        return result

    @staticmethod
    def _resolver_directories() -> tuple[Path, ...]:
        resolv = Path("/etc/resolv.conf")
        if not resolv.is_symlink():
            return ()
        try:
            real = resolv.resolve(strict=True)
        except OSError:
            return ()
        if real.is_relative_to("/run") and real.parent != Path("/run") and real.parent.is_dir():
            return (real.parent,)
        return ()

    def _store_masks(self, home: Path) -> list[str]:
        """tmpfs over each store directory the sandbox would otherwise see: one under a system
        path (bound read-only, or overlaid by simulate) and outside the masked HOME, by its
        configured spelling and by its resolved one. Anywhere else it is not mounted."""
        masks: list[str] = []
        systems = [Path(system) for system in (*_SYSTEM_READONLY, "/boot")]
        homes = {home, Path(os.path.realpath(home))}
        for configured in (self.paths.data, self.paths.state, self.paths.config, self.paths.runtime):
            for private in dict.fromkeys((configured, Path(os.path.realpath(configured)))):
                if os.path.islink(private):
                    continue  # bwrap cannot mount onto a link; its resolved spelling is covered
                if any(masked == private or masked in private.parents for masked in homes):
                    continue
                if any(system == private or system in private.parents for system in systems):
                    masks.extend(("--tmpfs", str(private)))
        return masks

    def _overlay_arguments(self, root: OverlayRoot) -> list[str]:
        return [*self._directory_arguments(root.target.parent), "--dir", str(root.target),
                "--overlay-src", str(root.lower),
                "--overlay", str(root.upper), str(root.work), str(root.target)]

    def build_argv(self, spec: SandboxSpec) -> tuple[str, ...]:
        if not spec.argv or any(not item for item in spec.argv):
            raise WorldlineError("INVALID_AGENT_COMMAND", "sandbox argv must be a nonempty string array")
        if not spec.cwd.is_absolute() or not any(self._overlap(spec.cwd, root.target) for root in spec.roots):
            raise WorldlineError("INVALID_SANDBOX_CWD", f"sandbox cwd is outside managed roots: {spec.cwd}")
        secure_directory(spec.runtime)
        uid = os.getuid() if spec.uid is None else int(spec.uid)
        gid = os.getgid() if spec.gid is None else int(spec.gid)
        if spec.network not in ("shared", "none", "allowlist"):
            raise WorldlineError("INVALID_NETWORK_POLICY", f"unknown sandbox network policy: {spec.network}")
        arguments: list[str] = [
            self.executable,
            "--unshare-all",
            "--unshare-user",
            *(("--share-net",) if spec.network == "shared" else ()),
            "--die-with-parent",
            "--new-session",
            "--uid",
            str(uid),
            "--gid",
            str(gid),
            "--hostname",
            f"worldline-{spec.instance_id[:12]}",
            "--clearenv",
        ]
        home = spec.operator_home if spec.operator_home is not None else self.paths.home
        overlay_targets = {str(root.target) for root in spec.roots}
        # simulate overlays whole system directories (/usr, /etc, /var, /opt, /boot). They are
        # mounted first, so the HOME and store masks below land on top of them; mounted last,
        # as in 1.7.0's first candidate, they covered the masks and the store was readable.
        system_targets = {*_SYSTEM_READONLY, "/boot"}
        system_overlays = [root for root in spec.roots if str(root.target) in system_targets]
        managed_overlays = [root for root in spec.roots if str(root.target) not in system_targets]
        for path_text in _SYSTEM_READONLY:
            if path_text in overlay_targets and not Path(path_text).is_symlink():
                continue
            source = Path(path_text)
            if not os.path.lexists(source):
                continue
            if source.is_symlink():
                arguments.extend(("--symlink", os.readlink(source), path_text))
            else:
                arguments.extend(("--ro-bind", path_text, path_text))
        for root in system_overlays:
            arguments.extend(self._overlay_arguments(root))
        arguments.extend(("--dev", "/dev", "--proc", "/proc"))
        arguments.extend(("--tmpfs", "/run", "--tmpfs", "/tmp"))
        # /run is a fresh tmpfs, which strands /etc/resolv.conf when it is the systemd-resolved
        # symlink into /run/systemd/resolve (Arch's default). Without this every agent inside a
        # world fails DNS with "Try again" and reconnects until it gives up, while the host
        # resolves fine. Bind the resolver directory read-only so the symlink lands.
        for directory in self._resolver_directories():
            arguments.extend(("--ro-bind", str(directory), str(directory)))
        if "/var" not in overlay_targets:
            arguments.extend(("--tmpfs", "/var/tmp"))
        arguments.extend(self._directory_arguments(home.parent))
        if not os.path.islink(home):
            arguments.extend(("--tmpfs", str(home)))
        real_home = Path(os.path.realpath(home))
        if real_home != home:
            # A HOME spelled through a link: the link's target is where the content is, and a
            # system bind or overlay would show it there.
            arguments.extend(self._directory_arguments(real_home.parent))
            arguments.extend(("--tmpfs", str(real_home)))
        # Nothing WORLDLINE runs may read its own store. Masking the HOME above covers a store
        # under it; a dedicated account's store elsewhere (/var/lib/...) would otherwise be
        # visible through the system binds and overlays, signing key included. Bind SOURCES
        # resolve on the host, so the overlays and runtimes below are unaffected.
        arguments.extend(self._store_masks(home))
        arguments.extend(self._directory_arguments(Path("/run/worldline-runtime")))
        arguments.extend(("--bind", str(spec.runtime), "/run/worldline-runtime"))
        for source, target in spec.readonly_mounts:
            if not source.is_dir():
                raise WorldlineError("VERIFIER_EXECUTION_UNIDENTIFIED",
                                     f"a declared read-only mount is missing: {source}")
            arguments.extend(self._directory_arguments(Path(target)))
            arguments.extend(("--ro-bind", str(source), target))

        mounted_targets: set[str] = set()
        for source in (*spec.readonly_home_paths, *(item.source for item in spec.credential_mounts)):
            if not source.is_absolute() or not source.exists():
                raise WorldlineError("CREDENTIAL_PROJECTION_UNAVAILABLE", f"declared read-only path is missing: {source}")
        projections = [CredentialProjection(path, path) for path in spec.readonly_home_paths]
        projections.extend(spec.credential_mounts)
        runtime_resolved = spec.runtime.resolve()
        for projection in projections:
            if not projection.target.is_absolute():
                raise WorldlineError("INVALID_CREDENTIAL_PROJECTION", f"projection target is not absolute: {projection.target}")
            target_text = str(projection.target)
            if target_text in mounted_targets:
                raise WorldlineError("INVALID_CREDENTIAL_PROJECTION", f"duplicate projection target: {target_text}")
            mounted_targets.add(target_text)
            arguments.extend(self._directory_arguments(projection.target.parent, stop=home))
            if projection.private_copy:
                # Writable, so it must be the world's own copy inside its runtime, never a host file.
                if not self._overlap(projection.source.resolve(), runtime_resolved):
                    raise WorldlineError(
                        "INVALID_CREDENTIAL_PROJECTION",
                        f"writable projection is not a private copy inside the world runtime: {projection.source}",
                    )
                arguments.extend(("--bind", str(projection.source), target_text))
            else:
                arguments.extend(("--ro-bind", str(projection.source), target_text))

        # Managed roots last: in a single-account install they live inside the masked HOME.
        for root in managed_overlays:
            arguments.extend(self._overlay_arguments(root))

        environment = {
            # The account's XDG homes name directories inside the masked HOME that the sandbox
            # does not have; tools then use their HOME-relative defaults, where projections land.
            **{key: value for key, value in spec.environment.items()
               if key not in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME")},
            "HOME": str(home),
            "USER": home.name,
            "LOGNAME": home.name,
            "XDG_RUNTIME_DIR": "/run/worldline-runtime",
        }
        for key, value in sorted(environment.items()):
            if not isinstance(key, str) or not isinstance(value, str) or "=" in key or "\x00" in key + value:
                raise WorldlineError("INVALID_SANDBOX_ENV", f"invalid environment entry: {key!r}")
            arguments.extend(("--setenv", key, value))
        command = list(spec.argv)
        if spec.network == "allowlist":
            forwarder = spec.runtime / "netguard.py"
            if not forwarder.is_file() or spec.netguard_source is None or not spec.netguard_source.exists():
                raise WorldlineError(
                    "NETGUARD_UNAVAILABLE",
                    "the allowlist policy needs the netguard forwarder in the world runtime and a live proxy socket",
                )
            arguments.extend(("--bind", str(spec.netguard_source), spec.netguard_socket))
            # Trusted, and a SCRIPT launch, so the directory it is exposed to is the script's
            # own -- /run/worldline-runtime, which is bind-mounted read-write and is the
            # world's XDG_RUNTIME_DIR. The workload writes there by design. See trusted.py.
            command = [
                *trusted_script(
                    "/run/worldline-runtime/netguard.py",
                    "--socket", spec.netguard_socket, "--port", str(spec.netguard_port),
                ),
                "--", *command,
            ]
        arguments.extend(("--chdir", str(spec.cwd), "--disable-userns", "--cap-drop", "ALL", "--"))
        arguments.extend(command)
        return tuple(arguments)

    def launch_world(
        self,
        spec: SandboxSpec,
        *,
        stdin: int | Any = subprocess.PIPE,
        stdout: int | Any = subprocess.PIPE,
        stderr: int | Any = subprocess.PIPE,
    ) -> SandboxProcess:
        argv = self.build_argv(spec)
        try:
            process = subprocess.Popen(
                argv,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                close_fds=True,
            )
        except OSError as exc:
            raise WorldlineError("SANDBOX_LAUNCH_FAILED", str(exc), {"executable": self.executable}) from exc
        return SandboxProcess(process=process, spec=spec, bubblewrap_argv=argv)

    @classmethod
    def capability(cls, paths: WorldlinePaths) -> dict[str, Any]:
        try:
            sandbox = cls(paths)
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "reason": exc.message}
        version_result = subprocess.run(
            [sandbox.executable, "--version"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=5,
        )
        version = version_result.stdout.decode("utf-8", "replace").strip()
        with tempfile.TemporaryDirectory(prefix="worldline-overlay-probe-", dir=paths.data) as temporary:
            base = Path(temporary)
            lower = base / "lower"
            upper = base / "upper"
            work = base / "work"
            runtime = base / "runtime"
            for directory in (lower, upper, work, runtime):
                directory.mkdir(mode=0o700)
            (lower / "sentinel").write_text("overlay", encoding="utf-8")
            instance = str(uuid.uuid4())
            spec = SandboxSpec(
                instance_id=instance,
                argv=("/usr/bin/test", "-f", "/tmp/worldline-probe/sentinel"),
                cwd=Path("/tmp/worldline-probe"),
                environment={"PATH": "/usr/bin"},
                roots=(OverlayRoot("probe", lower, upper, work, Path("/tmp/worldline-probe")),),
                runtime=runtime,
            )
            try:
                completed = subprocess.run(
                    sandbox.build_argv(spec),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=15,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                return {"state": "UNAVAILABLE", "reason": str(exc)}
            if completed.returncode != 0:
                return {
                    "state": "UNAVAILABLE",
                    "reason": completed.stderr.decode("utf-8", "replace").strip() or f"probe exited {completed.returncode}",
                }
        return {"state": "AVAILABLE", "backend": "overlayfs+bubblewrap", "version": version}
