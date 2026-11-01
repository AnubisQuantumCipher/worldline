"""Pure finite policy construction from the exact frozen input roster."""
from pathlib import Path

SCHEMA = "worldline.xgen.progress.v2"
PROJECTS = {"minimal": ("GNATCOLL_Minimal",),
            "core": ("GNATCOLL_Minimal", "GNATCOLL_Core"),
            "helpers": ("Helpers",)}
LIBRARIES = {"minimal": ("gnatcoll_minimal",),
             "core": ("gnatcoll_minimal", "gnatcoll_core"),
             "helpers": ("helpers", "xtree")}


def progress(tag, artifact):
    if tag not in ("Ada", "C", "Asm", "gprbind", "gprlib", "archive", "index", "link", "mkdir"):
        raise RuntimeError("unregistered progress producer")
    return "   [" + tag + "]" + " " * (13 - len(tag)) + artifact


def source_names(stage, inputs):
    if len(inputs) != 342:
        raise RuntimeError("frozen input count required")
    selected = []
    for row in inputs:
        name = row["destination"]
        include = (name.startswith("source/gnatcoll/minimal/") if stage == "minimal"
                   else name.startswith("source/gnatcoll/") if stage == "core"
                   else name.startswith("source/spark/"))
        if include:
            selected.append(Path(name).name)
    return sorted(set(selected))


def stage_records(stage, inputs):
    rows = {"Setup", "Compile", "Bind", "Link", "Build Libraries"}
    for name in source_names(stage, inputs):
        suffix = Path(name).suffix
        if suffix in (".adb", ".ads"):
            rows.add(progress("Ada", name))
        elif suffix == ".c":
            rows.add(progress("C", name))
        elif suffix in (".s", ".S"):
            rows.add(progress("Asm", name))
    for project in PROJECTS[stage]:
        for spelling in sorted({project, project.lower()}):
            for directory in ("object", "library"):
                rows.add(progress("mkdir", directory + " directory for project " + spelling))
    for library in LIBRARIES[stage]:
        rows.add(progress("gprlib", library + ".lexch"))
        for tag in ("archive", "index"):
            rows.add(progress(tag, "lib" + library + ".a"))
    if stage == "helpers":
        rows.add(progress("gprbind", "xtree.bexch"))
        rows.add(progress("Ada", "xtree.ali"))
        rows.add(progress("link", "xtree.adb"))
        for name in ("b__xtree.adb", "b__xtree.ads", "b~xtree.adb", "b~xtree.ads"):
            rows.add(progress("Ada", name))
    return sorted(rows)


def policy(inputs, input_hash):
    return {"schema": SCHEMA, "input_pins_sha256": input_hash,
            "records": {stage: stage_records(stage, inputs)
                        for stage in ("minimal", "core", "helpers")}}
