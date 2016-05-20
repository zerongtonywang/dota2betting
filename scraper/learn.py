import tensorflow as tf
from .query import matches_filter
from django.utils import timezone
from datetime import timedelta


def create_train_data(args):
    train_days = args["delta_days"]
    begintime = timezone.now() - timedelta(days=args["delta_begin"])

    matches = matches_filter(delta_days=train_days, delta_begin=begintime)

    print(len(matches))

    train_data = []
