#!/usr/bin/env python3
"""Read and use the CCoP 2026 OSCAL catalog (standard library only).

Examples:
    python examples/read_catalog.py summary
    python examples/read_catalog.py show 5.9.2
    python examples/read_catalog.py search "multi-factor"
    python examples/read_catalog.py deadlines
    python examples/read_catalog.py recurring
    python examples/read_catalog.py csv ccop_controls.csv

Pass --catalog PATH to point at a different copy (default: ../catalog.json).
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "catalog.json"


# --------------------------------------------------------------------------- #
# Loading and traversal
# --------------------------------------------------------------------------- #
def load_catalog(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["catalog"]


def iter_controls(groups, trail=()):
    """Yield (group_trail, control) for every control, depth first.

    group_trail is a tuple of group titles, e.g.
    ("Governance Requirements", "Board-Level Accountability").
    """
    for g in groups:
        t = trail + (g["title"],)
        for c in g.get("controls", []):
            yield t, c
        yield from iter_controls(g.get("groups", []), t)


def prop(obj, name, default=None):
    for p in obj.get("props", []):
        if p["name"] == name:
            return p["value"]
    return default


def get_control(catalog, clause):
    """Look up a control by clause number, e.g. '3.1.2'."""
    wanted = f"ccop-{clause}"
    for _, c in iter_controls(catalog["groups"]):
        if c["id"] == wanted:
            return c
    return None


def statement_lines(part, depth=0):
    """Flatten a statement part into indented text lines (prose + labelled items)."""
    label = prop(part, "label")
    prose = part.get("prose", "")
    prefix = f"{label} " if label else ""
    indent = "    " * depth
    for i, para in enumerate(prose.split("\n\n")):
        if para:
            yield f"{indent}{prefix if i == 0 else ''}{para}"
    for sub in part.get("parts", []):
        yield from statement_lines(sub, depth + (1 if prose or label else 0))


def full_text(control):
    """All statement text of a control as one string (excludes guidance parts)."""
    out = []
    for part in control.get("parts", []):
        if part["name"] == "statement":
            out.extend(statement_lines(part))
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_summary(cat, _args):
    md = cat["metadata"]
    print(md["title"])
    print(f"Version {md['version']}  |  OSCAL {md['oscal-version']}  |  published {md['published'][:10]}\n")
    total = 0
    for g in cat["groups"]:
        n = sum(1 for _ in iter_controls([g]))
        total += n
        print(f"  {prop(g, 'label'):>2}  {g['title']:<60} {n:>3} controls")
    print(f"\n  Total controls: {total}")


def cmd_show(cat, args):
    c = get_control(cat, args.clause)
    if not c:
        sys.exit(f"No clause {args.clause} in catalog")
    print(c["title"])
    cd = prop(c, "compliance-date")
    if cd:
        print(f"[compliance date for existing CIIOs: {cd}]")
    print()
    print(full_text(c))
    for part in c.get("parts", []):
        if part["name"] == "guidance":
            print("\nGuidance:", part["prose"])


def cmd_search(cat, args):
    rx = re.compile(args.pattern, re.IGNORECASE)
    hits = 0
    for trail, c in iter_controls(cat["groups"]):
        text = full_text(c)
        if rx.search(text):
            hits += 1
            first = text.splitlines()[0]
            snippet = first if len(first) <= 110 else first[:107] + "..."
            print(f"{prop(c, 'label'):<8} {trail[-1]:<42} {snippet}")
    print(f"\n{hits} matching control(s)")


def cmd_deadlines(cat, _args):
    rows = []
    for trail, c in iter_controls(cat["groups"]):
        d = prop(c, "compliance-date")
        if d:
            rows.append((d, prop(c, "sort-id"), prop(c, "label"), trail[-1]))
    for d, _, label, sub in sorted(rows):
        print(f"{d}  {label:<8} {sub}")
    print(f"\n{len(rows)} controls have a compliance date")


RECUR = re.compile(r"at least once every (\d+) months", re.IGNORECASE)


def cmd_recurring(cat, _args):
    """List controls with 'at least once every N months' requirements."""
    rows = []
    for trail, c in iter_controls(cat["groups"]):
        for m in RECUR.finditer(full_text(c)):
            rows.append((int(m.group(1)), prop(c, "label"), trail[-1]))
            break
    for months, label, sub in sorted(rows, key=lambda r: (r[0], r[1])):
        print(f"every {months:>2} months  {label:<8} {sub}")
    print(f"\n{len(rows)} recurring requirements")


def cmd_csv(cat, args):
    """Export one row per control - handy as a starting point for a gap assessment."""
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["clause", "section", "subsection", "compliance_date", "statement",
                    "status", "evidence", "owner"])  # last three are blank columns to fill in
        for trail, c in iter_controls(cat["groups"]):
            w.writerow([prop(c, "label"), trail[0], trail[-1], prop(c, "compliance-date", ""),
                        full_text(c), "", "", ""])
    print(f"Wrote {args.output}")


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("summary").set_defaults(fn=cmd_summary)
    p = sub.add_parser("show"); p.add_argument("clause"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("search"); p.add_argument("pattern"); p.set_defaults(fn=cmd_search)
    sub.add_parser("deadlines").set_defaults(fn=cmd_deadlines)
    sub.add_parser("recurring").set_defaults(fn=cmd_recurring)
    p = sub.add_parser("csv"); p.add_argument("output"); p.set_defaults(fn=cmd_csv)
    args = ap.parse_args()
    args.fn(load_catalog(args.catalog), args)


if __name__ == "__main__":
    main()
