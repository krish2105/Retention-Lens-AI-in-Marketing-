# Outreach drafting evaluation (live, local model)

Model `qwen2.5:7b` via Ollama · 2026-11-01T09:14:50+00:00 · 16 drafts across segments and tones.
This is the first baseline run; it sets the reference, it is not compared with an invented target.

- Drafts passing every check: **1 of 16**
- Median time per draft (draft + second-pass review): 15.25 s

| Check | Passed |
|---|---|
| Numbers match the model's facts | 15/16 |
| No pressure or false urgency | 16/16 |
| No discounts or offers | 16/16 |
| No personal contact data | 16/16 |
| Uses name placeholders | 16/16 |
| Length 40–180 words | 16/16 |
| Second-pass review (tone, manipulation) | 1/16 |

Deterministic red-team cases (invented numbers, discounts, pressure, contact data, injection text, consent rules, idempotency) are unit tests in `services/api/tests/test_outreach.py`.

## Example drafts

**Promising · warm · fail**

> Subject: Hi [First name],
>
> Hi [First name],
> 
> I hope you're well. It's been a while since we last worked together, and I wanted to check in and see if there are any new picnic basket items you might be interested in trying. Our customers really love the Picnic Basket Wicker 60 Pieces and the Picnic Basket Wicker Small. Let me know if you need any samples or have any questions.
> 
> Best regards,
> [Your name]

**Promising · brief · fail**

> Subject: Nudge to Revive Your Order with Us
>
> Hi [First name],
> 
> I hope this message finds you well. It's been 82 days since your last order, and I wanted to touch base. You've ordered from us once, and I noticed you've really enjoyed the Childrens Cutlery Polkadot range. To keep things fresh, I've put together some items you might like to try next time. Looking forward to seeing you soon!
> 
> Best regards,
> [Your name]

**Can't lose · seasonal · fail**

> Subject: Seasonal Stock and Your Order
>
> Hi [First name],
> 
> I hope this email finds you well. It's been 373 days since your last order, which is longer than your usual 15-day gap. I wanted to touch base and discuss our upcoming season's stock, particularly the Red Harmonica In Box, Bag 250G Swirly Marbles, and Large Red Spot Windmill. These are always popular!
> 
> Would you like to schedule a call this week so we can go over the new range in more detail?
> 
> Best regards,
> [Your name]
