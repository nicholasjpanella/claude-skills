# Frosted glass, done on purpose

Glassmorphism is on the tells list because it usually shows up as decoration: translucent cards on a flat background, a blur nobody can see, glows on everything. It can also be the right call. A media tool, a canvas app or a dashboard over live content can use frosted surfaces to say "this floats above the work". Read this file when DESIGN.md chooses glass, or when a project already uses it, and add `glass` to the `allow` line in the tokens block so the lint stops warning about it.

The values below come from one worked example, a canvas app with violet and cyan on smoky glass in dark and light themes. Treat them as a starting point to tune, not a palette to copy.

## When it earns its place

- **There's something behind it worth softening.** Media, a canvas, a map, a soft gradient haze. In the example, soft radial gradients sit behind the panels; over a flat colour, glass is just a grey panel that costs a blur.
- **It marks layers.** Things that float over content (a nav rail, popovers, sheets, controls over media) are glass; the content itself isn't. If every card is glass, nothing floats.
- **The project can afford the blur.** See performance below.

If none of these hold, use an opaque raised surface and say why in the hand-back.

## Readability comes from opacity, not blur

Blur doesn't fix contrast: a bright photo behind a 20% white panel still turns white text unreadable. Make the surface mostly opaque and let the blur be a finish:

| Tier | Example, dark | Example, light | Use |
|---|---|---|---|
| Glass | `#2b2c35` at 86% (`db`) | `#ffffff` at 80% (`cc`) | panels and cards that sit on the canvas |
| Rail | `#25262f` at 88% (`e0`) | `#fafafe` at 88% | nav rail, popovers |
| Raised | `#353640` at 80% | `#ffffff` at 92% | controls inside a glass panel |
| Overlay | `#202129` at 92% (`eb`) | `#ffffff` at 95% (`f2`) | modal sheets |

The higher the layer, the more opaque it is, because more sits behind it. Keep the alpha in the token (an 8-digit hex or `rgb(... / 0.86)`), not as `opacity` on the element, which would fade the text too.

The test: text on a glass surface must pass 4.5:1 against the surface composited over **both** pure black and pure white, since you don't control what scrolls behind it. The browser check's `glass` field reports this; anything under 4.5 needs a more opaque surface, not a stronger blur.

## Blur, edge, shadow

- **One blur radius for surfaces.** For example, `blur(12px)` everywhere a panel is glass. A different radius per component reads as accident. Small exceptions are fine when they're a different kind of thing: a 2px blur under a phone scrim, a small blur on round controls over images.
- **A hairline edge.** Translucent surfaces lose their outline where the background matches them. A 1px border defines the edge: light at 10 to 25% alpha on dark (`#f4f3ff1c`), ink at 15 to 30% on light (`#34344e26`). Light themes need the stronger end.
- **A soft, tinted shadow.** Depth from one direction, tinted towards the palette rather than pure grey: for example, a 6% glow in the accent hue plus a 12% black drop. Sheets get a longer, darker shadow because they sit highest.
- **No glow stacking.** One shadow system. Neon rims, inner glows and gradient borders together are the decorative version this file exists to avoid.

## Scrims for controls over media

A small control over an image or video (an icon button on a thumbnail, a video control strip) can't rely on the surface tiers, because the image can be any colour. Give it its own dark scrim: for example, thumbnail buttons in `black` at 45% with a 15% white border and a small blur, and video controls on a gradient from transparent to `rgb(10 11 14 / 0.72)`. Check them over the brightest and the busiest image you have.

## Gotchas

- **A `backdrop-filter` creates a containing block.** Any `position: fixed` descendant is positioned against the blurred element, not the viewport, and is clipped by it. Render popovers, menus and toasts at the end of `<body>` (a portal) instead of inside a glass panel, and leave a comment there saying why.
- **Don't nest glass.** A blurred element inside a blurred panel only blurs the panel's own fill, which looks muddy and doubles the cost. Inside glass, use the more opaque raised tier with no blur.
- **Performance.** Every blurred layer is redrawn when what's behind it changes. Large or full-screen blurs, blurs over video, and blurred cards in long scrolling lists are the expensive cases. Keep blurred areas few and modest, don't animate the blur radius, and look at scrolling on a mid-range phone if the page has many.
- **Older Safari** needs `-webkit-backdrop-filter` alongside `backdrop-filter`; add both.

## Fallbacks

Some people turn transparency off, some browsers can't blur, and forced-colours mode replaces backgrounds. Make each case solid instead of broken, and add these whenever you build glass:

```css
/* No blur support: the same surface, fully opaque */
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass, .glass-strong, .glass-sheet { background-color: var(--surface-solid); }
}

/* The OS asks for less transparency (Chromium honours this; other browsers ignore it) */
@media (prefers-reduced-transparency: reduce) {
  .glass, .glass-strong, .glass-sheet {
    background-color: var(--surface-solid);
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
  }
}

/* Forced colours: keep a visible edge, let the system pick colours */
@media (forced-colors: active) {
  .glass, .glass-strong, .glass-sheet { border: 1px solid CanvasText; }
}
```

`--surface-solid` is the tier's colour without alpha; define one per theme.

## In DESIGN.md

Record glass as a decision, not a texture: the tiers with their alpha, the one blur radius, the edge and shadow tokens, which components are glass and which aren't, the scrim rule for media, and the fallbacks. Put `glass` on the `allow` line of the tokens block.
