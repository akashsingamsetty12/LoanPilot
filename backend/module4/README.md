# LoanIQ Module 4 — Document Classification & Information Extraction

Module 4 receives OCR text output from Module 3 and executes automated document processing:

1. **Document Classification**: Identifies canonical type (`payslip`, `bank_statement`, `tax_return`, `kyc_identity`, `address_proof`, `other`).
2. **Field Extraction**: Extracts canonical structured key-value pairs with numeric confidence, page numbers, and source evidence.
3. **Confidence Calculation & Review Flagging**: Flags extracted fields or documents requiring manual human review.
4. **LLM Fallback & Resiliency Engine**: Guarantees production reliability across multiple LLM providers.

---

## LLM Fallback Strategy

Module 4 includes an automated **LLM Fallback Engine** (`generate_with_fallback`) to ensure continuous operation even during LLM provider rate limits, network outages, API errors, or unconfigured keys.

### Provider Execution & Fallback Chain

```text
Configured Primary Provider (LLM_PROVIDER)
               ↓ (fails / rate limit)
Retry Primary Provider (Max 2 attempts total)
               ↓ (still fails)
Secondary Provider (OpenAI ↔ Gemini)
               ↓ (fails)
Mock Provider (Deterministic offline engine)
               ↓ (fails)
Human Review & Safe Error Response (needs_review=true)
```

### Fallback Rules & Behavior

* **Primary Provider**: Set via `LLM_PROVIDER` environment variable (`openai`, `gemini`, or `mock`).
* **Retry Count**: Maximum `2` attempts per provider. Indefinite retries are strictly prohibited.
* **Key Validation**: If a provider's API key is unconfigured, it is automatically skipped with a safe log message without attempting network calls.
* **No Duplicate Provider Calls**: The fallback chain deduplicates providers (e.g. `openai` → `gemini` → `mock` or `gemini` → `openai` → `mock`).
* **Data Safety**: System **never invents or fabricates missing financial/KYC data**. On complete provider failure, an empty/safe payload is returned with `needs_review: true`.

---

## Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | Primary LLM provider (`openai`, `gemini`, `mock`) | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | `""` |
| `OPENAI_MODEL` | OpenAI model identifier | `gpt-4o-mini` |
| `GEMINI_API_KEY` | Google Gemini API key | `""` |
| `GEMINI_MODEL` | Gemini model identifier | `gemini-2.5-flash` |
| `CONFIDENCE_THRESHOLD` | Confidence threshold for human review flagging | `0.70` |

---

## Response Metadata Schema

Every classification and extraction response includes safe metadata fields tracking provider execution and fallback usage:

```json
{
  "provider_used": "gemini",
  "fallback_used": true,
  "attempt_count": 3,
  "needs_review": false
}
```

* `provider_used` (`string | null`): Provider name that successfully fulfilled the request (`openai`, `gemini`, `mock`, or `null` if all failed).
* `fallback_used` (`boolean`): `true` if the primary provider failed, was skipped due to missing API keys, or retried.
* `attempt_count` (`integer`): Total number of provider execution attempts made across the chain.
* `needs_review` (`boolean`): `true` if overall confidence < `CONFIDENCE_THRESHOLD`, extracted fields contain missing/unconfident data, or all providers failed.
* `error` (`string | null`): Error details populated when processing or fallback fails.

---

## Controlled Failure Responses

If all LLM providers in the fallback chain fail, Module 4 returns controlled responses without throwing unhandled server exceptions or fabricating fake values:

### Classification Failure Response
```json
{
  "document_id": "DOC-999",
  "document_type": "other",
  "confidence": 0.0,
  "reason": "All LLM providers failed. Manual review required.",
  "provider_used": null,
  "fallback_used": true,
  "attempt_count": 6,
  "needs_review": true,
  "error": "All LLM providers failed. Manual review required."
}
```

### Extraction Failure Response
```json
{
  "document_id": "DOC-999",
  "document_type": "payslip",
  "fields": {},
  "confidence": 0.0,
  "provider_used": null,
  "fallback_used": true,
  "attempt_count": 6,
  "needs_review": true,
  "error": "All LLM providers failed. Manual review required."
}
```

---

## Fallback Logging Output Example

During execution, Module 4 logs safe, non-sensitive audit logs tracking fallback events:

```text
Trying primary provider: openai
OpenAI request failed
Retrying openai: attempt 2
OpenAI request failed
Switching fallback provider: gemini
Gemini request failed
Using Mock provider
```

*Note: API keys are strictly masked and never printed to logs or standard output.*
