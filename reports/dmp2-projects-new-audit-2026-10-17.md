# DMP2 "Projects (New)" source audit, 2026-10-17

Read-only audit. Drive was only listed (search by parent folder); nothing was edited, shared or moved. Branch shop-factory.

## 1. What is in DMP2 > Projects (New)

Folder `1g_iW51QKJGe0c8qTIcK-CawxDgzaClys`, created and modified 2026-03-25, parent DMP2 (`1XgzrVGw...`). No loose files at the top level. 16 subfolders.

| Subfolder | Contents (type, modified) |
|---|---|
| Alchemy Architect | Alchemy Architect - Project Sheet & Rubric (Google Doc, 2026-03-26) |
| Anti-Music Manifesto | Anti Music Manifesto - Project Sheet & Rubric (Doc, 2026-03-26) |
| Billboard Top 10 | Billboard Top 10 - Project Sheet & Rubric (Doc, 2026-03-26) |
| Found Sound | Found Sound - Project Sheet & Rubric (Doc, 2026-03-26) |
| Free Play | Free Play - Project Sheet & Rubric (Doc, 2026-03-26) |
| FX Deep Dive | FX Deep Dive - Project Sheet & Rubric (Doc, 2026-03-26) |
| Genre Exploration | Genre Exploration - Project Sheet & Rubric (Doc, 2026-03-26) |
| Infinite Horizon | Infinite Horizon - Project Sheet & Rubric (Doc, 2026-03-26) |
| Music for Visual Media | Music for Visual Media - Project Sheet & Rubric (Doc, 2026-03-26) |
| Pattern Prodigy | Pattern Prodigy - Project Sheet & Rubric (Doc, 2026-03-26) |
| Royalty Free | Royalty Free - Project Sheet & Rubric (Doc, 2026-03-26) |
| Sample Flipping | Sample Flipping - Project Sheet & Rubric (Doc, 2026-03-26) |
| Session Player's Studio | Session Player's Studio - Project Sheet & Rubric (Doc, 2026-03-26) |
| Sonic Time Capsule | Sonic Time Capsule - Project Sheet & Rubric (Doc, 2026-03-26; edited 15:19 same day) |
| TEACHER NOTES | 14 Docs, one per project above (all 2026-03-26): Alchemy Architect, Anti Music Manifesto, Billboard Top 10, Found Sound, Free Play, FX Deep Dive, Genre Exploration, Infinite Horizon, Music for Visual Media, Pattern Prodigy, Royalty Free, Sample Flipping, Session Player's Studio, Sonic Time Capsule - Teacher Notes |
| Final Project - Simulated Artist Release (created 2026-04-06, mod 2026-04-06) | Docs: Project Outline & Rubric ("Listed on TpT - Do Not Delete", mod 2026-04-20), Proposal & Brainstorm Worksheet, Group Size Requirements, Link Submission Form, Senior Requirements (mod 2026-04-20); Sheet: Social Media Planning Calendar (1.7 MB, 2026-04-07); subfolders Submission Checklists (Solo / Duo / Group - Final Checklist, Docs, 2026-04-08), Teacher Example - Lotze EP (New Guitars.mp4, .mp3, Poster.png, album.png, .ai, Presentation Link.docx, Social Media Planning Calendar.xlsx; files dated 2024-05), Student Examples (STUDENT WORK, not opened, never use) |

So Projects (New) has 14 projects (each = one Sheet/Rubric Doc + one Teacher Notes Doc, roughly 105-111 KB) plus the Final capstone. The 14 project folders contain exactly one file each. The folder search paged oddly (a next-page token after one result) but every follow-up page was empty, so nothing is hidden.

## 2. Built kits vs Projects (New)

Kits 014 Billboard Top 10, 015 Sample Flipping, 016 FX Deep Dive, 017 Music for Visual Media, 018 Alchemy Architect: all five projects exist in Projects (New), each with a Sheet & Rubric and a Teacher Notes Doc.

Source named in each gen.py header: Projects (New) > [project] > Project Sheet & Rubric, TEACHER NOTES > Teacher Notes, plus the project's entry on "DMP2 - Project Menu". No kit's source notes cite a file in an older folder as input.

Findings:
- **No built kit copied content from a wrong folder.** Rubric totals, wording and pacing come from the Projects (New) Sheet and Notes (QA files confirm "no added requirements").
- **Menu entry is outside Projects (New).** The Project Menu is in DMP2 root (June 2026 Doc `1uQIgG_J`, quoted by all five kits as "From my DMP2 project menu" with Type / Focus). The owner's rule allows the Menu entry, but strictly it is not inside Projects (New). If "only Projects (New)" is literal, the menu quote block (MENU_TYPE / MENU_FOCUS / MENU_DESC in each gen.py, the "project menu entry quoted" on the overview page, and the CHANGES page) should be dropped or confirmed by the owner. Kits 017 and 018 also compared the newer 4 Sep 2026 menu (older Projects folder) in their UPLOAD section 9 questions, but did not use it; they quote the June menu.
- **Other folders were looked at but not used as sources**, only mentioned in owner questions:
  - 014: a 2023 "Billboard Top 10 Beat Making" Doc and a Form (another teacher's account) were flagged; the owner declined a wording comparison (ACTION-LOG 15 Oct 17:49). Not used.
  - 015: older 2023 "Project Outline" (10 classes, /20) not used. The class sample set (a folder of .wav files, 50 vocal loops, a 109 MB ZIP, in an older folder, not in Projects (New)) is NOT included; banned-strings check blocks "50 Vocal Samples".
  - 016: older 2025 "Project 4 - FX Deep Dive" (/20, 10 periods) not used.
  - 017: older 2024/2025 versions of the project not used. 018: older 2025 "Alchemy Architect - Project Outline" not used.
- **Third-party material named by the owner's own notes** (Cambridge-MT multitracks and the Native Instruments "10 FX" video in 016; "Quick Sampler" YouTube titles in 015; YouTube/Vimeo in 017; Alchemy YouTube tutorials in 018) appears only by title as the owner's resource list. None is bundled or linked.
- Kit UPLOAD section 9 and gen.py contain no use of files from the older Projects folder, the 2023/2025 Outlines, the Cycle Calendar, forms or the DMP2 Projects audio folder.

## 3. Unused items, missing and extra projects

Not used by the kits, and in fact NOT present in Projects (New) (they are named by the Teacher Notes but live elsewhere or nowhere): EQ Cheatsheet PDF and Plug-in Links doc (016), Film scoring examples on YouTube and the Logic Pro markers tutorial (017), the 50 provided vocal samples (015), YouTube/video tutorial links (015, 016, 017, 018). The kits substitute their own EQ guide, synth guide and Quick Sampler guide. Nothing else sits in the 14 project folders, so there is no unused file inside Projects (New) other than:
- The whole **Final Project - Simulated Artist Release** folder (Outline & Rubric, Proposal worksheet, Group Size, Link Submission, Senior Requirements, Social Media Calendar, checklists, Lotze EP example). Already listed on TpT; no kit built, queue only asks whether it joins the DMP2 bundle. Student Examples inside it must never be used.
- Teacher Notes for the 9 projects not yet built.

Queue comparison (queue.md lines 34-48 and tpt/DMP-INVENTORY.md section 1):
- Queue lists 14 DMP2 project kits (5 built [x]: Billboard, Sample Flipping, FX, Music for Visual Media, Alchemy; 9 open: Anti-Music Manifesto, Found Sound, Free Play, Genre Exploration, Infinite Horizon, Pattern Prodigy, Royalty Free, Session Player's Studio, Sonic Time Capsule) plus the $99 DMP2 Bundle. "13" in the brief matches the 13 still to build after the first kit, or the 9 open plus 4 = 13 minus Billboard; the actual planned count is 14 and DMP-INVENTORY agrees (14 pickable + Final).
- Missing from the queue but in Projects (New): only the Final project (intentional).
- In the queue but not in Projects (New): none. All 14 queued titles match a Projects (New) folder (spelling: folder "Anti-Music Manifesto", docs "Anti Music Manifesto").
- Not in Projects (New) and not queued: nothing found. The older Projects folder contains duplicates of the same names, which are not sources.

## 4. Recommendations
1. Ask the owner whether the DMP2 root "Project Menu" quote is acceptable as a source; if not, strip it from kits 014-018 (and from the 9 future kits' queue wording).
2. Update queue.md sources wording to say "Projects (New) only" and drop "Project Menu entry" if the owner says so.
3. Treat teacher-note resources (EQ Cheatsheet, Plug-in Links, film scoring examples, markers tutorial, 50 vocal samples) as unavailable until the owner supplies cleared copies.
