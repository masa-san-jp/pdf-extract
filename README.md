# pdf-extract

**A small command-line tool that extracts plain text from PDF files.**
The extracted text can be used for summarizing, searching, copy-pasting, or saving to another file.

It works with both:

- 📄 PDFs on your computer (local files)
- ☁️ PDFs stored in Google Drive

> 日本語の説明は [README.ja.md](README.ja.md) にあります。

---

## What it can and can't do

| Situation | Supported? |
|---|---|
| Extract text from a PDF exported from Word / Google Docs | ✅ Yes |
| Extract text from a downloaded report / paper / invoice PDF | ✅ Yes |
| Read a PDF in Google Drive directly (without downloading it first) | ✅ Yes (one-time auth required) |
| Extract text from a **scanned** PDF (image-only, no text layer) | ❌ No (OCR needed — out of scope) |

This tool works with PDFs that contain a real text layer. Scanned or photographed
PDFs have no text data, so nothing can be extracted from them here.

---

## Requirements

- Python 3.8+
- For Google Drive PDFs: a Google account and the `gcloud` CLI ([install guide](https://cloud.google.com/sdk/docs/install))

---

## Setup (first time only)

```bash
bash setup.sh
```

This installs the Python dependencies (`pypdf` and the Google API client).

- For **local PDFs only**, that's all you need.
- For **Google Drive PDFs**, you also need to authenticate once — see
  "Reading PDFs from Google Drive" below.

---

## Usage — local PDF

```bash
./pdf_extract.py /path/to/file.pdf
```

> On macOS, you can drag a PDF from Finder into the terminal to fill in its full path.

If `./pdf_extract.py` doesn't run, call it through Python directly:

```bash
python3 pdf_extract.py /path/to/file.pdf
```

### What you get

```
<!-- pdf-extract source -->
<!-- source: /path/to/file.pdf -->
<!-- name: file.pdf -->
<!-- mime: application/pdf -->
<!-- pages: 3/3 -->

(the extracted text appears here)
```

The leading `<!-- ... -->` block is a small metadata header (which file, how many
pages). `pages: 3/3` means "3 of 3 pages were extracted". Use `--no-header` to omit it.

---

## Options

Options go **after** the input. They can be combined.

| Goal | Flag | Example |
|---|---|---|
| Save the result to a file | `-o out.txt` | `./pdf_extract.py file.pdf -o out.txt` |
| Extract only some pages | `--pages 1-5,8` | `./pdf_extract.py file.pdf --pages 1-5,8` |
| Insert page separators | `--page-markers` | `./pdf_extract.py file.pdf --page-markers` |
| Omit the metadata header | `--no-header` | `./pdf_extract.py file.pdf --no-header` |
| Force local-file input | `--local` | `./pdf_extract.py input --local` |
| Force Drive input | `--drive` | `./pdf_extract.py input --drive` |

- **`--pages 1-5,8`** — extracts pages 1–5 and page 8 (page numbers are 1-based).
- **`--page-markers`** — inserts `--- page N ---` between pages so you can tell which
  page text came from.

Full example:

```bash
./pdf_extract.py report.pdf --pages 1-10 --page-markers -o excerpt.txt
```

---

## Reading PDFs from Google Drive

### 1. Authenticate (first time only)

```bash
bash auth.sh
# or for a specific account:
bash auth.sh you@example.com
```

A browser opens; sign in with your Google account. This grants **read-only**
access to Drive (`drive.readonly`) — the tool never modifies or deletes anything.

### 2. Pass the Drive link or file ID

```bash
./pdf_extract.py "https://drive.google.com/file/d/1AbC.../view"
```

> Wrap the URL in double quotes `"..."` so special characters don't break the command.

To get the link: right-click the PDF in Google Drive → **Copy link** (or **Share →
Copy link**). The long string between `/d/` and `/view` is the file ID; passing just
the ID works too.

---

## Troubleshooting (by exit code)

The tool prints an exit code when it finishes. Match it against this table:

| Code | Meaning | What to do |
|---|---|---|
| 0 | Success | Nothing — it worked |
| 1 | Runtime / API error | The PDF may be corrupt, or the network failed. Reopen the file / retry |
| 2 | Bad input | Wrong path, or file not found. Re-enter the path |
| 3 | Missing dependency or not authenticated | Local PDF → run `bash setup.sh`; Drive PDF → run `bash auth.sh` |
| 4 | Not a PDF | The Drive file is a native Google Doc/Sheet/Slide — export it to PDF first |

### FAQ

**Japanese (or other non-Latin) text comes out garbled**
This happens when a PDF lacks the mapping information (a *ToUnicode* map) needed to
recover characters. PDFs produced by Word, Google Docs, or Acrobat are almost always
fine. A different extraction engine can be added if you hit a PDF that garbles.

**No text comes out / the result is empty**
The PDF is probably scanned (image-only) with no text data. Extracting text from it
requires OCR, which this tool does not do.

**`command not found`**
The file may not be executable. Run it through Python instead:
`python3 pdf_extract.py file.pdf`

---

## How input is detected

| Input | Treated as |
|---|---|
| An existing path (e.g. `/Users/you/...`) | Local PDF |
| A `https://.../d/<ID>/...` URL | Drive PDF |
| A long ID-like string with no matching local file | Drive PDF |

If detection guesses wrong, force it with `--local` or `--drive`.

---

## License

MIT — see [LICENSE](LICENSE).
