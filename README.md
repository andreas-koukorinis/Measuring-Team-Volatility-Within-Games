Measuring-Team-Potential
========================

Python 3 code used to measure a basketball team's peak performance within each game. We define a team's peak performance within a game as the maxium number of points that team was ahead by during each game (i.e., the maximum point-difference within each game). A team's peak performance within a game can be averaged over a series of games to provide an estimate of a team's current potential beyond what is captured by examining final score of each game. 

The script first scrapes NBA play-by-play data from the web and stores that data in a SQLite database. With this data, it calculates several metrics for each game that indicate each team's peak performance in that game. Specifically, it provides (1) the the maximum point-difference within each game, (2) the maiximum number of points each team was behind by in each game, and (3) the standard deviation of point-differences within each game. 
