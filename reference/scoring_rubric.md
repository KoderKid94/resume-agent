# Resume Scoring Rubric
# Used by Agent 3 (Resume Scorer) to evaluate tailored resumes.
# Score range: 0–100. Target: 85+. Rewrite if below 85.

---

## SCORING CATEGORIES

### 1. ATS Keyword Match (30 points)

| Score | Criteria |
|-------|----------|
| 28–30 | 90%+ of required JD keywords present; exact phrases used; keywords in both Skills and bullets |
| 22–27 | 70–89% of required keywords; mostly exact phrases; minor synonym usage |
| 15–21 | 50–69% of required keywords; some synonyms; gaps in coverage |
| 0–14  | <50% keyword match; heavy synonym use; major keyword gaps |

**How to score:**
1. List all required/preferred skills from the JD
2. Check each against Skills section (1pt each, max 15)
3. Check each against bullet points (1pt each, max 15)
4. Total = keyword score

---

### 2. Quantification & Impact (25 points)

| Score | Criteria |
|-------|----------|
| 23–25 | Every bullet quantified with numbers, %, scale, or clear outcome |
| 18–22 | 80%+ bullets quantified; strong action verbs throughout |
| 12–17 | 50–79% bullets quantified; some vague bullets remain |
| 0–11  | <50% bullets quantified; heavy use of vague language |

**Deductions:**
- "Worked on..." (-2 per instance)
- "Helped with..." (-2 per instance)
- "Responsible for..." (-2 per instance)
- "Experienced in..." (-1 per instance)
- Missing number/outcome in experience bullets (-1 each)

---

### 3. ATS Formatting Compliance (20 points)

| Score | Criteria |
|-------|----------|
| 19–20 | Zero formatting violations; clean single-column; standard headers |
| 15–18 | 1–2 minor violations (e.g., one table, one graphic) |
| 10–14 | 3–4 violations; parsing risk |
| 0–9   | 5+ violations; high rejection risk |

**Violations (each = -2):**
- Multi-column layout
- Table
- Header/footer content
- Graphic or image
- Non-standard section name
- Special characters (em dashes, bullets not using •)
- Inconsistent date formats
- Font < 10pt

---

### 4. Relevance & Tailoring (15 points)

| Score | Criteria |
|-------|----------|
| 14–15 | Resume reads as if written specifically for this job; top projects match JD priorities |
| 11–13 | Strong tailoring with minor generic elements |
| 7–10  | Partially tailored; some generic bullets remain |
| 0–6   | Generic resume with surface-level keyword insertion |

**Checks:**
- Does the summary mention the exact job title? (+3)
- Are the most JD-relevant projects listed first? (+3)
- Are generic bullets replaced with JD-specific language? (+4)
- Does the skills section mirror JD language exactly? (+5)

---

### 5. Clarity & Professionalism (10 points)

| Score | Criteria |
|-------|----------|
| 9–10  | Zero errors; crisp active voice; easy to scan in 6 seconds |
| 7–8   | 1–2 minor errors; strong readability |
| 4–6   | 3–5 errors or passive voice issues |
| 0–3   | Grammar/spelling errors; hard to read; unprofessional tone |

**Deductions:**
- Spelling error (-2 each)
- Grammar error (-1 each)
- Personal pronoun (I/me/my) (-1 each)
- Cliché ("team player", "passionate", "hard worker") (-1 each)
- Objective statement instead of summary (-2)

---

## SCORING TEMPLATE (Agent 3 Output Format)

```
RESUME SCORE REPORT
====================
Company:      [NAME]
Role:         [TITLE]
Date:         [DATE]
Version:      v[X]

SCORES
------
ATS Keyword Match:       [XX] / 30
Quantification/Impact:   [XX] / 25
Formatting Compliance:   [XX] / 20
Relevance/Tailoring:     [XX] / 15
Clarity/Professionalism: [XX] / 10

TOTAL SCORE: [XX] / 100

GRADE: [A/B/C/D/F]
  A = 90–100 (submit with confidence)
  B = 80–89  (submit; minor improvements possible)
  C = 70–79  (revise before submitting)
  D = 60–69  (significant rework needed)
  F = <60    (start over with Agent 2)

TOP 3 STRENGTHS
1. [strength]
2. [strength]
3. [strength]

TOP 3 WEAKNESSES
1. [weakness + specific fix]
2. [weakness + specific fix]
3. [weakness + specific fix]

MISSING KEYWORDS FROM JD
- [keyword] — not found in resume
- [keyword] — found in skills but not in bullets (add to a bullet)
- [keyword] — synonym used instead of exact phrase

ATS VIOLATIONS
- [violation] at [location in resume]
- [violation] at [location in resume]

RECOMMENDATION
[Submit / Revise / Major rewrite — with specific next steps]
```

---

## GRADE THRESHOLDS

| Score | Grade | Action |
|-------|-------|--------|
| 90–100 | A | Submit. Optional: minor polish. |
| 85–89 | B+ | Submit. Note weaknesses for v2 if no response in 2 weeks. |
| 80–84 | B | 1 more pass with Agent 4 before submitting. |
| 70–79 | C | Mandatory Agent 4 revision. Re-score. |
| <70 | D/F | Re-run Agent 2 from scratch. Do not submit. |

