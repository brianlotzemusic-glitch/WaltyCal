#!/usr/bin/env python3
"""Canary for the paused file replacements (tpt/REUPLOAD-PAUSED). Cloud-side, offline, reads/writes repo files only.

tpt/REUPLOAD-PAUSED pauses every `reupload` (file replacement on a live product). A line `allow: 043` lets only the listed
items through, so one item (the canary) tests a fix of tools/tpt.js on the Mac before the ~28 waiting replacements run.

  python3 tools/tpt-reupload-canary.py status     one line per canary: PASSED / FAILED / UNVERIFIED / WAITING, then a NEXT: line
  python3 tools/tpt-reupload-canary.py release    canary PASSED -> delete tpt/REUPLOAD-PAUSED (every waiting replacement proceeds)
There is deliberately NO fallback (owner, 16 Nov 2026): corrected files go onto the EXISTING listings or they do not go live.
  --root DIR                                      use DIR instead of the repo (tests)
Exit status: status 0 always (the word tells), release 1 if the canary has not passed.
"""
import glob, hashlib, json, os, sys

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
    """PASSED | FAILED | UNVERIFIED | WAITING | NO-MARKER for the folder's CURRENT reupload marker.
    UNVERIFIED: the Mac submitted the new files but the edit page did not show them yet; it looks again by itself (70 min, 3 h)."""
    h = marker_hash(folder)
    if not h:
        done = read_json(os.path.join(folder, "reuploaded"))
        return "PASSED" if done else "NO-MARKER"
    done = read_json(os.path.join(folder, "reuploaded"))
    if done and done.get("marker_sha256") == h:
        return "PASSED"
    unv = read_json(os.path.join(folder, "reupload-unverified"))
    if unv and unv.get("marker_sha256") == h:
        return "UNVERIFIED"
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
    cmd = next((a for a in args if a in ("status", "release")), "status")
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
            print("NEXT: see TPT-FACTORY.md 'The Mac uploader'. Fixes 1 and 2 are used (16 Nov): keep tpt/REUPLOAD-PAUSED, leave the "
                  "replacements queued, and push the owner once (8am-8pm ET) with the step and cause from the diagnostics above")
        elif any(s == "UNVERIFIED" for s in states):
            print("NEXT: wait: the Mac submitted and looks again by itself (>= 70 min and >= 3 h after the save); it never resubmits")
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

    return 0  # unreachable: cmd is status or release

if __name__ == "__main__":
    sys.exit(main())
