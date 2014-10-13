Measuring Within-Game Team Volatility
========================

This Python 3 code measures a basketball team's volatility within games. Some teams have more hot and cold streaks—more ups and downs—within each game. Other teams are more consistent from play to play. I indexed this team volatility within a game by computing the standard deviation of the of point differences at each play (as well as with other alternative metrics). 

The script [first](scrape and store game info.py) scrapes NBA play-by-play data from the web and stores that data in a SQLite database. [Second](take data from sqlite and calculate team-variability metrics.py), with this data it calculates several metrics for each game that indicate each team's volatility in that game. Specifically, it provides (1) the standard deviation of point-differences within each game, (2) the maximum point-difference within each game, and (3) the maximum number of points each team was behind by in each game. 

Using these data I examined whether a team’s tendency towards volatility within games helps to predict their future performance. By itself, volatility did little to predict how well teams will perform. Rather, the ability of volatility to predict future performance depended on whether a team’s opponent was worse or better than them. In games against a better opponent, more volatile teams perform better than less volatile teams. In games against a worse opponent, more volatile teams perform worse than less volatile teams. Stated differently, volatility appears to provide a benefit to teams when playing superior opponents but has a negative impact when playing inferior opponents. 

The graph below depicts this pattern. 




