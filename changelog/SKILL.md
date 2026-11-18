---
name: changelog
description: |
  Keep CHANGELOG.md current in plain language whenever code changes that a
  user of the project would notice. Use this after finishing any feature, fix,
  behaviour change, removal or performance work in a repo, right before or as
  part of the commit, even if nobody mentioned the changelog. Also use it when
  the user says "update the changelog", "release notes", "what changed since",
  "cut a release", "bump the version", or asks whether the changelog is up to
  date. Reads version files and git history to pick the right heading
  (version plus date, or a date alone when the project has no version),
  categorises entries, and reconciles the current section against the commits
  so stale, duplicated or reverted entries are fixed. Skip it for pure
  refactors, test-only, CI, formatting or typo changes.
---

# Changelog

A changelog is for the people who use the project, not the people who wrote it. Each entry answers: what can I do now that I couldn't, what works that didn't, what should I watch out for. Commit messages answer a different question (what did the developer change and why), so a changelog is never a reformatted git log, even though git log is where you go to check you have not missed anything.

## When this runs

Two moments:

1. **You just finished a code change** in a repo that has a CHANGELOG (or declares a version). Before you commit, or in the same commit, update the changelog. You know better than anyone what you built and why it matters, and that knowledge evaporates once the task is over. This is the primary moment; do not wait to be asked.
2. **The user asks** for a changelog update, a release, a version bump, or "what changed since X". Here git history is your main source, and the job is as much reconciliation as writing.

Not every change belongs in a changelog. Skip refactors with no behaviour change, test-only changes, CI, formatting, dependency bumps with no user effect, and typo fixes. If you are unsure whether a user would notice, ask whether they could tell the difference without reading the code. If no, leave it out. A changelog padded with internals buries the entries that matter.

## Step 1: gather context

Run the bundled script from the repo:

```
python3 <skill-dir>/scripts/changelog_context.py [repo-path]
```

It prints the declared version and where it came from, the tags, whether the manifest version is ahead of the latest tag, today's date, the existing changelog's sections and format, and the commits since the last release with a heuristic hint per commit (user-visible, internal, revert). It never writes anything. Read the whole report before deciding what to do; the hints are a starting point and your own knowledge of the work outranks them.

If the repo has no changelog and the change is user-visible, create `CHANGELOG.md` in the Keep a Changelog layout (below). If the repo already has a changelog in a different layout, match it exactly. Consistency inside a project matters more than any convention.

## Step 2: pick the heading

**The project declares a version** (package.json, pyproject.toml, Cargo.toml, a VERSION file, and so on):

- Manifest version is ahead of the latest tag, or the user is releasing or bumping now: the current section is `## [X.Y.Z] - YYYY-MM-DD`, with the version from the manifest and today's date. A version heading always carries a date; that is what lets a reader line the changelog up with deployments and bug reports.
- Manifest version equals the latest tag and nobody is releasing: put the work under `## [Unreleased]`. When the version is bumped later, that section is renamed, not rewritten.
- When asked to bump the version, change the manifest too, not just the heading, and keep the two in step.
- If the repo bumps the version and tags it in the same commit as each change, write that change's entries under the new version's heading in that commit. `[Unreleased]` is only for work that will ship in a later bump. Every version tag gets its own section. If the report says tagged releases have no section, their entries have piled up under `[Unreleased]`: split them out by tag before adding anything new.

**Version tags but no version file the script can find** (the version lives somewhere it doesn't check, or only in tags): the project is still versioned. Find the version in the repo, or take it from the latest tag, and follow the rules above. Don't switch to date headings.

**The project has no version** (no manifest version, no version tags): use the date alone, `## 2026-11-06`. One section per day of user-visible change is fine; a tiny project does not need semver to have a history.

**One heading per version or date, never two.** Before adding a heading, check whether it already exists. If today's date section is already there because something shipped earlier in the day, add your entries under it, merging into its existing `### Added` or `### Fixed` groups. The same goes for a version heading that already exists for the release in progress. A changelog with two `## 2026-11-06` sections, or two `[0.3.0]` sections, reads as nobody looking at the file before writing to it, which is exactly the impression this skill exists to prevent.

Never edit a released section's content except to fix a factual error in it. Released sections are a record, and the next section is where corrections go ("Fixed: the 1.3.0 export change broke ...").

## Step 3: write the entries

Group under `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Deprecated`, `### Security`. Only include the groups you have entries for. Breaking changes go first, in `### Changed` or `### Removed`, with the word **Breaking** at the start of the entry so a skim finds them.

Writing rules, with the reason for each:

- **Say what the user gets, not what the code does.** "You can preview what a fetch would do with `--dry-run`" rather than "Add dry_run flag to build_parser". The user does not know what `build_parser` is and should not have to.
- **Name the thing the user touches.** CLI flags, settings, menu items, endpoints, file formats, error messages. Those are the nouns a user searches the changelog for. File paths, function names and class names are not, unless the project is a library and the function is the public API.
- **One entry per change the user would notice**, not per commit. Three commits that together add one feature are one entry. One commit that fixes two unrelated bugs is two entries.
- **Lead with the effect for fixes.** "Fixed a crash when the input file is empty" tells the user whether their problem is solved. "Handle empty file in parser" does not.
- **Plain words.** "Faster" not "optimised". "Removed" not "deprecated and removed". No "enhanced", "improved" or "robust" without saying what changed. If a sentence would read as marketing on a product page, cut the adjectives until it reads as a note from a colleague.
- **No commit hashes, PR numbers or author names** in the entry text unless the project's existing changelog uses them. If it links PRs at the end of entries, keep doing that.
- **Keep the owner's voice.** This file is part of the repo. No "Claude", no "the agent", no attribution of any kind. The project owner wrote this changelog as far as any reader can tell.

### Examples

Commits:

```
feat(export): write ICS from the calendar view
fix(sync): stop duplicating events when the server returns 304
refactor(sync): split SyncClient into fetch and merge
ci: run tests on windows
docs: document ICS export in readme
```

Entries:

```
### Added
- Export any calendar view to an `.ics` file from the share menu, so events open in Apple Calendar, Outlook or Google Calendar.

### Fixed
- Events no longer appear twice after a sync where the server reports nothing changed.
```

The refactor, CI and docs commits produce nothing. The 304 fix became a sentence about what used to happen and what happens now, because that is what a user hitting the bug would search for; the status code is not.

A wrong version of the same section, for contrast:

```
### Added
- Added ICS export to CalendarView (e4f1a9c)
- Split SyncClient into SyncFetcher and SyncMerger
- Added Windows CI job
### Fixed
- Handle HTTP 304 in SyncClient.merge()
```

Every line here describes the code to someone who can already read the code.

## Step 4: reconcile the current section with git

When a section already exists for the work in progress, check it against the commit list before adding to it. Entries drift: someone logs a feature, then reverts it; two people log the same change in different words; a fix gets filed under Added because that was the nearest heading.

- **Reverted commits**: remove their entries entirely. A changelog entry for something that is no longer in the release is a false promise.
- **Duplicates**: merge into one entry in the clearest wording.
- **Miscategorised entries**: move them. A crash fix under Added is a fix.
- **Missing changes**: every user-visible commit since the last release should be represented. Add what is missing.
- **Entries for internals**: remove them, unless the project's existing changelog clearly records internals on purpose.

Do this reconciliation every time, not only on release. It is cheap when the section is short and it is what keeps the release-day job small.

## Step 5: commit

If the code change is not yet committed, the changelog edit belongs in the same commit; a change and its changelog entry are one unit of work. If the code is already committed, make a separate commit in the repo's existing commit style (check `git log --oneline -20`), with a subject like `Update changelog for 0.3.0` or `docs: changelog for --dry-run`, whichever matches the history. Stage the files you changed by name rather than `git add -A`, and look at `git status` first: running tests leaves `__pycache__`, `.pytest_cache` and similar behind, and committing them is the kind of mess the project owner would never make. No attribution lines.

## Layout reference (Keep a Changelog)

```
# Changelog

All notable changes to this project are recorded here.

## [Unreleased]

## [0.3.0] - 2026-11-06

### Added
- ...

### Fixed
- ...

## [0.2.0] - 2025-09-14
...
```

Newest section first. Blank line between sections and between a heading and its list. If the existing file has a link-reference block at the bottom (`[0.3.0]: https://.../compare/v0.2.0...v0.3.0`), add the new version's line there too.

## Output

Report in one or two lines what you added or changed in the changelog and under which heading. If you skipped the changelog because nothing was user-visible, say that in one line so the user knows it was a decision, not an omission.
