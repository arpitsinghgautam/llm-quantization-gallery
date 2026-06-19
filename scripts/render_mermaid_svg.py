#!/usr/bin/env python3
"""
Render all assets/mermaid/*.mmd → assets/mermaid-rendered/*.svg
using the kroki.io public API.

Usage: python scripts/render_mermaid_svg.py
"""
import base64, zlib, time, urllib.request, urllib.error
from pathlib import Path

ROOT     = Path(__file__).parent.parent
MMD_DIR  = ROOT / "assets" / "mermaid"
OUT_DIR  = ROOT / "assets" / "mermaid-rendered"
OUT_DIR.mkdir(exist_ok=True)

files = sorted(MMD_DIR.glob("*.mmd"))
ok = skipped = failed = 0

def render(path: Path, force: bool = False):
    global ok, skipped, failed
    out = OUT_DIR / (path.stem + ".svg")
    if out.exists() and not force:
        skipped += 1
        return

    src = path.read_text(encoding="utf-8").strip()
    # kroki.io encode: deflate + base64url
    compressed = zlib.compress(src.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    url = f"https://kroki.io/mermaid/svg/{encoded}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mermaid-render/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            svg = resp.read().decode("utf-8")
        out.write_text(svg, encoding="utf-8")
        ok += 1
        print(f"  [ok]   {path.stem}")
    except Exception as e:
        failed += 1
        print(f"  [fail] {path.stem}: {e}")

for i, f in enumerate(files):
    render(f)
    # Small pause every 5 to be polite to the API
    if (i + 1) % 5 == 0:
        time.sleep(0.5)

print(f"\nDone: {ok} rendered, {skipped} skipped, {failed} failed")
if failed:
    print("Re-run to retry failed ones.")
