#!/usr/bin/env python3
"""
AI pattern detector for application essays.

A free, offline heuristic checker. It does NOT reproduce GPTZero's model and
cannot prove whether text is AI-written. It scores writing signals that AI text
tends to show (stock vocabulary, contrast frames, even sentence rhythm, stacked
lists, smooth transitions) and points at the sentences that carry them.

Usage:
    python detect.py essay.txt
    python detect.py essay.txt --json
    cat essay.txt | python detect.py -
"""
import json
import re
import statistics
import sys

AI_VOCAB = [
    "delve", "leverage", "leveraging", "tapestry", "pivotal", "foster", "fostering",
    "navigate", "navigating", "landscape", "realm", "testament", "underscore",
    "underscores", "seamless", "seamlessly", "robust", "holistic", "embark",
    "journey", "transformative", "invaluable", "multifaceted", "ever-evolving",
    "fast-paced", "intricate", "meticulous", "meticulously", "showcase", "showcasing",
    "empower", "empowering", "synergy", "paramount", "crucial", "vital", "vibrant",
    "commendable", "noteworthy", "unwavering", "resonate", "resonates", "elevate",
    "spearhead", "spearheaded", "harness", "harnessing", "cutting-edge", "game-changer",
    "nuanced", "profound", "endeavor", "endeavour", "beacon", "cornerstone",
]
TRANSITIONS = [
    "moreover", "furthermore", "additionally", "ultimately", "in essence",
    "in conclusion", "consequently", "notably", "importantly", "overall,",
    "in today's", "in summary",
]
HEDGED = [
    "incredibly", "truly", "deeply", "genuinely", "profoundly", "immensely",
    "remarkably",
]
CONTRAST = [
    r"\bnot (just|only|merely)\b.*\bbut\b",
    r"\brather than\b",
    r"\binstead of (just|merely|simply)\b",
    r"\bit'?s not about\b.*\bit'?s about\b",
    r"\bnot\b[^.]{0,40}\bbut\b",
]
LESSON = [
    r"\b(this|it) taught me (that|the)\b",
    r"\bi learned that (leadership|success|true)\b",
    r"\bleadership (means|is about)\b",
    r"\btrue (success|leadership)\b",
    r"\bthe (importance|value|power) of\b",
]
VIRTUE = [
    r"\bwith (compassion|resilience|determination|integrity|empathy)\b",
    r"\bpassionate about\b",
    r"\bled (them|the team) with\b",
]


def split_paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


def split_sentences(par):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", par.strip())
    return [s.strip() for s in parts if s.strip()]


def words(s):
    return re.findall(r"[A-Za-z0-9$%'’\-,.]+", s)


def sentence_flags(s):
    low = s.lower()
    flags = []
    for w in AI_VOCAB:
        if re.search(r"\b" + re.escape(w) + r"\b", low):
            flags.append(("AI vocabulary", w, 2))
    for t in TRANSITIONS:
        if low.startswith(t) or (", " + t) in low:
            flags.append(("Smooth transition", t, 1))
    for h in HEDGED:
        if re.search(r"\b" + h + r"\b", low):
            flags.append(("Hedged positivity", h, 1))
    for pat in CONTRAST:
        if re.search(pat, low):
            flags.append(("Contrast frame", re.search(pat, low).group(0)[:40], 3))
            break
    for pat in LESSON:
        if re.search(pat, low):
            flags.append(("Generic lesson", re.search(pat, low).group(0), 3))
            break
    for pat in VIRTUE:
        if re.search(pat, low):
            flags.append(("Virtue claim", re.search(pat, low).group(0), 3))
            break
    if "—" in s:
        flags.append(("Em dash", "—", 2))
    if re.search(r"^[A-Z][^:]{0,40}:\s", s):
        flags.append(("Colon reveal", s.split(":")[0][:30], 1))
    # stacked triad: "a, b and c" / "a, b, and c" of short items
    if re.search(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? and \w+(?: \w+)?\b", s) and len(words(s)) < 30:
        flags.append(("Stacked triad", "", 1))
    # long chained actions: 4+ commas in one sentence
    if s.count(",") >= 4:
        flags.append(("Long chained list", f"{s.count(',')} commas", 1))
    return flags


def paragraph_rhythm(sents):
    lens = [len(words(s)) for s in sents]
    if len(lens) < 4:
        return None, lens
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    return cv, lens


def analyse(text):
    pars = split_paragraphs(text)
    all_lens, report, total_pts = [], [], 0
    all_sents = 0
    for i, p in enumerate(pars, 1):
        sents = split_sentences(p)
        all_sents += len(sents)
        cv, lens = paragraph_rhythm(sents)
        all_lens.extend(lens)
        pts, hits = 0, []
        for s in sents:
            f = sentence_flags(s)
            if f:
                hits.append({"sentence": s, "flags": [{"pattern": a, "match": b} for a, b, _ in f]})
                pts += sum(w for _, _, w in f)
        if cv is not None and cv < 0.15:
            pts += 2
            hits.append({"sentence": "(whole paragraph)", "flags": [{"pattern": "Even rhythm", "match": f"length variation {cv:.2f} (<0.15)"}]})
        risk = "Low" if pts <= 1 else "Medium" if pts <= 4 else "High"
        report.append({"paragraph": i, "risk": risk, "points": pts, "sentence_lengths": lens, "hits": hits})
        total_pts += pts
    # whole-text burstiness
    cv_all = (statistics.pstdev(all_lens) / statistics.mean(all_lens)) if len(all_lens) > 2 else 1
    flat = len(all_lens) >= 10 and cv_all < 0.22
    if flat:
        total_pts += 3
    density = total_pts / max(all_sents, 1)
    score = min(100, round(density * 40 + (10 if flat else 0)))
    overall = "Low" if score < 20 else "Medium" if score < 45 else "High"
    return {
        "words": len(re.findall(r"\S+", text)),
        "sentences": all_sents,
        "sentence_length_variation": round(cv_all, 2),
        "pattern_score": score,
        "overall_risk": overall,
        "paragraphs": report,
        "note": "Heuristic pattern score, not an AI-probability. Confirm with GPTZero or Pangram.",
    }


def print_report(r):
    print(f"Overall pattern risk: {r['overall_risk']}  (pattern score {r['pattern_score']}/100)")
    print(f"Words: {r['words']} | Sentences: {r['sentences']} | Sentence-length variation: {r['sentence_length_variation']} (higher = more human-like)")
    print()
    for p in r["paragraphs"]:
        print(f"P{p['paragraph']}: {p['risk']} ({p['points']} pts) lengths={p['sentence_lengths']}")
        for h in p["hits"]:
            pats = "; ".join(f"{f['pattern']}" + (f" [{f['match']}]" if f["match"] else "") for f in h["flags"])
            print(f"   - {pats}\n     \"{h['sentence'][:140]}\"")
    print()
    print(r["note"])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0] if args else "-"
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    res = analyse(text)
    if "--json" in sys.argv:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print_report(res)
