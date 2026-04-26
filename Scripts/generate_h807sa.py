#!/usr/bin/env python3
from pathlib import Path
import argparse

HEADER_SIZE = 512
FRAME_SIZE  = 512
BPP         = 4  # bytes per pixel: R,G,B,W (W left 0)

def clamp(x): 
    return max(0, min(255, int(x)))

def parse_rgb(s: str):
    r, g, b = (clamp(int(p.strip(), 0)) for p in s.split(","))
    return r, g, b

def make_header(speed: int, pixels: int):
    """
    Minimal header that matches what we've observed:
      - bytes 2..3 = 'HC'
      - byte 18 = speed (this matched your '30' = 0x1E test)
      - byte 32 = pixels (this matched your 5-pixel header having 0x05 there)
    Everything else 0x00.
    """
    h = bytearray([0x00] * HEADER_SIZE)
    h[2:4] = b"HC"
    h[18]  = clamp(speed)
    h[32]  = clamp(pixels)
    return h

def make_frame(pixels: int, colors, reverse: bool):
    """
    colors: list of (r,g,b) length == pixels
    frame is padded to 512 bytes.
    """
    fr = bytearray([0x00] * FRAME_SIZE)

    max_pixels_in_frame = FRAME_SIZE // BPP
    if pixels > max_pixels_in_frame:
        raise ValueError(f"{pixels} pixels won't fit in one 512-byte frame with {BPP} BPP "
                         f"(max {max_pixels_in_frame}).")

    for i, (r, g, b) in enumerate(colors):
        j = (pixels - 1 - i) if reverse else i
        off = j * BPP
        fr[off + 0] = r
        fr[off + 1] = g
        fr[off + 2] = b
        fr[off + 3] = 0  # W/master unused
    return bytes(fr)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pixels", type=int, required=True)
    ap.add_argument("--color", default="255,0,0", help="R,G,B")
    ap.add_argument("--tail", type=int, default=0)
    ap.add_argument("--speed", type=int, default=50)
    ap.add_argument("--loops", type=int, default=5)
    ap.add_argument("--hold", type=int, default=2, help="duplicate each step this many frames")
    ap.add_argument("--reverse", action="store_true", help="reverse pixel order (if chase runs backwards)")
    args = ap.parse_args()

    if args.pixels <= 0:
        raise ValueError("--pixels must be > 0")
    if args.tail < 0:
        raise ValueError("--tail must be >= 0")
    if args.loops <= 0:
        raise ValueError("--loops must be > 0")
    if args.hold <= 0:
        raise ValueError("--hold must be > 0")

    r, g, b = parse_rgb(args.color)

    header = make_header(args.speed, args.pixels)

    frames = []
    positions = args.pixels + args.tail  # include tail-clear positions
    for _ in range(args.loops):
        for pos in range(positions):
            colors = [(0,0,0)] * args.pixels
            for t in range(args.tail + 1):
                p = pos - t
                if 0 <= p < args.pixels:
                    scale = 1.0 if t == 0 else (1.0 - t/(args.tail+1))
                    colors[p] = (clamp(r*scale), clamp(g*scale), clamp(b*scale))

            fr = make_frame(args.pixels, colors, reverse=args.reverse)
            for _ in range(args.hold):
                frames.append(fr)

    out = bytearray()
    out.extend(header)
    out.extend(b"".join(frames))

    Path(args.out).write_bytes(out)
    print(f"Wrote {args.out}")
    print(f"pixels={args.pixels} frames={len(frames)} speed={args.speed} tail={args.tail} hold={args.hold} reverse={args.reverse}")

if __name__ == "__main__":
    main()
