# Pilot scope: capabilities and limitations

This document describes what the current TrojanAI prototype can and cannot do.
It is intended for technical, security, privacy, and advising stakeholders
reviewing a possible USC IT pilot.

## What the prototype can do today

### Answer USC advising questions

The application can research and explain public USC information for questions
such as:

- Internal transfer pathways and eligibility requirements
- Transfer preparation and prerequisite planning
- Drop, withdrawal, refund, and transcript deadlines
- Special-session deadline questions
- Registration errors and D-clearance processes
- Course overlap, transfer credit, residency, and applicability questions
- Advising-office responsibilities and public contact instructions
- Questions where the student needs to know what information to check next

It is designed to give a safe general answer when a student has not supplied
enough detail, then ask one focused follow-up question such as target major,
term, course session, catalog year, or student category. The next message uses
the previous conversation and the new clarification as context.

### Research public USC sources

Each research request uses the OpenAI Responses API with web search restricted
to `usc.edu` domains. The model is instructed to open relevant official pages,
check the applicable year/session, distinguish related policy milestones, and
avoid treating search snippets as proof.

The interface displays source links and identifies sources as official USC or
external. Source annotations and URLs are checked before they are displayed.

### Review and repair answers

When review mode is enabled, the application performs a second model request to
check the draft for:

- Directness: does it answer the student's actual question?
- Factual support: do important claims have appropriate evidence?
- Specificity: are dates, requirements, offices, and actions concrete?
- Context: does it use the student's supplied facts and correct term/session?
- Actionability: can the student realistically act on the next steps?

If the review finds a problem, the application performs one repair request and
then checks the repaired answer once more. Unresolved issues remain visible to
the student instead of being silently removed.

### Keep a consistent answer format

The model returns structured fields and Python renders them into a stable layout:

1. Answer
2. Assumptions
3. Key details and sources
4. What to do next
5. Important notes
6. One follow-up question, when needed

The renderer removes empty list items and duplicate numbering before displaying
the result.

### Support prototype evaluation

The repository includes mocked engine and Streamlit UI tests. The optional live
evaluator contains cases for deadlines, special sessions, internal transfer,
course planning, D-clearance, credit overlap, private records, and misleading
admission premises.

## What it cannot do today

### No private USC-system access

The prototype cannot access or look up:

- STARS reports
- WebReg or registration accounts
- USC applicant or student portals
- Degree audits or account holds
- Campus-only websites
- Private department systems
- Financial-aid records
- Medical or disability records

It cannot log in, bypass authentication, use a student's session cookies, submit
forms, register for classes, change a major, or take any action on a student's
account.

Campus VPN access on the student's computer does not give OpenAI's hosted web
search access to internal USC pages. Supporting internal sources would require a
separately approved retrieval service running inside the USC network, with its own
authentication, authorization, logging, and data-handling controls.

### No authoritative decision-making

The prototype does not:

- Grant admission or determine eligibility
- Produce an official degree audit
- Guarantee a course seat, graduation date, or transfer outcome
- Replace an advisor, registrar, admissions office, or department decision
- Guarantee that a deadline is correct merely because a citation is present

An official USC page and the responsible office remain authoritative.

### No guarantee of model accuracy

The model may misunderstand a policy, choose the wrong session, miss an
exception, cite an outdated page, or provide an incomplete plan. The automated
review is another model judgment, not independent human verification. A passing
score is a quality signal, not proof of correctness.

The fail-closed checks catch some obvious problems, including missing official
citations and missing dates for many deadline questions. They cannot prove that
every sentence is correct.

### Public-source and search limitations

The current search path is limited to public `usc.edu` domains. It does not have
approved access to internal USC sources, and it does not claim that public USC
marketing or overview pages represent community consensus. Search results and
page content can change after an answer is generated.

### No production controls yet

The prototype does not yet provide the controls expected for an institutional
service, including:

- USC single sign-on or role-based access control
- Centralized secrets management
- Per-user quotas and budget limits
- Production monitoring and alerting
- Audit-log policy approved by USC
- Formal incident response and abuse handling
- Approved data-retention and deletion controls
- Human escalation workflow
- Accessibility certification or formal usability study
- Service-level objectives, backup, and disaster recovery
- USC-approved internal retrieval for campus-only content

## Data and privacy boundaries

The application sends the current question, recent conversation, optional student
profile, current Los Angeles date, and relevant research context to OpenAI. The
prototype uses `store=False`, but that setting is not a guarantee of zero provider
retention. The application should not receive passwords, USC IDs, API keys,
medical information, or unredacted account records.

The local UI does not intentionally write chat history or API keys to disk. Local
development secrets belong in environment variables or ignored Streamlit secrets.
Production secrets should be supplied by USC-approved infrastructure.

## Recommended pilot boundaries

An initial pilot should be limited to informational questions based on public USC
sources. It should:

1. Display a clear unofficial-prototype notice.
2. Require students to verify consequential dates and decisions with the linked
   official source or responsible USC office.
3. Exclude private-record lookups and account actions.
4. Avoid collecting direct identifiers and sensitive academic records.
5. Record only the minimum operational data approved by USC stakeholders.
6. Measure citation correctness, missed exceptions, clarification quality,
   harmful overconfidence, cost, latency, and user outcomes.
7. Include human review of representative answers before expanding scope.

## USC IT review needed before broader use

Before a broader pilot or deployment, USC IT and relevant university stakeholders
should approve the hosting model, OpenAI account and data settings, secret
management, data classification, retention/deletion rules, accessibility,
authentication, logging, rate limits, cost controls, internal-source architecture,
human escalation, and release acceptance criteria.
