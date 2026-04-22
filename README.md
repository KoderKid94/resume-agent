# Resume Agent

An agentic resume-tailoring system built on Claude Code that transforms a single master resume into ATS-optimized, job-specific resumes and cover letters — one-page guaranteed, scored, and iterated until it clears an 85/100 threshold.

Built by a graduating CS student to solve my own job-search problem: **how do you apply to 100+ roles without either (a) spraying the same resume everywhere or (b) burning an hour per application manually rewriting bullets?**

---

## What It Does

Give it a job description. It produces:

1. A **structured JD analysis** — required skills, preferred skills, exact ATS keywords, qualification gaps
2. A **tailored one-page resume** (Markdown source + PDF output) with content selected and reordered from your master resume to match the role
3. A **score report** grading the tailored resume on a 100-point rubric
4. **Automated improvement iterations** if the score comes in under 85
5. An optional **cover letter** mirroring the JD's tone and keywords

The pipeline runs end-to-end from a single paste of a job description. No per-step commands, no manual handoffs.

---

## Why I Built It

Applying to software roles as a new grad means volume. Each application wants a tailored resume — the same eight bullet points in a different order with different keywords emphasized — but doing that by hand is slow and inconsistent. Generic "resume optimizer" SaaS tools weren't any better: they either demanded paid subscriptions, produced templated LinkedIn-style output, or missed the judgment calls that actually matter (which project to lead with for this role, which keyword matters vs. which is noise).

I wanted a system that:

- Treats my **master resume as the single source of truth** and never fabricates experience
- Prioritizes **projects over work experience** (I'm a CS grad with no CS work history yet — inverting the default resume order is a deliberate choice)
- Produces **real PDFs at a guaranteed one-page length** so I can submit immediately
- Grades its own output and **iterates automatically** when the score is weak
- Runs locally in my editor so I can review, override, and re-run in seconds

Claude Code was the right substrate — file-aware, agentic, and already in my VS Code workflow.

---

## Architecture

The system runs as a **multi-agent pipeline** orchestrated by a `CLAUDE.md` file that acts as the brain. Each agent has a distinct responsibility and hands off structured output to the next.

```
Job Description
      ↓
┌─────────────────┐
│ Agent 1         │  JD Analyst
│ JD Analyst      │  → extracts keywords, skills, responsibilities, gaps
└────────┬────────┘
         ↓
┌─────────────────┐
│ Agent 2         │  Resume Tailor
│ Resume Tailor   │  → pulls from master_resume.md, reorders, injects keywords
└────────┬────────┘
         ↓
┌─────────────────┐
│ PDF Conversion  │  md_to_pdf.py
│ (pypdf loop)    │  → auto-scales font/spacing until output == 1 page
└────────┬────────┘
         ↓
┌─────────────────┐
│ Agent 3         │  Resume Scorer
│ Resume Scorer   │  → grades on 100-point rubric, flags weaknesses
└────────┬────────┘
         ↓
    Score ≥ 85? ──── No ──→ ┌─────────────────┐
         │                  │ Agent 4         │
        Yes                 │ Resume Improver │ ──┐
         ↓                  └─────────────────┘   │
┌─────────────────┐               ↑               │
│ Agent 5 (opt)   │               └───────────────┘
│ Cover Letter    │            (re-score, max 3 iterations)
└─────────────────┘
```

### Agent Responsibilities

**Agent 1 — JD Analyst**
Parses the job description into structured data. Captures exact keyword phrases verbatim (ATS matching is literal — "CI/CD" and "continuous integration" are different hits). Flags any required qualifications the candidate doesn't have so they can be addressed in the cover letter rather than papered over.

**Agent 2 — Resume Tailor**
Reads `reference/master_resume.md` and produces the tailored version. Hard constraints:
- Never invents experience — pulls only from the master
- Follows mandatory section order: **Summary → Technical Skills → Projects → Experience → Education**
- Injects JD keywords using exact phrasing where possible
- Quantifies every bullet that can be quantified (scale, %, count, outcome)
- Targets one page

**PDF Conversion (`scripts/md_to_pdf.py`)**
Converts the Markdown resume to a PDF using ReportLab, then verifies the output is exactly one page using `pypdf`. If it overflows, it walks a scale table (font size, leading, spacing) progressively tighter and re-renders until page count equals 1. This guarantees the output is always single-page regardless of how dense the content is.

**Agent 3 — Resume Scorer**
Grades the tailored resume against `reference/scoring_rubric.md`:

| Category          | Weight |
|-------------------|--------|
| ATS Keywords      | 30     |
| Quantification    | 25     |
| Formatting        | 20     |
| Tailoring         | 15     |
| Clarity           | 10     |
| **Total**         | **100** |

Also lists missing keywords from the JD and flags any ATS violations (tables, graphics, unusual characters).

**Agent 4 — Resume Improver**
Auto-invoked when Agent 3's score is below 85. Fixes each flagged weakness, re-runs PDF conversion, re-scores, and repeats up to three iterations.

**Agent 5 — Cover Letter Writer** (optional)
On request, generates a cover letter using `reference/cover_letter_template.md`. Mirrors the JD's tone and keywords, connects the candidate's background as a differentiator, stays under 400 words.

---

## Directory Structure

```
resume-agent/
├── CLAUDE.md                          # Orchestration — brain of the system
├── requirements.txt                   # Python deps (auto-installed on first run)
├── .gitignore                         # Excludes .venv/, outputs
├── application_tracker.md             # Log of submitted applications
│
├── reference/                         # Source of truth — never touched by pipeline
│   ├── master_resume.md               # Complete career/project inventory
│   ├── ats_rules.md                   # ATS formatting constraints
│   ├── scoring_rubric.md              # 100-point scoring definitions
│   ├── cs_keywords.md                 # Keyword bank by role type
│   └── cover_letter_template.md       # Cover letter structure
│
├── jobs/                              # Auto-populated per application
│   └── [Company]_[Role].md            # JD analysis output
│
├── scripts/
│   └── md_to_pdf.py                   # MD → PDF converter with one-page guarantee
│
└── resumes/                           # Auto-populated per application
    └── [Company]_[Role]/
        ├── [Company]_[Role]_resume.md        # Tailored markdown source
        ├── [Company]_[Role]_resume.pdf       # Submission-ready PDF
        └── [Company]_[Role]_coverletter.md   # Optional cover letter
```

---

## Usage

**Prerequisites:** Claude Code installed, Python 3.10+, VS Code.

**First-time setup:**

```bash
git clone git@github.com:KoderKid94/resume-agent.git
cd resume-agent
# Fill out reference/master_resume.md with your complete career/project inventory
code .
```

Open Claude Code in the `resume-agent/` directory. The venv and dependencies auto-install on first run.

**Running the pipeline:**

Paste a job description directly into Claude Code. Any of these trigger the pipeline:

```
new job: [paste JD]
apply to this: [paste JD]
[paste JD]
```

The pipeline runs end-to-end and prints:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESUME READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Job:     Backend Engineer — ExampleCo
Score:   91/100 (A)
PDF:     resumes/ExampleCo_BackendEngineer/ExampleCo_BackendEngineer_resume.pdf
Source:  resumes/ExampleCo_BackendEngineer/ExampleCo_BackendEngineer_resume.md

Gaps flagged:
  • No Kubernetes production experience
  • No commercial Go experience (Python/Java only)

Would you like a cover letter for this role? (yes / no)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Review the PDF, edit if needed (the Markdown source is always regenerable), and submit.

---

## Design Decisions Worth Calling Out

**Projects before Experience, always.** Standard resume advice puts Experience first. That advice was written for people with relevant work history. For a new grad whose strongest evidence of ability is a capstone, a TCP multiplayer game, and an AI search-algorithms project that scored 104/100, burying that under "Military Police Officer, 2018–2022" is leaving the most relevant content below the fold. The pipeline enforces Projects above Experience regardless of what a generic best-practice guide says.

**Exact-phrase keyword matching, not synonyms.** ATS systems do literal matching on most criteria. If the JD says "RESTful APIs," the resume says "RESTful APIs" — not "REST services" or "HTTP APIs." Agent 2 preserves the JD's exact wording and lets the candidate's actual work speak for itself underneath.

**One-page enforcement via render-and-measure, not token estimation.** Instead of guessing at line counts or word limits, `md_to_pdf.py` actually renders the PDF, counts the pages with `pypdf`, and retries at a tighter scale if overflow occurs. This is slower than estimation but eliminates the "my resume is 1.05 pages" failure mode.

**Never fabricates.** Agent 2 is explicitly instructed to pull only from `master_resume.md`. If a JD asks for a skill the candidate doesn't have, it surfaces as a flagged gap, not an invented bullet. Integrity over score.

**Human in the loop at the end.** The pipeline ends with a PDF and a score, not a submitted application. The candidate still reviews every output before sending. This is a tool that makes tailoring 10x faster, not a bot that auto-applies.

---

## Tech Stack

- **Orchestration:** Claude Code + `CLAUDE.md` as the agent controller
- **Runtime:** Python 3.10+ in an auto-managed venv
- **PDF generation:** ReportLab (flowables, paragraph styles, custom scale tables)
- **PDF verification:** pypdf (page-count read loop)
- **Editor integration:** VS Code + Claude Code extension
- **Version control:** Git (SSH authentication)

---

## Roadmap

*(To be finalized — placeholder section pending a full review of the current program state.)*

- TBD

---

## Author

**Kenya Sayles Jr.** — BS Computer Science, University of Texas at Dallas (May 2026) · U.S. Marine Corps veteran

- GitHub: [KoderKid94](https://github.com/KoderKid94)
- LinkedIn: [kenya-sayles-jr](https://www.linkedin.com/in/kenya-sayles-jr)
- Email: kenya.sayjr@gmail.com
