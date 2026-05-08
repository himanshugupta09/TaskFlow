from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='project')
router.register('tasks', views.TaskViewSet, basename='task')

urlpatterns = [
    path('auth/register/', views.register),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/me/', views.me),
    path('healthz/', views.healthz),
    path('dashboard/', views.dashboard),
    path('', include(router.urls)),
]