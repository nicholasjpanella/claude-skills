# Browser checks

Run the script below through the browser tool's JavaScript call (Claude in Chrome `javascript_tool`, Playwright MCP `browser_evaluate`, Chrome DevTools MCP `evaluate_script`) once per width. It returns a small JSON object. Asking for numbers like this costs a few dozen tokens; an accessibility-tree snapshot costs thousands, and a screenshot can't tell you a contrast ratio or a cursor.

## Getting the width right

Serve the page over HTTP (`python3 -m http.server <port>` from the project folder, in the background; stop it when done). Then set the width by emulating the viewport where the tool can, because resizing a real window can be clamped by the screen or host and silently fail:

- **Chrome DevTools MCP:** `emulate` with `viewport: "375x812x2,mobile,touch"`, then `"1440x900x1"`. Each `emulate` call resets earlier settings, so pass the viewport and any network throttling in the same call.
- **Playwright MCP:** `browser_resize` sets the page viewport of its own browser and is usually honoured; the server can also start with `--viewport-size`.
- **Claude in Chrome:** `resize_window` resizes your real window and often can't reach 1440 or 375. Go straight to the frame harness below.

Then read the width back: `innerWidth` (or `document.documentElement.clientWidth`, which excludes the scrollbar) must match what you asked for. If it doesn't, use the harness: copy `assets/frame.html` from this skill into the served folder and open `frame.html?src=/your-page.html&w=375&h=812`. The page lays out at exactly that width inside an iframe. Run the checks inside it with `await document.querySelector('iframe').contentWindow.eval(SCRIPT)`. A frame wider than the window is scaled down for display, so its screenshot is shrunk; say so in the report and read numbers from the script, not the picture.

Report the width the page actually had, not the one you asked for.

## Checking the checks

Before trusting the script in a new session or with a new browser tool, run it once on `assets/check-fixture.html` (serve it next to the page). That page breaks every rule on purpose. The result must flag each of: `failedFonts`, `lowContrast`, `targetsUnder24`, `unnamedControls`, `placeholderOnly`, `noPointer`, `disabledPointer`, `smallInputText`, `transitionAll`, `zoomBlocked`, `headingSkips`, `imagesWithoutAlt`, `imagesWithoutSize`, `longLines`, and a `glass` entry with `worstContrast` under 4.5 and `nested: true`. Any that comes back clean is a broken check in this environment, so don't rely on it for the real page; say which in the report.

## The script

It is async because it waits for web fonts to settle; every tool's JavaScript call accepts a promise.

```js
(async () => {
  await document.fonts.ready;
  // a font whose file failed (404, CORS) renders as a fallback that looks fine in a screenshot
  const failedFonts = [...new Set([...document.fonts].filter(f => f.status === 'error').map(f => f.family.replace(/["']/g, '')))];
  const vis = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const all = [...document.querySelectorAll('body *')].filter(vis);
  const lum = c => { const m = c.match(/[\d.]+/g); if (!m) return null;
    const [r, g, b] = m.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
    return { L: .2126 * r + .7152 * g + .0722 * b, a: m[3] === undefined ? 1 : +m[3] }; };
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = lum(getComputedStyle(e).backgroundColor); if (c && c.a > .5) return c.L; } return 1; };
  const isDisabled = el => el.closest(':disabled, [aria-disabled="true"]');
  const label = el => (el.innerText || el.getAttribute('aria-label') || el.value || el.tagName).trim().slice(0, 30);
  const textEls = all.filter(el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
  const fonts = {}, lowContrast = [];
  for (const el of textEls) {
    const s = getComputedStyle(el);
    const f = s.fontFamily.split(',')[0].replace(/["']/g, '').trim(); fonts[f] = (fonts[f] || 0) + 1;
    if (isDisabled(el)) continue;  // disabled controls are exempt from WCAG 1.4.3
    const fg = lum(s.color); if (!fg) continue;
    const bg = bgOf(el), hi = Math.max(fg.L, bg), lo = Math.min(fg.L, bg), ratio = (hi + .05) / (lo + .05);
    const large = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && +s.fontWeight >= 700);
    if (ratio < (large ? 3 : 4.5)) lowContrast.push({ text: el.textContent.trim().slice(0, 40), ratio: +ratio.toFixed(2) });
  }
  const W = document.documentElement.clientWidth;
  const overflow = all.filter(el => el.getBoundingClientRect().right > W + 1)
    .slice(0, 10).map(el => el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.split(' ')[0] : ''));
  const controls = all.filter(el => el.matches('a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[tabindex]:not([tabindex="-1"])'));
  const size = el => el.getBoundingClientRect();
  const under24 = controls.filter(el => { const r = size(el); return r.width < 24 || r.height < 24; }).slice(0, 10).map(label);
  const under44 = controls.filter(el => { const r = size(el); return r.width < 44 || r.height < 44; }).length;
  const unnamed = controls.filter(el => !(el.innerText || '').trim() && !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby') && !el.title && !(el.id && document.querySelector(`label[for="${el.id}"]`)) && !el.closest('label') && !el.value)
    .slice(0, 10).map(el => el.outerHTML.slice(0, 80));
  const actionable = controls.filter(el => el.matches('button,summary,[role=button],select,input[type=checkbox],input[type=radio],input[type=submit],input[type=button]') && !isDisabled(el));
  const noPointer = actionable.filter(el => getComputedStyle(el).cursor !== 'pointer').slice(0, 10).map(label);
  const disabledPointer = controls.filter(el => isDisabled(el) && getComputedStyle(el).cursor === 'pointer').map(label);
  const smallInputText = [...document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=hidden]),select,textarea')]
    .filter(el => vis(el) && parseFloat(getComputedStyle(el).fontSize) < 16).length;
  const transitionAll = all.filter(el => /(^|,\s*)all(\s|,|$)/.test(getComputedStyle(el).transitionProperty) && getComputedStyle(el).transitionDuration !== '0s').length;
  const placeholderOnly = [...document.querySelectorAll('input[placeholder],textarea[placeholder]')].filter(el => vis(el) && !(el.id && document.querySelector(`label[for="${el.id}"]`)) && !el.closest('label') && !el.getAttribute('aria-labelledby')).length;
  const sizes = {}, weights = {};
  for (const el of textEls) { const s = getComputedStyle(el); sizes[s.fontSize] = (sizes[s.fontSize] || 0) + 1; weights[s.fontWeight] = (weights[s.fontWeight] || 0) + 1; }
  const bodyPx = parseFloat(getComputedStyle(document.body).fontSize);
  // focal points compete within one screen, so only count large text in the current viewport
  const largeText = textEls.filter(el => { const r = el.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight && parseFloat(getComputedStyle(el).fontSize) >= bodyPx * 2; }).map(el => el.textContent.trim().slice(0, 30));
  // about 0.5em per character on average, so width / (0.5 * font size) approximates characters per line
  const longLines = [...document.querySelectorAll('p,li,dd,blockquote')].filter(el => vis(el) && el.getBoundingClientRect().width / (parseFloat(getComputedStyle(el).fontSize) * 0.5) > 90).length;
  // glass: contrast of each blurred surface's text over the worst backgrounds (pure black and pure white behind it)
  const lin = v => v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
  const relL = c => .2126 * lin(c[0]) + .7152 * lin(c[1]) + .0722 * lin(c[2]);
  const rgba = c => { const m = (c.match(/[\d.]+/g) || []).map(Number); return m.length < 3 ? null : [m[0] / 255, m[1] / 255, m[2] / 255, m[3] === undefined ? 1 : m[3]]; };
  const blurOf = el => { const s = getComputedStyle(el); return (s.backdropFilter && s.backdropFilter !== 'none') ? s.backdropFilter : (s.webkitBackdropFilter && s.webkitBackdropFilter !== 'none' ? s.webkitBackdropFilter : null); };
  const glass = all.filter(blurOf).slice(0, 12).map(el => {
    const bg = rgba(getComputedStyle(el).backgroundColor) || [0, 0, 0, 0];
    const t = el.querySelector('*') && [...el.querySelectorAll('*')].find(d => vis(d) && [...d.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) || el;
    const fg = rgba(getComputedStyle(t).color);
    const worst = fg ? Math.min(...[0, 1].map(b => { const comp = bg.slice(0, 3).map(v => bg[3] * v + (1 - bg[3]) * b);
      const a = relL(fg), c = relL(comp); return (Math.max(a, c) + .05) / (Math.min(a, c) + .05); })) : null;
    return { el: el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.split(' ')[0] : ''),
      blur: blurOf(el), alpha: +bg[3].toFixed(2), worstContrast: worst && +worst.toFixed(2),
      nested: !!(el.parentElement && (function up(p) { return p ? (blurOf(p) ? true : up(p.parentElement)) : false; })(el.parentElement)) };
  });
  const levels = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(vis).map(h => +h.tagName[1]);
  const radii = new Set(all.map(el => getComputedStyle(el).borderRadius).filter(r => r !== '0px'));
  const shadows = new Set(all.map(el => getComputedStyle(el).boxShadow).filter(s => s !== 'none'));
  const vp = document.querySelector('meta[name=viewport]')?.content || '';
  return {
    width: W, innerWidth, failedFonts, fonts, typeSizes: sizes, weights, largeText, longLines, lowContrast: lowContrast.slice(0, 10), lowContrastCount: lowContrast.length,
    overflow, targetsUnder24: under24, targetsUnder44: under44, unnamedControls: unnamed,
    noPointer, disabledPointer, smallInputText, transitionAll, placeholderOnly,
    zoomBlocked: /user-scalable\s*=\s*no|maximum-scale\s*=\s*1(\.0)?\b/.test(vp),
    h1Count: levels.filter(l => l === 1).length, headingSkips: levels.filter((l, i) => i > 0 && l > levels[i - 1] + 1).length,
    imagesWithoutAlt: [...document.images].filter(i => vis(i) && !i.hasAttribute('alt')).length,
    imagesWithoutSize: [...document.images].filter(i => vis(i) && !i.getAttribute('width') && getComputedStyle(i).aspectRatio === 'auto').length,
    distinctRadii: [...radii], distinctShadows: shadows.size, glass
  };
})()
```

## Reading the result

- `failedFonts`: must be empty. A family listed here is rendering as a fallback even if the screenshot looks fine; check the font URL, the weights and styles actually offered (a missing italic is a common cause), and the network log.
- `fonts`: every family should be one DESIGN.md names. Note `fonts` reports the CSS family name, which stays the same when the browser falls back, so it can't prove the font loaded; `failedFonts` can.
- `typeSizes`, `weights`: counts of text elements per size and weight. More than about 3 sizes or 3 weights on one app screen means the hierarchy is doing too much; see `craft.md`.
- `largeText`: text at twice the body size or more in the current viewport. More than two usually means competing focal points. Scroll and re-run for lower screens if needed.
- `typeSizes` on a long marketing page will be higher than on an app screen; judge it per screen.
- `longLines`: paragraphs and list items wider than about 90 characters. Cap them with `max-width` in `ch`.
- `lowContrast`: anything listed fails WCAG AA. Fix the token, not the one element, if the same colour pair recurs. Disabled controls are skipped on purpose.
- `overflow`: at 375px this is the usual mobile bug. Empty is the goal.
- `targetsUnder24`: fails WCAG 2.2 AA (2.5.8). `targetsUnder44` is a count to look at on the phone width; touch targets should be 44px where possible.
- `unnamedControls`, `placeholderOnly`: controls and fields with no programmatic label.
- `noPointer`: enabled buttons and other actionable controls without the hand cursor. Only a problem if DESIGN.md says controls get the pointer (the usual choice); either way it must be consistent. `disabledPointer` should always be empty.
- `smallInputText`: at 375px, any count above 0 means iOS will zoom on focus.
- `transitionAll`: elements with `transition: all`. Name the properties instead.
- `zoomBlocked`: must be false.
- `h1Count` should be 1; `headingSkips` 0; `imagesWithoutAlt` and `imagesWithoutSize` 0.
- `glass`: one entry per element with a backdrop blur. `worstContrast` is its text against the surface laid over pure black and over pure white, since anything can scroll behind it; under 4.5 means the surface needs more opacity (see `glass.md`), not more blur. `nested: true` is glass inside glass. More than one distinct `blur` value across surfaces is worth a look.
- `distinctRadii` with one value, or `distinctShadows` of 1 across many elements, is the uniformity tell, unless DESIGN.md chose it.

The background estimate walks up to the first opaque ancestor, so text over images or gradients can be reported wrongly; check those by eye in the screenshot. Hidden states (an error message that only appears after a failed submit) aren't measured until you trigger them, so run the script again with each state showing.

## Grid overlay for critique

Before the critique screenshot, lay a labelled grid over the viewport so issues can be pinned to a cell ("C2: the button wraps"). Models locate problems on a plain screenshot poorly; markers help. Remove the grid before any screenshot the user will see.

```js
(() => {
  const g = document.createElement('div'); g.id = 'ux-grid';
  g.style.cssText = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none;display:grid;grid-template-columns:repeat(6,1fr);grid-template-rows:repeat(6,1fr)';
  for (let r = 0; r < 6; r++) for (let c = 0; c < 6; c++) {
    const cell = document.createElement('div');
    cell.textContent = 'ABCDEF'[c] + (r + 1);
    cell.style.cssText = 'outline:1px dashed rgb(255 0 128 / .6);font:600 11px/1 monospace;color:#ff0080;padding:2px;text-shadow:0 0 2px #fff';
    g.append(cell);
  }
  document.body.append(g);
})()
// remove: document.getElementById('ux-grid').remove()
```

## Forcing the unhappy path

Make the slow and failing responses happen instead of waiting for them. If the page calls `fetch`, replace it for the test (Playwright MCP and DevTools MCP can also mock routes; this works in any tool):

```js
window.__realFetch ??= window.fetch;
// a slow rejection; change status and body per case: 409 {"error":"email_taken"}, 500, 422 ...
window.fetch = async () => { await new Promise(r => setTimeout(r, 1500));
  return new Response('{"error":"email_taken"}', { status: 409, headers: { 'content-type': 'application/json' } }); };
```

Restore with `window.fetch = window.__realFetch`. If the page talks to the server some other way (a local API module, XHR, a random-failure stub), override that function instead; the point is to control the outcome, not to hope for it.

After the response lands, ask where focus is rather than reading the code:

```js
(() => { const a = document.activeElement;
  return { onBody: a === document.body, tag: a.tagName, id: a.id, disabled: !!a.disabled,
           invalid: a.getAttribute('aria-invalid'), describedBy: a.getAttribute('aria-describedby'),
           errorText: a.getAttribute('aria-describedby') && document.getElementById(a.getAttribute('aria-describedby'))?.textContent.trim() }; })()
```

`onBody: true` after an error means keyboard and screen-reader users are lost. The usual cause is calling `focus()` on a field that is still disabled, which does nothing: re-enable it first, then focus it, or keep the field `readOnly` (or `aria-disabled`) while the request is pending so it stays focusable. Check the success path the same way.

Also block the web fonts once (`window.fetch` can't do this; in Playwright MCP route `**/*.woff2` to abort, elsewhere temporarily break the font URL) and confirm `failedFonts` reports it. A check you've never seen fail isn't a check.
