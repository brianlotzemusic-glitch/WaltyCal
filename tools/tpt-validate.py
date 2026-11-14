#!/usr/bin/env python3
"""Check an item's tpt.json against what TpT's upload form really accepts. Run it BEFORE writing `release`.

  python3 tools/tpt-validate.py tpt/036-lofi-holiday-beat [more folders ...]     exit 1 on any problem

Why: TpT's Subject and Tag menus mix category HEADINGS in with the real choices. Picking a heading (a subject
"Performing Arts", tags "Holiday" or "Student Practice") wipes the field and the upload stops (13 Nov 2026).
Only the entries under a heading can be chosen. Lists: tpt/SUBJECT-OPTIONS.json, tpt/TAG-OPTIONS.json (captured from TpT).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Tag headings, read off the order of tpt/TAG-OPTIONS.json (each is followed by the entries it holds).
TAG_HEADINGS = {"Audience", "Language", "Programs & Methods", "Programs", "Resource Type", "Theme", "Holiday", "Seasonal",
                "Classroom Decor", "Forms", "Hands-on Activities", "Instruction", "Student Assessment", "Student Practice",
                "Teacher Tools", "Supports", "Special Education", "Specialty", "Speech Therapy"}
GRADES = {"preschool", "kindergarten", "higher-education", "adult-education", "not-grade-specific"} | {f"{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'}-grade" for i in range(1, 13)}


def load(name):
    raw = json.load(open(os.path.join(ROOT, "tpt", name)))
    raw = raw if isinstance(raw, list) else raw.get("options", list(raw))
    return [x if isinstance(x, str) else str(x) for x in raw]


def check(folder):
    out = []
    try:
        cfg = json.load(open(os.path.join(folder, "tpt.json")))
    except Exception as e:
        return [f"tpt.json unreadable: {e}"]
    subs, tags = load("SUBJECT-OPTIONS.json"), load("TAG-OPTIONS.json")
    sub_headings = {m.group(1) for x in subs for m in [re.match(r"Other \((.+)\)$", x)] if m}
    s, t, g = cfg.get("subjects") or [], cfg.get("tags") or [], cfg.get("grades") or []
    if not 1 <= len(s) <= 3: out.append("subjects: need 1-3")
    for x in s:
        if x not in subs: out.append(f"subject '{x}' is not an option in tpt/SUBJECT-OPTIONS.json")
        elif x in sub_headings: out.append(f"subject '{x}' is a HEADING: pick one of its entries (e.g. Music, Instrumental Music)")
    if not 1 <= len(t) <= 6: out.append("tags: need 1-6")
    for x in t:
        if x not in tags: out.append(f"tag '{x}' is not an option in tpt/TAG-OPTIONS.json")
        elif x in TAG_HEADINGS: out.append(f"tag '{x}' is a HEADING: pick an entry under it")
    if not 1 <= len(g) <= 4: out.append("grades: need 1-4")
    for x in g:
        if x not in GRADES: out.append(f"grade '{x}' is not valid")
    for k in ("price", "license_price", "tax_code"):
        if not cfg.get(k): out.append(f"{k} missing")
    for slot, f in (cfg.get("files") or {}).items():
        if not os.path.exists(os.path.join(folder, f)): out.append(f"file missing: {slot} {f}")
    if "product" not in (cfg.get("files") or {}): out.append("files.product missing")
    return out


if __name__ == "__main__":
    bad = 0
    for folder in sys.argv[1:] or ["."]:
        problems = check(folder)
        print(("OK   " if not problems else "FAIL ") + folder)
        for p in problems: print("     - " + p)
        bad += bool(problems)
    sys.exit(1 if bad else 0)
