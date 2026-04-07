from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('parse-resume/', views.parse_resume, name='parse-resume'),
    path('score-candidate/', views.score_candidate, name='score-candidate'),
    path('rank-candidates/<uuid:job_id>/', views.rank_candidates_for_job, name='rank-candidates'),
    path('generate-job-description/', views.generate_job_description, name='generate-job-description'),
    path('generate-interview-questions/', views.generate_interview_questions, name='generate-interview-questions'),
    path('screen-resume/', views.screen_resume_against_job, name='screen-resume'),
]
