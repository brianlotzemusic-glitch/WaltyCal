# TpT log (one line per product or event; newest last)

- 2026-11-12: Owner restarted the factory as TpT only: 3 classroom products + 1 holiday Logic kit a day, bundles as conditions are met. Lean manual TPT-FACTORY.md, queue tpt/QUEUE.md. tpt/PAUSED removed; the Mac nightly may publish again (up to 6 a night). Old routines stay off.
- 2026-11-12 18:26 UTC: dispatcher session ready.
- 2026-11-12: Shift routine trig_014u9VV3zENDYyeP3Vu5HHuf (5:42am and 1:42pm ET) fires into dispatcher session_01PMk4civaSDTgEB9sBVMyMH (Sonnet). First shift: today 1:42pm ET.
- 2026-11-12: 031-carol-flip-logic (Holiday Logic kit, $9) built, QA approved after 1 fix round, released. Added ORIGINAL mode to dmp2.py.
- 2026-11-12: 032-christmas-color-by-note (classroom, $4) built, QA approved after 1 fix round (tags), released.
- 2026-11-12: 033-thanksgiving-music-sub-plan (classroom, $4) built, QA approved after 1 fix round (layout), released. Afternoon shift done: 031, 032, 033.
- 2026-11-12: Owner chose to keep uploads on the Mac but make them hands-off. The Mac job now waits for the network after a wake, runs one at a time, adds a catch-up schedule (login + 6 times a day, on top of 8:30pm), opens no browser when nothing is pending, and holds an item after 2 failed publishes (publish-failed; rewrite release to re-arm). The Mac picks this up by itself on its next two runs.
- 2026-11-12: 030 DMP1 bundle: found why it never published. Three of its four tags (High School, Project Based Learning, Technology) are not in TpT's Tag list, and the uploader refuses unknown values. Tags corrected, release rewritten (re-armed). TpT's full tag list saved as tpt/TAG-OPTIONS.json; builders and QA must use exact entries.
