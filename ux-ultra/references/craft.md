# Craft: the judgement calls, with numbers

These are the rules experienced product designers apply without thinking. The common thread is subtraction: to make one thing stand out, quiet everything else rather than enlarging it. Use them while planning a screen and as the yardstick in the critique. DESIGN.md overrides any number here when it says otherwise.

## Hierarchy

- One focal point and one primary action per view. If two things compete, demote one.
- At most two large elements on a screen. Emphasise with weight and contrast before size.
- Demote secondary content with a lighter grey or smaller weight before adding a new colour or a border.
- **Blur test:** the focal point should still be obvious with the page blurred. In the browser, run `document.body.style.filter = 'blur(6px)'`, take a screenshot, then `document.body.style.filter = ''`. If the eye goes somewhere you didn't intend, fix the hierarchy.

## Type

- About three sizes on one screen (body 14 to 16px, subhead 18 to 22px, heading up to 32px on app screens; marketing pages can go further), and two or three weights.
- Take sizes from a hand-picked, non-linear scale (for example 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72), not arbitrary values.
- Line length 45 to 90 characters; 60 to 75 is a safe default. Cap it with `max-width` in `ch`.
- Line height 120 to 145% for body text; longer lines need more.
- All caps, when used at all, gets 5 to 12% extra letter-spacing.

## Space

- A fixed spacing scale (for example 2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96).
- More space between groups than within them. If everything has the same gap, nothing is grouped.
- Start with too much space and remove it. Separate with space or a background change before reaching for a border.
- Dense tools (tables, dashboards, editors) stay calm by cutting noise, not by adding whitespace: fewer separators, dimmer chrome.

## Colour

- Define every shade up front: 8 to 10 greys and 5 to 10 shades of each brand colour, tuned by eye. Don't generate tints by lightening or darkening at runtime.
- Dark mode is not an inversion. Base around #121212, lighter surfaces for higher elevation, accents about 20 points less saturated than in light mode.

## Depth

- One light source for the whole UI. Higher elevation means more offset and more blur.
- Layered shadows tinted with the background hue look real; a single grey `rgba(0,0,0,.1)` looks pasted on.

## Waiting

Match the feedback to the wait:

| Wait | Feedback |
|---|---|
| Under about 300ms | Nothing; a spinner would only flash |
| Up to about 5 seconds | A spinner or busy label on the part that's working, not the whole page |
| First load of a list, cards or a table | A skeleton in the shape of the content, for a few seconds at most |
| Longer than about 5 seconds, or unknown | A progress bar with the current stage named, and a way to cancel. Indeterminate until progress can be measured, then determinate |

Skeletons belong to containers and data views only. Never put one on a toast, a menu or dropdown item, or a modal itself (content inside a modal can have one). Buttons, inputs, checkboxes and toggles don't get skeletons; a busy button keeps its label and shows an indicator (see `polish.md`). Based on IBM Carbon's loading pattern, updated 2026.

## Motion

- How often an action happens decides whether it animates. Frequent actions and keyboard actions get none. Rare, meaningful moments (opening a dialog, completing a task) can.
- 150 to 250ms for UI motion.

## Difficult data

Design with the content that breaks layouts, not the sample:

- the longest and shortest real values (a 60-character name, a one-letter one);
- 0, 3 and 25+ items in every list;
- a missing image, a missing optional field;
- an error, and a slow response.

If there's no real data, make fixtures with these cases and render each one.

## Rationale

Every major choice gets a one-line reason and the tradeoff it accepts ("one column so the price is the first thing read; costs a longer scroll on desktop"). A choice you can't give a reason for is probably a default.
