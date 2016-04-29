from .models import *


def fix_odds(team):
    if team.odds > 0:
        print("before: {0}".format(team.odds))
        team.odds = team.odds * team.games / (team.games - 1)
        print("-after: {0}".format(team.odds))
        team.save()


def find_matches_with_no_odds():
    matches = Match.objects.filter(team1odds=0, team2odds=0)[2:]

    for match in matches:
        print(match.id)
        team1 = match.team1
        fix_odds(team1)
        team2 = match.team2
        fix_odds(team2)
