from django.db import models

# Create your models here.

class ScrapedData(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + " | " +  self.url