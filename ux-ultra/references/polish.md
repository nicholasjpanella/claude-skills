# Polish: the details that only show up in use

Agents write code and never use the page, so anything that only appears in behaviour gets skipped: the cursor, a focus ring, a button that does nothing visible for a second, a dropdown behind the content. Go through this list for every control you build. The numbers come from WCAG 2.2 (still the standard in 2026; WCAG 3 is a working draft), Apple and Android guidance, NN/g, GOV.UK and Vercel's Web Interface Guidelines.

Several items can be fixed once for the whole project instead of per element; `references/base-layer.css` does that. Check for it (or equivalent rules) in Step 0 and offer to add it.

## Controls

- **Cursor.** Tailwind v4's reset changed buttons to `cursor: default` to match browsers, so a v4 project has no hand cursor on buttons unless something adds it. Whether buttons should show the hand is genuinely debated (platform guidance reserves it for links; users often read its absence as "broken"). Pick one rule for the project, write it in DESIGN.md, and apply it everywhere. Never show the pointer on a disabled control.
- **States.** Every control has default, hover, `:focus-visible`, active and disabled; anything that starts work also has loading. Put hover styles under `@media (hover: hover)` so touch screens don't get stuck hover states.
- **Targets.** 24x24 CSS px is the WCAG 2.2 AA floor (2.5.8). Aim for 44x44 on touch layouts (Apple's default; Android asks 48x48dp with 8dp between targets). Grow the hit area with padding, not by enlarging the icon.
- **Copy.** Verb plus noun ("Delete project", "Save changes"). One primary button per view; the rest are secondary. Avoid "OK" in confirmations; "Continue" is fine in a linear flow.
- **Links and buttons.** Navigation is `<a href>`; actions are `<button type="button|submit">`. A `<button>` without `type` inside a form submits it.

## Waiting and submitting

- **Loading.** Keep the button's label and add an indicator, or change the label to the action in progress ("Saving…"). Delay showing a spinner by 150 to 300ms, so fast responses don't flash, and once shown keep it for at least 300 to 500ms, so it doesn't flicker.
- **Submit.** Leave the submit button enabled until submission starts (a disabled button gives no reason why; GOV.UK advises against it), then disable it to stop double submits. On a validation failure, move focus to the first field with an error.
- **Results.** Success and failure are announced: `role="status"` for success, `role="alert"` for failure, or an `aria-live` region. Async errors that belong to a field (like "email already taken") go under that field, and focus goes back to it.
- **Focus after async work.** `focus()` on a disabled element silently does nothing, so a field disabled during a request can't take focus back when the error arrives, and focus falls to `<body>`. Re-enable the field before focusing it, or don't disable the field at all: disable only the button, or make the field `readOnly` while the request runs. Also put focus somewhere sensible after a successful save (the button, or the confirmation).
- **Focus when content is replaced.** Anything that removes or hides the focused element sends focus to `<body>`: replacing a form with "Account deleted", hiding a "Try again" button once it's clicked, closing a panel. Move focus to the new content (give the heading or message `tabindex="-1"` and focus it) or to the next sensible control, and check with `document.activeElement` afterwards.
- **Forms with nowhere to send.** If there's no endpoint or address yet, the form still validates, but on submit it says plainly that sending isn't set up (and what to do instead). It never shows success, and never posts to a made-up address.

## Forms

- A visible label for every field, outside the field. A placeholder is not a label; it disappears when the user types.
- The right `type`, `autocomplete` and `inputmode` on each input, so phones show the right keyboard and browsers can autofill.
- Input text at least 16px on mobile, or iOS zooms the page when the field is focused.
- Never block paste, and never block zoom (`user-scalable=no` or `maximum-scale=1` in the viewport meta).
- Errors don't rely on colour alone (WCAG 1.4.1; a red border with no text is the textbook failure). Say what's wrong in words.

## Colour

- Text 4.5:1 against its background, 3:1 for large text (24px, or 18.66px bold). Helper and placeholder text count.
- Icons, input borders and focus rings 3:1 (WCAG 1.4.11).
- Disabled controls are exempt from the contrast rules, but they still need to look disabled and not just faded.
- Never colour alone for status: pair it with text or an icon.

## Content

- Design the empty, error, long-text and very-many-items cases, not only the sample data. A name with 60 characters, a list of 1,000 rows and an empty account should all render without overflow.
- Numbers that get compared (prices, tables, totals) use `font-variant-numeric: tabular-nums`. Format numbers, dates and currency for the locale.
- Headings `text-wrap: balance`, paragraphs `text-wrap: pretty`, so lines don't end on a single word.

## Layout

- Spacing from the project's scale (usually 4 or 8px steps); optical nudges of 1px are fine, arbitrary values like 13px are not.
- Images get explicit `width`/`height` or `aspect-ratio`, so the page doesn't jump when they load.
- Anchored headings get `scroll-margin-top` when there's a sticky header.
- A z-index scale written down (dropdown, sticky, overlay, toast), so menus don't render behind content.
- `[hidden]` stays hidden: any `display` rule on the same element overrides the browser's own `[hidden]` style, so a hidden notice or filtered-out item shows anyway. `base-layer.css` forces it; without that, check every element you toggle with `hidden`.
- A sticky or pinned panel has to fit its tallest state (errors showing, a notice, a long value) inside the shortest likely viewport, about 700px tall on a laptop, or it hides its own submit button and messages. If it can't, don't pin it. Check: show every state and compare the panel's bottom edge with `innerHeight`.

## Motion

- Animate only `transform` and `opacity`. Never `transition: all`, which animates layout properties and anything added later.
- 100 to 150ms for small feedback (press, toggle), under 300ms for UI motion. A press can scale to about 0.97.
- Honour `prefers-reduced-motion` for anything that moves on its own.

## Keyboard and overlays

- Dialogs move focus inside when they open, keep it there, close on Escape, and return focus to the control that opened them. A native `<dialog>` opened with `showModal()` does the first three.
- Tab order follows the visual order. Nothing focusable is hidden.
- Menus and popovers close on Escape and on a click outside.
- Dialogs closing on a click outside depends on what they hold. An informational dialog or a confirmation can close that way. A dialog where the user has typed or chosen something must not, because one stray click loses the work. Native `<dialog closedby="any">` gives that light dismiss without JavaScript where browsers support it; check support before relying on it.

## Right to left

- **Direction on the root.** `dir="rtl"` and the right `lang` on `<html>`. Use logical properties so the layout flips by itself: `margin-inline-start`, `inset-inline-start`, `text-align: start`; in Tailwind `ms-*`, `me-*`, `ps-*`, `pe-*`, `start-*`, `text-start`. Never flip a whole container with `scaleX(-1)`; it mirrors the text inside too.
- **Icons.** Mirror only icons that show direction or order: back and forward, chevrons, undo and redo, send. Leave media controls, clocks, checkmarks, search and logos as they are.
- **Mixed text.** Put Latin words, numbers, codes and anything the user typed in `<bdi>`, or give them `unicode-bidi: isolate`, so they don't drag nearby punctuation to the wrong side. Signed numbers go in `<bdi dir="ltr">`, or `+12%` shows as `12%+`.
- **Inputs.** Email, URL, phone and code fields stay `dir="ltr"`, aligned to the end so they line up with the other fields.
- **Digits.** One digit system per screen. Format with `Intl.NumberFormat` for the locale, not by hand.
- **Arabic script.** Letter spacing always 0; any tracking pulls the joined letters apart. No italic; browsers fake it by slanting the glyphs. Body line height about 1.6 to 1.8, and sizes a step larger than for Latin text. Use a family drawn for the script, not a Latin one with a system fallback.

Logical properties per MDN's guide (updated November 2025). Adapted from the unslop skill by Damir Sokolovsky (CC BY 4.0), 2026.

## Done means checked

Before saying a UI change is done, say what you checked and how: which widths, which states you triggered, what you tabbed through, which overlays you closed with Escape. If something wasn't checked, say so. Don't update visual-test baselines (`--update-snapshots`) to make a failing test pass.
