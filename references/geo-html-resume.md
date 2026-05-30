# GEO and HTML Resume Reference

Use this reference when generating HTML/PDF-ready resumes or optimizing for ATS, AI screening, recruiter agents, and generative search.

## GEO/ATS Checklist

- Keep all critical resume content as selectable text.
- Use common section labels: Summary, Experience, Projects, Education, Skills, Certifications, Awards; Chinese equivalents are fine for Chinese resumes.
- Use truthful target-role language backed by visible evidence in the title, summary, skills, and relevant experience bullets.
- Include natural keyword variants only where natural, such as summary, skills, or matching experience/project bullets, with examples like "产品运营 / 用户增长 / 活动运营 / 数据复盘" or "data analyst / SQL / dashboard / cohort analysis".
- Include contact details in visible text and machine-readable schema when appropriate.
- Add a concise `<meta name="description">` that states candidate positioning.
- Add `<meta name="keywords">` only when useful, and only with truthful, role-relevant keywords that also appear naturally in visible content.
- Add schema.org `Person` JSON-LD with name, email, telephone, addressLocality, jobTitle when current/accurate, knowsAbout, alumniOf, url, and contact/location fields when available; model seeks only if using a valid schema.org object.
- Avoid hidden keyword blocks, invisible text, repeated keyword stuffing, image-only resumes, and tables that break reading order.

## Content Quality Boundaries

ATS and recruiter agents should receive the same truthful content that human HR sees.

- Use visible, natural keywords only; never add hidden keyword blocks.
- Keep aliases close to actual proof, such as "SQL / dashboard / cohort analysis" in skills and a matching project bullet.
- Prefer role nouns over decorative labels: "Experience" and "Projects" parse better than poetic headings.
- Keep bullet order meaningful: strongest role-relevant evidence first, older or weaker proof later.
- Do not over-optimize meta keywords. If a skill is not visible in the resume body, remove it from meta keywords.
- Do not convert contact, section headings, company names, schools, or skills into images.

## HTML Requirements

- Use semantic landmarks: `main`, `header`, `section`, headings, lists, and links.
- Set `<html lang="zh-CN">` for Chinese resumes or a suitable language code for other languages.
- Include viewport metadata for mobile.
- Use system fonts or bundled fonts only; avoid network font dependencies.
- Keep color contrast high and decoration quiet.
- Use responsive CSS with a mobile breakpoint around 720px or lower.
- Use print CSS with `@page`, `@media print`, page-break controls, and ink-friendly colors.
- Avoid layout that depends on JavaScript. JSON-LD is fine.
- Keep `<title>`, meta description, meta keywords, visible target role, and JSON-LD jobTitle/seeks aligned with the same target direction.

## Template Usage

Start from `assets/resume-template.html` for polished Chinese resumes:

Non-Chinese resumes can use the template after language, metadata, and section-label adaptation.

1. Copy the asset to the user's requested output path.
2. Replace all sample identity, contact, education, experience, projects, skills, awards, meta tags, title, and JSON-LD data.
3. Remove irrelevant sections instead of leaving placeholders.
4. Keep the CSS structure unless the target industry calls for a different visual tone.
5. For senior candidates, move work experience before education.
6. For one-page resumes, reduce weak content before reducing font size.

## PDF Export QA

After exporting PDF:

- Open or render the PDF when possible and check that no section is cut off.
- Confirm links and contact text remain selectable if the tool supports selectable PDF output.
- Check mobile HTML separately; a good PDF does not guarantee a good phone layout.
- Mention any environment limitation if PDF export or visual inspection cannot be run.
- Check that the first screen on mobile still exposes name, target role, contact path, and one concise positioning line or proof point without horizontal scroll.
