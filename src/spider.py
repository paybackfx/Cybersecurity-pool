#!/usr/bin/env python3
"""spider — recursively download images from a website.

Part of the Arachnida project (Cybersecurity Project).

Only the Python standard library is used: ``urllib`` for HTTP and
``html.parser`` for extracting links. The crawl logic (queue, visited
set, depth limit, same-host restriction) is implemented here by hand,
as required by the subject (no ``wget``, no ``scrapy``).

Usage:
    python spider.py [-r] [-l N] [-p PATH] URL
"""

import argparse
import os
import sys
from collections import deque
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
DEFAULT_DEPTH = 5
DEFAULT_PATH = "./data/"
TIMEOUT = 15  # seconds
USER_AGENT = "Mozilla/5.0 (Arachnida spider; +https://github.com/paybackfx)"


class LinkExtractor(HTMLParser):
    """Collect image sources and anchor links from an HTML document."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "img":
            for key in ("src", "data-src"):
                value = attributes.get(key)
                if value:
                    self.images.append(value)
        elif tag == "a":
            href = attributes.get("href")
            if href:
                self.links.append(href)
        elif tag == "source":  # <picture>/<source srcset="...">
            srcset = attributes.get("srcset")
            if srcset:
                # srcset = "a.jpg 1x, b.jpg 2x" -> keep the URLs only
                for part in srcset.split(","):
                    url = part.strip().split(" ")[0]
                    if url:
                        self.images.append(url)


def normalize_url(url):
    """Drop the fragment and normalize a URL for deduplication."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def has_allowed_extension(url):
    path = urlsplit(url).path.lower()
    return path.endswith(ALLOWED_EXTENSIONS)


def fetch(url):
    """Fetch a URL. Returns (content_type, data, final_url) or None on error."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            content_type = response.headers.get_content_type()
            data = response.read()
            return content_type, data, response.geturl()
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        print(f"[!] skip {url} ({error})", file=sys.stderr)
        return None
    except Exception as error:  # never crash on a single bad link
        print(f"[!] skip {url} (unexpected: {error})", file=sys.stderr)
        return None


def safe_filename(url, out_dir, used_names):
    """Build a collision-free, traversal-safe file name inside ``out_dir``."""
    path = urlsplit(url).path
    name = os.path.basename(path) or "image"
    # keep only the base name; strips any "../" and directory components
    name = name.replace("\\", "_").strip()
    if not name:
        name = "image"

    root, ext = os.path.splitext(name)
    candidate = name
    counter = 1
    while candidate.lower() in used_names or os.path.exists(
        os.path.join(out_dir, candidate)
    ):
        candidate = f"{root}_{counter}{ext}"
        counter += 1
    used_names.add(candidate.lower())
    return candidate


def download_image(url, out_dir, downloaded, used_names):
    """Download a single image URL into ``out_dir`` if not already fetched."""
    key = normalize_url(url)
    if key in downloaded:
        return False
    downloaded.add(key)

    result = fetch(url)
    if result is None:
        return False
    _content_type, data, _final = result

    filename = safe_filename(url, out_dir, used_names)
    destination = os.path.join(out_dir, filename)
    try:
        with open(destination, "wb") as handle:
            handle.write(data)
    except OSError as error:
        print(f"[!] could not write {destination} ({error})", file=sys.stderr)
        return False
    print(f"[+] {filename}  <-  {url}")
    return True


def crawl(start_url, recursive, max_depth, out_dir):
    """Breadth-first crawl restricted to the start URL's host."""
    start_host = urlsplit(start_url).netloc
    queue = deque([(normalize_url(start_url), 0)])
    visited_pages = set()
    downloaded = set()
    used_names = set()
    count = 0

    while queue:
        url, depth = queue.popleft()
        if url in visited_pages:
            continue
        visited_pages.add(url)

        result = fetch(url)
        if result is None:
            continue
        content_type, data, final_url = result

        # The page itself might be a direct image link.
        if content_type.startswith("image/") and has_allowed_extension(final_url):
            if download_image(final_url, out_dir, downloaded, used_names):
                count += 1
            continue

        if content_type != "text/html":
            continue

        parser = LinkExtractor()
        try:
            parser.feed(data.decode("utf-8", errors="replace"))
        except Exception as error:
            print(f"[!] parse error on {url} ({error})", file=sys.stderr)
            continue

        for src in parser.images:
            image_url = normalize_url(urljoin(final_url, src))
            if has_allowed_extension(image_url):
                if download_image(image_url, out_dir, downloaded, used_names):
                    count += 1

        if recursive and depth < max_depth:
            for href in parser.links:
                link = normalize_url(urljoin(final_url, href))
                parts = urlsplit(link)
                if parts.scheme not in ("http", "https"):
                    continue
                if parts.netloc != start_host:  # stay on the same host
                    continue
                if link not in visited_pages:
                    queue.append((link, depth + 1))

    return count


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="spider",
        description="Recursively download images from a website.",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        help="recursively download images from the URL",
    )
    parser.add_argument(
        "-l",
        type=int,
        default=DEFAULT_DEPTH,
        metavar="N",
        help=f"maximum recursion depth (default: {DEFAULT_DEPTH}, needs -r)",
    )
    parser.add_argument(
        "-p",
        default=DEFAULT_PATH,
        metavar="PATH",
        help=f"output directory (default: {DEFAULT_PATH})",
    )
    parser.add_argument("url", help="target URL")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.l < 0:
        print("[!] depth (-l) must be >= 0", file=sys.stderr)
        return 1

    scheme = urlsplit(args.url).scheme
    if scheme not in ("http", "https"):
        print("[!] URL must start with http:// or https://", file=sys.stderr)
        return 1

    try:
        os.makedirs(args.p, exist_ok=True)
    except OSError as error:
        print(f"[!] cannot create output directory {args.p} ({error})", file=sys.stderr)
        return 1

    max_depth = args.l if args.r else 0
    print(
        f"[*] crawling {args.url} "
        f"(recursive={args.r}, depth={max_depth}, out={args.p})"
    )
    total = crawl(args.url, args.r, max_depth, args.p)
    print(f"[*] done: {total} image(s) downloaded into {args.p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
