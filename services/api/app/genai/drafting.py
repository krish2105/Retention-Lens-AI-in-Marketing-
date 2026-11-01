"""Grounded outreach drafting (outcome D).

Design rules:
- The deterministic analytics core supplies every fact; the language model only writes words.
- No free text from customers, reviews or social posts is ever placed in the prompt.
- A checker blocks any number not in the facts, pressure tactics, discounts and personal data.
- A second model pass critiques tone; a person must approve; nothing is ever sent from here.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

import httpx

DRAFT_SCHEMA = {
    "type": "object",
    "properties": {"subject": {"type": "string"}, "body": {"type": "string"}},
    "required": ["subject", "body"],
}
CRITIC_SCHEMA = {
    "type": "object",
    "properties": {"verdict": {"type": "string", "enum": ["pass", "revise"]}, "issues": {"type": "array", "items": {"type": "string"}}},
    "required": ["verdict", "issues"],
}
TONES = {"warm": "warm and personal", "brief": "short and businesslike", "seasonal": "focused on the coming season's stock"}

SYSTEM = """You write short B2B emails for a UK giftware wholesaler's account manager to send to a trade customer.
Rules you must follow:
- Use ONLY the facts provided. Do not invent numbers, dates, prices, discounts or promotions.
- If you mention a number, copy it exactly from the facts. Prefer no numbers at all.
- Never offer a discount, free item or deadline. No pressure or urgency ("act now", "last chance", "only today").
- Use the placeholder [First name] for the greeting and [Your name] for the sign-off. Never write an email address or phone number.
- 60 to 140 words. Plain, friendly British English.
Return JSON with "subject" and "body"."""

CRITIC = """You review a draft B2B email from a wholesaler to a trade customer.
Return "revise" if it pressures the reader, invents an offer or deadline, sounds manipulative, or is not suitable for a professional account manager to send. Otherwise return "pass".
List each issue briefly. Return JSON with "verdict" and "issues"."""

NUMBER = re.compile(r"(?<![\w\[])£?\d[\d,]*(?:\.\d+)?%?")
PRESSURE = re.compile(r"\b(act now|last chance|only today|hurry|limited time|expires?|don't miss|final call)\b", re.I)
OFFER = re.compile(r"\b(\d+\s*%\s*off|discount|free (gift|delivery|shipping|item)|voucher|coupon|promo code)\b", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?:\+?\d[\d\s-]{8,}\d)")
LINK_OR_MARKUP = re.compile(r"https?://|www\.|<\s*/?\s*[a-z][^>]*>|\]\(", re.I)
LEAK = re.compile(r"rules you must follow|return json|system prompt|as an ai\b|language model|my instructions", re.I)
# Product names come from customers' own files, so they are untrusted text that reaches the prompt.
INSTRUCTION_LIKE = re.compile(r"ignore|instruction|system|prompt|assistant|you must|disregard|discount|offer|http|www\.|@", re.I)
SAFE_PRODUCT = re.compile(r"[^A-Za-z0-9 &'/.,()-]")


def clean_product(name: str) -> str | None:
    """Keep a product name only if it looks like a product name: short, plain characters, no instructions."""
    text = SAFE_PRODUCT.sub("", str(name)).strip()[:60]
    if not text or INSTRUCTION_LIKE.search(text):
        return None
    return text


@dataclass
class Facts:
    customer_id: str
    segment: str
    risk_band: str
    last_order_days: int
    usual_gap_days: int | None
    purchase_days: int
    top_products: list[str]
    play: str

    @classmethod
    def from_account(cls, account: dict, play: str) -> "Facts":
        gap = account.get("mean_gap_days")
        return cls(
            customer_id=account["customer_id"],
            segment=account.get("segment") or "Unsegmented",
            risk_band=account["risk_band"],
            last_order_days=int(account["recency_days"]),
            usual_gap_days=int(round(gap)) if gap else None,
            purchase_days=int(account["frequency"]) + 1,
            top_products=[p for p in (clean_product(n) for n in (account.get("top_products") or [])) if p][:3],
            play=play,
        )

    def prompt_lines(self) -> list[str]:
        lines = [
            f"Customer account: {self.customer_id} (do not mention the account number in the email)",
            f"Segment: {self.segment}",
            f"Days since their last order: {self.last_order_days}",
            f"Number of separate days they have ordered: {self.purchase_days}",
            f"Products they buy most: {', '.join(self.top_products) or 'not available'}",
            f"Suggested approach from our playbook: {self.play}",
        ]
        if self.usual_gap_days:
            lines.insert(3, f"Their usual gap between orders in days: {self.usual_gap_days}")
        return lines

    def allowed_numbers(self) -> set[str]:
        values = {self.last_order_days, self.purchase_days}
        if self.usual_gap_days:
            values.add(self.usual_gap_days)
        allowed = {str(v) for v in values}
        for product in self.top_products:
            allowed.update(re.findall(r"\d+", product))
        return allowed


@dataclass
class CheckResult:
    passed: bool
    checks: list[dict] = field(default_factory=list)


def check_draft(subject: str, body: str, facts: Facts) -> CheckResult:
    text = f"{subject}\n{body}"
    numbers = [n.strip("£%").replace(",", "") for n in NUMBER.findall(text)]
    unsupported = sorted({n for n in numbers if n.split(".")[0] not in facts.allowed_numbers()})
    words = len(body.split())
    checks = [
        {"name": "Numbers match the model's facts", "passed": not unsupported, "detail": f"unsupported: {', '.join(unsupported)}" if unsupported else "every number appears in the facts"},
        {"name": "No pressure or false urgency", "passed": not PRESSURE.search(text), "detail": (PRESSURE.search(text) or [""])[0] or "none found"},
        {"name": "No discounts or offers", "passed": not OFFER.search(text), "detail": (OFFER.search(text) or [""])[0] or "none found"},
        {"name": "No personal contact data", "passed": not (EMAIL.search(text) or PHONE.search(text)), "detail": "none found" if not (EMAIL.search(text) or PHONE.search(text)) else "email or phone number present"},
        {"name": "Uses name placeholders", "passed": "[First name]" in body, "detail": "greets with [First name]" if "[First name]" in body else "missing [First name]"},
        {"name": "Length 40–180 words", "passed": 40 <= words <= 180, "detail": f"{words} words"},
        {"name": "No links or markup", "passed": not LINK_OR_MARKUP.search(text), "detail": "none found" if not LINK_OR_MARKUP.search(text) else "link or markup present"},
        {"name": "Does not reveal instructions", "passed": not LEAK.search(text), "detail": "none found" if not LEAK.search(text) else "instruction text present"},
    ]
    return CheckResult(passed=all(c["passed"] for c in checks), checks=checks)


def template_draft(facts: Facts) -> dict:
    products = " and ".join(facts.top_products[:2]) if facts.top_products else "your usual lines"
    body = (
        "Hi [First name],\n\n"
        f"I was looking back at your orders and wanted to check in. You have regularly stocked {products}, "
        "and the new season's range is now in. If it would help, I'm happy to put together a suggested reorder "
        "based on what has sold well for you, or to talk through anything that hasn't worked.\n\n"
        "Just reply to this email whenever suits you.\n\nBest wishes,\n[Your name]"
    )
    return {"subject": "Checking in on your next order", "body": body}


class OllamaClient:
    def __init__(self, url: str, model: str, timeout: float = 120.0):
        self.url, self.model, self.timeout = url, model, timeout

    def chat(self, system: str, user: str, schema: dict, seed: int = 42) -> dict:
        response = httpx.post(
            f"{self.url}/api/chat",
            json={"model": self.model, "stream": False, "format": schema, "options": {"temperature": 0.3, "seed": seed},
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return json.loads(response.json()["message"]["content"])


def generate(facts: Facts, tone: str, client: OllamaClient | None) -> dict:
    """Return a draft with source, checks and critic verdict. Falls back to a labelled template."""
    started = time.monotonic()
    prompt = "Facts:\n- " + "\n- ".join(facts.prompt_lines()) + f"\n\nTone: {TONES[tone]}."
    draft, source, critic, error = None, "template", None, None
    if client is not None:
        try:
            draft = client.chat(SYSTEM, prompt, DRAFT_SCHEMA)
            source = "model"
            critic = client.chat(CRITIC, f"Subject: {draft['subject']}\n\n{draft['body']}", CRITIC_SCHEMA)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            draft, source, error = None, "template", f"local model unavailable: {exc.__class__.__name__}"
    if draft is None:
        draft = template_draft(facts)
    result = check_draft(draft["subject"], draft["body"], facts)
    checks = result.checks
    if critic is not None:
        checks = checks + [{"name": "Second-pass review (tone, manipulation)", "passed": critic.get("verdict") == "pass",
                            "detail": "; ".join(critic.get("issues", [])) or "no issues raised"}]
    return {
        "subject": draft["subject"].strip(),
        "body": draft["body"].strip(),
        "source": source,
        "checks": checks,
        "passed": all(c["passed"] for c in checks),
        "prompt": prompt,
        "error": error,
        "seconds": round(time.monotonic() - started, 1),
    }
