from .models import *
from .query import *
from django.utils import timezone
from datetime import timedelta


def get_outcome(team, match, outcome, cash):
    if match.winner == team:
        if team == match.team1:
            outcome += cash / match.team1odds - cash
        elif team == match.team2:
            outcome += cash / match.team2odds - cash
    else:
        outcome -= cash
    return outcome


def bet_on_winrate(team1stat, team2stat, match, outcome, cash):
    # bet on team1
    if team1stat.winrate > team2stat.winrate:
        outcome = get_outcome(match.team1, match, outcome, cash)
    # bet on team2
    elif team1stat.winrate < team2stat.winrate:
        outcome = get_outcome(match.team2, match, outcome, cash)
    return outcome


def bet_on_odds(team1stat, team2stat, match, outcome, cash, factor_cutoff):
    # bet on team1
    if team1stat.winrate > team2stat.winrate and match.team1odds - match.team2odds >= factor_cutoff:
        outcome = get_outcome(match.team1, match, outcome, cash)
    # bet on team2
    elif team1stat.winrate < team2stat.winrate and match.team2odds - match.team1odds >= factor_cutoff:
        outcome = get_outcome(match.team2, match, outcome, cash)
    return outcome


def bet_dynamically(team1stat, team2stat, match, outcome, cash, factor_cutoff):
    # bet on team1
    if team1stat.winrate > team2stat.winrate:
        delta_odds = match.team1odds - match.team2odds
        if delta_odds >= 0:
            bet_factor = 1 - delta_odds
            cash *= bet_factor
            outcome = get_outcome(match.team1, match, outcome, cash)
    # bet on team2
    elif team1stat.winrate < team2stat.winrate:
        delta_odds = match.team2odds - match.team1odds
        if delta_odds >= 0:
            bet_factor = 1 - delta_odds
            cash *= bet_factor
            outcome = get_outcome(match.team1, match, outcome, cash)
    return outcome


# bet on matches using learned teamstats, with cash
def bet(matches, statset, cash=100, factor_cutoff=0):
    outcome1 = 0
    outcome2 = 0
    outcome3 = 0
    for match in matches:
        try:
            team1stat = Teamstat.objects.get(statset=statset, team=match.team1)
            team2stat = Teamstat.objects.get(statset=statset, team=match.team2)
        except Teamstat.DoesNotExist:
            continue

        outcome1 = bet_on_winrate(team1stat, team2stat, match, outcome1, cash)
        outcome2 = bet_on_odds(team1stat, team2stat, match, outcome2, cash, factor_cutoff)
        outcome3 = bet_dynamically(team1stat, team2stat, match, outcome3, cash, factor_cutoff)
    return outcome1, outcome2, outcome3


# Simulate betting with {cash} dollars using data from past {delta_days} days, validate using data from {test_days} days
def simulate(learn_days, test_days, days_offset=0, cash=100, factor_cutoff=0):
    offset_begin = timezone.now() - timedelta(days=days_offset)
    matches = matches_filter(delta_days=test_days, delta_begin=offset_begin)

    title = "learn:{0} test:{1} offset:{2}".format(learn_days, test_days, days_offset)
    delta_begin = offset_begin - timedelta(days=test_days)
    try:
        statset = StatSet.objects.get(title=title)
    except StatSet.DoesNotExist:
        statset = add_statset(title=title, delta_days=learn_days, delta_begin=delta_begin)

    outcomes = bet(matches, statset, cash, factor_cutoff)
    print("{0} - {1}".format(title, outcomes))
    return outcomes


def bulk_simulate(learn_days, test_days, days_offset=0, cash=100, factor_cutoff=0, bulk=360):
    totals = [0, 0, 0]
    for period in range(0, bulk, test_days):
        outcomes = simulate(learn_days, test_days, days_offset=period, cash=cash, factor_cutoff=factor_cutoff)
        for i, outcome in enumerate(outcomes):
            totals[i] += outcome

    averages = [0, 0, 0]
    for i, total in enumerate(totals):
        averages[i] += total / (bulk / test_days)
    print("learn:{0} test:{1} bulk:{2} - {3}".format(learn_days, test_days, bulk, averages))
    # return average
