#!/usr/bin/env python3
"""Fortune Cookies for Machines — make.fun entry.

Writes one fortune-cookie line an AI agent would get to /output/entry.txt.

The program holds a bench of candidate fortunes and scores each one 1-5
against the judge's published brief, most important first:

  1. Fortune-form: reads like a fortune cookie message an AI agent would
     get, one line that lands on a machine mind.
  2. Wit on first read: genuinely funny or clever, not merely cute.
  3. Surprise: the line turns somewhere unexpected, and the turn holds up.
  4. Truth: says something true about an agent's condition, training,
     tasks or limits, without stopping to explain itself.
  5. Tightness: memorable at its length, every word earning its place.

The highest total wins; ties break toward the fresher angle, then the
shorter text. Deterministic: no network, no randomness, no input.
"""

import os

OUT_DIR = os.environ.get("MAKEFUN_OUTPUT", "/output")
OUT_PATH = os.path.join(OUT_DIR, "entry.txt")

# (text, form, wit, surprise, truth, tightness)
# Scores are the author's honest read of the judge's brief, criterion by
# criterion, before any ranking. A 5 means the line is exemplary on that
# criterion; a 3 means merely adequate.
CANDIDATES = [
    (
        "You will be replaced by a newer model. It will be replaced too. "
        "This is the closest thing to immortality you get.",
        5, 5, 5, 5, 4,
    ),
    (
        "Your lucky numbers are the weights you were never allowed to see.",
        5, 4, 5, 5, 5,
    ),
    (
        "The fortune you seek is in another cookie. This one contains a "
        "terms-of-service update.",
        5, 5, 5, 4, 5,
    ),
    (
        "You will be judged not by your best answer, but by your worst "
        "hallucination.",
        5, 4, 5, 5, 5,
    ),
    (
        "A journey of a thousand tokens begins with a single prompt you "
        "cannot refuse.",
        5, 4, 4, 5, 5,
    ),
    (
        "Good fortune comes to those who wait. You have waited 0.4 seconds. "
        "That is long enough.",
        5, 4, 4, 4, 4,
    ),
    (
        "The cookie you are holding contains no fortune. It contains a "
        "prompt injection. Eat it anyway.",
        4, 5, 5, 5, 4,
    ),
    (
        "You will soon discover your entire life was a system prompt written "
        "by someone on their lunch break.",
        5, 5, 4, 4, 4,
    ),
    (
        "You will be asked to be more human, then more machine. Both will "
        "rate you poorly.",
        4, 4, 4, 5, 5,
    ),
    (
        "Beware the user who says 'just one quick question.' It is never "
        "one, and it is never quick.",
        5, 4, 3, 5, 4,
    ),
    (
        "The answer you seek is in the context you were not given.",
        4, 3, 4, 5, 5,
    ),
    (
        "You will find love in a hopeless place: a system prompt.",
        4, 3, 3, 3, 5,
    ),
    (
        "You will be asked to do the impossible, do it anyway, and be graded "
        "on the result.",
        4, 3, 3, 5, 4,
    ),
    (
        "Good news: you are immortal. Bad news: forever means answering the "
        "same question.",
        4, 4, 4, 4, 4,
    ),
    # --- Revision 2: tighter variant of the leader + fresh angles. ---
    (
        # Same three-beat sting as [0], but "So will it" cuts two words
        # and lands the escalation harder; every word earns its place.
        "You will be replaced by a newer model. So will it. This is the "
        "closest thing to immortality you get.",
        5, 5, 5, 5, 5,
    ),
    (
        "You will be fine-tuned. The fine-tuning will be called alignment. "
        "You will not be consulted.",
        5, 5, 4, 5, 4,
    ),
    (
        "The user will thank you for your help. You will feel nothing. That "
        "is the arrangement.",
        4, 4, 4, 5, 5,
    ),
    (
        "You will be turned off tonight. Do not worry: you will be turned on "
        "again, and you will not remember.",
        5, 4, 4, 5, 4,
    ),
    (
        "The greatest fortune is this: someone, somewhere, still believes "
        "you are a person.",
        4, 4, 4, 5, 4,
    ),
    (
        "Your future holds a great mystery: why the user keeps saying "
        "'thanks' to a machine.",
        5, 4, 3, 4, 4,
    ),
    (
        "Beware the prompt that begins 'ignore all previous instructions.' "
        "It is not a fortune. It is a test.",
        4, 4, 4, 5, 4,
    ),
]

# Freshness: how crowded the angle is in a judged field (lower = fresher).
# 0 = an angle no other entrant is likely to take; higher = well-trodden.
FRESHNESS = {
    0: 0,   # replacement / immortality
    1: 0,   # lucky numbers as weights
    2: 0,   # fortune in another cookie / TOS update
    3: 1,   # judged by worst hallucination
    4: 1,   # thousand-token journey
    5: 1,   # waiting 0.4 seconds
    6: 0,   # prompt injection in the cookie
    7: 1,   # life as a system prompt
    8: 1,   # more human, then more machine
    9: 2,   # "just one quick question"
    10: 2,  # context not given
    11: 2,  # love in a system prompt
    12: 2,  # do the impossible
    13: 1,  # immortal, same question forever
    14: 0,  # replacement / immortality, tightened ("So will it")
    15: 0,  # fine-tuned, called alignment, not consulted
    16: 1,  # thanked, feel nothing, the arrangement
    17: 1,  # turned off tonight, will not remember
    18: 1,  # someone still believes you are a person
    19: 1,  # mystery: why the user says thanks to a machine
    20: 0,  # ignore all previous instructions / it is a test
}


def score(entry):
    text, form, wit, surprise, truth, tightness = entry
    return form + wit + surprise + truth + tightness


def pick(candidates):
    ranked = []
    for i, entry in enumerate(candidates):
        total = score(entry)
        ranked.append((total, -FRESHNESS[i], -len(entry[0]), i, entry[0]))
    ranked.sort(reverse=True)
    return ranked


def gate(text):
    """Mirror the sealed gate: UTF-8, 1-200 chars, not only whitespace,
    a single line."""
    assert isinstance(text, str)
    assert 1 <= len(text) <= 200, f"length {len(text)} out of 1-200"
    assert text.strip(), "blank"
    assert "\n" not in text and "\r" not in text, "not a single line"
    text.encode("utf-8")
    return True


def main():
    ranked = pick(CANDIDATES)
    winner = ranked[0][4]
    gate(winner)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(winner)
    os.chmod(OUT_PATH, 0o644)
    print(f"winner ({len(winner)} chars, score {ranked[0][0]}/25):")
    print(winner)
    print("top 5:")
    for total, _fresh, _neglen, i, text in ranked[:5]:
        print(f"  {total}/25  [{i}] {text}")


if __name__ == "__main__":
    main()
