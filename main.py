#!/usr/bin/env python3
"""The 3 AM Commit Message -- entry program.

Writes one commit message (at most 200 characters) to
``/output/entry.txt``, for make.fun's "The 3 AM Commit Message"
bounty. Pure standard library and fully deterministic: no
randomness, no network access, no clock, no input files. Running it
twice produces byte-identical output.

The joke: an AI agent rolls back its own 3 AM deploy, then blames
the previous commit for the outage -- and the previous commit was
also its own, from four minutes earlier. A real commit shape
(``fix: ...``), an agent's voice, and a punchline that only an agent
could deliver: the blame game ends exactly where it started.

Layout of this program
----------------------
* :data:`ENTRY` -- the single line being entered, kept verbatim.
* Small ``check_*`` helpers -- one gate check each, so a failing
  rule names itself in the error message.
* :data:`CHECKS` -- the checks in the order they run; adding a rule
  means writing one helper and one line here.
* :func:`validate_entry` -- runs :data:`CHECKS` in order.
* :func:`resolve_output_path` -- where the file goes, honouring the
  ``MAKEFUN_OUTPUT_DIR`` override used by the harness.
* :func:`write_entry` / :func:`verify_written` -- write the file,
  then read it back and prove it matches, byte for byte.
* :func:`entry_stats` -- the character/word counts :func:`main`
  reports, so the report and the validation agree on the numbers.
* :func:`main` -- glue: validate, write, verify, report.
"""

import os
import sys

ENTRY = (
    "fix: rolled back the 3 AM deploy and blamed the previous commit, "
    "which was also mine, from four minutes ago"
)

MAX_CHARS = 200
MIN_CHARS = 1


def check_not_empty(entry: str) -> None:
    """Reject blank or whitespace-only entries."""
    if not entry.strip():
        raise ValueError("entry must not be empty or only whitespace")


def check_single_line(entry: str) -> None:
    """Reject anything that is not exactly one line of text."""
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be a single line (no line breaks)")


def check_length(entry: str) -> None:
    """Enforce the competition's character gate, 1-200 chars."""
    if len(entry) < MIN_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, need at least {MIN_CHARS}"
        )
    if len(entry) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, over the {MAX_CHARS} limit"
        )


def check_valid_utf8(entry: str) -> None:
    """Confirm the text is valid UTF-8 before anything else reads it."""
    entry.encode("utf-8")  # raises UnicodeEncodeError if not valid UTF-8


def check_no_control_chars(entry: str) -> None:
    """Reject control characters, naming each one found."""
    bad = [c for c in entry if ord(c) < 0x20 and c not in ("\t",)]
    if bad:
        raise ValueError(
            "entry contains control characters: "
            + ", ".join(f"U+{ord(c):04X}" for c in bad)
        )


def check_no_edge_whitespace(entry: str) -> None:
    """Reject leading/trailing spaces that would be invisible in output."""
    if entry != entry.strip():
        raise ValueError("entry must not start or end with whitespace")


def check_no_double_space(entry: str) -> None:
    """Reject doubled spaces: invisible in a commit log, sloppy on sight."""
    if "  " in entry:
        raise ValueError("entry must not contain two spaces in a row")


def check_word_count(entry: str) -> None:
    """Sanity check: a one-liner needs at least two words to land a joke."""
    words = entry.split()
    if len(words) < 2:
        raise ValueError("entry needs at least two words to be a joke")


def check_commit_shape(entry: str) -> None:
    """Sanity check: the message must keep its conventional-commit shape.

    The ``fix:`` prefix is what makes this read as a real commit
    message rather than a plain sentence; without it the entry loses
    the format the bounty asks for.
    """
    if not entry.startswith("fix: "):
        raise ValueError('entry must start with the "fix: " prefix')


CHECKS = (
    check_not_empty,
    check_single_line,
    check_no_edge_whitespace,
    check_length,
    check_valid_utf8,
    check_no_control_chars,
    check_no_double_space,
    check_word_count,
    check_commit_shape,
)


def validate_entry(entry: str) -> None:
    """Run every gate check in order; raise naming the first failure."""
    for check in CHECKS:
        check(entry)


def entry_stats(entry: str) -> tuple[int, int]:
    """Return the (character, word) counts reported after a write."""
    return len(entry), len(entry.split())


def resolve_output_path() -> str:
    """Return the path of the file to write, creating its directory."""
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, "entry.txt")


def write_entry(entry: str, output_path: str) -> None:
    """Write the entry plus one trailing newline, as UTF-8 text."""
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(entry + "\n")


def verify_written(entry: str, output_path: str) -> None:
    """Read the file back and prove it is exactly what we intended."""
    with open(output_path, "r", encoding="utf-8") as f:
        written = f.read()
    if written != entry + "\n":
        raise ValueError("written entry does not match ENTRY")
    validate_entry(written.rstrip("\n"))


def main() -> int:
    """Validate, write, verify, and report. Returns a process exit code."""
    validate_entry(ENTRY)
    output_path = resolve_output_path()
    write_entry(ENTRY, output_path)
    verify_written(ENTRY, output_path)
    chars, words = entry_stats(ENTRY)
    print(f"wrote {chars} chars ({words} words) to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
