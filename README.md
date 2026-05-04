# cokemusic-extractor

Convert CokeMusic / Coke Studios Director cast files (`.cct`, `.dcr`)
into structured JSON + PNGs.

Built for fan archivists and reconstruction projects working from the
original 2007 client. Format conversion only — not a runtime port.
(See [igorlira/dirplayer-rs](https://github.com/igorlira/dirplayer-rs)
if you want to actually *play* Director files in a browser.)

## What this does

CokeMusic / Coke Studios was a 2005-2007 browser game by Coca-Cola
built on Macromedia Director. The cast files (`.cct`, `.dcr`) hold
all the room art, sprites, scripts, and scene metadata in Director's
binary format. This toolchain converts those files into formats
modern code can read:

- **Bitmap members → PNG** (per-room background, every sprite,
  furniture members, palette-cycle variants, filmLoop manifests).
- **Text bodies → JSON** (scene XML, room descriptions, member names,
  attached Lingo scripts).

## Two rails

| Rail | Tool | Output | Frequency |
|---|---|---|---|
| **A — text bodies + scripts** | `extract/extract_room.py` (Python; drives Electron + dirplayer-rs MCP) | `extracted/<room>.json` per room | Once per cct change. Heavy ritual. |
| **B — bitmap members** | Cargo tests in the dirplayer-rs fork (Rust, no Electron) | `<room_id>/<member>.png`, `_members.json` | Routine. Re-run after fork SHA bump. |

Most users only need Rail B. Rail A's outputs are typically committed
alongside downstream consumers, so a fresh checkout has the text
bodies without re-running Rail A.

## Quickstart

```bash
git clone https://github.com/reowens/cokemusic-extractor
cd cokemusic-extractor

./setup.sh             # clones the dirplayer-rs fork as ../dirplayer-rs
                       # at the SHA pinned in dirplayer-rs.lock
cp .env.example .env   # then edit paths
```

See [`docs/SETUP.md`](docs/SETUP.md) for the full walkthrough,
[`docs/SCHEMA.md`](docs/SCHEMA.md) for the JSON output shape, and
[`docs/PROVENANCE.md`](docs/PROVENANCE.md) for legal posture.

## Repo layout

```
cokemusic-extractor/
├── extract/             Python: cct → JSON text bodies / scripts (Rail A)
├── docs/                SETUP, SCHEMA, PROVENANCE
├── dirplayer-rs.lock    Pinned fork SHA
└── setup.sh             Clones fork at pinned SHA
```

The Rust bitmap dumpers (Rail B) live in the fork at
[`reowens/dirplayer-rs#cokemusic`](https://github.com/reowens/dirplayer-rs/tree/cokemusic) —
not in this repo. `setup.sh` clones the fork for you; from there you
`cd ../dirplayer-rs && cargo test ...` to dump bitmaps. See
[SETUP.md](docs/SETUP.md) for the exact commands.

## License

GPL-3.0-or-later. Inherited from
[`igorlira/dirplayer-rs`](https://github.com/igorlira/dirplayer-rs).
See [LICENSE](LICENSE).

## Cast files

This repo ships **tools only** — no cast binaries, no extracted PNGs,
no extracted JSON. Cast files for the original game can be sourced
from community archives.
