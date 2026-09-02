from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Sequence
import uuid

from .client import DaemonClient
from .config import GlobalConfig
from .core import Core
from .errors import WorldlineError
from .linux.namespaces import BubblewrapSandbox, SandboxSpec
from .linux.systemd import SystemdAdapter
from .paths import WorldlinePaths
from .payload import materialize_payload_view


def _emit(value: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))
    elif isinstance(value, str):
        print(value)
    else:
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def _progress(event: str, data: dict[str, Any]) -> None:
    world = data.get("world")
    state = data.get("state") or data.get("event", {}).get("kind")
    print(f"{event}: {world or ''} {state or ''}".rstrip(), file=sys.stderr)


def _mission(arguments: argparse.Namespace, client: DaemonClient) -> str:
    if getattr(arguments, "mission", None):
        return Path(arguments.mission).read_text(encoding="utf-8")
    if getattr(arguments, "mission_text", None) is not None:
        return arguments.mission_text
    if not sys.stdin.isatty():
        value = sys.stdin.read()
        if value:
            return value
    roots = client.request("root.list")
    primary = next((root for root in roots if root["primary"]), None)
    if primary is not None:
        path = Path(primary["path"]) / "mission.md"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise WorldlineError("NO_MISSION", "worldline: no mission; pass --mission FILE, pipe stdin, or create mission.md")


def _confirm(prompt: str, *, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        raise WorldlineError("CONFIRMATION_REQUIRED", "noninteractive mutation requires --yes")
    response = input(f"{prompt} [y/N] ").strip().lower()
    return response in {"y", "yes"}


def _print_transaction(facts: dict[str, Any]) -> None:
    print(f"Base: {facts['before_root']}")
    print(f"Candidate: {facts['candidate_root']}")
    print("Managed roots:")
    for root in facts["managedRoots"]:
        print(f"  {root['path']}  [{root['kind']}]  {root['rootKey']}")
    print("Delta:")
    for operation in facts["delta"]["operations"]:
        print(f"  {operation['op']:6} {operation['rootKey']}:{operation['pathDisplay']}")
    print("Conflicts:")
    if facts["conflicts"]:
        for conflict in facts["conflicts"]:
            print(f"  {conflict['pathDisplay']}")
    else:
        print("  NONE")
    print("Foreign contamination:")
    if facts["contamination"]:
        for item in facts["contamination"]:
            print(f"  {item}")
    else:
        print("  NONE")


def _root_mutation(client: DaemonClient, operation: str, arguments: argparse.Namespace) -> Any:
    roots = arguments.roots if hasattr(arguments, "roots") else [arguments.root]
    payload = {
        "roots": roots,
        "kind": getattr(arguments, "kind", None),
        "primary": getattr(arguments, "primary", None),
        "confirmed": False,
    }
    if operation == "root.remove":
        payload = {"root": arguments.root, "confirmed": False}
    try:
        client.request(operation, payload)
        raise AssertionError("unconfirmed root mutation unexpectedly succeeded")
    except WorldlineError as exc:
        if exc.code != "CONFIRMATION_REQUIRED":
            raise
        details = exc.details
    print("Managed root change:")
    for root in details.get("roots", []):
        print(f"  {root['path']}  [{root['kind']}]" + ("  PRIMARY" if root.get("primary") else ""))
    if not _confirm("Apply this exact managed-root change?", assume_yes=arguments.yes):
        return {"state": "ABORTED"}
    payload["confirmed"] = True
    return client.request(operation, payload)


def _shell(client: DaemonClient, world_name: str) -> int:
    info = client.request("shell.info", {"world": world_name})
    paths = WorldlinePaths.from_environment()
    config = GlobalConfig.load(paths)
    sandbox = BubblewrapSandbox(paths)
    identifier = str(uuid.uuid4())
    payload = Path(info["payload"])
    root_records = [
        {"root_key": root["rootKey"]}
        for root in info["roots"]
    ]
    lower = materialize_payload_view(
        payload,
        root_records,
        paths.overlays / identifier / "shell-lower",
        Core.shared(),
    )
    inputs = [
        (root["rootKey"], lower / root["rootKey"], Path(root["target"]))
        for root in info["roots"]
    ]
    overlays = sandbox.overlay_roots(identifier, inputs)
    runtime = paths.overlays / identifier / "shell-runtime"
    shell = os.environ.get("SHELL", "/bin/bash")
    cwd = Path(info["cwd"])
    if not any(cwd == item.target or item.target in cwd.parents for item in overlays):
        cwd = overlays[0].target
    spec = SandboxSpec(
        instance_id=identifier,
        argv=(shell,),
        cwd=cwd,
        environment={"PATH": os.environ.get("PATH", "/usr/bin"), "TERM": os.environ.get("TERM", "xterm-256color")},
        roots=overlays,
        runtime=runtime,
        readonly_home_paths=config.readonly_home_paths,
        operator_home=paths.home,
    )
    process = SystemdAdapter().launch(
        identifier,
        sandbox.build_argv(spec),
        description=f"WORLDLINE shell {world_name}",
        pty=True,
        stdin=None,
        stdout=None,
        stderr=None,
    )
    return process.launcher.wait()


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="worldline")
    root.add_argument("--json", action="store_true", dest="global_json")
    commands = root.add_subparsers(dest="command", required=True)

    status = commands.add_parser("status")
    status.add_argument("--json", action="store_true")
    listing = commands.add_parser("list")
    listing.add_argument("--json", action="store_true")
    show = commands.add_parser("show")
    show.add_argument("world")
    show.add_argument("--json", action="store_true")
    graph = commands.add_parser("graph")
    graph.add_argument("--json", action="store_true")
    log = commands.add_parser("log")
    log.add_argument("--verify", action="store_true")
    log.add_argument("--json", action="store_true")
    why = commands.add_parser("why")
    why.add_argument("location")
    why.add_argument("--json", action="store_true")
    inspect = commands.add_parser("inspect")
    inspect.add_argument("world")
    inspect.add_argument("--json", action="store_true")

    initialize = commands.add_parser("init")
    initialize.add_argument("roots", nargs="+")
    initialize.add_argument("--primary")
    initialize.add_argument("--kind", choices=("repo", "config", "filesystem"))
    initialize.add_argument("--yes", action="store_true")
    initialize.add_argument("--json", action="store_true")

    root_command = commands.add_parser("root")
    root_subcommands = root_command.add_subparsers(dest="root_command", required=True)
    root_add = root_subcommands.add_parser("add")
    root_add.add_argument("roots", nargs="+")
    root_add.add_argument("--primary")
    root_add.add_argument("--kind", choices=("repo", "config", "filesystem"))
    root_add.add_argument("--yes", action="store_true")
    root_add.add_argument("--json", action="store_true")
    root_remove = root_subcommands.add_parser("remove")
    root_remove.add_argument("root")
    root_remove.add_argument("--yes", action="store_true")
    root_remove.add_argument("--json", action="store_true")
    root_list = root_subcommands.add_parser("list")
    root_list.add_argument("--json", action="store_true")

    fork = commands.add_parser("fork")
    fork.add_argument("name")
    fork.add_argument("agent")
    mission_group = fork.add_mutually_exclusive_group()
    mission_group.add_argument("--mission")
    mission_group.add_argument("--mission-text")
    fork.add_argument("--wait", action="store_true")
    fork.add_argument("--json", action="store_true")

    race = commands.add_parser("race")
    race.add_argument("mission_file", nargs="?")
    race.add_argument("--mission-text")
    race.add_argument("--agent", action="append", required=True)
    race.add_argument("--detach", action="store_true")
    race.add_argument("--json", action="store_true")

    collapse = commands.add_parser("collapse")
    collapse.add_argument("world")
    collapse.add_argument("--yes", action="store_true")
    collapse.add_argument("--json", action="store_true")
    returning = commands.add_parser("return")
    returning.add_argument("world", nargs="?")
    returning.add_argument("--yes", action="store_true")
    returning.add_argument("--json", action="store_true")

    simulate = commands.add_parser("simulate")
    simulate.add_argument("argv", nargs=argparse.REMAINDER)
    simulate.add_argument("--json", action="store_true")
    doctor = commands.add_parser("doctor")
    doctor.add_argument("--refresh", action="store_true")
    doctor.add_argument("--json", action="store_true")
    adapters = commands.add_parser("adapters")
    adapters.add_argument("--json", action="store_true")

    shell = commands.add_parser("shell")
    shell.add_argument("world")
    watch = commands.add_parser("watch")
    watch.add_argument("--json", action="store_true")
    switch = commands.add_parser("switch")
    selection = switch.add_mutually_exclusive_group()
    selection.add_argument("--next", action="store_true")
    selection.add_argument("--previous", action="store_true")
    switch.add_argument("world", nargs="?")
    switch.add_argument("--json", action="store_true")

    ghost = commands.add_parser("ghost")
    ghost_subcommands = ghost.add_subparsers(dest="ghost_command", required=True)
    ghost_enable = ghost_subcommands.add_parser("enable")
    ghost_enable.add_argument("--agent", required=True)
    ghost_enable.add_argument("--json", action="store_true")
    ghost_disable = ghost_subcommands.add_parser("disable")
    ghost_disable.add_argument("--json", action="store_true")
    ghost_status = ghost_subcommands.add_parser("status")
    ghost_status.add_argument("--json", action="store_true")
    ghost_run = ghost_subcommands.add_parser("run")
    ghost_run.add_argument("objective", choices=("security-refactor", "performance", "remove-dependency", "simplification"))
    ghost_run.add_argument("--wait", action="store_true")
    ghost_run.add_argument("--json", action="store_true")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    as_json = bool(arguments.global_json or getattr(arguments, "json", False))
    client = DaemonClient(timeout=86_400)
    try:
        command = arguments.command
        if command == "status":
            result = client.request("status")
        elif command == "list":
            result = client.request("list")
        elif command == "show":
            result = client.request("show", {"world": arguments.world})
        elif command == "graph":
            result = client.request("graph")
        elif command == "log":
            result = client.request("log", {"verify": arguments.verify})
        elif command == "why":
            path, separator, line_text = arguments.location.rpartition(":")
            if not separator or not line_text.isdigit():
                raise WorldlineError("INVALID_LOCATION", "why location must be PATH:LINE")
            result = client.request("why", {"path": path, "line": int(line_text)})
        elif command == "inspect":
            result = client.request("inspect", {"world": arguments.world})
        elif command == "init":
            result = _root_mutation(client, "init", arguments)
        elif command == "root":
            if arguments.root_command == "add":
                result = _root_mutation(client, "root.add", arguments)
            elif arguments.root_command == "remove":
                result = _root_mutation(client, "root.remove", arguments)
            else:
                result = client.request("root.list")
        elif command == "fork":
            mission = _mission(arguments, client)
            result = client.request(
                "fork",
                {"name": arguments.name, "mission": mission, "agent": arguments.agent, "wait": arguments.wait},
                progress=_progress,
            )
        elif command == "race":
            if arguments.mission_text is not None:
                mission = arguments.mission_text
            elif arguments.mission_file:
                mission = Path(arguments.mission_file).read_text(encoding="utf-8")
            else:
                mission = _mission(arguments, client)
            result = client.request(
                "race",
                {"agents": arguments.agent, "mission": mission, "detach": arguments.detach},
                progress=_progress,
            )
        elif command in {"collapse", "return"}:
            operation = "collapse.prepare" if command == "collapse" else "return.prepare"
            payload = {"world": arguments.world} if command == "return" else {"world": arguments.world}
            facts = client.request(operation, payload)
            _print_transaction(facts)
            prompt = (
                f"Collapse {arguments.world} into PRIME?"
                if command == "collapse"
                else f"RETURN to {facts['returnWorld']}?"
            )
            if not _confirm(prompt, assume_yes=arguments.yes):
                result = client.request("transaction.abort", {"transactionId": facts["transaction_id"]})
            else:
                result = client.request("collapse.commit", {"transactionId": facts["transaction_id"]})
        elif command == "simulate":
            exact = list(arguments.argv)
            if exact and exact[0] == "--":
                exact.pop(0)
            if not exact:
                raise WorldlineError("INVALID_SIMULATION_COMMAND", "simulate requires COMMAND...")
            result = client.request("simulate", {"argv": exact}, progress=_progress)
        elif command == "doctor":
            result = client.request("doctor", {"refresh": arguments.refresh})
        elif command == "adapters":
            result = client.request("adapters")
        elif command == "shell":
            return _shell(client, arguments.world)
        elif command == "watch":
            previous = None
            while True:
                current = client.request("status")
                if current != previous:
                    _emit(current, as_json=as_json)
                    previous = current
                time.sleep(1)
        elif command == "switch":
            target = "next" if arguments.next else "previous" if arguments.previous else arguments.world
            if target is None:
                raise WorldlineError("INVALID_SWITCH", "switch requires --next, --previous, or WORLD")
            result = client.request("switch", {"target": target})
        elif command == "ghost":
            if arguments.ghost_command == "enable":
                result = client.request("ghost.enable", {"agent": arguments.agent})
            elif arguments.ghost_command == "disable":
                result = client.request("ghost.disable")
            elif arguments.ghost_command == "status":
                result = client.request("ghost.status")
            else:
                result = client.request("ghost.run", {"objective": arguments.objective, "wait": arguments.wait}, progress=_progress)
        else:
            raise AssertionError(command)
        _emit(result, as_json=as_json)
        return 0
    except KeyboardInterrupt:
        return 130
    except WorldlineError as exc:
        print(f"worldline: {exc.code}: {exc.message}", file=sys.stderr)
        if as_json and exc.details:
            print(json.dumps(exc.details, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
