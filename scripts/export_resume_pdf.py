#!/usr/bin/env python3
# Copyright (C) 2026 resume-skill contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Export a local HTML resume to PDF with a headless Chromium browser."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BROWSER_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    MAC_CHROME,
    "google-chrome",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
]


def find_browser(explicit: str | None) -> str | None:
    candidates = [explicit] if explicit else []
    candidates.extend(BROWSER_CANDIDATES)
    for candidate in candidates:
        if not candidate:
            continue
        candidate_path = Path(candidate)
        if candidate_path.exists():
            return str(candidate_path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def print_stream(value: str | bytes | None) -> None:
    if not value:
        return
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    value = value.strip()
    if value:
        print(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export an HTML resume to PDF.")
    parser.add_argument("html_file", help="Path to the HTML resume")
    parser.add_argument("pdf_file", help="Path for the exported PDF")
    parser.add_argument("--browser", help="Explicit Chrome/Chromium executable path")
    parser.add_argument("--timeout", type=int, default=45, help="Export timeout in seconds")
    args = parser.parse_args()

    html_path = Path(args.html_file).resolve()
    pdf_path = Path(args.pdf_file).resolve()
    if not html_path.exists():
        print(f"FAIL: HTML file not found: {html_path}")
        return 2

    browser = find_browser(args.browser)
    if not browser:
        print("FAIL: Chrome/Chromium browser not found. Set CHROME_PATH or pass --browser.")
        return 2

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()
    profile_override = os.environ.get("RESUME_PDF_CHROME_PROFILE")
    temp_profile = None
    if profile_override:
        user_data_dir = Path(profile_override).resolve()
        user_data_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_profile = tempfile.TemporaryDirectory(prefix="resume-pdf-chrome-")
        user_data_dir = Path(temp_profile.name)

    command = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-extensions",
        "--disable-sync",
        "--no-default-browser-check",
        "--no-first-run",
        "--run-all-compositor-stages-before-draw",
        f"--user-data-dir={user_data_dir}",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]

    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        print_stream(exc.stdout)
        print_stream(exc.stderr)
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            print(
                f"WARN: browser timed out after {args.timeout} seconds after writing the PDF."
            )
            print(f"OK: exported PDF to {pdf_path}")
            return 0
        print(f"FAIL: PDF export timed out after {args.timeout} seconds.")
        return 124
    finally:
        if temp_profile:
            temp_profile.cleanup()
    if completed.returncode != 0:
        print_stream(completed.stdout)
        print_stream(completed.stderr)
        print(f"FAIL: PDF export failed with exit code {completed.returncode}.")
        return completed.returncode
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        print("FAIL: browser exited successfully but PDF was not created.")
        return 1
    print(f"OK: exported PDF to {pdf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
