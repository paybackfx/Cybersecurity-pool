#!/usr/bin/env python3
"""scorpion — parse and display image metadata (EXIF + basic attributes).

Part of the Arachnida project (a cybersecurity exercise).

For each image file given on the command line, scorpion prints basic
attributes (format, dimensions, size on disk, creation/modification date)
and, when present, the EXIF metadata — including a decoded GPS position.
Missing EXIF data is handled cleanly instead of crashing.

Usage:
    python scorpion.py FILE1 [FILE2 ...]
"""

import argparse
import os
import sys
from datetime import datetime

try:
    from PIL import Image, ExifTags
except ImportError:
    print(
        "[!] Pillow is required. Install it with: python -m pip install pillow",
        file=sys.stderr,
    )
    sys.exit(1)

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


def human_size(num_bytes):
    """Format a byte count as a human-readable string."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"


def format_timestamp(epoch):
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def print_basic_attributes(path, image):
    stats = os.stat(path)
    print("  Basic attributes:")
    print(f"    Format      : {image.format}")
    print(f"    Mode        : {image.mode}")
    print(f"    Dimensions  : {image.width} x {image.height} px")
    print(f"    File size   : {human_size(stats.st_size)}")
    # st_ctime is creation time on Windows, metadata-change time on Unix.
    print(f"    Created     : {format_timestamp(stats.st_ctime)}")
    print(f"    Modified    : {format_timestamp(stats.st_mtime)}")


def decode_gps(gps_raw):
    """Convert a raw EXIF GPSInfo block into readable fields."""
    gps = {}
    for key, value in gps_raw.items():
        tag = ExifTags.GPSTAGS.get(key, key)
        gps[tag] = value
    return gps


def gps_to_decimal(coordinate, reference):
    """Convert ((deg,), (min,), (sec,)) + ref (N/S/E/W) to a signed float."""
    try:
        degrees, minutes, seconds = (float(part) for part in coordinate)
        decimal = degrees + minutes / 60 + seconds / 3600
        if reference in ("S", "W"):
            decimal = -decimal
        return round(decimal, 6)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def print_exif(image):
    """Print EXIF metadata if available, otherwise a clean message."""
    exif = image.getexif()
    if not exif:
        print("  EXIF        : none")
        return

    print("  EXIF:")
    gps_raw = None
    for tag_id, value in exif.items():
        tag = ExifTags.TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            gps_raw = value
            continue
        # Bytes and long binary blobs are noise; trim them.
        if isinstance(value, bytes):
            value = value[:32].hex()
        text = str(value)
        if len(text) > 100:
            text = text[:100] + "..."
        print(f"    {tag:<24}: {text}")

    if gps_raw:
        gps = decode_gps(gps_raw)
        lat = gps_to_decimal(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
        lon = gps_to_decimal(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
        print("    GPS:")
        if lat is not None and lon is not None:
            print(f"      Coordinates         : {lat}, {lon}")
            print(f"      Google Maps         : https://maps.google.com/?q={lat},{lon}")
        for tag, value in gps.items():
            print(f"      {tag:<20}: {value}")


def process_file(path):
    """Analyze a single file. Returns True on success, False otherwise."""
    print(f"\n=== {path} ===")

    if not os.path.isfile(path):
        print("  [!] not a file or does not exist", file=sys.stderr)
        return False

    extension = os.path.splitext(path)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        print(
            f"  [!] unsupported extension '{extension}' "
            f"(allowed: {', '.join(ALLOWED_EXTENSIONS)})",
            file=sys.stderr,
        )
        return False

    try:
        with Image.open(path) as image:
            print_basic_attributes(path, image)
            # Extra container info (PNG text chunks, GIF frames, etc.)
            if image.info:
                interesting = {
                    key: value
                    for key, value in image.info.items()
                    if not isinstance(value, bytes)
                }
                if interesting:
                    print("  Info:")
                    for key, value in interesting.items():
                        text = str(value)
                        if len(text) > 100:
                            text = text[:100] + "..."
                        print(f"    {key:<24}: {text}")
            print_exif(image)
    except Exception as error:
        print(f"  [!] could not read image ({error})", file=sys.stderr)
        return False

    return True


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="scorpion",
        description="Display EXIF and basic metadata for image files.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="image file(s)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    failures = 0
    for path in args.files:
        if not process_file(path):
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
