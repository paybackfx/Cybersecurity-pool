# Resources

Concepts to review:
- HTTP GET requests and handling redirects
- HTML parsing and link resolution (absolute vs relative URLs)
- URL normalization and deduplication
- File I/O and safe path handling
- EXIF metadata basics and common fields

Non-library guidance (avoid disallowed tools):
- Build your own recursion and crawl queue
- Maintain a visited set to prevent re-fetching
- Respect a depth limit even if pages link in cycles

Testing tips:
- Create a tiny local HTML page with a few images and links
- Host it locally (or use `file://` if your parser supports it)
- Validate output directory creation and file naming

Security and correctness notes:
- Do not allow directory traversal in download paths
- Handle broken links without crashing
- Make sure binary files are downloaded as bytes
