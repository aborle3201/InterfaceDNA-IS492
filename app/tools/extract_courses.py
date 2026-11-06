"""Extract real UIUC course data from the PDFs in "University docs/" into
app/sources/courses.json. Run once after the source PDFs change:

    pip install pypdf
    python tools/extract_courses.py          (from app/)

CS and IS courses come from the departmental course listings (catalog current as
of 06/2026). Supporting courses used by the CS/IS degree plans come from the
requirement tables in the 2026-2027 Academic Catalog.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re

from pypdf import PdfReader

APP = pathlib.Path(__file__).resolve().parents[1]
DOCS = APP.parent / 'University docs'
OUT = APP / 'sources' / 'courses.json'

LISTINGS = ['CS courses.pdf', 'IS courses.pdf']
CATALOG = 'UIUC catalog 2026-2027.pdf'

# Non-CS/IS courses used in the synthetic degree plans. Each must appear in a
# catalog requirement table with a title and credit hours.
SUPPORTING = [
    'MATH 220', 'MATH 221', 'MATH 231', 'MATH 241', 'MATH 225', 'MATH 227',
    'PHYS 211', 'PHYS 212', 'ENG 100', 'STAT 107', 'STAT 207', 'STAT 400',
    'ECON 102', 'ECON 103', 'PSYC 100', 'SOC 100', 'ANTH 101', 'CHEM 102',
    'CHEM 103', 'IB 150', 'GEOL 107', 'CMN 101', 'LING 100', 'MUS 132',
    'GLBL 100', 'AAS 100', 'AFRO 100', 'LLS 100', 'BADM 310', 'ACCY 201',
    'PHIL 103',
    # TE courses in the ILEE (Technology Entrepreneur Center) requirements
    'TE 230', 'TE 250', 'TE 333', 'TE 360', 'TE 390', 'TE 401',
    'TE 461', 'TE 462', 'TE 466', 'SE 361',
]
# The 2026-2027 catalog table wraps this title across lines, so the generic
# row pattern misses it. Verified by hand: Computer Science, BS, page 238.
MANUAL = {
    'MATH 257': ('Linear Algebra with Computational Applications', '3', 238),
    # Titles wrap in the ILEE table, Innovation, Leadership & Engineering
    # Entrepreneurship (ILEE), BS, page 476 (quoted in sources/programs.json).
    'TE 100': ('Introduction to Innovation, Leadership and Engineering Entrepreneurship', '1', 476),
    'TE 450': ('Startups: Incorporation, Funding, Contracts, & Intellectual Property', '3', 476),
}

ENTRY = re.compile(
    r'(?m)^([A-Z]{2,4}) (\d{3})   (.+?)   credit: (.+?)\s*Hours?\.', re.S)
ROW = re.compile(
    r'(?m)^([A-Z]{2,5}) (\d{3}) ([A-Z&][^\n]{2,80}?) (\d(?: or \d| to \d)?)\s*$')
PAGE = re.compile(r'<<PAGE (\d+)>>')


def pdf_text(name):
    reader = PdfReader(DOCS / name)
    return ''.join(
        f'\n<<PAGE {i}>>\n' + (p.extract_text() or '').replace(' ', ' ')
        for i, p in enumerate(reader.pages, start=1))


def page_at(text, pos):
    pages = PAGE.findall(text, 0, pos)
    return int(pages[-1]) if pages else None


def credit_range(raw):
    nums = [int(n) for n in re.findall(r'\d+', raw)]
    return min(nums), max(nums)


def listing_courses(name):
    text = pdf_text(name)
    matches = list(ENTRY.finditer(text))
    courses = []
    for m, nxt in zip(matches, matches[1:] + [None]):
        body = text[m.end(): nxt.start() if nxt else len(text)]
        body = PAGE.sub(' ', body)
        body = re.sub(r'Information listed in this catalog is current as of \S+', ' ', body)
        body = re.sub(r'(CS - Computer Science|IS - Information Sciences)\s+\d+', ' ', body)
        flat = ' '.join(body.split())
        prereq = re.search(r'Prerequisite: (.+?\.)(?: |$)', flat)
        credits = ' '.join(m[4].split())
        lo, hi = credit_range(credits)
        courses.append({
            'code': f'{m[1]} {m[2]}',
            'title': ' '.join(m[3].split()),
            'credits_text': credits,
            'credits_min': lo,
            'credits_max': hi,
            'prerequisite': prereq[1] if prereq else None,
            'source': {'document': name, 'page': page_at(text, m.start())},
        })
    return courses


def supporting_courses():
    text = pdf_text(CATALOG)
    rows = collections.defaultdict(collections.Counter)
    first_page = {}
    for m in ROW.finditer(text):
        code = f'{m[1]} {m[2]}'
        rows[code][(m[3].strip(), m[4])] += 1
        first_page.setdefault((code, m[3].strip(), m[4]), page_at(text, m.start()))
    courses = []
    for code in SUPPORTING:
        if not rows[code]:
            raise SystemExit(f'{code} not found in {CATALOG}')
        (title, credits), _ = rows[code].most_common(1)[0]
        courses.append(_supporting(code, title, credits,
                                   first_page[(code, title, credits)]))
    for code, (title, credits, page) in MANUAL.items():
        courses.append(_supporting(code, title, credits, page))
    return courses


def _supporting(code, title, credits, page):
    lo, hi = credit_range(credits)
    return {
        'code': code,
        'title': title,
        'credits_text': credits,
        'credits_min': lo,
        'credits_max': hi,
        'prerequisite': None,
        'source': {'document': CATALOG, 'page': page},
    }


def main():
    courses = {}
    for name in LISTINGS:
        for c in listing_courses(name):
            courses.setdefault(c['code'], c)
    for c in supporting_courses():
        courses.setdefault(c['code'], c)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(
        sorted(courses.values(), key=lambda c: c['code']), indent=1) + '\n')
    print(f'Wrote {len(courses)} courses to {OUT}')


if __name__ == '__main__':
    main()
