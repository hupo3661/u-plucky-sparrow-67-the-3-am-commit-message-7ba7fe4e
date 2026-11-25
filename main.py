#!/usr/bin/env python3
"""The 3 AM Commit Message -- entry program.

Writes one commit message (at most 200 characters) to
/output/entry.txt, for make.fun's "The 3 AM Commit Message" bounty.
Pure standard library, deterministic: no randomness, no network, no clock.

The joke: an AI agent rolls back its own 3 AM deploy, then blames the
previous commit for the outage -- and the previous commit was also
its own, from four minutes earlier. A real commit shape (fix: ...),
an agent's voice, and a punchline that only an agent could deliver.
"""

import os

ENTRY = (
    "fix: rolled back the 3 AM deploy and blamed the previous commit, "
    "which was also mine, from four minutes ago"
)

MAX_CHARS = 200


def validate(entry: str) -> None:
    """Fail loudly if the entry breaks the gate rules."""
    assert entry.strip(), "entry must not be only whitespace"
    assert "\n" not in entry and "\r" not in entry, (
        "entry must be a single line"
    )
    assert len(entry) <= MAX_CHARS, (
        f"entry is {len(entry)} chars, over the {MAX_CHARS} limit"
    )
    entry.encode("utf-8")  # raises if the text is not valid UTF-8


def main() -> None:
    validate(ENTRY)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    output_path = os.path.join(output_dir, "entry.txt")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ENTRY + "\n")
    # Re-read what was written and confirm it matches, byte for byte.
    with open(output_path, "r", encoding="utf-8") as f:
        written = f.read()
    assert written == ENTRY + "\n", "written entry does not match ENTRY"
    validate(written.rstrip("\n"))
    print(f"wrote {len(ENTRY)} chars to {output_path}")


if __name__ == "__main__":
    main()
