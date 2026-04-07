from django.db import models
from django.conf import settings

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(help_text="Time limit for the quiz in minutes")
    start_time = models.DateTimeField(null=True, blank=True, help_text="When the quiz becomes available")
    end_time = models.DateTimeField(null=True, blank=True, help_text="When the quiz is no longer available")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Anti-cheat / General Settings
    shuffle_questions = models.BooleanField(default=False)
    shuffle_choices = models.BooleanField(default=False)
    total_questions = models.IntegerField(default=0, help_text="Number of questions to serve from the total pool")

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=0, help_text="Optional logic for keeping questions ordered if not shuffled")

    def __str__(self):
        return f"{self.quiz.title} - Question {self.pk}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'quiz') # Enforce single attempt per user per quiz

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} Attempt"

class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('attempt', 'question') # Prevent duplicate answers per question per attempt

    def __str__(self):
        return f"Answer for {self.question.pk} by Attempt {self.attempt.pk}"
