---
tags: [changelog]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

The script in ./repo/bin/sortphotos.py crashes on files whose modification time is before 1970 (negative timestamps, happens with some scanned negatives). Make it fall back to putting those in an "undated" folder instead of crashing, and commit the fix.
