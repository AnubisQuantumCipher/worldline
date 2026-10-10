"""One rule for turning a policy argv token into the object it names inside a managed root.

Two resolvers disagreeing is the same defect as two checks disagreeing. `resolve_verifiers`
(which decides the AUTHORITATIVE verifier bytes) and `rewrite_argv` (which decides which argv
token points at the staged copy) each had their own copy of this logic, and a campaign found the
seam:

    /root/gate.py      both agree -> gate.py                        (fine)
    /root/./gate.py    membership recorded "./gate.py",             (B: forged overlay ran,
                       rewrite looked up "gate.py" -> miss           reported BOUND over PRIME)
    /root//gate.py     remainder "/gate.py" is absolute, dropped    (D: same)
    /root/../root/x    lexically escapes, silently "not a verifier" (T2-P4b: same)

The membership side took the remainder verbatim; the rewrite side normalised it. This module is
the single rule both now use, and it distinguishes three outcomes that the callers must treat
differently:

    ("member", root_key, relative)  a clean regular-file path inside a root
    ("escape", None, None)          the token names a root (by prefix) but the object is not
                                    cleanly inside it -- an absolute remainder, a `..` that
                                    climbs out, or a root itself. This is NOT "leave it alone":
                                    a token that addresses a managed root but cannot be bound
                                    to a member is exactly the ambiguity the campaign exploited.
    None                            the token addresses no managed root: an interpreter, a
                                    system tool, a `-flag`. Left untouched.

Lexical normalisation is not a filesystem-containment proof -- symlinks and root identity are
handled by the callers, which stat the object. This module makes the two callers agree on which
object a token designates; it does not by itself decide the object is safe.
"""
from __future__ import annotations

import os
from typing import Mapping, Sequence


def root_prefixes(roots: Mapping[str, object] | Sequence[tuple[str, str]]) -> list[tuple[str, str]]:
    """`[(prefix-with-trailing-slash, root_key), ...]`, longest first so the most specific root
    wins when one logical root nests inside another."""
    if isinstance(roots, Mapping):
        pairs = [(str(path).rstrip("/") + "/", key) for key, path in roots.items()]
    else:
        pairs = [(str(path).rstrip("/") + "/", key) for key, path in roots]
    return sorted(pairs, key=lambda pair: -len(pair[0]))


def resolve_token(token: str, prefixes: Sequence[tuple[str, str]], *,
                  primary_root_key: str | None = None,
                  cwd: str = "") -> tuple[str, str | None, str | None]:
    """Classify one argv token. See the module docstring for the three outcomes."""
    if not token or token.startswith("-"):
        return ("outside", None, None)

    if token.startswith("/"):
        for prefix, key in prefixes:
            if token.startswith(prefix):
                # The remainder may carry the shapes the campaign used: a leading `/` (from a
                # doubled separator), a `./` segment, or a `..` that climbs back out. Collapse
                # them, then insist the result is a clean relative path strictly inside the root.
                remainder = os.path.normpath(token[len(prefix):].lstrip("/"))
                if remainder in (".", "") or remainder.startswith("..") or os.path.isabs(remainder):
                    return ("escape", None, None)
                return ("member", key, remainder)
            if token.rstrip("/") + "/" == prefix:
                # The token IS the root directory.
                return ("escape", None, None)
        return ("outside", None, None)

    # A relative token is resolved against the check's cwd within the primary root.
    if primary_root_key is None:
        return ("outside", None, None)
    relative = os.path.normpath(os.path.join(cwd, token) if cwd else token)
    if relative.startswith("..") or os.path.isabs(relative):
        return ("escape", None, None)
    return ("member", primary_root_key, relative)
