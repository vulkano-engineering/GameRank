from django.contrib import admin
from .models import Game, Vote, Follow, Comment


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'platform',
        'genre',
        'developer',
        'publisher',
        'release_date',
        'source',
        'average_score',
        'votes_count',
        'followers_count',
        'comments_count',
    )
    list_filter = ('platform', 'genre', 'source', 'release_date')
    search_fields = ('title', 'developer', 'publisher', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'game__title')
    readonly_fields = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'game__title')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'body', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'game__title', 'body')
    readonly_fields = ('created_at', 'updated_at')
