# Learned

Lessons this skill picked up in use, written on the spot by the agent running it (see "Learn on the spot" in SKILL.md). Read this file at the start of every ux-ultra task and treat each entry as part of the skill.

Entries are added, never silently rewritten. When the list passes about 20 entries, tell the user it's time to fold them into SKILL.md and the references; that's a review with evals, not an on-the-spot job.

## Entry format

```
### YYYY-MM-DD: short name
- Seen: what went wrong, as a pattern (no project names, UI copy, labels, file paths or one app's measurements)
- Rule: what to do instead, with a number if there is one
- Why: what it costs the user when it's missed
- Source: user correction | own check (which one)
- Check: how to catch it next time (lint id, a browser measurement, a step)
- Seen again: dates, added when an entry fires a second time
```

## Lint rules

`scripts/slop_lint.py` loads every line of the block below as an extra rule on each UI file. One JSON object per line: `id` (start it with `learned-`), `pattern` (a Python regex), `message`, and optionally `"severity": "error"` (default `warn`) and `"ignore_case": true`. Lines starting with `//` are comments. A line that doesn't parse shows up as `learned-rule-broken`. A project's DESIGN.md can still `allow` or `ban` these ids.

```lint
// {"id": "learned-example", "severity": "warn", "pattern": "lorem ipsum", "ignore_case": true, "message": "placeholder copy left in"}
```

## Entries

Seeded 2026-11-17 from about 240 UI corrections the user made across several projects. Most corrections came with a screenshot, which means the agent hadn't looked.

### 2026-11-17: a refresh that changes nothing
- Seen: asked for a "UI refresh", "more polish" or a bolder take, the agent kept the same nav, header, hero, footer, filters and interactions and only restyled. The user had to say "you pretty much just kept everything the same" and "everything looks just the way it was" more than once.
- Rule: when the request is a refresh, redesign or "make it better", structure and interaction are in scope. Before building, list what will be different for the user in the nav, the first screen, browsing or filtering, and the main flow. If nothing on that list changes, it isn't a refresh.
- Why: a restyle that looks the same to the user wastes a whole round and reads as ignoring the request.
- Source: user correction (repeated)
- Check: put a before and after screenshot side by side at the same width. If a non-designer can't see the difference in two seconds, it isn't done.

### 2026-11-17: moving the layout around isn't UX
- Seen: the agent rearranged sections and called it a UX improvement. The user asked "what does the funnel look like", "how would people get to the other content pages on mobile", and "why would people drop off".
- Rule: before changing a layout, write down the path a new visitor takes from arrival to the outcome that matters (signup, plan, purchase), where they're likely to drop off, and how every content type is reached on a phone. Each change has to name the step it improves.
- Why: a layout can look new and still lose users at the same step.
- Source: user correction
- Check: name one tap path from the landing page to every top-level section at 375px.

### 2026-11-17: the pattern has to fit the amount of data
- Seen: a line-by-line list was proposed for a catalogue of thousands of items.
- Rule: size the pattern to the real count. Hundreds or more items need search, filters and a dense grid or grouped views. Rows that each take a full line only work for short lists.
- Why: at real volume the page becomes an endless scroll.
- Source: user correction
- Check: render the view with the real item count, or a fixture of the same size, and count the screens of scrolling it takes.

### 2026-11-17: handing back work nobody looked at
- Seen: the agent repeatedly ended with "published without previewing", "I haven't checked light mode" or "I haven't looked at desktop", and the user found the breakage from a screenshot. This happened on mockups and artifacts as well as app code.
- Rule: saying it wasn't checked doesn't excuse skipping the check. Before handing back any visual change, take screenshots at 375px and at desktop width, in every theme the product has, of the whole viewport. If one truly can't be taken, say why in the first line of the hand-back, not the last.
- Why: every unseen hand-back turns into a screenshot and a correction from the user.
- Source: user correction (repeated)
- Check: the hand-back lists a screenshot for each width and theme pair.

### 2026-11-17: mobile-first doesn't mean mobile-only
- Seen: after "keep it mobile-first", the agent designed and checked only the phone layout.
- Rule: "mobile-first" here means a lot of the traffic is expected from mobile browsers and apps, so the phone experience has to be excellent. It doesn't make desktop secondary: desktop design is just as important. Design both layouts on purpose in the same round. Never ship a phone layout stretched out to desktop, or a desktop layout squeezed onto a phone.
- Source: user correction, and the user's own definition (2026-11-17)
- Check: a desktop screenshot accompanies every phone screenshot.

### 2026-11-17: the component looks fine, the view doesn't
- Seen: the agent fixed one component and checked only that component. The user then found that "the top is a jumbled mess", the header was pushed down by a thick button, a footer label clashed with a floating action bar, or the result didn't "look good in full view".
- Rule: after changing any component, screenshot the whole viewport around it, plus the header and anything fixed or floating. Check what the change did to its neighbours: alignment, overlap, and the height of shared bars.
- Source: user correction (repeated)
- Check: one full-viewport screenshot per round, besides any close-ups.

### 2026-11-17: selected has to be unmistakable
- Seen: selected cards were hard to tell apart, the checkmarks showed on cards that weren't selected, and items that were still processing could be selected.
- Rule: a selected state uses at least two signals: a 1px border in the accent colour plus a tinted fill of about 20% in the same hue, or a check that appears only when selected. Unselected items show no selection mark. Items that are processing or disabled can't be selected.
- Source: user correction (repeated)
- Check: screenshot a set with none, one and several selected, with one processing item among them.

### 2026-11-17: waits without feedback
- Seen: slow replies, long start-ups and other multi-second waits ran with no indicator. A generic loading label was criticised as well.
- Rule: anything that can take more than a second shows progress where the user is looking. Anything that takes more than a few seconds names the current stage ("Loading model weights", "Downloading 2 of 5") and shows progress if it's known.
- Source: user correction (repeated)
- Check: force a slow response (browser-checks.md has the snippet) and screenshot what the user sees during it.

### 2026-11-17: internals leaking into the UI
- Seen: internal IDs appeared in user-facing text, technical format codes were shown to non-developers, a toggle named after an implementation detail didn't say what it turned on, and labels just repeated the name of the pane they sat in.
- Rule: show what something means for the user, not how it's implemented. Translate technical terms into outcomes ("Smaller and faster", "Best quality"). IDs go in secondary text or nowhere. Drop labels that repeat what the layout already makes clear.
- Source: user correction (repeated)
- Check: read every visible label as a non-developer. Any term you'd have to explain gets rewritten.

### 2026-11-17: controls that don't do what they say
- Seen: a primary button did a fraction of what its label promised, another button did nothing, a download saved a file with no name, and deleting an item showed a "no longer exists" error afterwards.
- Rule: click every control you add or touch and check that the result matches its label. Anything that does less than its label promises gets finished, renamed or removed, and you say which in the hand-back. Don't show an error for the expected result of the user's own action.
- Source: user correction
- Check: click every changed control in the browser and note the result of each.

### 2026-11-17: heavy lines and stray surfaces
- Seen: bold white divider lines, a white border on a dark card, and an unwanted backdrop behind sections, each called out from a screenshot.
- Rule: a divider or border uses the lowest contrast that still separates, taken from DESIGN.md's line token, never plain white on a dark theme. Don't add a surface behind a group unless the design asks for one.
- Source: user correction (repeated)
- Check: on the desktop screenshot, list every visible line and surface and ask whether it would be missed if removed.

### 2026-11-17: improving a component means more than restyling it
- Seen: the user asked to "make this look better and have more functionality", and to make it "more interactive", and called the restyled result "so weak". A redesigned emblem was "WAY too simple" and didn't carry the meaning of the original.
- Rule: when asked to improve a component, propose what the user could newly do there (presets, a preview, a shortcut, a step that's currently missing) alongside the visual change. For icons and marks, keep what the original stands for.
- Source: user correction
- Check: the hand-back names at least one new capability, or says why none fits.

### 2026-11-17: scroll, overflow and things left alone
- Seen: a long prompt made the whole dialog scroll with an unstyled scrollbar, rows of horizontal cards couldn't be scrolled on small screens with a mouse, and a lone metadata line looked out of place.
- Rule: only the long part of a dialog scrolls, with a styled scrollbar. Horizontal rows need a visible way to scroll on every input (arrows or a scrollbar for a mouse, swiping on touch). An element alone in its row either joins a group or moves.
- Source: user correction
- Check: test the dialog with a very long value, and the rows at 768px with a mouse.

### 2026-11-17: a reference copied instead of learned from
- Seen: a details view built from the user's reference product came out "too close to [the reference], ripped".
- Rule: SKILL.md already says to borrow systems, not layouts. This entry records that it was missed in practice. Before building from a reference, write two things the new version does differently and why.
- Source: user correction

### 2026-11-17: the same thing built twice
- Seen: a second view needed what an existing view already did (a grid of results). The agent built a new one, then reused the tiles but changed their size, selection and data path. The user wanted the existing component unchanged.
- Rule: when a view needs what another view already has, pull that whole piece out as one shared component and feed it different data. Change no behaviour unless the user asks. If a change seems needed, ask with options before making it.
- Why: users expect the same thing to behave the same everywhere, and each departure is another round of correction.
- Source: user correction
- Check: before building a UI piece, grep the views for one that already does the job. In the hand-back, list every way the new use differs from the original, and make that list empty or approved.

### 2026-11-18: images upscaled past their source
- Seen: grid tiles were drawn from thumbnails generated for a much smaller layout. They looked soft, and nobody had compared the file size with the size on screen.
- Rule: an image file should have at least as many pixels as it takes on screen times devicePixelRatio. If thumbnails are generated, size them for the largest tile. When raising the size, change the URL or set Cache-Control so browsers do not keep the old small files.
- Why: blurry results make the generated work itself look worse.
- Source: user correction
- Check: in the browser, compare each img naturalWidth with clientWidth * devicePixelRatio. Flag any image whose file is under 0.9 of that.

### 2026-11-18: a menu button that opens but can't close
- Seen: a slide-in menu left the header visible but made it inert (the modal pattern), and its backdrop started below the header. Pressing ☰ again landed on a dead button, so the menu stayed open.
- Rule: a control that opens an overlay also closes it. If the overlay makes the background inert or modal, the open control's spot still has to close it: extend the click-to-close area over it, or keep the control outside the inert region.
- Source: user correction
- Check: open every overlay, then press its opening control again with a real mouse click and confirm it closes.

### 2026-11-18: a redesign that drops the shipped version's polish
- Seen: new cards for an existing component were built from scratch and came out plainer than the shipped ones, losing their overlaid actions, chips and detail rows. The user found the shipped cards "more refined" and asked for a middle ground.
- Rule: when redesigning a component that already ships, start from its visual language and reuse its pieces. Cut what doesn't fit the new context (extra chips, long text, secondary links) instead of starting over.
- Source: user correction
- Check: put a screenshot of the shipped component beside the new one before showing it. Every piece the new one dropped needs a reason.

### 2026-11-18: a prompt box that read as a button bar
- Seen: a pill-shaped text field with the primary button inside it, on a dark hero, read as a single button. Pressing it empty only showed a validation message, because typing was required for the main action.
- Rule: don't make free text a requirement for a primary action. Give the empty press a sensible default (such as curated or popular picks), offer one-tap choices beside the field, and make the field look editable: a visible label, an inset lighter surface, a text cursor, and an "e.g." placeholder.
- Source: user correction
- Check: press every primary button with its fields empty. The result is useful, not an error.

### 2026-11-18: a side column that grows and pushes the headline down
- Seen: adding wrapping suggestion chips to a hero's side column made that column taller than the headline. With the grid aligned to the bottom (`items-end`), the title moved down and the hero grew.
- Rule: in a two-column hero, the secondary column can't be taller than the primary one. Keep additions there to one line (scroll instead of wrap) and centre the columns rather than bottom-aligning them.
- Source: user correction
- Check: after adding anything to a hero, compare its height at 1440px with the height before the change.

### 2026-11-18: an overlay that misses the bar it sits on
- Seen: a phone sheet was offset by the height of a nearby spacer instead of the bottom bar's real height, which left a strip of page showing between the sheet and the bar.
- Rule: offset an overlay by the measured height of the element it meets, not by a nearby spacer or a guess. Write the sum the height is made of in a comment.
- Source: user correction
- Check: in the browser, compare the overlay's getBoundingClientRect().bottom with the bar's top. They should be equal.
