from django.contrib import admin
from django.urls import path, include

# JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Documentation
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

# Router + API ViewSets
from rest_framework.routers import DefaultRouter
from education.views import CourseViewSet, LessonViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    # твой main app
    path('', include('main.urls')),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]

# Router for education API
router = DefaultRouter()
router.register("api/v1/education/courses", CourseViewSet, basename="courses")
router.register("api/v1/education/lessons", LessonViewSet, basename="lessons")

urlpatterns += router.urls
