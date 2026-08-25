#!/usr/bin/env python3
"""Build cv.pdf, resume.pdf and the generated page regions from data/cv.json.

    python3 tools/build.py            # everything
    python3 tools/build.py --check    # report gaps in the data, build nothing
    python3 tools/build.py --pages    # skip LaTeX (fast, for HTML work)

Style per document is set below; both read the same data.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, ".build")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import render  # noqa: E402
import render_html  # noqa: E402

CV_STYLE = os.environ.get("CV_STYLE", "times")
RESUME_STYLE = os.environ.get("RESUME_STYLE", "ats")

REGION = "<!-- BEGIN:generated {0} -->{1}\n    <!-- END:generated {0} -->"


def load():
    with open(os.path.join(ROOT, "data", "cv.json")) as fh:
        return json.load(fh)


def check(data):
    """Fields that render as a red [marker] in the PDFs."""
    gaps = []
    for e in data.get("education", []):
        if not (e.get("start") and e.get("end")):
            gaps.append("education: %s has no dates" % e.get("institution", "?"))
    for r in data.get("research", []):
        if not (r.get("start") and r.get("end")):
            gaps.append("research: %s has no dates" % r.get("org", "?"))
        if not r.get("highlights"):
            gaps.append("research: %s has no bullets (the resume leans on these)" % r.get("org", "?"))
    if not any(s.get("items") for s in data.get("skills", [])):
        gaps.append("skills: empty, so the section is hidden on the resume")
    return gaps


def latex(doc, style, out_name):
    # PDFs are committed, so pin the embedded timestamp to the data file's mtime:
    # rebuilding unchanged data then produces byte-identical output, not a diff.
    env = dict(os.environ,
               SOURCE_DATE_EPOCH=str(int(os.path.getmtime(os.path.join(ROOT, "data", "cv.json")))),
               FORCE_SOURCE_DATE="1")
    tex_path = os.path.join(BUILD, "%s.tex" % doc)
    tex = render.render_resume(data, style) if doc == "resume" else render.render(data, style)
    with open(tex_path, "w") as fh:
        fh.write(tex)
    proc = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "%s.tex" % doc],
        cwd=BUILD, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        errors = [ln for ln in proc.stdout.splitlines() if ln.startswith("!")]
        raise SystemExit("LaTeX failed on %s:\n%s" % (doc, "\n".join(errors[:10]) or proc.stdout[-1500:]))
    shutil.copyfile(os.path.join(BUILD, "%s.pdf" % doc), os.path.join(ROOT, out_name))
    pages = subprocess.run(["pdfinfo", os.path.join(ROOT, out_name)],
                           capture_output=True, text=True).stdout
    n = next((int(l.split()[1]) for l in pages.splitlines() if l.startswith("Pages:")), 0)
    return out_name, n


def page(path, name, body):
    full = os.path.join(ROOT, path)
    with open(full) as fh:
        html = fh.read()
    pattern = re.compile(
        r"<!-- BEGIN:generated %s -->.*?<!-- END:generated %s -->" % (name, name), re.S)
    if not pattern.search(html):
        raise SystemExit("no generated region for %r in %s" % (name, path))
    updated = pattern.sub(lambda m: REGION.format(name, "\n" + body if body else ""), html)
    if updated != html:
        with open(full, "w") as fh:
            fh.write(updated)
        return path + " (updated)"
    return path + " (unchanged)"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report data gaps only")
    ap.add_argument("--pages", action="store_true", help="skip the LaTeX build")
    args = ap.parse_args()

    data = load()
    gaps = check(data)

    if args.check:
        print("\n".join("gap: " + g for g in gaps) or "no gaps")
        raise SystemExit(0)

    os.makedirs(BUILD, exist_ok=True)
    if not args.pages:
        for doc, style, out in [("cv", CV_STYLE, "cv.pdf"), ("resume", RESUME_STYLE, "resume.pdf")]:
            name, pages = latex(doc, style, out)
            note = "  <- should be 1 page" if out == "resume.pdf" and pages != 1 else ""
            print("built %s (%s style, %d page%s)%s"
                  % (name, style, pages, "" if pages == 1 else "s", note))

    print(page("papers/index.html", "papers",
               render_html.papers(data.get("papers", []), data["profile"].get("name"))))
    print(page("projects/index.html", "projects", render_html.projects(data.get("projects", []))))
    print(page("coursework/index.html", "coursework", render_html.coursework(data.get("coursework", []))))

    if gaps:
        print("\n%d gap%s in the data:" % (len(gaps), "" if len(gaps) == 1 else "s"))
        print("\n".join("  - " + g for g in gaps))
