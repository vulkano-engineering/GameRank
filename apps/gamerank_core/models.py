from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.utils import timezone
from typing import Optional


class Game(models.Model):
    """Model representing a video game."""
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=200)
    platform = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    developer = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    release_date = models.DateField()
    description = models.TextField()
    image_url = models.URLField()
    source = models.CharField(max_length=50)  # e.g., 'LIS1', 'FTG', 'MMO'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date']

    def __str__(self) -> str:
        return f"{self.title} ({self.platform})"

    @property
    def average_score(self) -> float:
        """Calculate the average score for this game."""
        result = self.votes.aggregate(avg=Avg('score'))
        return result['avg'] or 0.0

    @property
    def votes_count(self) -> int:
        """Get the total number of votes for this game."""
        return self.votes.count()

    @property
    def followers_count(self) -> int:
        """Get the total number of followers for this game."""
        return self.follows.count()

    @property
    def comments_count(self) -> int:
        """Get the total number of comments for this game."""
        return self.comments.count()


class Vote(models.Model):
    """Model representing a user's vote on a game."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='votes')
    score = models.IntegerField(choices=[(i, i) for i in range(6)])  # 0-5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'game']
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} voted {self.score} for {self.game.title}"


class Follow(models.Model):
    """Model representing a user following a game."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='follows')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'game']
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} follows {self.game.title}"


class Comment(models.Model):
    """Model representing a user's comment on a game."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Comment by {self.user.username} on {self.game.title}"


# Add properties to User model
def get_user_votes_count(self) -> int:
    """Get the total number of votes by this user."""
    return self.votes.count()


def get_user_average_score(self) -> float:
    """Calculate the average score given by this user."""
    result = self.votes.aggregate(avg=Avg('score'))
    return result['avg'] or 0.0


def get_user_follows_count(self) -> int:
    """Get the total number of games followed by this user."""
    return self.follows.count()


def get_user_comments_count(self) -> int:
    """Get the total number of comments by this user."""
    return self.comments.count()


# Add properties to User model
User.add_to_class('votes_count', property(get_user_votes_count))
User.add_to_class('average_score', property(get_user_average_score))
User.add_to_class('follows_count', property(get_user_follows_count))
User.add_to_class('comments_count', property(get_user_comments_count))
