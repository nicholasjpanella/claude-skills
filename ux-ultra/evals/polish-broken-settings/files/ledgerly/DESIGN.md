# Design

Ledgerly is a bookkeeping app for sole traders who do their own books on a Sunday evening. The design should feel like a well-kept paper ledger: quiet, exact, nothing shouting. The one thing it must make easy is finding a number and trusting it.

## Direction

"Ledger paper." Off-white paper, ink-green accents like a bank stamp, figures set in tabular numerals. The memorable thing is the ruled ledger table; everything else stays plain.

## Tokens

```tokens
color.paper      #FAF8F2   page background
color.surface    #FFFFFF   panels, inputs
color.ink        #1F2A24   body text
color.muted      #5D6A62   secondary text, captions
color.accent     #1E6B4A   primary buttons, links, focus ring
color.danger     #A63A2B   errors, destructive actions only
color.rule       #DDD8CC   borders, table rules

font.display     "Literata"
font.body        "Public Sans"

radius           4px 8px
shadow           0 1px 0 #DDD8CC

ban              default-accent gradient-text
```

## Type

| Role | Family | Size / line height | Weight |
|---|---|---|---|
| Page title | Literata | 32/40 | 600 |
| Section heading | Literata | 20/28 | 600 |
| Body | Public Sans | 16/24 | 400 |
| Label, caption | Public Sans | 14/20 | 500 |

Figures use `font-variant-numeric: tabular-nums`.

## Space, radius, elevation

Spacing scale 4, 8, 12, 16, 24, 32, 48. Inputs and buttons use the 4px radius, panels the 8px one. Elevation is a single bottom rule, never a soft shadow; hierarchy comes from spacing and type.

## Motion

None on load. Buttons and inputs change colour over 120ms. Respect prefers-reduced-motion.

## Components

| Component | Source | States |
|---|---|---|
| Button | `.btn`, `.btn-primary`, `.btn-danger` in styles.css | default, hover, focus-visible, disabled, busy (label changes to the action in progress) |
| Text field | `.field` in styles.css | default, focus-visible, disabled, error (message under the field, linked with aria-describedby) |
| Panel | `.panel` in styles.css | none |
| Notice | `.notice`, `.notice-error`, `.notice-ok` | appears after an action, announced with role="status" or role="alert" |

## Voice

Sentence case. Buttons say what happens: "Save name", "Delete account". Errors say what went wrong and what to do: "We couldn't save your email. Check your connection and try again." No exclamation marks, no apologies.

## Don't

- No soft drop shadows or gradients.
- No icons in buttons.
- No modal without focus trapping and Escape to close.
