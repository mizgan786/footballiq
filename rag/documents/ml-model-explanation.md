# How FootballIQ's Prediction Model Works

## Model
FootballIQ's market value predictor is an XGBoost gradient-boosted tree
model, chosen after comparing it against Linear Regression, Ridge
Regression, Random Forest, and Gradient Boosting on a validation set.
XGBoost had the lowest validation error and was selected as the final
model.

## Features
The model uses 26 inputs: age, height, appearances, minutes played,
goals, assists, goals per 90 minutes, assists per 90 minutes, yellow
and red cards, a "club prestige" score (the prior season's average
market value at the player's club), and one-hot-encoded sub-position,
preferred foot, and league.

## Training
The model is trained on log-transformed market values (because market
value is heavily right-skewed - many modestly valued players and a
long tail of superstars), using a time-aware split: seasons 2012-2020
for training, 2021-2022 for validation and model selection, and
2023-2025 held out entirely as a final test set the model was never
tuned against.

## Performance
On the held-out test set, the model achieves an R² of roughly 0.73
(meaning it explains about 73% of the variance in market value) and a
mean absolute error of a few million euros. It performs best in the
middle of the value distribution and tends to underestimate the very
highest-valued superstars (150M EUR and above), since there are very
few such players to learn from and their valuations often reflect
"generational talent" premiums that plain statistics can't fully
capture.

## What "Prediction Difference" Means
When FootballIQ shows a difference between a player's actual market
value and the model's prediction, that is not a claim that the player
is objectively overpriced or underpriced - it means the model's
estimate, based only on the statistical inputs above, differs from
the market's actual valuation. Real market value also reflects things
the model doesn't see: reputation, potential, injury history, contract
situation, and transfer market conditions.
