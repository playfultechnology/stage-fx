#!/usr/bin/env python3
"""
Generate a simple H807SA .DAT test file by cloning the 512-byte header
from a known-good template .DAT, then writing step records.

This works well for experimentation because the H807SA format appears to be:
- 512-byte header/padding block
- followed by N records of fixed width (often 12 bytes in your examples)

Usage examples:
  # Solid "on" (RGB = 255,0,0) for 1000 steps, pad 24 steps of zero
  python make_h807sa_dat.py --template 01.dat --out TEST_RED.DAT --r 255 --g 0 --b 0

  # Same but explicit step count
  python make_h807sa_dat.py --template 01.dat --out TEST.DAT --r 0 --g 255 --b 0 --steps 2000

  # If you suspect RGBW packing, supply W as well
  python make_h807sa_dat.py --template 01.dat --out TEST_RGBW.DAT --r 10 --g 20 --b 30 --w 40 --channels 4
"""

import argparse
from pathlib import Path

HEADER_SIZE = 512


def clamp_byte(x: int) -> int:
    if x < 0 or x > 255:
        raise ValueError(f"Value {x} out of range 0..255")
    return x


def build_record(step_width: int, channels: int, r: int, g: int, b: int, w: int) -> bytes:
    """
    Build one fixed-width record by repeating [R,G,B] or [R,G,B,W] until filled.
    """
    if channels not in (3, 4):
        raise ValueError("--channels must be 3 or 4")

    base = [r, g, b] if channels == 3 else [r, g, b, w]

    rec = bytearray()
    while len(rec) < step_width:
        rec.extend(base)

    # Trim to exact width
    return bytes(rec[:step_width])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Path to a known-good H807SA .DAT to copy header from")
    ap.add_argument("--out", required=True, help="Output .DAT path")
    ap.add_argument("--r", type=int, required=True, help="Red 0..255")
    ap.add_argument("--g", type=int, required=True, help="Green 0..255")
    ap.add_argument("--b", type=int, required=True, help="Blue 0..255")
    ap.add_argument("--w", type=int, default=0, help="White 0..255 (used only if --channels 4)")
    ap.add_argument("--channels", type=int, default=3, help="3 for RGB or 4 for RGBW packing (default: 3)")
    ap.add_argument("--steps", type=int, default=1000, help="Number of 'on' steps to write (default: 1000)")
    ap.add_argument("--pad-steps", type=int, default=24, help="Trailing zero steps (default: 24)")
    ap.add_argument("--step-width", type=int, default=12, help="Bytes per step record (default: 12)")
    args = ap.parse_args()

    template_path = Path(args.template)
    out_path = Path(args.out)

    r = clamp_byte(args.r)
    g = clamp_byte(args.g)
    b = clamp_byte(args.b)
    w = clamp_byte(args.w)

    step_width = args.step_width
    if step_width <= 0:
        raise ValueError("--step-width must be > 0")
    if args.steps < 0 or args.pad_steps < 0:
        raise ValueError("--steps and --pad-steps must be >= 0")

    # Read template header
    data = template_path.read_bytes()
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Template file too small to contain {HEADER_SIZE}-byte header")

    header = data[:HEADER_SIZE]

    # Sanity check (optional): "HC" signature at bytes 2-3
    # Not required, but helpful.
    if header[2:4] != b"HC":
        print("Warning: template header does not contain 'HC' at bytes 2-3; continuing anyway.")

    # Build output
    out = bytearray()
    out.extend(header)

    on_record = build_record(step_width, args.channels, r, g, b, w)
    off_record = bytes([0] * step_width)

    out.extend(on_record * args.steps)
    out.extend(off_record * args.pad_steps)

    out_path.write_bytes(out)

    print(f"Wrote {out_path}")
    print(f"Header: {HEADER_SIZE} bytes copied from {template_path.name}")
    print(f"Steps: {args.steps} on + {args.pad_steps} pad")
    print(f"Step width: {step_width} bytes  |  Channels packed: {args.channels}")
    print(f"Total size: {len(out)} bytes")


if __name__ == "__main__":
    main()
