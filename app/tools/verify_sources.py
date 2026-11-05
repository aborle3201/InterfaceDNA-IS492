"""Check that every quote in sources/policies.json and sources/programs.json
appears verbatim on the cited page of its source PDF in "University docs/".

    pip install pypdf
    python tools/verify_sources.py          (from app/)

"..." in a quote marks omitted text; each remaining fragment must match.
Whitespace, curly quotes and ligatures are normalized before comparing.
Every dated value (e.g. a deadline) must also appear as "Month D" in its quote.
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import date

from pypdf import PdfReader

APP = pathlib.Path(__file__).resolve().parents[1]
DOCS = APP.parent / 'University docs'
LIGATURES = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl',
             '’': "'", 'ʼ': "'", '‘': "'", '“': '"', '”': '"', ' ': ' '}


def norm(text):
    for a, b in LIGATURES.items():
        text = text.replace(a, b)
    return ' '.join(text.split())


def main():
    policies = json.loads((APP / 'sources' / 'policies.json').read_text())
    programs = json.loads((APP / 'sources' / 'programs.json').read_text())
    sources = policies['sources']
    checks = [(k, f['source'], f['page'], f['quote'])
              for k, f in policies['facts'].items()]
    date_failures = 0
    for k, f in policies['facts'].items():
        if isinstance(f.get('values'), list):
            for v in (v for v in f['values'] if 'date' in v):
                d = date.fromisoformat(v['date'])
                if f'{d:%B} {d.day}' not in f['quote']:
                    date_failures += 1
                    print(f'FAIL {k}: date {v["date"]} not in quote')
    for code, prog in programs['programs'].items():
        for i, q in enumerate(prog['quotes']):
            checks.append((f'{code}[{i}]', 'catalog', q['page'], q['quote']))

    readers, failures = {}, 0
    for key, src, page, quote in checks:
        doc = sources[src]['document']
        reader = readers.setdefault(doc, PdfReader(DOCS / doc))
        text = norm(reader.pages[page - 1].extract_text() or '')
        missing = [frag for frag in quote.split('...')
                   if norm(frag) and norm(frag) not in text]
        if missing:
            failures += 1
            print(f'FAIL {key} ({doc} p.{page}): {missing[0][:90]!r}')
        else:
            print(f'ok   {key}')
    print(f'{len(checks) - failures}/{len(checks)} quotes verified')
    return 1 if failures or date_failures else 0


if __name__ == '__main__':
    sys.exit(main())
