from .models import *
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


def get_q_names(names):
    q = Q()
    if names:
        for name in names:
            q.add(Q(team1__name=name), conn_type="OR")
            q.add(Q(team2__name=name), conn_type="OR")
    return q


def get_q_days(delta_days, delta_begin):
    delta = timedelta(days=delta_days)
    cutoff_date = delta_begin - delta
    q = Q(when__range=[cutoff_date, delta_begin])
    return q


def matches_filter(names=None, lastgames=99999, delta_days=60, delta_begin=timezone.now()):
    q_names = get_q_names(names)
    q_days = get_q_days(delta_days, delta_begin)
    q = (Q(q_names) & Q(q_days) & Q(valid=True))
    matches = Match.objects.filter(q).order_by("-id")[:lastgames]
    return matches


def save_teamstat(statset, team, win, team_odds):
    teamstat, _ = Teamstat.objects.get_or_create(statset=statset, team=team)
    teamstat.games += 1
    if win:
        teamstat.wins += 1
    teamstat.odds += team_odds
    teamstat.save()
    return teamstat


def add_statset(title, delta_days, delta_begin=timezone.now(), names=None, lastgames=99999):
    if names:
        names_list = names.split(",")
    else:
        names_list = []
    matches = matches_filter(names_list, lastgames, delta_days, delta_begin)
    print("{0} matches gathered".format(len(matches)))

    try:
        statset = StatSet.objects.get(title=title)
        statset.delete()
    except StatSet.DoesNotExist:
        pass
    statset = StatSet(title=title)
    statset.names = names
    statset.lastgames = lastgames
    statset.delta_days = delta_days
    statset.delta_begin = delta_begin
    statset.save()

    print("Statset created: {0}".format(statset.title))
    for match in matches:
        if match.team1.name in names_list or names_list == []:
            save_teamstat(statset, match.team1, match.team1 == match.winner, match.team1odds)
        if match.team2.name in names_list or names_list == []:
            save_teamstat(statset, match.team2, match.team2 == match.winner, match.team2odds)

    teamstats = Teamstat.objects.filter(statset=statset)
    print("{0} teamstats prepared for {1}".format(len(teamstats), statset.title))
    for teamstat in teamstats:
        teamstat.winrate = teamstat.wins / teamstat.games
        teamstat.odds = teamstat.odds / teamstat.games
        teamstat.delta = teamstat.winrate - teamstat.odds
        teamstat.save()

    print("{0} teamstats processed".format(len(teamstats)))
    return statset
