# -*- coding: utf-8 -*-
"""
Python code that gets basketball play-by-play (pbp) info previously scraped and 
stored in SQLite database. The code then takes the within-game pbp info and 
calculates several metrics that reflect a team's variability in each game.

Author: Andy Martens
Date: August 29, 2014
"""

# import modules:
import numpy as np
import sqlite3
import pandas as pd
from pandas import *
import matplotlib.pyplot as plt


# List of teams and year in the dataframe:
list_of_teams = ['BOS2014', 'NYK2014', 'BRK2014', 'PHI2014', 'TOR2014', 'MIL2014', 'DET2014', 'CLE2014', 'CHI2014', 
'IND2014', 'MIA2014', 'ATL2014', 'WAS2014', 'CHA2014', 'ORL2014', 'OKC2014', 'DEN2014', 'UTA2014', 'POR2014', 'MIN2014', 
'LAC2014', 'GSW2014', 'LAL2014', 'SAC2014', 'PHO2014', 'SAS2014', 'MEM2014', 'HOU2014', 'DAL2014', 'NOP2014','BOS2013', 
'NYK2013', 'BRK2013', 'PHI2013', 'TOR2013', 'MIL2013', 'DET2013', 'CLE2013', 'CHI2013', 
'IND2013', 'MIA2013', 'ATL2013', 'WAS2013', 'CHA2013', 'ORL2013', 'OKC2013', 'DEN2013', 'UTA2013', 'POR2013', 'MIN2013', 
'LAC2013', 'GSW2013', 'LAL2013', 'SAC2013', 'PHO2013', 'SAS2013', 'MEM2013', 'HOU2013', 'DAL2013', 'NOH2013', 'NYK2012', 
'BOS2012', 'BRK2012', 'PHI2012', 'TOR2012', 'MIL2012', 'DET2012', 'CLE2012', 'CHI2012', 'IND2012', 'MIA2012', 'ATL2012', 
'WAS2012', 'CHA2012', 'ORL2012', 'OKC2012', 'DEN2012', 'UTA2012', 'POR2012', 'MIN2012', 'LAC2012', 'GSW2012', 'LAL2012', 
'SAC2012', 'PHO2012', 'SAS2012', 'MEM2012', 'HOU2012', 'DAL2012', 'NOH2012', 'NYK2011', 'BOS2011', 'BRK2011', 'PHI2011', 
'TOR2011', 'MIL2011', 'DET2011', 'CLE2011', 'CHI2011', 'IND2011', 'MIA2011', 'ATL2011', 'WAS2011', 'CHA2011', 'ORL2011', 
'OKC2011', 'DEN2011', 'UTA2011', 'POR2011', 'MIN2011', 'LAC2011', 'GSW2011', 'LAL2011', 'SAC2011', 'PHO2011', 'SAS2011', 
'MEM2011', 'HOU2011', 'DAL2011', 'NOH2011', 'NYK2010', 'BOS2010', 'NJN2010', 'PHI2010', 'TOR2010', 'MIL2010', 'DET2010', 
'CLE2010', 'CHI2010', 'IND2010', 'MIA2010', 'ATL2010', 'WAS2010', 'CHA2010', 'ORL2010', 'OKC2010', 'DEN2010', 'UTA2010', 
'POR2010', 'MIN2010', 'LAC2010', 'GSW2010', 'LAL2010', 'SAC2010', 'PHO2010', 'SAS2010', 'MEM2010', 'HOU2010', 'DAL2010', 
'NOH2010', 'NYK2009', 'BOS2009', 'NJN2009', 'PHI2009', 'TOR2009', 'MIL2009', 'DET2009', 'CLE2009', 'CHI2009', 'IND2009', 
'MIA2009', 'ATL2009', 'WAS2009', 'CHA2009', 'ORL2009', 'OKC2009', 'DEN2009', 'UTA2009', 'POR2009', 'MIN2009', 'LAC2009', 
'GSW2009', 'LAL2009', 'SAC2009', 'PHO2009', 'SAS2009', 'MEM2009', 'HOU2009', 'DAL2009', 'NOH2009', 'NYK2008', 'BOS2008', 
'NJN2008', 'PHI2008', 'TOR2008', 'MIL2008', 'DET2008', 'CLE2008', 'CHI2008', 'IND2008', 'MIA2008', 'ATL2008', 'WAS2008', 
'CHA2008', 'ORL2008', 'SEA2008', 'DEN2008', 'UTA2008', 'POR2008', 'MIN2008', 'LAC2008', 'GSW2008', 'LAL2008', 'SAC2008', 
'PHO2008', 'SAS2008', 'MEM2008', 'HOU2008', 'DAL2008', 'NOH2008', 'NYK2007', 'BOS2007', 'NJN2007', 'PHI2007', 'TOR2007', 
'MIL2007', 'DET2007', 'CLE2007', 'CHI2007', 'IND2007', 'MIA2007', 'ATL2007', 'WAS2007', 'CHA2007', 'ORL2007', 'SEA2007', 
'DEN2007', 'UTA2007', 'POR2007', 'MIN2007', 'LAC2007', 'GSW2007', 'LAL2007', 'SAC2007', 'PHO2007', 'SAS2007', 'MEM2007', 
'HOU2007', 'DAL2007', 'NOK2007']

#################################################################
# Gets play-by-play data from SQLite and condenses into one line per game
# with 'peak performance' metrics. The code then puts this data into a 
# pandas dataframe (df).


def create_empty_df():
    """Helper funcdtion for pbp_df. Creates an empty dataframe in pandas"""
    con = sqlite3.connect("bball_pbp.db")
    cur = con.cursor()    
    cur.execute('SELECT * FROM CLE2013')
    CLE2013 = cur.fetchall()
    w_diffs = games_w_diffs_list(CLE2013)
    w_max = games_w_max_metric(w_diffs)
    df = DataFrame(w_max)
    return df[:0]


def games_w_max_metric(small_list):
    """Helper function for pbb_df. Takes the list of games that contains a 
    list of the score difference at each play during each game. Computes 
    metrics to assess a peak performance within each game. It selects the 
    maximum score difference during each game, the minium score difference 
    in each game, and several measures of the standard deviation of score 
    differences in each game."""
    small_list2 = small_list[1:]
    last_list = []        
    for line in small_list2:
        diffs_list = line[7]
        # Computes the maximim number of points the team was winning by:
        max_of_g = np.max(diffs_list)
        # Computes the maximum number of points the team was losing by:        
        min_of_g = np.min(diffs_list)
        # Computes the standard deviation of the score differences:
        std_of_g = np.std(diffs_list)
        # Computes the standard deviation of the score differences every 20 plays:        
        std_list = []        
        for i in range(19):
            stdev = np.std(diffs_list[i::20])        
            std_list.append(stdev)
        std20_of_g = np.mean(std_list)
        # Computes the standard deviation of the score differences every 40 plays:        
        std_list = []
        for i in range(39):
            stdev = np.std(diffs_list[i::40])
            std_list.append(stdev)
        std40_of_g = np.mean(std_list)
        # Computes the standard deviation of the score differences every 80 plays:
        std_list = []
        for i in range(79):
            stdev = np.std(diffs_list[i::80])
            std_list.append(stdev)
        std80_of_g = np.mean(std_list)
        game_list = line[:7] + [max_of_g] + [min_of_g] + [std_of_g] + [std20_of_g] + [std40_of_g] + [std80_of_g]
        last_list.append(game_list)
    return last_list
        

def games_w_diffs_list(team_data_from_db):
    """Helper function for pbb_df. Puts the info from SQLite into a list where 
    each line is an individual game and the final element is a list of the 
    score differences for each play in the game."""    
    small_list = []
    diffs_list = []
    basic_info_list = []
    priorline = 0
    data_last_game = team_data_from_db[-1][0]
    team_data_from_db.append((data_last_game + 1, team_data_from_db[-1][1], team_data_from_db[-1][2], 
                              team_data_from_db[-1][3], team_data_from_db[-1][4], team_data_from_db[-1][5], 
                              team_data_from_db[-1][6], team_data_from_db[-1][7], team_data_from_db[-1][8]))
    for line in team_data_from_db: 
        if line[0] > priorline:
            basic_info_list.append(diffs_list)
            small_list.append(basic_info_list)        
            basic_info = line[:7] 
            basic_info_list = list(basic_info)
            diff = line[7] - line[8]
            diffs_list = [diff]   
            priorline = line[0]
        else:
            diff = line[7] - line[8]
            diffs_list.append(diff)
    return small_list


def pbps_from_sql(team):
    """Helper function for pbp_df. Gets play-by-play information from the
    SQLite tabel in which it is stored."""
    con = sqlite3.connect("bball_pbp.db")
    cur = con.cursor()        
    statement = 'SELECT * FROM ' + team
    cur.execute(statement)
    return cur.fetchall()


def pbp_df(list_of_teams):  
    """Produces a pandas dataframe that contains basic info for each game
    along with the maximum number of points that the team was ahead by 
    during each game, the maximum number of points that the team was losing
    by, and metrics calculating the standard deviation of score differences
    within each game."""
    pbp_df = create_empty_df()
    for team in list_of_teams:
        teamdata = pbps_from_sql(team)
        w_diffs_list = games_w_diffs_list(teamdata)
        w_max_metric = games_w_max_metric(w_diffs_list)
        df = DataFrame(w_max_metric)
        pbp_df = concat([df, pbp_df], ignore_index=True)
    pbp_df[1] = to_datetime(pbp_df[1])
    pbp_df.columns = ['game', 'date', 'team', 'oppt', 'home', 'teamscore', 'opptscore', 'max_metric', 'min_metric', 'std_metric', 'std20_metric', 'std40_metric', 'std80_metric']
    return pbp_df


# Main function that returns a pandas dataframe with information about each game,
# including metrics that index each team's peak performance in that game.
final_df = pbp_df(list_of_teams)
