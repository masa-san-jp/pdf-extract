#!/usr/bin/env python3
"""Extract plain text from PDF files (local path or Google Drive).

- Local PDF       → read bytes from disk and extract text with pypdf
- Drive PDF       → download via Drive API (get_media) then extract

Native Google Workspace files (Docs / Sheets / Slides) are NOT handled here.
This tool only deals with `application/pdf` content.

Note: text-based (digital) PDFs only. Scanned / image-only PDFs have no text
layer and will produce empty output — OCR is out of scope.

Authentication (Drive only) uses Application Default Credentials (ADC).

Usage:
    pdf_extract.py <path-or-drive-id-or-url>
    pdf_extract.py <input> -o output.txt
    pdf_extract.py <input> --pages 1-5,8     # subset of pages (1-based)
    pdf_extract.py <input> --no-header        # omit metadata header
    pdf_extract.py <input> --page-markers     # insert "--- page N ---" between pages
    pdf_extract.py <input> --local            # force local-file interpretation
    pdf_extract.py <input> --drive            # force Drive interpretation

Auth (one time, for Drive inputs):
    bash ./auth.sh
    # or for a specific account
    bash ./auth.sh <email>

Exit codes:
    0  success
    1  runtime / API failure
    2  invalid arguments
    3  missing dependency or credentials
    4  unsupported input (Drive file is not a PDF)
"""
from __future__ import annotations

import argparse
import io
import os
import pathlib
import re
import sys

PDF_MIME = "application/pdf"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

DRIVE_URL_RE = re.compile(r"/d/([a-zA-Z0-9_-]+)")
# A bare Drive file id: long-ish, only id-safe chars, no path separator / dot.
DRIVE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{20,}$")


# --------------------------------------------------------------------------- #
# Dependencies
# --------------------------------------------------------------------------- #
def _import_pypdf():
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.stderr.write("ERROR: missing dependency: pypdf\n")
        sys.stderr.write("Run: bash ./setup.sh\n")
        sys.exit(3)
    return PdfReader


def _import_google():
    try:
        from google.auth import default as google_auth_default
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
    except ImportError as exc:
        sys.stderr.write(f"ERROR: missing dependency: {exc.name}\n")
        sys.stderr.write("Run: bash ./setup.sh\n")
        sys.exit(3)
    return google_auth_default, Request, build, MediaIoBaseDownload


# --------------------------------------------------------------------------- #
# Input routing
# --------------------------------------------------------------------------- #
def looks_like_drive(s: str) -> bool:
    if DRIVE_URL_RE.search(s):
        return True
    if DRIVE_ID_RE.match(s) and not os.path.exists(s):
        return True
    return False


def extract_file_id(s: str) -> str:
    m = DRIVE_URL_RE.search(s)
    return m.group(1) if m else s.strip()


# --------------------------------------------------------------------------- #
# Drive download
# --------------------------------------------------------------------------- #
def get_credentials():
    google_auth_default, Request, _build, _dl = _import_google()
    try:
        creds, _proj = google_auth_default(scopes=SCOPES)
    except Exception as exc:
        sys.stderr.write(f"ERROR: failed to load credentials: {exc}\n")
        sys.stderr.write("Run: bash ./auth.sh\n")
        sys.exit(3)
    if not creds.valid:
        creds.refresh(Request())
    return creds


def drive_metadata(creds, file_id: str) -> dict:
    _, _, build, _ = _import_google()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return (
        service.files()
        .get(
            fileId=file_id,
            fields="id,name,mimeType,modifiedTime,size,owners(emailAddress)",
            supportsAllDrives=True,
        )
        .execute()
    )


def drive_download(creds, file_id: str) -> bytes:
    _, _, build, MediaIoBaseDownload = _import_google()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _status, done = downloader.next_chunk()
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# PDF extraction
# --------------------------------------------------------------------------- #
def parse_pages(spec: str, total: int) -> list[int]:
    """Parse "1-5,8,10-12" into a sorted list of 0-based page indices."""
    wanted: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            start, end = int(a), int(b)
        else:
            start = end = int(chunk)
        for n in range(start, end + 1):
            if 1 <= n <= total:
                wanted.add(n - 1)
    return sorted(wanted)


def extract_text(data: bytes, pages: str | None, page_markers: bool) -> tuple[str, int, int]:
    """Return (text, n_pages_emitted, n_pages_total)."""
    PdfReader = _import_pypdf()
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:
        sys.stderr.write(f"ERROR: failed to parse PDF: {exc}\n")
        sys.exit(1)

    if reader.is_encrypted:
        try:
            reader.decrypt("")  # try empty password
        except Exception:
            pass

    total = len(reader.pages)
    indices = parse_pages(pages, total) if pages else list(range(total))

    parts: list[str] = []
    for idx in indices:
        try:
            txt = reader.pages[idx].extract_text() or ""
        except Exception as exc:
            txt = f"[page {idx + 1}: extraction failed: {exc}]"
        if page_markers:
            parts.append(f"--- page {idx + 1} ---\n{txt}")
        else:
            parts.append(txt)
    return "\n\n".join(parts).strip() + "\n", len(indices), total


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
def build_header(source: str, name: str, mime: str, extra: dict) -> str:
    lines = [
        "<!-- pdf-extract source -->",
        f"<!-- source: {source} -->",
        f"<!-- name: {name} -->",
        f"<!-- mime: {mime} -->",
    ]
    for k, v in extra.items():
        if v:
            lines.append(f"<!-- {k}: {v} -->")
    return "\n".join(lines) + "\n\n"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract text from a PDF (local path or Google Drive)."
    )
    ap.add_argument("input", help="local PDF path, or Drive file id / share URL")
    ap.add_argument("-o", "--output", help="write text to this file instead of stdout")
    ap.add_argument("--pages", help='page subset, 1-based, e.g. "1-5,8"')
    ap.add_argument("--no-header", action="store_true", help="omit metadata header")
    ap.add_argument(
        "--page-markers", action="store_true", help='insert "--- page N ---" markers'
    )
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--local", action="store_true", help="force local-file input")
    src.add_argument("--drive", action="store_true", help="force Drive input")
    args = ap.parse_args()

    is_drive = args.drive or (not args.local and looks_like_drive(args.input))

    if is_drive:
        creds = get_credentials()
        file_id = extract_file_id(args.input)
        try:
            meta = drive_metadata(creds, file_id)
        except Exception as exc:
            sys.stderr.write(f"ERROR: Drive metadata failed: {exc}\n")
            return 1
        mime = meta.get("mimeType", "")
        if mime != PDF_MIME:
            sys.stderr.write(
                f"ERROR: Drive file is not a PDF (mimeType={mime}).\n"
            )
            if mime.startswith("application/vnd.google-apps."):
                sys.stderr.write(
                    "This is a native Google Workspace file (Docs / Sheets / Slides),\n"
                    "not a PDF. Export it to PDF first, or use a Google Workspace\n"
                    "export tool.\n"
                )
            return 4
        try:
            data = drive_download(creds, file_id)
        except Exception as exc:
            sys.stderr.write(f"ERROR: Drive download failed: {exc}\n")
            return 1
        source = f"drive:{file_id}"
        name = meta.get("name", file_id)
        extra = {
            "modified": meta.get("modifiedTime"),
            "owner": (meta.get("owners") or [{}])[0].get("emailAddress"),
        }
    else:
        path = pathlib.Path(args.input).expanduser()
        if not path.is_file():
            sys.stderr.write(f"ERROR: file not found: {path}\n")
            return 2
        data = path.read_bytes()
        source = str(path)
        name = path.name
        extra = {}

    text, emitted, total = extract_text(data, args.pages, args.page_markers)

    out = ""
    if not args.no_header:
        extra["pages"] = f"{emitted}/{total}"
        out += build_header(source, name, PDF_MIME, extra)
    out += text

    if args.output:
        pathlib.Path(args.output).expanduser().write_text(out, encoding="utf-8")
        sys.stderr.write(f"==> wrote {args.output} ({emitted}/{total} pages)\n")
    else:
        sys.stdout.write(out)

    if text.strip() == "" or (not args.no_header and text.strip() == ""):
        sys.stderr.write(
            "WARNING: no text extracted. The PDF may be scanned/image-only "
            "(no text layer); OCR is required and not supported here.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
