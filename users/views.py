from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

from quizzes.models import Attempt
from django.db.models import Count
import json

@login_required
def dashboard(request):
    attempts = Attempt.objects.filter(user=request.user, is_completed=True).select_related('quiz').annotate(num_questions=Count('quiz__questions')).order_by('-completed_at')
    
    total_attempts = attempts.count()
    total_score = 0
    total_possible = 0
    
    chart_labels = []
    chart_scores = []
    
    # Process analytics
    for attempt in attempts:
        tq = attempt.num_questions
        total_score += attempt.score
        total_possible += tq
        # For charts, storing the most recent ones or all. We reverse for chronological chart.
        
    accuracy = 0
    if total_possible > 0:
        accuracy = round((total_score / total_possible) * 100, 2)
        
    # Chronological order for chart
    chronological_attempts = attempts.reverse()
    for attempt in chronological_attempts:
        chart_labels.append(attempt.quiz.title)
        chart_scores.append(attempt.score)
        
    context = {
        'user': request.user,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'accuracy': accuracy,
        'chart_labels': json.dumps(chart_labels),
        'chart_scores': json.dumps(chart_scores),
    }
    return render(request, 'users/dashboard.html', context)
