# Application Writing Skills for Claude

Two Claude skills for writing scholarship, university and job applications in your own words.

| Skill | What it does |
|---|---|
| [`application-writing-coach`](application-writing-coach/SKILL.md) | Asks you questions, organises your own sentences, fixes spelling and grammar, fits the word limit and reviews your answers like an assessor. It never writes content for you. |
| [`ai-pattern-detector`](ai-pattern-detector/SKILL.md) | A free, offline script that flags AI-writing patterns paragraph by paragraph and shows the exact sentences. |

## Why "your own words"

These skills came out of preparing a Chevening application. Answers that an AI had edited scored up to 100% AI in GPTZero. Answers the author wrote herself, with only grammar fixes and reordering, scored 98–100% human. The coach skill is built around that workflow.

## About the detector

`ai-pattern-detector` is a heuristic, **not** a copy of GPTZero and not an AI-probability. It catches stock AI phrasing: contrast frames ("not X but Y"), generic lessons ("leadership means…"), virtue claims, AI vocabulary, em dashes and flat sentence rhythm.

**Known blind spot:** it does not reliably catch human text that an AI has polished. Always confirm with [GPTZero](https://gptzero.me/) or [Pangram](https://www.pangram.com/).

Run it directly:

```bash
python ai-pattern-detector/scripts/detect.py essay.txt
python ai-pattern-detector/scripts/detect.py essay.txt --json
```

## Install

- **Claude.ai:** zip a skill folder (e.g. `application-writing-coach/`) and upload it as a custom skill.
- **Claude Code:** copy the folder into `~/.claude/skills/`.
