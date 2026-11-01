"""Complete captured-log readback with a finite exact progress policy."""
import hashlib
import os
import re
from xgen_common import HERE, FILE, load_json, regular

CHUNK = 65536
LINE = 4096
RECORDS = 8192
POLICY_BYTES = 512 * 1024


def identity_schema(value, limit):
    if not isinstance(value, dict) or set(value) != {"bytes", "sha256"}:
        raise RuntimeError("missing/malformed capture identity")
    size, sha = value["bytes"], value["sha256"]
    if type(size) is not int or not 0 <= size < limit:
        raise RuntimeError("capture count type/limit; possible evidence loss")
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
        raise RuntimeError("capture hash type/syntax")


def consume(chunk, state, allowed):
    """Bounded interpretation only; original complete file is never altered."""
    for value in chunk:
        if state["failure"] is not None:
            return
        if value == 10:
            state["records"] += 1
            if state["records"] > RECORDS:
                state["failure"] = "record count limit"
            elif bytes(state["pending"]) not in allowed:
                state["failure"] = "unregistered diagnostic record"
            state["pending"].clear()
        elif not 32 <= value <= 126:
            state["failure"] = "control/non-ASCII diagnostic byte"
        elif len(state["pending"]) >= LINE:
            state["failure"] = "overlong diagnostic record"
        else:
            state["pending"].append(value)


def validate_stream(path, expected, limit, allowed):
    """Hash all captured bytes even when interpretation already rejects them."""
    identity_schema(expected, limit)
    fd, info = regular(path, limit)
    total, sha = 0, hashlib.sha256()
    state = {"pending": bytearray(), "records": 0, "failure": None}
    try:
        if info.st_size != expected["bytes"]:
            raise RuntimeError("capture length changed/missing evidence")
        # At most(limit-1) nonempty one-byte reads, then EOF.
        for _ in range(limit + 1):
            raw = os.read(fd, CHUNK)
            if not raw:
                actual = {"bytes": total, "sha256": sha.hexdigest()}
                if actual != expected or os.fstat(fd).st_size != total:
                    raise RuntimeError("capture hash/length changed")
                if state["pending"] and state["failure"] is None:
                    state["failure"] = "incomplete diagnostic record"
                if state["failure"] is not None:
                    raise RuntimeError(state["failure"])
                return {"identity": actual, "records": state["records"]}
            total += len(raw)
            if total >= limit:
                raise RuntimeError("capture reached limit; possible evidence loss")
            sha.update(raw)
            consume(raw, state, allowed)
        raise RuntimeError("diagnostic read iteration bound")
    finally:
        os.close(fd)


def progress_policy():
    policy = load_json(HERE / "progress-policy.json", POLICY_BYTES)
    if (not isinstance(policy, dict) or policy.get("schema") != "worldline.xgen.progress.v2"
            or not isinstance(policy.get("records"), dict)
            or set(policy["records"]) != {"minimal", "core", "helpers"}):
        raise RuntimeError("progress policy schema")
    result = {}
    for stage, rows in policy["records"].items():
        if not isinstance(rows, list) or len(rows) > 4096:
            raise RuntimeError("progress policy count/type")
        allowed = set()
        for row in rows:
            if (not isinstance(row, str) or not 0 < len(row) <= LINE
                    or any(not 32 <= ord(char) <= 126 for char in row)):
                raise RuntimeError("progress policy record type/bytes")
            allowed.add(row.encode("ascii"))
        if len(allowed) != len(rows):
            raise RuntimeError("duplicate progress policy record")
        result[stage] = frozenset(allowed)
    return result


def validate_pair(paths, identities, limit, stdout_allowed):
    results, failures = {}, []
    for channel in ("stdout", "stderr"):
        try:
            allowed = stdout_allowed if channel == "stdout" else frozenset()
            results[channel] = validate_stream(paths[channel], identities[channel], limit, allowed)
        except (OSError, RuntimeError, TypeError, KeyError, ValueError) as error:
            failures.append(channel + ": " + str(error)[:256])
    if failures:
        raise RuntimeError("; ".join(failures))
    return results


def stage_diagnostics(name, out, err, item):
    if name in ("minimal", "core", "helpers"):
        allowed = progress_policy()[name]
    elif name == "target":
        allowed = frozenset({b"aarch64-linux-gnu"})
    elif name == "version":
        allowed = frozenset({b"16.1.0"})
    elif name in ("generation-a", "generation-b"):
        allowed = frozenset()
    else:
        raise RuntimeError("unregistered diagnostic stage")
    item["diagnostic_validation"] = "RUNNING"
    try:
        result = validate_pair({"stdout": out, "stderr": err}, item, FILE, allowed)
        if name in ("target", "version") and result["stdout"]["records"] != 1:
            raise RuntimeError("one exact target/version record required")
    except (OSError, RuntimeError, TypeError, KeyError, ValueError):
        item["diagnostic_validation"] = "FAILED"
        raise
    item["diagnostic_validation"] = "OBSERVED_EXACT_PROGRESS_OR_SILENCE"
    return result


def recovery_diagnostics(prefix, item, limit):
    counts = item.get("captured_bytes")
    if not isinstance(counts, dict) or set(counts) != {"stdout", "stderr"}:
        raise RuntimeError("missing recovery capture counts")
    for channel in ("stdout", "stderr"):
        identity_schema(item.get(channel), limit)
        if type(counts[channel]) is not int or counts[channel] != item[channel]["bytes"]:
            raise RuntimeError("recovery capture count type/mismatch")
    return validate_pair({name: prefix.with_suffix("." + name)
                          for name in ("stdout", "stderr")}, item, limit, frozenset())
