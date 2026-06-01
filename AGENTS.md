# BEGIN PROMPTIFY MANAGED BLOCK
# Promptify for Codex

Adapter skill: /Users/blingabc/.promptify/current/adapters/codex/skills/promptify/SKILL.md
Fallback instructions: /Users/blingabc/.promptify/current/adapters/codex/instructions/promptify.md
Shared rules: /Users/blingabc/.promptify/current/shared
# END PROMPTIFY MANAGED BLOCK

# Repository Instructions

This repository contains `resume-skill`, a Codex/Claude-compatible AI skill for Chinese resume review, rewriting, ATS/GEO optimization, and HTML/PDF resume generation.

## Primary Files

- `SKILL.md`: Core runtime instructions for the skill.
- `references/`: Resume review, role-specific writing, and ATS/GEO guidance.
- `assets/resume-template.html`: Source template for generated HTML resumes.
- `resume-template.html`: Local preview copy of the resume template.
- `scripts/check_resume_html.py`: Validator for generated resume HTML.
- `scripts/export_resume_pdf.py`: HTML-to-PDF export helper.
- `tests/`: Unit tests for scripts and validation behavior.
- `dist/`: Example generated HTML/PDF resumes.

## Working Rules

- Preserve the Promptify managed block above. Do not edit it unless the user explicitly asks to update Promptify integration.
- Follow `SKILL.md` when changing resume-writing behavior, references, templates, scripts, or examples.
- Keep instructions portable across Codex, Claude Code, and compatible skill runtimes. Prefer relative paths and simple `python3` commands.
- Do not invent resume facts, employers, schools, dates, certificates, titles, or metrics. Use only user-provided facts, clearly marked assumptions, or proxy scale facts.
- Optimize for HR readability, ATS/GEO parsing, and visible selectable text. Do not add hidden keyword blocks, white-on-white text, or image-only resume content.
- Keep Chinese resume copy concise, credible, and role-oriented. Replace weak claims like "熟悉", "了解", "负责", and "参与" with truthful evidence whenever possible.
- Keep changes scoped. Avoid broad rewrites of templates, generated examples, or reference docs unless the task requires them.
- Project is licensed under AGPL-3.0-or-later (copyleft). Do not relicense, weaken the copyleft, or change licensing language without explicit user approval.

## HTML/PDF Guidance

- Use `assets/resume-template.html` as the source for polished HTML resume artifacts.
- Preserve semantic HTML, responsive mobile layout, print styles, `@page`, useful meta tags, and schema.org `Person` JSON-LD.
- Ensure all important resume content remains visible and selectable.
- Generated HTML should pass validation before being treated as ready:

```bash
python3 scripts/check_resume_html.py path/to/resume.html
```

- Export PDF only when requested or clearly useful:

```bash
python3 scripts/export_resume_pdf.py path/to/resume.html path/to/resume.pdf
```

## Verification

- For validator or script changes, run:

```bash
python3 -m unittest tests/test_check_resume_html.py
```

- For broader changes, run:

```bash
python3 -m unittest
```

- For template checks, run:

```bash
python3 scripts/check_resume_html.py assets/resume-template.html --allow-placeholders
```
