---
name: resume-skill
description: Use when an AI coding assistant needs to rewrite an existing resume, create a new resume from user background materials, give HR-style resume feedback, optimize a resume for ATS, recruiter agents, AI screening, GEO, or generate a professional responsive HTML/PDF-ready resume for mobile and desktop in Claude Code, Codex, or compatible skill runtimes.
---

# Resume Skill

## Overview

Turn raw career materials into a concise, credible, HR-readable resume. Produce content that works for humans and screening agents, then deliver a responsive HTML resume that can be viewed on mobile/desktop and exported to PDF. Keep instructions portable across Claude Code, Codex, and compatible skill runtimes.

## Quick Routing

- Existing resume: audit first, then rewrite the resume section-by-section.
- New resume: inventory the user's background, infer the target positioning, then draft a complete resume.
- Advice-only request: provide HR review findings, prioritized fixes, and examples of stronger wording.
- HTML/PDF request: use `assets/resume-template.html` as the starting layout, then run the validation script before delivery.

If the target role, industry, seniority, or language is missing and cannot be inferred, ask one concise question. Otherwise make explicit assumptions and continue.

## Runtime Compatibility

- Use only relative paths from this skill folder when loading references, templates, or scripts.
- Treat `agents/openai.yaml` as optional Codex/OpenAI UI metadata; Claude Code can ignore it.
- Avoid relying on product-specific tools unless the user explicitly asks for that runtime's integration.
- Prefer shell commands that work in both Claude Code and Codex: `python3`, local scripts, and local file paths.

## Required Workflow

1. Build an input inventory: target role/JD, work or internship history, projects, education, skills, certifications, awards, links, location, availability, and constraints.
2. Read `references/hr-resume-review.md` before giving HR-style critique, rewriting bullets, or creating a resume from raw notes.
3. Read `references/role-playbooks.md` when the user names a target role, provides a JD, asks for role-specific optimization, or the target can be reasonably inferred.
4. Read `references/geo-html-resume.md` before optimizing for ATS/AI/GEO or generating HTML/PDF-ready output.
5. Rewrite content with evidence: use action + scope + method + impact; keep dates, companies, schools, degrees, and metrics truthful.
6. Optimize keywords without stuffing: mirror target-role language, include common aliases, and keep all important content visible as selectable text.
7. Generate HTML from `assets/resume-template.html` when a polished artifact is requested. Replace sample data, meta tags, JSON-LD, section headings, and all visible content.
8. Run `python3 scripts/check_resume_html.py <resume.html>` for generated HTML. Fix failures before claiming the artifact is ready.
9. Export PDF only when requested or useful with `python3 scripts/export_resume_pdf.py <resume.html> <resume.pdf>`, then verify the file exists.

## HR Writing Rules

- Lead with fit for the target role, not biography.
- Prefer strong nouns and verbs over adjectives: "reduced review time by 30%" beats "excellent communication skills".
- Use real numbers when provided; never invent metrics. If a metric is missing, ask, estimate only when the user explicitly authorizes it, or use scale/proxy facts such as frequency, volume, users, duration, or stakeholder count.
- Convert duties into outcomes. Preserve a short responsibility phrase only when the role context would otherwise be unclear.
- Remove weak claims: "familiar with", "responsible for", "participated in", "good at", "hardworking", and unsupported self-evaluations.
- Keep one resume optimized for one target. If the user has multiple targets, create variants.

## HTML Artifact Rules

- Keep the resume as semantic HTML, not an image or canvas.
- Preserve mobile readability: no fixed-width content wider than the viewport, no tiny text, no horizontal scroll.
- Preserve PDF export quality: include `@page`, `@media print`, page-break controls, and no screen-only critical content.
- Include GEO signals: meaningful `<title>`, meta description, meta keywords when useful, schema.org `Person` JSON-LD, machine-readable contact details, and target-role keywords in natural visible text.
- Avoid hidden keyword blocks, white-on-white text, fake roles, fake skills, or unverifiable claims.

## Output Shape

For resume rewriting, return:

- A short HR diagnosis with the highest-impact issues first.
- A scorecard-style view for the limiting dimensions when the user asks for professional review.
- Role-specific keyword and evidence gaps when a target role or JD is available.
- HR risk flags and concrete mitigation wording.
- The rewritten resume content or updated artifact path.
- Any assumptions, missing facts, or metric questions that would improve the next pass.

For new HTML resumes, return the local HTML path, PDF path if exported, and the validation command result.
