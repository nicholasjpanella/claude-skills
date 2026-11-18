#!/usr/bin/env python3
"""Gather everything needed to update a CHANGELOG: version, tags, existing
sections, and the commits since the last release with hints about which
ones matter to users.

Usage: changelog_context.py [repo-path] [--since REF] [--max N]

Prints a markdown report. Read-only; touches nothing.
"""
import json, os, re, subprocess, sys, pathlib

def sh(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""

def detect_version(repo):
    repo = pathlib.Path(repo)
    checks = [
        ("package.json", lambda t: json.loads(t).get("version")),
        ("pyproject.toml", lambda t: (re.search(r'^\s*version\s*=\s*"([^"]+)"', t, re.M) or [None, None])[1]),
        ("Cargo.toml", lambda t: (re.search(r'^\[package\][^\[]*?^version\s*=\s*"([^"]+)"', t, re.M | re.S) or [None, None])[1]),
        ("setup.cfg", lambda t: (re.search(r'^version\s*=\s*(\S+)', t, re.M) or [None, None])[1]),
        ("setup.py", lambda t: (re.search(r'version\s*=\s*["\']([^"\']+)["\']', t) or [None, None])[1]),
        ("composer.json", lambda t: json.loads(t).get("version")),
        ("manifest.json", lambda t: json.loads(t).get("version")),
        ("pubspec.yaml", lambda t: (re.search(r'^version:\s*(\S+)', t, re.M) or [None, None])[1]),
        ("Chart.yaml", lambda t: (re.search(r'^version:\s*(\S+)', t, re.M) or [None, None])[1]),
        ("VERSION", lambda t: t.strip() or None),
        ("version.txt", lambda t: t.strip() or None),
    ]
    # root first, then one level down for monorepos (engine/pyproject.toml, ui/package.json)
    subdirs = sorted(d for d in repo.iterdir() if d.is_dir() and not d.name.startswith(".") and d.name not in ("node_modules", "vendor", "dist", "build"))
    for base in [repo, *subdirs]:
        for name, fn in checks:
            p = base / name
            if p.is_file():
                try:
                    v = fn(p.read_text())
                except Exception:
                    v = None
                if v:
                    return str(p.relative_to(repo)), str(v)
    return None, None

def find_changelog(repo):
    for name in ("CHANGELOG.md", "CHANGES.md", "HISTORY.md", "changelog.md", "Changelog.md", "CHANGELOG", "CHANGELOG.rst", "NEWS.md"):
        p = pathlib.Path(repo) / name
        if p.exists():
            return p
    return None

HEAD_RX = re.compile(r"^(#{1,3})\s+(.*)$")
VER_RX = re.compile(r"v?(\d+\.\d+(?:\.\d+)?(?:[-+][\w.]+)?)")
DATE_RX = re.compile(r"(\d{4}-\d{2}-\d{2})")

def parse_changelog(path):
    lines = path.read_text().splitlines()
    sections = []
    for i, l in enumerate(lines):
        m = HEAD_RX.match(l)
        if not m or len(m.group(1)) == 1:
            continue
        if len(m.group(1)) == 3 and sections:
            sections[-1]["subheads"].append(m.group(2).strip("# ").strip())
            continue
        title = m.group(2).strip()
        sections.append({
            "line": i + 1, "title": title,
            "version": (VER_RX.search(title) or [None, None])[1] if not re.search(r"unreleased", title, re.I) else "Unreleased",
            "date": (DATE_RX.search(title) or [None, None])[1],
            "subheads": [],
        })
    fmt = "unknown"
    if any(s["version"] == "Unreleased" for s in sections) or any(re.match(r"\[?v?\d+\.\d+", s["title"]) for s in sections):
        fmt = "keep-a-changelog" if any(s["subheads"] for s in sections) else "versioned, flat bullets"
    elif sections and all(s["date"] and not s["version"] for s in sections):
        fmt = "date-stamped headings"
    return sections, fmt, len(lines)

INTERNAL_PATHS = re.compile(r"^(\.github/|\.gitlab-ci|\.circleci|\.pre-commit|Makefile$|Dockerfile|docker-compose|\.editorconfig|\.gitignore|tox\.ini|noxfile|\.eslintrc|\.prettierrc|ruff\.toml|setup\.cfg|tests?/|spec/|__tests__/|.*\.test\.|.*\.spec\.|.*_test\.go$|test_.*\.py$|.*/fixtures/|docs?/|README|CONTRIBUTING|CHANGELOG|LICENSE)", re.I)
INTERNAL_SUBJ = re.compile(r"^(chore|ci|test|tests|style|refactor|docs|build)(\(|:|\b)|\b(typo|lint|format|formatting|reformat|bump deps|update deps|dependabot)\b", re.I)
USER_SUBJ = re.compile(r"^(feat|fix|perf|security)(\(|:|\b)|\b(add|added|support|fix|fixed|fixes|remove|removed|deprecate|breaking|faster|speed|rename|default|option|flag|command)\b", re.I)

def commits(repo, since, maxn):
    rng = f"{since}..HEAD" if since else "HEAD"
    raw = sh(repo, "log", f"--max-count={maxn}", "--date=short", "--format=%x1e%H%x1f%ad%x1f%an%x1f%s%x1f%b", "--name-only", rng)
    out = []
    for block in raw.split("\x1e"):
        if not block.strip():
            continue
        head, _, files = block.partition("\n")
        parts = head.split("\x1f")
        if len(parts) < 5:
            continue
        h, date, author, subj, body = parts[:5]
        body, _, _ = body.partition("\n\n")  # body before name-only list is already separated by git; keep first paragraph
        fl = [f.strip() for f in files.strip().splitlines() if f.strip() and "\x1f" not in f]
        all_internal = bool(fl) and all(INTERNAL_PATHS.search(f) for f in fl)
        revert_of = re.search(r"This reverts commit ([0-9a-f]{7,40})", block)
        hint = "revert" if (subj.lower().startswith("revert") or revert_of) else \
               "internal (paths)" if all_internal else \
               "internal (subject)" if INTERNAL_SUBJ.search(subj) and not USER_SUBJ.search(subj) else \
               "user-visible?" if USER_SUBJ.search(subj) else "unclear"
        out.append({"hash": h[:8], "date": date, "author": author, "subject": subj, "body": body.strip(), "files": fl, "hint": hint, "reverts": revert_of.group(1)[:8] if revert_of else None})
    return out

def main():
    args = sys.argv[1:]
    repo = pathlib.Path(args[0]) if args and not args[0].startswith("--") else pathlib.Path.cwd()
    since = None; maxn = 60
    if "--since" in args: since = args[args.index("--since") + 1]
    if "--max" in args: maxn = int(args[args.index("--max") + 1])
    top = sh(repo, "rev-parse", "--show-toplevel")
    if not top:
        print("not a git repository:", repo); sys.exit(1)
    repo = pathlib.Path(top)
    src, ver = detect_version(repo)
    tags = sh(repo, "tag", "--sort=-v:refname").splitlines()
    last_tag = sh(repo, "describe", "--tags", "--abbrev=0")
    last_tag_date = sh(repo, "log", "-1", "--format=%ad", "--date=short", last_tag) if last_tag else ""
    head_date = sh(repo, "log", "-1", "--format=%ad", "--date=short")
    dirty = sh(repo, "status", "--porcelain")
    cl = find_changelog(repo)
    sections, fmt, nlines = parse_changelog(cl) if cl else ([], "none", 0)
    last_released = next((s for s in sections if s["version"] and s["version"] != "Unreleased"), None)
    cl_last_touch = sh(repo, "log", "-1", "--format=%H", "--", str(cl.relative_to(repo))) if cl else ""

    if since is None:
        if last_tag: since = last_tag; basis = f"last tag {last_tag}"
        elif cl_last_touch: since = cl_last_touch; basis = f"last commit that touched {cl.name} ({cl_last_touch[:8]}); check that it corresponds to the last section"
        else: since = None; basis = "no tag and no changelog history, so the whole history (capped)"
    else:
        basis = f"--since {since}"
    cs = commits(repo, since, maxn)

    print(f"# Changelog context for {repo.name}\n")
    ver_tags = [t for t in tags if re.fullmatch(r"v?\d+\.\d+(\.\d+)?([-+][\w.]+)?", t)]
    if ver: print(f"- Version source: {src} -> **{ver}**")
    elif ver_tags: print(f"- Version source: no version file found, but version tags exist (latest {ver_tags[0]}): the project is versioned. Use `[X.Y.Z] - <date>` headings that match the tags, not dates.")
    else: print("- Version source: none found (project does not declare a version; use date-stamped headings)")
    print(f"- Tags: {', '.join(tags[:5]) if tags else 'none'}" + (f"; latest reachable: {last_tag} ({last_tag_date})" if last_tag else ""))
    if ver and last_tag:
        tv = VER_RX.search(last_tag)
        if tv and tv.group(1) != ver: print(f"- Version in manifest ({ver}) is ahead of latest tag ({tv.group(1)}): a release of **{ver}** is in progress, so the current section should be `[{ver}] - <date>`")
        elif tv: print(f"- Manifest version equals latest tag: new work is unreleased. Use `[Unreleased]` unless the user is bumping now.")
    print(f"- Today: {__import__('datetime').date.today().isoformat()}; HEAD commit date: {head_date}")
    print(f"- Working tree: {'clean' if not dirty else 'DIRTY, uncommitted changes present:'}")
    if dirty: print("  " + "\n  ".join(dirty.splitlines()[:15]))
    print(f"\n## Existing changelog\n")
    if cl:
        print(f"- File: {cl.name} ({nlines} lines), format: {fmt}")
        for s in sections[:8]:
            print(f"- line {s['line']}: `{s['title']}`" + (f" ({', '.join(s['subheads'])})" if s['subheads'] else ""))
        if last_released: print(f"- Last released section: {last_released['version']} ({last_released['date'] or 'no date'})")
        have = {s["version"] for s in sections if s["version"]}
        missing = [t for t in ver_tags if VER_RX.search(t).group(1) not in have]
        if missing: print(f"- **{len(missing)} tagged release(s) have no section** ({', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}). Their entries are probably sitting under `[Unreleased]`: split them out by tag, using `git log <prev-tag>..<tag>` for each.")
    else:
        print("- No changelog file found. Create CHANGELOG.md (Keep a Changelog layout) if the change is worth recording.")
    print(f"\n## Commits since {basis} ({len(cs)} shown, newest first)\n")
    print("Hints are heuristics from paths and subjects. Your own knowledge of what you just built outranks them.\n")
    for c in cs:
        print(f"- `{c['hash']}` {c['date']} **{c['subject']}** [{c['hint']}" + (f", reverts {c['reverts']}" if c['reverts'] else "") + "]")
        if c["body"]: print(f"  - body: {c['body'][:200].replace(chr(10), ' ')}")
        print(f"  - files: {', '.join(c['files'][:8])}" + (" ..." if len(c['files']) > 8 else ""))
    reverted = {c["reverts"] for c in cs if c["reverts"]}
    if reverted: print(f"\nReverted commits in range (drop their entries): {', '.join(sorted(reverted))}")

if __name__ == "__main__":
    main()
