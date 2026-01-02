#!/usr/bin/env python3
"""
Generate multiple H807SA probe DAT files in one go, using a known-good 04.dat as template.

Assumes 04.dat-like structure:
- 512-byte header
- payload is frames of 4096 bytes
- 4096 = 1024 pixels * 4 bytes/pixel
- frame count inferred from file size

What it does:
- Copies the template exactly
- Overwrites the first N frames (hold-frames) with a visible probe pattern
- Writes multiple variants to help infer:
    * meaning/order of 4 bytes per pixel
    * mapping of pixels across 8 ports (sequential vs port-block vs interleaved)

Probe pattern (base intent):
- Put distinct "channel gates" on 4 probe pixels:
    P0: FF 00 00 FF
    P1: 00 FF 00 FF
    P2: 00 00 FF FF
    P3: FF FF FF FF
But each variant permutes/interprets these bytes differently.

Usage:
  python generate_h807sa_probes.py --template 04.dat --outdir OUT --hold-frames 400

Then copy all generated .DAT files to SD card and try them one by one.
"""

from __future__ import annotations
import argparse
from pathlib import Path

HEADER_SIZE = 512
PIXELS_PER_FRAME = 1024
BPP = 4
FRAME_SIZE = PIXELS_PER_FRAME * BPP  # 4096

# The "ideal" probe tuples (conceptually FF gates + FF master):
# We'll permute these into different byte orders depending on variant.
PROBE_PIXELS_IDEAL = [
    ("P0_Ronly", (0xFF, 0x00, 0x00, 0xFF)),  # R gate, master=FF
    ("P1_Gonly", (0x00, 0xFF, 0x00, 0xFF)),  # G gate, master=FF
    ("P2_Bonly", (0x00, 0x00, 0xFF, 0xFF)),  # B gate, master=FF
    ("P3_RGB",   (0xFF, 0xFF, 0xFF, 0xFF)),  # all gates/master=FF
]

def infer_frames(template_bytes: bytes) -> int:
    if len(template_bytes) < HEADER_SIZE + FRAME_SIZE:
        raise ValueError("Template too small to be 04.dat-like.")
    payload = len(template_bytes) - HEADER_SIZE
    if payload % FRAME_SIZE != 0:
        raise ValueError(
            f"Template payload ({payload}) not divisible by frame size ({FRAME_SIZE}). "
            "If this isn't 04.dat-like, adjust constants."
        )
    return payload // FRAME_SIZE

def idx_sequential(n: int = 4) -> list[int]:
    return list(range(n))

def idx_port_blocks(n: int = 4) -> list[int]:
    """
    Assume 8 ports, 128 pixels per port -> total 1024.
    Patch first pixel of port 1, port 2, port 3, port 4 (as the 4 probes).
    """
    per_port = 128
    return [0*per_port + 0, 1*per_port + 0, 2*per_port + 0, 3*per_port + 0]

def idx_interleaved_ports(n: int = 4) -> list[int]:
    """
    Assume interleaved by port:
    pixel0port0, pixel0port1, ... pixel0port7, pixel1port0, ...
    Then the first 4 "pixels" in the frame correspond to port0..port3 at pixel index 0.
    """
    return [0, 1, 2, 3]

def pack_order(r: int, g: int, b: int, m: int, order: str) -> bytes:
    """
    Map conceptual components to actual stored byte order.
    Components: R, G, B, M (M could be master / W / alpha).
    """
    src = {"R": r, "G": g, "B": b, "M": m}
    order = order.upper()
    if len(order) != 4 or any(ch not in "RGBM" for ch in order) or len(set(order)) != 4:
        raise ValueError(f"Bad order: {order} (must be a permutation of RGBM)")
    return bytes(src[ch] for ch in order)

def make_frame_all_zero() -> bytearray:
    return bytearray([0x00] * FRAME_SIZE)

def apply_probe(frame: bytearray, pixel_indices: list[int], order: str, replicate: bool = False) -> None:
    """
    Apply the 4 probe pixels at the requested pixel indices.

    If replicate=True, force each pixel to be either 0000 or FFFF (replicated mask style),
    using the max of the intended 4-tuple as the replicated value.
    """
    for (label, (r, g, b, m)), px in zip(PROBE_PIXELS_IDEAL, pixel_indices):
        off = px * BPP
        if off + 4 > len(frame):
            continue
        if replicate:
            v = max(r, g, b, m)
            frame[off:off+4] = bytes([v, v, v, v])
        else:
            frame[off:off+4] = pack_order(r, g, b, m, order)

def apply_probe_interleaved(frame: bytearray, ports_first4: list[int], order: str, replicate: bool = False) -> None:
    """
    Interleaved layout variant:
    Treat 'pixel index' as interleaved slots.
    For interleaved case we just reuse indices 0..3 but it's kept separate for clarity.
    """
    apply_probe(frame, ports_first4, order=order, replicate=replicate)

def write_variant(template: bytes, out_path: Path, hold_frames: int,
                  mapping: str, order: str, replicate: bool) -> None:
    frames = infer_frames(template)
    hold = min(hold_frames, frames)

    header = template[:HEADER_SIZE]
    payload = template[HEADER_SIZE:]

    out = bytearray()
    out.extend(header)

    # Build probe frame based on mapping
    probe_frame = make_frame_all_zero()

    if mapping == "seq":
        pix = idx_sequential(4)
        apply_probe(probe_frame, pix, order=order, replicate=replicate)
    elif mapping == "portblocks":
        pix = idx_port_blocks(4)
        apply_probe(probe_frame, pix, order=order, replicate=replicate)
    elif mapping == "interleaved":
        pix = idx_interleaved_ports(4)
        apply_probe_interleaved(probe_frame, pix, order=order, replicate=replicate)
    else:
        raise ValueError(f"Unknown mapping {mapping}")

    # Emit hold frames of probe, then copy remainder of original payload untouched
    for i in range(frames):
        if i < hold:
            out.extend(probe_frame)
        else:
            off = i * FRAME_SIZE
            out.extend(payload[off:off+FRAME_SIZE])

    out_path.write_bytes(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Working 04.dat")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--hold-frames", type=int, default=400,
                    help="How many initial frames to force the probe pattern (default 400)")
    args = ap.parse_args()

    template_path = Path(args.template)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    template = template_path.read_bytes()
    frames = infer_frames(template)
    print(f"Template: {template_path.name} size={len(template)} frames={frames} frame_size={FRAME_SIZE}")

    # Variants:
    # - mapping: seq / portblocks / interleaved
    # - order: permutations to test whether bytes correspond to R,G,B,Master (M)
    # - replicate: whether controller expects replicated mask (FFFF / 0000) style
    variants = [
        # Sequential pixels
        ("seq_RGBM",      "seq",       "RGBM", False),
        ("seq_BGRM",      "seq",       "BGRM", False),
        ("seq_GRBM",      "seq",       "GRBM", False),
        ("seq_MRGB",      "seq",       "MRGB", False),  # master first
        ("seq_RGBM_REPL", "seq",       "RGBM", True),   # replicated mask style

        # Port blocks (128 pixels per port)
        ("pb_RGBM",       "portblocks","RGBM", False),
        ("pb_BGRM",       "portblocks","BGRM", False),
        ("pb_MRGB",       "portblocks","MRGB", False),
        ("pb_REPL",       "portblocks","RGBM", True),

        # Interleaved ports
        ("il_RGBM",       "interleaved","RGBM", False),
        ("il_MRGB",       "interleaved","MRGB", False),
        ("il_REPL",       "interleaved","RGBM", True),
    ]

    for name, mapping, order, replicate in variants:
        out_path = outdir / f"PROBE_{name}.DAT"
        write_variant(template, out_path, args.hold_frames, mapping, order, replicate)
        print(f"Wrote {out_path.name}  mapping={mapping:10s} order={order} replicate={replicate}")

    print("\nDMX test suggestion:")
    print("  - Set DMX1 (master)=255")
    print("  - Try DMX RGB = (255,0,0), then (0,255,0), then (0,0,255), then (255,255,255)")
    print("  - Look at the first 4 lit pixels (or first pixel per port) and note which file makes them behave as expected.")

if __name__ == "__main__":
    main()
