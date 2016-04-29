from django.contrib import admin
from django.apps import apps

from advanced_filters.admin import AdminAdvancedFiltersMixin

from .query import *

app = apps.get_app_config("scraper")


class TeamAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    field_list = ("name",)

    readonly_fields = field_list
    list_display = field_list
    search_fields = field_list
    advanced_filter_fields = field_list


class MatchAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    field_list = ("id", "winner", "team1", "team1odds", "team2odds", "team2")

    readonly_fields = (
        "id", "when", "event", "finished", "valid", "bestof", "winner",
        "team1", "team1odds", "team2odds", "team2",
    )

    list_display = field_list
    search_fields = ("id", "team1__name", "team2__name")
    advanced_filter_fields = (
        ("team1__name", "team1 name"),
        ("team2__name", "team2 name"),
        ("winner__name", "winner"),
        ("valid", "valid"),
    )


class TeamstatAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    field_list = ("statset", "team", "wins", "games", "winrate", "odds", "delta")

    list_display = field_list
    ordering = ("-games",)
    advanced_filter_fields = (
        ("statset__title", "title"),
        # ("teams", "teams"),
        # ("wins", "wins"),
        # ("games", "games"),
        # ("winrate", "winrate"),
        # ("odds", "odds"),
        # ("delta", "delta")
    )


class StatSetAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        print("saving model")
        add_statset(title=obj.title, names=obj.names, lastgames=obj.lastgames, delta_days=obj.delta_days,
                    delta_begin=obj.delta_begin)


ADMIN_DICT = {
    "team": TeamAdmin,
    "match": MatchAdmin,
    "teamstat": TeamstatAdmin,
    "statset": StatSetAdmin,
}

for model_name, model in app.models.items():
    exclude = []
    if model_name in ADMIN_DICT:
        admin.site.register(model, ADMIN_DICT[model_name])
    elif model_name not in exclude:
        admin.site.register(model)
