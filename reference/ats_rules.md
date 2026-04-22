# ATS Rules & Formatting Constraints
# Agent 2 (Resume Tailor) and Agent 3 (Scorer) use this file.
# Violating these rules means the resume may never be read by a human.

---

## WHAT IS ATS?

Applicant Tracking Systems (Greenhouse, Lever, Workday, iCIMS, Taleo, etc.) parse resumes
before a human ever sees them. Resumes that fail ATS parsing get auto-rejected regardless
of qualifications. These rules ensure clean machine-readable output.

---

## HARD RULES — NEVER VIOLATE

### Formatting
- [ ] Plain text or single-column layout ONLY — no multi-column layouts
- [ ] No tables, text boxes, or frames
- [ ] No headers or footers (ATS often can't read them)
- [ ] No graphics, logos, icons, or images
- [ ] No special Unicode characters, em dashes replaced with hyphens or colons
- [ ] Standard section headers only: SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION
- [ ] Consistent date format: "Jan 2022 – May 2026" or "2022 – 2026"
- [ ] Font: standard (Arial, Calibri, Georgia, Times New Roman) — 10–12pt body, 14–16pt name
- [ ] Margins: 0.5" to 1" — never less than 0.5"
- [ ] File format: .docx for most ATS (NOT .pdf unless specified — PDFs fail some parsers)

### Keywords
- [ ] Use EXACT phrases from the job description — not synonyms
  - JD says "machine learning" → use "machine learning" NOT "ML" or "artificial intelligence"
  - JD says "RESTful APIs" → use "RESTful APIs" NOT "REST APIs"
  - JD says "cross-functional teams" → use "cross-functional teams"
- [ ] Spell out acronyms at least once: "Application Programming Interface (API)"
- [ ] Include keywords in BOTH the Skills section AND embedded in bullet points
- [ ] Match the job title in your summary/headline to the exact title in the JD

### Content
- [ ] No "References available upon request" — wastes space, ATS ignores it
- [ ] No photos
- [ ] No personal info: age, marital status, religion, nationality
- [ ] No objective statements (use a summary instead)
- [ ] Bullet points start with strong action verbs (past tense for old roles, present for current)

---

## ACTION VERB BANK

**Built/Created:** Developed, Built, Engineered, Designed, Implemented, Architected, Created, Deployed

**Led/Managed:** Led, Managed, Directed, Coordinated, Supervised, Mentored, Trained, Oversaw

**Improved:** Optimized, Reduced, Improved, Enhanced, Streamlined, Accelerated, Increased

**Analyzed:** Analyzed, Evaluated, Investigated, Diagnosed, Identified, Assessed, Researched

**Delivered:** Delivered, Launched, Released, Shipped, Completed, Executed, Produced

**Collaborated:** Collaborated, Partnered, Interfaced, Contributed, Supported, Facilitated

---

## QUANTIFICATION GUIDE

Every bullet should answer: **So what? How much? How many? How fast?**

| Weak | Strong |
|------|--------|
| "Improved model accuracy" | "Improved model accuracy by 12% through feature engineering" |
| "Led a team" | "Led 6-person development team across 3 workstreams" |
| "Managed Marines" | "Supervised 8 Marines across 24/7 security operations covering X sq miles" |
| "Built an API" | "Built REST API serving 3 frontend clients with <100ms avg response time" |
| "Cleaned data" | "Cleaned and normalized 50,000+ property records for ML pipeline input" |

If you don't know exact numbers, use ranges or approximations ("~50", "10+", "3x").

---

## ATS KEYWORD PLACEMENT STRATEGY

Best placement for keyword scoring (highest to lowest weight):
1. **Job title / headline** in summary
2. **Skills section** — explicit list
3. **First bullet point** of each experience entry
4. **Project descriptions**
5. Later bullets

---

## COMMON ATS SYSTEMS BY COMPANY TYPE

| Company Type | Likely ATS |
|---|---|
| Large tech (Google, Meta, Amazon) | Workday, custom |
| Mid-size tech / startups | Greenhouse, Lever |
| Finance (Goldman, JPMorgan) | Taleo, Workday |
| Defense / Government contractors | USAJOBS, Taleo |
| Consulting | Workday, SAP SuccessFactors |

**Greenhouse and Lever** are generally the most resume-friendly.
**Taleo** is the most aggressive parser — apply strictest rules.

---

## RESUME LENGTH RULE

- New grad with < 3 years industry experience: **1 page, no exceptions**
- Military experience counts — but frame it in tech/leadership terms
- If content doesn't fit: cut older/less-relevant projects, trim bullets to 1 line

---

## TAILORING CHECKLIST (Agent 3 uses this for scoring)

- [ ] Job title in summary matches JD title exactly
- [ ] Top 5 required skills from JD appear in Skills section
- [ ] Top 5 required skills from JD appear in at least one bullet point
- [ ] Every bullet point has a number or measurable outcome
- [ ] No grammar errors or passive voice
- [ ] Dates are consistent format throughout
- [ ] Company name spelled correctly
- [ ] No personal pronouns (I, me, my)
- [ ] No clichés: "team player", "hard worker", "passionate about"

