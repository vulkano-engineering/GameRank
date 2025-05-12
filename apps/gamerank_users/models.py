from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Optional


class SitePassword(models.Model):
    """Model for storing the site-wide password."""
    value = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "Site Password"


class UserProfile(models.Model):
    """Model for storing user preferences and settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    alias = models.CharField(max_length=100, blank=True)
    font_family = models.CharField(max_length=100, default='Arial')
    font_size = models.CharField(max_length=20, default='medium')  # small, medium, large
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile for {self.user.username}"

    @property
    def display_name(self) -> str:
        """Get the user's display name (alias or username)."""
        return self.alias or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender: type[User], instance: User, created: bool, **kwargs: dict) -> None:
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender: type[User], instance: User, **kwargs: dict) -> None:
    """Save the UserProfile when the User is saved."""
    instance.profile.save()
