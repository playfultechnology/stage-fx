#!/usr/bin/env python3
"""
H807SA 12-byte-step lane probe.
Creates a DAT that cycles which of the 12 bytes is 0xFF (others 0x00).
This helps identify which byte(s) affect your connected port/output.

It clones the 512-byte header from a known-good template (e.g. 01.dat)
and preserves total file size (important).

Usage:
  python lane_rotate_probe.py --template 01.dat --out PROBE_ROTATE.DAT

Optional:
  --hold 20     # number of steps to hold each lane on (slower)
  --value 255   # brightness value for the active lane
"""

import argparse
from pathlib import Path

HEADER_SIZE = 512
STEP_WIDTH = 12

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hold", type=int, default=30, help="Steps to hold each lane on (default 30)")
    ap.add_argument("--value", type=int, default=255, help="Active lane value 0..255 (default 255)")
    ap.add_argument("--pad-steps", type=int, default=24, help="Trailing all-zero steps (default 24)")
    args = ap.parse_args()

    if not (0 <= args.value <= 255):
        raise ValueError("--value must be 0..255")
    if args.hold <= 0:
        raise ValueError("--hold must be > 0")

    template = Path(args.template).read_bytes()
    if len(template) < HEADER_SIZE:
        raise ValueError("Template too small")

    header = template[:HEADER_SIZE]
    payload_len = len(template) - HEADER_SIZE

    if payload_len % STEP_WIDTH != 0:
        raise ValueError("Template is not the 12-bytes-per-step style DAT (payload not divisible by 12).")

    total_steps = payload_len // STEP_WIDTH
    if args.pad_steps >= total_steps:
        raise ValueError("--pad-steps must be less than total steps")

    usable_steps = total_steps - args.pad_steps

    # Build rotating payload
    out_payload = bytearray()

    step_idx = 0
    lane = 0
    while step_idx < usable_steps:
        # Hold this lane on for args.hold steps
        for _ in range(args.hold):
            if step_idx >= usable_steps:
                break
            rec = bytearray([0] * STEP_WIDTH)
            rec[lane] = args.value
            out_payload.extend(rec)
            step_idx += 1
        lane = (lane + 1) % STEP_WIDTH

    # Pad tail with zeros
    out_payload.extend(bytes([0] * STEP_WIDTH) * args.pad_steps)

    out_bytes = header + out_payload
    Path(args.out).write_bytes(out_bytes)

    print(f"Wrote {args.out}")
    print(f"Total steps: {total_steps} (probe {usable_steps} + pad {args.pad_steps})")
    print(f"Each lane held for {args.hold} steps; active value={args.value}")

if __name__ == "__main__":
    main()
