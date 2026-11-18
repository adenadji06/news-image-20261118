# The World in One Day — Wednesday 18 November 2026

A front-page-style image summing up the world's news of Wednesday
18 November 2026, drawn entirely in code with Python and Pillow.

## The image

The masthead names the day in large type — **WEDNESDAY 18 NOVEMBER 2026** —
above three lead stories: Trump landing in Manila for Quad talks, Ukraine's
strike on the Crimea bridge, and Iran's drone attack on a US radar system
in Bahrain. Below them, a world map carries a numbered pin for each of the
30 stories, and the lower half is a numbered index of all 30, so a reader
who missed the day can tell what happened from the image alone.

## Story selection

I researched the day with live news searches on the morning of 18 November
2026 (sources: AP, Reuters, Al Jazeera, DW, ABC News, Euronews, Times of
India, Variety, Socceroos). Every story on the image is a real event that
happened or was first reported on 18 November 2026 in some time zone. The
30 stories span six continents and politics, war, markets, tech, sport,
culture, science and weather:

1. Trump lands in Manila — Quad talks open; China visit next
2. Ukraine strikes the Crimea bridge — road span damaged; Kyiv crossings hit
3. Iran drones hit Bahrain — US radar targeted; Gulf on alert
4. Britain sanctions settlers — eight Israeli firms; Gaza aid blockers
5. Canada–China extend trade — Xi meets Carney before APEC
6. US presses UN over Taiwan — flight curbs row; Beijing hits back
7. Nvidia beats forecasts — $115.8bn quarter; shares jump
8. Apple outage hits iCloud — Pay and App Store down after an update
9. NSA network goes down — classified system hit amid tech chaos
10. Google flags AI cyberattack — first autonomous AI attack seen
11. Dhoni retires from IPL — becomes Chennai Super Kings mentor
12. Earthshot Prize 2026 — PFAS-Free France wins the waste-free award
13. Jordan beat Australia 2-0 — Socceroos' final game of 2026
14. Celtic edge Dundee 2-1 — late goal settles the cup tie in extra time
15. Lyon beat Arsenal 2-1 — women's football
16. Rain halts SA fightback — Wanderers Test vs Bangladesh
17. Gujarat beat RCB — seven wickets in the IPL
18. Cyclone Akvan strengthens — Bay of Bengal; severe by 19 Nov
19. Modi at East Asia Summit — Indo-Pacific vision; India re-elected to ITU
20. Amazon's $7bn India bet — renewables investment by 2030
21. Latvia backs new cabinet — Kulbergs government wins confidence vote
22. UN: 372 killed in Ukraine — civilian toll for October
23. Gaza: one hot meal in two days — WFP update on displaced families
24. Costa Rica journalist killed — probed drug links and corruption
25. Guinea mining crackdown — ban displaces thousands
26. 17 killed in SA shootings — two mass shootings
27. Jordan bans Telegram — national security cited
28. Houthis take Bab al-Mandab — strait under rebel control
29. Baidu chief warns of AI bubble — ahead of APEC talks
30. Pope Leo hit by rosary — crowd throw strikes his eye in Peru

Where a story broke late on 17 November in the Americas it is dated
18 November in Asia-Pacific time zones, which is how it was reported on
the day; nothing here is invented, and no event predates 13 November 2026.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13 standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). It first checks the
file exists and starts with the PNG magic bytes. Both runs write identical
bytes.

## Files

- `entry.png` — the image (1024×1024, ~168 KB)
- `main.py` — the entry program
- `LICENSE` — MIT
- `.makefun/owner.json` — payout wallet claim file
