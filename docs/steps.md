# Steps

This is a pragmatic path to complete the project. Adapt to your language/tooling.

1. Read the subject carefully
- Extract the exact requirements for `spider` and `scorpion`.
- Note disallowed tools (`wget`, `scrapy`) and allowed libraries (HTTP + file handling only).

2. Choose your stack and project layout
- Decide language and create `spider` and `scorpion` entry points.
- Agree on a simple folder layout: `src/`, `bin/`, `data/`, `docs/`.

3. Implement `spider` core
- Parse CLI args: `-r`, `-l N`, `-p PATH`, URL.
- Fetch HTML for the URL.
- Parse links to images (start with `img` tags and `src` attributes).
- Resolve relative URLs.
- Filter by allowed extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`.
- Download files to output directory.

4. Add recursion to `spider`
- If `-r`, parse anchor links on the page.
- Track visited URLs to avoid loops.
- Respect depth limit (`-l N`, default 5).
- Only recurse within the same host unless you decide otherwise.

5. Implement `scorpion`
- Parse CLI args: `FILE1 [FILE2 ...]`.
- For each file, read metadata.
- Print creation date and EXIF fields (camera, dimensions, GPS if present).
- Keep output format consistent across files.

6. Validate behavior
- Test with a few small sites you control or public sample pages.
- Confirm `spider` does not use disallowed tools and handles errors gracefully.
- Confirm `scorpion` handles files without EXIF data.

7. Package for evaluation
- Provide clear `usage` examples in `ReadME.md`.
- If compiled language, include build instructions and source.
- Confirm output paths and file names match expectations.
