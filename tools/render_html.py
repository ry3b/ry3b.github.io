"""data/cv.json -> the generated regions of papers, projects and coursework pages.

Output matches the markup already used on those pages (.paper, .courses),
so the hand-written CSS keeps working untouched.
"""
from html import escape as e

IND = " " * 4


def _link(url, label):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(url), e(label))


def papers(rows, self_name):
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
