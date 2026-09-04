// matchday/brief/transfers.js — season transfer ledger, 2026–27.
//
// Single source of truth for squad changes across the app. Loaded by:
//   index.html   -> "Transfer Log" section (#window) + featured-squad modal In/Out
//   clubs.html   -> squad-modal In/Out rows + the load-time ledger-vs-SQUADS audit
//
// Entry shape (the array body is strict JSON — keep it machine-editable):
//   d       ISO date; "YYYY-MM" = month known only; "2026" = summer, date unrecorded
//   p       player name (as written on this site)
//   from/to club display names; "" when not recorded — never guess one
//   fromKey/toKey  SQUADS slugs from clubs.html, only for the 30 tracked clubs
//   fee     short display string ("€125m (+€15m)", "£55m→£60m"); omit if unknown
//   type    transfer | loan | free | clause
//   status  official | agreed | reported  — same ladder as the daily brief:
//           only "official" is asserted; the rest are attributed, not settled
//   note    one line of context; name outlets for agreed/reported entries
//   w       Wikipedia URL, when the player has a card on players.html
//
// Maintenance: newest entries first is not required (pages sort), but keep the
// official/live split honest — when an agreed/reported move completes, flip its
// status to official and fill d/fee; when it collapses, delete it. The daily
// brief writer job may append confirmed deals here in the same shape. After any
// squad edit or ledger edit, open clubs.html and check the console: TL.audit()
// warns when the ledger and SQUADS disagree (sold player still listed, arrival
// missing) — the failure mode that has bitten this app twice before.

window.TRANSFERS = [
 {
  "d": "2026-09-03",
  "p": "Carlos Martín",
  "from": "Atlético Madrid",
  "to": "Hajduk Split",
  "fromKey": "atletico-madrid",
  "type": "loan",
  "status": "official",
  "note": "Loan until end of season with option to buy, after an Almería move collapsed (fichajes.net)"
 },
 {
  "d": "2026-09-03",
  "p": "Ousseynou Niang",
  "from": "Union SG",
  "to": "Zulte Waregem",
  "fromKey": "union-sg",
  "type": "transfer",
  "status": "official",
  "note": "Two-year contract plus option (walfoot.be)"
 },
 {
  "d": "2026-09-02",
  "p": "Leon Bailey",
  "from": "Aston Villa",
  "to": "Olympiacos",
  "fromKey": "aston-villa",
  "toKey": "olympiacos",
  "type": "transfer",
  "status": "official",
  "note": "Permanent; Villa-side reports and sportsmole.co.uk, completed after the English deadline",
  "fee": "~£3.4m"
 },
 {
  "d": "2026-09-02",
  "p": "Chido Obi",
  "from": "Man United",
  "to": "Willem II",
  "fromKey": "man-united",
  "type": "loan",
  "status": "official",
  "note": "Completed a day after the English deadline (Dutch window open); no buy option (TEAMtalk, FootballTransfers)"
 },
 {
  "d": "2026-09-02",
  "p": "El Chadaille Bitshiabu",
  "from": "RB Leipzig",
  "to": "Galatasaray",
  "fromKey": "rb-leipzig",
  "toKey": "galatasaray",
  "fee": "€2m loan (+€28m option)",
  "type": "loan",
  "status": "official",
  "note": "Season loan, €2m fee, €28m option; announced to KAP (Milliyet, A Spor, Hürriyet)"
 },
 {
  "d": "2026-09-02",
  "p": "Gabriel Mec",
  "from": "Grêmio",
  "to": "Porto",
  "toKey": "porto",
  "fee": "€11m (+€1m)",
  "type": "transfer",
  "status": "official",
  "note": "€11m + €1m variables, to 2031, €80m clause (FCPorto.pt, A Bola, Record)"
 },
 {
  "d": "2026-09-02",
  "p": "Isaac Babadi",
  "from": "PSV",
  "to": "Sparta Rotterdam",
  "fromKey": "psv",
  "type": "loan",
  "status": "official",
  "note": "Season loan (NOS deadline-day liveblog)"
 },
 {
  "d": "2026-09-02",
  "p": "Sam Lammers",
  "from": "FC Twente",
  "to": "PSV",
  "toKey": "psv",
  "type": "transfer",
  "status": "official",
  "note": "Two-season deal, No. 29 (Roundtable/NOS); previous club and fee not verified",
  "fee": "~€2m"
 },
 {
  "d": "2026-09-02",
  "p": "Ayoni Santos",
  "from": "Sparta Rotterdam",
  "to": "PSV",
  "toKey": "psv",
  "fee": "€5m",
  "type": "transfer",
  "status": "official",
  "note": "~€5m, long-term contract (Twente Insite, NOS)"
 },
 {
  "d": "2026-09-02",
  "p": "Mikkel Bro Hansen",
  "from": "Bodø/Glimt",
  "to": "PSV",
  "toKey": "psv",
  "fee": "€3m",
  "type": "transfer",
  "status": "official",
  "note": "17-year-old, ~€3m, joins Jong PSV (NOS)"
 },
 {
  "d": "2026-09-02",
  "p": "Joel van den Berg",
  "from": "PSV",
  "to": "Celtic",
  "fromKey": "psv",
  "toKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Four-year deal, confirmed ~22:30 on 2 Sep (STV, Celts Are Here); not in PSV site squad"
 },
 {
  "d": "2026-09-02",
  "p": "Thilo Kehrer",
  "from": "Monaco",
  "to": "Ajax",
  "toKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "One-year loan (NL Times, NOS)"
 },
 {
  "d": "2026-09-02",
  "p": "Simon Adingra",
  "from": "Sunderland",
  "to": "Ajax",
  "toKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "Loan to replace Godts (NL Times)"
 },
 {
  "d": "2026-09-02",
  "p": "Gerónimo Spina",
  "from": "Atlético Madrid",
  "to": "Ajax",
  "fromKey": "atletico-madrid",
  "toKey": "ajax",
  "type": "transfer",
  "status": "official",
  "note": "21-year-old defender, initially for Jong Ajax (NL Times)"
 },
 {
  "d": "2026-09-02",
  "p": "Sam Johnstone",
  "from": "Wolves",
  "to": "Celtic",
  "toKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Season loan (STV, Celts Are Here)"
 },
 {
  "d": "2026-09-02",
  "p": "Jordan Lotomba",
  "from": "Feyenoord",
  "to": "Celtic",
  "toKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Season loan, announced just before 23:00 (STV)"
 },
 {
  "d": "2026-09-02",
  "p": "Oliver Sørensen",
  "from": "Parma",
  "to": "Celtic",
  "toKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Loan; debuted vs Aberdeen (STV)"
 },
 {
  "d": "2026-09-02",
  "p": "Shim Mheuka",
  "from": "Chelsea",
  "to": "Celtic",
  "fromKey": "chelsea",
  "toKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Loan (STV)"
 },
 {
  "d": "2026-09-02",
  "p": "Landon Emenalo",
  "from": "Chelsea",
  "to": "Celtic",
  "fromKey": "chelsea",
  "toKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Loan; short-term injury (Glasgow World)"
 },
 {
  "d": "2026-09-02",
  "p": "Keito Nakamura",
  "from": "Reims",
  "to": "Lyon",
  "toKey": "lyon",
  "fee": "€1m (+€19m)",
  "type": "transfer",
  "status": "official",
  "note": "'Joker' signing after the window; four years to 2030; €1m fixed + up to €19m variables (Lyon Foot, Orange, Ferveur Lyonnaise)"
 },
 {
  "d": "2026-09-02",
  "p": "Victor Nelsson",
  "from": "Galatasaray",
  "to": "Nordsjælland",
  "fromKey": "galatasaray",
  "type": "transfer",
  "status": "official",
  "note": "Galatasaray 'parted ways' per Fanatik; destination/date not retrieved"
 },
 {
  "d": "2026-09-01",
  "p": "Enzo Fernández",
  "from": "Chelsea",
  "to": "Man City",
  "fromKey": "chelsea",
  "toKey": "man-city",
  "fee": "£125m",
  "type": "transfer",
  "status": "official",
  "note": "Joint British record; five-year deal, takes No. 17 (Sky Sports, Al Jazeera)"
 },
 {
  "d": "2026-09-01",
  "p": "Iliman Ndiaye",
  "from": "Everton",
  "to": "Man City",
  "toKey": "man-city",
  "fee": "£60m (+£5m)",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal; pivot after Liverpool refused to sell Gakpo (Sky Sports, ESPN)"
 },
 {
  "d": "2026-09-01",
  "p": "Jack Grealish",
  "from": "Man City",
  "to": "Everton",
  "fromKey": "man-city",
  "fee": "loan; £50m option",
  "type": "loan",
  "status": "official",
  "note": "Second successive season loan; Everton hold £50m option (mancity.com, ESPN)"
 },
 {
  "d": "2026-09-01",
  "p": "Gabriel Jesus",
  "from": "Arsenal",
  "to": "Barcelona",
  "fromKey": "arsenal",
  "toKey": "barcelona",
  "fee": "£8.6m (€10m)",
  "type": "transfer",
  "status": "official",
  "note": "Deadline-day move; contract to June 2029 (Sky Sports, Al Jazeera, Barca Blaugranes)"
 },
 {
  "d": "2026-09-01",
  "p": "Gabriel Martinelli",
  "from": "Arsenal",
  "to": "Al Hilal",
  "fromKey": "arsenal",
  "fee": "£60m",
  "type": "transfer",
  "status": "official",
  "note": "Arsenal's record sale; four-year deal. Al Hilal's own announcement followed on 3 Sep (Saudi window open) (Sky Sports, ESPN)"
 },
 {
  "d": "2026-09-01",
  "p": "Fábio Vieira",
  "from": "Arsenal",
  "to": "Hamburg",
  "fromKey": "arsenal",
  "fee": "€10m (£8.6m)",
  "type": "transfer",
  "status": "official",
  "note": "Permanent after loan; HSV declined the €22m option and paid less (ESPN, Bundesliga.com)"
 },
 {
  "d": "2026-09-01",
  "p": "Ethan Nwaneri",
  "from": "Arsenal",
  "to": "Borussia Dortmund",
  "fromKey": "arsenal",
  "toKey": "dortmund",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan (arsenal.com, bvb.de)"
 },
 {
  "d": "2026-09-01",
  "p": "Tommy Setford",
  "from": "Arsenal",
  "to": "Stevenage",
  "fromKey": "arsenal",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan to League One (arsenal.com, Stevenage FC)"
 },
 {
  "d": "2026-09-01",
  "p": "Harvey Elliott",
  "from": "Liverpool",
  "to": "Valencia",
  "fromKey": "liverpool",
  "type": "loan",
  "status": "official",
  "note": "Season loan, no option or obligation (liverpoolfc.com, ESPN)"
 },
 {
  "d": "2026-09-01",
  "p": "Ibrahim Mbaye",
  "from": "PSG",
  "to": "Aston Villa",
  "fromKey": "psg",
  "toKey": "aston-villa",
  "fee": "£47m (reported)",
  "type": "transfer",
  "status": "official",
  "note": "18-year-old winger; fee per Sports Mole (ESPN, avfc.co.uk)"
 },
 {
  "d": "2026-09-01",
  "p": "Taylor Harwood-Bellis",
  "from": "Southampton",
  "to": "Aston Villa",
  "toKey": "aston-villa",
  "fee": "£25m–£30m (reports vary)",
  "type": "transfer",
  "status": "official",
  "note": "Konsa replacement (ESPN, Football365)"
 },
 {
  "d": "2026-09-01",
  "p": "Marc Guiu",
  "from": "Chelsea",
  "to": "RB Leipzig",
  "fromKey": "chelsea",
  "toKey": "rb-leipzig",
  "fee": "£14.6m",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal to 2031 (RB Leipzig, Bundesliga.com)"
 },
 {
  "d": "2026-09-01",
  "p": "Robert Sánchez",
  "from": "Chelsea",
  "to": "Como",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Season loan (chelseafc.com, France 24)"
 },
 {
  "d": "2026-09-01",
  "p": "Mykhailo Mudryk",
  "from": "Chelsea",
  "to": "Tottenham",
  "fromKey": "chelsea",
  "fee": "loan; £75m option",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option (tottenhamhotspur.com, Yahoo/Evening Standard)"
 },
 {
  "d": "2026-09-01",
  "p": "Tosin Adarabioyo",
  "from": "Chelsea",
  "to": "Tottenham",
  "fromKey": "chelsea",
  "fee": "£10m (+£2m)",
  "type": "transfer",
  "status": "official",
  "note": "Permanent (chelseafc.com, tottenhamhotspur.com)"
 },
 {
  "d": "2026-09-01",
  "p": "Dário Essugo",
  "from": "Chelsea",
  "to": "Strasbourg",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Listed in Sky Sports' deadline-day done deals; loan to sister club"
 },
 {
  "d": "2026-09-01",
  "p": "Deivid Washington",
  "from": "Chelsea",
  "to": "Strasbourg",
  "fromKey": "chelsea",
  "type": "transfer",
  "status": "official",
  "note": "Listed in Sky Sports' deadline-day done deals; loan/permanent status not verified"
 },
 {
  "d": "2026-09-01",
  "p": "Dani Ceballos",
  "from": "Real Madrid",
  "to": "Real Betis",
  "fromKey": "real-madrid",
  "toKey": "real-betis",
  "type": "free",
  "status": "official",
  "note": "Contract rescinded by mutual agreement; Betis announced the signing to 2029 just after 1am on 2 Sep (realbetisbalompie.es, Infobae, Goal)"
 },
 {
  "d": "2026-09-01",
  "p": "Marc Casadó",
  "from": "Barcelona",
  "to": "Deportivo",
  "fromKey": "barcelona",
  "type": "loan",
  "status": "official",
  "note": "Deadline-day loan to June 2027 with €30m purchase option (riazor.org / Deportivo announcement, Infobae)"
 },
 {
  "d": "2026-09-01",
  "p": "Jonathan David",
  "from": "Juventus",
  "to": "Atlético Madrid",
  "fromKey": "juventus",
  "toKey": "atletico-madrid",
  "type": "loan",
  "status": "official",
  "note": "Loan with €25m option; Juve cover part of salary; announced ~3 hours before deadline (ESPN, Into the Calderón, Sky Italia)"
 },
 {
  "d": "2026-09-01",
  "p": "Issiaka Kamaté",
  "from": "Inter",
  "to": "Atlético Madrid",
  "toKey": "atletico-madrid",
  "fee": "€1.7m",
  "type": "transfer",
  "status": "official",
  "note": "Permanent; Inter keep €8m buy-back and 30% sell-on (fcinter1908, L'Interista, FcInterNews)"
 },
 {
  "d": "2026-09-01",
  "p": "José María Giménez",
  "from": "Atlético Madrid",
  "to": "Deportivo",
  "fromKey": "atletico-madrid",
  "type": "loan",
  "status": "official",
  "note": "Loan to June 2027 with purchase option after 13 seasons (atleticodemadrid.com, riazor.org, Infobae)"
 },
 {
  "d": "2026-09-01",
  "p": "Thomas Lemar",
  "from": "Atlético Madrid",
  "to": "Elche",
  "fromKey": "atletico-madrid",
  "type": "loan",
  "status": "official",
  "note": "Season loan announced on deadline day (atleticodemadrid.com, Infobae)"
 },
 {
  "d": "2026-09-01",
  "p": "Pablo García",
  "from": "Real Betis",
  "to": "Racing Santander",
  "fromKey": "real-betis",
  "fee": "€5.5m (50%)",
  "type": "transfer",
  "status": "official",
  "note": "€5.5m fixed plus variables for 50% of rights; contract to 2030 (Infobae, Andalucía Información)"
 },
 {
  "d": "2026-09-01",
  "p": "Andoni Gorosabel",
  "from": "Athletic Bilbao",
  "to": "Espanyol",
  "fromKey": "athletic",
  "type": "loan",
  "status": "official",
  "note": "Season loan with purchase option that becomes mandatory on appearances (Deia, Naiz)"
 },
 {
  "d": "2026-09-01",
  "p": "Adama Boiro",
  "from": "Athletic Bilbao",
  "to": "West Ham",
  "fromKey": "athletic",
  "type": "loan",
  "status": "official",
  "note": "Loan to end of season with conditional option; announced 01:25 on 2 Sep (Deia, Infobae)"
 },
 {
  "d": "2026-09-01",
  "p": "Unai Vencedor",
  "from": "Athletic Bilbao",
  "to": "Burgos",
  "fromKey": "athletic",
  "type": "free",
  "status": "official",
  "note": "Contract terminated, signed one-year deal at Burgos (Deia)"
 },
 {
  "d": "2026-09-01",
  "p": "Pape Matar Sarr",
  "from": "Tottenham",
  "to": "Juventus",
  "toKey": "juventus",
  "fee": "€2.5m loan (+€27.5m obligation)",
  "type": "loan",
  "status": "official",
  "note": "Paid loan (~€2–2.5m) with conditional obligation ~€27.5–28m (Sky Italia, Corriere dello Sport, juvefc)"
 },
 {
  "d": "2026-09-01",
  "p": "Nick Woltemade",
  "from": "Newcastle",
  "to": "Juventus",
  "toKey": "juventus",
  "fee": "€2.8m loan",
  "type": "loan",
  "status": "official",
  "note": "Dry loan for one season, €2.8m fee (Sky Italia, Corriere dello Sport, Yahoo/AFP)"
 },
 {
  "d": "2026-09-01",
  "p": "Pasquale Mazzocchi",
  "from": "Napoli",
  "to": "Venezia",
  "fromKey": "napoli",
  "type": "loan",
  "status": "official",
  "note": "Loan with obligation if Venezia stay up; completed 31 Aug–1 Sep (Tuttoazzurro, napolimagazine, calcionapoli24)"
 },
 {
  "d": "2026-09-01",
  "p": "Jens Cajuste",
  "from": "Napoli",
  "to": "Málaga",
  "fromKey": "napoli",
  "type": "loan",
  "status": "official",
  "note": "Loan with €8m option (Tuttoazzurro, napolimagazine)"
 },
 {
  "d": "2026-09-01",
  "p": "Jesper Lindstrøm",
  "from": "Napoli",
  "to": "Salzburg",
  "fromKey": "napoli",
  "type": "loan",
  "status": "official",
  "note": "Loan with option (Il Mattino, calcionapoli24)"
 },
 {
  "d": "2026-09-01",
  "p": "Dinis Rodrigues",
  "from": "Man City",
  "to": "Napoli",
  "toKey": "napoli",
  "type": "transfer",
  "status": "official",
  "note": "Young signing, immediately loaned to Spanish second division (Il Mattino, Corriere dello Sport)",
  "fromKey": "man-city"
 },
 {
  "d": "2026-09-01",
  "p": "Neil El Aynaoui",
  "from": "Roma",
  "to": "RB Leipzig",
  "toKey": "rb-leipzig",
  "fee": "€4m loan (+€25m option)",
  "type": "loan",
  "status": "official",
  "note": "€4m loan fee, €25m purchase option (AS Roma, Bundesliga.com)"
 },
 {
  "d": "2026-09-01",
  "p": "Conrad Harder",
  "from": "RB Leipzig",
  "to": "Strasbourg",
  "fromKey": "rb-leipzig",
  "type": "loan",
  "status": "official",
  "note": "Season loan, no purchase option, Strasbourg cover salary (RC Strasbourg, GFFN)"
 },
 {
  "d": "2026-09-01",
  "p": "Deniz Gül",
  "from": "Porto",
  "to": "Galatasaray",
  "fromKey": "porto",
  "toKey": "galatasaray",
  "fee": "€11m",
  "type": "transfer",
  "status": "official",
  "note": "€11m, five-year deal; KAP filing (Galatasaray.org, Fanatik)"
 },
 {
  "d": "2026-09-01",
  "p": "Youri Regeer",
  "from": "Ajax",
  "to": "Werder Bremen",
  "fromKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "Season loan with purchase option (Bundesliga.com, Goal)"
 },
 {
  "d": "2026-09-01",
  "p": "Reo Hatate",
  "from": "Celtic",
  "to": "Burnley",
  "fromKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Per Sports Mole; fee not retrieved"
 },
 {
  "d": "2026-09-01",
  "p": "Johnny Kenny",
  "from": "Celtic",
  "to": "Preston",
  "fromKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Per Sports Mole"
 },
 {
  "d": "2026-09-01",
  "p": "Lucca Brughmans",
  "from": "Genk",
  "to": "Liverpool (loaned back to Genk)",
  "fee": "up to £30m",
  "type": "transfer",
  "status": "official",
  "note": "18-year-old GK; loaned back to Genk for 2026-27, joins in 2027 (liverpoolfc.com, ESPN)"
 },
 {
  "d": "2026-09-01",
  "p": "Honest Ahanor",
  "from": "Atalanta",
  "to": "Chelsea (joins 2027)",
  "fee": "£40m (reported)",
  "type": "transfer",
  "status": "official",
  "note": "Deferred deal: joins Chelsea in July 2027; spends 2026-27 on loan at Crystal Palace direct from Atalanta (ESPN, Heavy)"
 },
 {
  "d": "2026-09-01",
  "p": "Kevin Danso",
  "from": "Tottenham",
  "to": "Sunderland",
  "fromKey": "tottenham",
  "fee": "loan; conditional obligation (~£25m reported)",
  "type": "loan",
  "status": "official",
  "note": "Season loan with performance-based obligation (tottenhamhotspur.com, VAVEL)"
 },
 {
  "d": "2026-09-01",
  "p": "Dane Scarlett",
  "from": "Tottenham",
  "to": "Leyton Orient",
  "fromKey": "tottenham",
  "type": "transfer",
  "status": "official",
  "note": "Undisclosed fee (TEAMtalk done-deals list)"
 },
 {
  "d": "2026-09-01",
  "p": "Arijon Ibrahimović",
  "from": "Bayern",
  "to": "Augsburg",
  "fromKey": "bayern",
  "type": "loan",
  "status": "official",
  "note": "Season loan, €0.5m fee, €8m option (Bundesliga.com, Sport1, AZ); not in site squad"
 },
 {
  "d": "2026-09-01",
  "p": "Malick Fofana",
  "from": "Lyon",
  "to": "Sunderland",
  "fromKey": "lyon",
  "fee": "€35m (+€5m)",
  "type": "transfer",
  "status": "official",
  "note": "€35m + €5m, five-year deal; Palace/Sunderland two-jets saga (Maxifoot, GFFN)"
 },
 {
  "d": "2026-09-01",
  "p": "Ainsley Maitland-Niles",
  "from": "Lyon",
  "to": "Everton",
  "fromKey": "lyon",
  "fee": "€3.5m",
  "type": "transfer",
  "status": "official",
  "note": "€3.5m, to 2029 (Maxifoot, GFFN, Ferveur Lyonnaise)"
 },
 {
  "d": "2026-09-01",
  "p": "Duje Ćaleta-Car",
  "from": "Lyon",
  "to": "Sassuolo",
  "fromKey": "lyon",
  "type": "free",
  "status": "official",
  "note": "Contract terminated by mutual consent; joined Sassuolo as a free agent (footmercato.net)"
 },
 {
  "d": "2026-09-01",
  "p": "Quinten Timber",
  "from": "Marseille",
  "to": "Crystal Palace",
  "fromKey": "marseille",
  "fee": "€20m",
  "type": "transfer",
  "status": "official",
  "note": "~€20m incl. bonuses, five-year deal (GFFN, Sofascore)"
 },
 {
  "d": "2026-09-01",
  "p": "Kiano Dyer",
  "from": "Chelsea",
  "to": "Chesterfield",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Loan until the end of 2026-27, completed on deadline day (chesterfield-fc.co.uk)"
 },
 {
  "d": "2026-09-01",
  "p": "Kōta Takai",
  "from": "Tottenham Hotspur",
  "to": "Sint-Truiden",
  "fromKey": "tottenham",
  "type": "loan",
  "status": "official",
  "note": "Deadline-day loan to Belgium (spurs-web.com)"
 },
 {
  "d": "2026-09-01",
  "p": "Bradley Burrowes",
  "from": "Aston Villa",
  "to": "Wigan Athletic",
  "fromKey": "aston-villa",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan; not in Villa's 2026-27 squad numbers (wigantoday.net)"
 },
 {
  "d": "2026-09-01",
  "p": "Ayodele Thomas",
  "from": "RB Leipzig",
  "to": "NEC Nijmegen",
  "fromKey": "rb-leipzig",
  "fee": "~€1m",
  "type": "transfer",
  "status": "official",
  "note": "Permanent sale after half a season (rbleipzig.com)"
 },
 {
  "d": "2026-09-01",
  "p": "Pedro Gonçalves",
  "from": "Sporting CP",
  "to": "Fiorentina",
  "fromKey": "sporting",
  "fee": "€2.5m loan (+€22.5m obligation)",
  "type": "loan",
  "status": "official",
  "note": "Loan with mandatory purchase (abola.pt)"
 },
 {
  "d": "2026-09-01",
  "p": "Daniel Bragança",
  "from": "Sporting CP",
  "to": "Torino",
  "fromKey": "sporting",
  "fee": "loan; ~€4m obligation",
  "type": "loan",
  "status": "official",
  "note": "Loan with mandatory purchase (abola.pt)"
 },
 {
  "d": "2026-09-01",
  "p": "Koba Koindredi",
  "from": "Sporting CP",
  "to": "Lausanne-Sport",
  "fromKey": "sporting",
  "type": "free",
  "status": "official",
  "note": "Contract rescinded; joined permanently until 2029 (lausanne-sport.ch)"
 },
 {
  "d": "2026-09-01",
  "p": "Mohammed Fuseini",
  "from": "Union SG",
  "to": "Derby County",
  "fromKey": "union-sg",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option to buy, completed on English deadline day (dcfc.co.uk)"
 },
 {
  "d": "2026-09",
  "p": "Sami Ouaissa",
  "from": "NEC",
  "to": "PSV",
  "toKey": "psv",
  "fee": "~€9m",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 2031, confirmed 1-2 Sep (psvfans.nl)"
 },
 {
  "d": "2026-09",
  "p": "Maher Carrizo",
  "from": "Ajax",
  "to": "FC Copenhagen",
  "fromKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "Season loan, no purchase option, deadline week (voetbalprimeur.nl)"
 },
 {
  "d": "2026-08-31",
  "p": "Bradley Barcola",
  "from": "PSG",
  "to": "Liverpool",
  "fromKey": "psg",
  "toKey": "liverpool",
  "fee": "£106m (+£17m)",
  "type": "transfer",
  "status": "official",
  "note": "Club's second-most expensive signing; five-year deal (liverpoolfc.com, Sky Sports, ESPN)"
 },
 {
  "d": "2026-08-31",
  "p": "Ollie Watkins",
  "from": "Aston Villa",
  "to": "Al Hilal",
  "fromKey": "aston-villa",
  "fee": "£50m",
  "type": "transfer",
  "status": "official",
  "note": "Three-year deal after six seasons and 108 Villa goals (ESPN, Sky Sports)"
 },
 {
  "d": "2026-08-31",
  "p": "Kristjan Asllani",
  "from": "Inter",
  "to": "Al-Jazira",
  "fromKey": "inter",
  "fee": "€2m loan (+€5m obligation)",
  "type": "loan",
  "status": "official",
  "note": "Loan (~€2m) with conditional obligation (~€5m); Inter statement in final days of window — exact day to verify (fcinter1908, Goal IT, Sportmediaset)"
 },
 {
  "d": "2026-08-31",
  "p": "Souza",
  "from": "Tottenham Hotspur",
  "to": "Porto",
  "fromKey": "tottenham",
  "type": "loan",
  "status": "official",
  "note": "Season-long dry loan, no purchase option; not on Porto's researched first-team list so toKey left unset (tottenhamhotspur.com)"
 },
 {
  "d": "2026-08-31",
  "p": "Dan Gore",
  "from": "Man United",
  "to": "Luton Town",
  "fromKey": "man-united",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan with a conditional option to buy (thepeoplesperson.com)"
 },
 {
  "d": "2026-08-31",
  "p": "Elijah Gift",
  "from": "Athletic Bilbao",
  "to": "Eibar",
  "fromKey": "athletic",
  "type": "loan",
  "status": "official",
  "note": "Bilbao Athletic player loaned to SD Eibar until end of season (deia.eus)"
 },
 {
  "d": "2026-08-31",
  "p": "Yanis Massolin",
  "from": "Inter Milan",
  "to": "Cagliari",
  "fromKey": "inter",
  "fee": "loan; €7m option",
  "type": "loan",
  "status": "official",
  "note": "Loan with €7m option and Inter counter-option (calciomercato.com)"
 },
 {
  "d": "2026-08-31",
  "p": "Gustaf Nilsson",
  "from": "Club Brugge",
  "to": "Hertha BSC",
  "fromKey": "club-brugge",
  "type": "loan",
  "status": "official",
  "note": "Loan for 2026-27 with purchase option (herthabsc.com)"
 },
 {
  "d": "2026-08-30",
  "p": "Allan Elias",
  "from": "Palmeiras",
  "to": "Man City",
  "toKey": "man-city",
  "fee": "£32m (+£2m) / €40m",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal; City's sixth summer arrival (ESPN, Al Jazeera, Goal)"
 },
 {
  "d": "2026-08-30",
  "p": "Emiliano Martínez",
  "from": "Aston Villa",
  "to": "Chelsea",
  "fromKey": "aston-villa",
  "toKey": "chelsea",
  "fee": "£7.5m",
  "type": "transfer",
  "status": "official",
  "note": "Three-year deal (chelseafc.com, ESPN, Sky Sports)"
 },
 {
  "d": "2026-08-30",
  "p": "Rafael Leão",
  "from": "AC Milan",
  "to": "Galatasaray",
  "toKey": "galatasaray",
  "fee": "€38m",
  "type": "transfer",
  "status": "official",
  "note": "€38m net, four-year deal; KAP filing 30 Aug; Milan official statement (ACMilan.com, A Spor)"
 },
 {
  "d": "2026-08-30",
  "p": "Sofyan Amrabat",
  "from": "Free agent",
  "to": "Ajax",
  "toKey": "ajax",
  "type": "free",
  "status": "official",
  "note": "Two-year deal after terminating his Fenerbahçe contract (english.ajax.nl)"
 },
 {
  "d": "2026-08-29",
  "p": "Héctor Fort",
  "from": "Barcelona",
  "to": "Real Sociedad",
  "fromKey": "barcelona",
  "fee": "€8m",
  "type": "transfer",
  "status": "official",
  "note": "Signed to 2031; Barça keep buy-back and sell-on; ~€8m reported (realsociedad.eus, Football España, COPE)"
 },
 {
  "d": "2026-08-29",
  "p": "Kaique Pereira",
  "from": "Palmeiras",
  "to": "Sporting CP",
  "toKey": "sporting",
  "fee": "€4m",
  "type": "transfer",
  "status": "official",
  "note": "Goalkeeper, to 2031, €80m clause; ~€4m (Sporting.pt, A Bola, RTP)"
 },
 {
  "d": "2026-08-29",
  "p": "Denzel De Roeve",
  "from": "",
  "to": "Union SG",
  "toKey": "union-sg",
  "type": "transfer",
  "status": "official",
  "note": "Per AiScore log; from-club unverified; not in site squad"
 },
 {
  "d": "2026-08-29",
  "p": "Ange Lago",
  "from": "Olympique de Marseille",
  "to": "Dijon",
  "fromKey": "marseille",
  "type": "free",
  "status": "official",
  "note": "Contract terminated; signed for the Ligue 2 side until 2029, OM keep 50% sell-on and a buy-back (maxifoot.fr)"
 },
 {
  "d": "2026-08-29",
  "p": "Marcus Holmgren Pedersen",
  "from": "Torino",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "fee": "~€8m (+bonuses)",
  "type": "transfer",
  "status": "official",
  "note": "Full-back, contract to 2030 (olympiacos.org)"
 },
 {
  "d": "2026-08-28",
  "p": "Nicolas Jackson",
  "from": "Chelsea",
  "to": "Aston Villa",
  "fromKey": "chelsea",
  "toKey": "aston-villa",
  "fee": "£47.5m (+£17.5m)",
  "type": "transfer",
  "status": "official",
  "note": "Permanent, £47.5m rising to £65m — Chelsea and Villa statements"
 },
 {
  "d": "2026-08-28",
  "p": "Fabio Miretti",
  "from": "Juventus",
  "to": "Beşiktaş",
  "fromKey": "juventus",
  "fee": "€2m loan (+€13m option)",
  "type": "loan",
  "status": "official",
  "note": "Loan to June 2027, €2m (+€0.1m) with €13m option (Wikipedia season page, bianconeranews)"
 },
 {
  "d": "2026-08-27",
  "p": "Omar Marmoush",
  "from": "Man City",
  "to": "Tottenham",
  "fromKey": "man-city",
  "toKey": "tottenham",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan with obligation to buy; No. 22 at Spurs (Sky Sports, Al Jazeera, Goal)",
  "fee": "loan; £50m obligation (+£10m)"
 },
 {
  "d": "2026-08-27",
  "p": "Nico González",
  "from": "Man City",
  "to": "Newcastle",
  "fromKey": "man-city",
  "fee": "£48m (+£4m)",
  "type": "transfer",
  "status": "official",
  "note": "Takes No. 6 at Newcastle after 18 months at City (Sky Sports, mancity.com)"
 },
 {
  "d": "2026-08-27",
  "p": "Issa Kaboré",
  "from": "Man City",
  "to": "Wrexham",
  "fromKey": "man-city",
  "type": "transfer",
  "status": "official",
  "note": "Permanent after last season's loan; undisclosed fee, ~£2m reported; three-year deal (Wrexham AFC, ESPN)"
 },
 {
  "d": "2026-08-27",
  "p": "Leon Goretzka",
  "from": "Bayern",
  "to": "Aston Villa",
  "toKey": "aston-villa",
  "type": "free",
  "status": "official",
  "note": "Free agent after Bayern contract expired (avfc.co.uk, Bavarian Football Works)"
 },
 {
  "d": "2026-08-27",
  "p": "Liam Delap",
  "from": "Chelsea",
  "to": "Nottingham Forest",
  "fromKey": "chelsea",
  "fee": "£45m (+£5m)",
  "type": "transfer",
  "status": "official",
  "note": "Forest club record; five-year deal (Nottingham Forest, Sky Sports)"
 },
 {
  "d": "2026-08-27",
  "p": "João Virgínia",
  "from": "Sporting CP",
  "to": "Wolves",
  "fromKey": "sporting",
  "fee": "€1.5m",
  "type": "transfer",
  "status": "official",
  "note": "Three-year deal (Wolves.co.uk); fee ~€1.5m per DAZN summary"
 },
 {
  "d": "2026-08-27",
  "p": "Viktor Tsygankov",
  "from": "Girona",
  "to": "Ajax",
  "toKey": "ajax",
  "fee": "~€4m",
  "type": "transfer",
  "status": "official",
  "note": "Right winger (ziggo.nl)"
 },
 {
  "d": "2026-08-26",
  "p": "Ayyoub Bouaddi",
  "from": "Lille",
  "to": "Man City",
  "toKey": "man-city",
  "fee": "€95m (+€5m) / £85.6m",
  "type": "transfer",
  "status": "official",
  "note": "Most expensive PL teenager; contract to 2031 (mancity.com, ESPN, Al Jazeera)"
 },
 {
  "d": "2026-08-26",
  "p": "Moncef Zekri",
  "from": "KV Mechelen",
  "to": "Sporting CP",
  "toKey": "sporting",
  "fee": "€3m",
  "type": "transfer",
  "status": "official",
  "note": "17-year-old left-back, five-year deal, ~€3m (A Bola)"
 },
 {
  "d": "2026-08-26",
  "p": "João Palhinha",
  "from": "Bayern",
  "to": "Benfica",
  "fromKey": "bayern",
  "fee": "€15m (+€5m)",
  "type": "transfer",
  "status": "official",
  "note": "To 2030; Bundesliga.com, Benfica, ESPN"
 },
 {
  "d": "2026-08-26",
  "p": "Seko Fofana",
  "from": "Rennes",
  "to": "Porto",
  "toKey": "porto",
  "type": "loan",
  "status": "official",
  "note": "Second loan spell, free loan to 30 Jun 2027, no option (abola.pt)"
 },
 {
  "d": "2026-08-25",
  "p": "Savinho",
  "from": "Man City",
  "to": "Tottenham",
  "fromKey": "man-city",
  "toKey": "tottenham",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal at Spurs (Sky Sports, Al Jazeera)",
  "w": "https://en.wikipedia.org/wiki/Savinho",
  "fee": "£75m (+£10m)"
 },
 {
  "d": "2026-08-25",
  "p": "Carlos Baleba",
  "from": "Brighton",
  "to": "Man United",
  "toKey": "man-united",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal plus option; Brighton sell-on (Sky Sports, Al Jazeera)",
  "fee": "£65m (+£5m)"
 },
 {
  "d": "2026-08-25",
  "p": "Michele Di Gregorio",
  "from": "Juventus",
  "to": "Bournemouth",
  "fromKey": "juventus",
  "fee": "€1.3m loan (+€12.7m option)",
  "type": "loan",
  "status": "official",
  "note": "Loan with option to buy (juventus.com)"
 },
 {
  "d": "2026-08-25",
  "p": "Kamil Grabara",
  "from": "Wolfsburg",
  "to": "Juventus",
  "toKey": "juventus",
  "fee": "€0.5m loan (+€0.5m; €11.5m option)",
  "type": "loan",
  "status": "official",
  "note": "Loan with €11.5m option; takes the No.1 shirt (juventus.com)"
 },
 {
  "d": "2026-08-25",
  "p": "Christopher Nkunku",
  "from": "AC Milan",
  "to": "RB Leipzig",
  "toKey": "rb-leipzig",
  "fee": "€3m loan (+€28m option)",
  "type": "loan",
  "status": "official",
  "note": "Season loan with €28m purchase option (acmilan.com)"
 },
 {
  "d": "2026-08-24",
  "p": "Ethan Wheatley",
  "from": "Man United",
  "to": "Lincoln City",
  "fromKey": "man-united",
  "type": "loan",
  "status": "official",
  "note": "Season loan to the Championship (manutd.com, The Linc); date approximate (late Aug)"
 },
 {
  "d": "2026-08-24",
  "p": "Mattia Perin",
  "from": "Juventus",
  "to": "Palermo",
  "fromKey": "juventus",
  "type": "transfer",
  "status": "official",
  "note": "Permanent move (Sportmediaset, Wikipedia season page)"
 },
 {
  "d": "2026-08-23",
  "p": "Jacob Devaney",
  "from": "Man United",
  "to": "Hibernian",
  "fromKey": "man-united",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option to buy (manutd.com, RTÉ)"
 },
 {
  "d": "2026-08-22",
  "p": "Benoît Badiashile",
  "from": "Chelsea",
  "to": "Napoli",
  "fromKey": "chelsea",
  "toKey": "napoli",
  "fee": "loan; ~€23–27m option",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option (chelseafc.com, Goal)"
 },
 {
  "d": "2026-08-22",
  "p": "Eljif Elmas",
  "from": "RB Leipzig",
  "to": "Atalanta",
  "fromKey": "rb-leipzig",
  "fee": "€2m loan (+€12m option)",
  "type": "loan",
  "status": "official",
  "note": "Loan for 2026-27 with €12m purchase option (ligainsider.de)"
 },
 {
  "d": "2026-08-22",
  "p": "Metehan Baltacı",
  "from": "Galatasaray",
  "to": "Gençlerbirliği",
  "fromKey": "galatasaray",
  "type": "loan",
  "status": "official",
  "note": "Loan for 2026-27 after a contract extension to 2029 (aspor.com.tr)"
 },
 {
  "d": "2026-08-22",
  "p": "Elias Jelert",
  "from": "Galatasaray",
  "to": "Le Havre",
  "fromKey": "galatasaray",
  "type": "loan",
  "status": "official",
  "note": "Loan until end of 2026-27 (galatasaray.org)"
 },
 {
  "d": "2026-08-22",
  "p": "Mehdi Taremi",
  "from": "Olympiacos",
  "to": "Al Wasl",
  "fromKey": "olympiacos",
  "type": "transfer",
  "status": "official",
  "note": "Nominal fee, to the UAE (alwaslsc.ae)"
 },
 {
  "d": "2026-08-22",
  "p": "Armando González",
  "from": "Chivas",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "fee": "~€8.6m",
  "type": "transfer",
  "status": "official",
  "note": "Striker from Chivas Guadalajara (olympiacos.org)"
 },
 {
  "d": "2026-08-21",
  "p": "Ezri Konsa",
  "from": "Aston Villa",
  "to": "Arsenal",
  "fromKey": "aston-villa",
  "toKey": "arsenal",
  "fee": "£51m (+£4m)",
  "type": "transfer",
  "status": "official",
  "note": "Arsenal announced 21 Aug (arsenal.com, Sky Sports)"
 },
 {
  "d": "2026-08-21",
  "p": "Curtis Jones",
  "from": "Liverpool",
  "to": "Inter",
  "fromKey": "liverpool",
  "toKey": "inter",
  "fee": "€30m (+€5m) / £25.7m+£4.3m",
  "type": "transfer",
  "status": "official",
  "note": "Inter announced 21 Aug; five-year deal, 10% sell-on (ESPN, Sky Sports)"
 },
 {
  "d": "2026-08-21",
  "p": "Dominik Livaković",
  "from": "Fenerbahçe",
  "to": "Barcelona",
  "toKey": "barcelona",
  "fee": "€2m (+variables)",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 30 June 2030; ~€2m fixed plus variables (RPP, WDeportes, ESPN)"
 },
 {
  "d": "2026-08-21",
  "p": "Arthur",
  "from": "Juventus",
  "to": "Free agent",
  "fromKey": "juventus",
  "type": "free",
  "status": "official",
  "note": "Contract terminated by mutual consent (Sportmediaset, Calcio e Finanza, Fantacalcio)"
 },
 {
  "d": "2026-08-21",
  "p": "Lutsharel Geertruida",
  "from": "RB Leipzig",
  "to": "PSV",
  "fromKey": "rb-leipzig",
  "toKey": "psv",
  "type": "loan",
  "status": "official",
  "note": "Season loan (Get German Football News)"
 },
 {
  "d": "2026-08-21",
  "p": "Giorgi Kochorashvili",
  "from": "Sporting CP",
  "to": "Sevilla",
  "fromKey": "sporting",
  "fee": "€4.5m",
  "type": "transfer",
  "status": "official",
  "note": "~€4.5m, to 2030 (Sevilla FC, COPE)"
 },
 {
  "d": "2026-08-21",
  "p": "Don-Angelo Konadu",
  "from": "Ajax",
  "to": "Lommel SK",
  "fromKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "Loan until 30 Jun 2027 with purchase option (ajax.nl)"
 },
 {
  "d": "2026-08-21",
  "p": "Fedde Leysen",
  "from": "Union SG",
  "to": "Sassuolo",
  "fromKey": "union-sg",
  "fee": "loan; ~€8m conditional obligation",
  "type": "loan",
  "status": "official",
  "note": "Loan with option that becomes an obligation if Sassuolo stay up (sassuolocalcio.it)"
 },
 {
  "d": "2026-08-20",
  "p": "João Cancelo",
  "from": "Free agent",
  "to": "Barcelona",
  "toKey": "barcelona",
  "type": "free",
  "status": "official",
  "note": "Returns on a free, three-year deal (fcbarcelona.es, Excelsior)"
 },
 {
  "d": "2026-08-20",
  "p": "Troy Parrott",
  "from": "AZ Alkmaar",
  "to": "Real Betis",
  "toKey": "real-betis",
  "fee": "€16m (+€4m)",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal to June 2031; €16m fixed + €4m variables (realbetisbalompie.es, El Desmarque)"
 },
 {
  "d": "2026-08-20",
  "p": "Iván Jaime",
  "from": "Porto",
  "to": "Las Palmas",
  "fromKey": "porto",
  "fee": "loan; €3m option",
  "type": "loan",
  "status": "official",
  "note": "Loan until end of season with €3m option (fcporto.pt)"
 },
 {
  "d": "2026-08-20",
  "p": "Aleksey Batrakov",
  "from": "Lokomotiv Moscow",
  "to": "Galatasaray",
  "toKey": "galatasaray",
  "fee": "€25m",
  "type": "transfer",
  "status": "official",
  "note": "Five-year contract (galatasaray.org)"
 },
 {
  "d": "2026-08-20",
  "p": "Pablo Maffeo",
  "from": "Olympiacos",
  "to": "Valencia",
  "fromKey": "olympiacos",
  "fee": "loan; €3m option",
  "type": "loan",
  "status": "official",
  "note": "Season loan with €3m purchase option, two months after joining from Mallorca (valenciacf.com)"
 },
 {
  "d": "2026-08-19",
  "p": "Tijjani Reijnders",
  "from": "Man City",
  "to": "Al Qadsiah",
  "fromKey": "man-city",
  "type": "transfer",
  "status": "official",
  "note": "Club-confirmed move to Saudi Pro League after one season; four-year deal (mancity.com, ESPN)",
  "w": "https://en.wikipedia.org/wiki/Tijjani_Reijnders",
  "fee": "€61m (~£52m)"
 },
 {
  "d": "2026-08-19",
  "p": "Zion Suzuki",
  "from": "Parma",
  "to": "Aston Villa",
  "toKey": "aston-villa",
  "fee": "€35m (£30m) + add-ons",
  "type": "transfer",
  "status": "official",
  "note": "Emi Martínez's replacement; missing from ledger (avfc.co.uk, ESPN)"
 },
 {
  "d": "2026-08-19",
  "p": "Matteo Ruggeri",
  "from": "Atlético Madrid",
  "to": "Aston Villa",
  "fromKey": "atletico-madrid",
  "toKey": "aston-villa",
  "fee": "€25m (+€1.5m)",
  "type": "transfer",
  "status": "official",
  "note": "Missing from ledger (avfc.co.uk, Football Italia)"
 },
 {
  "d": "2026-08-19",
  "p": "Kosta Nedeljković",
  "from": "Aston Villa",
  "to": "Rangers",
  "fromKey": "aston-villa",
  "fee": "loan; £4m obligation",
  "type": "loan",
  "status": "official",
  "note": "Season loan, obligation triggered on appearances (Sky Sports, STV)"
 },
 {
  "d": "2026-08-19",
  "p": "Costantino Favasuli",
  "from": "Catanzaro",
  "to": "Napoli",
  "toKey": "napoli",
  "fee": "€1m loan (+€6m obligation)",
  "type": "loan",
  "status": "official",
  "note": "Loan with obligation (€1m + €6m); contract to 2031 (Il Messaggero, NapoliToday)"
 },
 {
  "d": "2026-08-19",
  "p": "Vince Osuji",
  "from": "Club Brugge",
  "to": "Tromsø",
  "fromKey": "club-brugge",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 2029 (clubbrugge.be)"
 },
 {
  "d": "2026-08-18",
  "p": "Guglielmo Vicario",
  "from": "Tottenham",
  "to": "Juventus",
  "fromKey": "tottenham",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option (tottenhamhotspur.com, ESPN, Football Italia)",
  "w": "https://en.wikipedia.org/wiki/Guglielmo_Vicario",
  "fee": "loan; £8.6m (€10m) option",
  "toKey": "juventus"
 },
 {
  "d": "2026-08-18",
  "p": "Rodri",
  "from": "Man City",
  "to": "Barcelona",
  "fromKey": "man-city",
  "toKey": "barcelona",
  "type": "transfer",
  "status": "official",
  "note": "Barcelona announced; contract to 2030 (Al Jazeera, ESPN)",
  "w": "https://en.wikipedia.org/wiki/Rodri_(footballer%2C_born_1996)",
  "fee": "€60m (+€16.5m)"
 },
 {
  "d": "2026-08-18",
  "p": "Joey Veerman",
  "from": "PSV",
  "to": "Dortmund",
  "fromKey": "psv",
  "fee": "€22m",
  "type": "clause",
  "status": "official",
  "note": "€22m release clause triggered; to 2031, No. 25 (BVB.de, PSV.nl, Bundesliga.com)"
 },
 {
  "d": "2026-08-18",
  "p": "Ali Bülbül",
  "from": "Galatasaray",
  "to": "Amed SK",
  "fromKey": "galatasaray",
  "type": "loan",
  "status": "official",
  "note": "Two-year loan-to-buy with purchase option in Amed's favour (amedspor.com.tr)"
 },
 {
  "d": "2026-08-18",
  "p": "André Luiz",
  "from": "Olympiacos",
  "to": "Sporting Kansas City",
  "fromKey": "olympiacos",
  "fee": "~$18m",
  "type": "transfer",
  "status": "official",
  "note": "Club-record MLS sale (sportingkc.com)"
 },
 {
  "d": "2026-08-18",
  "p": "Promise David",
  "from": "Union SG",
  "to": "Brighton",
  "fromKey": "union-sg",
  "fee": "loan; ~£22m obligation",
  "type": "loan",
  "status": "official",
  "note": "Season loan with obligation to buy, a club-record fee (brightonandhovealbion.com)"
 },
 {
  "d": "2026-08-17",
  "p": "Jhon Lucumí",
  "from": "Bologna",
  "to": "Juventus",
  "toKey": "juventus",
  "fee": "€19.5m (+€2m)",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 30 June 2030; €19.5m + €0.6m fees + up to €2m bonuses (juventus.com, Sky Italia, Corriere dello Sport)"
 },
 {
  "d": "2026-08-17",
  "p": "Diant Ramaj",
  "from": "Borussia Dortmund",
  "to": "FC Copenhagen",
  "fromKey": "dortmund",
  "fee": "loan; €5m option",
  "type": "loan",
  "status": "official",
  "note": "Loan for 2026-27 with €5m purchase option (bvb.de)"
 },
 {
  "d": "2026-08-17",
  "p": "Jofre Torrents",
  "from": "Barcelona",
  "to": "Ajax",
  "fromKey": "barcelona",
  "toKey": "ajax",
  "type": "free",
  "status": "official",
  "note": "19-year-old defender, free from Barcelona on a four-year deal (ziggo.nl)"
 },
 {
  "d": "2026-08-16",
  "p": "Mika Godts",
  "from": "Ajax",
  "to": "PSG",
  "fromKey": "ajax",
  "toKey": "psg",
  "fee": "up to €55m",
  "type": "transfer",
  "status": "official",
  "note": "To 2031, No. 22; Ajax says fee can reach €55m with bonuses (PSG.fr, Ajax1, ESPN)"
 },
 {
  "d": "2026-08-16",
  "p": "Giannis Konstantelias",
  "from": "PAOK",
  "to": "Dortmund",
  "toKey": "dortmund",
  "fee": "€26m (+€6m)",
  "type": "transfer",
  "status": "official",
  "note": "To 2030; €26m + €6m add-ons, 15% sell-on (BVB.de 17 Aug, Bundesliga.com). Tore an ACL vs Hamburg on 31 Aug — out several months"
 },
 {
  "d": "2026-08-15",
  "p": "Djed Spence",
  "from": "Tottenham",
  "to": "Inter",
  "fromKey": "tottenham",
  "toKey": "inter",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal, 10% sell-on (tottenhamhotspur.com, Sky Sports, ESPN)",
  "fee": "£30m"
 },
 {
  "d": "2026-08-15",
  "p": "Cristian Romero",
  "from": "Tottenham",
  "to": "Atlético Madrid",
  "toKey": "atletico-madrid",
  "fee": "€35m (+€5m)",
  "type": "transfer",
  "status": "official",
  "note": "Captain leaves on a five-year deal; missing from ledger (tottenhamhotspur.com, Sky Sports, ESPN)"
 },
 {
  "d": "2026-08-15",
  "p": "Nestory Irankunda",
  "from": "Watford",
  "to": "Sporting CP",
  "toKey": "sporting",
  "fee": "€15m",
  "type": "transfer",
  "status": "official",
  "note": "~€15m, to 2031, €80m clause (Notícias ao Minuto, Zerozero, A Bola)"
 },
 {
  "d": "2026-08-15",
  "p": "Anan Khalaili",
  "from": "Union SG",
  "to": "Crystal Palace",
  "fromKey": "union-sg",
  "fee": "€24.5m",
  "type": "transfer",
  "status": "official",
  "note": "£21m/€24.5m, club-record sale, to 2031 (CPFC.co.uk, Brussels Times)"
 },
 {
  "d": "2026-08-15",
  "p": "Ashley Phillips",
  "from": "Tottenham",
  "to": "Middlesbrough",
  "fromKey": "tottenham",
  "fee": "£7m (+ add-ons, up to £20m reported)",
  "type": "transfer",
  "status": "official",
  "note": "Missing from ledger (tottenhamhotspur.com, Gazette Live)"
 },
 {
  "d": "2026-08-15",
  "p": "Davide Frattesi",
  "from": "Inter",
  "to": "Lazio",
  "fromKey": "inter",
  "fee": "€5m loan",
  "type": "loan",
  "status": "official",
  "note": "Loan with option to buy (€5m loan + €3m bonuses, €10m option, 50% sell-on reported); Lazio announced 14–15 Aug (ANSA, Lazio, fcinter1908)"
 },
 {
  "d": "2026-08-14",
  "p": "Samuel Iling-Junior",
  "from": "Aston Villa",
  "to": "Bolton Wanderers",
  "fromKey": "aston-villa",
  "type": "loan",
  "status": "official",
  "note": "Season loan; missing from ledger (Bolton Wanderers/BBC via Yahoo)"
 },
 {
  "d": "2026-08-14",
  "p": "Ferran Torres",
  "from": "Barcelona",
  "to": "PSG",
  "fromKey": "barcelona",
  "toKey": "psg",
  "fee": "€50m",
  "type": "transfer",
  "status": "official",
  "note": "Four-year deal at PSG; €50m with no variables (Que.es, Eurosport ES)"
 },
 {
  "d": "2026-08-14",
  "p": "Zachary Athekame",
  "from": "AC Milan",
  "to": "Lyon",
  "toKey": "lyon",
  "type": "loan",
  "status": "official",
  "note": "Right-back loaned to OL until June 2027 (Foot Mercato table); parent club not verified; not in site squad"
 },
 {
  "d": "2026-08-14",
  "p": "Almugera Kabar",
  "from": "Borussia Dortmund",
  "to": "NEC Nijmegen",
  "fromKey": "dortmund",
  "type": "loan",
  "status": "official",
  "note": "Loan until end of 2026-27 (bvb.de)"
 },
 {
  "d": "2026-08-14",
  "p": "Halil Dervişoğlu",
  "from": "Galatasaray",
  "to": "Gaziantep FK",
  "fromKey": "galatasaray",
  "type": "loan",
  "status": "official",
  "note": "Loan until end of season (fotomac.com.tr)"
 },
 {
  "d": "2026-08-14",
  "p": "Ludovit Reis",
  "from": "Club Brugge",
  "to": "Werder Bremen",
  "fromKey": "club-brugge",
  "type": "transfer",
  "status": "official",
  "note": "No guaranteed fee, bonuses plus sell-on; contract to 2029 (werder.de)"
 },
 {
  "d": "2026-08-13",
  "p": "Ethan Williams",
  "from": "Man United",
  "to": "Peterborough United",
  "fromKey": "man-united",
  "type": "transfer",
  "status": "official",
  "note": "Undisclosed, reported >£750k; missing from ledger (manutd.com, Peterborough Today)"
 },
 {
  "d": "2026-08-12",
  "p": "Evann Guessand",
  "from": "Aston Villa",
  "to": "Crystal Palace",
  "fromKey": "aston-villa",
  "fee": "loan; option to buy",
  "type": "loan",
  "status": "official",
  "note": "Returns to Palace on a season loan; missing from ledger (cpfc.co.uk)"
 },
 {
  "d": "2026-08-12",
  "p": "Pep Chavarría",
  "from": "Rayo Vallecano",
  "to": "Chelsea",
  "toKey": "chelsea",
  "fee": "£16.3m initial (~€21m)",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal; missing from ledger (chelseafc.com, ESPN)"
 },
 {
  "d": "2026-08-12",
  "p": "Dušan Vlahović",
  "from": "Juventus",
  "to": "Beşiktaş",
  "fromKey": "juventus",
  "type": "free",
  "status": "official",
  "note": "Left on a free (Wikipedia season page, settecalcio)"
 },
 {
  "d": "2026-08-12",
  "p": "Romelu Lukaku",
  "from": "Napoli",
  "to": "Fenerbahçe",
  "fromKey": "napoli",
  "fee": "€7.2m (loan + obligation)",
  "type": "transfer",
  "status": "official",
  "note": "Club statement; €1m loan with €6.2m obligation + €1m bonuses (Corriere dello Sport, napolimagazine, NapoliToday)"
 },
 {
  "d": "2026-08-12",
  "p": "Ege Araç",
  "from": "Galatasaray",
  "to": "Adana 01 FK",
  "fromKey": "galatasaray",
  "type": "loan",
  "status": "official",
  "note": "Season loan to the second-tier side (5ocakgazetesi.com)"
 },
 {
  "d": "2026-08-12",
  "p": "Bjorn Meijer",
  "from": "Club Brugge",
  "to": "Sampdoria",
  "fromKey": "club-brugge",
  "fee": "~€1m (+bonuses)",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 2030; bonuses and sell-on (sampdoria.it)"
 },
 {
  "d": "2026-08-11",
  "p": "Ousmane Diomande",
  "from": "Sporting CP",
  "to": "Nottingham Forest",
  "fromKey": "sporting",
  "fee": "£34.3m",
  "type": "transfer",
  "status": "official",
  "note": "£34.3m (~€40m), four-year deal (Sky Sports, Forest)"
 },
 {
  "d": "2026-08-11",
  "p": "Filip Jörgensen",
  "from": "Chelsea",
  "to": "Strasbourg",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan, no purchase option (beinsports.com)"
 },
 {
  "d": "2026-08-11",
  "p": "Enzo Molebe",
  "from": "Olympique Lyonnais",
  "to": "Lausanne-Sport",
  "fromKey": "lyon",
  "type": "loan",
  "status": "official",
  "note": "Loan until 30 Jun 2027, no option (lausanne-sport.ch)"
 },
 {
  "d": "2026-08-11",
  "p": "Samuel Portugal",
  "from": "Porto",
  "to": "Gil Vicente",
  "fromKey": "porto",
  "type": "transfer",
  "status": "official",
  "note": "Permanent; Porto keep 40% of economic rights (fcporto.pt)"
 },
 {
  "d": "2026-08-10",
  "p": "Ronald Araújo",
  "from": "Barcelona",
  "to": "Liverpool",
  "fromKey": "barcelona",
  "toKey": "liverpool",
  "fee": "loan; €55m option",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option to buy; missing from ledger (Sky Sports, ESPN, liverpoolfc.com)"
 },
 {
  "d": "2026-08-10",
  "p": "Manor Solomon",
  "from": "Tottenham",
  "to": "West Ham",
  "fromKey": "tottenham",
  "fee": "£7m",
  "type": "transfer",
  "status": "official",
  "note": "Missing from ledger (tottenhamhotspur.com, WHUFC)"
 },
 {
  "d": "2026-08-09",
  "p": "Lucas Digne",
  "from": "Aston Villa",
  "to": "PSG",
  "fromKey": "aston-villa",
  "toKey": "psg",
  "fee": "€10m clause",
  "type": "clause",
  "status": "official",
  "note": "Three-year deal, a decade after his first spell",
  "w": "https://en.wikipedia.org/wiki/Lucas_Digne"
 },
 {
  "d": "2026-08-09",
  "p": "Trevoh Chalobah",
  "from": "Chelsea",
  "to": "Como",
  "fromKey": "chelsea",
  "fee": "£30m+",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal; missing from ledger (chelseafc.com, ESPN)"
 },
 {
  "d": "2026-08-08",
  "p": "Bruno Guimarães",
  "from": "Newcastle",
  "to": "Arsenal",
  "toKey": "arsenal",
  "fee": "£75m",
  "type": "transfer",
  "status": "official",
  "note": "Fixed fee, 4+1 years — record for a midfielder aged 28 or over",
  "w": "https://en.wikipedia.org/wiki/Bruno_Guimar%C3%A3es"
 },
 {
  "d": "2026-08-08",
  "p": "Radek Vítek",
  "from": "Man United",
  "to": "Middlesbrough",
  "fromKey": "man-united",
  "fee": "£7m (+£7m)",
  "type": "transfer",
  "status": "official",
  "note": "Missing from ledger (manutd.com, Gazette Live)"
 },
 {
  "d": "2026-08-08",
  "p": "Nahuel Molina",
  "from": "Atlético Madrid",
  "to": "Roma",
  "fromKey": "atletico-madrid",
  "fee": "€13m",
  "type": "transfer",
  "status": "official",
  "note": "Permanent sale (Infobae, fichajes.com)"
 },
 {
  "d": "2026-08-07",
  "p": "Gerónimo Rulli",
  "from": "Marseille",
  "to": "Man City",
  "toKey": "man-city",
  "fee": "£1.7m",
  "type": "transfer",
  "status": "official",
  "note": "Two-year deal as Donnarumma's understudy (mancity.com, beIN)",
  "fromKey": "marseille"
 },
 {
  "d": "2026-08-07",
  "p": "Altay Bayındır",
  "from": "Man United",
  "to": "Celta Vigo",
  "fromKey": "man-united",
  "fee": "loan; ~£3.5m option",
  "type": "loan",
  "status": "official",
  "note": "Season loan with purchase option; missing from ledger (manutd.com, ESPN)"
 },
 {
  "d": "2026-08-07",
  "p": "Georgios Masouras",
  "from": "Olympiacos",
  "to": "NEOM SC",
  "fromKey": "olympiacos",
  "type": "transfer",
  "status": "official",
  "note": "Two-year deal in Saudi Arabia (thrylos7intl.com)"
 },
 {
  "d": "2026-08-06",
  "p": "Yan Diomandé",
  "from": "RB Leipzig",
  "to": "Real Madrid",
  "fromKey": "rb-leipzig",
  "toKey": "real-madrid",
  "fee": "€125m (+€15m)",
  "type": "transfer",
  "status": "official",
  "note": "Club-record signing, past Bellingham; Leipzig's record sale",
  "w": "https://en.wikipedia.org/wiki/Yan_Diomande"
 },
 {
  "d": "2026-08-06",
  "p": "Maghnes Akliouche",
  "from": "Monaco",
  "to": "PSG",
  "toKey": "psg",
  "fee": "€50m",
  "type": "transfer",
  "status": "official",
  "note": "To 2031; takes the No. 11 shirt",
  "w": "https://en.wikipedia.org/wiki/Maghnes_Akliouche"
 },
 {
  "d": "2026-08-06",
  "p": "Mohamed Salah",
  "from": "Liverpool",
  "to": "Trabzonspor",
  "fromKey": "liverpool",
  "type": "free",
  "status": "official",
  "note": "Two-year deal; contract mutually ended in March after nine years at Anfield",
  "w": "https://en.wikipedia.org/wiki/Mohamed_Salah"
 },
 {
  "d": "2026-08-06",
  "p": "James Trafford",
  "from": "Man City",
  "to": "Leeds United",
  "fromKey": "man-city",
  "fee": "£40m (+£5m)",
  "type": "transfer",
  "status": "official",
  "note": "British-record GK fee; City keep 20% sell-on and matching rights (mancity.com, Leeds United, Sky)"
 },
 {
  "d": "2026-08-06",
  "p": "Francisco Ortega",
  "from": "Olympiacos",
  "to": "River Plate",
  "fromKey": "olympiacos",
  "fee": "€5m",
  "type": "transfer",
  "status": "official",
  "note": "Permanent (infobae.com)"
 },
 {
  "d": "2026-08-05",
  "p": "Franco Mastantuono",
  "from": "Real Madrid",
  "to": "Fiorentina",
  "fromKey": "real-madrid",
  "type": "loan",
  "status": "official",
  "note": "Season loan to 30 June 2027, no purchase option (realmadrid.com, El Español)"
 },
 {
  "d": "2026-08-05",
  "p": "Miguel Gutiérrez",
  "from": "Napoli",
  "to": "Bayer Leverkusen",
  "fromKey": "napoli",
  "fee": "€30m (+€2m)",
  "type": "transfer",
  "status": "official",
  "note": "Club statement; €30m plus €2m bonuses (ANSA, napolimagazine, tuttonapoli)"
 },
 {
  "d": "2026-08-05",
  "p": "Konstantinos Tzolakis",
  "from": "Olympiacos",
  "to": "Hull City",
  "fromKey": "olympiacos",
  "fee": "€20m",
  "type": "transfer",
  "status": "official",
  "note": "Club-record sale (beinsports.com)"
 },
 {
  "d": "2026-08-04",
  "p": "Freddie Potts",
  "from": "West Ham",
  "to": "Club Brugge",
  "toKey": "club-brugge",
  "fee": "€10m",
  "type": "transfer",
  "status": "official",
  "note": "€10m per FotMob; not in site squad"
 },
 {
  "d": "2026-08-04",
  "p": "Ørjan Nyland",
  "from": "Sevilla",
  "to": "RB Leipzig",
  "toKey": "rb-leipzig",
  "type": "free",
  "status": "official",
  "note": "Free transfer, contract to 2028; Gulácsi's replacement, No.1 (rbleipzig.com)"
 },
 {
  "d": "2026-08-04",
  "p": "Cisse Sandra",
  "from": "Club Brugge",
  "to": "Westerlo",
  "fromKey": "club-brugge",
  "fee": "~€1.5m",
  "type": "transfer",
  "status": "official",
  "note": "Four-year contract (voetbalkrant.com)"
 },
 {
  "d": "2026-08-03",
  "p": "Péter Gulácsi",
  "from": "RB Leipzig",
  "to": "Villarreal",
  "fromKey": "rb-leipzig",
  "type": "transfer",
  "status": "official",
  "note": "Two-season deal after eleven years; Vandevoordt takes the gloves",
  "w": "https://en.wikipedia.org/wiki/Péter_Gulácsi"
 },
 {
  "d": "2026-08-03",
  "p": "Jordan Henderson",
  "from": "Brentford",
  "to": "Chelsea",
  "toKey": "chelsea",
  "type": "free",
  "status": "official",
  "note": "Two-year deal after leaving Brentford by mutual consent; missing from ledger (chelseafc.com, Sky Sports)"
 },
 {
  "d": "2026-08-03",
  "p": "Gonzalo García",
  "from": "Real Madrid",
  "to": "Fulham",
  "fromKey": "real-madrid",
  "fee": "€40m",
  "type": "transfer",
  "status": "official",
  "note": "Club statement; Fulham bought 70% of rights, Madrid keep buy-back; to 2031 (realmadrid.com, ESPN, COPE)"
 },
 {
  "d": "2026-08-03",
  "p": "João Mário",
  "from": "Juventus",
  "to": "Fiorentina",
  "fromKey": "juventus",
  "fee": "€1.8m loan",
  "type": "loan",
  "status": "official",
  "note": "Loan for 2026-27, €1.8m with €9.5m option (juventus.com, A Bola)"
 },
 {
  "d": "2026-08-03",
  "p": "Konstantinos Karetsas",
  "from": "Genk",
  "to": "Dortmund",
  "toKey": "dortmund",
  "fee": "€32m",
  "type": "transfer",
  "status": "official",
  "note": "To 2031 (BVB.de, Bundesliga.com); missing from ledger and squad"
 },
 {
  "d": "2026-08-03",
  "p": "Lee Han-beom",
  "from": "Midtjylland",
  "to": "Club Brugge",
  "toKey": "club-brugge",
  "fee": "€7m",
  "type": "transfer",
  "status": "official",
  "note": "€7m per FotMob; not in site squad"
 },
 {
  "d": "2026-08-03",
  "p": "Vasilije Adžić",
  "from": "Juventus",
  "to": "Sassuolo",
  "fromKey": "juventus",
  "fee": "€0.5m loan (+€12m option)",
  "type": "loan",
  "status": "official",
  "note": "Loan with option to buy (sportmediaset.mediaset.it)"
 },
 {
  "d": "2026-08-02",
  "p": "Randal Kolo Muani",
  "from": "PSG",
  "to": "Juventus",
  "fromKey": "psg",
  "toKey": "juventus",
  "fee": "€38m (+€12m)",
  "type": "transfer",
  "status": "official",
  "note": "Permanent after the Tottenham loan; to 2031, No. 9",
  "w": "https://en.wikipedia.org/wiki/Randal_Kolo_Muani"
 },
 {
  "d": "2026-08-02",
  "p": "Mamadou Thierno Barry",
  "from": "Union SG",
  "to": "Al-Shabab",
  "fromKey": "union-sg",
  "type": "loan",
  "status": "official",
  "note": "Season loan with an option to buy",
  "w": "https://en.wikipedia.org/wiki/Mamadou_Thierno_Barry"
 },
 {
  "d": "2026-08-02",
  "p": "Kerim Alajbegović",
  "from": "Bayer Leverkusen",
  "to": "Juventus",
  "toKey": "juventus",
  "fee": "€30m (+bonuses)",
  "type": "transfer",
  "status": "official",
  "note": "Permanent; €30m plus fees/bonuses (Sky Italia lists €30m+, Wikipedia €32m)"
 },
 {
  "d": "2026-08-02",
  "p": "Raphael Onyedika",
  "from": "Club Brugge",
  "to": "Eintracht Frankfurt",
  "fromKey": "club-brugge",
  "fee": "€9m",
  "type": "transfer",
  "status": "official",
  "note": "€9m per FotMob transfer log; club statement not retrieved"
 },
 {
  "d": "2026-08-02",
  "p": "Felix Bacher",
  "from": "Estoril",
  "to": "Lyon",
  "toKey": "lyon",
  "type": "transfer",
  "status": "official",
  "note": "Centre-back, listed among OL's seven summer signings (Foot Mercato table, Mercatoprime); date/fee unverified; not in site squad",
  "fee": "€5.1m"
 },
 {
  "d": "2026-08-02",
  "p": "Souleymane Faye",
  "from": "Sporting CP",
  "to": "Lorient",
  "fromKey": "sporting",
  "fee": "loan; €6.5m option",
  "type": "loan",
  "status": "official",
  "note": "Loan with €6.5m purchase option (fclorient.bzh)"
 },
 {
  "d": "2026-08-01",
  "p": "Danny Welbeck",
  "from": "Brighton",
  "to": "Chelsea",
  "toKey": "chelsea",
  "fee": "~£5m–£6.7m (undisclosed)",
  "type": "transfer",
  "status": "official",
  "note": "Two-year deal; missing from ledger (chelseafc.com, ESPN)"
 },
 {
  "d": "2026-08-01",
  "p": "Ebenezer Akinsanmiro",
  "from": "Inter Milan",
  "to": "Monza",
  "fromKey": "inter",
  "fee": "loan; ~€7.5m obligation",
  "type": "loan",
  "status": "official",
  "note": "Loan with conditional obligation to buy (fcinter1908.it / calciomercato.com)"
 },
 {
  "d": "2026-08-01",
  "p": "Jonas Rouhi",
  "from": "Juventus",
  "to": "Carrarese",
  "fromKey": "juventus",
  "type": "loan",
  "status": "official",
  "note": "Second consecutive loan to the Serie B side, until 30 Jun 2027 (calciomercato.com)"
 },
 {
  "d": "2026-08-01",
  "p": "Argyris Liatsikouras",
  "from": "Olympiacos",
  "to": "Kalamata",
  "fromKey": "olympiacos",
  "type": "loan",
  "status": "official",
  "note": "Loan to the Super League 2 side (goal.com)"
 },
 {
  "d": "2026-08",
  "p": "Juma Bah",
  "from": "Man City",
  "to": "Augsburg",
  "fromKey": "man-city",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option to buy, announced late August (exact date not verified) (Bundesliga.com, FC Augsburg)"
 },
 {
  "d": "2026-08",
  "p": "Cristian Orozco",
  "from": "Fortaleza CEIF",
  "to": "Man United",
  "toKey": "man-united",
  "type": "transfer",
  "status": "official",
  "note": "18-year-old Colombian midfielder, U21s (manutd.com, Goal)"
 },
 {
  "d": "2026-08",
  "p": "Aaron Wan-Bissaka",
  "from": "West Ham",
  "to": "Aston Villa",
  "toKey": "aston-villa",
  "type": "loan",
  "status": "official",
  "note": "Listed by Villa among the 10 summer arrivals (between Ruggeri 19 Aug and Goretzka 27 Aug); exact date not verified (avfc.co.uk)"
 },
 {
  "d": "2026-08",
  "p": "Valentín Barco",
  "from": "Strasbourg",
  "to": "Chelsea",
  "toKey": "chelsea",
  "type": "transfer",
  "status": "official",
  "note": "Seven-year deal to 2033, early August; missing from ledger (chelseafc.com, ESPN)"
 },
 {
  "d": "2026-08",
  "p": "Santiago Giménez",
  "from": "AC Milan",
  "to": "Porto",
  "toKey": "porto",
  "type": "loan",
  "status": "official",
  "note": "Loan with €18m + €2m option that can become an obligation (Record, Zerozero, ESPN); announced ~30–31 Aug"
 },
 {
  "d": "2026-08",
  "p": "Jan Virgili",
  "from": "Mallorca",
  "to": "Club Brugge",
  "toKey": "club-brugge",
  "fee": "€12m",
  "type": "transfer",
  "status": "official",
  "note": "€12m per FotMob ('recently'); date unverified; not in site squad"
 },
 {
  "d": "2026-08",
  "p": "Michel-Ange Balikwisha",
  "from": "Celtic",
  "to": "Gent",
  "fromKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Loan with option; agreed 28 Aug (ReadCeltic), listed as departed by Sports Mole"
 },
 {
  "d": "2026-08",
  "p": "Remo Freuler",
  "from": "Bologna",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "type": "transfer",
  "status": "official",
  "note": "August arrival per Worldfootball/AiScore logs; fee/date unverified; not in site squad"
 },
 {
  "d": "2026-08",
  "p": "Nair Tiknizyan",
  "from": "Red Star Belgrade",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "type": "transfer",
  "status": "official",
  "note": "August arrival per Worldfootball/AiScore; not in site squad"
 },
 {
  "d": "2026-08",
  "p": "Yang Min-hyeok",
  "from": "Tottenham",
  "to": "Westerlo",
  "fromKey": "tottenham",
  "type": "loan",
  "status": "official",
  "note": "Season loan to Belgium; exact date not verified (TEAMtalk, Spurs Web)"
 },
 {
  "d": "2026-08",
  "p": "Leonardo Balerdi",
  "from": "Marseille",
  "to": "Roma",
  "fromKey": "marseille",
  "fee": "€1m loan (+~€15m)",
  "type": "loan",
  "status": "official",
  "note": "€1m paid loan, option likely to become obligation (~€15m) (AS Roma, GFFN); late August"
 },
 {
  "d": "2026-08",
  "p": "Adam Montgomery",
  "from": "Celtic",
  "to": "Livingston",
  "fromKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Loaned out per Sports Mole; club unverified"
 },
 {
  "d": "2026-08",
  "p": "Mamadou Sarr",
  "from": "Chelsea",
  "to": "Real Sociedad",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan, no purchase option (chelseafc.com)"
 },
 {
  "d": "2026-08",
  "p": "Genesis Antwi",
  "from": "Chelsea",
  "to": "Strasbourg",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan (chelseafc.com)"
 },
 {
  "d": "2026-08",
  "p": "Kodai Sano",
  "from": "NEC",
  "to": "PSV",
  "toKey": "psv",
  "fee": "~€14.5m",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 2031, shirt 24 (psv.nl)"
 },
 {
  "d": "2026-08",
  "p": "Filip Kostić",
  "from": "Juventus",
  "to": "PSV",
  "fromKey": "juventus",
  "toKey": "psv",
  "type": "free",
  "status": "official",
  "note": "Free agent after his Juventus contract ended; two-year deal, shirt 18 (psv.nl)"
 },
 {
  "d": "2026-08",
  "p": "Ko Itakura",
  "from": "Ajax",
  "to": "Borussia Mönchengladbach",
  "fromKey": "ajax",
  "fee": "€3.5m (+bonuses)",
  "type": "transfer",
  "status": "official",
  "note": "Four-year deal (vi.nl)"
 },
 {
  "d": "2026-08",
  "p": "Ahmetcan Kaplan",
  "from": "Ajax",
  "to": "NEC",
  "fromKey": "ajax",
  "fee": "€2.5m",
  "type": "transfer",
  "status": "official",
  "note": "Contract to 2030 (voetbalzone.nl)"
 },
 {
  "d": "2026-07-31",
  "p": "Marc-André ter Stegen",
  "from": "Barcelona",
  "to": "Ajax",
  "fromKey": "barcelona",
  "toKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "Season loan to 30 June 2027; Barça pay ~90% of salary (fcbarcelona.com, DAZN)"
 },
 {
  "d": "2026-07-31",
  "p": "Jesse Bisiwu",
  "from": "Free agent",
  "to": "Barcelona",
  "toKey": "barcelona",
  "type": "free",
  "status": "official",
  "note": "Belgian winger signed to 2031 (fcbarcelona.es)"
 },
 {
  "d": "2026-07-31",
  "p": "Kian Fitz-Jim",
  "from": "Ajax",
  "to": "Torino",
  "fromKey": "ajax",
  "fee": "~€3m",
  "type": "transfer",
  "status": "official",
  "note": "Three-year deal (ajax.nl)"
 },
 {
  "d": "2026-07-31",
  "p": "Julian Brandt",
  "from": "Borussia Dortmund",
  "to": "Ajax",
  "fromKey": "dortmund",
  "toKey": "ajax",
  "type": "free",
  "status": "official",
  "note": "Free agent from Dortmund, contract to 2029 (english.ajax.nl)"
 },
 {
  "d": "2026-07-30",
  "p": "Tyler Fredricson",
  "from": "Man United",
  "to": "Lausanne-Sport",
  "fromKey": "man-united",
  "type": "transfer",
  "status": "official",
  "note": "Three-year deal; missing from ledger (manutd.com, beIN)"
 },
 {
  "d": "2026-07-30",
  "p": "Maxence Lacroix",
  "from": "Crystal Palace",
  "to": "Chelsea",
  "toKey": "chelsea",
  "fee": "£52m",
  "type": "transfer",
  "status": "official",
  "note": "Six-year deal; missing from ledger (chelseafc.com, Sky Sports)"
 },
 {
  "d": "2026-07-30",
  "p": "Carlos Espí",
  "from": "Levante",
  "to": "Real Madrid",
  "toKey": "real-madrid",
  "fee": "€25m",
  "type": "transfer",
  "status": "official",
  "note": "Club statement; five-year deal to 2031 (realmadrid.com, DAZN, Record)"
 },
 {
  "d": "2026-07-30",
  "p": "John Stones",
  "from": "Man City",
  "to": "Inter",
  "fromKey": "man-city",
  "type": "free",
  "status": "official",
  "note": "Two-year deal to 30 June 2028 (Sky Italia, Corriere dello Sport, Sportmediaset)"
 },
 {
  "d": "2026-07-29",
  "p": "Tolu Arokodare",
  "from": "Wolves",
  "to": "Ajax",
  "toKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "Season loan with purchase option (english.ajax.nl)"
 },
 {
  "d": "2026-07-28",
  "p": "Joe Gauci",
  "from": "Aston Villa",
  "to": "Lincoln City",
  "fromKey": "aston-villa",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan to League One",
  "w": "https://en.wikipedia.org/wiki/Joe_Gauci"
 },
 {
  "d": "2026-07-28",
  "p": "Thiago Almada",
  "from": "Atlético Madrid",
  "to": "River Plate",
  "fromKey": "atletico-madrid",
  "fee": "€20m",
  "type": "transfer",
  "status": "official",
  "note": "Permanent sale (fichajes.com, Infobae)"
 },
 {
  "d": "2026-07-28",
  "p": "Loïs Openda",
  "from": "Juventus",
  "to": "Lyon",
  "fromKey": "juventus",
  "fee": "€3.5m loan",
  "type": "loan",
  "status": "official",
  "note": "Loan to June 2027 for €3.5m (Wikipedia season page, juventusnews24)"
 },
 {
  "d": "2026-07-27",
  "p": "Kjell Scherpen",
  "from": "Union SG",
  "to": "Ipswich",
  "fromKey": "union-sg",
  "fee": "€10m",
  "type": "transfer",
  "status": "official",
  "note": "€10m (AiScore/Transferfeed logs); missing from ledger"
 },
 {
  "d": "2026-07-26",
  "p": "Daizen Maeda",
  "from": "Celtic",
  "to": "Ipswich Town",
  "fromKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Sold this summer per Sports Mole; buying club/fee not retrieved",
  "fee": "£8m (+£2m)"
 },
 {
  "d": "2026-07-25",
  "p": "Lee Kang-in",
  "from": "PSG",
  "to": "Atlético Madrid",
  "fromKey": "psg",
  "toKey": "atletico-madrid",
  "fee": "€35m (+€5m)",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal, inherits the No. 7",
  "w": "https://en.wikipedia.org/wiki/Lee_Kang-in"
 },
 {
  "d": "2026-07-24",
  "p": "Ricardo Mangas",
  "from": "Sporting CP",
  "to": "Monza",
  "fromKey": "sporting",
  "type": "loan",
  "status": "official",
  "note": "Loan until 30 Jun 2027 with conditional obligation to buy (acmonza.com)"
 },
 {
  "d": "2026-07-24",
  "p": "Keo Boets",
  "from": "KFC Dessel Sport",
  "to": "Union SG",
  "toKey": "union-sg",
  "type": "free",
  "status": "official",
  "note": "Goalkeeper signed on a free; on the UEFA squad list (sports.yahoo.com)"
 },
 {
  "d": "2026-07-23",
  "p": "Elliot Anderson",
  "from": "Nottingham Forest",
  "to": "Man City",
  "toKey": "man-city",
  "fee": "£116m",
  "type": "transfer",
  "status": "official",
  "note": "City record and, briefly, the British record",
  "w": "https://en.wikipedia.org/wiki/Elliot_Anderson"
 },
 {
  "d": "2026-07-23",
  "p": "Christos Tzolis",
  "from": "Club Brugge",
  "to": "Arsenal",
  "fromKey": "club-brugge",
  "toKey": "arsenal",
  "fee": "£34m",
  "type": "transfer",
  "status": "official",
  "note": "Belgian-record sale (€40m); takes the left-sided role vacated by Trossard",
  "w": "https://en.wikipedia.org/wiki/Christos_Tzolis"
 },
 {
  "d": "2026-07-23",
  "p": "Karim Adeyemi",
  "from": "Dortmund",
  "to": "Barcelona",
  "fromKey": "dortmund",
  "toKey": "barcelona",
  "fee": "€22m (+€7m)",
  "type": "transfer",
  "status": "official",
  "note": "To 2031, No. 14",
  "w": "https://en.wikipedia.org/wiki/Karim_Adeyemi"
 },
 {
  "d": "2026-07-23",
  "p": "Alejandro Garnacho",
  "from": "Chelsea",
  "to": "Aston Villa",
  "fromKey": "chelsea",
  "toKey": "aston-villa",
  "fee": "loan; conditional obligation (~£40m)",
  "type": "loan",
  "status": "official",
  "note": "Missing from ledger (avfc.co.uk, ESPN, Sky Sports)"
 },
 {
  "d": "2026-07-23",
  "p": "Achraf Laâziri",
  "from": "Olympique Lyonnais",
  "to": "Ittihad Tanger",
  "fromKey": "lyon",
  "fee": "free (10% sell-on)",
  "type": "transfer",
  "status": "official",
  "note": "Sold for no fee with a 10% sell-on clause (olympique-et-lyonnais.com)"
 },
 {
  "d": "2026-07-22",
  "p": "Ibrahima Ba",
  "from": "Famalicão",
  "to": "Sporting CP",
  "toKey": "sporting",
  "type": "transfer",
  "status": "official",
  "note": "Named in Sporting.pt's list of 2026/27 signings; details unverified; not in site squad",
  "fee": "€21.25m"
 },
 {
  "d": "2026-07-19",
  "p": "Ahmed Kutucu",
  "from": "Galatasaray",
  "to": "Çaykur Rizespor",
  "fromKey": "galatasaray",
  "type": "loan",
  "status": "official",
  "note": "One-season loan (fotomac.com.tr)"
 },
 {
  "d": "2026-07-15",
  "p": "Leandro Trossard",
  "from": "Arsenal",
  "to": "Beşiktaş",
  "fromKey": "arsenal",
  "fee": "£15.3m (+£1.7m)",
  "type": "transfer",
  "status": "official",
  "note": "Ledger lists exit without destination (arsenal.com, Sky Sports)"
 },
 {
  "d": "2026-07-15",
  "p": "Andrej Vasović",
  "from": "Luzern",
  "to": "Club Brugge",
  "toKey": "club-brugge",
  "fee": "€6m",
  "type": "transfer",
  "status": "official",
  "note": "€6m per FotMob; not in site squad"
 },
 {
  "d": "2026-07-11",
  "p": "Jeremy Monga",
  "from": "Leicester",
  "to": "Man City",
  "toKey": "man-city",
  "type": "transfer",
  "status": "official",
  "note": "17-year-old winger, contract to 2031; ~€14.7m reported (mancity.com, Sky Sports)"
 },
 {
  "d": "2026-07-11",
  "p": "Nohim Chibani",
  "from": "Quevilly-Rouen",
  "to": "Union SG",
  "toKey": "union-sg",
  "type": "free",
  "status": "official",
  "note": "Defender signed on a free (sports.yahoo.com)"
 },
 {
  "d": "2026-07-08",
  "p": "Illan Meslier",
  "from": "Leeds United",
  "to": "Arsenal",
  "toKey": "arsenal",
  "type": "free",
  "status": "official",
  "note": "Free agent, two-year deal plus option; third-choice GK (arsenal.com, Sky Sports)"
 },
 {
  "d": "2026-07-06",
  "p": "Alessandro Longoni",
  "from": "AC Milan",
  "to": "PSG",
  "toKey": "psg",
  "type": "free",
  "status": "official",
  "note": "Free transfer, contract to 2031; third goalkeeper, No.16 (psg.fr)"
 },
 {
  "d": "2026-07-05",
  "p": "Denzel Dumfries",
  "from": "Inter",
  "to": "Real Madrid",
  "fromKey": "inter",
  "toKey": "real-madrid",
  "fee": "€20m clause",
  "type": "clause",
  "status": "official",
  "note": "Release clause triggered; to 2030, cover behind Alexander-Arnold",
  "w": "https://en.wikipedia.org/wiki/Denzel_Dumfries"
 },
 {
  "d": "2026-07-04",
  "p": "Nathan Aké",
  "from": "Man City",
  "to": "Fenerbahçe",
  "fromKey": "man-city",
  "fee": "£7m (+£1.5m)",
  "type": "transfer",
  "status": "official",
  "note": "Ledger lists exit without destination (mancity.com, ESPN)"
 },
 {
  "d": "2026-07-03",
  "p": "Nathaniel Brown",
  "from": "Eintracht Frankfurt",
  "to": "Bayern",
  "toKey": "bayern",
  "fee": "€55m",
  "type": "transfer",
  "status": "official",
  "note": "To 2031, took the No. 11; Frankfurt's player of the season",
  "w": "https://en.wikipedia.org/wiki/Nathaniel_Brown_%28footballer%29"
 },
 {
  "d": "2026-07-02",
  "p": "Julien Duranville",
  "from": "Dortmund",
  "to": "Lyon",
  "fromKey": "dortmund",
  "toKey": "lyon",
  "fee": "€5m (+€3.5m)",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal to 2031; €5m + up to €3.5m bonuses, 20% sell-on (Walfoot, L'Avenir); missing from ledger, already in Lyon squad"
 },
 {
  "d": "2026-07-01",
  "p": "Piero Hincapié",
  "from": "Bayer Leverkusen",
  "to": "Arsenal",
  "toKey": "arsenal",
  "fee": "£34.5m",
  "type": "clause",
  "status": "official",
  "note": "Buy clause activated after title-winning loan season; five-year deal (arsenal.com)"
 },
 {
  "d": "2026-07",
  "p": "Ismael Saibari",
  "from": "PSV",
  "to": "Bayern",
  "fromKey": "psv",
  "toKey": "bayern",
  "fee": "€50m",
  "type": "transfer",
  "status": "official",
  "note": "PSV's record sale, agreed mid-World Cup",
  "w": "https://en.wikipedia.org/wiki/Ismael_Saibari"
 },
 {
  "d": "2026-07",
  "p": "Yann Sommer",
  "from": "Inter",
  "to": "Club Brugge",
  "fromKey": "inter",
  "toKey": "club-brugge",
  "type": "free",
  "status": "official",
  "note": "Three-year deal",
  "w": "https://en.wikipedia.org/wiki/Yann_Sommer"
 },
 {
  "d": "2026-07",
  "p": "Balša Popović",
  "from": "Red Star Belgrade",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "fee": "€1.5m",
  "type": "transfer",
  "status": "official",
  "note": "Red Star keep a 15% sell-on",
  "w": "https://en.wikipedia.org/wiki/Balša_Popović"
 },
 {
  "d": "2026-07",
  "p": "Kit Margetson",
  "from": "Swansea",
  "to": "Man United",
  "toKey": "man-united",
  "type": "free",
  "status": "official",
  "note": "20-year-old GK; compensation package agreed with Swansea (manutd.com)"
 },
 {
  "d": "2026-07",
  "p": "Kostas Fortounis",
  "from": "Olympiacos",
  "to": "Al Khaleej",
  "fromKey": "olympiacos",
  "type": "free",
  "status": "official",
  "note": "Free transfer in July per Worldfootball/FotMob logs; missing from ledger and still in site XI"
 },
 {
  "d": "2026-07",
  "p": "Stefan Ortega",
  "from": "Unattached",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "type": "free",
  "status": "official",
  "note": "July free signing per logs; not in site squad"
 },
 {
  "d": "2026-07",
  "p": "Gustavo Sá",
  "from": "Nottingham Forest",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "type": "loan",
  "status": "official",
  "note": "Bought by Nottingham Forest from Famalicão and loaned to Olympiacos (olympiacos.org)"
 },
 {
  "d": "2026-07",
  "p": "Manolis Saliakas",
  "from": "St. Pauli",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "fee": "~€1.5m",
  "type": "transfer",
  "status": "official",
  "note": "Right-back re-signed, contract to 2029 (fcstpauli.com)"
 },
 {
  "d": "2026-06-30",
  "p": "Casemiro",
  "from": "Man United",
  "to": "",
  "fromKey": "man-united",
  "type": "free",
  "status": "official",
  "note": "Contract expired; club confirmed exit alongside Sancho and Malacia (manutd.com)"
 },
 {
  "d": "2026-06-18",
  "p": "Víctor Muñoz",
  "from": "Osasuna",
  "to": "Liverpool",
  "toKey": "liverpool",
  "fee": "£34.5m",
  "type": "transfer",
  "status": "official",
  "note": "Six-year deal; missing from ledger (liverpoolfc.com, ESPN)"
 },
 {
  "d": "2026-06-17",
  "p": "Bernardo Silva",
  "from": "Man City",
  "to": "Real Madrid",
  "fromKey": "man-city",
  "toKey": "real-madrid",
  "type": "free",
  "status": "official",
  "note": "Two-year deal to 2028 after nine seasons and 20 trophies at City",
  "w": "https://en.wikipedia.org/wiki/Bernardo_Silva"
 },
 {
  "d": "2026-06",
  "p": "Pablo Maffeo",
  "from": "Mallorca",
  "to": "Olympiacos",
  "fee": "€3m",
  "type": "transfer",
  "status": "official",
  "note": "After Mallorca's relegation — then loaned to Valencia (€3m option), 20 Aug",
  "w": "https://en.wikipedia.org/wiki/Pablo_Maffeo"
 },
 {
  "d": "2026-01",
  "p": "Marc Guéhi",
  "from": "Crystal Palace",
  "to": "Man City",
  "toKey": "man-city",
  "fee": "£20m",
  "type": "transfer",
  "status": "official",
  "note": "January window; back-to-back FA Cups with different clubs",
  "w": "https://en.wikipedia.org/wiki/Marc_Gu%C3%A9hi"
 },
 {
  "d": "2026",
  "p": "Gonçalo Ramos",
  "from": "PSG",
  "to": "AC Milan",
  "fromKey": "psg",
  "fee": "€74m",
  "type": "transfer",
  "status": "official",
  "note": "Milan's club record; Rúben Amorim's first signing",
  "w": "https://en.wikipedia.org/wiki/Gon%C3%A7alo_Ramos"
 },
 {
  "d": "2026",
  "p": "Jérémy Jacquet",
  "from": "Rennes",
  "to": "Liverpool",
  "toKey": "liverpool",
  "fee": "£55m→£60m",
  "type": "transfer",
  "status": "official",
  "note": "Rennes' record sale; chose Anfield over Chelsea",
  "w": "https://en.wikipedia.org/wiki/J%C3%A9r%C3%A9my_Jacquet"
 },
 {
  "d": "2026",
  "p": "Ibrahima Konaté",
  "from": "Liverpool",
  "to": "Real Madrid",
  "fromKey": "liverpool",
  "toKey": "real-madrid",
  "type": "transfer",
  "status": "official",
  "note": "Part of Real's summer haul",
  "w": "https://en.wikipedia.org/wiki/Ibrahima_Konat%C3%A9"
 },
 {
  "d": "2026",
  "p": "Marc Cucurella",
  "from": "Chelsea",
  "to": "Real Madrid",
  "fromKey": "chelsea",
  "toKey": "real-madrid",
  "type": "transfer",
  "status": "official",
  "note": "World Cup team of the tournament at left-back",
  "w": "https://en.wikipedia.org/wiki/Marc_Cucurella"
 },
 {
  "d": "2026",
  "p": "Anthony Gordon",
  "from": "Newcastle",
  "to": "Barcelona",
  "toKey": "barcelona",
  "fee": "€80m",
  "type": "transfer",
  "status": "official",
  "note": "Replaces Lewandowski's goals"
 },
 {
  "d": "2026",
  "p": "Robert Lewandowski",
  "from": "Barcelona",
  "to": "Free agent",
  "fromKey": "barcelona",
  "type": "free",
  "status": "official",
  "note": "Left at the end of his contract"
 },
 {
  "d": "2026",
  "p": "Rasmus Højlund",
  "from": "Man United",
  "to": "Napoli",
  "fromKey": "man-united",
  "toKey": "napoli",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Youri Tielemans",
  "from": "Aston Villa",
  "to": "Man United",
  "fromKey": "aston-villa",
  "toKey": "man-united",
  "type": "transfer",
  "status": "official",
  "note": "Midfield rebuild under Carrick"
 },
 {
  "d": "2026",
  "p": "Andrey Santos",
  "from": "Chelsea",
  "to": "Man United",
  "fromKey": "chelsea",
  "toKey": "man-united",
  "fee": "£48m",
  "type": "transfer",
  "status": "official",
  "note": "After a prolific Strasbourg loan",
  "w": "https://en.wikipedia.org/wiki/Andrey_Santos"
 },
 {
  "d": "2026",
  "p": "Morgan Rogers",
  "from": "Aston Villa",
  "to": "Chelsea",
  "fromKey": "aston-villa",
  "toKey": "chelsea",
  "type": "transfer",
  "status": "official",
  "note": "Chelsea's club-record signing"
 },
 {
  "d": "2026",
  "p": "Jorrel Hato",
  "from": "Ajax",
  "to": "Chelsea",
  "fromKey": "ajax",
  "toKey": "chelsea",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Kenneth Taylor",
  "from": "Ajax",
  "to": "Lazio",
  "fromKey": "ajax",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Sandro Tonali",
  "from": "Newcastle",
  "to": "Tottenham",
  "toKey": "tottenham",
  "type": "transfer",
  "status": "official",
  "note": "Tottenham's club-record signing"
 },
 {
  "d": "2026",
  "p": "Andrew Robertson",
  "from": "Liverpool",
  "to": "Tottenham",
  "fromKey": "liverpool",
  "toKey": "tottenham",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Marcos Senesi",
  "from": "Bournemouth",
  "to": "Tottenham",
  "toKey": "tottenham",
  "type": "free",
  "status": "official",
  "note": "One of De Zerbi's first signings",
  "w": "https://en.wikipedia.org/wiki/Marcos_Senesi"
 },
 {
  "d": "2026",
  "p": "Morten Hjulmand",
  "from": "Sporting CP",
  "to": "Atlético Madrid",
  "fromKey": "sporting",
  "toKey": "atletico-madrid",
  "type": "transfer",
  "status": "official",
  "note": "Sporting's captain"
 },
 {
  "d": "2026",
  "p": "Rodrigo Zalazar",
  "from": "",
  "to": "Sporting CP",
  "toKey": "sporting",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Sergi Altimira",
  "from": "",
  "to": "Sporting CP",
  "toKey": "sporting",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Mason Greenwood",
  "from": "Marseille",
  "to": "Fenerbahçe",
  "fromKey": "marseille",
  "fee": "€40m",
  "type": "transfer",
  "status": "official",
  "note": "OM's top scorer, sold under DNCG restrictions"
 },
 {
  "d": "2026",
  "p": "Loïs Openda",
  "from": "RB Leipzig",
  "to": "Juventus",
  "fromKey": "rb-leipzig",
  "type": "transfer",
  "status": "official",
  "note": "loaned on to Lyon 28 Jul"
 },
 {
  "d": "2026",
  "p": "Zeki Çelik",
  "from": "Roma",
  "to": "Juventus",
  "toKey": "juventus",
  "type": "transfer",
  "status": "official",
  "note": "Signed through 2029",
  "w": "https://en.wikipedia.org/wiki/Zeki_Çelik"
 },
 {
  "d": "2026",
  "p": "Sven Mijnans",
  "from": "AZ",
  "to": "PSV",
  "toKey": "psv",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Antony",
  "from": "Man United",
  "to": "Real Betis",
  "fromKey": "man-united",
  "toKey": "real-betis",
  "type": "transfer",
  "status": "official",
  "note": "Loan made permanent"
 },
 {
  "d": "2026",
  "p": "Jakub Kiwior",
  "from": "Arsenal",
  "to": "Porto",
  "fromKey": "arsenal",
  "toKey": "porto",
  "fee": "€17m",
  "type": "transfer",
  "status": "official",
  "note": "Loan made permanent",
  "w": "https://en.wikipedia.org/wiki/Jakub_Kiwior"
 },
 {
  "d": "2026",
  "p": "Maxime Estève",
  "from": "Burnley",
  "to": "RB Leipzig",
  "toKey": "rb-leipzig",
  "type": "transfer",
  "status": "official",
  "note": "Five-year deal after Burnley's relegation",
  "w": "https://en.wikipedia.org/wiki/Maxime_Estève"
 },
 {
  "d": "2026",
  "p": "Abdoul Koné",
  "from": "Reims",
  "to": "RB Leipzig",
  "toKey": "rb-leipzig",
  "type": "transfer",
  "status": "official",
  "note": "Signed in January and loaned back; joins the squad now",
  "w": "https://en.wikipedia.org/wiki/Abdoul_Koné"
 },
 {
  "d": "2026",
  "p": "Yan Couto",
  "from": "Dortmund",
  "to": "Como",
  "fromKey": "dortmund",
  "type": "loan",
  "status": "official",
  "note": "Season loan to the Serie A newcomers",
  "w": "https://en.wikipedia.org/wiki/Yan_Couto"
 },
 {
  "d": "2026",
  "p": "Lesley Ugochukwu",
  "from": "Burnley",
  "to": "Galatasaray",
  "toKey": "galatasaray",
  "type": "loan",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Jota Silva",
  "from": "Nottingham Forest",
  "to": "Olympiacos",
  "toKey": "olympiacos",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Costinha",
  "from": "Olympiacos",
  "to": "Brighton",
  "fromKey": "olympiacos",
  "fee": "€12.7m",
  "type": "transfer",
  "status": "official"
 },
 {
  "d": "2026",
  "p": "Marco Bizot",
  "from": "",
  "to": "Aston Villa",
  "toKey": "aston-villa",
  "type": "transfer",
  "status": "official",
  "note": "Listed as Villa's No. 1 in the summer squad sweep"
 },
 {
  "d": "2026",
  "p": "Manuel Akanji",
  "from": "Man City",
  "to": "",
  "fromKey": "man-city",
  "type": "transfer",
  "status": "official",
  "note": "Departure applied to the squad; destination not recorded here"
 },
 {
  "d": "2026",
  "p": "Nathan Aké",
  "from": "Man City",
  "to": "",
  "fromKey": "man-city",
  "type": "transfer",
  "status": "official",
  "note": "Departure applied to the squad; destination not recorded here"
 },
 {
  "d": "2026",
  "p": "Leandro Trossard",
  "from": "Arsenal",
  "to": "",
  "fromKey": "arsenal",
  "type": "transfer",
  "status": "official",
  "note": "Departure applied to the squad; destination not recorded here"
 },
 {
  "d": "2026",
  "p": "Raphaël Guerreiro",
  "from": "Bayern",
  "to": "Unattached",
  "fromKey": "bayern",
  "type": "free",
  "status": "official",
  "w": "https://en.wikipedia.org/wiki/Rapha%C3%ABl_Guerreiro"
 },
 {
  "d": "2026",
  "p": "Hidemasa Morita",
  "from": "Sporting CP",
  "to": "Unattached",
  "fromKey": "sporting",
  "type": "free",
  "status": "official",
  "note": "Listed among exits by A Bola/Maisfutebol; not in site squad"
 },
 {
  "d": "2026",
  "p": "Yann Karamoh",
  "from": "Porto",
  "to": "Porto B",
  "fromKey": "porto",
  "type": "transfer",
  "status": "official",
  "note": "Dropped to FC Porto B for 2026-27 (record.pt)"
 },
 {
  "d": "2026",
  "p": "João Afonso",
  "from": "Santa Clara",
  "to": "Porto",
  "toKey": "porto",
  "type": "transfer",
  "status": "official",
  "note": "Per Maisfutebol/A Bola official lists; date/fee unverified; not in site squad"
 },
 {
  "d": "2026",
  "p": "Couhaib Driouech",
  "from": "PSV",
  "to": "Celta Vigo",
  "fromKey": "psv",
  "type": "transfer",
  "status": "official",
  "note": "Per PSV.nl summer overview / FCUpdate; date and fee unverified"
 },
 {
  "d": "2026",
  "p": "Josip Šutalo",
  "from": "Ajax",
  "to": "Lazio",
  "fromKey": "ajax",
  "fee": "€3m loan",
  "type": "loan",
  "status": "official",
  "note": "€3m loan fee, Lazio pay full salary (Ajax Showtime/Voetbalzone); date unverified"
 },
 {
  "d": "2026",
  "p": "Aleksandar Stanković",
  "from": "Inter",
  "to": "Club Brugge",
  "toKey": "club-brugge",
  "type": "transfer",
  "status": "official",
  "note": "Listed among Brugge signings (FotMob/Voetbalbelgie); not in site squad; date unverified"
 },
 {
  "d": "2026",
  "p": "Hervé Koffi",
  "from": "Lens",
  "to": "Union SG",
  "toKey": "union-sg",
  "type": "loan",
  "status": "official",
  "note": "Per AiScore/Transferfeed logs; date unverified; not in site squad"
 },
 {
  "d": "2026",
  "p": "Arne Engels",
  "from": "Celtic",
  "to": "West Ham",
  "fromKey": "celtic",
  "fee": "£22m",
  "type": "transfer",
  "status": "official",
  "note": "£22m, five-year deal (Sports Mole summary); date unverified"
 },
 {
  "d": "2026",
  "p": "Paulo Bernardo",
  "from": "Celtic",
  "to": "Górnik Zabrze",
  "fromKey": "celtic",
  "type": "loan",
  "status": "official",
  "note": "Per Sports Mole summary"
 },
 {
  "d": "2026",
  "p": "Kasper Høgh",
  "from": "",
  "to": "Celtic",
  "toKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Earlier summer signing per Sports Mole/FootballTransfers; not in site squad"
 },
 {
  "d": "2026",
  "p": "Haissem Hassan",
  "from": "",
  "to": "Celtic",
  "toKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Earlier summer signing per Sports Mole; not in site squad"
 },
 {
  "d": "2026",
  "p": "Mika Baur",
  "from": "",
  "to": "Celtic",
  "toKey": "celtic",
  "type": "transfer",
  "status": "official",
  "note": "Earlier summer signing per Sports Mole; not in site squad"
 },
 {
  "d": "2026",
  "p": "Alexander Nübel",
  "from": "Bayern",
  "to": "Beşiktaş",
  "fromKey": "bayern",
  "type": "transfer",
  "status": "official",
  "note": "Listed as completed in fcbinside/Sportschau summer summaries; date not verified; not in site squad"
 },
 {
  "d": "2026",
  "p": "Daniel Peretz",
  "from": "Bayern",
  "to": "Southampton",
  "fromKey": "bayern",
  "type": "transfer",
  "status": "official",
  "note": "Per fcbinside/Sportschau summaries; date not verified; not in site squad"
 },
 {
  "d": "2026",
  "p": "Jonah Kusi-Asare",
  "from": "Bayern",
  "to": "Fulham",
  "fromKey": "bayern",
  "type": "transfer",
  "status": "official",
  "note": "Per fcbinside summary; not in site squad"
 },
 {
  "d": "2026",
  "p": "Noel Aseko",
  "from": "Bayern",
  "to": "Eintracht Frankfurt",
  "fromKey": "bayern",
  "type": "transfer",
  "status": "official",
  "note": "Per fcbinside summary; not in site squad"
 },
 {
  "d": "2026",
  "p": "Mahamadou Diawara",
  "from": "Lyon",
  "to": "Red Star",
  "fromKey": "lyon",
  "type": "loan",
  "status": "official",
  "note": "Season loan with option per OL-focused summaries; date unverified"
 },
 {
  "d": "2026",
  "p": "Facundo Medina",
  "from": "Marseille",
  "to": "Bayer Leverkusen",
  "fromKey": "marseille",
  "fee": "€23m (+€2m)",
  "type": "transfer",
  "status": "official",
  "note": "€23m + €2m per OM recaps (FootballClubDeMarseille, Maxifoot); exact date not verified (mid-August)"
 },
 {
  "d": "2026",
  "p": "Pierre-Emerick Aubameyang",
  "from": "Marseille",
  "to": "Deportivo La Coruña",
  "fromKey": "marseille",
  "fee": "€1.5m",
  "type": "transfer",
  "status": "official",
  "note": "€1.5m per OM recap; not in site squad"
 },
 {
  "d": "2026",
  "p": "Hamed Junior Traoré",
  "from": "Marseille",
  "to": "Genoa",
  "fromKey": "marseille",
  "type": "loan",
  "status": "official",
  "note": "Per OM recap; not in site squad"
 },
 {
  "d": "2026",
  "p": "Ryan Kavuma-McQueen",
  "from": "Chelsea",
  "to": "Portsmouth",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan to the Championship side (chelseafc.com)"
 },
 {
  "d": "2026",
  "p": "Reggie Walsh",
  "from": "Chelsea",
  "to": "Wigan Athletic",
  "fromKey": "chelsea",
  "type": "loan",
  "status": "official",
  "note": "Season-long loan to the League One side (thechelseachronicle.com)"
 },
 {
  "d": "2026",
  "p": "Amourricho van Axel Dongen",
  "from": "Ajax",
  "to": "SC Heerenveen",
  "fromKey": "ajax",
  "type": "transfer",
  "status": "official",
  "note": "Left for Heerenveen after his loan there; terms not established (en.wikipedia.org)"
 },
 {
  "d": "2026",
  "p": "Abdoulaye Camara",
  "from": "Udinese",
  "to": "Ajax",
  "toKey": "ajax",
  "type": "loan",
  "status": "official",
  "note": "17-year-old on season loan with option; reported as a Jong Ajax signing (ajax.nl)"
 }
];

window.TL = {
  esc: function(s){
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  },
  // "2026-08-06" -> "Aug 6" · "2026-07" -> "July" · "2026" -> "summer"
  fmtDate: function(d){
    var M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var FULL = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    var p = (d || '').split('-');
    if(p.length === 3) return M[+p[1]-1] + ' ' + (+p[2]);
    if(p.length === 2) return FULL[+p[1]-1];
    return 'summer';
  },
  // undated summer entries sort between June and January
  sortKey: function(t){ return t.d && t.d.length > 4 ? t.d : t.d + '-05'; },
  sorted: function(list){
    var TL = window.TL;
    return list.slice().sort(function(a, b){
      return TL.sortKey(b) < TL.sortKey(a) ? -1 : TL.sortKey(b) > TL.sortKey(a) ? 1 : 0;
    });
  },
  // In/Out block for a squad modal; uses .squad-depth-label + .tlw-* classes
  windowBlockHTML: function(slug){
    var TL = window.TL, T = window.TRANSFERS || [];
    var ins = TL.sorted(T.filter(function(t){ return t.toKey === slug; }));
    var outs = TL.sorted(T.filter(function(t){ return t.fromKey === slug; }));
    if(!ins.length && !outs.length) return '';
    function row(t, dir){
      var other = dir === 'in' ? t.from : t.to;
      var otherTxt = other ? ((dir === 'in' ? 'from ' : 'to ') + other)
                           : (dir === 'in' ? '' : 'destination not recorded');
      var name = t.w
        ? '<a href="' + TL.esc(t.w) + '" target="_blank" rel="noopener">' + TL.esc(t.p) + '</a>'
        : '<span class="tlw-p">' + TL.esc(t.p) + '</span>';
      var badges = '';
      if(t.status !== 'official') badges += '<span class="tlw-badge live">' + t.status + '</span>';
      if(t.type && t.type !== 'transfer') badges += '<span class="tlw-badge">' + t.type + '</span>';
      var fee = t.fee ? '<span class="tlw-fee">' + TL.esc(t.fee) + '</span>' : '';
      var title = TL.esc((t.note ? t.note + ' · ' : '') + TL.fmtDate(t.d));
      return '<div class="tlw-row" title="' + title + '">' + name
        + '<span class="tlw-club">' + TL.esc(otherTxt) + '</span>' + badges + fee + '</div>';
    }
    var h = '';
    if(ins.length) h += '<div class="squad-depth-label" style="margin-top:16px">Window · In</div>'
      + ins.map(function(t){ return row(t, 'in'); }).join('');
    if(outs.length) h += '<div class="squad-depth-label" style="margin-top:14px">Window · Out</div>'
      + outs.map(function(t){ return row(t, 'out'); }).join('');
    return h;
  },
  // Console-only consistency check: ledger vs the SQUADS object on clubs.html.
  audit: function(SQ){
    function norm(s){
      return (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .toLowerCase().replace(/[^a-z]/g, '');
    }
    function present(key, player){
      var d = SQ[key];
      if(!d) return null;
      var pn = norm(player), last = norm(player.split(' ').slice(-1)[0]);
      var initial = pn.charAt(0);
      return (d.xi || []).concat(d.rest || []).some(function(p){
        var n = norm(p.name);
        // surname match alone is too loose (Pablo García vs Fran García) —
        // the first initial has to agree as well
        return n === pn || (last.length > 3 && n.slice(-last.length) === last && n.charAt(0) === initial);
      });
    }
    var out = [];
    (window.TRANSFERS || []).forEach(function(t){
      if(t.status !== 'official') return;
      if(t.toKey && present(t.toKey, t.p) === false)
        out.push('missing arrival: ' + t.p + ' not found in "' + t.toKey + '"');
      // loaned-out players stay on the parent club's books, so only permanent
      // departures are expected to leave the squad list
      if(t.type !== 'loan' && t.fromKey && present(t.fromKey, t.p) === true)
        out.push('stale departure: ' + t.p + ' still listed in "' + t.fromKey + '"');
    });
    if(out.length) console.warn('[transfer-log audit] ' + out.length + ' mismatch(es)\n' + out.join('\n'));
    else console.info('[transfer-log audit] ledger and squads agree');
    return out;
  }
};
