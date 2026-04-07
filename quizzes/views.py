from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Quiz, Question, Choice, Attempt, Answer
from django.db import IntegrityError, transaction

@login_required
def quiz_list(request):
    # Only show active quizzes
    quizzes = Quiz.objects.filter(is_active=True).order_by('-created_at')
    print(Quiz.objects.all())
    # We can also fetch the user's past attempts to show if they've already taken a quiz
    attempts = Attempt.objects.filter(user=request.user).values_list('quiz_id', flat=True)
    
    context = {
        'quizzes': quizzes,
        'attempted_quizzes': attempts,
    }
    return render(request, 'quizzes/quiz_list.html', context)

@login_required
def quiz_attempt(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if attempt already exists (prevent multiple attempts)
    attempt = Attempt.objects.filter(user=request.user, quiz=quiz).first()
    
    if request.method == 'POST':
        if attempt and attempt.is_completed:
            return redirect('quiz_result', quiz_id=quiz.id)
            
        if not attempt:
            # Fallback if attempt wasn't created via GET somehow
            attempt = Attempt.objects.create(user=request.user, quiz=quiz)
            
        score = 0
        questions = quiz.questions.all()
        
        # Calculate time taken
        time_diff = timezone.now() - attempt.started_at
        time_taken_seconds = int(time_diff.total_seconds())
        duration_seconds = quiz.duration_minutes * 60
        
        # We allow late submissions but record the true time_taken_seconds.
        # No score penalty is applied here per user constraints.

        with transaction.atomic():
            # Process submitted answers consistently
            for question in questions:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    try:
                        choice = Choice.objects.get(id=choice_id, question=question)
                        # Create or update answer record idempotently mapping attempt and question
                        Answer.objects.update_or_create(
                            attempt=attempt, 
                            question=question,
                            defaults={'choice': choice}
                        )
                        if choice.is_correct:
                            score += 1
                    except Choice.DoesNotExist:
                        pass # Ignore gracefully
            
            # Update attempt atomically
            attempt.score = score
            # Cap the logged time if it's wildly over to not break leaderboards too badly, or just leave it. Leaving it is accurate.
            attempt.time_taken_seconds = time_taken_seconds
            attempt.completed_at = timezone.now()
            attempt.is_completed = True
            attempt.save()
        
        return redirect('quiz_result', quiz_id=quiz.id)

    else:
        # GET request: start the quiz
        if attempt and attempt.is_completed:
            return redirect('quiz_result', quiz_id=quiz.id)
            
        if not attempt:
            try:
                attempt = Attempt.objects.create(user=request.user, quiz=quiz)
            except IntegrityError:
                attempt = Attempt.objects.get(user=request.user, quiz=quiz)
        
        # Calculate remaining time (Backend as source of truth)
        time_elapsed = (timezone.now() - attempt.started_at).total_seconds()
        duration_seconds = quiz.duration_minutes * 60
        time_left = max(0, int(duration_seconds - time_elapsed))
        
        # If time has already expired while loading, force submission or redirect
        if time_left <= 0:
            attempt.is_completed = True
            attempt.completed_at = timezone.now()
            attempt.time_taken_seconds = int((timezone.now() - attempt.started_at).total_seconds())
            attempt.save()
            return redirect('quiz_result', quiz_id=quiz.id)

        # We prefetch choices to optimize DB queries
        questions = quiz.questions.prefetch_related('choices').all()
        
        # Optional: Custom logic for randomizing questions/choices can be added here based on quiz flags
        if quiz.shuffle_questions:
            questions = questions.order_by('?')
            
        context = {
            'quiz': quiz,
            'questions': questions,
            'attempt': attempt,
            'time_left': time_left,
        }
        return render(request, 'quizzes/quiz_attempt.html', context)

@login_required
def quiz_result(request, quiz_id):
    attempt = get_object_or_404(Attempt, user=request.user, quiz_id=quiz_id, is_completed=True)
    total_questions = attempt.quiz.questions.count()
    
    context = {
        'attempt': attempt,
        'total_questions': total_questions
    }
    return render(request, 'quizzes/quiz_result.html', context)

@login_required
def quiz_leaderboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Query for all completed attempts for this specific quiz
    # Order by highest score first (-score), then by lowest time taken (time_taken_seconds)
    leaderboard_attempts = Attempt.objects.filter(
        quiz=quiz, 
        is_completed=True
    ).select_related('user').order_by('-score', 'time_taken_seconds')
    
    context = {
        'quiz': quiz,
        'leaderboard': leaderboard_attempts
    }
    return render(request, 'quizzes/quiz_leaderboard.html', context)
