# Checklist

Before submission:
- `spider` supports `-r`, `-l N`, `-p PATH`, and a URL
- Default depth is 5 when `-l` is omitted
- Default output directory is `./data/`
- Allowed extensions are enforced
- Recursive crawl does not loop forever
- `scorpion` supports multiple files
- `scorpion` prints creation date and EXIF if present
- Missing EXIF is handled cleanly
- No `wget` or `scrapy` usage
- README includes usage examples
