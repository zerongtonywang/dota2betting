from datetime import datetime
from .bet import *


# Simulate betting with {cash} dollars using data from past {delta_days} days, validate using data from {test_days} days
def simulate(learn_days, test_days, days_offset=0, cash=100, factor_cutoff=0):
    offset_begin = datetime.now() - timedelta(days=days_offset)
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


# Run simulations across {bulk} days
def bulk_simulate(learn_days, test_days, days_offset=0, cash=100, factor_cutoff=0, bulk=360):
    totals = [0, 0, 0]
    for period in range(days_offset, bulk, test_days):
        outcomes = simulate(learn_days, test_days, days_offset=period, cash=cash, factor_cutoff=factor_cutoff)
        for i, outcome in enumerate(outcomes):
            totals[i] += outcome

    averages = [0, 0, 0]
    for i, total in enumerate(totals):
        averages[i] += total / (bulk / test_days)
    print("learn:{0} test:{1} bulk:{2} - {3}".format(learn_days, test_days, bulk, averages))
    # return average
