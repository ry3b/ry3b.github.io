"""data/cv.json -> the generated regions of papers, projects and coursework pages.

Output matches the markup already used on those pages (.paper, .courses),
so the hand-written CSS keeps working untouched.
"""
import re

from html import escape as e

IND = " " * 4


def _link(url, label):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(url), e(label))


def papers(rows, self_name):
    rows = [p for p in rows if (p.get("title") or "").strip()]
    if not rows:
        return IND + '<p class="muted small">nothing published yet...</p>'

    def block(p):
        authors = ", ".join(
            '<span class="self">%s</span>' % e(a) if a == self_name else e(a)
            for a in p.get("authors", [])
        )
        venue = ", ".join(x for x in [e(p.get("venue", "")), e(str(p.get("year", "")))] if x)
        links = " &middot; ".join(
            _link(url, name) for name, url in (p.get("links") or {}).items() if url)
        out = [IND + '<div class="paper">']
        out.append(IND * 2 + '<div class="title">%s</div>' % e(p.get("title", "")))
        if authors:
            out.append(IND * 2 + '<div class="authors">%s</div>' % authors)
        if venue:
            out.append(IND * 2 + '<div class="venue">%s</div>' % venue)
        if links:
            out.append(IND * 2 + '<div class="links">%s</div>' % links)
        out.append(IND + "</div>")
        return "\n".join(out)

    groups = [("preprints &amp; manuscripts", ["preprint", "in preparation", "submitted", ""]),
              ("publications", ["published"])]
    chunks = []
    for heading, statuses in groups:
        rows_in = [p for p in rows if (p.get("status") or "").lower() in statuses]
        if not rows_in:
            continue
        rows_in.sort(key=lambda p: str(p.get("year", "")), reverse=True)
        chunks.append(IND + "<h2>%s</h2>" % heading)
        chunks += [block(p) for p in rows_in]
    return "\n".join(chunks)


def projects(rows):
    rows = [pr for pr in rows if (pr.get("name") or "").strip()]
    if not rows:
        return IND + '<p class="muted small">nothing here yet...</p>'
    out = []
    for p in sorted(rows, key=lambda p: str(p.get("year", "")), reverse=True):
        title = e(p.get("name", ""))
        if p.get("url"):
            title = _link(p["url"], p.get("name", ""))
        meta = " &middot; ".join(x for x in [e(p.get("tech", "")), e(str(p.get("year", "")))] if x)
        out.append(IND + '<div class="paper">')
        out.append(IND * 2 + '<div class="title">%s</div>' % title)
        if p.get("blurb"):
            out.append(IND * 2 + '<div class="authors">%s</div>' % e(p["blurb"]))
        if meta:
            out.append(IND * 2 + '<div class="venue">%s</div>' % meta)
        out.append(IND + "</div>")
    return "\n".join(out)


def coursework(areas):
    out = []
    for area in areas:
        courses = area.get("courses", [])
        if not courses:
            continue
        out.append(IND + "<h2>%s</h2>" % e(area.get("area", "").lower()))
        out.append(IND + '<ul class="courses">')
        for c in courses:
            if c.get("grad"):
                out.append(IND * 2 + "<li><mark>%s (Graduate)</mark>%s</li>"
                           % (e(c.get("name", "")), '<span class="code"> %s</span>' % e(c.get("code", ""))))
            else:
                out.append(IND * 2 + '<li>%s <span class="code">%s</span></li>'
                           % (e(c.get("name", "")), e(c.get("code", ""))))
        out.append(IND + "</ul>")
    return "\n".join(out)


MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def month_name(stamp):
    """'2026-06' -> 'June 2026'. Anything else is passed through."""
    parts = (stamp or "").split("-")
    if len(parts) == 2 and parts[1].isdigit() and 1 <= int(parts[1]) <= 12:
        return "%s %s" % (MONTHS[int(parts[1])], parts[0])
    return e(stamp or "")


def live(posts):
    """Published posts, newest first. Dates are YYYY-MM, so a string sort works."""
    return sorted([p for p in posts if not p.get("draft") and p.get("slug")],
                  key=lambda p: p.get("date", ""), reverse=True)


def post_index(posts):
    rows = live(posts)
    if not rows:
        return IND + '<p class="muted small">nothing written yet...</p>'
    out = [IND + '<ul class="posts">']
    for p in rows:
        out.append(IND * 2 + "<li>")
        out.append(IND * 3 + '<span class="date">%s</span>' % month_name(p.get("date")))
        out.append(IND * 3 + '<a class="post-title" href="%s.html">%s</a>'
                   % (e(p["slug"]), e(p.get("title", ""))))
        out.append(IND * 2 + "</li>")
    out.append(IND + "</ul>")
    return "\n".join(out)


def paragraphs(body):
    """Blank lines inside a <p> become paragraph breaks, so a post typed as
    plain text with a blank line between paragraphs renders the way it was
    written. Everything else in the body is left alone."""
    def split(m):
        parts = [s.strip() for s in re.split(r"\n\s*\n", m.group(1)) if s.strip()]
        return "\n\n".join("<p>%s</p>" % s for s in parts)
    return re.sub(r"<p>(.*?)</p>", split, body, flags=re.S)


def post_page(post, name):
    """A whole post page. The body is the author's HTML, passed through except
    that blank lines inside a <p> split it into paragraphs."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{description}">
    <title>{title} &mdash; {name}</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>

    <a class="back" href="/blog">&larr; blog</a>

    <!-- generated from data/cv.json by tools/build.py; edit the post there -->
    <article class="prose">
        <h1>{title}</h1>
        <p class="muted small" style="margin-top:-2px">{date}</p>

        {body}

    </article>

</body>
</html>
""".format(description=e(post.get("description") or post.get("title", "")),
           title=e(post.get("title", "")),
           name=e(name.lower()),
           date=month_name(post.get("date")),
           body=paragraphs(post.get("body", "").strip()))
