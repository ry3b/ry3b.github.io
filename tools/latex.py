"""LaTeX helpers: escaping, dates, and loud markers for data I don't have yet."""

SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(s):
    """Escape a plain string for LaTeX."""
    return "".join(SPECIALS.get(c, c) for c in str(s))


def fill(value, label):
    """Escaped value, or a red [label?] marker when the data is missing."""
    return esc(value) if value else r"\FILL{%s}" % esc(label)


def month(stamp):
    """'2026-05' -> 'May 2026'; '2026' -> '2026'; 'present' -> 'Present'."""
    stamp = (stamp or "").strip()
    if not stamp:
        return ""
    if stamp.lower() == "present":
        return "Present"
    parts = stamp.split("-")
    if len(parts) == 2 and parts[1].isdigit() and 1 <= int(parts[1]) <= 12:
        return "%s %s" % (MONTHS[int(parts[1])], parts[0])
    return esc(stamp)


def daterange(start, end, label="dates", sep="--"):
    a, b = month(start), month(end)
    if a and b:
        return "%s%s%s" % (a, sep, b) if a != b else a
    if a or b:
        return a or b
    return r"\FILL{%s}" % esc(label)


def sortkey(entry):
    """Newest first. 'present' sorts above any real date."""
    end = (entry.get("end") or "").strip().lower()
    if end == "present":
        return (9999, 99)
    src = end or (entry.get("start") or "")
    parts = src.split("-")
    year = int(parts[0]) if parts and parts[0].isdigit() else 0
    mon = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (year, mon)
