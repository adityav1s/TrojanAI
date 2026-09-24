# Trojan AI V6.1 — Research, Review, Repair

This revision targets actionable, source-supported USC advising answers. It does
not claim counselor-level accuracy or a measured 9/10 quality score.

## What changed

- Supplies today's Los Angeles date to every research and review request.
- Requires explicit year/session assumptions and separates refund, no-W and W deadlines.
- Researches live USC pages, then makes a separate fact-checking/review request.
- Reviews directness, factual support, specificity, context and actionability.
- Repairs a failing draft once and rechecks it; unresolved issues remain visible.
- Does not accept a high model score as a pass if basic citation/date checks fail.
- Converts API citation spans into clickable links and preserves sources on reruns.
- Keeps the latest 16 messages plus an optional student-maintained academic profile.
- Shows token/search counts, not a misleading fixed cost per question.
- Optional old database is read-only and treated as historical leads, not current policy.

## Setup

Stop the old app with Control-C. Extract this ZIP into a fresh folder and run from
the extracted `trojan-ai-v6` directory (Finder may add a suffix if one already exists).
The page must say **Revision 6.1**. Do not keep running the old app in another tab.
Use Python 3.10 or later.

```bash
cd ~/Downloads/trojan-ai-v6
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Set the OpenAI API key programmatically before starting Streamlit. Do not put the
key in source code or in a chat message.

```bash
export OPENAI_API_KEY='your-api-key'
python3 -m streamlit run app.py
```

For deployed Streamlit, set `OPENAI_API_KEY` in the deployment secrets/configuration.

## Optional local knowledge database

For previously indexed USC pages, optionally copy your database into this extracted
folder. It is not required. Preserve your original database.

```bash
cp ~/Downloads/trojan-ai-v3/trojan_knowledge.db ~/Downloads/trojan-ai-v6/
```

Live search is restricted to USC domains. This is not a private portal integration,
and it cannot read your STARS report or other account data. Community consensus is
not claimed from official marketing pages.

## Notes

- Live search is always enabled. Review mode is on by default: two model requests,
  or four if repair is needed, with up to 18 total built-in tool calls across the
  full repair path. Output is limited to 7,000 tokens per request including reasoning.
  These are execution bounds, NOT a dollar spending cap. Input/search content costs
  also vary. Disable review for a one-request draft, visibly labeled unreviewed.
- Default model is GPT-5.5. `TROJAN_AI_MODEL` can override it; overrides must
  support Responses API, web_search with domain filtering, and low reasoning.
- Never commit an API key to this project.
- Questions, recent history, and optional profile are sent to OpenAI. The app uses
  `store=False`, but this is not a guarantee of zero provider retention. No chat or
  key is written to disk by the UI. Clear conversation does not erase the profile.

## Tests and honest evaluation status

```bash
python3 -m unittest -v test_engine.py test_ui.py
```

19 tests passed during development, including Streamlit UI tests with mocked API
responses. No live answer-quality evaluation was run: no API key was configured
in the development environment. See EVALUATION.md for limitations and criteria.

To run the first real test with your own API key (charges apply):

```bash
python3 evaluate.py --limit 1
```

The script asks for RUN confirmation and then a hidden key if needed. Start with
one case to measure cost. For all eight cases, use `--limit 8 --output evaluation-all.json`.
It saves answers, links, automated reviews and usage so a human can inspect them.
Send the resulting evaluation JSON for review, not your key. Built-in cases contain
no personal identifiers. Existing output files are not overwritten.
