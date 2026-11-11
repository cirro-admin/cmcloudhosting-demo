from django.db import models


class Entry(models.Model):
    """One guestbook row — enough to prove migrations ran and writes land."""

    label = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.label
