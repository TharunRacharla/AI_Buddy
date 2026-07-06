from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Note {self.id}"

    class Meta:
        ordering = ['-created_at']  # latest first