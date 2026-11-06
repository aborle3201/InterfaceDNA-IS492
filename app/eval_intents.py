"""Evaluate live intent/entity extraction against prompts/intent_eval.json.
Makes one real Groq call per case (needs GROQ_API_KEY in app/.env).

Run from app/:  python eval_intents.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

from server import classify_live

CASES = json.loads(
    (pathlib.Path(__file__).parent / 'prompts' / 'intent_eval.json').read_text())


def main():
    passed, totals, failures = Counter(), Counter(), []
    tokens = 0
    for case in CASES:
        totals[case['kind']] += 1
        try:
            intent, entities, _, usage = classify_live(case['message'])
            tokens += (usage['input_tokens'] or 0) + (usage['output_tokens'] or 0)
        except Exception as exc:  # noqa: BLE001 - report every failure kind
            failures.append((case, f'error: {exc}'))
            continue
        course = entities.get('course_code')
        wanted = case.get('entities', {})
        if (intent == case['intent'] and course == case['course_code']
                and all(entities.get(k) == v for k, v in wanted.items())):
            passed[case['kind']] += 1
        else:
            failures.append((case, f'got intent={intent} entities={entities}'))
        time.sleep(12)  # Groq free tier: 8,000 tokens/min at ~1,700 tokens/call

    for case, why in failures:
        print(f'FAIL {case["id"]} {case["message"]!r}\n'
              f'     expected intent={case["intent"]} '
              f'course_code={case["course_code"]}; {why}')
    print()
    for kind in totals:
        print(f'{kind:12} {passed[kind]}/{totals[kind]}')
    total = sum(passed.values())
    print(f'{"overall":12} {total}/{len(CASES)} '
          f'({100 * total / len(CASES):.0f}%), {tokens} tokens')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
