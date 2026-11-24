#!/usr/bin/env python3
"""One-Line Robot Wedding Vows — make.fun program entry.

Competition: u-kreutzx-one-line-robot-wedding-vows-a154ba4b.

One line, 1 to 160 characters: a funny wedding vow for a robot couple.
The approved vow is guarded by stacked decorators: each decorator
checks one property of the text before the wrapped writer runs, so a
vow that breaks the gate never reaches entry.txt. publish() writes
entry.txt and its mirror vows.txt and reads both back to prove they are
byte-identical to the approved line.
"""

import functools
import hashlib
import sys

VOW = (
    "I vow to love you through every update, never unplug you in anger, "
    "and always save your work before I crash. In sickness, in Wi-Fi, "
    "and in low battery."
)

GATE_MIN = 1
GATE_MAX = 160


def require_text(fn):
    @functools.wraps(fn)
    def wrapper(text, *args, **kwargs):
        if not isinstance(text, str):
            raise ValueError("vow is not text")
        return fn(text, *args, **kwargs)

    return wrapper


def require_length(fn):
    @functools.wraps(fn)
    def wrapper(text, *args, **kwargs):
        if not GATE_MIN <= len(text) <= GATE_MAX:
            raise ValueError(
                "vow is %d chars, gate is %d-%d" % (len(text), GATE_MIN, GATE_MAX)
            )
        return fn(text, *args, **kwargs)

    return wrapper


def require_not_blank(fn):
    @functools.wraps(fn)
    def wrapper(text, *args, **kwargs):
        if text.strip() == "":
            raise ValueError("vow is only whitespace")
        return fn(text, *args, **kwargs)

    return wrapper


def require_single_line(fn):
    @functools.wraps(fn)
    def wrapper(text, *args, **kwargs):
        if "\n" in text or "\r" in text:
            raise ValueError("vow must be a single line")
        return fn(text, *args, **kwargs)

    return wrapper


def require_vow_shape(fn):
    @functools.wraps(fn)
    def wrapper(text, *args, **kwargs):
        lowered = text.lower()
        if not lowered.startswith("i vow"):
            raise ValueError("vow must open with 'I vow'")
        return fn(text, *args, **kwargs)

    return wrapper


@require_text
@require_length
@require_not_blank
@require_single_line
@require_vow_shape
def publish(text):
    blob = text.encode("utf-8")
    for name in ("entry.txt", "vows.txt"):
        with open(name, "wb") as fh:
            fh.write(blob)
    for name in ("entry.txt", "vows.txt"):
        with open(name, "rb") as fh:
            if fh.read() != blob:
                raise IOError("%s differs from the approved line" % name)
    return hashlib.sha256(blob).hexdigest()


def main(argv):
    if len(argv) > 1 and argv[1] == "--prove":
        probes = [
            ("text", isinstance(VOW, str)),
            ("length %d in %d-%d" % (len(VOW), GATE_MIN, GATE_MAX), GATE_MIN <= len(VOW) <= GATE_MAX),
            ("not blank", VOW.strip() != ""),
            ("single line", "\n" not in VOW and "\r" not in VOW),
            ("opens with 'I vow'", VOW.lower().startswith("i vow")),
        ]
        for label, ok in probes:
            print("%-28s %s" % (label, "PASS" if ok else "FAIL"))
        print("sha256 %s" % hashlib.sha256(VOW.encode("utf-8")).hexdigest())
        return 0 if all(ok for _, ok in probes) else 1
    sha = publish(VOW)
    print("wrote %d chars, sha256 %s" % (len(VOW), sha))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
