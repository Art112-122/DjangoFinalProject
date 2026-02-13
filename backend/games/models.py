from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField()
    tags = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="games/", blank=True, null=True)

    def __str__(self):
        return self.name
