from django.db import models
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class StatSet(models.Model):
    title = models.CharField(max_length=40, unique=True)
    names = models.CharField(max_length=200, null=True, blank=True)
    lastgames = models.IntegerField(default=99999)
    delta_days = models.IntegerField(default=60)
    delta_begin = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Teamstat(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    statset = models.ForeignKey(StatSet)

    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    delta = models.FloatField(default=0)
    winrate = models.FloatField(default=0)
    odds = models.FloatField(default=0)


class Match(models.Model):
    finished = models.BooleanField(default=True)
    valid = models.BooleanField(default=True)
    team1 = models.ForeignKey(Team, related_name="team1")
    team1odds = models.FloatField()
    team2 = models.ForeignKey(Team, related_name="team2")
    team2odds = models.FloatField()
    winner = models.ForeignKey(Team, related_name="winner")
    bestof = models.IntegerField(default=1)
    when = models.DateTimeField(null=True, blank=True)
    event = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Matches"
