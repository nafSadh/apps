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
  "toKey": "olympiacos",
  "fee": "€3m",
  "type": "transfer",
  "status": "official",
  "note": "After Mallorca's relegation",
  "w": "https://en.wikipedia.org/wiki/Pablo_Maffeo"
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
  "toKey": "juventus",
  "type": "transfer",
  "status": "official"
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
  "p": "Ugochukwu",
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
  "p": "Leon Goretzka",
  "from": "Bayern",
  "to": "",
  "fromKey": "bayern",
  "type": "transfer",
  "status": "official",
  "note": "Departure applied to the squad; destination not recorded here"
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
  "d": "2026-08-20",
  "p": "Ezri Konsa",
  "from": "Aston Villa",
  "to": "Arsenal",
  "fromKey": "aston-villa",
  "toKey": "arsenal",
  "fee": "£50m+",
  "type": "transfer",
  "status": "agreed",
  "note": "Deal agreed, medical to follow — cover for the injured Saliba (BBC, Transfermarkt)"
 },
 {
  "d": "2026-08-20",
  "p": "Curtis Jones",
  "from": "Liverpool",
  "to": "Inter",
  "fromKey": "liverpool",
  "toKey": "inter",
  "fee": "£30m",
  "type": "transfer",
  "status": "agreed",
  "note": "Fee agreed between the clubs, not yet announced (Sky, Transfermarkt, FourFourTwo)"
 },
 {
  "d": "2026-08-20",
  "p": "Savinho",
  "from": "Man City",
  "to": "Tottenham",
  "fromKey": "man-city",
  "toKey": "tottenham",
  "type": "transfer",
  "status": "reported",
  "note": "Clubs in talks (Sky, BBC)",
  "w": "https://en.wikipedia.org/wiki/Savinho"
 },
 {
  "d": "2026-08-20",
  "p": "Omar Marmoush",
  "from": "Man City",
  "to": "Tottenham",
  "fromKey": "man-city",
  "toKey": "tottenham",
  "type": "transfer",
  "status": "reported",
  "note": "Clubs in talks (Sky, BBC)"
 },
 {
  "d": "2026-08-20",
  "p": "Adam Wharton",
  "from": "Crystal Palace",
  "to": "Liverpool",
  "toKey": "liverpool",
  "type": "transfer",
  "status": "reported",
  "note": "Transfermarkt lists Liverpool interest; Sky says Palace expect him to stay"
 },
 {
  "d": "2026-08-19",
  "p": "Carlos Baleba",
  "from": "Brighton",
  "to": "Man United",
  "toKey": "man-united",
  "type": "transfer",
  "status": "reported",
  "note": "Move said to be close; Brighton's CEO has discussed it (Sky, Transfermarkt)"
 },
 {
  "d": "2026-08-19",
  "p": "Tijjani Reijnders",
  "from": "Man City",
  "to": "Saudi Pro League",
  "fromKey": "man-city",
  "type": "transfer",
  "status": "reported",
  "note": "Transfermarkt reports it complete; no second source — still listed in City's XI here",
  "w": "https://en.wikipedia.org/wiki/Tijjani_Reijnders"
 },
 {
  "d": "2026-08-19",
  "p": "Julián Alvarez",
  "from": "Atlético Madrid",
  "to": "Real Madrid",
  "fromKey": "atletico-madrid",
  "toKey": "real-madrid",
  "type": "transfer",
  "status": "reported",
  "note": "Pushing to leave after Atlético rejected a €150m Real bid (Transfermarkt)",
  "w": "https://en.wikipedia.org/wiki/Julián_Alvarez"
 },
 {
  "d": "2026-08-20",
  "p": "Harry Kane",
  "from": "Bayern",
  "to": "Al-Hilal",
  "fromKey": "bayern",
  "type": "transfer",
  "status": "reported",
  "note": "Al-Hilal interest (BBC gossip, Transfermarkt)",
  "w": "https://en.wikipedia.org/wiki/Harry_Kane"
 },
 {
  "d": "2026-08-20",
  "p": "Viktor Gyökeres",
  "from": "Arsenal",
  "to": "",
  "fromKey": "arsenal",
  "type": "transfer",
  "status": "reported",
  "note": "Said to want out, with daily exit talks (FourFourTwo)",
  "w": "https://en.wikipedia.org/wiki/Viktor_Gy%C3%B6keres"
 },
 {
  "d": "2026-08-20",
  "p": "Guglielmo Vicario",
  "from": "Tottenham",
  "to": "Serie A",
  "fromKey": "tottenham",
  "type": "transfer",
  "status": "reported",
  "note": "Inter, Juventus and Napoli interest; open to a return",
  "w": "https://en.wikipedia.org/wiki/Guglielmo_Vicario"
 },
 {
  "d": "2026-08-13",
  "p": "Rodri",
  "from": "Man City",
  "to": "Barcelona",
  "fromKey": "man-city",
  "toKey": "barcelona",
  "type": "transfer",
  "status": "reported",
  "note": "City rejected a fresh Barcelona bid (BBC gossip)",
  "w": "https://en.wikipedia.org/wiki/Rodri_(footballer%2C_born_1996)"
 },
 {
  "d": "2026-08-13",
  "p": "Djed Spence",
  "from": "Tottenham",
  "to": "Inter",
  "fromKey": "tottenham",
  "toKey": "inter",
  "type": "transfer",
  "status": "reported",
  "note": "On the verge, per BBC gossip"
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
      return (d.xi || []).concat(d.rest || []).some(function(p){
        var n = norm(p.name);
        return n === pn || (last.length > 3 && n.slice(-last.length) === last);
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
