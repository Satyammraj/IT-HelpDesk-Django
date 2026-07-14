from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    phone = models.CharField(max_length=20, blank=True)

    bio = models.TextField(blank=True)

    theme = models.CharField(
        max_length=10,
        choices=[
            ("light", "Light"),
            ("dark", "Dark"),
        ],
        default="light",
    )
    email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username



