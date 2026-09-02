"""Package pre-rendered PNG icon sizes into Windows ICO and macOS ICNS files."""

from pathlib import Path
import struct


ROOT = Path(__file__).parents[1]
PNG_DIR = ROOT / "assets" / "icons" / "png"
ICON_DIR = PNG_DIR.parent


def build_ico() -> Path:
    sizes = (16, 32, 48, 64, 128, 256)
    images = [(size, (PNG_DIR / f"icon-{size}.png").read_bytes()) for size in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + (16 * len(images))
    directory = bytearray()
    payload = bytearray()
    for size, data in images:
        dimension = 0 if size == 256 else size
        directory.extend(struct.pack(
            "<BBBBHHII", dimension, dimension, 0, 0, 1, 32, len(data), offset
        ))
        payload.extend(data)
        offset += len(data)
    destination = ICON_DIR / "qa-evidence-builder.ico"
    destination.write_bytes(header + directory + payload)
    return destination


def build_icns() -> Path:
    chunks = (
        (b"icp4", 16),
        (b"icp5", 32),
        (b"icp6", 64),
        (b"ic07", 128),
        (b"ic08", 256),
        (b"ic09", 512),
        (b"ic10", 1024),
    )
    payload = bytearray()
    for kind, size in chunks:
        data = (PNG_DIR / f"icon-{size}.png").read_bytes()
        payload.extend(kind + struct.pack(">I", len(data) + 8) + data)
    destination = ICON_DIR / "qa-evidence-builder.icns"
    destination.write_bytes(b"icns" + struct.pack(">I", len(payload) + 8) + payload)
    return destination


if __name__ == "__main__":
    print(build_ico())
    print(build_icns())
