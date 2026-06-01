# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo is **a skill package**, not an application. It is a portable instruction bundle that an AI coding assistant (Claude Code, Codex, or compatible runtimes) loads to rewrite/create HR-readable, GEO/ATS-friendly resumes (primary output language: Chinese) and to generate responsive HTML/PDF resumes.

The "product" that ships is the set of instructions + supporting assets, not a runnable service. Most editing work here is editing *instructions for an AI*, with a small amount of supporting Python (validator + PDF exporter).

## Commands

Run from the repo root (the test imports `from scripts.check_resume_html import validate`, which requires repo root on `sys.path`):

```bash
# Run tests (discovery from repo root is itself asserted by a test)
python3 -m unittest                 # or: python3 -m unittest tests/test_check_resume_html.py

# Validate the bundled template (placeholders allowed only for templates)
python3 scripts/check_resume_html.py assets/resume-template.html --allow-placeholders

# Validate a real user resume (placeholders are a hard failure)
python3 scripts/check_resume_html.py path/to/resume.html

# Export a resume to PDF (needs Chrome/Chromium; set CHROME_PATH if not auto-found)
python3 scripts/export_resume_pdf.py path/to/resume.html path/to/resume.pdf
```

No build step, no package manager, no third-party deps — stdlib Python 3 + system Chrome only.

## Architecture and the rules that connect files

**`SKILL.md` is the runtime contract** — the file the AI actually reads to do its job. Its "Required Workflow", "HR Writing Rules", and "HTML Artifact Rules" are the authoritative behavior spec. `references/*.md` are lazily loaded per the workflow (HR critique → `hr-resume-review.md`; named role/JD → `role-playbooks.md`; ATS/GEO/HTML → `geo-html-resume.md`).

**The validator encodes the same rules as the prose, in code.** `scripts/check_resume_html.py` is a single-file `HTMLParser`-based checker whose pattern lists (`SECTION_PATTERNS`, `WEAK_CLAIM_PATTERNS`, `IMPACT_PATTERNS`, `PLACEHOLDER_PATTERNS`, hidden-CSS detection) are the machine-enforced version of SKILL.md's HR/HTML rules. **When you change an HR or HTML rule, update all three layers that express it: `SKILL.md`, the relevant `references/*.md`, and the validator patterns** — otherwise prose and gate drift apart.

`validate()` returns `(failures, warnings)`:
- **failures** = hard gates that block delivery (doctype, semantic `html`+`main`, viewport, meta description, `<title>`, print CSS `@media print`+`@page`, responsive `@media`+`max-width`, `Person` JSON-LD, ≥700 chars visible text, ≥4 recognizable sections, placeholders unless `--allow-placeholders`).
- **warnings** = soft signals (missing email/phone, weak-claim bullets, bullets >120 chars, low evidence density, template-like visible title, hidden text).
- Exit codes: `0` pass, `1` failures present, `2` file/arg error.

One subtle behavior worth preserving: hidden-CSS detection (`display:none` / `visibility:hidden`) is **allowed** when the selector targets only `::before`/`::after` (decorative), but still flagged when a real selector is grouped with a pseudo-element. The test suite locks this in.

**`export_resume_pdf.py`** drives headless Chrome via `--print-to-pdf`. Browser lookup order: `CHROME_PATH` → macOS Chrome path → `google-chrome`/`chromium`/etc. It uses a throwaway profile (override with `RESUME_PDF_CHROME_PROFILE`) and treats "timed out but PDF was written" as success.

## Things that bite

- **Template is duplicated.** `assets/resume-template.html` (the one SKILL.md tells the AI to use) and root `resume-template.html` (local-preview convenience) are byte-identical copies. Edit both, or they drift.
- **Dual-runtime portability is a constraint, not a preference.** SKILL.md must use only relative paths from the skill folder and shell commands that work in both Claude Code and Codex (`python3`, local scripts, local paths). `agents/openai.yaml` is optional Codex/OpenAI UI metadata and is ignored by Claude Code. Don't introduce runtime-specific tool dependencies into the skill instructions.
- **`dist/` is generated release output**, not source — redacted sample HTML+PDF resumes for 10 role examples. Don't hand-edit; regenerate.
- **Licensing is AGPL-3.0-or-later (copyleft).** `LICENSE.md` is the verbatim GNU AGPL v3 text, preceded by the project copyright notice. It is an OSI open-source license and permits commercial use, but its network/copyleft clause (§13) requires modified versions served over a network to publish their source under the same terms. Don't relicense to a more permissive license (MIT/Apache) or strip the copyleft without explicit user approval — that would weaken the protection the maintainer chose. Keep SPDX headers (`AGPL-3.0-or-later`) on source files consistent.
