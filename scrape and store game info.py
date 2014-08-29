"""
Scrapes basketball play-by-play information and stores it in SQLite.
Author: Andyn Martens
Date: August 29, 2014
"""

# Import modules:
import urllib.request   
from bs4 import BeautifulSoup
import numpy
import sqlite3


class Game(object):
    ''' Object that stores information about a basketball game'''
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


def get_list_of_scores(pbp_tags):
    """Helper function for list_of_pbp_scores in one game. 
    Returns list of play-by-play scores in the game."""    
    scores = []
    for tag in pbp_tags:
        tag_string = tag.string        
        scores.append(tag_string)
    return scores


def get_pbp_link(tag):    
    """Helper function for list_of_pbp_scores in one game. 
    Returns play-by-play link for the game."""        
    tag_str = str(tag)    
    start_location = tag_str.rfind("/boxscores/") + 11
    end_location = tag_str.rfind(">Box Score<") - 1
    link_unique = tag_str[start_location:end_location] 
    link_base = "http://www.basketball-reference.com/boxscores/pbp/"   
    return link_base + link_unique
    
    
def list_of_pbp_scores(tag): 
    """Returns list of play-by-play scores in the game."""    
    pbp_link = get_pbp_link(tag)    
    on_webpage = urllib.request.urlopen(pbp_link)
    html_doc = on_webpage.read()
    soup = BeautifulSoup(html_doc)
    on_webpage.close()    
    pbp_tags = soup.find_all("td", class_="align_center background_white")
    #Above returns a list of all the tags with the pbp scores in them.    
    return get_list_of_scores(pbp_tags)
    

def game_obj_list(tags, sched_and_scores_url):
    """Returns list of game objects; i.e., returns one object for each 
    game (that contains basic game info and a list of the play-by-play scores"""    
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
    """Helper function for scrape_pbp_lists. 
    Returns tags from webpages that contain play-by-play information"""
    contents = urllib.request.urlopen(sched_and_scores_url)
    html_contents = contents.read()
    soup_object = BeautifulSoup(html_contents)
    contents.close() 
    return soup_object.tbody.find_all("tr", class_="")
    

def pbp_list_for_sql(games):
    """Helper function for scrape_pbp_lists. Takes the list of game objects and 
    returns many new lists for each game object. Each new list contains a 
    within-game score with accompanying game info. Use this to insert into 
    SQLite, so each row will represent a moment/play within one game."""
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

  
def scrape_pbp_lists(sched_and_scores_url):
    """Takes a team's schedule and scores url and scrapes play-by-play scores
    so that they can then be stored in SQLite table"""
    tags = tags_from_schedule(sched_and_scores_url)
    game_objects_list = game_obj_list(tags, sched_and_scores_url)
    return pbp_list_for_sql(game_objects_list)   
    

def scrape_and_store_pbps(sched_and_scores_url, team, year): 
    """Scrapes and stores the play-by-play scores for each game in SQLite table"""
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


def loop_through_teams(list_of_teams, year):
    """Loops through teams in a given year and scrapes and stores play-by-play scores"""
    for team in list_of_teams:
        sched_and_scores_url = "http://www.basketball-reference.com/teams/" + team + "/" + str(year) + "_games.html"
        scrape_and_store_pbps(sched_and_scores_url, team, year)


"""List of teams to use as parameter in the loop_through_teams function. 
Note, this list will differ from year to year, depending on changes"""
teams = ['NYK', 'BOS', 'BRK', 'PHI', 'TOR', 'MIL', 'DET', 'CLE', 'CHI', 'IND', 'MIA', 'ATL', 'WAS', 'CHA', 'ORL', 'OKC', 'DEN', 'UTA', 'POR', 'MIN', 'LAC', 'GSW', 'LAL', 'SAC', 'PHO', 'SAS', 'MEM', 'HOU', 'DAL', 'NOH']


"""Loops through all the teams in the 2014 season and stores all the
play-by-play scores in SQLite"""
loop_through_teams(teams, 2014)


#cur.execute('SELECT * FROM BOS')
#cur.fetchone()



      
        
        
        