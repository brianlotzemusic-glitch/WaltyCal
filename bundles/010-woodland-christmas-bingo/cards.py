"""Deal 30 unique 5x5 bingo cards from the 30-icon pool, and prove it.

Each card holds 24 of the 30 icons (+ FREE centre). Dealt in 6 rounds: each
round shuffles the pool into 5 groups of 6, and each group is what one card
leaves out, so every icon appears on exactly 24 of the 30 cards (fair game).
Checks (asserted, re-run any time with `python3 cards.py --check`):
  1. no two cards share the same set of 24 icons
  2. no two cards share the same layout
  3. no two cards share a winning line (row, column or diagonal, as a set),
     so two players can't win on the very same line at the same call
  4. every icon is used on exactly 24 cards; every card has 24 distinct icons
"""
import json, os, random, sys, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
N_ICONS, N_CARDS = 30, 30


def lines(grid):  # grid: 25 entries, index 12 = FREE (None)
    rows = [grid[r * 5:(r + 1) * 5] for r in range(5)]
    cols = [grid[c::5] for c in range(5)]
    diags = [[grid[i * 6] for i in range(5)], [grid[4 + i * 4] for i in range(5)]]
    return [frozenset(x for x in ln if x is not None) for ln in rows + cols + diags]


def check(cards):
    assert len(cards) == N_CARDS
    sets = [frozenset(x for x in c if x is not None) for c in cards]
    for c, s in zip(cards, sets):
        assert len(c) == 25 and c[12] is None and len(s) == 24
    assert len(set(sets)) == N_CARDS, "duplicate icon sets"
    assert len(set(tuple(c) for c in cards)) == N_CARDS, "duplicate layouts"
    seen = {}
    for i, c in enumerate(cards):
        for ln in lines(c):
            assert ln not in seen, f"cards {seen[ln] + 1} and {i + 1} share a line"
            seen[ln] = i
    use = [sum(ic in s for s in sets) for ic in range(N_ICONS)]
    assert set(use) == {24}, use
    overlap = max(len(a & b) for a, b in itertools.combinations(sets, 2))
    return {"cards": N_CARDS, "unique_sets": len(set(sets)), "unique_layouts": N_CARDS,
            "shared_lines": 0, "uses_per_icon": 24, "max_icons_shared_by_two_cards": overlap}


def deal(seed):
    rnd = random.Random(seed)
    cards = []
    for _ in range(6):
        pool = list(range(N_ICONS)); rnd.shuffle(pool)
        for g in range(5):
            omit = set(pool[g * 6:(g + 1) * 6])
            keep = [i for i in range(N_ICONS) if i not in omit]
            rnd.shuffle(keep)
            cards.append(keep[:12] + [None] + keep[12:])
    return cards


if __name__ == "__main__":
    path = os.path.join(HERE, "cards.json")
    if "--check" in sys.argv:
        print(json.dumps(check(json.load(open(path))["cards"]), indent=1)); sys.exit()
    seed = 2026
    while True:
        cards = deal(seed)
        try:
            report = check(cards); break
        except AssertionError:
            seed += 1
    json.dump({"seed": seed, "cards": cards, "proof": report}, open(path, "w"))
    print("seed", seed, report)
