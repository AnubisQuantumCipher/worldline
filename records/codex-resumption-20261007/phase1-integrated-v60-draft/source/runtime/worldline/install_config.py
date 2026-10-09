from __future__ import annotations

import json
from pathlib import Path
import re

from .canonical import atomic_write
from .errors import WorldlineError

_WIDGET_ID = "khephri.worldline"
_BEGIN = "-- BEGIN WORLDLINE (managed by install.sh)"
_END = "-- END WORLDLINE (managed by install.sh)"
_BLOCK = f'''{_BEGIN}
-- SUPER + SHIFT + W displaced Omawrite.
hl.unbind("SUPER + SHIFT + W")
o.bind("SUPER + SHIFT + W", "WORLDLINE: fork reality", "omarchy-shell shell summon khephri.worldline '{{\\"mode\\":\\"fork\\"}}'")

-- SUPER + CTRL + W displaced Network.
hl.unbind("SUPER + CTRL + W")
o.bind("SUPER + CTRL + W", "WORLDLINE: multiverse", "omarchy-shell shell summon khephri.worldline '{{\\"mode\\":\\"multiverse\\"}}'")

-- SUPER + ALT + RIGHT displaced Move window to group on right.
hl.unbind("SUPER + ALT + RIGHT")
o.bind("SUPER + ALT + RIGHT", "WORLDLINE: next reality", "worldline switch --next")
{_END}
'''


def patch_shell(path: Path) -> None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        layout = value["bar"]["layout"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise WorldlineError("INVALID_SHELL_CONFIG", f"cannot patch {path}: {exc}") from exc
    if not isinstance(layout, dict):
        raise WorldlineError("INVALID_SHELL_CONFIG", "bar.layout is not an object")
    for section, entries in layout.items():
        if not isinstance(entries, list):
            raise WorldlineError("INVALID_SHELL_CONFIG", f"bar.layout.{section} is not an array")
        layout[section] = [entry for entry in entries if not (isinstance(entry, dict) and entry.get("id") == _WIDGET_ID)]
    selected_section = "right" if "right" in layout else next(iter(layout), None)
    if selected_section is None:
        raise WorldlineError("INVALID_SHELL_CONFIG", "bar.layout has no sections")
    for section, entries in layout.items():
        if any(isinstance(entry, dict) and entry.get("id") == "khephri.jackal" for entry in entries):
            selected_section = section
            break
    else:
        for section, entries in layout.items():
            if any(isinstance(entry, dict) and entry.get("id") == "omarchy.indicators" for entry in entries):
                selected_section = section
                break
    entries = layout[selected_section]
    jackal = next((index for index, entry in enumerate(entries) if isinstance(entry, dict) and entry.get("id") == "khephri.jackal"), None)
    indicators = next((index for index, entry in enumerate(entries) if isinstance(entry, dict) and entry.get("id") == "omarchy.indicators"), None)
    index = jackal + 1 if jackal is not None else indicators if indicators is not None else len(entries)
    entries.insert(index, {"id": _WIDGET_ID})
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def patch_bindings(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorldlineError("INVALID_HYPR_BINDINGS", f"cannot patch {path}: {exc}") from exc
    pattern = re.compile(re.escape(_BEGIN) + r".*?" + re.escape(_END) + r"\n?", re.DOTALL)
    cleaned = pattern.sub("", text).rstrip()
    atomic_write(path, (cleaned + "\n\n" + _BLOCK).encode("utf-8"))
