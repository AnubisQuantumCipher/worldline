#!/usr/bin/env python3
"""Fail-closed pre-upgrade check for a live WORLDLINE installation.

Every question has three possible answers, and only one permits an upgrade:

    OK        the condition was observed to be safe
    REFUSE    the condition was observed to be unsafe
    UNKNOWN   the condition could not be observed  -> treated as REFUSE

A **declared roster** is what makes that true. `Gate.permitted` does not ask whether the checks
that happened to run were happy; it asks whether every gate in `REQUIRED_GATES` was recorded AND
is OK. A question that is never asked is therefore a refusal, not silence. This matters because
the same defect has now appeared three times in this installer's history: the original inline
check printed 0 on any exception; a later version short-circuited every gate on an inactive
unit; a third simply failed to record five gates when the daemon was quiet. Each time the shape
was identical — an unasked question became permission.

Daemon liveness is read as a STATE, not as the exit code of `is-active`. `activating` and
`deactivating` are neither running nor stopped: a unit on its way up will finish coming up
during the backup, and one on its way down may still be writing. Both refuse.

When the daemon genuinely is not running, the conditions that matter most still are: open
transactions, recovery and integrity live on disk and survive a stop. Prepared transactions are
therefore read straight out of the store directory — that is precisely the state an interrupted
install leaves behind — and the gates that cannot be answered offline refuse unless the operator
passes --daemon-down-unchecked.

    preflight.py [--json] [--allow-ghosts] [--daemon-down-unchecked] [--with-payloads]

Exit 0 only when every required gate is OK. Exit 2 otherwise, 3 on a usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ACTIVE_JOB_STATES = ("STARTING", "RUNNING", "FINALIZING")
OPEN_TRANSACTION_STATES = ("PREPARED", "COMMITTING", "QUARANTINED")

# The roster. A gate missing from the report is a refusal, exactly like an UNKNOWN one.
REQUIRED_GATES = (
    "daemon-state",
    "status-readable",
    "no-active-jobs",
    "no-unfinished-worlds",
    "no-world-units",
    "doctor-readable",
    "no-open-transactions",
    "recovery-clean",
    "store-integrity",
    "root-integrity",
    "no-unsupervised-worlds",
    "ghosts-quiet",
    "backup-space",
)
OFFLINE_UNANSWERABLE = ("recovery-clean", "store-integrity", "root-integrity", "no-unsupervised-worlds")


class Gate:
    def __init__(self, roster: tuple[str, ...] = REQUIRED_GATES) -> None:
        self.results: list[dict] = []
        self.roster = roster

    def record(self, name: str, state: str, detail: str, observed=None) -> None:
        self.results.append({"gate": name, "state": state, "detail": detail, "observed": observed})

    def ok(self, name, detail, observed=None):
        self.record(name, "OK", detail, observed)

    def refuse(self, name, detail, observed=None):
        self.record(name, "REFUSE", detail, observed)

    def unknown(self, name, detail, observed=None):
        self.record(name, "UNKNOWN", detail, observed)

    @property
    def missing(self) -> list[str]:
        recorded = {r["gate"] for r in self.results}
        return [name for name in self.roster if name not in recorded]

    @property
    def permitted(self) -> bool:
        return not self.missing and all(r["state"] == "OK" for r in self.results)


def run_cli(binary: str, *args: str, timeout: int = 60) -> tuple[int, str, str]:
    try:
        proc = subprocess.run([binary, "--json", *args], stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 255, "", f"{type(exc).__name__}: {exc}"
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def unit_state(systemctl: str, unit: str) -> str:
    """ActiveState, or 'unreachable' when the manager cannot answer. Never a boolean: `is-active`
    exits non-zero for failed, activating and deactivating alike, and reading that as "not
    running" is how an installer replaces a runtime out from under a live process."""
    try:
        proc = subprocess.run([systemctl, "--user", "show", "-p", "ActiveState", "--value", unit],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=30, text=True)
    except (OSError, subprocess.TimeoutExpired):
        return "unreachable"
    if proc.returncode != 0:
        return "unreachable"
    return proc.stdout.strip() or "unreachable"


def prepared_transactions(state_dir: Path) -> tuple[list[str] | None, str]:
    """Open transactions read from the store directory, so a stopped daemon does not blind the
    gate that matters most when the daemon is stopped."""
    directory = state_dir / "transactions"
    if not directory.is_dir():
        return [], f"no transactions directory under {state_dir}"
    records = sorted(directory.glob("*.json"))
    open_ids: list[str] = []
    for path in records:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None, f"{path.name} could not be read"
        if record.get("state") in OPEN_TRANSACTION_STATES:
            open_ids.append(str(record.get("transactionId") or path.stem))
    return open_ids, f"{len(records)} record(s) under {directory}"


def tree_bytes(path: Path, skip: set[str]) -> int:
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if str(Path(root) / d) not in skip]
        for name in files:
            p = Path(root) / name
            if p.is_symlink() or not p.exists():
                continue
            try:
                total += p.stat().st_size
            except OSError:
                continue
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit the machine-readable report only")
    parser.add_argument("--allow-ghosts", action="store_true",
                        help="permit while ghost worlds are enabled (they fork on any PRIME checkpoint)")
    parser.add_argument("--daemon-down-unchecked", action="store_true",
                        help="permit although a stopped daemon leaves recovery and integrity unobservable")
    parser.add_argument("--with-payloads", action="store_true",
                        help="the install will also copy payload data, so size it into the estimate")
    parser.add_argument("--binary", default=str(Path.home() / ".local/bin/worldline"))
    parser.add_argument("--unit", default="worldlined.service")
    parser.add_argument("--systemctl", default="systemctl", help="the systemctl to consult")
    parser.add_argument("--socket", help="daemon socket (default: $XDG_RUNTIME_DIR/worldline/worldlined.sock)")
    parser.add_argument("--state-dir", help="default: $XDG_STATE_HOME/worldline")
    parser.add_argument("--share-dir", help="default: $XDG_DATA_HOME/worldline")
    args = parser.parse_args()

    gate = Gate()
    # The runtime honours XDG_STATE_HOME / XDG_DATA_HOME; so must every tool that copies its data.
    state = Path(args.state_dir) if args.state_dir else \
        Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "worldline"
    share = Path(args.share_dir) if args.share_dir else \
        Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "worldline"
    report: dict = {"schemaVersion": 1, "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "binary": args.binary, "unit": args.unit, "stateDir": str(state), "shareDir": str(share),
                    "requiredGates": list(REQUIRED_GATES)}

    if not Path(args.binary).is_file():
        report.update({"mode": "first-install", "gates": [], "missingGates": [], "permitted": True, "refused": []})
        print(json.dumps(report, indent=2) if args.json else
              "preflight: no existing installation; this is a first install, nothing to protect")
        return 0
    report["mode"] = "upgrade"

    # ---- daemon liveness as a state -------------------------------------------------------------
    active_state = unit_state(args.systemctl, args.unit)
    socket = Path(args.socket) if args.socket else \
        Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}") / "worldline/worldlined.sock"
    socket_present = socket.exists()
    report["unitActiveState"] = active_state
    report["socketPresent"] = socket_present

    if active_state in ("activating", "deactivating"):
        gate.refuse("daemon-state",
                    f"the unit is {active_state}: neither running nor stopped, so an upgrade would either race it "
                    "coming up or replace it while it is still writing. Wait for it to settle.", active_state)
    elif active_state == "unreachable":
        gate.unknown("daemon-state", f"the user manager could not report ActiveState for {args.unit}", active_state)
    else:
        gate.ok("daemon-state", f"the unit is {active_state}", active_state)
    running = active_state in ("active", "reloading")

    # ---- the installation is always asked --------------------------------------------------------
    status = None
    quiet = False
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
    elif not running and active_state in ("inactive", "failed") and not socket_present:
        quiet = True
        gate.ok("status-readable",
                f"no daemon is running: the installation does not answer, the unit is {active_state}, and there "
                "is no socket")
    else:
        gate.unknown("status-readable",
                     f"`worldline status` exited {code} while the unit is {active_state} and the socket is "
                     f"{'present' if socket_present else 'absent'}; the daemon's state is unknown",
                     {"stderr": err.strip()[-400:]})

    if status is not None:
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
    elif quiet:
        gate.ok("no-active-jobs", "no daemon is running, so no job can be running under it")
        gate.ok("no-unfinished-worlds", "no daemon is running")
    else:
        gate.unknown("no-active-jobs", "cannot enumerate jobs because the status document was unreadable")
        gate.unknown("no-unfinished-worlds", "cannot enumerate worlds because the status document was unreadable")

    # ---- transient units belonging to worlds ------------------------------------------------------
    try:
        listing = subprocess.run([args.systemctl, "--user", "list-units", "worldline-*", "--all", "--plain",
                                  "--no-legend"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 text=True, timeout=30)
        listed, failed = listing.stdout, listing.returncode != 0
    except (OSError, subprocess.TimeoutExpired):
        listed, failed = "", True
    if failed:
        gate.unknown("no-world-units", "could not list the user manager's worldline-* units")
    else:
        live = [line.split()[0] for line in listed.splitlines() if line.split() and line.split()[0] != args.unit]
        if live:
            gate.refuse("no-world-units", f"{len(live)} transient world unit(s) still exist", live[:20])
        else:
            gate.ok("no-world-units", "no transient world unit is present")

    # ---- store-derived gates -----------------------------------------------------------------------
    doctor = None
    if quiet:
        gate.ok("doctor-readable", "no daemon is running; doctor cannot be consulted, so the store is read directly")
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

    if doctor is not None:
        open_tx = doctor.get("openTransactions")
        if open_tx is None:
            gate.unknown("no-open-transactions", "doctor did not report openTransactions")
        elif open_tx:
            gate.refuse("no-open-transactions",
                        f"{len(open_tx)} transaction(s) are open; upgrading during a prepared transaction risks a "
                        "half-applied collapse", open_tx[:10])
        else:
            gate.ok("no-open-transactions", "no transaction is open")

        recovery = doctor.get("recovery") or {}
        if not recovery:
            gate.unknown("recovery-clean", "doctor did not report recovery state")
        elif recovery.get("state") == "OK" and not recovery.get("quarantined"):
            gate.ok("recovery-clean", "recovery reports OK with nothing quarantined")
        else:
            gate.refuse("recovery-clean", f"recovery state is {recovery.get('state')!r}", recovery)

        store_integrity = doctor.get("storeIntegrity") or {}
        if not store_integrity:
            gate.unknown("store-integrity", "doctor did not report storeIntegrity")
        elif store_integrity.get("state") == "OK":
            gate.ok("store-integrity", "store integrity OK")
        else:
            gate.refuse("store-integrity", f"store integrity is {store_integrity.get('state')!r}", store_integrity)

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
    else:
        open_ids, how = prepared_transactions(state)
        if open_ids is None:
            gate.unknown("no-open-transactions", f"a transaction record could not be read offline: {how}")
        elif open_ids:
            gate.refuse("no-open-transactions",
                        f"{len(open_ids)} transaction(s) are open, read from the store directory", open_ids[:10])
        else:
            gate.ok("no-open-transactions", f"no open transaction in the store directory: {how}")
        for name in OFFLINE_UNANSWERABLE:
            if args.daemon_down_unchecked:
                gate.ok(name, "not observable with the daemon stopped; permitted by --daemon-down-unchecked")
            else:
                gate.unknown(name,
                             "the daemon is not answering, so this cannot be observed. It describes on-disk state "
                             "that survives a stop. Start the daemon, or pass --daemon-down-unchecked deliberately.")

    # ---- ghosts fork a world on any PRIME checkpoint ------------------------------------------------
    if quiet:
        gate.ok("ghosts-quiet", "no daemon is running; nothing can fork")
    else:
        code, out, _err = run_cli(args.binary, "ghost", "status")
        if code != 0:
            gate.unknown("ghosts-quiet", "could not read ghost status")
        else:
            try:
                ghost = json.loads(out)
            except json.JSONDecodeError:
                gate.unknown("ghosts-quiet", "ghost status is not valid JSON")
            else:
                if not ghost.get("enabled"):
                    gate.ok("ghosts-quiet", "ghosts are disabled; no world can be forked by a checkpoint")
                elif args.allow_ghosts:
                    gate.ok("ghosts-quiet", "ghosts are ENABLED and the operator passed --allow-ghosts", ghost)
                else:
                    gate.refuse("ghosts-quiet",
                                "ghosts are enabled; a PRIME checkpoint during the upgrade would fork worlds. "
                                "Disable them (worldline ghost disable) or pass --allow-ghosts.", ghost)

    # ---- room for what will actually be copied -------------------------------------------------------
    try:
        state_bytes = tree_bytes(state, {str(state / "install-backups")}) if state.exists() else 0
        payload_bytes = tree_bytes(share, set()) if (args.with_payloads and share.exists()) else 0
        free = shutil.disk_usage(state if state.exists() else Path.home()).free
        total = state_bytes + payload_bytes
        report.update({"stateBytes": state_bytes, "payloadBytes": payload_bytes, "freeBytes": free,
                       "payloadsIncluded": bool(args.with_payloads)})
        if not state.exists():
            gate.refuse("backup-space",
                        f"the state directory {state} does not exist, so either there is nothing to back up or the "
                        "paths this tool was given are wrong")
        elif free > total * 3:
            gate.ok("backup-space",
                    f"{total // 2**20} MiB to back up"
                    f"{' (payloads included)' if args.with_payloads else ' (payloads not copied)'}, "
                    f"{free // 2**30} GiB free")
        else:
            gate.refuse("backup-space", f"{total // 2**20} MiB to back up but only {free // 2**20} MiB free")
    except OSError as exc:
        gate.unknown("backup-space", f"could not size the data directories: {exc}")

    report["gates"] = gate.results
    report["missingGates"] = gate.missing
    report["permitted"] = gate.permitted
    report["refused"] = [r for r in gate.results if r["state"] != "OK"]

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for r in gate.results:
            mark = {"OK": "  ok  ", "REFUSE": "REFUSE", "UNKNOWN": "UNKNWN"}[r["state"]]
            print(f"[{mark}] {r['gate']}: {r['detail']}")
        for name in gate.missing:
            print(f"[MISSNG] {name}: never recorded, which is a refusal")
        print()
        print("preflight: UPGRADE PERMITTED" if gate.permitted else
              "preflight: UPGRADE REFUSED — an UNKNOWN or missing gate is a refusal, not permission")
    return 0 if gate.permitted else 2


if __name__ == "__main__":
    raise SystemExit(main())
