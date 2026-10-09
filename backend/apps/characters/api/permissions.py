"""
Character API Permissions
Custom permissions für Character-Management mit Admin-Support
"""

from rest_framework.permissions import BasePermission
from apps.permissions.models import Permission


class CharacterPermission(BasePermission):
    """
    Custom Permission für Character-Management
    - User kann eigene Charaktere verwalten
    - Admin kann alle Charaktere in der Welt verwalten
    """
    
    def has_permission(self, request, view):
        """Basis-Permission: User muss authentifiziert sein"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Object-Level-Permission für spezifische Charaktere"""
        # Eigene Charaktere sind immer erlaubt
        if obj.user == request.user:
            return True
        
        # Admin-Berechtigungen prüfen
        if self._has_world_admin_permission(request.user, obj.world):
            return True
        
        return False
    
    def _has_world_admin_permission(self, user, world):
        """Prüft ob User Admin-Rechte für die Welt hat"""
        return Permission.objects.filter(
            user=user,
            resource_type='world',
            object_id=str(world.id),
            permission_type='admin'
        ).exists()


class CharacterOwnerOrWorldAdminPermission(BasePermission):
    """
    Permission für Character-Operations:
    - Character-Owner kann alle Operationen durchführen
    - World-Admin kann alle Operationen durchführen
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Character-Owner
        if obj.user == request.user:
            return True
        
        # World-Admin
        world_admin = Permission.objects.filter(
            user=request.user,
            resource_type='world',
            object_id=str(obj.world.id),
            permission_type='admin'
        ).exists()
        
        return world_admin 