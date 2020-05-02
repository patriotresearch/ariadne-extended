from django.db import models


class Something(models.Model):
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=4)
