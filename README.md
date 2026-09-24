# TrojanAI

TrojanAI is an unofficial USC student-advising research prototype. It uses the
OpenAI Responses API and USC-domain-filtered web search to help answer questions
about transfer pathways, deadlines, registration, course planning, and related
academic processes.

It is designed as a prototype for evaluation and a possible future USC IT pilot.
It is not an official USC service and is not a substitute for an academic
advisor, degree audit, official USC policy, or an admissions decision.

## What it does

- Searches current public USC web pages before answering.
- Produces a consistent answer format with assumptions, key details, sources,
  next steps, notes, and one focused follow-up question when needed.
- Reviews the draft for directness, factual support, specificity, context, and
  actionability.
- Performs one bounded repair and re-review when the draft has unresolved issues.
- Keeps recent conversation context so follow-up answers can use prior questions
  and clarifications.
- Shows citations, research date, request count, and usage information.

## Prototype limitations

- This is not an official USC system.
- It searches public `usc.edu` pages only. It cannot access campus-only websites,
  STARS, WebReg, student accounts, private portals, or medical records.
- It cannot submit forms or act on a student's account.
- Model answers and automated review scores are not guaranteed to be accurate.
- The project has not completed USC IT security, privacy, FERPA, accessibility,
  procurement, or production-readiness review.
- Questions, recent conversation, and optional academic context are sent to
  OpenAI. Do not submit passwords, USC IDs, API keys, or other sensitive data.
- OpenAI model and web-search usage may incur charges.

## Setup

Use Python 3.10 or later.

```bash
cd trojan-ai-v6
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY='your-api-key'
python3 -m streamlit run app.py
```

For local development without exporting the key every time, create
`.streamlit/secrets.toml` inside `trojan-ai-v6`:

```toml
OPENAI_API_KEY = "your-api-key"
```

Never commit that file. For deployment, use the host's approved secrets manager.

## Model and cost

The default model is `gpt-5.5`. Override it with:

```bash
export TROJAN_AI_MODEL='model-name'
```

Review mode normally uses two model requests and can use up to four if a repair
and re-review are needed. Web searches and model tokens are billed by OpenAI.
Turn off **Research + review + repair** for a single unreviewed draft when
appropriate; the UI labels that answer as unreviewed.

## Tests and evaluation

Run the deterministic tests from `trojan-ai-v6`:

```bash
python3 -m unittest -v test_engine.py test_ui.py
```

The optional live evaluator requires an API key and can incur charges:

```bash
python3 evaluate.py --limit 1
python3 evaluate.py --limit 8 --output evaluation-all.json
```

The live evaluation cases cover deadlines, special sessions, internal transfer,
course planning, D-clearance, credit overlap, private records, and false
admission guarantees. Automated scores are not independent human validation;
inspect every cited source before drawing conclusions.

## Project structure

```text
.
├── architecture.html       Plain-language architecture overview
├── trojan-ai-v6/
│   ├── app.py               Streamlit user interface
│   ├── engine.py            Research, citations, review, repair, and formatting
│   ├── evaluate.py          Opt-in live evaluation runner
│   ├── test_engine.py       Engine tests with mocked API responses
│   ├── test_ui.py           Streamlit UI tests
│   ├── EVALUATION.md        Evaluation scope and limitations
│   ├── README.md            Detailed setup notes
│   └── requirements.txt     Python dependencies
```

## Potential USC IT pilot work

A pilot would need USC IT and relevant university stakeholders to define approved
hosting, secret management, authentication, internal-network retrieval, data
retention, access controls, rate limits, logging, accessibility, human escalation,
and a source-verified evaluation protocol. Internal USC websites would require a
separate approved retrieval service inside the USC network; OpenAI's public web
search cannot access campus-only pages.

## License and status

No production license or USC endorsement is implied by this repository. Choose a
license and complete institutional review before distributing or deploying it.
