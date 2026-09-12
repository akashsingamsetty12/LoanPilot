# Antigravity Prompt — Implement Module 7 (AI Investigation Agent) for LoanPilot

Copy everything below into Antigravity as your task prompt. It's written so the agent explores the existing repo first and matches conventions before writing anything, rather than inventing a parallel style.

---

## PROMPT START

You are working inside the existing `LoanPilot` repository. Your job is to implement **Module 7 — AI Investigation Agent** completely, end to end, while staying consistent with the codebase that already exists for Modules 1–6.

### Step 0 — Orientation (do this before writing any code)

Before writing anything, explore and report back on:
1. The full `backend/` directory tree (`models/`, `routers/`, `schemas/`, `services/`, `utils/`, `tests/`, `config.py`, `database.py`, `main.py`).
2. The existing `backend/services/agent.py`, `backend/routers/agent.py`, `backend/schemas/agent.py` — these are skeleton/stub files already reserved for this module. Read them fully and preserve their existing function/route signatures unless there's a concrete reason to change them (explain any change you make).
3. The existing SQLAlchemy models for `Application`, `Document`, `Verification`, `Risk` in `backend/models/` — read their actual field names, don't assume mine. Use the real schema.
4. How existing routers in `backend/routers/` structure their endpoints — dependency injection pattern for the DB session, error handling style (custom exceptions vs HTTPException), response model usage, and the `/api/v1` prefix convention.
5. How existing services in `backend/services/` are structured — are they class-based or function-based, how do they raise/handle errors, do they use logging, what pattern do successful modules follow.
6. `backend/config.py` — how environment variables and settings are currently loaded (e.g. Pydantic `BaseSettings`), so new config (LLM provider, Bedrock region, model ID, API keys) follows the same pattern instead of introducing a second way of reading env vars.
7. `requirements.txt` / `pyproject.toml` — confirm what's already installed (`boto3` presence, `openai`, `langchain`, `faiss` or `chromadb`) before adding new dependencies.
8. `frontend/src/api/agent.js` and `frontend/src/components/agent/ChatPanel.jsx` — read the existing stub/TODOs and match the existing Axios call patterns, component structure, and Tailwind styling conventions used elsewhere in `frontend/src/components/`.
9. `backend/tests/` — read existing test files to match the pytest fixture style (test DB setup, test client, factory/seed pattern) already used for other modules.

Do not restructure or rename existing files/folders. Do not touch Modules 1–6 business logic. Only integrate with them by reading their models/outputs.

If Modules 3–6 are incomplete, contain TODO/NotImplemented code, or exist on another repository branch, do not implement those modules as part of this task. Use the real existing models/interfaces and create small seeded/demo records behind the Module 7 tools when necessary. Module 7 must remain independently testable.

### Step 1 — Build the provider-neutral LLM client

Create `backend/services/llm_client.py` with a provider-neutral interface:

```python
class LLMClient:
    def chat(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str
    ) -> LLMResponse:
        ...
```

Normalize every provider into one `LLMResponse` model/dataclass:

```python
class LLMResponse:
    stop_reason: str          # "tool_use" | "end_turn"
    tool_calls: list[dict]     # name, args, id
    text: str | None
```

**Critical architecture rule:** `backend/services/agent.py` must consume only this normalized `LLMResponse`. It must never access Bedrock-specific fields such as `response["output"]` or `response["stopReason"]`, or OpenAI-specific response objects. Provider-specific parsing belongs entirely inside `llm_client.py`.

Implement three backends behind this interface, selected via a `LLM_PROVIDER` config value (`bedrock` | `openai` | `local`), following the existing settings pattern found in `config.py`:

1. **BedrockClient (primary)** — uses `boto3`'s `bedrock-runtime` client and the **Converse API** (not raw `invoke_model`) for tool-use support. Model ID must be read from config, not hardcoded. Confirm the exact available model ID against the AWS account/region before assuming any specific model string. Region must be config-driven.
2. **OpenAIClient (secondary fallback)** — reuse whatever OpenAI/LangChain dependency already exists in the repo. It must accept the exact same inputs and return the same normalized `LLMResponse`.
3. **LocalEmergencyClient (last-resort fallback)** — makes zero network calls. It is a deliberately limited deterministic emergency mode, not a pretend full LLM. At minimum support "why was this flagged", "what does policy say about income mismatches" where a known local response is available, approve/reject-style questions, and unknown questions. Approve/reject questions must always be refused.

The local client returns `LLMResponse`; the **orchestrator** is responsible for constructing the final `AgentResponse` including `trace`, `evidence`, and `requires_human_review=True`. Do not put frontend-only fields into `LLMResponse`.

Add `ENABLE_OPENAI_FALLBACK` and `ENABLE_LOCAL_FALLBACK` config flags.

Recommended fallback policy:
- timeout/network failure → fallback
- throttling → fallback
- temporary provider/service-unavailable error → fallback
- invalid model ID → surface a clear configuration error
- invalid credentials/permissions → surface a clear configuration error rather than silently hiding a broken deployment

When fallback occurs, log the provider attempted, failure category, and provider that ultimately served the response using the repository's existing logging setup. Never log secrets or unnecessary applicant PII.

### Step 2 — Implement the five tools

Create `backend/services/agent_tools.py` implementing these functions against the **real** SQLAlchemy models you found in Step 0 (adjust field names to match reality, do not invent fields):

- `get_application_data(application_id: str, db: Session) -> dict`
- `get_verification_results(application_id: str, db: Session) -> dict`
- `get_risk_flags(application_id: str, db: Session) -> dict`
- `get_flag_evidence(application_id: str, flag_id: str, db: Session) -> dict`
- `search_policy(query: str) -> dict`

The first four functions receive the existing SQLAlchemy `Session` explicitly using the same dependency/session pattern already used elsewhere in the repo. Do not create ad hoc DB sessions inside the tools. `search_policy()` uses the local RAG index and does not need a DB session.

Each must:
- Return `{"error": "..."}` in a consistent shape if the application/flag isn't found, rather than raising — the orchestrator needs to be able to feed this back to the LLM as a tool result so it can react (e.g. say "I don't have that information").
- Never raise unhandled exceptions back to the orchestrator loop.

Build a `TOOL_REGISTRY = {"get_application_data": get_application_data, ...}` dict mapping tool name → callable, and a separate `TOOLS` list containing the JSON tool-use schemas (name, description, input_schema) matching Bedrock Converse tool format.

When the orchestrator executes a DB-backed tool, pass the already-created `db` session explicitly, for example:

```python
result = TOOL_REGISTRY[name](db=db, **args)
```

Never create a second session inside `agent_tools.py`.

Use these exact five tool descriptions (edit only if the real field names require it):

```
get_application_data: "Retrieve basic applicant and loan information for an application... Call this first if you need general context about who the applicant is."
get_verification_results: "Retrieve cross-document verification results for an application, including any mismatches found between documents... Call this when the question is about discrepancies or inconsistencies."
get_risk_flags: "Retrieve the risk score, risk level, and specific risk flags raised for an application. Call this when asked why an application was flagged or what its risk level is."
get_flag_evidence: "Retrieve the specific source documents, page numbers, and extracted values that support a given risk flag. Always call this before citing evidence for a specific flag — never state document/page evidence without calling this first."
search_policy: "Search lending policy documents for guidance relevant to a situation. Call this when the officer asks what policy says, or when recommending a next action."
```

### Step 3 — Policy RAG

Create `backend/services/policy_rag.py`:
- Write 3–5 short policy documents (plain markdown or text, ~½ page each) in a new `backend/data/policies/` directory: Income Verification Policy, Underwriting Guidelines, Loan Documentation SOP, Risk Assessment Guidelines, Address Verification Policy. Write real, sensible policy content — don't leave placeholders.
- Chunk each by paragraph.
- Embed chunks at build time or first startup. Prefer a provider already available in the repo. Bedrock Titan Embeddings may be used when available; OpenAI embeddings may be used as a build-time fallback.
- Persist the resulting FAISS/Chroma index and embeddings locally.
- After the index has been successfully built, `search_policy()` must make **zero network calls at query time**. A policy query must continue working if the internet and all remote LLM providers are unavailable.
- If the index does not exist, build it once and clearly report any embedding-provider/configuration failure. Do not rebuild embeddings for every query.
- Check `requirements.txt` before adding dependencies and prefer existing libraries.
- Implement `search_policy(query: str, k: int = 3) -> dict` returning `{"chunks": [{"text", "source", "section"}]}`.

### Step 3A — Required fallback architecture

Implement provider resilience as:

```text
                 Agent Orchestrator
                         |
                  LLMClient Interface
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Bedrock        OpenAI          Local
       PRIMARY       FALLBACK       EMERGENCY
          |              |              |
          +--------------+--------------+
                         |
                   LLMResponse
                         |
                   AgentResponse
```

Normal priority:

```text
Bedrock → OpenAI → Local Emergency
```

If `LLM_PROVIDER=bedrock`:
1. Try Bedrock.
2. On a recoverable runtime failure, try OpenAI if enabled.
3. If OpenAI also fails, use local emergency mode if enabled.
4. If no fallback is enabled, return a safe human-review response rather than a 500.

If `LLM_PROVIDER=openai`, use OpenAI as the primary configured provider and local emergency mode as the fallback if enabled.

If `LLM_PROVIDER=local`, do not make any remote calls.

The frontend must receive the same `AgentResponse` schema regardless of provider.

The local emergency mode must always set:

```json
{
  "requires_human_review": true
}
```

It must never fabricate:
- applicant facts,
- document values,
- risk scores,
- evidence,
- policy passages,
- approval/rejection decisions.

---

### Step 4 — Orchestration loop

Implement/replace `backend/services/agent.py`'s core function (keep its existing name/signature if one already exists from the skeleton):

```python
def run_agent(application_id: str, question: str, db: Session) -> AgentResponse
```

Requirements:
- System prompt must explicitly enforce: (1) never answer without calling a tool first, (2) never state evidence without having called `get_flag_evidence`, (3) never recommend approve/reject — always redirect to human underwriter, (4) ground recommendations in a policy passage from `search_policy` when possible, (5) say "I don't have that information" rather than guessing when tools don't return what's needed.
- Loop capped at `MAX_TURNS = 5` (config-driven). On each turn, call the provider-neutral `llm_client.chat(...)`. The orchestrator must inspect only `LLMResponse.stop_reason`, `LLMResponse.tool_calls`, and `LLMResponse.text`.
- If `stop_reason == "tool_use"`, execute each requested tool via `TOOL_REGISTRY`. For DB-backed tools, inject the existing `db` session. Inject `application_id` into arguments server-side (never trust an LLM-supplied application_id — always overwrite it with the one from the authenticated request).
- Append tool results to the provider-neutral conversation format and continue the loop. If `stop_reason == "end_turn"`, parse the final text into the structured `AgentResponse` schema and return.
- Every tool call executed must be appended to a `trace` list with `step`, `tool`, `args`, and a short `summary` string.
- If `MAX_TURNS` is exceeded without a final answer, return a safe fallback response with `requires_human_review=True` and whatever trace was gathered — never crash the endpoint.

### Step 5 — Output schema and validation

In `backend/schemas/agent.py` (extend the existing skeleton rather than replacing it if fields already exist), define:

```python
class EvidenceItem(BaseModel): document: str; page: int; value: str
class TraceStep(BaseModel): step: int; tool: str; args: dict; summary: str
class AgentResponse(BaseModel):
    answer: str
    risk_level: Optional[str] = None
    evidence: list[EvidenceItem] = []
    policy_reference: Optional[str] = None
    recommendation: Optional[str] = None
    requires_human_review: bool = True
    trace: list[TraceStep] = []
```

If the LLM's final text doesn't parse into this schema, retry once with a repair instruction appended to the conversation ("Your previous response was not valid JSON matching the required schema. Return only valid JSON matching the required schema."). If the second attempt also fails, return a safe fallback with `requires_human_review=True` rather than a 500 error.

Do not erase a valid trace merely because the final structured response failed to parse. Preserve the trace already gathered where possible.

### Step 6 — API endpoint

In `backend/routers/agent.py`, wire `POST /api/v1/applications/{id}/agent` to accept `{"question": str}`, call `run_agent(application_id, question, db)`, and return `AgentResponse`. Match the existing error-handling and dependency-injection conventions found in Step 0 (e.g. how other routers handle a 404 for unknown `application_id`).

### Step 7 — Frontend integration

In `frontend/src/api/agent.js`, implement the Axios call to the endpoint above, matching the existing API module patterns in the repo (base URL, error handling, response typing if TypeScript/PropTypes are used elsewhere).

In `frontend/src/components/agent/ChatPanel.jsx`, replace the TODOs to:
- Send the officer's question and display the returned `answer`.
- Render a collapsible **"Agent Reasoning"** panel showing the `trace` array (tool name, args, summary) in order.
- Render an **"Evidence"** section listing each `evidence` item (document, page, value).
- Render `policy_reference` and `recommendation`, with a visible badge/label when `requires_human_review` is true.
- Match the existing Tailwind styling conventions and component patterns used by sibling components in `frontend/src/components/` (don't introduce a new visual style).

### Step 8 — Tests

In `backend/tests/`, following the existing test conventions found in Step 0:
- Unit tests for each of the five tools against seeded test data (happy path + not-found path).
- A test for the orchestration loop using a mocked/stubbed `llm_client` (don't call real Bedrock/OpenAI in automated tests) that verifies: correct tool is invoked for a risk question, `trace` is populated correctly, malformed LLM output triggers the repair retry, and an approve/reject-style question does not produce `requires_human_review=False`.
- A test that the API endpoint returns a valid `AgentResponse` shape for a seeded application.
- Provider tests using mocked clients that verify: Bedrock success uses Bedrock; recoverable Bedrock failure falls back to OpenAI; OpenAI failure falls back to local emergency mode; local mode makes no network calls; and configuration errors produce clear errors rather than silently hiding invalid setup.
- A test that the frontend-facing `AgentResponse` shape is identical regardless of which provider served the answer.

### Step 9 — Offline evaluation script

Add `backend/scripts/evaluate_agent.py` (or match wherever similar scripts already live in the repo, if any) implementing a small offline eval harness:
- A hardcoded list of 10–15 question/expected-tool pairs.
- Run each through `run_agent` (using whichever provider is configured) and compute: tool-call correctness (%), groundedness (does every evidence/policy claim map to something actually present in that run's `trace`), refusal correctness on the approve/reject-style questions, and average latency.
- Print a summary table to stdout. This is for reporting real numbers in the presentation, not for CI.

### Step 10 — Config and docs

- Add all new environment variables (`LLM_PROVIDER`, `ENABLE_OPENAI_FALLBACK`, `ENABLE_LOCAL_FALLBACK`, `BEDROCK_REGION`, `BEDROCK_MODEL_ID`, `OPENAI_MODEL` or the repository's existing OpenAI setting, `MAX_AGENT_TURNS`, embedding provider/index settings) to `.env.example` (or wherever the repo already documents required env vars) with short comments.
- Do not hardcode credentials, API keys, model IDs, or AWS regions.
- Update the README's Module 7 section (only that section) to reflect what's actually implemented, following the existing README's tone/format — do not rewrite unrelated sections.

### Constraints — do not violate these

- Do not modify Modules 1–6 business logic. Read-only integration with their models/outputs only.
- Do not introduce a second config-loading pattern, a second DB session pattern, or a second API response convention — match what Step 0 finds.
- Do not hardcode a Bedrock model ID without first confirming it's actually enabled for the account/region; make it configurable. Do not silently hide invalid model IDs, credentials, permissions, or region configuration. Recoverable runtime failures may use the configured fallback chain.
- Never let the LLM's tool-supplied `application_id` override the one from the authenticated API request.
- Every code path must return the same `AgentResponse` schema to the frontend regardless of which LLM provider actually served the response.
- Prefer editing/extending the existing skeleton files (`agent.py`, router, schemas, `ChatPanel.jsx`) over creating parallel new ones, unless a new file is clearly warranted (e.g. `llm_client.py`, `agent_tools.py`, `policy_rag.py` are expected to be new).

### Deliverable

When done, summarize:
- every file created or modified,
- exact commands to run the backend/tests,
- how to run the offline evaluation script,
- how to switch `LLM_PROVIDER` between `bedrock` / `openai` / `local`,
- how the automatic fallback chain works,
- how to deliberately test Bedrock → OpenAI → Local fallback,
- how the local policy RAG remains usable without network access,
- and every assumption made about model IDs, field names, dependencies, or existing conventions because the actual repo differed from this prompt.

Do not claim a provider works unless it was actually tested or clearly label it as unverified.

## PROMPT END
