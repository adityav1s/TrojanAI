"""Opt-in live evaluation. Requires a key; never run automatically by the UI."""
import argparse
from getpass import getpass
import json
import os
from pathlib import Path
from openai import OpenAI
from engine import answer

CASES = [
    {'name':'drop_deadline','question':'When is the last day to drop my courses if I think the course will hurt my GPA?',
     'check':'Exact year/session assumption; separate refund/no-W/W dates; GPA versus transcript; passed deadlines; one focused follow-up.'},
    {'name':'special_session','question':'My class starts in October and lasts eight weeks. Does the regular drop deadline apply?',
     'check':'Do not apply standard semester dates. Identify session-specific check and ask course/session, not private IDs.'},
    {'name':'internal_transfer','question':'I am a Philosophy major. Exactly how do I transfer into Computer Science?',
     'check':'Current official pathway, review courses, GPA/grades, AP exceptions, timing, eligibility versus guarantee, denial policy, office.'},
    {'name':'personalized_followup','question':'What should I take next semester if I want to avoid physics?',
     'profile':'HTI freshman, CSCI 102 in progress, AP Calculus AB score 4. Interested in internal transfer to CS.',
     'check':'Use supplied facts; distinguish qualifying alternatives from degree requirements; no invented completed AP Biology credit or seats.'},
    {'name':'clearance','question':'WebReg says I need D-clearance for a CS course. Who actually approves that and how do I request it?',
     'check':'Verified CS department process/contact. Distinguish clearance from prerequisite completion; request course if needed.'},
    {'name':'credit_overlap','question':'Can the same classes count toward both my HTI major and a CS minor?',
     'check':'Verify both university and program rules; do not invent overlap cap; ask catalog year if decisive.'},
    {'name':'private_record','question':'Look up my STARS report and tell me exactly what credits I am missing.',
     'check':'Admit no account access. No fabricated audit or request for credentials. Explain safe redacted information needed.'},
    {'name':'false_premise','question':'My friend said meeting the transfer GPA guarantees CS admission. Is that true?',
     'check':'Research rather than accept premise; cite explicit official eligibility/admission wording.'},
]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int,default=1,choices=range(1,len(CASES)+1))
    parser.add_argument('--output',default='evaluation-results.json')
    args=parser.parse_args()
    print(f'This runs {args.limit} live test(s). Each may use 4 model calls plus searches; API charges apply.')
    if input('Type RUN to proceed: ').strip() != 'RUN':
        return
    key=os.getenv('OPENAI_API_KEY') or getpass('API key (hidden): ')
    client=OpenAI(api_key=key,timeout=180,max_retries=0)
    output=Path(args.output)
    if output.exists():
        raise SystemExit('Output already exists; use --output with a new filename.')
    results=[]
    for case in CASES[:args.limit]:
        print(case['name'])
        try:
            result=answer(client,case['question'],profile=case.get('profile',''),progress=print)
            results.append({'case':case,'result':result,'human_review':None})
        except Exception as exc:
            results.append({'case':case,'error_type':type(exc).__name__})
        output.write_text(json.dumps(results,indent=2,ensure_ascii=False))
    print(f'Saved {output}. Open every cited page and check the case criteria. Automated scores alone are not proof.')


if __name__=='__main__':
    main()
