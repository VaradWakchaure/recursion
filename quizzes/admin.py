from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
import re
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

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:object_id>/import/', self.admin_site.admin_view(self.import_questions_view), name='quizzes_quiz_import'),
        ]
        return my_urls + urls

    def import_questions_view(self, request, object_id):
        quiz = self.get_object(request, object_id)
        if quiz is None:
            return self._get_obj_does_not_exist_redirect(request, self.model._meta, object_id)

        if request.method == 'POST':
            text = request.POST.get('questions_text', '')
            try:
                questions_created = self.parse_aiken_format(quiz, text)
                self.message_user(request, f"Successfully imported {questions_created} questions.", messages.SUCCESS)
                return redirect('admin:quizzes_quiz_change', object_id)
            except Exception as e:
                self.message_user(request, f"Error importing questions: {str(e)}", messages.ERROR)

        context = dict(
            self.admin_site.each_context(request),
            opts=self.model._meta,
            object=quiz,
            title=f"Import Questions for {quiz.title}"
        )
        return render(request, 'admin/quizzes/quiz/import_questions.html', context)

    def parse_aiken_format(self, quiz, text):
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        questions_created = 0
        current_question = []
        current_choices = []
        
        with transaction.atomic():
            for line in lines:
                # Check for answer line
                if line.upper().startswith("ANSWER:"):
                    correct_letter = line.split(":")[1].strip().upper()
                    
                    # Save current question
                    if current_question and current_choices:
                        q_text = "\n".join(current_question)
                        question = Question.objects.create(quiz=quiz, text=q_text)
                        
                        for choice_letter, choice_text in current_choices:
                            is_correct = (choice_letter == correct_letter)
                            Choice.objects.create(question=question, text=choice_text, is_correct=is_correct)
                            
                        questions_created += 1
                        
                    # Reset state
                    current_question = []
                    current_choices = []
                elif re.match(r'^[A-Z][\.\)]\s+', line):
                    # It's a choice line (e.g. "A. option" or "A) option")
                    match = re.match(r'^([A-Z])[\.\)]\s+(.*)', line)
                    if match:
                        choice_letter = match.group(1).upper()
                        choice_text = match.group(2)
                        current_choices.append((choice_letter, choice_text))
                else:
                    # It's part of the question text
                    current_question.append(line)
                    
        return questions_created

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
