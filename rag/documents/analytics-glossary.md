# Football Analytics Glossary

## xG (Expected Goals)
xG estimates the probability that a given shot results in a goal, based
on factors like shot distance, angle, body part used, and the type of
play that created the chance (open play, header, penalty, and so on).
A player who consistently scores more than their total xG is
outperforming the underlying quality of their chances; a player
scoring below their xG may be finishing poorly or simply unlucky. xG is
a shot-quality measure, not a prediction of any single shot's outcome.

## xA (Expected Assists)
xA estimates the probability that a given pass leads directly to a
goal, based on the quality of the chance it created. It measures
chance creation independently of whether the teammate's shot actually
went in, which is useful for judging a passer's contribution even in a
match where their teammates finished poorly.

## Progressive Passes
A progressive pass is one that moves the ball a significant distance
toward the opponent's goal, typically measured against a threshold
that scales with the pass's starting position on the pitch. It is used
to identify players who reliably advance play through passing, as
opposed to simply maintaining possession sideways or backwards.

## Key Passes
A key pass is the final pass before a teammate takes a shot, regardless
of whether that shot results in a goal. It is a simpler, more common
event than an assist and is often used alongside xA to evaluate chance
creation.

## Per-90 Statistics
Because players accumulate different amounts of playing time, raw
totals (goals, assists, tackles) can be misleading when comparing them.
Per-90 statistics scale a count to a full 90-minute match
(count / minutes_played * 90), making it possible to compare a player
who has played 900 minutes to one who has played 3000 minutes on equal
footing.

## Market Value
In football, "market value" (as popularized by sites like Transfermarkt)
is a crowd- and expert-informed estimate of what a club would
realistically need to pay in transfer fees to sign a player, not a
formal appraisal or a guaranteed transfer price. It moves with form,
age, contract length, and reputation, and it is this figure that
FootballIQ's machine learning model is trained to predict from
performance statistics.
