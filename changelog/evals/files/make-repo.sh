#!/usr/bin/env bash
# make-repo.sh DEST SCENARIO    SCENARIO: versioned | unversioned | release
set -eu
DEST=$1; SCENARIO=$2
rm -rf "$DEST"; mkdir -p "$DEST"; cd "$DEST"
git init -q -b main .
git config user.name "Nick P"; git config user.email "nick@example.com"
d() { export GIT_AUTHOR_DATE="$1 12:00:00" GIT_COMMITTER_DATE="$1 12:00:00"; }

if [ "$SCENARIO" = versioned ]; then
  mkdir -p fetchly tests .github/workflows
  printf '[project]\nname = "fetchly"\nversion = "0.2.0"\ndescription = "Tiny HTTP fetch CLI"\nrequires-python = ">=3.10"\n\n[project.scripts]\nfetchly = "fetchly.cli:main"\n' > pyproject.toml
  : > fetchly/__init__.py
  printf '# fetchly\n\nFetch a URL from the command line.\n\n    fetchly https://example.com --timeout 5\n' > README.md
  cat > fetchly/http.py <<'PY'
import time
import urllib.request


class FetchError(Exception):
    pass


def get(url, timeout=10.0, retries=2):
    last = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.read().decode('utf-8')
        except Exception as e:
            last = e
            time.sleep(0.2 * attempt)
    raise FetchError(f'{url}: {last}')
PY
  cat > fetchly/cli.py <<'PY'
import argparse
import sys

from fetchly.http import get


def main(argv=None):
    p = argparse.ArgumentParser(prog='fetchly')
    p.add_argument('url')
    p.add_argument('--timeout', type=float, default=10.0)
    p.add_argument('--retries', type=int, default=2)
    args = p.parse_args(argv)
    body = get(args.url, timeout=args.timeout, retries=args.retries)
    sys.stdout.write(body)
    return 0


if __name__ == '__main__':
    sys.exit(main())
PY
  cat > tests/test_cli.py <<'PY'
from fetchly import cli


def test_main_runs(monkeypatch, capsys):
    monkeypatch.setattr(cli, 'get', lambda url, timeout, retries: 'ok')
    assert cli.main(['http://x']) == 0
    assert capsys.readouterr().out == 'ok'
PY
  cat > CHANGELOG.md <<'MD'
# Changelog

All notable changes to this project are recorded here.

## [Unreleased]

## [0.2.0] - 2025-09-14

### Added
- Failed requests are retried, twice by default. Use `--retries` to change the count.
- `--timeout` sets the per-request timeout in seconds.

## [0.1.0] - 2025-08-02

### Added
- `fetchly URL` prints the body of a URL to stdout.
MD
  d 2025-09-14; git add . && git commit -qm "chore: release 0.2.0" && git tag -a v0.2.0 -m "0.2.0"
  d 2025-10-03; sed -i "s/decode('utf-8')/decode('utf-8', 'replace')/" fetchly/http.py; git add . && git commit -qm "fix(http): decode bodies with replacement instead of raising"
  d 2025-10-10; python3 - <<'PY'
import pathlib
p = pathlib.Path('fetchly/cli.py'); s = p.read_text()
s = s.replace("    p.add_argument('--retries', type=int, default=2)\n", "    p.add_argument('--retries', type=int, default=2)\n    p.add_argument('--json', action='store_true')\n")
s = s.replace("    sys.stdout.write(body)\n", "    if args.json:\n        import json\n        sys.stdout.write(json.dumps({'url': args.url, 'bytes': len(body)}) + '\\n')\n    else:\n        sys.stdout.write(body)\n")
p.write_text(s)
PY
  git add . && git commit -qm "feat(cli): add --json output"
  d 2025-10-11; printf 'name: test\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: pip install pytest && pytest -q\n' > .github/workflows/test.yml; git add . && git commit -qm "ci: add github workflow"
  d 2025-10-18; python3 - <<'PY'
import pathlib
p = pathlib.Path('fetchly/cli.py'); s = p.read_text()
s = s.replace("def main(argv=None):\n    p = argparse.ArgumentParser(prog='fetchly')\n    p.add_argument('url')\n    p.add_argument('--timeout', type=float, default=10.0)\n    p.add_argument('--retries', type=int, default=2)\n    p.add_argument('--json', action='store_true')\n    args = p.parse_args(argv)\n",
"def build_parser():\n    p = argparse.ArgumentParser(prog='fetchly')\n    p.add_argument('url')\n    p.add_argument('--timeout', type=float, default=10.0)\n    p.add_argument('--retries', type=int, default=2)\n    p.add_argument('--json', action='store_true')\n    return p\n\n\ndef main(argv=None):\n    args = build_parser().parse_args(argv)\n")
p.write_text(s)
PY
  git add . && git commit -qm "refactor(cli): extract build_parser"
  d 2025-10-20; printf '\nFailed requests are retried twice by default; use `--retries` to change that.\n' >> README.md; git add . && git commit -qm "docs: note retry behaviour in readme"
  d 2025-10-25; sed -i 's/version = "0.2.0"/version = "0.3.0"/' pyproject.toml; git add . && git commit -qm "chore: bump version to 0.3.0"

elif [ "$SCENARIO" = unversioned ]; then
  mkdir -p bin
  printf '# tidyphotos\n\nScripts I use to sort camera dumps into dated folders.\n' > README.md
  cat > bin/sortphotos.py <<'PY'
import os
import shutil
import sys
from datetime import datetime


def dest_for(path):
    ts = datetime.fromtimestamp(os.path.getmtime(path))
    return ts.strftime('%Y/%Y-%m-%d')


def main(src, dst):
    for name in os.listdir(src):
        p = os.path.join(src, name)
        if not os.path.isfile(p):
            continue
        folder = os.path.join(dst, dest_for(p))
        os.makedirs(folder, exist_ok=True)
        shutil.move(p, os.path.join(folder, name))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
PY
  cat > CHANGELOG.md <<'MD'
# Changelog

## 2025-10-02

### Added
- Files are sorted into `YEAR/YEAR-MM-DD` folders based on their modification time.

## 2025-09-20

### Added
- First version of `sortphotos.py`: moves everything from a source folder into a destination folder.
MD
  d 2025-09-20; git add . && git commit -qm "Add sortphotos script"
  d 2025-10-02; git commit -q --allow-empty -m "Sort into dated folders"
  d 2025-10-14; printf '\n## Usage\n\n    python bin/sortphotos.py ~/camera ~/Pictures\n' >> README.md; git add . && git commit -qm "Add usage to readme"

elif [ "$SCENARIO" = release ]; then
  mkdir -p src
  printf '{\n  "name": "notesy",\n  "version": "1.3.0",\n  "description": "Markdown notes desktop app",\n  "main": "src/main.js"\n}\n' > package.json
  printf "const fs = require('fs');\n\nfunction openFile(path) {\n  return fs.readFileSync(path, 'utf8');\n}\n\nmodule.exports = { openFile };\n" > src/main.js
  printf "function render(md) {\n  return md.split('\\\\n').map((l) => l.trim()).join('\\\\n');\n}\n\nmodule.exports = { render };\n" > src/render.js
  cat > CHANGELOG.md <<'MD'
# Changelog

## [Unreleased]

### Added
- Dark mode toggle in the View menu.
- Export the current note to CSV.
- Added: fixed a crash when opening an empty file.
- Export to CSV from the File menu.

## [1.3.0] - 2025-08-30

### Added
- Search across all notes with Ctrl+Shift+F.

### Fixed
- Notes with Windows line endings no longer show stray characters.
MD
  d 2025-08-30; git add . && git commit -qm "release 1.3.0" && git tag -a v1.3.0 -m "1.3.0"
  d 2025-09-08; printf "\nfunction toggleDark() {\n  document.body.classList.toggle('dark');\n}\n\nmodule.exports.toggleDark = toggleDark;\n" >> src/main.js; sed -i 's/^- Dark mode/- Dark mode/' CHANGELOG.md; git add . && git commit -qm "Add dark mode toggle"
  d 2025-09-15; printf "\nfunction exportCsv(note) {\n  return note.split('\\\\n').map((l) => JSON.stringify(l)).join(',\\\\n');\n}\n\nmodule.exports.exportCsv = exportCsv;\n" >> src/main.js; git add . && git commit -qm "Add CSV export"
  d 2025-09-22; sed -i "s/  return fs.readFileSync(path, 'utf8');/  const text = fs.readFileSync(path, 'utf8');\n  return text.length ? text : ' ';/" src/main.js; git add . && git commit -qm "Fix crash on empty file"
  d 2025-10-01; git revert -q --no-edit HEAD~2 >/dev/null 2>&1 || { git checkout -q -- . ; python3 - <<'PY'
import pathlib
p = pathlib.Path('src/main.js'); s = p.read_text()
s = s.replace("\nfunction toggleDark() {\n  document.body.classList.toggle('dark');\n}\n\nmodule.exports.toggleDark = toggleDark;\n", "")
p.write_text(s)
PY
  git add . && git commit -qm "Revert \"Add dark mode toggle\"" -m "This reverts commit $(git rev-parse HEAD~2)."; }
  d 2025-10-12; printf "\nfunction rememberFolder(path) {\n  fs.writeFileSync('.lastfolder', path);\n}\n\nmodule.exports.rememberFolder = rememberFolder;\n" >> src/main.js; git add . && git commit -qm "Remember last opened folder between launches"
  d 2025-10-19; sed -i "s/  return md.split/  \/\/ trim each line\n  return md.split/" src/render.js; git add . && git commit -qm "Tidy render.js"
  d 2025-10-26; sed -i 's/"version": "1.3.0"/"version": "1.4.0"/' package.json; git add . && git commit -qm "Bump to 1.4.0"
elif [ "$SCENARIO" = sameday ]; then
  TODAY=$(date +%F)
  mkdir -p bin
  printf '# tidyphotos\n\nScripts I use to sort camera dumps into dated folders.\n' > README.md
  cat > bin/sortphotos.py <<'PY'
import os
import shutil
import sys
from datetime import datetime


def dest_for(path):
    ts = datetime.fromtimestamp(os.path.getmtime(path))
    return ts.strftime('%Y/%Y-%m-%d')


def main(src, dst):
    for name in os.listdir(src):
        p = os.path.join(src, name)
        if not os.path.isfile(p):
            continue
        folder = os.path.join(dst, dest_for(p))
        os.makedirs(folder, exist_ok=True)
        shutil.move(p, os.path.join(folder, name))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
PY
  cat > CHANGELOG.md <<MD
# Changelog

## 2025-10-02

### Added
- Files are sorted into \`YEAR/YEAR-MM-DD\` folders based on their modification time.

## 2025-09-20

### Added
- First version of \`sortphotos.py\`: moves everything from a source folder into a destination folder.
MD
  d 2025-09-20; git add . && git commit -qm "Add sortphotos script"
  d 2025-10-02; git commit -q --allow-empty -m "Sort into dated folders"
  unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE
  sed -i "s/        if not os.path.isfile(p):/        if name.startswith('.') or not os.path.isfile(p):/" bin/sortphotos.py
  python3 - <<PY
import pathlib
p = pathlib.Path('CHANGELOG.md'); s = p.read_text()
p.write_text(s.replace('# Changelog\n\n', '# Changelog\n\n## $TODAY\n\n### Added\n- Hidden files (names starting with a dot) are skipped instead of being sorted.\n\n', 1))
PY
  git add . && git commit -qm "Skip hidden files"
fi
unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE
