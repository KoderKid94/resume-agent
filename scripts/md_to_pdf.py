#!/usr/bin/env python3
"""
md_to_pdf.py — Resume Markdown to PDF Converter

GUARANTEE: Output is always exactly 1 page.

Strategy:
1. Parse resume sections, assign relevance weights
2. Render to temp PDF — check actual page count
3. If > 1 page: remove lowest-weight removable element, repeat
4. Loop until page count == 1
5. Write final PDF

Weights (higher = more protected, removed last):
  10 = name, contact, section headers         — never removed
   8 = project 1 header/meta                   — most relevant project, never removed
   7 = project 1 bullets                       — protected
   6 = education entries, project 2 hdr/meta   — education is the qualifying
                                                 credential; entries never removed
   5 = project 2 bullets                       — protected
   4 = project 3 hdr/meta, military hdr/meta   — entries never removed
   3 = project 3 bullets, military bullets     — trimmed after low-trust content
   2 = skills lines, coursework, summary body  — trimmed first
   1 = project 4+ headers (entire block)       — removed after bullets exhausted

NOTE: Section order in the rendered PDF follows the markdown source order
(Summary -> Education -> Projects -> Experience -> Technical Skills). These
weights only decide WHAT GETS TRIMMED when content overflows one page — not
section order. Priorities reflect the 2026-06-06 ordering decision:
  - Education is the qualifying credential for a new grad -> protected near the
    top, never removed.
  - Projects are the primary evidence of ability -> they outrank military
    experience, which is always included but trimmed before project 1/2 content.
  - A self-reported skills list is a low-trust signal (and ATS parses keywords
    regardless of placement) -> skills lines are trimmed first.
"""

import sys
import re
import tempfile
from pathlib import Path
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.enums import TA_CENTER
from pypdf import PdfReader

PAGE_W, PAGE_H = letter

# Font scales to try — starts at best quality, compresses only if needed
SCALES = [
    (9.0, 12.0, 7, 4, 1.5, 0.55, 0.65),
    (8.8, 11.5, 6, 3, 1.2, 0.50, 0.60),
    (8.5, 11.0, 5, 3, 1.0, 0.45, 0.55),
    (8.2, 10.6, 4, 2, 0.8, 0.42, 0.52),
    (8.0, 10.2, 3, 2, 0.6, 0.40, 0.50),
    (7.8, 10.0, 2, 1, 0.5, 0.37, 0.48),
]


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_md(md_text):
    sections     = []
    header_done  = False
    project_idx  = 0
    in_military  = False
    current_group = None

    in_education = False

    for line in md_text.strip().split('\n'):
        line = line.rstrip()
        if not line:
            continue
        if line.startswith('>') or 'AGENT NOTE' in line or 'DO NOT SUBMIT' in line:
            continue

        if line.startswith('# ') and not sections:
            sections.append(dict(type='name', text=line[2:].strip(),
                weight=10, group='header', removable=False))

        elif '|' in line and not line.startswith('#') and not line.startswith('-') and not header_done:
            sections.append(dict(type='contact', text=line.strip(),
                weight=10, group='header', removable=False))
            header_done = True

        elif line.startswith('## '):
            sec = line[3:].strip()
            in_military   = False
            in_education  = sec.lower() == 'education'
            current_group = f'sec_{sec}'
            sections.append(dict(type='section', text=sec,
                weight=10, group=current_group, removable=False))

        elif line.startswith('### '):
            entry  = line[4:].strip()
            is_mil = any(k in entry.lower() for k in ['marine', 'military', 'corps', 'usmc'])
            if in_education:
                # Education entries get their own group, never removed
                edu_group = f'edu_{entry[:20].replace(" ", "_")}'
                current_group = edu_group
                sections.append(dict(type='entry_header', text=entry,
                    weight=6, group=edu_group, removable=False))
            elif is_mil:
                in_military   = True
                current_group = 'military'
                sections.append(dict(type='entry_header', text=entry,
                    weight=4, group='military', removable=False))
            else:
                in_military  = False
                project_idx += 1
                current_group = f'proj_{project_idx}'
                if project_idx == 1:
                    hdr_w = 8
                elif project_idx == 2:
                    hdr_w = 6
                elif project_idx == 3:
                    hdr_w = 4
                else:
                    hdr_w = 1
                sections.append(dict(type='entry_header', text=entry,
                    weight=hdr_w, group=current_group,
                    removable=(project_idx > 2)))

        elif line.startswith('**') and '|' in line:
            if in_education:
                sections.append(dict(type='entry_meta', text=line.strip(),
                    weight=6, group=current_group, removable=False))
            elif in_military:
                sections.append(dict(type='entry_meta', text=line.strip(),
                    weight=4, group='military', removable=False))
            else:
                if project_idx == 1:
                    meta_w = 8
                elif project_idx == 2:
                    meta_w = 6
                elif project_idx == 3:
                    meta_w = 4
                else:
                    meta_w = 1
                sections.append(dict(type='entry_meta', text=line.strip(),
                    weight=meta_w, group=current_group,
                    removable=(project_idx > 2)))

        elif line.startswith('- ') or line.startswith('• '):
            text = line[2:].strip()
            if 'AGENT NOTE' in text:
                continue
            if in_military:
                # Military bullets removable only after project 3+ content is gone
                sections.append(dict(type='bullet', text=text,
                    weight=3, group='military', removable=True))
            elif current_group and current_group.startswith('proj_'):
                if project_idx == 1:
                    bul_w = 7
                elif project_idx == 2:
                    bul_w = 5
                elif project_idx == 3:
                    bul_w = 3
                else:
                    bul_w = 1
                sections.append(dict(type='bullet', text=text,
                    weight=bul_w, group=current_group, removable=True))
            else:
                sections.append(dict(type='bullet', text=text,
                    weight=3, group=current_group or 'misc', removable=True))

        elif header_done and not line.startswith('#'):
            sections.append(dict(type='text', text=line.strip(),
                weight=2, group=current_group or 'misc', removable=True))

    return sections


def md_to_rl(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*',     r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`',       r'\1',        text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text


# ── Story builder ─────────────────────────────────────────────────────────────

def make_story(sections, scale):
    fb, lb, sec_b, ent_b, bul_a, mt, ms = scale
    dark = colors.HexColor('#1a1a1a')
    mid  = colors.HexColor('#555555')
    body = colors.HexColor('#1f1f1f')
    rule = colors.HexColor('#2c2c2c')

    sty = {
        'name':         ParagraphStyle('N',  fontName='Helvetica-Bold',
                            fontSize=15, leading=18, textColor=dark,
                            alignment=TA_CENTER, spaceAfter=1),
        'contact':      ParagraphStyle('C',  fontName='Helvetica',
                            fontSize=fb-0.5, leading=lb-1, textColor=mid,
                            alignment=TA_CENTER, spaceAfter=3),
        'section':      ParagraphStyle('S',  fontName='Helvetica-Bold',
                            fontSize=fb+0.3, leading=lb, textColor=dark,
                            spaceBefore=sec_b, spaceAfter=1),
        'entry_header': ParagraphStyle('EH', fontName='Helvetica-Bold',
                            fontSize=fb, leading=lb, textColor=dark,
                            spaceBefore=ent_b, spaceAfter=0),
        'entry_meta':   ParagraphStyle('EM', fontName='Helvetica-Oblique',
                            fontSize=fb-0.5, leading=lb-1,
                            textColor=colors.HexColor('#666666'), spaceAfter=1),
        'bullet':       ParagraphStyle('B',  fontName='Helvetica',
                            fontSize=fb, leading=lb,
                            leftIndent=10, firstLineIndent=-7,
                            spaceAfter=bul_a, textColor=body),
        'text':         ParagraphStyle('T',  fontName='Helvetica',
                            fontSize=fb-0.3, leading=lb-0.5,
                            spaceAfter=1, textColor=body),
    }

    story = []
    for item in sections:
        kind = item['type']
        raw  = item['text']
        t    = md_to_rl(raw)

        if kind == 'name':
            story.append(Paragraph(t, sty['name']))
        elif kind == 'contact':
            story.append(Paragraph(re.sub(r'\*\*(.*?)\*\*', r'\1', raw), sty['contact']))
        elif kind == 'section':
            story.append(HRFlowable(width='100%', thickness=0.6, color=rule, spaceAfter=1))
            story.append(Paragraph(t.upper(), sty['section']))
        elif kind == 'entry_header':
            story.append(Paragraph(t, sty['entry_header']))
        elif kind == 'entry_meta':
            story.append(Paragraph(re.sub(r'\*\*(.*?)\*\*', r'\1', raw), sty['entry_meta']))
        elif kind == 'bullet':
            story.append(Paragraph(f'&#8226;&nbsp;{t}', sty['bullet']))
        elif kind == 'text':
            story.append(Paragraph(t, sty['text']))

    return story


# ── Render to temp file and check page count ──────────────────────────────────

def render_temp(sections, scale):
    """Render to a temp file, return actual page count."""
    fb, lb, sec_b, ent_b, bul_a, mt, ms = scale
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        tmp = f.name
    doc = SimpleDocTemplate(tmp, pagesize=letter,
        leftMargin=ms*inch, rightMargin=ms*inch,
        topMargin=mt*inch,  bottomMargin=mt*inch)
    doc.build(make_story(sections, scale))
    pages = len(PdfReader(tmp).pages)
    Path(tmp).unlink()
    return pages


# ── Trim loop ─────────────────────────────────────────────────────────────────

def trim_to_one_page(sections, scale):
    """
    Remove lowest-relevance elements one at a time, re-rendering after each,
    until the resume fits on exactly 1 page.
    Returns (trimmed_sections, trim_log).
    """
    working  = [s.copy() for s in sections]
    trim_log = []

    for _ in range(60):  # hard safety cap
        pages = render_temp(working, scale)
        if pages == 1:
            return working, trim_log

        # Find removable items sorted by weight (lowest first)
        # Within same weight: prefer removing individual bullets before whole project blocks
        removable = [s for s in working if s['removable']]
        if not removable:
            break

        removable.sort(key=lambda s: (
            s['weight'],
            0 if s['type'] == 'bullet' else  # bullets before headers
            1 if s['type'] == 'text'   else
            2
        ))

        target = removable[0]

        if target['type'] in ('entry_header', 'entry_meta'):
            # Pull the whole project group — header, meta, and all bullets
            group  = target['group']
            before = len(working)
            working = [s for s in working if s['group'] != group]
            n = before - len(working)
            trim_log.append(f"Removed project '{target['text'][:50]}' (group={group}, {n} elements)")
        else:
            working.remove(target)
            trim_log.append(f"Trimmed {target['type']}: '{target['text'][:55]}...' [w={target['weight']}]")

    return working, trim_log


# ── Main build ────────────────────────────────────────────────────────────────

def build_pdf(sections, output_path):
    """
    Try each scale from loosest to tightest.
    For each scale, run the trim loop.
    Use the first combination that achieves 1 page.
    """
    for scale in SCALES:
        trimmed, log = trim_to_one_page(sections, scale)
        pages = render_temp(trimmed, scale)
        if pages == 1:
            # Write final PDF
            fb, lb, sec_b, ent_b, bul_a, mt, ms = scale
            doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                leftMargin=ms*inch, rightMargin=ms*inch,
                topMargin=mt*inch,  bottomMargin=mt*inch)
            doc.build(make_story(trimmed, scale))
            return scale[0], log

    # Absolute fallback — tightest scale, maximum trimming
    scale   = SCALES[-1]
    trimmed, log = trim_to_one_page(sections, scale)
    fb, lb, sec_b, ent_b, bul_a, mt, ms = scale
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
        leftMargin=ms*inch, rightMargin=ms*inch,
        topMargin=mt*inch,  bottomMargin=mt*inch)
    doc.build(make_story(trimmed, scale))
    return scale[0], log


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/md_to_pdf.py <input.md> <output_folder>")
        sys.exit(1)

    input_path    = Path(sys.argv[1])
    output_folder = Path(sys.argv[2])
    output_folder.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    sections          = parse_md(input_path.read_text(encoding='utf-8'))
    pdf_path          = output_folder / f"{input_path.stem}.pdf"
    font_pt, trim_log = build_pdf(sections, pdf_path)

    # Verify
    final_pages = len(PdfReader(str(pdf_path)).pages)
    status = "✓ 1 page confirmed" if final_pages == 1 else f"⚠ {final_pages} pages"

    print(f"✓ PDF created:     {pdf_path}  [font: {font_pt}pt | {status}]")
    print(f"✓ Markdown source: {input_path}")

    if trim_log:
        print(f"\n  Trimmed {len(trim_log)} element(s) to fit 1 page:")
        for entry in trim_log:
            print(f"    - {entry}")
    else:
        print("  All content fit — no trimming needed.")


if __name__ == '__main__':
    main()
