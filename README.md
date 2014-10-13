Measuring Within-Game Team Volatility
========================

Python 3 code used to measure a basketball team's volatility within each game. We define a team's volatility within a game as the standard deviation of the of point differences at each play (i.e., the standard deviation of point-differences within the game). Volatility within games can be averaged over a series of games to estimate a team's average volatility. 

The script [first](scrape and store game info.py) scrapes NBA play-by-play data from the web and stores that data in a SQLite database. [Second](take data from sqlite and calculate team-variability metrics.py), with this data it calculates several metrics for each game that indicate each team's volatility in that game. Specifically, it provides (1) the standard deviation of point-differences within each game, (2) the the maximum point-difference within each game, and (3) the maiximum number of points each team was behind by in each game. 

Anysis of this data shows...



