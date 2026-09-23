"""One startup policy for every Python process WORLDLINE runs on its own behalf.

A *trusted* process is one whose output WORLDLINE treats as its own observation: the check
harness that attests an examination happened, the materializer that snapshots a candidate, the
simulation runner, the netguard forwarder. A *candidate* process is the workload and the
verifiers it is examined by — those legitimately need candidate working directories and
candidate imports, and nothing here applies to them.

The rule is narrow and it is a security boundary, not tidiness:

    A trusted process must not take any part of its executable environment from a directory
    the candidate can write.

CPython hands one over by default, and which one depends on how the process was started.
Measured on this host with CPython 3.14.7, with a hostile module planted in each location:

    python3 -c SOURCE          sys.path[0] is the WORKING DIRECTORY   -> hijacked
    python3 /path/script.py    sys.path[0] is the SCRIPT'S DIRECTORY  -> hijacked
    python3 -I -S <either>     stdlib in both cases                   -> clean

Both directories are candidate-writable in normal operation: a check's working directory must
be inside a managed root, and `/run/worldline-runtime` is bind-mounted read-write and is the
world's XDG_RUNTIME_DIR. This was not theoretical. A candidate that planted `base64.py` where
the check harness would start owned the harness outright on its first import and fabricated a
passing result; the examiner never ran, and every other protection held while it happened.

`-I` removes the unsafe sys.path entry (it implies `-P`), ignores every PYTHON* variable and
drops the user site directory. `-S` additionally suppresses site initialisation, which is what
processes `.pth` files and `sitecustomize` — controlling PYTHONPATH alone does not reach those.

The consequence to respect when adding a trusted helper: **it may import the standard library
only.** `-S` means no site-packages. If a helper ever needs a third-party module, the answer is
to give it a trusted directory on an explicit path, never to drop these flags.
"""
from __future__ import annotations

# Absolute, so PATH cannot choose the interpreter either.
TRUSTED_INTERPRETER = "/usr/bin/python3"

# The policy itself, named once so a test can assert every launch site carries it.
ISOLATION_FLAGS: tuple[str, ...] = ("-I", "-S")


def trusted_inline(source: str, *arguments: str) -> tuple[str, ...]:
    """argv for a trusted helper supplied as inline source (`-c`)."""
    return (TRUSTED_INTERPRETER, *ISOLATION_FLAGS, "-c", source, *arguments)


def trusted_script(path: str, *arguments: str) -> tuple[str, ...]:
    """argv for a trusted helper supplied as a script path."""
    return (TRUSTED_INTERPRETER, *ISOLATION_FLAGS, path, *arguments)
