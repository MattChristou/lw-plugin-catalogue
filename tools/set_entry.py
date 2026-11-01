"""Add or update a plugin's entry in catalogue.json from its built file.

    python tools/set_entry.py <plugin.p | plugin.py> [--name N] [--url U]
                              [--notes T] [--catalogue catalogue.json]

The id and version come from the plugin itself: a .p's LWFPluginInfo record
(lwf_version.h in LWF) or a .py's LWF_PLUGIN_INFO line, so the catalogue
lists exactly what was built. Fields not given keep their current values.
"""
import argparse
import ast
import datetime
import json
import struct
import sys
from pathlib import Path

MAGIC = b"LWFPLUGININFO\x01\x7e\x00"     # 16 bytes, LWF_PLUGIN_INFO_MAGIC
RECORD = struct.Struct("<16sii64s32s64s")  # magic, abi, size, id, version, lwf


def _cstr(b):
    end = b.find(b"\0")
    return None if end <= 0 else b[:end].decode("utf-8")


def read_binary(data):
    at = data.find(MAGIC)
    while at >= 0:
        chunk = data[at:at + RECORD.size]
        if len(chunk) == RECORD.size:
            _, abi, size, pid, ver, _lwf = RECORD.unpack(chunk)
            pid, ver = _cstr(pid), _cstr(ver)
            if abi == 1 and size == RECORD.size and pid and ver:
                return pid, ver
        at = data.find(MAGIC, at + 1)
    return None


def read_python(text):
    for node in ast.parse(text).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "LWF_PLUGIN_INFO"):
            info = ast.literal_eval(node.value)
            if isinstance(info, dict) and info.get("id") and info.get("version"):
                return str(info["id"]), str(info["version"])
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("plugin", type=Path)
    ap.add_argument("--name")
    ap.add_argument("--url")
    ap.add_argument("--notes")
    ap.add_argument("--catalogue", type=Path,
                    default=Path(__file__).resolve().parent.parent / "catalogue.json")
    a = ap.parse_args(argv)

    if a.plugin.suffix.lower() == ".py":
        found = read_python(a.plugin.read_text(encoding="utf-8"))
    else:
        found = read_binary(a.plugin.read_bytes())
    if not found:
        sys.exit("%s carries no plugin info (LWF_PLUGIN_INFO)" % a.plugin)
    pid, version = found

    cat = json.loads(a.catalogue.read_text(encoding="utf-8"))
    entry = cat.setdefault("plugins", {}).setdefault(pid, {})
    old = entry.get("version")
    entry["version"] = version
    for key in ("name", "url", "notes"):
        value = getattr(a, key)
        if value is not None:
            entry[key] = value
    cat["updated"] = datetime.date.today().isoformat()
    a.catalogue.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("%s: %s -> %s" % (pid, old or "(new)", version))


if __name__ == "__main__":
    main()
