from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CandidateNoteViewSet, CandidateViewSet

router = DefaultRouter()
router.register(r'', CandidateViewSet, basename='candidate')
router.register(r'notes', CandidateNoteViewSet, basename='candidate-note')

urlpatterns = [
    path('', include(router.urls)),
]
