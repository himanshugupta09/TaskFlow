from rest_framework.permissions import BasePermission
from .models import ProjectMember

class IsProjectAdmin(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id') or view.kwargs.get('pk')
        if not project_id:
            return False
        return ProjectMember.objects.filter(
            project_id=project_id, user=request.user, role='admin'
        ).exists()

class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id') or view.kwargs.get('pk')
        if not project_id:
            return True
        return ProjectMember.objects.filter(
            project_id=project_id, user=request.user
        ).exists()