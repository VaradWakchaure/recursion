from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('<int:quiz_id>/leaderboard/', views.quiz_leaderboard, name='quiz_leaderboard'),
]
