#!/usr/bin/env python3
"""Lint UI code against the decisions in DESIGN.md.

Flags values that aren't in the design file (colours, fonts) and the
patterns that read as generated defaults when nothing chose them. Reads
the ```tokens block in DESIGN.md; `allow` there silences a rule, `ban`
turns a warning into an error.

Usage:
  slop_lint.py [PATH ...] [--design DESIGN.md] [--json]
  slop_lint.py --hook        # PostToolUse hook: JSON on stdin, exit 2 on errors

Exit status: 0 clean or warnings only, 1 errors (2 in --hook mode).
Standard library only; changes nothing.
"""
import argparse, json, pathlib, re, sys

UI_EXT = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".js", ".ts",
          ".vue", ".svelte", ".astro", ".mdx"}
STYLE_EXT = {".css", ".scss", ".sass", ".less"}
MARKUP_EXT = UI_EXT - STYLE_EXT - {".js", ".ts"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage", ".svelte-kit",
             "vendor", ".turbo", ".cache", ".output", "storybook-static"}
GENERIC_FONTS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif",
                 "ui-serif", "ui-monospace", "ui-rounded", "-apple-system", "blinkmacsystemfont",
                 "inherit", "initial", "unset", "segoe ui", "helvetica", "helvetica neue", "arial",
                 "apple color emoji", "segoe ui emoji", "noto color emoji", "emoji", "math"}
SYSTEM_STACK = {"system-ui", "-apple-system", "blinkmacsystemfont", "ui-sans-serif", "sans-serif"}
DEFAULT_FONTS = {"inter", "roboto", "space grotesk", "poppins", "montserrat", "open sans", "lato",
                 "geist", "dm sans", "plus jakarta sans"}

RULES = {  # id: (default severity, scope, message)
    "off-palette-color": ("error", "file", "colour {x} is not a DESIGN.md token"),
    "off-token-font": ("error", "file", "font {x} is not a DESIGN.md font"),
    "focus-removed": ("error", "file", "focus outline removed and no focus-visible style in this file"),
    "zoom-blocked": ("error", "file", "viewport meta blocks zoom ({x})"),
    "paste-blocked": ("error", "file", "paste is blocked on an input"),
    "transition-all": ("warn", "file", "transition on all properties ({x}); name transform/opacity/colours instead"),
    "button-no-type": ("warn", "file", "<button> without type (submits its form by default)"),
    "no-cursor-rule": ("warn", "project", "buttons exist but no cursor rule anywhere; decide one in DESIGN.md (see base-layer.css)"),
    "default-font": ("warn", "file", "{x} is a default face; DESIGN.md should name it if chosen"),
    "default-accent": ("warn", "file", "default indigo/violet/purple utility {x}"),
    "default-palette": ("warn", "file", "{x}: a stock Tailwind colour picked as-is, not a decision"),
    "gradient-text": ("warn", "file", "gradient-filled text"),
    "arrow-link": ("warn", "file", "arrow appended to link or button text"),
    "emoji-icon": ("warn", "file", "emoji {x} used in markup, likely as an icon"),
    "uppercase-eyebrow": ("warn", "project", "{x} uppercase tracked-out labels (eyebrow chrome)"),
    "single-radius": ("warn", "project", "one radius ({x}) on everything"),
    "default-shadow": ("warn", "project", "the same soft shadow repeated {x} times"),
    "fade-up-everywhere": ("warn", "project", "{x} fade/slide-up entrances"),
    "glass": ("warn", "project", "{x} backdrop blurs (glassmorphism); if chosen, allow it and see references/glass.md"),
    "glass-no-fallback": ("warn", "project", "backdrop blur with no solid fallback (prefers-reduced-transparency or @supports not backdrop-filter)"),
    "middot-meta": ("warn", "project", "{x} 'A · B · C' meta strings"),
    "no-reduced-motion": ("warn", "project", "motion found but no prefers-reduced-motion handling"),
    "learned-rule-broken": ("error", "project", "references/learned.md lint line {x}"),
}
BUILTIN = set(RULES)
LEARNED, LEARNED_BROKEN = [], []  # filled by load_learned(): [(id, regex)], ["n: why"]


def load_learned(path=None):
    """Rules added on the spot: one JSON object per line in the ```lint block of references/learned.md."""
    path = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent.parent / "references" / "learned.md"
    LEARNED.clear(), LEARNED_BROKEN.clear()
    m = re.search(r"```lint\n(.*?)```", path.read_text(encoding="utf-8", errors="replace"), re.S) if path.is_file() else None
    for n, line in enumerate(m.group(1).splitlines() if m else [], 1):
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        try:
            r = json.loads(line)
            rid, sev = r["id"], r.get("severity", "warn")
            if rid in BUILTIN or sev not in ("warn", "error"):
                raise ValueError("id clashes with a built-in rule or severity isn't warn/error")
            rx = re.compile(r["pattern"], re.I if r.get("ignore_case") else 0)
            msg = r["message"].replace("{", "{{").replace("}", "}}") + " ({x})"
        except (ValueError, KeyError, TypeError, re.error) as e:
            LEARNED_BROKEN.append(f"{n}: {e}")
            continue
        RULES[rid] = (sev, "file", msg)
        LEARNED.append((rid, rx))

HEX = re.compile(r"(?<=[\s:,(\[\"'=])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\w-])")
SELECTOR_LINE = re.compile(r"^\s*[^:{;]*\{\s*$")
FONT_DECL = re.compile(r"font-family\s*:\s*([^;}\n]+)|fontFamily\s*:\s*[\[{]?\s*([\"'][^\"']+[\"'])|font-\[['\"]?([^\]'\"]+)"
                       r"|(?<![\w-])font\s*:\s*(?:[^;}\n]*?\s)?[\d.]+(?:px|rem|em|%|pt)(?:\s*/\s*[\d.]+[a-z%]*)?\s+([^;}\n]+)")
FONT_IMPORT = re.compile(r"fonts\.googleapis\.com/css2?\?family=([A-Za-z+]+)|import\s*\{\s*([A-Z][\w_ ,]+)\}\s*from\s*['\"]next/font/google|@fontsource(?:-variable)?/([a-z0-9-]+)")
OUTLINE_OFF = re.compile(r"outline\s*:\s*(none|0)\b|(?<![\w:-])outline-none\b|focus:outline-none")
FOCUS_ON = re.compile(r"focus-visible|focus:ring|focus-within:ring|:focus\s*\{[^}]*(?:outline\s*:(?!\s*(?:none|0\b))|box-shadow)|focus:outline-(?!none)")
ACCENT = re.compile(r"\b(?:bg|text|from|via|to|border|ring|fill|stroke|shadow|outline|decoration|accent|caret)-(?:indigo|violet|purple)-\d{2,3}\b")
GRAD_TEXT = re.compile(r"background-clip\s*:\s*text|bg-clip-text[^\"'`]*text-transparent|text-transparent[^\"'`]*bg-clip-text")
ARROW = re.compile(r"(?:\w|['\"])\s*(?:→|&rarr;|&#8594;)\s*(?:<|['\"`]|$)", re.M)
EMOJI = re.compile("[\U0001F300-\U0001FAFF✨⚡✅]")
EYEBROW = re.compile(r"[\"'`][^\"'`]*\buppercase\b[^\"'`]*\btracking-(?:wide|wider|widest|\[)[^\"'`]*[\"'`]|[\"'`][^\"'`]*\btracking-(?:wide|wider|widest|\[)[^\"'`]*\buppercase\b[^\"'`]*[\"'`]|text-transform\s*:\s*uppercase[^}]*letter-spacing|letter-spacing[^}]*text-transform\s*:\s*uppercase")
RADIUS = re.compile(r"border-radius\s*:\s*([^;}\n]+)|\b(rounded(?:-(?:sm|md|lg|xl|2xl|3xl|\[[^\]]+\]))?)(?![\w-])")
SHADOW = re.compile(r"box-shadow\s*:\s*([^;}\n]+)|\b(shadow(?:-(?:sm|md|lg|xl|2xl))?)(?![\w-])")
FADE = re.compile(r"fade-?up|fadeInUp|slide-?up|data-aos=|initial=\{\{\s*opacity:\s*0\s*,\s*y:", re.I)
GLASS = re.compile(r"backdrop-blur|backdrop-filter\s*:\s*blur")
GLASS_FALLBACK = re.compile(r"prefers-reduced-transparency|@supports\s+not\s*\(+\s*(?:-webkit-)?backdrop-filter")
MIDDOT = re.compile(r"\S · \S[^\n]* · \S")
MOTION = re.compile(r"@keyframes|animation\s*:|transition\s*:|\banimate-|\btransition(?:-\w+)?\b|framer-motion|motion\.\w+")
ZOOM = re.compile(r"user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0)?(?![\d.])")
PASTE = re.compile(r"onpaste\s*=\s*[\"'{][^\"'}]*(?:return\s+false|preventDefault)|onPaste=\{[^}]*preventDefault|['\"]paste['\"][^;]{0,80}?preventDefault|['\"]paste['\"],\s*\w+\)[\s\S]{0,200}?preventDefault")
TRANSITION_ALL = re.compile(r"transition\s*:\s*(?:all\b|[\d.]+m?s\b)|(?<![\w-])transition-all(?![\w-])")
BUTTON_NO_TYPE = re.compile(r"<button(?![^>]*\btype\s*=)[\s>]")
HAS_BUTTON = re.compile(r"<button[\s>]|role=[\"']button[\"']")
CURSOR_RULE = re.compile(r"cursor\s*:|(?<![\w-])cursor-(?:pointer|default)(?![\w-])")
REDUCED = re.compile(r"prefers-reduced-motion|motion-reduce|motion-safe|useReducedMotion|MotionConfig")


TW_CLASS = re.compile(r"(?<![\w-])(?:bg|text|from|via|to|border|ring|fill|stroke|outline|decoration|accent|caret|divide|placeholder)"
                      r"-((?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3})(?![\w-])")
_PALETTE = None


def palette():
    """Tailwind v4 (oklch) and v3 (hex) default swatches: {name: (hex, L, a, b)} in OKLab."""
    global _PALETTE
    if _PALETTE is None:
        p = pathlib.Path(__file__).with_name("tailwind_palette.json")
        _PALETTE = {k: tuple(v) for k, v in json.loads(p.read_text()).items()} if p.is_file() else {}
    return _PALETTE


def oklab(hex6):
    lin = [((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92 for c in bytes.fromhex(hex6[1:7])]
    l, m, s = ((x * lin[0] + y * lin[1] + z * lin[2]) ** (1 / 3) for x, y, z in (
        (0.4122214708, 0.5363325363, 0.0514459929), (0.2119034982, 0.6806995451, 0.1073969566),
        (0.0883024619, 0.2817188376, 0.6299787005)))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def stock_swatch(hex6, max_d=0.012):
    """Name of the chromatic Tailwind swatch this colour copies, if any (greys are too common to flag)."""
    L, a, b = oklab(hex6)
    if (a * a + b * b) ** 0.5 < 0.04:
        return None
    best = min(palette().items(), key=lambda kv: (kv[1][1] - L) ** 2 + (kv[1][2] - a) ** 2 + (kv[1][3] - b) ** 2, default=None)
    if best and ((best[1][1] - L) ** 2 + (best[1][2] - a) ** 2 + (best[1][3] - b) ** 2) ** 0.5 < max_d:
        return best[0]
    return None


def norm_hex(h):
    h = h.lower().lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    return "#" + h[:6]


def find_design(start):
    p = pathlib.Path(start).resolve()
    for d in [p] + list(p.parents) if p.is_dir() else list(p.parents):
        for name in ("DESIGN.md", "design.md", "docs/DESIGN.md"):
            if (d / name).is_file():
                return d / name
        if (d / ".git").exists():
            break
    return None


def parse_design(path):
    """-> dict(palette:set|None, fonts:set|None, allow:set, ban:set)"""
    d = {"palette": None, "fonts": None, "allow": set(), "ban": set(), "path": str(path) if path else None}
    if not path:
        return d
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"```tokens\n(.*?)```", text, re.S)
    if not m:  # no tokens block: every hex in the file counts as decided
        d["palette"] = {norm_hex(h) for h in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", text)} or None
        return d
    palette, fonts = set(), set()
    for line in m.group(1).splitlines():
        line = re.sub(r"(^|\s)#(\s.*|$)", "", line).strip()  # comments are "# ..."; hex values have no space
        if not line:
            continue
        key, _, rest = line.partition(" ")
        if key.startswith("color"):
            palette |= {norm_hex(h) for h in re.findall(r"#[0-9a-fA-F]{3,8}\b", rest)}
        elif key.startswith("font"):
            fonts |= {f.lower() for f in re.findall(r"[\"']([^\"']+)[\"']", rest)} or {rest.strip().lower()}
        elif key in ("allow", "ban"):
            d[key] |= set(rest.split())
    d["palette"], d["fonts"] = palette or None, (fonts - {"none"}) or None
    return d


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def lint_file(path, text, design):
    """File-scope findings: list of (rule, line, detail)."""
    out, ext = [], path.suffix.lower()
    is_style = ext in STYLE_EXT or "<style" in text
    chosen = design["palette"] or set()
    lines = text.split("\n")
    for m in HEX.finditer(text):
        ln = line_of(text, m.start())
        if is_style and SELECTOR_LINE.match(lines[ln - 1]):
            continue
        nh = norm_hex(m.group(0))
        if nh in chosen:
            continue
        if design["palette"]:
            out.append(("off-palette-color", ln, m.group(0)))
        swatch = stock_swatch(nh)
        if swatch:
            out.append(("default-palette", ln, f"{m.group(0)} is Tailwind {swatch.replace('v3-', '')}"))
    if design["palette"]:
        for m in TW_CLASS.finditer(text):
            sw = [palette().get(m.group(1)), palette().get("v3-" + m.group(1))]
            if not any(s and s[0] in chosen for s in sw):
                out.append(("off-palette-color", line_of(text, m.start()), m.group(0)))
    for m in FONT_DECL.finditer(text):
        raw = (m.group(1) or m.group(2) or m.group(3) or m.group(4) or "").strip()
        first = raw.split(",")[0].strip().strip("\"'").replace("_", " ").lower()
        if first in SYSTEM_STACK and not design["fonts"]:
            out.append(("default-font", line_of(text, m.start()), f"{first} (the system stack)"))
            continue
        if not first or first.startswith("var(") or first in GENERIC_FONTS or first.startswith("$") or "theme(" in first:
            continue
        if design["fonts"] and first not in design["fonts"]:
            out.append(("off-token-font", line_of(text, m.start()), first))
        elif first in DEFAULT_FONTS and not (design["fonts"] and first in design["fonts"]):
            out.append(("default-font", line_of(text, m.start()), first))
    for m in FONT_IMPORT.finditer(text):
        for name in re.split(r"[,+]", (m.group(1) or m.group(2) or m.group(3) or "").replace("_", " ")):
            name = name.strip().replace("-", " ").lower()
            if name in DEFAULT_FONTS and not (design["fonts"] and name in design["fonts"]):
                out.append(("default-font", line_of(text, m.start()), name))
    om = OUTLINE_OFF.search(text)
    if om and not FOCUS_ON.search(text):
        out.append(("focus-removed", line_of(text, om.start()), ""))
    for m in TRANSITION_ALL.finditer(text):
        out.append(("transition-all", line_of(text, m.start()), m.group(0).strip()))
    if ext in MARKUP_EXT:
        for m in ZOOM.finditer(text):
            out.append(("zoom-blocked", line_of(text, m.start()), m.group(0)))
        for m in BUTTON_NO_TYPE.finditer(text):
            out.append(("button-no-type", line_of(text, m.start()), ""))
    pm = PASTE.search(text)
    if pm:
        out.append(("paste-blocked", line_of(text, pm.start()), ""))
    for m in ACCENT.finditer(text):
        out.append(("default-accent", line_of(text, m.start()), m.group(0)))
    for m in GRAD_TEXT.finditer(text):
        out.append(("gradient-text", line_of(text, m.start()), ""))
    if ext in MARKUP_EXT:
        for m in ARROW.finditer(text):
            out.append(("arrow-link", line_of(text, m.start()), ""))
        for m in EMOJI.finditer(text):
            out.append(("emoji-icon", line_of(text, m.start()), m.group(0)))
    for rid, rx in LEARNED:
        for m in rx.finditer(text):
            out.append((rid, line_of(text, m.start()), m.group(0)[:60]))
    return out


def lint_project(texts):
    """Project-scope findings from all file texts: list of (rule, detail)."""
    blob = "\n".join(texts)
    out = []
    n = len(EYEBROW.findall(blob))
    if n >= 3:
        out.append(("uppercase-eyebrow", n))
    radii = [(a or b).strip() for a, b in RADIUS.findall(blob)]
    radii = [r for r in radii if r not in ("rounded-full", "9999px", "999px", "50%", "0", "0px", "rounded-none")]
    if len(radii) >= 6 and len(set(radii)) == 1:
        out.append(("single-radius", radii[0]))
    shadows = [(a or b).strip() for a, b in SHADOW.findall(blob)]
    shadows = [s for s in shadows if s not in ("none", "shadow-none")]
    if len(shadows) >= 4 and len(set(shadows)) == 1:
        out.append(("default-shadow", len(shadows)))
    for rule, rx, min_n in (("fade-up-everywhere", FADE, 3), ("glass", GLASS, 2), ("middot-meta", MIDDOT, 3)):
        n = len(rx.findall(blob))
        if n >= min_n:
            out.append((rule, n))
    if GLASS.search(blob) and not GLASS_FALLBACK.search(blob):
        out.append(("glass-no-fallback", ""))
    if HAS_BUTTON.search(blob) and not CURSOR_RULE.search(blob):
        out.append(("no-cursor-rule", ""))
    if MOTION.search(blob) and not REDUCED.search(blob):
        out.append(("no-reduced-motion", ""))
    return out


def severity(rule, design):
    if rule in design["allow"]:
        return None
    return "error" if rule in design["ban"] else RULES[rule][0]


def ui_files(paths):
    for p in paths:
        p = pathlib.Path(p)
        if p.is_file():
            if p.suffix.lower() in UI_EXT:
                yield p
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in UI_EXT and not (set(f.relative_to(p).parts[:-1]) & SKIP_DIRS) \
                    and not f.name.endswith((".min.js", ".min.css", ".d.ts")):
                yield f


def run(paths, design_path=None):
    design = parse_design(design_path or find_design(paths[0] if paths else "."))
    findings, texts = [], []
    for f in ui_files(paths or ["."]):
        text = f.read_text(encoding="utf-8", errors="replace")
        texts.append(text)
        for rule, ln, x in lint_file(f, text, design):
            sev = severity(rule, design)
            if sev:
                findings.append({"rule": rule, "severity": sev, "file": str(f), "line": ln,
                                 "message": RULES[rule][2].format(x=x)})
    for rule, x in lint_project(texts) + [("learned-rule-broken", b) for b in LEARNED_BROKEN]:
        sev = severity(rule, design)
        if sev:
            findings.append({"rule": rule, "severity": sev, "file": None, "line": None,
                             "message": RULES[rule][2].format(x=x)})
    return design, findings, len(texts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--design")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hook", action="store_true")
    a = ap.parse_args()
    load_learned()

    if a.hook:
        try:
            fp = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
        except (ValueError, AttributeError):
            return 0
        if not fp or pathlib.Path(fp).suffix.lower() not in UI_EXT or not pathlib.Path(fp).is_file():
            return 0
        design = parse_design(find_design(fp))
        text = pathlib.Path(fp).read_text(encoding="utf-8", errors="replace")
        errs = [(r, ln, x) for r, ln, x in lint_file(pathlib.Path(fp), text, design) if severity(r, design) == "error"]
        if not errs:
            return 0
        print(f"ux-ultra lint: {len(errs)} error(s) in {fp} (rules from {design['path'] or 'no DESIGN.md'}):", file=sys.stderr)
        for r, ln, x in errs:
            print(f"  line {ln}: [{r}] {RULES[r][2].format(x=x)}", file=sys.stderr)
        return 2

    design, findings, nfiles = run(a.paths, a.design)
    if a.json:
        print(json.dumps({"design": design["path"], "files": nfiles, "findings": findings}, indent=1))
    else:
        print(f"DESIGN.md: {design['path'] or 'not found (palette and font checks off)'}; {nfiles} UI file(s)")
        for f in findings:
            where = f"{f['file']}:{f['line']}" if f["file"] else "project"
            print(f"{f['severity']:5} {where}  [{f['rule']}] {f['message']}")
        e = sum(f["severity"] == "error" for f in findings)
        print(f"{e} error(s), {len(findings) - e} warning(s)")
    return 1 if any(f["severity"] == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
