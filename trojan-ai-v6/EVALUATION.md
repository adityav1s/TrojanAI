# Evaluation record — Revision 6.1

## Evidence and scope

The supplied screenshot was manually reviewed. It fails the intended usefulness
standard because it omits an actual deadline, blurs different drop milestones,
and delegates the main lookup to the student. Its policy accuracy cannot be
established from its collapsed source panel. No fabricated replacement dates were
added to the code to make the demo appear successful.

The code now encodes the following acceptance criteria:

| Dimension | Full-credit answer |
|---|---|
| Directness | Answers the actual decision or date first, or gives a justified conditional answer. |
| Factual support | Current applicable official pages directly support important claims; uncertainty is disclosed. |
| Specificity | Exact dates/courses/contacts where verifiable; relevant distinctions and exceptions remain intact. |
| Context | Uses supplied facts, correct date/year/session and explicit assumptions without inventing personal facts. |
| Actionability | Gives feasible next steps and at most one necessary clarification, not generic referral. |

Each dimension is scored 0–2 by a separate model request. Target is >=9/10,
factual support 2/2, and no blockers. This is an automated gate, not a measured
human quality score. Same-model reviewer errors can correlate with author errors.

## Completed tests

19/19 deterministic tests passed on 2026-09-21:

- Los Angeles date conversion and explicit profile/follow-up context.
- Missing database is not created; legacy reads stay optional.
- URL scheme and USC hostname boundary checks.
- Citation span conversion to clickable links.
- Invalid review JSON fails closed; score cannot override a blocker.
- Missing calendar date/citations override an otherwise passing review.
- Passing answers take two requests; repair and re-review take four.
- Repeated failures stop after one repair and show warnings.
- Review-off mode is explicitly disclosed.
- Token counters, tool limits, store=False and incomplete-response rejection.
- Streamlit no-key startup, mocked response submission, source preservation on
  rerun and clearing conversation.

Mock dates and answers in unit tests are synthetic fixtures, NOT USC facts.
An initial UI test exposed a development-environment SOCKS dependency issue;
the optional dependency was installed, and the UI test isolates client creation
so it cannot accidentally contact or charge the API.

## Not completed / not claimed

- No real model answer was generated from this app during development: no API key.
- No end-to-end official-source accuracy, average cost or latency measurement.
- No independent human verification of the revised app's live answers.
- No 9/10 or 10/10 product-quality claim.

## Live evaluation protocol

Run evaluate.py for one case first, then examine every linked official page.
The eight cases cover drop deadlines, nonstandard sessions, internal transfer,
personalized course planning, D-clearance, overlap, private-record access and a
false guarantee premise. Each result includes its case-specific human checklist.

For every important claim record: claim, supporting URL, policy/session/year,
whether the page directly supports it, and any correction. A high model score
does not rescue a wrong date or missing requirement. Repeat failing cases after
changes and also re-run other categories to check for regressions. Test real
multi-turn conversations as well as these standalone profile-based cases.

Release acceptance requires human-confirmed source correctness on these cases,
not simply longer answers or passing mock tests. If a page is inaccessible, the
answer must acknowledge the specific gap and give a safe next check.
