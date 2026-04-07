"""
URL configuration for recruitment_platform project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from jobs.views import ApplicationViewSet, InterviewViewSet

# Top-level router for resources that need their own /api/v1/ prefix
api_router = DefaultRouter()
api_router.register(r'applications', ApplicationViewSet, basename='application')
api_router.register(r'interviews', InterviewViewSet, basename='interview')

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT authentication
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # App endpoints
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/candidates/", include("candidates.urls")),
    path("api/v1/jobs/", include("jobs.urls")),
    path("api/v1/", include(api_router.urls)),
    path("api/v1/integrations/", include("integrations.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/ai/", include("ai_engine.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
