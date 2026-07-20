# AI Content Quality Workflow

A workflow that checks written content (marketing copy, product descriptions,
announcements) against a structured, per-piece quality checklist — length,
required keywords, a call-to-action, banned jargon, and readability — then
automatically applies a small set of deterministic fixes and re-scores the
result so you can see exactly what changed and why.

Built by Amir Sadat as a hands-on prompt-engineering/content-QA project. The
default mode needs **no API key and no network access at all**: every
scorer and every fix is a plain, inspectable Python function, not a model
call. An optional LLM-backed provider is included for real usage later, but
nothing in this repo — including its own test suite — spends any API
credits.

## How it works

1. **Define criteria** for a piece of content: minimum/maximum word count,
   keywords it must mention, at least one required call-to-action phrase,
   and terms it must not contain. See
   [`examples/criteria.json`](examples/criteria.json).
2. **Evaluate** — five independent scorers
   ([`content_qa/criteria.py`](content_qa/criteria.py)) each return a score
   from 0–1: length, keyword coverage, CTA presence, forbidden-term
   compliance, and readability (a from-scratch Flesch Reading Ease
   approximation). A weighted composite score is computed from all five.
3. **Revise** — the default `RulesProvider`
   ([`content_qa/rules_provider.py`](content_qa/rules_provider.py)) applies
   explicit fixes: strips forbidden terms, appends a missing call-to-action,
   and trims over-length content at a sentence boundary (never mid-sentence)
   to fit the word budget.
4. **Re-evaluate** — the revised text is scored again so you can see the
   before/after delta.

### A note on what "revise" can and can't do

The rules-only provider can only make content **shorter, cleaner, and more
compliant** — it can strip banned terms, add a missing CTA, and trim
length. It cannot invent new content to fix a draft that's *too short* or
lacks a required keyword the draft never touched on; that's a genuine
limitation of a deterministic, non-generative approach, and it's better to
be upfront about that than to fake it. An optional
[`LLMProvider`](content_qa/llm_provider.py) with the same interface is
included for cases where real content generation is actually needed — see
below.

## Setup

```bash
git clone https://github.com/amirsadat1980-lgtm/ai-content-quality-workflow.git
cd ai-content-quality-workflow
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements-dev.txt   # pytest only — the workflow itself needs nothing
```

There is nothing to configure for the default mode — no `.env`, no API key.

## Usage

Run the bundled example content pieces through the full evaluate → revise →
re-evaluate pipeline:

```bash
python -m content_qa.cli run
```

This prints a Markdown comparison table and writes
`results/sample_report.md` / `.json`. A version generated this way is
already committed in [`results/`](results/) so you can see the output
without running anything.

Run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

### Optional: the LLM-backed provider

For real content generation/revision (not just rule-based cleanup):

```bash
pip install -r requirements-optional.txt
cp .env.example .env   # add your own OPENAI_API_KEY — never commit this file
python -m content_qa.cli run --provider llm
```

This is optional and untested by the automated suite here — it makes real,
billed API calls, so it's never invoked by the tests, the CLI's default
mode, or anything in CI.

## Project structure

```
content_qa/
  criteria.py         # QualityCriteria + the 5 scoring functions
  rules_provider.py     # default deterministic revise() — no API needed
  llm_provider.py        # optional real-model revise(), same interface
  prompts.py               # loads the reusable prompt templates below
  prompts/
    revise_system.txt        # system prompt used by llm_provider.py
    revise_user.txt            # user prompt template (criteria filled in)
  workflow.py           # evaluate -> revise -> re-evaluate orchestration
  loaders.py             # reads examples/criteria.json + input files
  report.py                # Markdown/JSON report builder
  cli.py                     # `python -m content_qa.cli run`
examples/
  criteria.json          # 3 example content pieces + their quality bars
  inputs/                  # the example drafts themselves
results/
  sample_report.md/.json  # committed output of the example run above
tests/                    # 20 tests covering every scorer, the rules
                          # provider's fixes, and end-to-end workflow runs
```

## Known limitations

- Readability, keyword, and forbidden-term checks are heuristic/lexical —
  they don't understand meaning, so a clever paraphrase can slip past a
  forbidden-term check.
- The rules provider can't add missing required content, only remove/trim/
  append fixed text — see above.
- This is a single-piece-at-a-time workflow, not a batch content pipeline
  with versioning or approval steps.

## License

MIT — see [LICENSE](LICENSE).
