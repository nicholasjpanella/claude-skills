# Case studies as lesson cards

Short, paraphrased lessons from public write-ups. Each card links its source and says what kind of evidence it is: **decision rationale** (why a team chose something, no numbers) or **measured outcome** (reported results, often from the company itself). Read the source before leaning on a card for a big decision; these summaries were compiled from a research note on 2026-11-13, not re-read from the originals.

Never copy text, screenshots or code from these sources into a project. Link them and say it in your own words.

Add a card when a write-up changes how you'd build something. Keep the format, so cards stay comparable and each one has a check you can run.

---

### Linear 2024 redesign: themes from three inputs
- Source: https://linear.app/now/how-we-redesigned-the-linear-ui
- Evidence: decision rationale
- Lesson: generate light, dark and high-contrast themes in a perceptual colour space (LCH or OKLCH) from a base colour, an accent and a contrast level, instead of hand-maintaining dozens of variables. Linear replaced 98 theme variables with 3 inputs.
- Apply when: a product needs more than one theme, or its colour variables have sprawled.
- Check: every theme colour traces back to a token or the generator; no one-off hex values in components.

### Linear 2026 refresh: calm through subtraction
- Source: https://linear.app/changelog/2026-03-12-ui-refresh
- Evidence: decision rationale
- Lesson: a dense tool gets calmer by removing noise (consistent headers, dimmer sidebars, fewer separators, redrawn icons), not by adding whitespace. The refresh counted as a success if most users didn't notice it.
- Apply when: an established, dense interface feels busy.
- Check: count separators, borders and distinct greys before and after; the after count should be lower.

### Material 3 Expressive: emphasis that is found faster
- Source: https://www.androidauthority.com/google-material-3-expressive-details-3554486/ (press coverage, not Google's own paper)
- Evidence: measured outcome, secondhand
- Lesson: Google reported 46 studies with over 18,000 participants, and key elements found up to 4 times faster when size, shape and colour emphasised the primary action.
- Apply when: arguing for stronger emphasis on one primary action.
- Check: the blur test in `craft.md` shows the primary action first.
- Caveat: the numbers come through press coverage; treat them as indicative.

### GOV.UK Home Office licensing: research at scale pays
- Source: https://services.blog.gov.uk/2021/03/05/showing-the-rewards-of-user-centred-service-design-at-scale/
- Evidence: measured outcome (small survey samples)
- Lesson: after more than 500 research sessions, satisfaction rose from 47% to 78% and processing time halved. Research aimed at the risky decisions moved real outcomes.
- Apply when: deciding whether a flow change needs user evidence first.
- Check: the brief names the outcome and how it would be observed.

### Counter-case — GOV.UK Carer's Allowance: best practice still needs evidence
- Source: https://userresearch.blog.gov.uk/6-case-studies-using-research-and-data-to-improve-a-live-service/
- Evidence: measured outcome (a null result)
- Lesson: removing a progress indicator, a change many would call obviously right or obviously wrong, made no measurable difference.
- Apply when: a "best practice" is about to be applied without evidence; say it's a judgement call, not a proven win.
- Check: the hand-back's rationale doesn't present a convention as a measured effect.

### Stripe: payment methods and conversion
- Source: https://stripe.com/blog/testing-the-conversion-impact-of-50-plus-global-payment-methods
- Evidence: measured outcome (vendor's own data)
- Lesson: offering one relevant non-card payment method raised conversion by about 7.4% on average, and Apple Pay by about 22%. What the checkout offers can matter more than how it looks.
- Apply when: designing or restyling a checkout; ask which payment methods the audience uses before polishing the form.
- Check: the brief lists the payment methods and why.
