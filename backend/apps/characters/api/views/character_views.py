"""
Character API Views
DRF views for character management endpoints
"""

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.characters.api.permissions import CharacterOwnerOrWorldAdminPermission

from apps.characters.models import (
    Character, RuleSet, DSARace, DSACulture, DSAProfession,
    DSAAdvantage, DSADisadvantage
)
from apps.characters.api.serializers.character_serializers import (
    CharacterListSerializer, CharacterDetailSerializer, CharacterCreateSerializer, CharacterUpdateSerializer,
    RuleSetSerializer, DSARaceSerializer, DSACultureSerializer, DSAProfessionSerializer,
    DSAAdvantageSerializer, DSADisadvantageSerializer, ReferenceDataSerializer,
    CharacterValidationSerializer, CharacterCalculationSerializer
)
from apps.characters.services.character_crud import CharacterCRUDService
from apps.characters.services.character_calculation_engine import CharacterCalculationEngine


class CharacterViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Character-Management
    """
    permission_classes = [IsAuthenticated, CharacterOwnerOrWorldAdminPermission]
    queryset = Character.objects.all().order_by('name')
    
    def get_queryset(self):
        """Filtert Charaktere nach User und Berechtigungen"""
        from apps.permissions.models import Permission
        from django.db.models import Q
        
        # Eigene Charaktere
        own_characters = Q(user=self.request.user)
        
        # Charaktere in Welten, für die der User Admin-Rechte hat
        admin_world_permissions = Permission.objects.filter(
            user=self.request.user,
            resource_type='world',
            permission_type='admin'
        )
        
        admin_world_ids = []
        for perm in admin_world_permissions:
            try:
                admin_world_ids.append(perm.object_id)
            except:
                continue
        
        # Wenn User Admin-Rechte für Welten hat, zeige alle Charaktere in diesen Welten
        if admin_world_ids:
            world_characters = Q(world_id__in=admin_world_ids)
            return Character.objects.filter(own_characters | world_characters).order_by('name')
        else:
            # Nur eigene Charaktere
            return Character.objects.filter(own_characters).order_by('name')
    
    def get_serializer_class(self):
        """Wählt Serializer basierend auf Action"""
        if self.action == 'list':
            return CharacterListSerializer
        elif self.action == 'create':
            return CharacterCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CharacterUpdateSerializer
        else:
            return CharacterDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Erstellt einen neuen Charakter"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Character erstellen
        character, errors = CharacterCRUDService.create_character(
            user=request.user,
            world_id=request.data.get('world_id') or str(request.data.get('world')),
            character_data=request.data
        )
        
        if character:
            response_serializer = CharacterDetailSerializer(character)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Aktualisiert einen Charakter"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Verwende CharacterCRUDService für das Update
        character, errors = CharacterCRUDService.update_character(
            character_id=str(instance.id),
            user=request.user,
            update_data=request.data
        )
        
        if character:
            response_serializer = CharacterDetailSerializer(character)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_update(self, serializer):
        """Führt das Update durch"""
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Löscht einen Charakter"""
        character = self.get_object()
        
        success, errors = CharacterCRUDService.delete_character(
            character_id=str(character.id),
            user=request.user
        )
        
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def full_data(self, request, pk=None):
        """Holt vollständige Charakterdaten"""
        character = self.get_object()
        
        full_data = CharacterCRUDService.get_character_full_data(
            character_id=str(character.id),
            user=request.user
        )
        
        if full_data:
            return Response(full_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Character not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def by_world(self, request):
        """Holt Charaktere für eine spezifische World"""
        world_id = request.query_params.get('world_id')
        if not world_id:
            return Response({'error': 'world_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        characters = CharacterCRUDService.get_user_characters(
            user=request.user,
            world_id=world_id
        )
        
        serializer = CharacterListSerializer(characters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validiert Character-Daten"""
        serializer = CharacterValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        character_data = serializer.validated_data['character_data']
        errors = CharacterCalculationEngine.validate_character_rules(character_data)
        
        return Response({
            'is_valid': len(errors) == 0,
            'errors': errors
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Berechnet abgeleitete Werte"""
        serializer = CharacterCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        derived_values = CharacterCalculationEngine.calculate_derived_values(
            core_attributes=serializer.validated_data['core_attributes'],
            race_modifiers=serializer.validated_data.get('race_modifiers'),
            advantages=serializer.validated_data.get('advantages')
        )
        
        return Response(derived_values, status=status.HTTP_200_OK)


class RuleSetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für RuleSet-Referenzdaten
    """
    permission_classes = [IsAuthenticated]
    queryset = RuleSet.objects.filter(is_active=True)
    serializer_class = RuleSetSerializer


class DSARaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für DSA Race-Referenzdaten
    """
    permission_classes = [IsAuthenticated]
    queryset = DSARace.objects.filter(is_active=True)
    serializer_class = DSARaceSerializer
    
    @action(detail=True, methods=['get'])
    def modifiers(self, request, pk=None):
        """Holt Attributs-Modifikatoren für eine Rasse"""
        race = self.get_object()
        return Response(race.attribute_modifiers, status=status.HTTP_200_OK)


class DSACultureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für DSA Culture-Referenzdaten
    """
    permission_classes = [IsAuthenticated]
    queryset = DSACulture.objects.filter(is_active=True)
    serializer_class = DSACultureSerializer
    
    @action(detail=True, methods=['get'])
    def bonuses(self, request, pk=None):
        """Holt Boni für eine Kultur"""
        culture = self.get_object()
        return Response({
            'language_bonuses': culture.language_bonuses,
            'script_bonuses': culture.script_bonuses,
            'talent_modifications': culture.talent_modifications
        }, status=status.HTTP_200_OK)


class DSAProfessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für DSA Profession-Referenzdaten
    """
    permission_classes = [IsAuthenticated]
    queryset = DSAProfession.objects.filter(is_active=True)
    serializer_class = DSAProfessionSerializer
    
    @action(detail=True, methods=['get'])
    def requirements(self, request, pk=None):
        """Holt Anforderungen für eine Profession"""
        profession = self.get_object()
        return Response({
            'attribute_requirements': profession.attribute_requirements,
            'talent_bonuses': profession.talent_bonuses,
            'granted_special_abilities': profession.granted_special_abilities
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Holt Professionen nach Kategorie"""
        category = request.query_params.get('category')
        if category:
            professions = DSAProfession.objects.filter(category=category, is_active=True)
        else:
            professions = DSAProfession.objects.filter(is_active=True)
        
        serializer = self.get_serializer(professions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DSAAdvantageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für DSA Advantage-Referenzdaten
    """
    permission_classes = [IsAuthenticated]
    queryset = DSAAdvantage.objects.filter(is_active=True)
    serializer_class = DSAAdvantageSerializer
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Holt Vorteile nach Kategorie"""
        category = request.query_params.get('category')
        if category:
            advantages = DSAAdvantage.objects.filter(category=category, is_active=True)
        else:
            advantages = DSAAdvantage.objects.filter(is_active=True)
        
        serializer = self.get_serializer(advantages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DSADisadvantageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für DSA Disadvantage-Referenzdaten
    """
    permission_classes = [IsAuthenticated]
    queryset = DSADisadvantage.objects.filter(is_active=True)
    serializer_class = DSADisadvantageSerializer
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Holt Nachteile nach Kategorie"""
        category = request.query_params.get('category')
        if category:
            disadvantages = DSADisadvantage.objects.filter(category=category, is_active=True)
        else:
            disadvantages = DSADisadvantage.objects.filter(is_active=True)
        
        serializer = self.get_serializer(disadvantages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferenceDataViewSet(viewsets.ViewSet):
    """
    ViewSet für alle Referenz-Daten
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Holt alle Referenz-Daten"""
        reference_data = CharacterCRUDService.get_reference_data()
        serializer = ReferenceDataSerializer(reference_data)
        return Response(serializer.data, status=status.HTTP_200_OK) 