---
name: ai-pattern-detector
description: Free offline check of an essay or application answer for AI-writing patterns, paragraph by paragraph, with the exact sentences flagged. Use when the user asks "does this sound AI", "check for AI", "AI detector", "is this AI generated" on scholarship, university or job application text. Not a GPTZero replacement; always confirm with GPTZero or Pangram. Not for LinkedIn posts.
---

# AI Pattern Detector

Runs `scripts/detect.py`, a heuristic checker that scores the writing signals AI text tends to show and points at the sentences carrying them.

## CRITICAL rules

1. **Never call this an AI probability.** It is a pattern score. Say "pattern risk", never "X% AI".
2. **Be honest about the blind spot.** The script catches stock AI phrasing (contrast frames, generic lessons, AI vocabulary, flat rhythm). It does **not** catch text that a human wrote and an AI then polished. In testing, an AI-edited essay that GPTZero rated 100% AI scored Low here. Always tell the user to confirm with GPTZero (gptzero.me) or Pangram (pangram.com).
3. **Never rewrite the text yourself to lower the score.** AI rewriting is exactly what real detectors catch. Point at the flagged sentences and ask the user to reword them in their own words (or hand off to the `application-writing-coach` skill).
4. **Quote, don't summarise.** Every flag shows the exact sentence and the pattern name.

## Workflow

1. Save the user's text to a file in the working directory, exactly as given.
2. Run:
   ```bash
   python scripts/detect.py essay.txt
   ```
   Use `--json` if you need structured output.
3. Report in this shape:

   **Overall pattern risk:** Low / Medium / High (pattern score N/100)

   | Para | Risk | Flagged sentence | Pattern |
   |---|---|---|---|

   **Sentence-length variation:** N (below about 0.22 across the whole text reads machine-even).
   **Blind spot:** this check can miss AI-polished text. Confirm with GPTZero or Pangram.
4. For each flagged sentence, say in one line what the pattern is and ask the user what they would say instead, in their own words.

## What the script scores

| Pattern | Weight | Example |
|---|---|---|
| Contrast frame | 3 | "not just X but Y", "rather than" |
| Generic lesson | 3 | "I learned that leadership means…", "this taught me that…" |
| Virtue claim | 3 | "led them with compassion", "passionate about" |
| AI vocabulary | 2 each | delve, leverage, pivotal, foster, tapestry, seamless, robust… |
| Em dash | 2 | dramatic pauses with "—" |
| Even rhythm | 2 / 3 | paragraph of 4+ sentences with near-identical lengths; whole text flat |
| Smooth transition, hedged positivity, colon reveal, stacked triad, long chained list | 1 | "Moreover", "truly", "The result: …" |

Paragraph risk: Low = 0–1 points, Medium = 2–4, High = 5+. The overall score is pattern density per sentence, capped at 100: under 20 Low, 20–44 Medium, 45+ High.

## Reading the result

- **Low here + high in GPTZero** usually means AI-polished text. The fix is for the author to rewrite from their own notes, not to tweak words.
- **Isolated single flags** on otherwise natural text are common false positives; mention them, don't alarm the user.
- Concrete numbers, names, places, uneven sentences and small grammar slips are signs of human writing. Never "fix" them away.

## Troubleshooting

- **Python not found:** try `python3 scripts/detect.py essay.txt`.
- **Text pasted with no line breaks:** the whole text is treated as one paragraph; ask the user for paragraph breaks or split it yourself on obvious topic changes.
