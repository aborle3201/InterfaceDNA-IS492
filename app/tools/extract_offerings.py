"""Extract which courses are offered each term from the Course Explorer schedule
PDFs in "University docs/" into app/sources/offerings.json.

    pip install pypdf
    python tools/extract_offerings.py          (from app/)

The schedule pages list the courses a department offers in a term. They do not
list sections or each section's part of term (POT).
"""
from __future__ import annotations

import json
import pathlib
import re

from pypdf import PdfReader

APP = pathlib.Path(__file__).resolve().parents[1]
DOCS = APP.parent / 'University docs'
OUT = APP / 'sources' / 'offerings.json'

HEADER = re.compile(r'SCHEDULE / (\d{4}) / (FALL|SPRING|SUMMER|WINTER) / ([A-Z]{2,4})')
RETRIEVED = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{2}), \d{1,2}:\d{2} [AP]M')


def course_titles(text, subject):
    """Course code -> title, joining titles the PDF wrapped onto a second line."""
    titles, last = {}, None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(rf'({subject} \d{{3}}) (.+)$', line)
        if m:
            last = m[1]
            titles[last] = m[2]
        elif last and line and line[0].isalpha() and not line.startswith(('Course', 'Number', 'Title')):
            titles[last] += ' ' + line
            last = None
        else:
            last = None
    return titles


def main():
    terms = {}
    for pdf in sorted(DOCS.glob('*Schedule*.pdf')):
        text = '\n'.join(p.extract_text() or '' for p in PdfReader(pdf).pages)
        head = HEADER.search(text)
        if not head:
            raise SystemExit(f'No Course Explorer header in {pdf.name}')
        year, season, subject = head.groups()
        titles = course_titles(text, subject)
        codes = sorted(titles)
        m, d, y = RETRIEVED.search(text).groups()
        term = f'{season.title()} {year}'
        terms.setdefault(term, {})[subject] = {
            'courses': codes,
            'titles': {c: titles[c].strip() for c in codes},
            'document': pdf.name,
            'url': f'https://courses.illinois.edu/schedule/{year}/{season.lower()}/{subject}',
            'retrieved': f'20{y}-{int(m):02d}-{int(d):02d}',
        }
        print(f'{term:12} {subject:4} {len(codes):3} courses  {pdf.name}')
    OUT.write_text(json.dumps(terms, indent=1) + '\n')
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    main()
