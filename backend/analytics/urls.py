from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.dashboard_stats, name='dashboard'),
    path('funnel/', views.hiring_funnel, name='funnel'),
    path('sources/', views.candidate_sources, name='sources'),
    path('trends/', views.hiring_trends, name='trends'),
    path('job-performance/', views.job_performance, name='job-performance'),
]
