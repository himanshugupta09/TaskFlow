from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='project')
router.register('tasks',    views.TaskViewSet,    basename='task')

urlpatterns = [
    # Auth
    path('auth/register/', views.register),
    path('auth/login/',    TokenObtainPairView.as_view()),
    path('auth/refresh/',  TokenRefreshView.as_view()),
    path('auth/me/',       views.me),

    # Dashboard + search
    path('dashboard/',    views.dashboard),
    path('users/search/', views.search_users),

    # Notifications
    path('notifications/',               views.notifications_list),
    path('notifications/unread/',        views.notifications_unread_count),
    path('notifications/mark-read/',     views.notifications_mark_read, {'ids': None}),
    path('notifications/mark-read/',     views.notifications_mark_read),
    path('notifications/<int:pk>/',      views.notification_delete),

    # Invites
    path('projects/<int:project_id>/invite/',               views.invite_to_project),
    path('projects/<int:project_id>/invites/',              views.project_invites),
    path('projects/<int:project_id>/invites/<int:invite_id>/', views.cancel_invite),
    path('invites/<uuid:token>/',                           views.invite_info),
    path('invites/<uuid:token>/accept/',                    views.accept_invite),

    # ViewSet routes (projects, tasks, task comments/history)
    path('', include(router.urls)),
]