from django.db import models


class Item(models.Model):
    number = models.TextField(max_length="25")
    description = models.TextField(max_length="25")


class Charge(models.Model):
    order = models.PositiveIntegerField()
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.CASCADE)
