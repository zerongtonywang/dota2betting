from .query import *


def get_cash_outcome(team, match, cash_outcome, cash):
    if match.winner == team:
        if team == match.team1:
            cash_outcome += cash / match.team1odds - cash
        elif team == match.team2:
            cash_outcome += cash / match.team2odds - cash
    else:
        cash_outcome -= cash
    return cash_outcome


def get_outcome_percentage(team, match, percentage_outcome, cash):
    return


def bet_on_winrate(team1stat, team2stat, match, outcome, cash):
    # bet on team1
    if team1stat.winrate > team2stat.winrate:
        outcome = get_cash_outcome(match.team1, match, outcome, cash)
    # bet on team2
    elif team1stat.winrate < team2stat.winrate:
        outcome = get_cash_outcome(match.team2, match, outcome, cash)
    return outcome


def bet_on_odds(team1stat, team2stat, match, outcome, cash, factor_cutoff):
    # bet on team1
    if team1stat.winrate > team2stat.winrate and match.team1odds - match.team2odds >= factor_cutoff:
        outcome = get_cash_outcome(match.team1, match, outcome, cash)
    # bet on team2
    elif team1stat.winrate < team2stat.winrate and match.team2odds - match.team1odds >= factor_cutoff:
        outcome = get_cash_outcome(match.team2, match, outcome, cash)
    return outcome


def bet_dynamically(team1stat, team2stat, match, outcome, cash, factor_cutoff):
    # bet on team1
    if team1stat.winrate > team2stat.winrate:
        delta_odds = match.team1odds - match.team2odds
        if delta_odds >= 0:
            bet_factor = 1 - delta_odds
            cash *= bet_factor
            outcome = get_cash_outcome(match.team1, match, outcome, cash)
    # bet on team2
    elif team1stat.winrate < team2stat.winrate:
        delta_odds = match.team2odds - match.team1odds
        if delta_odds >= 0:
            bet_factor = 1 - delta_odds
            cash *= bet_factor
            outcome = get_cash_outcome(match.team1, match, outcome, cash)
    return outcome


# bet on matches using learned teamstats, with cash
def bet(matches, statset, cash=100, factor_cutoff=0):
    outcomes = [0, 0, 0]
    for match in matches:
        try:
            team1stat = Teamstat.objects.get(statset=statset, team=match.team1)
            team2stat = Teamstat.objects.get(statset=statset, team=match.team2)
        except Teamstat.DoesNotExist:
            continue

        outcomes[0] = bet_on_winrate(team1stat, team2stat, match, outcomes[0], cash)
        outcomes[1] = bet_on_odds(team1stat, team2stat, match, outcomes[1], cash, factor_cutoff)
        outcomes[2] = bet_dynamically(team1stat, team2stat, match, outcomes[2], cash, factor_cutoff)
    return outcomes
