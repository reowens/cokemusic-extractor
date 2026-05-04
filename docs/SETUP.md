# SETUP — cokemusic-extractor

How to set up the toolchain and run both extraction rails.

## Prereqs

- **Python ≥ 3.10** (for Rail A — text bodies)
- **Rust + cargo** (stable; for Rail B — bitmap dumpers)
- **jq** (`brew install jq` on macOS) — used by `setup.sh`
- **Cast files** (`.cct`, `.dcr`) sourced from a community archive — this
  repo ships tools only, no binaries

## One-shot setup

```bash
./setup.sh
```

Reads `dirplayer-rs.lock`, clones the dirplayer-rs fork at the pinned
SHA into `../dirplayer-rs` (sibling to this checkout). Override the
destination with `DIRPLAYER_DEST=...` or pass it as the first arg.

Idempotent — re-run after a lockfile bump to fetch + checkout the new
SHA.

## Environment

Copy `.env.example` to `.env` and fill in the four paths. The Rail B
dumpers (run from inside the fork checkout) read these from the
environment.

```bash
cp .env.example .env
$EDITOR .env
source .env
```

## Rail B — bitmap dumpers (the routine path)

From the fork checkout root (after `setup.sh` clones the fork as a
sibling):

```bash
cd ../dirplayer-rs    # or "$DIRPLAYER_DEST"

# Backgrounds + per-room sprites for the 23 publicrooms
cargo test -p vm-rust --test dump_cct_bitmaps -- --nocapture

# Studio templates (Studio A-G + suites)
cargo test -p vm-rust --test dump_studio_bitmaps -- --nocapture

# Engine cast libraries (cc_room, cc_furniture, chatengine, etc.)
cargo test -p vm-rust --test dump_engine_bitmaps -- --nocapture

# Furniture regPoint metadata (JSON only, no PNGs)
cargo test -p vm-rust --test dump_furniture_bitmaps -- --nocapture

# Recycler mini-game (FurniFactory2.dcr)
cargo test -p vm-rust --test dump_dcr_bitmaps -- --nocapture
```

Outputs land at:
- `<OUTPUT_ROOT>/rooms/<room_id>/...` — publicroom + studio PNGs and
  `_members.json` sidecars
- `<OUTPUT_ROOT>/ui/...` — engine cast library PNGs
- `<OUTPUT_ROOT>/furniture/_cc_furniture_members.json` — furniture
  regPoint metadata (JSON only, no PNGs)
- `<OUTPUT_ROOT>/games/recycler/` — Recycler mini-game PNGs +
  `_members.json` (also dual-written to
  `/tmp/dirplayer_dumps/recycler/` as a fixed scratch path for
  debugging)

Output paths are also documented in each dumper's source-file header
inside the fork checkout.

## Rail A — text bodies (rare, heavy)

Only needed if a `.cct` file changes upstream (which is essentially
never for CokeMusic — the casts are read-only archives).

```bash
# 1. Start the CORS file server
python3 extract/cors_server.py        # default :8765

# 2. Boot dirplayer-rs in Electron with MCP enabled.
#    See ../dirplayer-rs/README.md for the build instructions.

# 3. Drive extraction
python3 extract/extract_room.py <room> <out.json>
```

`extract_room.py` hot-swaps the cct into cast lib 19 inside the
running dirplayer instance and dumps members + text bodies + scripts
to JSON. See [`SCHEMA.md`](SCHEMA.md) for the output shape.

## Lockfile bumps

`dirplayer-rs.lock` pins the fork's URL + branch + SHA. To bump:

1. Land the change on `reowens/dirplayer-rs#cokemusic`.
2. Note the new SHA: `git -C $DIRPLAYER_DEST rev-parse HEAD`.
3. Update `dirplayer-rs.lock`'s `sha` field.
4. Re-run the dumpers; ship the resulting PNG / `_members.json`
   deltas alongside the bump.
