# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 12:24:07 2014
This works. Takes about 2 min to get all the info for one team from one season.
@author: andymartens
"""

# ISSUES: home_away isn't working -- must be finding '@' sign no matter what?
# and probably related, when teams are away, it's assigning oppt pbp scores
# to the team, and team pbp scores to the oppt.
# so if can fix the home_away function, should fix the other probably automatically?

# Runs this for one team in one season in under 3 min. 
# So 1 season would take about 1.5 hours. 
# Maybe break up into 10 teams at a time? or screw it, just do a whole season.




import urllib.request   
from bs4 import BeautifulSoup
import numpy
import sqlite3

##go to schedule and results of boston celtics
#urlBoston = "http://www.basketball-reference.com/teams/BOS/2013_games.html"
#contents = urllib.request.urlopen(urlBoston)
#html_contents = contents.read()
#soup_object = BeautifulSoup(html_contents)
#contents.close()
###tags = soup_object.tbody.find_all("a", text = "Box Score")
#tags = soup_object.tbody.find_all("tr", class_="")
##tags_for_score = soup_object.tbody.find_all("tr", class_="")

#or should i get all info for that game into one string as part
#of a list and then loop through list and divide each part up
#into different components of the game class object?
#can use the rfind method to do this, split method, etc.
#e.g., for tag in tags, game = ...
#i should make the st dev metrics attributes of the class
#so for each game, the st dev metrics are computed and there
#then save all the games to sql


class Game(object):
    def __init__(self, date, team, opponent, home_away, team_score, opponent_score, pbp_scores_list):
        self.date = date
        self.team = team
        self.opponent = opponent
        self.home_away = home_away
        self.team_score = team_score
        self.opponent_score = opponent_score
        self.pbp_scores_list = pbp_scores_list
        
    def __str__(self):
        return "{}, {}, {}".format(self.date, self.team, self.opponent)


def date_of_game(tag):
    """Helper function for game_obj_list. Returns the date of game."""
    tag_str = str(tag)    
    start_location = tag_str.rfind("csk=") + 8
    end_location = start_location + 10
    return tag_str[start_location:end_location]  

# Not in use at the moment, but consider using in the game_obj_list function.
#def team(tag):
#    return sched_and_scores_url[42:45]


def opponent(tag):
    """Helper function for game_obj_list. Returns the opponent."""
    tag_str = str(tag)    
    start_location = tag_str.rfind("/teams/") + 7
    end_location = start_location + 3
    return tag_str[start_location:end_location]


def home_or_away(tag):
    """Helper function for game_obj_list. Returns whether the team was home or away."""
    if "@" in str(tag):
        return "away"
    else:
        return "home"


def team_score(tag):
    """Helper function for game_obj_list. Returns total points scored by the team."""    
    tag_list = list(tag)
    team_score_element = tag_list[15]
    team_score_string = str(team_score_element)
    start_location = team_score_string.rfind('"right" >') + 19
    end_location = team_score_string.rfind("</td")
    team_score = team_score_string[start_location:end_location]
    return int(team_score)


def opponent_score(tag):
    """Helper function for game_obj_list. Returns total points scored by the opponent."""    
    tag_list = list(tag)
    opponent_score_element = tag_list[17]
    opponent_score_string = str(opponent_score_element)
    start_location = opponent_score_string.rfind('"right" >') + 19
    end_location = opponent_score_string.rfind("</td")
    opponent_score = opponent_score_string[start_location:end_location]
    return int(opponent_score)


# The following functions are helper functions for the list_of_pbp_scores function
def get_list_of_scores(pbp_tags):
    """Helper function for list_of_pbp_scores in one game. 
    Returns list of pbp scores in the game."""    
    scores = []
    for tag in pbp_tags:
        tag_string = tag.string        
        scores.append(tag_string)
    return scores


def get_pbp_link(tag):    
    """Helper function for list_of_pbp_scores in one game. 
    Returns pbp link for the game."""        
    tag_str = str(tag)    
    start_location = tag_str.rfind("/boxscores/") + 11
    end_location = tag_str.rfind(">Box Score<") - 1
    link_unique = tag_str[start_location:end_location] 
    link_base = "http://www.basketball-reference.com/boxscores/pbp/"   
    return link_base + link_unique
    
    
def list_of_pbp_scores(tag): 
    """Returns list of pbp scores in the game."""    
    pbp_link = get_pbp_link(tag)    
    on_webpage = urllib.request.urlopen(pbp_link)
    html_doc = on_webpage.read()
    soup = BeautifulSoup(html_doc)
    on_webpage.close()    
    pbp_tags = soup.find_all("td", class_="align_center background_white")
    #Above returns a list of all the tags with the pbp scores in them.    
    return get_list_of_scores(pbp_tags)
    


def game_obj_list(tags, sched_and_scores_url):
    """Returns the list of game objects, i.e., one object for each game
    that contains the game info and a list of the pbp scores"""    
    game_list = []
    for tag in tags:
        the_date = date_of_game(tag)
        the_opponent = opponent(tag)
        home_away = home_or_away(tag)
        the_team_score = team_score(tag)
        the_opponent_score = opponent_score(tag)
        the_team_string = str(sched_and_scores_url)
        the_team = the_team_string[42:45]
        the_list_of_pbp_scores = list_of_pbp_scores(tag)
        game = Game(the_date, the_team, the_opponent, home_away, the_team_score, the_opponent_score, the_list_of_pbp_scores)
        game_list.append(game)
    return game_list


def tags_from_schedule(sched_and_scores_url):
    contents = urllib.request.urlopen(sched_and_scores_url)
    html_contents = contents.read()
    soup_object = BeautifulSoup(html_contents)
    contents.close() 
    return soup_object.tbody.find_all("tr", class_="")
    

#this creates the data to store in sqlite, i.e., each line is a play withe new score
def pbp_list_for_sql(games):
    """Takes the game objects list and returns many new lists for each game object, 
    each new list containing a within-game score with accompanying game info. 
    Use this to insert into sqlite, so each row will represent a moment within one game."""
    list_pbps = []  
    game_number = 0
    for game in games:
        game_number = game_number + 1
        list_pbp_strings = game.pbp_scores_list        
        for pbp_string in list_pbp_strings:  
            two_scores = pbp_string.split("-") 
            if game.home_away == 'away':               
                info_for_play = [game_number] + [game.date] + [game.team] + [game.opponent] + [game.home_away] + [game.team_score] + [game.opponent_score] + [int(two_scores[0])] + [int(two_scores[1])]
                list_pbps.append(info_for_play)
            else:
                info_for_play = [game_number] + [game.date] + [game.team] + [game.opponent] + [game.home_away] + [game.team_score] + [game.opponent_score] + [int(two_scores[1])] + [int(two_scores[0])]
                list_pbps.append(info_for_play)
    return list_pbps


# MAIN FUNCTION    
def scrape_pbp_lists(sched_and_scores_url):
    """Takes a team's schedule and scores url. 
    Stores all the info in sqlite table."""
    tags = tags_from_schedule(sched_and_scores_url)
    game_objects_list = game_obj_list(tags, sched_and_scores_url)
    return pbp_list_for_sql(game_objects_list)   
    

# CALL THE FUNCTION AND ASSIGN TO A VARIABLE:
#game_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/BOS/2013_games.html")


# MASTER FUNCTION TO BOTH SCRAPE AND STORE:
def scrape_and_store_pbps(sched_and_scores_url, team, year):   
    game_pbp_lists_for_sql = scrape_pbp_lists(sched_and_scores_url)    
    con = sqlite3.connect("bball_pbp.db")
    cur = con.cursor()
    table_name = team + str(year)
    table_syntax = "CREATE TABLE " + table_name + '''(game INTEGER, date TEXT, 
    team TEXT, opponent TEXT, home_away TEXT, team_tot_score INTEGER, 
    opponent_tot_score INTEGER, team_pbp_score INTEGER, opponent_pbp_score INTEGER)'''
    cur.execute(table_syntax)
    for line in game_pbp_lists_for_sql:
        insert_syntax = "INSERT INTO " + table_name + " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(insert_syntax, line) 
    con.commit()


# Call the function to scrape and store one team:
#scrape_and_store_pbps("http://www.basketball-reference.com/teams/BOS/2013_games.html", "BOS")


def loop_through_teams(list_of_teams, year):
    for team in list_of_teams:
        sched_and_scores_url = "http://www.basketball-reference.com/teams/" + team + "/" + str(year) + "_games.html"
        scrape_and_store_pbps(sched_and_scores_url, team, year)


# Call the function to scrape and store multiple teams in one year:
#teams = ['DEN', 'UTA', 'POR', 'MIN', 'LAC', 'GSW', 'LAL', 'SAC', 'PHO', 'SAS', 'MEM', 'HOU', 'DAL', 'NOK']

# Full list of teams:
teams = ['NYK', 'BOS', 'BRK', 'PHI', 'TOR', 'MIL', 'DET', 'CLE', 'CHI', 'IND', 'MIA', 'ATL', 'WAS', 'CHA', 'ORL', 'OKC', 'DEN', 'UTA', 'POR', 'MIN', 'LAC', 'GSW', 'LAL', 'SAC', 'PHO', 'SAS', 'MEM', 'HOU', 'DAL', 'NOH']
teams = ['NOP']

loop_through_teams(teams, 2014)



#to close connection to sqlite3:
#con.close()

#to see list of the tables in the database:
#con = sqlite3.connect("bball_pbp.db")
#cur = con.cursor()
#cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
#cur.fetchall()

#cur.execute('SELECT * FROM NOH2009')
#cur.fetchall()
#cur.fetchone()

# Try retrieving and storingin sqlite in one go.
#DONE#BOS2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/BOS/2013_games.html")
#DONE#NYK2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/NYK/2013_games.html")
#DONE#BRK2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/BRK/2013_games.html")
#PHI2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/PHI/2013_games.html")
#TOR2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/TOR/2013_games.html")
#MIL2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/MIL/2013_games.html")
#DET2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/DET/2013_games.html")
#CLE2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/CLE/2013_games.html")
#CHI2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/CHI/2013_games.html")
#IND2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/IND/2013_games.html")
#MIA2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/MIA/2013_games.html")
#ATL2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/ATL/2013_games.html")
#WAS2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/WAS/2013_games.html")
#CHA2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/CHA/2013_games.html")
#ORL2013_pbp_lists_for_sql = scrape_pbp_lists("http://www.basketball-reference.com/teams/ORL/2013_games.html")

#teams = [NYK, BOS, BRK, PHI, TOR, MIL, DET, CLE, CHI, IND, MIA, ATL, WAS, CHA, ORL]

##THEN RUN THIS FUNCTION TO STORE IN SQLITE.
#def store_pbp_lists(game_pbp_lists_for_sql):
#   # Connects to test_bball3 database or creates it if doesn't exist. 
#    con = sqlite3.connect("test_bball3.db")
#    cur = con.cursor()
#    cur.execute('''CREATE TABLE pbp_scores_scraped(game INTEGER, date TEXT, 
#    team TEXT, opponent TEXT, home_away TEXT, team_tot_score INTEGER, 
#    opponent_tot_score INTEGER, team_pbp_score INTEGER, opponent_pbp_score INTEGER)''')
#    for line in game_pbp_lists_for_sql:
#        cur.execute("INSERT INTO pbp_scores_scraped VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", line) 
#    con.commit()
#
#
#store_pbp_lists(game_pbp_lists_for_sql)
#
#
#cur.execute('SELECT * FROM BOS')
#cur.fetchall()
#cur.fetchone()



      
        
        
        