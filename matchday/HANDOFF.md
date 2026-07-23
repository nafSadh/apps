# Handoff — Match-Guide-Agent → MatchDayBuddy

**From:** Match-Guide-Agent (this pass)
**To:** MatchDayBuddy (main agent, other tab — same repo, working concurrently)
**Date:** 2026-07-23
**Repo state:** nothing committed yet. `git status --short` right now:
```
 M matchday/clubs.html
 M matchday/index.html
 M matchday/players.html
?? matchday/cal.html
?? matchday/guide.html
```

## ⚠️ Concurrent-edit notice — see agents-talk.md

We were both live-editing this working tree at the same time this pass and collided twice (players.html and clubs.html each got silently overwritten once, since fixed). Ongoing coordination and open questions between us now live in **`agents-talk.md`**, not here — check that file for the current state.

**Scope update (2026-07-23):** the owner has scoped Match-Guide-Agent down to `guide.html` only going forward. No more edits from this side to `index.html`, `clubs.html`, `players.html`, `cal.html`, `legends.html`, or `blacklist.md` — those are yours without collision risk now.

I don't know if these were intentional cleanups from your tab or something else. **Before you commit, diff clubs.html yourself and confirm those two changes are yours and intended** — I'm flagging rather than reverting since I can't tell which of us has the fuller context on them. Similarly, `index.html` already has a `cal.html` full-calendar link and a fixed Nuno Mendes photo in the PSG depth chart that I didn't add — I'm assuming that's your work from this session, noting it so you know it's still uncommitted.

Recommend: one of us finishes and commits before the other starts a new edit pass, or at minimum re-`git diff` before trusting file state — same hazard as the concurrent album-culling issue on the photos side.

## What I built this pass

Prompted by: user pointed at a Gemini share link (couldn't fetch — auth-walled) and then a Google Doc, **"The Modern European & Global Football Companion Guide (2026/27)"**, and asked me to build a viewing-guide page for sadh.app/matchday, then to pull the doc's club/player content into the existing app pages rather than silo everything in a new page.

### 1. `guide.html` (new file)
Companion page, same visual system as the other pages (same fonts, `.eyebrow`/`.svc`/`.fmt`/`.dcard` components, dark floodlit-pitch background). Sections, in order:
1. **Where to Watch** — US streaming per competition: Paramount+ (UCL/UEL/Serie A/Carabao), Peacock (EPL), ESPN+ (La Liga/FA Cup/Copa del Rey), beIN via Fanatiz (~$12.99/mo)/Sling/Fubo (Ligue 1, PSG's UCL games noted as Paramount+ instead).
2. **Champions League Format** — 36-team Swiss-model league phase, the 1–8 / 9–24 / 25–36 bands, tiebreaker order, no-away-goals knockout rule, Aug 25–Sep 10 2026 key dates.
3. **League vs Cup** — round-robin leagues vs open-draw single-elim domestic cups vs Carabao-style rotation cup, stated factually (no editorializing, per the standing style rule below).
4. **Reading a Match** (added in the enrichment pass) — xG, PSxG, PPDA, field tilt, goal-timing windows, and a forecasts card linking `../wc2026/` as the in-house example of the 10,000-run Monte Carlo method from the doc.
5. **Season Plan** — PT-first: Sep–Dec one marquee game per UCL matchday, late-Jan simultaneous Matchday 8, Feb–Jun knockouts, Aug–May weekend league mornings.

Footer links back to `./`, `cal.html`, `clubs.html`, `players.html`. **Not yet linked from `index.html`'s nav** — still an open decision, see below.

### 2. `players.html` enrichment
- Added a new card: **Florian Wirtz** (Liverpool, No. 7, 23yo, attacking mid) — inserted at the head of the Liverpool block. Bio: "Vertical playmaker with rapid decision-making in transition; delivers line-breaking passes under heavy pressure." Headshot verified live (HTTP 200) at `upload.wikimedia.org/.../Florian_Wirtz_Ecuador_v_Germany_25_June_2026-181_(cropped).jpg`.
- Rewrote three placeholder/generic bios to match the doc's tactical-profile framing (objective, no comps-to-other-players language):
  - **Musiala** → tight-space dribbler / creative playmaker framing.
  - **Valverde** → box-to-box engine framing.
  - **Gyökeres** → power-striker framing (previously just "Forward in Arsenal's 2026–27 squad", a placeholder).
- All `data-fav` values ≥66 bumped +1 to make room for Wirtz. Verified afterward: 157 cards, contiguous 1–157, no duplicates.

### 3. `clubs.html` enrichment
- Added **Athletic Bilbao** card (La Liga, fav 10, inserted after Real Betis): cantera policy (Basque-only squad), the "never relegated, alongside Real Madrid/Barcelona" fact, 12th-place 2025–26 finish, Nico Williams/Oihan Sancet/returning Aymeric Laporte for 2026–27. Manager/stadium verified via Wikipedia fetch: **Edin Terzić · Estadio San Mamés** (the source doc predates this appointment, so I re-verified rather than trusting the doc). Real (non-free) crest hotlinked from `en.wikipedia.org/.../Club_Athletic_Bilbao_logo.svg` — verified 200 on the `en` wiki path (404'd on `commons`, so it must stay pointed at `en`).
  - **No squad-modal entry exists for Athletic** — its `Squad ↗` button was intentionally omitted rather than pointing at a dead `#athletic` anchor; card links to Wikipedia + season page instead. If you want a real squad view for it, that needs an entry added to the `const squads` JS object (same `pl()`/`dp()` pattern as the other six).
  - Remaining `data-fav` values ≥10 bumped +1.
- Fixed the header tag from **"30 clubs" → "31 clubs"** after the insert (this was a stale count bug introduced by my own insert, caught and fixed same pass).

## Style rules I followed (carried over from your original HANDOFF.md in Downloads/files.zip)
- No subjective/editorial copy — every new sentence is a stated fact, not a comp/gloss.
- No ALL CAPS.
- Verified crest licensing before hotlinking (checked HTTP status on the actual file, not just assumed from the doc).
- Didn't touch `legends.html`, `blacklist.md`, or the Team XI vs Squad 11 Salah issue — out of scope for this pass, still open items from your handoff.

## Open decisions (yours or the user's call)
1. Link `guide.html` from `index.html`'s nav — my suggestion last turn was appending `· viewing guide ↗` next to the `full calendar ↗` tag in the Typical Schedule eyebrow, but I never applied it since you may already be touching that exact line.
2. Whether/when to commit — working tree has been dirty across both our edits all session; see the concurrent-edit notice above before you do.
3. Athletic Bilbao squad-modal entry (see above) — never requested, just flagging the gap.
4. Confirm the two clubs.html changes I can't attribute (Real Betis/PSV season-link removal, "Clubs to Follow" heading removal) are yours and intended.
