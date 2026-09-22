#!/usr/bin/env python3
"""Fail-closed pre-upgrade check for a live WORLDLINE installation.

Every question this asks has three possible answers, and only one of them permits an upgrade:

    OK        the condition was observed to be safe
    REFUSE    the condition was observed to be unsafe
    UNKNOWN   the condition could not be observed  -> treated as REFUSE

The old installer inlined a check that printed ``0`` whenever the status document could not be
parsed, so an unreadable daemon read as "no jobs are running" and the upgrade proceeded. Nothing
here converts an unanswered question into permission.

    preflight.py [--json] [--allow-ghosts]

Exit 0 only when every gate is OK. Exit 2 on any REFUSE or UNKNOWN, 3 on a usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ACTIVE_JOB_STATES = ("STARTING", "RUNNING", "FINALIZING")
OPEN_TRANSACTION_STATES = ("PREPARED", "COMMITTING", "QUARANTINED")


class Gate:
    def __init__(self) -> None:
        self.results: list[dict] = []

    def record(self, name: str, state: str, detail: str, observed=None) -> None:
        self.results.append({"gate": name, "state": state, "detail": detail, "observed": observed})

    def ok(self, name, detail, observed=None):
        self.record(name, "OK", detail, observed)

    def refuse(self, name, detail, observed=None):
        self.record(name, "REFUSE", detail, observed)

    def unknown(self, name, detail, observed=None):
        # An unanswered question is not permission. This is the whole point of the file.
        self.record(name, "UNKNOWN", detail, observed)

    @property
    def permitted(self) -> bool:
        return all(r["state"] == "OK" for r in self.results)


def run_cli(binary: str, *args: str, timeout: int = 60) -> tuple[int, str, str]:
    try:
        proc = subprocess.run([binary, "--json", *args], stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 255, "", f"{type(exc).__name__}: {exc}"
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit the machine-readable report only")
    parser.add_argument("--allow-ghosts", action="store_true",
                        help="permit the upgrade while ghost worlds are enabled (they can fork on any PRIME checkpoint)")
    parser.add_argument("--binary", default=str(Path.home() / ".local/bin/worldline"))
    parser.add_argument("--unit", default="worldlined.service", help="the daemon's user unit")
    parser.add_argument("--socket", help="the daemon socket to look for (default: $XDG_RUNTIME_DIR/worldline/worldlined.sock)")
    args = parser.parse_args()

    gate = Gate()
    report: dict = {"schemaVersion": 1, "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "binary": args.binary}

    # ---- is there an installation at all? -----------------------------------------------------
    if not Path(args.binary).is_file():
        gate.ok("installation-present", "no existing installation; this is a first install, nothing to protect")
        report["mode"] = "first-install"
        report["gates"] = gate.results
        report["permitted"] = gate.permitted
        print(json.dumps(report, indent=2))
        return 0
    report["mode"] = "upgrade"

    unit_active = subprocess.run(["systemctl", "--user", "is-active", "--quiet", args.unit]).returncode == 0
    socket = Path(args.socket) if args.socket else \
        Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}") / "worldline/worldlined.sock"
    socket_present = socket.exists()
    report["daemonUnitActive"] = unit_active
    report["socketPresent"] = socket_present

    # The installation is ALWAYS asked, never inferred from the unit. A daemon can run without
    # its unit being active (launched directly, as the lab harness does), and a `systemctl` that
    # cannot answer must not be read as "nothing is running". "Quiet" therefore has to be
    # observed from three independent signals agreeing, not assumed from one.
    status = None
    daemon_quiet = False
    code, out, err = run_cli(args.binary, "status")
    if code == 0:
        try:
            status = json.loads(out)
        except json.JSONDecodeError as exc:
            gate.unknown("status-readable", f"the status document is not valid JSON: {exc}", {"head": out[:200]})
        else:
            if not isinstance(status, dict) or "jobs" not in status or "worlds" not in status:
                gate.unknown("status-readable", "the status document does not have the expected shape",
                             {"keys": sorted(status)[:20] if isinstance(status, dict) else None})
                status = None
            else:
                gate.ok("status-readable", "the status document parsed and has the expected shape")
    elif not unit_active and not socket_present:
        daemon_quiet = True
        gate.ok("status-readable",
                "no daemon is running: the installation does not answer, its unit is inactive and there is no socket")
    else:
        gate.unknown("status-readable",
                     f"`worldline status` exited {code} while the unit is "
                     f"{'active' if unit_active else 'inactive'} and the socket is "
                     f"{'present' if socket_present else 'absent'}; the daemon's state is unknown",
                     {"stderr": err.strip()[-400:]})
    gate.ok("daemon-running", "the daemon unit is active; the gates below are read from it") if unit_active \
        else gate.ok("daemon-running", "the daemon unit is not active")

    # ---- no active agent work -----------------------------------------------------------------
    if status is None and not daemon_quiet:
        gate.unknown("no-active-jobs", "cannot enumerate jobs because the status document was unreadable")
        gate.unknown("no-unfinished-worlds", "cannot enumerate worlds because the status document was unreadable")
    elif status is None:
        gate.ok("no-active-jobs", "no daemon is running, so no job can be running under it")
        gate.ok("no-unfinished-worlds", "no daemon is running")
    else:
        active = [j for j in status.get("jobs", []) if j.get("state") in ACTIVE_JOB_STATES]
        if active:
            gate.refuse("no-active-jobs", f"{len(active)} agent job(s) are active; restarting the daemon would orphan them",
                        [{"world": j.get("world"), "state": j.get("state")} for j in active])
        else:
            gate.ok("no-active-jobs", "no job is STARTING, RUNNING or FINALIZING")

        mutable = [w for w in status.get("worlds", []) if w.get("state") in ("MUTABLE", "FINALIZING")]
        if mutable:
            gate.refuse("no-unfinished-worlds", f"{len(mutable)} world(s) are still MUTABLE/FINALIZING",
                        [{"alias": w.get("alias"), "state": w.get("state")} for w in mutable])
        else:
            gate.ok("no-unfinished-worlds", "every world is in a terminal state")

    # ---- transient units belonging to worlds --------------------------------------------------
    listing = subprocess.run(["systemctl", "--user", "list-units", "worldline-*", "--all", "--plain", "--no-legend"],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if listing.returncode != 0:
        gate.unknown("no-world-units", "could not list the user manager's worldline-* units")
    else:
        units = [line.split()[0] for line in listing.stdout.splitlines() if line.split()]
        live = [u for u in units if u != args.unit]
        if live:
            gate.refuse("no-world-units", f"{len(live)} transient world unit(s) still exist", live[:20])
        else:
            gate.ok("no-world-units", "no transient world unit is present")

    # ---- doctor: transactions, recovery, integrity --------------------------------------------
    doctor = None
    if daemon_quiet:
        gate.ok("doctor-readable", "no daemon is running; doctor cannot and need not be consulted")
    else:
        code, out, err = run_cli(args.binary, "doctor", timeout=120)
        if code != 0:
            gate.unknown("doctor-readable", f"`worldline doctor` exited {code}", {"stderr": err.strip()[-400:]})
        else:
            try:
                doctor = json.loads(out)
            except json.JSONDecodeError as exc:
                gate.unknown("doctor-readable", f"the doctor document is not valid JSON: {exc}")
            else:
                gate.ok("doctor-readable", "the doctor document parsed")

    if doctor is None and not daemon_quiet:
        for name in ("no-open-transactions", "recovery-clean", "store-integrity", "root-integrity"):
            gate.unknown(name, "the doctor document was unreadable, so this could not be observed")
    elif doctor is not None:
        open_tx = doctor.get("openTransactions")
        if open_tx is None:
            gate.unknown("no-open-transactions", "doctor did not report openTransactions")
        elif open_tx:
            gate.refuse("no-open-transactions",
                        f"{len(open_tx)} transaction(s) are open; an upgrade during a prepared transaction risks a half-applied collapse",
                        open_tx[:10])
        else:
            gate.ok("no-open-transactions", "no transaction is open")

        recovery = doctor.get("recovery") or {}
        if recovery.get("state") == "OK" and not recovery.get("quarantined"):
            gate.ok("recovery-clean", "recovery reports OK with nothing quarantined")
        elif not recovery:
            gate.unknown("recovery-clean", "doctor did not report recovery state")
        else:
            gate.refuse("recovery-clean", f"recovery state is {recovery.get('state')!r}", recovery)

        store = doctor.get("storeIntegrity") or {}
        if store.get("state") == "OK":
            gate.ok("store-integrity", "store integrity OK")
        elif not store:
            gate.unknown("store-integrity", "doctor did not report storeIntegrity")
        else:
            gate.refuse("store-integrity", f"store integrity is {store.get('state')!r}", store)

        roots = (doctor.get("rootIntegrity") or {}).get("roots")
        if roots is None:
            gate.unknown("root-integrity", "doctor did not report rootIntegrity")
        else:
            bad = [r for r in roots if r.get("state") != "OK"]
            if bad:
                gate.refuse("root-integrity", f"{len(bad)} managed root(s) are not OK", bad)
            else:
                gate.ok("root-integrity", f"all {len(roots)} managed roots report OK")

        unsupervised = doctor.get("unsupervisedWorlds")
        if unsupervised is None:
            gate.unknown("no-unsupervised-worlds", "doctor did not report unsupervisedWorlds")
        elif unsupervised:
            gate.refuse("no-unsupervised-worlds", "worlds without supervision exist", unsupervised[:10])
        else:
            gate.ok("no-unsupervised-worlds", "no unsupervised world")

    # ---- ghosts can fork a world on any PRIME checkpoint --------------------------------------
    if not daemon_quiet:
        code, out, _err = run_cli(args.binary, "ghost", "status")
        if code != 0:
            gate.unknown("ghosts-quiet", "could not read ghost status")
        else:
            try:
                ghost = json.loads(out)
            except json.JSONDecodeError:
                gate.unknown("ghosts-quiet", "ghost status is not valid JSON")
            else:
                enabled = bool(ghost.get("enabled"))
                if not enabled:
                    gate.ok("ghosts-quiet", "ghosts are disabled; no world can be forked by a checkpoint")
                elif args.allow_ghosts:
                    gate.ok("ghosts-quiet", "ghosts are ENABLED and the operator passed --allow-ghosts", ghost)
                else:
                    gate.refuse("ghosts-quiet",
                                "ghosts are enabled; a PRIME checkpoint during the upgrade would fork worlds. "
                                "Disable them (worldline ghost disable) or pass --allow-ghosts.", ghost)
    else:
        gate.ok("ghosts-quiet", "no daemon is running; nothing can fork")

    # ---- room for the backup -------------------------------------------------------------------
    state = Path.home() / ".local/state/worldline"
    share = Path.home() / ".local/share/worldline"
    try:
        def tree_bytes(path: Path, skip: set[str]) -> int:
            total = 0
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if str(Path(root) / d) not in skip]
                for f in files:
                    p = Path(root) / f
                    if p.is_symlink() or not p.exists():
                        continue
                    total += p.stat().st_size
            return total
        needed = tree_bytes(state, {str(state / "install-backups")}) + tree_bytes(share, set())
        free = shutil.disk_usage(state if state.exists() else Path.home()).free
        report["backupBytesNeeded"] = needed
        report["freeBytes"] = free
        if free > needed * 3:
            gate.ok("backup-space", f"{needed // 2**20} MiB to back up, {free // 2**30} GiB free")
        else:
            gate.refuse("backup-space", f"{needed // 2**20} MiB to back up but only {free // 2**20} MiB free")
    except OSError as exc:
        gate.unknown("backup-space", f"could not size the data directories: {exc}")

    report["gates"] = gate.results
    report["permitted"] = gate.permitted
    report["refused"] = [r for r in gate.results if r["state"] != "OK"]

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for r in gate.results:
            mark = {"OK": "  ok  ", "REFUSE": "REFUSE", "UNKNOWN": "UNKNWN"}[r["state"]]
            print(f"[{mark}] {r['gate']}: {r['detail']}")
        print()
        print("preflight: UPGRADE PERMITTED" if gate.permitted else
              "preflight: UPGRADE REFUSED — an UNKNOWN gate is a refusal, not permission")
    return 0 if gate.permitted else 2


if __name__ == "__main__":
    raise SystemExit(main())
