# Arachnida — Documentation & Guide

> An educational walkthrough of the **Arachnida** project (a cybersecurity exercise):
> two small Python tools — **spider** (a recursive image scraper) and **scorpion**
> (an image metadata / EXIF parser) — built with the standard library only, no `wget`,
> no `scrapy`. This guide explains *what* the tools do, *how* they work, and *why*
> image metadata matters for security.

---

## Table of contents

1. [What is Arachnida?](#1-what-is-arachnida)
2. [Why this project matters](#2-why-this-project-matters)
3. [Install & quick start](#3-install--quick-start)
4. [spider — how it works](#4-spider--how-it-works)
5. [scorpion — how it works](#5-scorpion--how-it-works)
6. [End-to-end example](#6-end-to-end-example)
7. [The security lesson: metadata leaks](#7-the-security-lesson-metadata-leaks)
8. [Documentation map](#8-documentation-map)
9. [Rules & constraints (subject)](#9-rules--constraints-subject)

---

## 1. What is Arachnida?

Arachnida is an introduction to **web scraping** and **file metadata**. It is made of two
independent command-line programs that are meant to be used together:

| Program | Role | Analogy |
|---------|------|---------|
| **spider** | Crawls a website and downloads every image it finds | The spider that walks the web and collects prey |
| **scorpion** | Reads the collected images and exposes their hidden metadata | The scorpion that dissects the prey |

Both live in [`src/`](../src/):
- [`src/spider.py`](../src/spider.py)
- [`src/scorpion.py`](../src/scorpion.py)

---

## 2. Why this project matters

You learn three concrete things:

1. **How the web is crawled** — HTTP requests, HTML parsing, link resolution, and how to
   recurse through pages *without* looping forever.
2. **What metadata is** — the invisible information (camera model, timestamps, GPS
   coordinates…) that image files carry around by default.
3. **Why it's a privacy/security risk** — a single photo posted online can leak where and
   when it was taken. Understanding this is the first step to defending against it.

---

## 3. Install & quick start

You only need **Python 3** and **Pillow** (used by scorpion to read EXIF).

```bash
# from the project root
python -m pip install -r requirements.txt   # installs Pillow
```

Or via the Makefile shortcuts:

```bash
make setup      # install dependencies
make spider     # run a sample crawl
make scorpion   # run scorpion on a sample image
```

More setup details: [`python.md`](python.md).

---

## 4. spider — how it works

`spider` downloads images from a URL and, optionally, follows links to crawl deeper.

### Usage

```bash
python src/spider.py [-r] [-l N] [-p PATH] URL
```

| Option | Meaning | Default |
|--------|---------|---------|
| `-r` | Recursively follow links and download images | off |
| `-l N` | Maximum recursion depth (only meaningful with `-r`) | `5` |
| `-p PATH` | Output directory for downloaded images | `./data/` |
| `URL` | The page to start from (required) | — |

Downloaded extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`.

### The crawl logic (built by hand)

Because `wget`/`scrapy` are forbidden, the crawl is implemented from scratch using only
`urllib` (HTTP) and `html.parser` (link extraction):

1. **Queue** — start with the given URL at depth 0 (a breadth-first `deque`).
2. **Fetch** — download the page's HTML.
3. **Extract** — pull `<img src=…>` (images to save) and `<a href=…>` (links to follow).
4. **Resolve** — turn relative URLs into absolute ones (`urljoin`).
5. **Filter** — keep only allowed image extensions; only follow links on the **same host**.
6. **Deduplicate** — a *visited set* prevents re-fetching the same page and infinite loops.
7. **Respect depth** — stop recursing once depth reaches `-l N`.
8. **Download** — save images as raw **bytes** into the output directory.

```
URL ──▶ fetch HTML ──▶ find <img> ──▶ download images
             │
             └──▶ find <a> ──▶ (same host? not visited? depth<limit?) ──▶ enqueue
```

---

## 5. scorpion — how it works

`scorpion` opens one or more image files and prints their attributes and EXIF metadata.

### Usage

```bash
python src/scorpion.py FILE1 [FILE2 ...]
```

For each file it prints:

- **Basic attributes** — format, dimensions, size on disk, creation/modification date.
- **EXIF metadata** — camera make/model, orientation, timestamps, and **GPS position**
  (decoded into readable latitude/longitude when present).

If a file has **no EXIF data**, scorpion says so cleanly instead of crashing — handling
missing metadata gracefully is part of the requirement.

---

## 6. End-to-end example

```bash
# 1. Crawl a site 2 levels deep, saving images into ./data/
python src/spider.py -r -l 2 -p ./data/ https://example.com

# 2. Inspect the metadata of one downloaded image
python src/scorpion.py ./data/image.jpg
```

---

## 7. The security lesson: metadata leaks

A photo is not "just pixels." Cameras and phones embed **EXIF** tags such as:

- the exact **date and time** the picture was taken,
- the **device** (make, model, sometimes serial number),
- and often the **GPS coordinates** of where you were standing.

Post that photo publicly and anyone running a tool like `scorpion` can read all of it.
That is why platforms strip metadata on upload — and why, defensively, you should too.
(The optional **bonus** of the project is to add metadata *editing/deletion* to scorpion.)

---

## 8. Documentation map

| File | What's inside |
|------|---------------|
| [`README.md`](README.md) | This guide (overview + how it works) |
| [`python.md`](python.md) | Minimal Python setup and run commands |
| [`steps.md`](steps.md) | Suggested implementation steps and milestones |
| [`resources.md`](resources.md) | Concepts to review and non-library guidance |
| [`checklist.md`](checklist.md) | Verification checklist before submission |

See also the top-level [`ReadME.md`](../ReadME.md) for the raw subject summary.

---

## 9. Rules & constraints (subject)

- ✅ Libraries are allowed **only** for HTTP requests and file handling — the crawl/parse
  **logic must be yours**.
- ❌ Using `wget` or `scrapy` is considered cheating (grade: 0).
- ✅ Both programs must support the same image extensions.
- ✅ `scorpion` must handle files **without** EXIF data without crashing.
- ℹ️ Bonus work is evaluated only if the mandatory part is perfect and fully functional.
