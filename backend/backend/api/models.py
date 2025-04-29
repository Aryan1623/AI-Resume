from django.db import models

class Resume(models.Model):
    user_id = models.CharField(max_length=255)  # Firebase UID
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    skills = models.TextField()
    experience = models.TextField()
    education = models.TextField()
    score = models.FloatField(default=0)  # AI-generated score
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

