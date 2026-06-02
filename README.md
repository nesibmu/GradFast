# VisaFlow

VisaFlow is an AI operations assistant for international-student bureaucracy. It turns messy administrative emails and checklists into structured next steps: extracted deadlines, requested documents, action items, prioritized tasks, and ready-to-use response artifacts.

## Project track

Automation / Agent Systems

## Problem

International students often deal with fragmented administrative workflows across housing, immigration, and financial aid. Important details are spread across emails, checklists, portals, and follow-up reminders. The cost of missing one deadline or document can be high, but the messages themselves are often repetitive, vague, and hard to operationalize quickly.

VisaFlow is built to reduce that friction. Instead of just reading the message, the system converts it into a workflow someone can actually act on.

## Core idea

The main idea is simple: treat administrative communication as operational input.

Given an email or text document, VisaFlow:
1. extracts deadlines, requested documents, and action items
2. attaches confidence scores and supporting evidence
3. builds a task plan with urgency, dependencies, and workflow tags
4. generates output artifacts that are useful in practice

The project focuses on making the result understandable, actionable, and demo-ready rather than building a deployed production system.

## What the product does

VisaFlow currently supports:

- deadline extraction
- requested document extraction
- action item extraction
- evidence mapping
- confidence scoring
- workflow tagging
- prioritized task planning
- blocked task explanations
- urgency ranking
- weak-input fallback handling
- presenter-friendly output generation

## Main outputs

For a given input, VisaFlow can produce:

- Short Summary
- Task Digest
- Full Summary
- Email-Ready Reply
- Baseline Draft
- Enhanced Draft
- Checklist
- Operations Handoff

## Demo modes

The app includes:

- Presenter Mode
- Minimal View
- Comparison Mode
- Quick Launch Presets
- Guided Demo Support
- Final Demo Checklist
- Best Demo Comparison Guidance

## Main presets

- **Mixed admin case** — strongest default demo
- **Escalated admin case** — denser multi-deadline case
- **Housing follow-up** — simpler walkthrough case
- **Financial aid review** — sentence-based document extraction case
- **Immigration update** — workflow-tagging case
- **Weak noisy case** — robustness and fallback case

## How it works

### 1. Ingestion
VisaFlow loads sample files, pasted text, or uploaded `.txt` inputs and normalizes the text before processing.

### 2. Extraction
The system identifies:
- deadlines
- requested documents
- action items

It also tries to normalize repeated document variants such as different ways of referring to a passport copy or I-20.

### 3. Evidence and confidence
Each extracted item is paired with a supporting snippet and a confidence score so the result is easier to inspect.

### 4. Planning
The extracted items are converted into a structured task plan. Tasks can be tagged as:
- urgent
- ready
- blocked

The planning layer also tracks dependencies, adds blocked-task explanations, and applies a lightweight urgency score for ordering.

### 5. Output generation
The final stage turns the plan into different artifacts depending on use case:
- compact updates
- operational handoffs
- email-style replies
- longer summaries

## Why this is useful

VisaFlow is useful in cases where someone needs to move from “I got an email” to “I know exactly what I need to do next.”

Possible use cases:
- students handling time-sensitive university communication
- advisors or support staff triaging incoming administrative requests
- operations workflows built on top of email-heavy bureaucratic processes
- future agents that coordinate reminders, follow-ups, and document collection

## Evaluation and evidence

This project was evaluated mainly through functional iteration and workflow behavior rather than large-scale benchmark results.

Evidence of progress includes:
- a public GitHub repository with commit history
- a working local Streamlit application
- multiple structured demo presets
- comparison between strong structured cases and weak/noisy cases
- explicit fallback handling for incomplete input
- iterative improvements to extraction, planning, and artifact quality

The current version is strongest as a local demo prototype and workflow artifact generator.

## Limitations

Current limitations include:
- rule-based extraction still misses some edge cases
- confidence scores are heuristic rather than learned
- support is focused on text inputs rather than PDFs, screenshots, or full portal integration
- no live deployment or authenticated university data integration
- evaluation is still lightweight and mostly demo-driven

## What I would add next

If I continued the project, I would prioritize:
- better multi-document and multi-message context handling
- stronger retrieval over full email threads
- richer document and portal integration
- learned or hybrid extraction models
- user testing with real student workflows
- automatic reminder and follow-up actions

## Run locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

## Repository structure

- `app.py` — main Streamlit app
- `visaflow/extraction/` — extraction, normalization, evidence selection
- `visaflow/planning/` — workflow planning, dependencies, urgency ordering
- `visaflow/drafting/` — summaries, drafts, task digest, checklist, handoff outputs
- `visaflow/ingestion/` — input loading
- `data/samples/` — sample text inputs
- `tests/` — lightweight validation tests

## AI usage and disclosure

AI tools were used in the development of this project, and this README is intended to disclose that clearly.

AI assistance was used for:
- brainstorming implementation directions
- drafting and revising parts of the UI copy
- debugging specific code issues
- refactoring and cleanup suggestions
- generating and refining some tests
- helping structure documentation and presentation materials

I still made the project-level decisions myself, including:
- choosing the problem and project direction
- deciding the product scope
- selecting which features to keep or cut
- integrating and editing the code in the repository
- choosing the presets, outputs, and demo flow
- reviewing and testing the final behavior locally

In other words, AI was used as a development assistant, not as a substitute for the underlying project work or final judgment.

## Final state

This repository is the final local demo version of VisaFlow for CS 153. It is optimized for:
- local demonstration
- preset-driven walkthroughs
- comparison of strong and weak cases
- exportable workflow artifacts

It is not intended to be a deployed production system.
