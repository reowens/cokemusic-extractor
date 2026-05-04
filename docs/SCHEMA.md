# SCHEMA — Rail A JSON output

Rail A (`extract/extract_room.py`) writes one JSON file per room:

```json
{
  "room": "<room_name>",
  "source_cct": "http://127.0.0.1:8765/publicrooms/<room>.cct",
  "cast_lib_loaded_into": 19,
  "member_count": 85,
  "members": [
    {
      "cast_lib": 19,
      "cast_member": 122,
      "name": "<member_name>",
      "member_type": "<bitmap|script|text|sound|...>"
    }
  ],
  "text_bodies": {
    "<member_name>": "<text content>",
    "MapXml": "<...>",
    "SceneXml": "<...>",
    "EntryXml": "<...>"
  },
  "scripts": {
    "scripts": [
      {
        "name": "<script_name>",
        "text": "<lingo source>"
      }
    ],
    "total_count": 12
  }
}
```

## Field reference

| Field | Type | Notes |
|---|---|---|
| `room` | string | Internal room name from the cct (`<name>` in the Director header), not necessarily the user-visible room id. |
| `source_cct` | string | URL the extractor loaded the cct from (CORS server). |
| `cast_lib_loaded_into` | int | Always `19` — the cast lib slot the cct is hot-swapped into for extraction. Member numbers in `members[].cast_lib` will match. |
| `member_count` | int | Total number of cast members in the cct. |
| `members[]` | array | Every cast member, in cast number order. |
| `members[].cast_lib` | int | Always equal to `cast_lib_loaded_into`. |
| `members[].cast_member` | int | The cast member number (1-indexed). |
| `members[].name` | string | The member's name as set in Director, possibly empty. |
| `members[].member_type` | string | Director member type: `bitmap`, `script`, `text`, `sound`, `field`, `palette`, `filmLoop`, etc. |
| `text_bodies` | object | Keyed by member name; value is the text content of that text/field/script member. Director-internal names like `MapXml`, `SceneXml`, `EntryXml` carry the structured per-room layout / scene / entry metadata. |
| `scripts` | object | `scripts[]` lists every script-type member with its source. `total_count` is the array length (sanity check). |

## Bitmap members

PNGs for bitmap members are produced by Rail B (the Rust dumpers in
the fork), not Rail A. The Rust dumpers cross-reference Rail A's
`members[]` to know which cast members to render. Output:

- `<OUTPUT_ROOT>/assets/rooms/<room_id>/<member_name>.png`
- `<OUTPUT_ROOT>/assets/rooms/<room_id>/_members.json` — sidecar with
  per-member metadata (regPoint, bitDepth, originalBitDepth, useAlpha,
  width, height) consumed by downstream atlas builders.

The `_members.json` schema mirrors the dumper source — see
`vm-rust/tests/dump_cct_bitmaps.rs` in the fork for the canonical
shape.
