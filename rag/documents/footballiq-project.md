# About FootballIQ

FootballIQ is a full-stack football analytics application that predicts
a player's market value from their season performance statistics, and
lets users search, compare, and explore players across Europe's top
five leagues.

## Dataset
The underlying data comes from a Transfermarkt-derived dataset covering
the Premier League, La Liga, Bundesliga, Serie A, and Ligue 1 from the
2012 season through 2025. It is organized as a player-season panel:
one row per player per season, built by aggregating that player's
domestic-league match appearances (goals, assists, minutes, cards) and
attaching the market valuation closest to that season's end date.

## Known Limitations
- The dataset includes goals, assists, minutes, appearances, and cards,
  but does not include passing, defensive actions (tackles,
  interceptions), or expected-goals data. This means the prediction
  model has less signal for defenders and defensive midfielders, whose
  value often depends heavily on statistics this dataset doesn't
  capture.
- Only domestic league matches are included - European competition and
  cup performances are not part of a player's statistics here.
- Market value itself is an estimate (see the analytics glossary), not
  a guaranteed transfer fee, so the model is predicting an estimate of
  an estimate.

## Why Club and League Matter
Two players with identical statistics can have very different market
values depending on their club's prestige and which league they play
in - a solid season at a wealthy, high-profile club in a rich league is
valued differently than the same statistical season at a smaller club.
FootballIQ's model accounts for this using two engineered features:
the player's league, and a "club prestige" score derived from the
average value of that club's squad in the prior season.
