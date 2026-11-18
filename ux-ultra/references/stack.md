# Stack facts that change how UI code should be written

Version facts go stale within months. Each row has the date it was last checked; when the installed packages say otherwise (`node_modules/<pkg>/package.json`, a framework's bundled docs, a design system's `llms.txt` or MCP), trust the installed packages. Re-check this file every few months.

## Frameworks and libraries

| Fact | Rule | Checked |
|---|---|---|
| Next.js 16.3 writes a managed `AGENTS.md` that points at docs bundled for the installed version, and warns that its APIs differ from older training data | In a Next project, read `AGENTS.md` and the bundled docs before writing routing, data or caching code | 2026-11-13 |
| React 19.3: `<ViewTransition>` and Fragment Refs are stable; React Compiler 1.0 is stable | Use `<ViewTransition>` for page and state transitions instead of hand-rolled animation libraries when the project is on 19.3+; still honour reduced motion | 2026-11-13 |
| shadcn/ui CLI v4: Base UI became the default primitives in July 2026 (earlier projects use Radix) | Read `components.json` before assuming Radix or Base UI APIs; the two differ | 2026-11-13 |
| Base UI 1.x is published as `@base-ui/react` | Import from the installed package name, not an older one you remember | 2026-11-13 |
| Tailwind CSS v4: buttons use `cursor: default` by Preflight; v4.3 adds `scrollbar-gutter-stable` | Keep the cursor base layer; use `scrollbar-gutter-stable` on scroll containers that would shift when a scrollbar appears | 2026-11-13 |
| ESLint 10 removed the old `.eslintrc` format | Generate only `eslint.config.*` | 2026-11-13 |
| Vite 8 forwards browser console errors to the terminal when it detects a coding agent | Read the dev-server output after loading a page; errors may already be there | 2026-11-13 |
| Astro 6 has a built-in Fonts API | In Astro, load fonts through it rather than hand-written `@font-face` | 2026-11-13 |

## CSS features safe to use

| Feature | Status | Rule | Checked |
|---|---|---|---|
| Anchor positioning | Baseline (Jan 2026) | Tooltips, menus and popovers can anchor in CSS without a positioning library | 2026-11-13 |
| `field-sizing: content` | Baseline (Jun 2026) | Auto-growing textareas without JavaScript | 2026-11-13 |
| `:has()`, CSS nesting | Widely available | Safe everywhere | 2026-11-13 |
| Scroll-driven animations | Baseline (Oct 2026) | Allowed, but they move on their own: wrap them in `prefers-reduced-motion: no-preference` | 2026-11-13 |
| Customisable `<select>` (`appearance: base-select`) | Chrome and Safari only | Progressive enhancement; the plain select must still work | 2026-11-13 |
| Cross-document view transitions, `contrast-color()`, style queries | Interop 2026 targets, not yet everywhere | Use with a fallback | 2026-11-13 |

## Tokens

| Fact | Rule | Checked |
|---|---|---|
| The DTCG design-token format reached a stable version (2025.10), with themes and OKLCH colour; it's a W3C Community Group report | If a project has DTCG `.tokens.json`, keep it as the source of truth and have DESIGN.md refer to it | 2026-11-13 |
| Google's DESIGN.md format (alpha) pairs YAML tokens with prose reasons | Compatible with this skill's DESIGN.md; keep the prose short and the components out of it | 2026-11-13 |
