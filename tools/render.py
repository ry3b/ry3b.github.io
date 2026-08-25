r"""data/cv.json -> cv.tex.

The document body is identical across styles; a style is purely a preamble
that defines \cvhead, \cventry, \cvpaper, \courseline and the cvbullets env.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex import esc, fill, daterange, sortkey  # noqa: E402

import styles  # noqa: E402


def contact(p):
    bits = []
    if p.get("email"):
        bits.append(r"\href{mailto:%s}{%s}" % (p["email"], esc(p["email"])))
    if p.get("email_school"):
        bits.append(r"\href{mailto:%s}{%s}" % (p["email_school"], esc(p["email_school"])))
    if p.get("site"):
        bits.append(r"\href{https://%s}{%s}" % (p["site"], esc(p["site"])))
    if p.get("github"):
        bits.append(r"\href{https://github.com/%s}{github.com/%s}" % (p["github"], esc(p["github"])))
    if p.get("phone"):
        bits.append(esc(p["phone"]))
    return r"\contactsep{}".join(bits)


def bullets(items):
    if not items:
        return ""
    lines = [r"\begin{cvbullets}"]
    lines += [r"  \item %s" % esc(b) for b in items]
    lines.append(r"\end{cvbullets}")
    return "\n".join(lines)


def plain(text):
    """Resume text goes through a parser, so no em/en dashes in the copy."""
    return str(text or "").replace(" \u2014 ", ", ").replace(" \u2013 ", ", ")


def entry(dates, title, subtitle, location):
    return r"\cventry{%s}{%s}{%s}{%s}" % (dates, title, subtitle, location)


def education(rows, sep="--"):
    out = []
    for e in sorted(rows, key=sortkey, reverse=True):
        dates = daterange(e.get("start"), e.get("end"), sep=sep)
        if e.get("expected"):
            dates = "Expected " + dates
        out.append(entry(
            dates,
            fill(e.get("institution"), "institution"),
            fill(e.get("degree"), "degree"),
            esc(e.get("location", "")),
        ))
        out.append(bullets(e.get("details")))
    return out


def research(rows, sep="--"):
    out = []
    for r in sorted(rows, key=sortkey, reverse=True):
        sub = fill(r.get("org"), "organization")
        if r.get("advisor"):
            sub += r" \; \emph{advisor:} %s" % esc(r["advisor"])
        out.append(entry(
            daterange(r.get("start"), r.get("end"), sep=sep),
            fill(r.get("role"), "role"),
            sub,
            esc(r.get("location", "")),
        ))
        out.append(bullets(r.get("highlights")))
    return out


def papers(rows, self_name):
    out = []
    for p in sorted(rows, key=lambda p: str(p.get("year", "")), reverse=True):
        authors = ", ".join(
            r"\textbf{%s}" % esc(a) if a == self_name else esc(a)
            for a in p.get("authors", [])
        )
        venue = ", ".join(x for x in [esc(p.get("venue", "")), esc(str(p.get("year", "")))] if x)
        links = r"\contactsep{}".join(
            r"\href{%s}{%s}" % (url, esc(name))
            for name, url in (p.get("links") or {}).items() if url
        )
        out.append(r"\cvpaper{%s}{%s}{%s}{%s}" % (
            fill(p.get("title"), "title"), authors, venue, links))
    return out


def projects(rows):
    out = []
    for pr in sorted(rows, key=lambda p: str(p.get("year", "")), reverse=True):
        name = fill(pr.get("name"), "name")
        if pr.get("url"):
            name = r"\href{%s}{%s}" % (pr["url"], name)
        meta = "\\contactsep{}".join(x for x in [esc(pr.get("tech", "")), esc(str(pr.get("year", "")))] if x)
        out.append(entry(meta, name, esc(pr.get("blurb", "")), ""))
    return out


def simple(rows, key="text"):
    """awards / talks / teaching: {text, detail, year}."""
    out = []
    for row in sorted(rows, key=lambda r: str(r.get("year", "")), reverse=True):
        out.append(entry(
            esc(str(row.get("year", ""))),
            fill(row.get(key), key),
            esc(row.get("detail", "")),
            "",
        ))
    return out


def coursework(areas, resume_only=False):
    out = []
    for area in areas:
        courses = [c for c in area.get("courses", [])
                   if not resume_only or c.get("resume")]
        if not courses:
            continue
        listing = ", ".join(
            (r"\textbf{%s}" % esc(c["name"]) if c.get("grad") else esc(c["name"]))
            for c in courses
        )
        out.append(r"\courseline{%s}{%s}" % (esc(area.get("area", "")), listing))
    return out


def skills(rows):
    out = []
    for s in rows:
        if s.get("items"):
            out.append(r"\courseline{%s}{%s}" % (
                esc(s.get("area", "")), ", ".join(esc(i) for i in s["items"])))
    return out


def section(title, blocks):
    blocks = [b for b in blocks if b.strip()]
    if not blocks:
        return ""
    return "\n".join([r"\section{%s}" % esc(title)] + blocks) + "\n"


def document(style_name, head, sections):
    parts = [styles.STYLES[style_name]["preamble"], r"\begin{document}", head]
    parts += [section(title, blocks) for title, blocks in sections]
    parts.append(r"\end{document}")
    return "\n".join(b for b in parts if b.strip()) + "\n"


def keep(rows):
    """Entries tagged for the one-page resume."""
    return [r for r in rows if r.get("resume")]


def render_resume(data, style_name="ats"):
    p = data["profile"]
    research_rows = [dict(r, role=plain(r.get("role"))) for r in keep(data.get("research", []))]
    head = r"\cvhead{%s}{%s}" % (fill(p.get("name"), "name"), contact(p))
    summary = [esc(p["resume_summary"])] if p.get("resume_summary") else []
    return document(style_name, head, [
        ("Summary", summary),
        ("Education", education(keep(data.get("education", [])), sep=" - ")),
        ("Experience", research(research_rows, sep=" - ")),
        ("Projects", projects(keep(data.get("projects", [])))),
        ("Skills", skills(data.get("skills", []))),
        ("Relevant Coursework", coursework(data.get("coursework", []), resume_only=True)),
    ])


def render(data, style_name):
    p = data["profile"]
    head = r"\cvhead{%s}{%s}" % (fill(p.get("name"), "name"), contact(p))
    return document(style_name, head, [
        ("Education", education(data.get("education", []))),
        ("Research Experience", research(data.get("research", []))),
        ("Preprints and Publications", papers(data.get("papers", []), p.get("name"))),
        ("Awards and Honors", simple(data.get("awards", []))),
        ("Talks", simple(data.get("talks", []))),
        ("Teaching", simple(data.get("teaching", []))),
        ("Projects", projects(data.get("projects", []))),
        ("Selected Coursework", coursework(data.get("coursework", []))),
        ("Skills", skills(data.get("skills", []))),
    ])


if __name__ == "__main__":
    doc = sys.argv[1] if len(sys.argv) > 1 else "cv"
    style_name = sys.argv[2] if len(sys.argv) > 2 else ("ats" if doc == "resume" else "times")
    out_path = sys.argv[3] if len(sys.argv) > 3 else "-"
    with open("data/cv.json") as fh:
        data = json.load(fh)
    tex = render_resume(data, style_name) if doc == "resume" else render(data, style_name)
    if out_path == "-":
        sys.stdout.write(tex)
    else:
        with open(out_path, "w") as fh:
            fh.write(tex)
        print("wrote", out_path)
