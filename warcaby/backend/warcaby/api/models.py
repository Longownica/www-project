from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class CheckersGame(models.Model):
    finished = models.BooleanField(default=False)
    state = PickledObjectField()