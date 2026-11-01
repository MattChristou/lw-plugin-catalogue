# LightWave plugin catalogue

The latest version of each plugin, read by **Plugin Updates** (Layout:
Utilities > Check for Plugin Updates) to tell users which of their installed
plugins have a newer version.

Plugin Updates fetches:

    https://raw.githubusercontent.com/MattChristou/lw-plugin-catalogue/main/catalogue.json

## Format

```json
{
  "format": 1,
  "updated": "2026-11-01",
  "plugins": {
    "DeltaMush": {
      "name": "Delta Mush",
      "version": "0.9.1",
      "url": "https://example.com/delta-mush",
      "notes": "One line on what changed."
    }
  }
}
```

- The key (`DeltaMush`) is the plugin's **id**: the one its binary exports
  (`LWF_PLUGIN_INFO("DeltaMush", ...)` in a `.p`, or the
  `LWF_PLUGIN_INFO = {"id": ...}` line in a `.py`).
- `version` is required. Versions compare numerically field by field
  (`1.10` > `1.9`, `1.2` = `1.2.0`); a prerelease sorts before its release
  (`1.0-rc.1` < `1.0`); a leading `v` and `+build` are ignored.
- `name`, `url` and `notes` are optional. Without a `url` the update is
  listed with "no download link yet".
- Unknown keys are ignored, so fields can be added without breaking older
  copies of Plugin Updates. A breaking change raises `format`; older copies
  then say they need updating instead of misreading it.

## Adding or updating an entry

`tools/set_entry.py` reads the id and version from a built plugin, so the
catalogue always matches what was shipped:

```sh
python tools/set_entry.py path/to/DeltaMush.p --name "Delta Mush" \
    --url https://example.com/delta-mush --notes "Faster rebinding."
```

Re-running it for a new build updates the version and keeps the other
fields unless they are given again.
