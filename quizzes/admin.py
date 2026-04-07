from django.contrib import admin
from .models import Quiz, Question, Choice, Attempt, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [ChoiceInline]

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True # Allows clicking through to edit choices

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'duration_minutes', 'start_time', 'end_time', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('quiz', 'is_completed')
    search_fields = ('user__username', 'quiz__title')

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'choice')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Attempt, AttemptAdmin)
admin.site.register(Answer, AnswerAdmin)
