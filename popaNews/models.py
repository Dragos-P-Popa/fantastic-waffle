from django.db import models
from django.conf import settings

CATEGORIES = (
    ("POL", "Politics"),
    ("ART", "Art"),
    ("TECH", "Technology New"),
    ("TRIVIA", "Trivia News")
)

REGIONS = (
    ("UK", "United Kingdom"),
    ("EU", "European Union"),
    ("W", "World")
)

class Article(models.Model):
    key = models.AutoField(primary_key=True)
    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=32,
                  choices=CATEGORIES)
    region = models.CharField(max_length=32,
                  choices=REGIONS)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    date = models.DateField(auto_now=True)
    details = models.CharField(max_length=128)
