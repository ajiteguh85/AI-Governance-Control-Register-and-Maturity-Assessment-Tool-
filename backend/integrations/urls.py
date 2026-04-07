from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'integrations'

router = DefaultRouter()
router.register(r'', views.IntegrationViewSet, basename='integration')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/<uuid:integration_id>/', views.webhook_receive, name='webhook-receive'),
]
