#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Extract one publicroom .cct's data via dirplayer MCP into a single JSON file."""
import json
import sys
import urllib.request

MCP_URL = "http://localhost:9847/"
CAST_LIB = 19  # Studio slot we hot-swap into
CAST_BASE = "http://127.0.0.1:8765/publicrooms"


def call(method: str, params: dict | None = None, req_id: int = 1) -> dict:
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def tool(name: str, arguments: dict, req_id: int = 1) -> dict:
    r = call("tools/call", {"name": name, "arguments": arguments}, req_id)
    if "error" in r:
        raise RuntimeError(f"MCP error: {r['error']}")
    text = r["result"]["content"][0]["text"]
    return json.loads(text)


def eval_expr(code: str, req_id: int = 1) -> dict:
    return tool("eval_lingo", {"code": code}, req_id)


def unquote_string(value: str) -> str:
    """Lingo eval returns string values wrapped in literal quotes; unwrap them."""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def extract(room_name: str, out_path: str) -> None:
    cct_url = f"{CAST_BASE}/{room_name}.cct"

    print(f"[0/5] Clearing castLib({CAST_LIB}) via Empty.cct cycle...", file=sys.stderr)
    r = eval_expr(f'castLib({CAST_LIB}).fileName = "http://127.0.0.1:8765/Empty.cct"', req_id=0)
    assert r.get("success"), r

    print(f"[1/5] Hot-swapping castLib({CAST_LIB}).fileName -> {cct_url}", file=sys.stderr)
    r = eval_expr(f'castLib({CAST_LIB}).fileName = "{cct_url}"', req_id=1)
    assert r.get("success"), r

    print(f"[2/5] Listing cast members of lib {CAST_LIB}...", file=sys.stderr)
    members = tool("list_cast_members", {"cast_lib": CAST_LIB}, req_id=2)
    print(f"      {len(members)} members loaded", file=sys.stderr)

    text_payloads: dict[str, str] = {}
    print(f"[3/5] Reading text/field bodies via eval_lingo...", file=sys.stderr)
    for m in members:
        if m["member_type"] in ("text", "field"):
            num = m["cast_member"]
            try:
                r = eval_expr(f"the text of member {num} of castLib {CAST_LIB}", req_id=100 + num)
                if r.get("success") and r.get("result_type") == "string":
                    text_payloads[m["name"]] = unquote_string(r["result_value"])
                else:
                    text_payloads[m["name"]] = f"<EVAL_FAILED: {r}>"
            except Exception as e:
                text_payloads[m["name"]] = f"<EXCEPTION: {e}>"

    print(f"[4/5] Listing scripts in lib {CAST_LIB}...", file=sys.stderr)
    scripts = tool("list_scripts", {"cast_lib": CAST_LIB}, req_id=3)

    out = {
        "room": room_name,
        "source_cct": cct_url,
        "cast_lib_loaded_into": CAST_LIB,
        "member_count": len(members),
        "members": members,
        "text_bodies": text_payloads,
        "scripts": scripts,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path} ({len(json.dumps(out))} bytes)", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: extract_room.py <room_name> <output_path>", file=sys.stderr)
        sys.exit(1)
    extract(sys.argv[1], sys.argv[2])
