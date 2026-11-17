# Singapore Cybersecurity Code of Practice (CCoP) 2026 – OSCAL Catalog

Machine-readable [OSCAL](https://pages.nist.gov/OSCAL/) 1.1.2 catalog for the Cybersecurity Code of Practice for Critical Information Infrastructure (2026), issued by the Cyber Security Agency of Singapore (CSA) under the Cybersecurity Act 2018.

> **Unofficial transcription.** This is not published or endorsed by CSA. The official PDF is authoritative; check any clause you rely on against it.

> **Acknowledgment** The README of this repository is adapted from Baden Hughes’ [sg-mas-trmg-oscal](https://github.com/badenh/sg-mas-trmg-oscal), which provides an OSCAL catalog of the MAS Technology Risk Management Guidelines. Thanks to Baden for publishing that work openly and for the approach it established.

## What's in the catalog

| | |
|---|---|
| Source | CCoP for CII 2026, Release 1 (effective 29 July 2026) |
| Scope | Sections 1 (Preliminary, p. 7) to 12 (Securing CII Interconnected Systems, p. 69) |
| Not included | Annex A (enterprise guidance), the Compliance Timeline and Document History pages (apart from the items listed below), and the diagram under clause 1.2.6 |
| Format | OSCAL 1.1.2 catalog, JSON |
| Size | 12 section groups, 60 subsection groups, 220 controls |

### Structure

```
catalog
└── group  ccop-sec-3            Section 3  Governance Requirements
    └── group  ccop-3.1          Subsection 3.1  Board-Level Accountability
        │   └── part overview    Preamble (context only, see below)
        └── control ccop-3.1.2   Clause 3.1.2
            └── part statement   Clause text
                └── part item    (a), (b), ... nested (i), (ii) where the Code has them
```

- **One control per numbered clause.** IDs follow the clause number: `ccop-3.1.2`. Sub-items are addressable, e.g. `ccop-3.2.2_smt.b.iii`. Clause titles are not in the Code, so they are generated as `Clause <n> – <subsection title>`.
- **Preambles are not requirements.** Section and subsection preambles are `overview` parts. Under clause 1.2.7 they are context only and are not within audit scope. Take requirement text from `statement` parts.
- **Glossary.** The definitions in clauses 1.2.1 and 10.1.2 are `item` parts inside those controls, with the term as the `label` property.
- **Illustrations.** The worked examples under 1.5 are `guidance` parts on 1.5.1 and 1.5.2. The illustration in the "Existing CII" definition is a `guidance` part inside that definition item.
- **Footnotes.** The seven footnotes, with their URLs, are `back-matter` resources. They are linked from the part where each is cited, and the footnote marker is removed from the prose.
- **Unnumbered clause.** Section 11.1 has no clause number in the Code, so it is a single control (`ccop-11.1`).
- **Compliance dates.** Controls named in the Code's Compliance Timeline (p. 3) carry a `compliance-date` property in the namespace `https://www.csa.gov.sg/ns/oscal/ccop`. The date is `2027-07-29`, or `2027-12-31` for clauses 3.3.1–3.3.3. It applies to existing CIIOs only. This table was transcribed by hand, so verify it against the PDF.

## Quick start

Python 3.8+ and the standard library only:

```bash
python examples/read_catalog.py summary              # controls per section
python examples/read_catalog.py show 5.9.2           # print one clause with its items
python examples/read_catalog.py search "multi-factor"   # regex search over clause text
python examples/read_catalog.py deadlines            # clauses with compliance dates
python examples/read_catalog.py recurring            # "at least once every N months" clauses
python examples/read_catalog.py csv controls.csv     # one row per control for a gap assessment
```

### Use it from your own code

```python
import json

with open("catalog.json", encoding="utf-8") as f:
    catalog = json.load(f)["catalog"]

def controls(groups):
    for g in groups:
        yield from g.get("controls", [])
        yield from controls(g.get("groups", []))

for c in controls(catalog["groups"]):
    if c["id"] == "ccop-5.3.1":
        stmt = next(p for p in c["parts"] if p["name"] == "statement")
        print(stmt["prose"])
        for item in stmt["parts"]:
            label = next(p["value"] for p in item["props"] if p["name"] == "label")
            print(label, item["prose"])
```

The example script has reusable helpers (`iter_controls`, `get_control`, `full_text`, `prop`) that you can import or copy.

## Working with the catalog in other tools

The file is a standard OSCAL catalog, so it should work with OSCAL tooling, for example as the source of a profile, component definition or assessment plan.

```bash
pip install compliance-trestle
trestle import -f catalog.json -o ccop2026
trestle validate -f catalog.json
```

I validated it with the OSCAL catalog model in `compliance-trestle`. Please also run it through your preferred validator (for example `oscal-cli`) before depending on it.

## Notes and limitations

- The text is extracted from the PDF programmatically. Line-break hyphenation was repaired, and the curly quotes and British spelling of the original are kept.
- Clause numbers, the (a)/(b)/(i) item structure and prose have been checked against the PDF. I did not independently check every word, so please report any discrepancy.
- Custom property names (`compliance-date`) use their own namespace, as OSCAL requires for names outside its registry.

## Source and licence

The regulatory content belongs to CSA and the Government of Singapore. See the official publication on the [CSA website](https://www.csa.gov.sg/legislation/codes-of-practice/) for the authoritative text and its terms of use.

Licence for the tooling and structure: LICENSE for `examples/`*.
