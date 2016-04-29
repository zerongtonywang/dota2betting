from bs4 import BeautifulSoup as bs
import requests, re

from .models import *

URL = "http://dota2lounge.com/"


def get_int_from_str(string, index=0):
    numbers = re.findall("\d+", string)
    try:
        number = numbers[index]
    except IndexError:
        number = None
    return number


def get_bestof(box_dom):
    bestof_str = box_dom.find("div").find_all("div")[1].text
    bestof = get_int_from_str(bestof_str)
    return bestof


def get_finished(box_dom):
    return "(win)" in box_dom.text


def save_team(team_name, win, team_odds, process=False):
    team, _ = Team.objects.get_or_create(name=team_name)
    team.games += 1
    if win:
        team.wins += 1
    if process:
        team.winrate = team.wins / team.games
        if team_odds != 0:
            team.odds = (team.odds * (team.games - 1) + team_odds) / team.games
    elif team_odds != 0:
        team.odds += team_odds
    team.save()
    return team


def get_teams(box_dom):
    teams_dom = box_dom.find_all("div", class_="team")
    match_teams = []
    match_winner = None
    for i in range(2):
        team_dom = teams_dom[i]
        team_name = team_dom.parent.b.text
        team_odds = int(team_dom.parent.i.text.strip("%")) / 100

        if " (win)" in team_name:
            team_name = team_name[:-6]
            win = True
            match_winner = i
        else:
            win = False

        team = save_team(team_name, win, team_odds, process=True)
        match_teams.append((team, team_odds))

    return match_teams[0][0], match_teams[0][1], match_teams[1][0], match_teams[1][1], match_teams[match_winner][0]


def scrape(request_match_id):
    site = requests.get("{0}match?m={1}".format(URL, request_match_id))
    soup = bs(site.text, "lxml")
    if "Match" in soup.title.text:
        match_id = get_int_from_str(soup.title.text, index=-1)
        print(match_id)
    else:
        print("bad request")
        return None
    box_dom = soup.find(id="mf")
    if not box_dom:
        box_dom = soup.find("section", class_="box")
    if not box_dom:
        print("cant find box")
        return None

    finished = get_finished(box_dom)
    if not finished:
        print("Match has no winners")
    elif len(Match.objects.filter(id=match_id)) > 0:
        print("Match already exists")
    else:
        bestof = get_bestof(box_dom)
        team1, team1_odds, team2, team2_odds, winner = get_teams(box_dom)
        if not winner:
            print("this match has no winner")
        match = Match()
        match.id = match_id
        if bestof:
            match.bestof = bestof
        match.finished = finished
        match.team1 = team1
        match.team1odds = team1_odds
        match.team2 = team2
        match.team2odds = team2_odds
        match.winner = winner
        match.save()
        return "{0} - Complete".format(match_id)
    return None


def scrapebulk(head, tail):
    for i in range(head, tail):
        print(i)
        if len(Match.objects.filter(id=i)) == 0:
            scrape(i)
