# Arachnida (Cybersecurity Piscine)

Summary: Introductory project to web scraping and metadata.

**Overview**
This project introduces two programs that work together to collect images from the web and analyze image metadata.

**Learning Goals**
- Practice web data processing by downloading images from websites.
- Parse and display metadata (including EXIF) from image files.
- Understand why metadata can reveal sensitive information.

**Project Requirements**
- You must create two programs: `spider` and `scorpion`.
- Programs can be scripts or binaries.
- If using a compiled language, include all source code and compile during evaluation.
- You may use libraries for HTTP requests and file handling, but the program logic must be yours.
- Using `wget` or `scrapy` is considered cheating and will receive a 0.

**Quick Start (Python)**
See `docs/python.md` for setup details.

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

Run spider:
```bash
python src/spider.py -r -l 2 -p ./data/ https://example.com
```

Run scorpion:
```bash
python src/scorpion.py ./data/image.jpg
```

**Program 1: spider**
The `spider` program extracts image files from a website, recursively, given a URL.

Usage:
```bash
./spider [-rlp] URL
```

Options:
- `-r` recursively downloads images from the URL.
- `-r -l N` sets maximum recursive depth (default: 5).
- `-p PATH` sets the output directory (default: `./data/`).

Default file extensions to download:
- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`

**Program 2: scorpion**
The `scorpion` program parses image files and prints EXIF and other metadata.

Usage:
```bash
./scorpion FILE1 [FILE2 ...]
```

Requirements:
- Must support the same file extensions as `spider`.
- Must display basic attributes such as creation date and EXIF data.
- Output format is up to you.

**Bonus (Optional)**
- Add an option to `scorpion` to modify or delete metadata in a given file.
- Provide a graphical interface for viewing and managing metadata.

Note: Bonus work is evaluated only if the mandatory part is perfect and fully functional.

**Submission**
- Turn in your work in your Git repository as usual.
- Only files inside the repository will be evaluated during defense.
- Double-check folder and file names.
