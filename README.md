# Contract Authoring Agent (Track A)
Deployed URL- https://zycus-contract-agent.streamlit.app/

An agentic system that drafts a Mutual NDA from structured business inputs,
flags anything missing, ambiguous, or non-standard, and routes each flag
to either auto-resolve or human review — never silently guessing on
anything that changes a party's rights.

## Architecture

```
Business inputs
      │
      ▼
┌─────────────────────┐   deterministic rules
│  1. Validator Agent │──────────────────────►  list[Flag]
└─────────────────────┘   (payment N/A? date open? non-standard clause?)
      │
      ▼ (only if a judgment-requiring flag exists)
┌─────────────────────┐   LLM call (Claude)
│  2. Drafting Agent   │──────────────────────►  bounded clause language
└─────────────────────┘   + plain-English rationale
      │
      ▼
┌─────────────────────┐   deterministic string templating
│  3. Template Fill    │──────────────────────►  filled sections
└─────────────────────┘
      │
      ▼
┌─────────────────────┐   deterministic tool (python-docx)
│  4. Docgen Tool      │──────────────────────►  NDA_Draft.docx
└─────────────────────┘
```

**Why split it this way:** anything that's pure data substitution (party
names, dates, term length) is deterministic — an LLM has no business
"creatively" filling in a defined field, and doing it deterministically
means that half the pipeline literally cannot hallucinate. The **only**
LLM call in the system is for the one thing that actually requires
judgment: drafting bounded replacement language for a clause that was
requested but is broader than standard practice.

## Confidence / uncertainty model

Every flag carries three independent fields — deliberately *not* one
blended confidence score:

| Field | Meaning |
|---|---|
| `resolution` | `auto_resolve` / `needs_human_review` |
| `confidence` | how sure the agent is about what it detected |
| `category` | `formatting` vs `scope_of_rights` |

**Rule:** high confidence about *what was asked* never authorizes
auto-inserting language that changes *what either party is agreeing to*.
A `scope_of_rights` flag always routes to human review regardless of
confidence score. Only pure `formatting` issues (missing date, N/A field)
are eligible for auto-resolve. See `agents/validator.py` for the full
rationale — it's written as a docstring above the function.

## Project structure

```
inputs.py              # business inputs (sample pack, hardcoded for this assignment)
templates/nda_template.py   # NDA template as structured sections
agents/validator.py    # deterministic rule checks + confidence routing
agents/llm_client.py   # single wrapper around the Anthropic API
agents/drafter.py      # LLM-drafts the one clause that needs judgment
agents/docgen.py       # deterministic docx generation
pipeline.py            # orchestrates all four stages
app.py                 # Streamlit UI
```

## Setup

```bash
git clone <your-repo-url>
cd zycus-contract-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then paste your real ANTHROPIC_API_KEY into .env
streamlit run app.py
```

## Deploying (Streamlit Community Cloud — free, fastest path)

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io → "New app" → pick your repo/branch → main file `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Deploy. You'll get a public `*.streamlit.app` URL — that's your live link.

## Known limitation / what would break with more time

The template-fill step assumes every placeholder in the template has a
matching key in the resolved inputs dict — if a future template added a
new bracketed field without a corresponding input, `str.format()` would
raise a `KeyError` at generation time rather than degrading gracefully.
For a 3-hour scope this is an acceptable, explicit trade-off, but a
production version would validate the template's placeholder set against
the input schema before attempting to fill it.
