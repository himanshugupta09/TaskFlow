from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='project')
router.register('tasks',    views.TaskViewSet,    basename='task')

urlpatterns = [

    path('auth/register/', views.register, name='auth_register'),
    path('auth/login/',    TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/',  TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/',       views.me, name='auth_me'),

    path('dashboard/',     views.dashboard, name='dashboard'),
    path('users/search/',  views.search_users, name='user_search'),

    path('notifications/',              views.notifications_list, name='notifications_list'),
    path('notifications/unread/',       views.notifications_unread_count, name='notifications_unread_count'),
    path('notifications/mark-read/',    views.notifications_mark_read, name='notifications_mark_read'),
    path('notifications/<int:pk>/',     views.notification_delete, name='notification_delete'),

    path('projects/<int:project_id>/invite/',                   views.invite_to_project, name='invite_to_project'),
    path('projects/<int:project_id>/invites/',                  views.project_invites, name='project_invites'),
    path('projects/<int:project_id>/invites/<int:invite_id>/',  views.cancel_invite, name='cancel_invite'),
    path('invites/<uuid:token>/',                               views.invite_info, name='invite_info'),
    path('invites/<uuid:token>/accept/',                        views.accept_invite, name='accept_invite'),

    path('health/',  views.health_check, name='health_check'),
    path('metrics/', views.metrics, name='metrics'),

    path('', include(router.urls)),
    path('debug-db/', views.debug_db),
]