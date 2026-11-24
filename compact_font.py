#!/usr/bin/env python3
"""Build-time tool: compact the generated bitmap font data into fontblob.py.

Reads FONTS from fontdata.py (the build-time glyph dump, since removed),
serializes it to compact JSON, zlib-compresses it, base64-encodes it, and
writes fontblob.py with the blob wrapped at 200 chars per line. The blob is
generated data; main.py decodes it at runtime with stdlib only (base64 +
zlib + json). Run once: python3 compact_font.py

Kept in the repo as the provenance record for fontblob.py.
"""
import base64
import json
import zlib

from fontdata import FONTS


def main():
    raw = json.dumps(FONTS, separators=(",", ":")).encode()
    blob = base64.b64encode(zlib.compress(raw, 9)).decode()
    lines = [
        '"""Compact bitmap font data (generated — see compact_font.py).',
        "",
        "Base64 of zlib-compressed compact JSON of the FONTS dict.",
        "Decoded at runtime by main.py with stdlib only.",
        '"""',
        "",
        "BLOB = (",
    ]
    for i in range(0, len(blob), 200):
        lines.append("    %r" % blob[i:i + 200])
    lines.append(")")
    lines.append("")
    with open("fontblob.py", "w") as f:
        f.write("\n".join(lines))
    print("wrote fontblob.py:", len(blob), "chars in",
          len(lines) - 8, "data lines")


if __name__ == "__main__":
    main()
