#!/usr/bin/env python3
"""Self-check for slop_lint.py: python3 test_slop_lint.py"""
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import slop_lint as L

DESIGN = """# Design
```tokens
color.paper   #F6F3EE   background   # a comment
color.accent  #2F6B4F
font.body     "Source Sans 3"
allow         glass
ban           arrow-link
```
"""

SLOP = """export default function Hero() {
  return <section className="bg-gradient-to-r from-indigo-500 to-blue-500">
    <p className="uppercase tracking-widest text-xs">New</p>
    <p className="uppercase tracking-wider">Fast</p>
    <p className="tracking-widest uppercase">Safe</p>
    <h1 className="bg-clip-text text-transparent">Elevate</h1>
    <a href="/x">Learn more →</a>
    <span>🚀</span>
    <div className="rounded-2xl shadow-lg backdrop-blur" /><div className="rounded-2xl shadow-lg backdrop-blur" />
    <div className="rounded-2xl shadow-lg fade-up" /><div className="rounded-2xl shadow-lg fade-up" />
    <div className="rounded-2xl fade-up animate-in" /><div className="rounded-2xl" />
  </section>
}
"""
CSS = """.btn { color: #2f6b4f; background: #f00; font-family: Inter, sans-serif; outline: none; }
#fab {
  color: #F6F3EE;
}
"""
CLEAN_CSS = """.btn { color: var(--accent); font-family: "Source Sans 3", sans-serif; }
.btn:focus-visible { outline: 2px solid #2F6B4F; }
@media (prefers-reduced-motion: reduce) { * { transition: none; } }
"""

with tempfile.TemporaryDirectory() as d:
    root = pathlib.Path(d)
    (root / ".git").mkdir()
    (root / "DESIGN.md").write_text(DESIGN)
    (root / "src").mkdir()
    (root / "src/Hero.tsx").write_text(SLOP)
    (root / "src/app.css").write_text(CSS)
    (root / "node_modules/x").mkdir(parents=True)
    (root / "node_modules/x/a.css").write_text("a { color: #123456 }")

    design = L.parse_design(root / "DESIGN.md")
    assert design["palette"] == {"#f6f3ee", "#2f6b4f"}, design
    assert design["fonts"] == {"source sans 3"}, design
    assert design["allow"] == {"glass"} and design["ban"] == {"arrow-link"}

    _, found, n = L.run([str(root / "src")])
    rules = {(f["rule"], f["severity"]) for f in found}
    assert n == 2, n  # node_modules skipped
    for want in [("off-palette-color", "error"), ("off-token-font", "error"), ("focus-removed", "error"),
                 ("default-accent", "warn"), ("gradient-text", "warn"), ("arrow-link", "error"),
                 ("emoji-icon", "warn"), ("uppercase-eyebrow", "warn"), ("single-radius", "warn"),
                 ("default-shadow", "warn"), ("fade-up-everywhere", "warn"), ("no-reduced-motion", "warn")]:
        assert want in rules, (want, sorted(rules))
    assert not any(f["rule"] == "glass" for f in found), "allowed rule still reported"
    offp = [f for f in found if f["rule"] == "off-palette-color"]
    msgs = sorted(f["message"].split()[1] for f in offp)
    assert msgs == ["#f00", "from-indigo-500", "to-blue-500"], msgs  # #fab selector and token hexes not flagged

    (root / "src/app.css").write_text(CLEAN_CSS)
    (root / "src/Hero.tsx").unlink()
    _, found, _ = L.run([str(root / "src")])
    assert found == [], found

    # no DESIGN.md: palette/font checks off, default font still warned
    other = root / "other"; other.mkdir(); (other / ".git").mkdir()
    (other / "a.css").write_text(CSS)
    design2, found, _ = L.run([str(other)])
    assert design2["path"] is None
    got = {f["rule"] for f in found}
    assert "off-palette-color" not in got and "default-font" in got and "focus-removed" in got, got

    # a :focus rule that itself removes the outline is not a replacement
    (other / "a.css").write_text("a:focus { outline: none; }")
    assert {f["rule"] for f in L.run([str(other)])[1]} >= {"focus-removed"}
    (other / "a.css").write_text("a:focus { outline: none; } a:focus { box-shadow: 0 0 0 2px #000; }")
    assert "focus-removed" not in {f["rule"] for f in L.run([str(other)])[1]}

    # polish rules
    p = root / "polish"; p.mkdir(); (p / ".git").mkdir()
    (p / "a.html").write_text('<meta name="viewport" content="width=device-width, maximum-scale=1">\n'
                              '<form><button>Save</button><button type="button">Cancel</button></form>\n'
                              '<input onpaste="return false">\n'
                              '<style>.x { transition: all .2s } .y { transition: 200ms } .z { transition: opacity .2s }</style>')
    got = [f["rule"] for f in L.run([str(p)])[1]]
    assert got.count("transition-all") == 2, got  # 'all' and the bare-duration shorthand, not 'opacity'
    for r in ("zoom-blocked", "paste-blocked", "no-cursor-rule"):
        assert r in got, (r, got)
    assert got.count("button-no-type") == 1, got
    (p / "a.html").write_text('<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                              '<button type="button" class="cursor-pointer">Save</button>\n'
                              '<input onpaste="track()">')
    got = {f["rule"] for f in L.run([str(p)])[1]}
    assert not got & {"zoom-blocked", "paste-blocked", "no-cursor-rule", "button-no-type", "transition-all"}, got

    # font shorthand: family after size/line-height is checked; `font: inherit` is not a family
    (p / "a.html").write_text('<style>body { font: 400 17px/1.55 "Roboto", sans-serif } input { font: inherit }'
                              ' .t { font: 16px/24px "Source Sans 3", sans-serif }</style><button type="button" class="cursor-pointer">x</button>')
    (p / "DESIGN.md").write_text(DESIGN)
    got = [(f["rule"], f["message"]) for f in L.run([str(p)])[1]]
    assert [r for r, _ in got if r == "off-token-font"] == ["off-token-font"], got
    assert "roboto" in [m for r, m in got if r == "off-token-font"][0], got

    # stock Tailwind colours: v3 hex and v4 hex copies are flagged, a near-but-chosen colour and greys are not
    q = root / "palette"; q.mkdir(); (q / ".git").mkdir()
    (q / "a.css").write_text(".a { color: #c2410c } .b { color: #ca3500 } .c { color: #b5502a } .d { color: #111827 }")
    got = [f["message"] for f in L.run([str(q)])[1] if f["rule"] == "default-palette"]
    assert len(got) == 2 and "orange-700" in got[0] and "orange-700" in got[1], got
    # with DESIGN.md tokens, Tailwind classes that aren't tokens are off-palette; a class whose swatch is a token is fine
    (q / "DESIGN.md").write_text("```tokens\ncolor.accent #c2410c\ncolor.paper #ffffff\n```\n")
    (q / "a.css").write_text("")
    (q / "b.html").write_text('<p class="text-orange-700 bg-emerald-600">x</p>')
    got = [f["message"] for f in L.run([str(q)])[1] if f["rule"] == "off-palette-color"]
    assert got == ["colour bg-emerald-600 is not a DESIGN.md token"], got

    # a page set entirely in the system stack with no DESIGN.md is an undecided default; with DESIGN.md fonts it's off-token
    s = root / "sys"; s.mkdir(); (s / ".git").mkdir()
    (s / "a.css").write_text("body { font: 17px/1.5 system-ui, sans-serif } code { font-family: ui-monospace, monospace }")
    got = [f["message"] for f in L.run([str(s)])[1] if f["rule"] == "default-font"]
    assert len(got) == 1 and "system stack" in got[0], got

    # glass needs a solid fallback, whether or not the glass itself is allowed
    gl = root / "glass"; gl.mkdir(); (gl / ".git").mkdir()
    (gl / "a.css").write_text(".glass { background: rgb(43 44 53 / .86); backdrop-filter: blur(12px) }")
    assert "glass-no-fallback" in {f["rule"] for f in L.run([str(gl)])[1]}
    (gl / "a.css").write_text(".glass { background: rgb(43 44 53 / .86); backdrop-filter: blur(12px) }\n"
                              "@media (prefers-reduced-transparency: reduce) { .glass { backdrop-filter: none } }")
    assert "glass-no-fallback" not in {f["rule"] for f in L.run([str(gl)])[1]}

    # learned rules: a good line fires (DESIGN.md allow/ban still apply), a bad line is reported, built-in ids can't be overridden
    lm = root / "learned.md"
    lm.write_text('# Learned\n```lint\n// comment\n'
                  '{"id": "learned-lorem", "severity": "warn", "pattern": "lorem ipsum", "ignore_case": true, "message": "filler copy {x}"}\n'
                  '{"id": "learned-bad", "pattern": "(", "message": "x"}\n'
                  '{"id": "gradient-text", "pattern": "x", "message": "x"}\n```\n')
    L.load_learned(lm)
    lr = root / "learned"; lr.mkdir(); (lr / ".git").mkdir()
    (lr / "a.html").write_text("<p>Lorem Ipsum dolor</p>")
    got = L.run([str(lr)])[1]
    assert [f["message"] for f in got if f["rule"] == "learned-lorem"] == ["filler copy {x} (Lorem Ipsum)"], got
    broken = sorted(f["message"] for f in got if f["rule"] == "learned-rule-broken")
    assert len(broken) == 2 and "line 3:" in broken[0] and "line 4: id clashes" in broken[1], broken
    (lr / "DESIGN.md").write_text("```tokens\nallow learned-lorem\n```\n")
    assert "learned-lorem" not in {f["rule"] for f in L.run([str(lr)])[1]}
    L.load_learned(root / "missing.md")
    assert not L.LEARNED and not L.LEARNED_BROKEN

print("ok")
