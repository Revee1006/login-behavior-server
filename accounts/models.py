from django.db import models

class LoginEvent(models.Model):
    event = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event} at {self.timestamp}"
