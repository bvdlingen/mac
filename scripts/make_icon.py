#!/usr/bin/env python3
"""Generate a 1024x1024 app icon (speech bubble on a rust-orange tile).

Pure Python, no dependencies: writes the PNG by hand with zlib + struct.
Usage: python3 make_icon.py <output.png>
"""
import struct
import sys
import zlib

N = 1024
CORNER = 190  # background tile corner radius

# Gradient background (top -> bottom), rust orange.
TOP = (247, 92, 43)
BOTTOM = (196, 54, 26)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def inside_round_rect(x, y, cx, cy, w, h, r):
    """Point test for a rounded rectangle centered at (cx, cy)."""
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    if not (x0 <= x < x1 and y0 <= y < y1):
        return False
    # Corner circles: if in a corner quadrant, must be inside the corner circle.
    qx = min(x - x0, x1 - x)
    qy = min(y - y0, y1 - y)
    if qx < r and qy < r:
        dx, dy = r - qx, r - qy
        return dx * dx + dy * dy <= r * r
    return True


def in_circle(x, y, cx, cy, rad):
    dx, dy = x - cx, y - cy
    return dx * dx + dy * dy <= rad * rad


def in_tri(x, y, p1, p2, p3):
    def sign(a, b, c):
        return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

    s1 = sign((x, y), p1, p2)
    s2 = sign((x, y), p2, p3)
    s3 = sign((x, y), p3, p1)
    neg = s1 < 0 or s2 < 0 or s3 < 0
    pos = s1 > 0 or s2 > 0 or s3 > 0
    return not (neg and pos)


BUBBLE = (512, 450, 560, 430, 110)  # cx, cy, w, h, r
TAIL = ((400, 640), (520, 640), (430, 730))
DOT_Y = 450
DOTS = [(512 - 140, DOT_Y), (512, DOT_Y), (512 + 140, DOT_Y)]
DOT_R = 52
DOT_COLOR = (154, 43, 18)


def pixel(x, y):
    t = y / (N - 1)
    # Background tile (rounded square, transparent outside).
    if not inside_round_rect(x, y, N / 2, N / 2, N, N, CORNER):
        return (0, 0, 0, 0)
    bg = lerp(TOP, BOTTOM, t)

    # Speech bubble + tail.
    if inside_round_rect(x, y, *BUBBLE) or in_tri(x, y, *TAIL):
        # Dots inside the bubble.
        for dx, dy in DOTS:
            if in_circle(x, y, dx, dy, DOT_R):
                return DOT_COLOR + (255,)
        return (255, 255, 255, 255)
    return bg + (255,)


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "icon.png"
    rows = bytearray()
    for y in range(N):
        rows.append(0)  # PNG filter type 0 (none)
        for x in range(N):
            rows.extend(pixel(x, y))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
