"""Fail if catalogue.json would mislead Plugin Updates.

Checks: valid JSON, "format" 1, a "plugins" object, and for each entry an
id made of letters, digits and '_', an object with a non-empty string
"version", and string "name"/"url"/"notes" when present (url: https).
"""
import json
import re
import sys
from pathlib import Path


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "catalogue.json")
    problems = []
    try:
        cat = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        sys.exit("%s is not valid JSON: %s" % (path, e))
    if cat.get("format") != 1:
        problems.append('"format" must be 1')
    plugins = cat.get("plugins")
    if not isinstance(plugins, dict):
        problems.append('"plugins" must be an object')
        plugins = {}
    for pid, e in plugins.items():
        if not re.fullmatch(r"[A-Za-z0-9_]{1,63}", pid):
            problems.append("%s: an id is letters, digits and _ (at most 63)" % pid)
        if not isinstance(e, dict):
            problems.append("%s: must be an object" % pid)
            continue
        v = e.get("version")
        if not isinstance(v, str) or not v.strip() or len(v) > 31:
            problems.append("%s: needs a \"version\" string (at most 31 characters)" % pid)
        for k in ("name", "url", "notes"):
            if k in e and not isinstance(e[k], str):
                problems.append("%s: \"%s\" must be a string" % (pid, k))
        if isinstance(e.get("url"), str) and e["url"] and not e["url"].startswith("https://"):
            problems.append("%s: \"url\" must be https://" % pid)
    for p in problems:
        print("::error::%s" % p)
    print("%d plugins, %d problems" % (len(plugins), len(problems)))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
