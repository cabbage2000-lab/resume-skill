#!/usr/bin/env python3
# Copyright (C) 2026 resume-skill contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Validate an HTML resume for HR/GEO/mobile/PDF readiness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


SECTION_PATTERNS = [
    r"个人优势|职业概况|个人简介|summary|profile",
    r"工作经历|实习经历|experience|employment",
    r"项目经历|projects?",
    r"教育背景|education",
    r"技能|skills?",
    r"证书|荣誉|awards?|certifications?",
]

PLACEHOLDER_PATTERNS = [
    r"张同学",
    r"138-0000-0000",
    r"name@example\.com",
    r"portfolio\.example\.com",
    r"某互联网公司",
    r"华东示例大学",
    r"TODO|\[TODO\]|待补充|占位",
]

WEAK_CLAIM_PATTERNS = [
    r"熟悉",
    r"了解",
    r"参与",
    r"负责",
    r"协助",
    r"良好",
    r"优秀",
    r"认真",
    r"踏实",
    r"hardworking",
    r"responsible for",
    r"participated in",
    r"familiar with",
]

IMPACT_PATTERNS = [
    r"\d+",
    r"提升|降低|减少|增长|覆盖|转化|留存|节省|缩短|完成|交付|上线|沉淀",
    r"increased|reduced|improved|launched|delivered|saved|covered|converted",
]

HIDDEN_CSS_PATTERNS = [
    r"display\s*:\s*none",
    r"visibility\s*:\s*hidden",
]

CSS_RULE_PATTERN = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
PSEUDO_ELEMENT_SELECTOR_PATTERN = re.compile(r":{1,2}(?:before|after)\b", re.I)


class ResumeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: set[str] = set()
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.jsonld_blocks: list[str] = []
        self.style_blocks: list[str] = []
        self.inline_styles: list[str] = []
        self.text_parts: list[str] = []
        self.list_items: list[str] = []
        self.headings: list[str] = []
        self._current_tag: str | None = None
        self._current_script_type: str = ""
        self._buffer: list[str] = []
        self._capture_stack: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        self.tags.add(tag)
        if attr_map.get("style"):
            self.inline_styles.append(attr_map["style"])
        if tag == "meta":
            self.meta.append(attr_map)
        elif tag == "a":
            self.links.append(attr_map)
        elif tag in {"script", "style"}:
            self._current_tag = tag
            self._current_script_type = attr_map.get("type", "").lower()
            self._buffer = []
        elif tag in {"li", "h1", "h2", "h3"}:
            self._capture_stack.append((tag, []))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == self._current_tag:
            data = "".join(self._buffer)
            if tag == "script" and self._current_script_type == "application/ld+json":
                self.jsonld_blocks.append(data)
            elif tag == "style":
                self.style_blocks.append(data)
            self._current_tag = None
            self._current_script_type = ""
            self._buffer = []
        for index in range(len(self._capture_stack) - 1, -1, -1):
            capture_tag, capture_buffer = self._capture_stack[index]
            if tag == capture_tag:
                del self._capture_stack[index]
                data = compact_text("".join(capture_buffer))
                if data:
                    if tag == "li":
                        self.list_items.append(data)
                    else:
                        self.headings.append(data)
                break

    def handle_data(self, data: str) -> None:
        if self._current_tag in {"script", "style"}:
            self._buffer.append(data)
        elif self._capture_stack:
            for _, capture_buffer in self._capture_stack:
                capture_buffer.append(data)
            if data.strip():
                self.text_parts.append(data)
        elif data.strip():
            self.text_parts.append(data)


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def has_meta(parser: ResumeParser, *, name: str | None = None, attr: str | None = None) -> bool:
    for meta in parser.meta:
        if name and meta.get("name", "").lower() == name.lower():
            return True
        if attr and attr in meta:
            return True
    return False


def has_person_jsonld(parser: ResumeParser) -> bool:
    for block in parser.jsonld_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "Person":
                return True
    return False


def has_hidden_css_declaration(style: str) -> bool:
    return any(re.search(pattern, style, re.I) for pattern in HIDDEN_CSS_PATTERNS)


def selector_targets_only_pseudo_elements(selector: str) -> bool:
    selectors = [part.strip() for part in selector.split(",") if part.strip()]
    return bool(selectors) and all(
        PSEUDO_ELEMENT_SELECTOR_PATTERN.search(part) for part in selectors
    )


def has_hidden_text_css(css: str, inline_styles: list[str]) -> bool:
    if any(has_hidden_css_declaration(style) for style in inline_styles):
        return True
    for match in CSS_RULE_PATTERN.finditer(css):
        selector, declaration_block = match.groups()
        if not has_hidden_css_declaration(declaration_block):
            continue
        if not selector_targets_only_pseudo_elements(selector):
            return True
    return False


def content_quality_warnings(parser: ResumeParser, visible_text: str) -> list[str]:
    warnings: list[str] = []
    weak_items = [
        item for item in parser.list_items
        if any(re.search(pattern, item, re.I) for pattern in WEAK_CLAIM_PATTERNS)
    ]
    if weak_items:
        warnings.append(
            f"{len(weak_items)} bullet(s) contain weak claim wording; replace duties or self-evaluation with evidence."
        )

    long_items = [item for item in parser.list_items if len(item) > 120]
    if long_items:
        warnings.append(
            f"{len(long_items)} bullet(s) exceed 120 characters; shorten for HR scan speed and PDF fit."
        )

    evidence_items = [
        item for item in parser.list_items
        if any(re.search(pattern, item, re.I) for pattern in IMPACT_PATTERNS)
    ]
    if parser.list_items and len(evidence_items) < max(2, len(parser.list_items) // 4):
        warnings.append(
            "Too few bullets include measurable scale, output, or impact; add truthful metrics or proxy facts."
        )

    template_title_patterns = [
        r"简历模板",
        r"resume template",
        r"应届毕业生简历模板",
    ]
    if any(re.search(pattern, visible_text, re.I) for pattern in template_title_patterns):
        warnings.append(
            "Template-like title text remains visible; replace it with the candidate name and target role."
        )
    return warnings


def validate(path: Path, allow_placeholders: bool) -> tuple[list[str], list[str]]:
    html = path.read_text(encoding="utf-8")
    parser = ResumeParser()
    parser.feed(html)

    failures: list[str] = []
    warnings: list[str] = []
    visible_text = compact_text(" ".join(parser.text_parts))
    lowered = html.lower()
    css = "\n".join(parser.style_blocks).lower()

    if "<!doctype html" not in lowered:
        failures.append("Missing <!doctype html>.")
    if "html" not in parser.tags or "main" not in parser.tags:
        failures.append("Use semantic HTML with at least <html> and <main>.")
    if not has_meta(parser, name="viewport"):
        failures.append("Missing mobile viewport meta tag.")
    if not has_meta(parser, name="description"):
        failures.append("Missing meta description for GEO screening.")
    if "<title" not in lowered:
        failures.append("Missing document title.")
    if "@media print" not in css or "@page" not in css:
        failures.append("Missing print CSS with @media print and @page.")
    if "@media" not in css or "max-width" not in css:
        failures.append("Missing responsive CSS media query.")
    if not has_person_jsonld(parser):
        failures.append("Missing schema.org Person JSON-LD.")

    if len(visible_text) < 700:
        failures.append("Visible resume text is too short; ensure content is not image-only.")

    section_hits = sum(1 for pattern in SECTION_PATTERNS if re.search(pattern, visible_text, re.I))
    if section_hits < 4:
        failures.append("Too few recognizable resume sections.")

    if not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", visible_text):
        warnings.append("No email address detected in visible text.")
    if not re.search(r"(\+?\d[\d\s().-]{7,}\d)", visible_text):
        warnings.append("No phone number detected in visible text.")

    placeholder_hits = []
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, html, re.I):
            placeholder_hits.append(pattern)
    if placeholder_hits and not allow_placeholders:
        failures.append("Placeholder/sample content remains: " + ", ".join(placeholder_hits))

    if has_hidden_text_css(css, parser.inline_styles):
        warnings.append("Hidden text detected; avoid hidden keyword blocks for GEO/ATS.")
    if "<img" in lowered and len(visible_text) < 1500:
        warnings.append("Images are present; ensure the resume is not relying on image-only content.")

    warnings.extend(content_quality_warnings(parser, visible_text))

    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check an HTML resume for baseline quality gates.")
    parser.add_argument("html_file", help="Path to the generated HTML resume")
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Allow sample placeholders when checking bundled templates",
    )
    args = parser.parse_args()

    path = Path(args.html_file)
    if not path.exists():
        print(f"FAIL: file not found: {path}")
        return 2
    if not path.is_file():
        print(f"FAIL: not a file: {path}")
        return 2

    failures, warnings = validate(path, args.allow_placeholders)
    for warning in warnings:
        print(f"WARN: {warning}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("OK: resume HTML passed quality gates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
