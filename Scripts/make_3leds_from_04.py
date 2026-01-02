#!/usr/bin/env python3
"""
Build a 4-pixel RGB mask probe DAT from a known-working 04.dat-style file.

Assumes:
- 512-byte header
- payload is frames of 1024 pixels * 4 bytes = 4096 bytes per frame
- each pixel is 4 bytes [?, ?, ?, ?] (we're probing meaning)

Creates a static program: first four pixels are set to:
  P0: FF 00 00 FF
  P1: 00 FF 00 FF
  P2: 00 00 FF FF
  P3: FF FF FF FF
Rest: 00 00 00 00
"""

import argparse
from pathlib import Path

HEADER_SIZE = 512
PIXELS = 1024
BPP = 4
FRAME_SIZE = PIXELS * BPP

PATTERN = [
    bytes([0xFF, 0x00, 0x00, 0xFF]),  # pixel 0
    bytes([0x00, 0xFF, 0x00, 0xFF]),  # pixel 1
    bytes([0x00, 0x00, 0xFF, 0xFF]),  # pixel 2
    bytes([0xFF, 0xFF, 0xFF, 0xFF]),  # pixel 3
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Use your working 04.dat as template")
    ap.add_argument("--out", required=True, help="Output DAT file")
    args = ap.parse_args()

    data = Path(args.template).read_bytes()
    if len(data) < HEADER_SIZE + FRAME_SIZE:
        raise ValueError("Template too small or not a 04.dat-style file.")

    header = data[:HEADER_SIZE]
    payload = data[HEADER_SIZE:]

    if len(payload) % FRAME_SIZE != 0:
        raise ValueError(
            f"Template payload ({len(payload)}) is not divisible by {FRAME_SIZE}. "
            "This script assumes 1024 pixels * 4 bytes per pixel."
        )

    frames = len(payload) // FRAME_SIZE
    print(f"Template frames: {frames}")

    # Build one frame
    frame = bytearray([0x00] * FRAME_SIZE)

    # Apply first 4 pixels
    for i, px in enumerate(PATTERN):
        off = i * BPP
        frame[off:off+BPP] = px

    # Repeat for all frames
    out_bytes = header + (bytes(frame) * frames)
    Path(args.out).write_bytes(out_bytes)

    print(f"Wrote {args.out} ({len(out_bytes)} bytes)")
    print("First 4 pixels set to:")
    print(" P0: FF 00 00 FF")
    print(" P1: 00 FF 00 FF")
    print(" P2: 00 00 FF FF")
    print(" P3: FF FF FF FF")

if __name__ == "__main__":
    main()
