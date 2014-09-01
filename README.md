Measuring-Team-Potential
========================

Python code that measures a basketball team's peak performance within each game. A team's peak-performance within a game can be averaged over a series of games to provide a reliable estimate of a team's potential/ceiling that may not be captured by examining just the final score of each game. 

The code first scrapes NBA play-by-play data from the web. Then it calculates several metrics for each game that indicate each team's peak performance in that game. Specifically, it provides (1) the the maximum number of points each team was ahead by in each game (i.e., the maximum point-difference within each game). It provides (2) the maiximum number of points each team was behind by in each game. And (3) it provides the standard deviation of point-differences within each game. 
