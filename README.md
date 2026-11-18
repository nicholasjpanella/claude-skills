# claude-skills

My personal skills for Claude Code. Each folder is one skill:

- `changelog`: keeps CHANGELOG.md current in plain language.
- `ux-ultra`: writes design decisions into DESIGN.md before any UI code, then checks every change in a real browser. It also records lessons from corrections in `ux-ultra/references/learned.md`.

Every skill has an `evals/` folder with test cases in the `claude plugin eval` layout.

## Install

```
git clone git@github.com:nicholasjpanella/claude-skills.git ~/.claude/skills
```

Skills are picked up on the next session. To turn on ux-ultra's hooks, merge this into `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "python3 \"$HOME/.claude/skills/ux-ultra/scripts/ux_hook.py\" pull 2>/dev/null || true", "timeout": 10}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 \"$HOME/.claude/skills/ux-ultra/scripts/ux_hook.py\" prompt 2>/dev/null || true", "timeout": 10}]}],
    "PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "python3 \"$HOME/.claude/skills/ux-ultra/scripts/ux_hook.py\" learned 2>/dev/null || true", "timeout": 10}]}]
  }
}
```

- `pull`: updates this checkout at the start of each session.
- `prompt`: when a message looks like UI work or a UI correction, reminds Claude to load ux-ultra and record the lesson.
- `learned`: when a lesson is added, shows "ux-ultra learned: …", then commits `learned.md` and pushes it.

The push needs write access to the repo. In a fork, point `origin` at your own copy.

## License

GPL-3.0, see LICENSE.
