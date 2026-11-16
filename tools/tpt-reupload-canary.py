#!/usr/bin/env python3
"""Canary for the paused file replacements (tpt/REUPLOAD-PAUSED). Cloud-side, offline, reads/writes repo files only.

tpt/REUPLOAD-PAUSED pauses every `reupload` (file replacement on a live product). A line `allow: 043` lets only the listed
items through, so one item (the canary) tests a fix of tools/tpt.js on the Mac before the ~28 waiting replacements run.

  python3 tools/tpt-reupload-canary.py status     one line per canary: PASSED / FAILED / WAITING, then a NEXT: line
  python3 tools/tpt-reupload-canary.py release    canary PASSED -> delete tpt/REUPLOAD-PAUSED (every waiting replacement proceeds)
  python3 tools/tpt-reupload-canary.py convert [--dry-run]
                                                  give up on the edit form: every waiting `reupload` item EXCEPT 001 gets a
                                                  `republish` marker with the same text and loses its `reupload` marker; then
                                                  tpt/REUPLOAD-PAUSED is deleted (001 keeps `reupload`: it has a sale, its URL must stay)
  --root DIR                                      use DIR instead of the repo (tests)
Exit status: status 0 always (the word tells), release 1 if the canary has not passed, convert 0.
"""
import glob, hashlib, json, os, sys

NEVER_REPUBLISH = ("001",)


def marker_hash(folder):
    try:
        return hashlib.sha256(open(os.path.join(folder, "reupload"), "rb").read()).hexdigest()
    except OSError:
        return None


def read_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def item_state(folder):
    """PASSED | FAILED | WAITING | NO-MARKER for the folder's CURRENT reupload marker."""
    h = marker_hash(folder)
    if not h:
        done = read_json(os.path.join(folder, "reuploaded"))
        return "PASSED" if done else "NO-MARKER"
    done = read_json(os.path.join(folder, "reuploaded"))
    if done and done.get("marker_sha256") == h:
        return "PASSED"
    failed = read_json(os.path.join(folder, "reupload-failed"))
    if failed and failed.get("marker_sha256") == h:
        return "FAILED"
    return "WAITING"


def pause_allow(tpt):
    p = os.path.join(tpt, "REUPLOAD-PAUSED")
    if not os.path.exists(p):
        return None, False
    allow = []
    for line in open(p, encoding="utf-8"):
        s = line.strip()
        if s.lower().startswith("allow:"):
            for tok in s[6:].replace(",", " ").split():
                d = "".join(c for c in tok.split("-")[0] if c.isdigit())
                if d:
                    allow.append(d.zfill(3))
    return allow, True


def folder_for(tpt, num):
    m = sorted(glob.glob(os.path.join(tpt, num + "-*")))
    return m[0] if m else None


def main():
    args = sys.argv[1:]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--root" in args:
        root = args[args.index("--root") + 1]
    tpt = os.path.join(root, "tpt")
    cmd = next((a for a in args if a in ("status", "release", "convert")), "status")
    allow, paused = pause_allow(tpt)

    if cmd == "status":
        if not paused:
            print("NOT-PAUSED tpt/REUPLOAD-PAUSED does not exist: every waiting replacement runs")
            print("NEXT: nothing to do")
            return 0
        if not allow:
            print("PAUSED-ALL tpt/REUPLOAD-PAUSED has no allow: line, so no canary is running")
            print("NEXT: nothing to do (a person paused everything)")
            return 0
        states = []
        for num in allow:
            f = folder_for(tpt, num)
            st = item_state(f) if f else "MISSING"
            states.append(st)
            extra = ""
            if st == "FAILED":
                j = read_json(os.path.join(f, "reupload-failed")) or {}
                extra = " | " + str(j.get("step", "")) + ": " + str(j.get("error", ""))[:300]
            print(f"{st:<9} canary {os.path.basename(f) if f else num}{extra}")
        if all(s == "PASSED" for s in states):
            print("NEXT: python3 tools/tpt-reupload-canary.py release   (deletes tpt/REUPLOAD-PAUSED)")
        elif any(s == "FAILED" for s in states):
            print("NEXT: read the canary's reupload-failed + tpt/_publish/*-reupload-*-diag.json; fix tools/tpt.js ONCE and re-arm the "
                  "canary (add a line to its `reupload` marker). If that was already the second fix: "
                  "python3 tools/tpt-reupload-canary.py convert")
        else:
            print("NEXT: wait for the Mac's next run")
        return 0

    if cmd == "release":
        if not paused:
            print("tpt/REUPLOAD-PAUSED is already gone")
            return 0
        ok = bool(allow) and all((folder_for(tpt, n) and item_state(folder_for(tpt, n)) == "PASSED") for n in allow)
        if not ok:
            print("refusing: the canary has not PASSED (run status)")
            return 1
        os.remove(os.path.join(tpt, "REUPLOAD-PAUSED"))
        print("deleted tpt/REUPLOAD-PAUSED: every waiting replacement proceeds on the Mac's next run")
        return 0

    # convert
    dry = "--dry-run" in args
    changed = []
    for f in sorted(glob.glob(os.path.join(tpt, "[0-9][0-9][0-9]-*"))):
        name = os.path.basename(f)
        if not os.path.exists(os.path.join(f, "reupload")) or name[:3] in NEVER_REPUBLISH:
            continue
        if item_state(f) == "PASSED":
            continue  # already replaced: nothing to republish
        if not os.path.exists(os.path.join(f, "uploaded")):
            continue  # not live: the normal publish handles it
        changed.append(name)
        if not dry:
            text = open(os.path.join(f, "reupload"), "rb").read()
            if not os.path.exists(os.path.join(f, "republish")):
                open(os.path.join(f, "republish"), "wb").write(text)
            os.remove(os.path.join(f, "reupload"))
    for n in changed:
        print(("would convert " if dry else "converted ") + n + ": reupload -> republish")
    if paused and not dry:
        os.remove(os.path.join(tpt, "REUPLOAD-PAUSED"))
        print("deleted tpt/REUPLOAD-PAUSED")
    print(f"{len(changed)} item(s); 001 is never converted (it keeps `reupload`).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
