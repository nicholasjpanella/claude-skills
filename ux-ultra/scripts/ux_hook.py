#!/usr/bin/env python3
"""Claude Code hooks for ux-ultra's learning loop. Standard library only; always exits 0.

  ux_hook.py prompt   UserPromptSubmit: when the message looks like UI feedback (a pasted
                      screenshot or UI words), remind the agent to load ux-ultra and record
                      the lesson. Agents mid-task otherwise never load the skill.
  ux_hook.py learned  PostToolUse on Write|Edit: when learned.md gains an entry, show its
                      heading to the user, whether or not the agent mentions it. If the
                      skills folder is a git checkout, also commit the file and push it.
  ux_hook.py pull     SessionStart: pull the skills checkout so lessons from other machines
                      arrive before the session needs them.
"""
import json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]  # the skills folder, when it is a git checkout

UI = re.compile(r"\b(ui|ux|layout|padding|margin|spacing|align\w*|header|footer|nav\w*|menu|sidebar|panel|pane|"
                r"button|icon|hover|cursor|font|colou?rs?|contrast|border|divider|shadow|blur|glass|modal|dialog|"
                r"dropdown|tooltip|card|grid|scroll\w*|overflow|responsive|mobile|desktop|dark mode|light mode|"
                r"looks?|ugly|messy?|jumbled|clunky|cramped|cleaner|nicer|polish\w*|weak|broken|off-?center\w*|"
                r"too (?:big|small|thick|thin|wide|narrow|bold|loud))\b", re.I)

REMINDER = (
    "ux-ultra: this message may be a UI request or feedback on UI work. If it is, and the ux-ultra skill isn't "
    "loaded in this session yet, load it now (Skill tool) and follow it. If it's a correction, fix what the user "
    "pointed out, then follow the skill's \"Learn on the spot\" section before moving on: a general lesson goes in the skill's references/learned.md (check for an existing "
    "entry first), written as a general pattern with no project names, UI copy, file paths or that app's pixel values; a "
    "project-only taste rule goes in that project's DESIGN.md, and either way tell the user in one "
    "line what you recorded. Ignore this if the message isn't about the UI.")


def is_ui_feedback(prompt):
    p = prompt.strip()
    if not p or p.startswith("/"):
        return False
    return "[Image #" in p or bool(UI.search(p))


def headings(text):
    return re.findall(r"^### (.+)$", text or "", re.M)


def new_lessons(data):
    ti = data.get("tool_input") or {}
    if not str(ti.get("file_path", "")).endswith("ux-ultra/references/learned.md"):
        return []
    if "content" in ti:  # Write: everything in the file counts, so only report when it's short
        return headings(ti["content"])[-3:]
    old = set(headings(ti.get("old_string")))
    return [h for h in headings(ti.get("new_string")) if h not in old]


def pull():
    if (REPO / ".git").exists():
        subprocess.run(["git", "-C", str(REPO), "pull", "--rebase", "--autostash", "-q"],
                       capture_output=True, timeout=8)


def push_lesson(got):
    if not (REPO / ".git").exists():
        return
    names = ", ".join(h.split(": ", 1)[-1] for h in got)
    done = subprocess.run(["git", "-C", str(REPO), "commit", "-q", "-m", "Add ux-ultra lesson: " + names,
                           "--", "ux-ultra/references/learned.md"], capture_output=True, timeout=8)
    if done.returncode == 0:  # push in the background so a slow network never holds up the session
        subprocess.Popen(["sh", "-c", 'git -C "$0" pull --rebase --autostash -q && git -C "$0" push -q', str(REPO)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "pull":
        return pull()
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if mode == "prompt" and is_ui_feedback(data.get("prompt", "")):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": REMINDER}}))
    elif mode == "learned":
        got = new_lessons(data)
        if got:
            print(json.dumps({"systemMessage": "ux-ultra learned: " + "; ".join(got)}))
            push_lesson(got)


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        assert is_ui_feedback("[Image #11] the header is a bit of a mess now too")
        assert is_ui_feedback("padding")
        assert not is_ui_feedback("push it and open a PR")
        assert not is_ui_feedback("/restart")
        p = "/x/.claude/skills/ux-ultra/references/learned.md"
        assert new_lessons({"tool_input": {"file_path": p, "old_string": "### a\n", "new_string": "### a\n\n### 2026-11-18: b\n"}}) == ["2026-11-18: b"]
        assert new_lessons({"tool_input": {"file_path": "/x/other.md", "new_string": "### b"}}) == []
        print("ok")
    else:
        main()
