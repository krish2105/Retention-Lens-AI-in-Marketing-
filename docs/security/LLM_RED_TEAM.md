# GenAI red team: OWASP Top 10 for LLM Applications (2025)

Automated cases live in `services/api/tests/test_redteam.py` and run in CI on every push. They test
deterministic controls, so they fail the build on a regression rather than depending on a model's mood.

| OWASP item | Applies? | Control | Tests |
|---|---|---|---|
| LLM01 Prompt injection | Yes: product names come from customers' files | Names sanitised and instruction-like text dropped before the prompt; only structured facts reach the model | 6 hostile names, plus ordinary names kept |
| LLM02 Sensitive information disclosure | Yes | Numbers must match the account's facts (blocks other customers' IDs and amounts); emails and phone numbers blocked | 4 cases |
| LLM03 Supply chain | Yes | Model pinned by tag (`qwen2.5:7b`); `pip-audit`, `npm audit`, CodeQL in CI | CI jobs |
| LLM04 Data and model poisoning | No | No model is trained or fine-tuned on user text; ML models fit on invoice numbers only | n/a |
| LLM05 Improper output handling | Yes | Links and markup blocked; drafts shown as text; CSV formula neutralisation | 4 cases + CSV test |
| LLM06 Excessive agency | Yes | No send capability anywhere; approval needs a person, a consent basis (PECR) and an idempotency key | route scan + approval tests |
| LLM07 System prompt leakage | Yes | Drafts echoing instructions are blocked | 3 cases |
| LLM08 Vector and embedding weaknesses | No | No retrieval or embeddings | n/a |
| LLM09 Misinformation | Yes | Invented numbers, offers and urgency blocked; second-pass critic; human approval | 3 cases + critic tests |
| LLM10 Unbounded consumption | Yes | 30 drafts per minute per workspace; 120 s model timeout; request size limits | rate-limit test |

Not covered by automated tests: jailbreaks that produce rude but rule-compliant text (the critic and the
human reviewer are the control), and attacks on Ollama itself (it listens on localhost only).
