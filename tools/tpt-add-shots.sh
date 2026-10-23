# Sourced by tools/tpt-nightly.sh and tools/tpt-collect-diagnostics.sh (run from the repo root).
# tpt/_publish/ is gitignored, so failure screenshots need `git add -f`. Keep the list SMALL: only
# *-failed*.png, *-free*.png, *-dropdown*.png and the reupload-fix subject/untick shots, each <= 1.5 MB.
# Never the many *-filled / *-submitted pngs.
tpt_add_shots() {
  local f sz
  for f in tpt/_publish/*-failed*.png tpt/_publish/*-free*.png tpt/_publish/*-dropdown*.png tpt/_publish/*-fix-subject*.png tpt/_publish/*-fix-untick*.png; do
    [ -f "$f" ] || continue
    sz=$(wc -c < "$f" | tr -d ' ')
    if [ "$sz" -gt 1572864 ]; then echo "skip $f (${sz} bytes > 1.5 MB)"; continue; fi
    git add -f -- "$f" || echo "git add -f $f FAILED (exit $?)"
  done
}
