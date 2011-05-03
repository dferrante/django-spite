from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Loser(models.Model):
    user = models.ForeignKey(User)

admin.site.register(Loser)
