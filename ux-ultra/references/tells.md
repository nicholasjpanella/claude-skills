# Defaults that read as generated

These are the looks an undirected model reaches for. None is wrong for every brief; each is a problem when it appears because nothing was decided. Use this list to flag your own proposals, not as a ban list to paste into every project. A project's DESIGN.md decides what is banned there, and it should never ban what the brand actually uses.

Banning one wave only moves the output to the next. The second wave below appeared after the first was widely banned, so expect a third. The durable fix is a decision tied to the subject, not a longer list.

Checked against 2026 design commentary on 2026-11-18. Both the first and second waves are still named as current giveaways, so neither has aged out. Check again when this note is more than a year old.

## First wave (the "vibe-coded" look)

- Inter, Roboto or system sans for everything, no display face.
- Indigo, violet or purple as the accent (`indigo-500` and neighbours), often as an indigo-to-blue gradient, often on headline text. Cyan on a dark background is the same default in another colour.
- Every block of text centred, with nothing left-aligned or asymmetric anywhere on the page.
- Centred hero with a pill badge above the headline and two buttons below.
- Three identical cards with an icon on top, then a stats row, then a "how it works" 1-2-3, then a closing CTA band.
- One large radius and one soft shadow (`rgba(0,0,0,.1)`, `shadow-lg`) on every card.
- Glassmorphism (backdrop blur), glows, gradient blobs behind content. Glass can be a real decision (frosted layers over media or a canvas); when it is, `glass.md` says how to do it so it doesn't read as this.
- Every section fades and slides up on scroll.
- Always-dark mode with grey body text and uppercase labels.
- shadcn/ui or another kit left in its default theme.
- Filler copy: "Elevate your workflow", "Unlock the power of", "Seamless", "Supercharge", and two-beat slogans that say nothing ("Build faster. Ship smarter.").
- Placeholder people: testimonials and avatars from "Sarah Johnson", "John Doe" or "Jane Smith". Use real quotes the user gave, or leave the section out.

## Second wave (what replaced it)

- Warm cream background (around `#F4F1EA`) with a high-contrast serif display and a terracotta or clay accent (around `#D97757`).
- Near-black background (`#0B0B0B`, `#111`) with one acid-green or vermilion accent.
- Broadsheet layout: hairline rules, zero radius, dense columns.
- Template chrome: a tracked-out ALL-CAPS eyebrow above every heading, monospace for small data labels, meta strings joined with middle dots (`A · B · C`), labels like `WORD — fragment`, `→` appended to link and button text.
- One word in the headline set in italic, bold or the accent colour.
- A hero of a big number, a small label and a gradient accent.
- `01 / 02 / 03` markers on content that isn't a sequence.

## Third wave (what this skill's own runs drifted to)

Once cream, near-black and the SaaS kit were flagged, test runs converged on a new set. These came from runs that followed every other rule:

- Pale tinted "paper" (green-grey, blue-grey, around `#EEF2EA` to `#F4F6F3`) with blue ruled lines, a red double rule under totals, and a book serif such as Literata for headings and figures: the ledger look, on every finance or invoicing page.
- A manila or yellow "repair tag" with a punched hole holding the form or the prices, enamel-blue accents and a condensed grotesque: the workshop look, on every trade or repair page.
- More generally, the category's first metaphor rendered literally: a ledger for money, a tag for repairs, a terminal for developer tools, a notebook for writing apps.

None is wrong for every brief. Each is the first thing that comes to mind for its category, which is why it repeats.

## The four layers

Reading tells by layer helps find the ones a colour list misses.

1. **Token defaults**: the font, the accent hex, one radius, one shadow.
2. **Template structure**: hero, badge, three cards, stats, steps, CTA, regardless of what the page is for.
3. **Decoration with no job**: gradients, glass, glow, coloured stripes on card edges, emoji as icons.
4. **Omission**: no empty, loading or error states; no hover or focus states; every button styled as primary; the same gap between everything so nothing is grouped; no progressive disclosure. Uniformity is a tell of its own: one radius, one shadow, one weight, one padding.

The fourth layer is the one users actually hit, and the one a screenshot of the happy path never shows.

## Accessibility, specifically

Generated UI tends to pass static checks (contrast, alt text) reasonably well and fail on behaviour: dialogs that let Tab escape and ignore Escape, missing focus styles, custom controls without names, skipped heading levels, and low-contrast grey on dark backgrounds. Check behaviour by hand.
