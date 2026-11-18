# Enforcing the lint on every edit

Offer this when the user wants the DESIGN.md rules enforced without relying on anyone remembering to run the lint. It adds a PostToolUse hook to the project's `.claude/settings.json`: after every Write or Edit, the lint runs on the file that changed. With `--hook`, the script reads the hook's JSON from stdin, skips files that aren't UI code, and exits 2 with its findings on stderr only when there are errors. Claude Code shows exit-2 stderr to the model, so it fixes the problem in the next step; warnings never block.

Merge this into the existing `hooks` object rather than replacing the file. Use the absolute path of the installed skill.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /ABSOLUTE/PATH/TO/ux-ultra/scripts/slop_lint.py --hook"
          }
        ]
      }
    ]
  }
}
```

The script finds DESIGN.md by walking up from the edited file. If there is none, it still flags the universal problems (focus outlines removed with nothing in their place, gradient text) but not palette or font drift, since nothing was decided.

This hook only catches what can be seen in source. States, cursor and keyboard behaviour need the browser loop; a project with Playwright can also run a polish spec from a `Stop` hook, which blocks Claude from finishing while it fails. If you set that up, have the script exit 0 when the hook input has `"stop_hook_active": true` (Claude Code overrides a Stop hook after repeated blocks anyway, and a loop wastes the session), and never let it pass by updating snapshots.

Test it once after adding: make a throwaway edit that adds `outline: none` to a CSS file and confirm the next turn sees the error. Remove the edit afterwards.
