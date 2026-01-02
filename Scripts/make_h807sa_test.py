#!/usr/bin/env python3
"""
Make an H807SA DAT "byte-order probe" by editing only the first 3 pixels.

- Copies the first 512 bytes (header) from a template DAT
- Leaves the rest of the payload unchanged EXCEPT:
    pixel 1 bytes = FF 00 00
    pixel 2 bytes = 00 FF 00
    pixel 3 bytes = 00 00 FF
- Supports 3 bytes/pixel (RGB) or 4 bytes/pixel (RGBW); for RGBW, W=00.

Usage:
  python probe_order.py --template 01.dat --out PROBE.DAT --bpp 3
  python probe_order.py --template 01.dat --out PROBE_RGBW.DAT --bpp 4
"""

import argparse
from pathlib import Path

HEADER = 512

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Known-good DAT (e.g. 01.dat)")
    ap.add_argument("--out", required=True, help="Output DAT")
    ap.add_argument("--bpp", type=int, default=3, choices=[3,4], help="Bytes per pixel: 3 (RGB) or 4 (RGBW)")
    args = ap.parse_args()

    data = bytearray(Path(args.template).read_bytes())
    if len(data) < HEADER + args.bpp * 3:
        raise ValueError("Template too small to patch 3 pixels.")

    # Start of pixel payload
    base = HEADER

    # Raw triples exactly as requested
    p1 = [0xFF, 0x00, 0x00]
    p2 = [0x00, 0xFF, 0x00]
    p3 = [0x00, 0x00, 0xFF]

    def write_pixel(i: int, rgb3):
        off = base + i * args.bpp
        data[off:off+3] = bytes(rgb3)
        if args.bpp == 4:
            data[off+3] = 0x00  # W = 0

    write_pixel(0, p1)  # LED1
    write_pixel(1, p2)  # LED2
    write_pixel(2, p3)  # LED3

    Path(args.out).write_bytes(data)
    print(f"Wrote {args.out}")
    print("LED1 bytes: FF 00 00")
    print("LED2 bytes: 00 FF 00")
    print("LED3 bytes: 00 00 FF")
    print(f"bpp={args.bpp} (RGB{'W' if args.bpp==4 else ''})")

if __name__ == "__main__":
    main()
