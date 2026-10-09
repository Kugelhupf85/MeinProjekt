"""
Character CRUD Service
Handles character creation, reading, updating, and deletion operations
"""

from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.characters.models import (
    Character, CharacterRuleSetData, RuleSet, DSARace, DSACulture, DSAProfession,
    DSAAdvantage, DSADisadvantage, CharacterAdvantage, CharacterDisadvantage
)
from apps.characters.services.character_calculation_engine import CharacterCalculationEngine

User = get_user_model()


class CharacterCRUDService:
    """Service für Character CRUD-Operationen"""
    
    @staticmethod
    def create_character(user: User, world_id: str, character_data: Dict) -> Tuple[Character, List[str]]:
        """
        Erstellt einen neuen Charakter
        
        Args:
            user: User-Objekt
            world_id: World UUID
            character_data: Character-Daten
            
        Returns:
            Tuple (Character, List[error_messages])
        """
        errors = []
        
        try:
            with transaction.atomic():
                # RuleSet validieren
                rule_set_id = character_data.get('rule_set')
                if isinstance(rule_set_id, str) and rule_set_id.replace('-', '').isalnum():
                    # UUID format
                    rule_set = RuleSet.objects.get(id=rule_set_id)
                else:
                    # Name format
                    rule_set = RuleSet.objects.get(name=character_data.get('rule_set', 'dsa_4_1'))
                
                # Character erstellen
                character = Character.objects.create(
                    user=user,
                    world_id=world_id,
                    rule_set=rule_set,
                    name=character_data['name'],
                    core_attributes=character_data.get('core_attributes', {}),
                    status='draft'
                )
                
                # CharacterRuleSetData erstellen
                ruleset_data = CharacterRuleSetData.objects.create(
                    character=character,
                    generation_points_max=character_data.get('generation_points_max', 110),
                    generation_points_attributes_max=character_data.get('generation_points_attributes_max', 100),
                    attribute_maximum=character_data.get('attribute_maximum', 14)
                )
                
                # Vorteile hinzufügen
                advantages = character_data.get('advantages', [])
                for adv_data in advantages:
                    try:
                        advantage = DSAAdvantage.objects.get(name=adv_data['name'])
                        CharacterAdvantage.objects.create(
                            character=character,
                            advantage=advantage,
                            level=adv_data.get('level', 1),
                            custom_modifiers=adv_data.get('custom_modifiers', {}),
                            validation_errors=[]
                        )
                    except DSAAdvantage.DoesNotExist:
                        errors.append(f"Vorteil '{adv_data['name']}' nicht gefunden")
                
                # Nachteile hinzufügen
                disadvantages = character_data.get('disadvantages', [])
                for dis_data in disadvantages:
                    try:
                        disadvantage = DSADisadvantage.objects.get(name=dis_data['name'])
                        CharacterDisadvantage.objects.create(
                            character=character,
                            disadvantage=disadvantage,
                            level=dis_data.get('level', 1),
                            custom_modifiers=dis_data.get('custom_modifiers', {}),
                            validation_errors=[]
                        )
                    except DSADisadvantage.DoesNotExist:
                        errors.append(f"Nachteil '{dis_data['name']}' nicht gefunden")
                
                # Validierung durchführen
                validation_errors = CharacterCalculationEngine.validate_character_rules(character_data)
                errors.extend(validation_errors)
                
                # Wenn es Fehler gibt, Character löschen und None zurückgeben
                if errors:
                    character.delete()
                    return None, errors
                
                return character, errors
                
        except Exception as e:
            import traceback
            errors.append(f"Fehler beim Erstellen des Charakters: {str(e)}")
            errors.append(f"Traceback: {traceback.format_exc()}")
            return None, errors
    
    @staticmethod
    def get_character(character_id: str, user: User) -> Optional[Character]:
        """
        Holt einen Charakter
        
        Args:
            character_id: Character UUID
            user: User-Objekt
            
        Returns:
            Character-Objekt oder None
        """
        try:
            return Character.objects.get(id=character_id, user=user)
        except Character.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_characters(user: User, world_id: Optional[str] = None) -> List[Character]:
        """
        Holt alle Charaktere eines Users
        
        Args:
            user: User-Objekt
            world_id: Optional World UUID für Filterung
            
        Returns:
            List von Character-Objekten
        """
        queryset = Character.objects.filter(user=user)
        if world_id:
            queryset = queryset.filter(world_id=world_id)
        return list(queryset.select_related('rule_set', 'world', 'ruleset_data'))
    
    @staticmethod
    def update_character(character_id: str, user: User, update_data: Dict) -> Tuple[Character, List[str]]:
        """
        Aktualisiert einen Charakter
        
        Args:
            character_id: Character UUID
            user: User-Objekt
            update_data: Update-Daten
            
        Returns:
            Tuple (Character, List[error_messages])
        """
        errors = []
        
        try:
            # Versuche zuerst, den Charakter als Besitzer zu finden
            character = Character.objects.get(id=character_id, user=user)
        except Character.DoesNotExist:
            # Wenn nicht als Besitzer gefunden, prüfe Admin-Rechte
            try:
                from apps.permissions.models import Permission
                character = Character.objects.get(id=character_id)
                
                # Prüfe, ob User Admin-Rechte für die Welt des Charakters hat
                admin_permission = Permission.objects.filter(
                    user=user,
                    resource_type='world',
                    object_id=str(character.world.id),
                    permission_type='admin'
                ).exists()
                
                if not admin_permission:
                    errors.append("Keine Berechtigung zum Aktualisieren dieses Charakters")
                    return None, errors
                    
            except Character.DoesNotExist:
                errors.append("Charakter nicht gefunden")
                return None, errors
        
        try:
            with transaction.atomic():
                # Core attributes aktualisieren
                if 'core_attributes' in update_data:
                    character.core_attributes = update_data['core_attributes']
                
                # Name aktualisieren
                if 'name' in update_data:
                    character.name = update_data['name']
                
                # Status aktualisieren
                if 'status' in update_data:
                    character.status = update_data['status']
                
                # User aktualisieren (nur für Admin-Berechtigungen)
                if 'user' in update_data and user != character.user:
                    # Prüfe, ob der aktuelle User Admin-Rechte hat
                    from apps.permissions.models import Permission
                    admin_permission = Permission.objects.filter(
                        user=user,
                        resource_type='world',
                        object_id=str(character.world.id),
                        permission_type='admin'
                    ).exists()
                    
                    if admin_permission:
                        try:
                            new_user = User.objects.get(id=update_data['user'])
                            character.user = new_user
                        except User.DoesNotExist:
                            errors.append("Neuer User nicht gefunden")
                
                character.save()
                
                # Ruleset data aktualisieren
                if 'ruleset_data' in update_data:
                    ruleset_data = character.ruleset_data
                    for key, value in update_data['ruleset_data'].items():
                        if hasattr(ruleset_data, key):
                            setattr(ruleset_data, key, value)
                    ruleset_data.save()
                
                # Vorteile aktualisieren
                if 'advantages' in update_data:
                    # Bestehende Vorteile löschen
                    character.character_advantages.all().delete()
                    
                    # Neue Vorteile hinzufügen
                    for adv_data in update_data['advantages']:
                        try:
                            advantage = DSAAdvantage.objects.get(name=adv_data['name'])
                            CharacterAdvantage.objects.create(
                                character=character,
                                advantage=advantage,
                                level=adv_data.get('level', 1),
                                custom_modifiers=adv_data.get('custom_modifiers', {})
                            )
                        except DSAAdvantage.DoesNotExist:
                            errors.append(f"Vorteil '{adv_data['name']}' nicht gefunden")
                
                # Nachteile aktualisieren
                if 'disadvantages' in update_data:
                    # Bestehende Nachteile löschen
                    character.character_disadvantages.all().delete()
                    
                    # Neue Nachteile hinzufügen
                    for dis_data in update_data['disadvantages']:
                        try:
                            disadvantage = DSADisadvantage.objects.get(name=dis_data['name'])
                            CharacterDisadvantage.objects.create(
                                character=character,
                                disadvantage=disadvantage,
                                level=dis_data.get('level', 1),
                                custom_modifiers=dis_data.get('custom_modifiers', {})
                            )
                        except DSADisadvantage.DoesNotExist:
                            errors.append(f"Nachteil '{dis_data['name']}' nicht gefunden")
                
                return character, errors
                
        except Exception as e:
            errors.append(f"Fehler beim Aktualisieren des Charakters: {str(e)}")
            return None, errors
    
    @staticmethod
    def delete_character(character_id: str, user: User) -> Tuple[bool, List[str]]:
        """
        Löscht einen Charakter
        
        Args:
            character_id: Character UUID
            user: User-Objekt
            
        Returns:
            Tuple (success, List[error_messages])
        """
        errors = []
        
        try:
            # Versuche zuerst, den Charakter als Besitzer zu finden
            character = Character.objects.get(id=character_id, user=user)
            character.delete()
            return True, errors
        except Character.DoesNotExist:
            # Wenn nicht als Besitzer gefunden, prüfe Admin-Rechte
            try:
                from apps.permissions.models import Permission
                character = Character.objects.get(id=character_id)
                
                # Prüfe, ob User Admin-Rechte für die Welt des Charakters hat
                admin_permission = Permission.objects.filter(
                    user=user,
                    resource_type='world',
                    object_id=str(character.world.id),
                    permission_type='admin'
                ).exists()
                
                if admin_permission:
                    character.delete()
                    return True, errors
                else:
                    errors.append("Keine Berechtigung zum Löschen dieses Charakters")
                    return False, errors
                    
            except Character.DoesNotExist:
                errors.append("Charakter nicht gefunden")
                return False, errors
        except Exception as e:
            errors.append(f"Fehler beim Löschen des Charakters: {str(e)}")
            return False, errors
    
    @staticmethod
    def get_character_full_data(character_id: str, user: User) -> Optional[Dict]:
        """
        Holt vollständige Charakterdaten
        
        Args:
            character_id: Character UUID
            user: User-Objekt
            
        Returns:
            Dictionary mit vollständigen Charakterdaten
        """
        try:
            character = Character.objects.select_related(
                'rule_set', 'world', 'ruleset_data'
            ).prefetch_related(
                'character_advantages__advantage',
                'character_disadvantages__disadvantage'
            ).get(id=character_id, user=user)
            
            # Basis-Daten
            data = {
                'id': str(character.id),
                'name': character.name,
                'status': character.status,
                'rule_set': character.rule_set.name,
                'world_id': str(character.world.id),
                'core_attributes': character.core_attributes,
                'created_at': character.created_at.isoformat(),
                'updated_at': character.updated_at.isoformat(),
            }
            
            # Ruleset-spezifische Daten
            if hasattr(character, 'ruleset_data'):
                ruleset_data = character.ruleset_data
                data['ruleset_data'] = {
                    'generation_points_max': ruleset_data.generation_points_max,
                    'generation_points_attributes_max': ruleset_data.generation_points_attributes_max,
                    'attribute_maximum': ruleset_data.attribute_maximum,
                    'xp_total': ruleset_data.xp_total,
                    'xp_current': ruleset_data.xp_current,
                    'level': ruleset_data.level,
                    'birthday': ruleset_data.birthday,
                    'age': ruleset_data.age,
                    'weight': ruleset_data.weight,
                    'height': ruleset_data.height,
                    'gender': ruleset_data.gender,
                    'hair_color': ruleset_data.hair_color,
                    'eye_color': ruleset_data.eye_color,
                    'magic_resistance': ruleset_data.magic_resistance,
                    'life_energy': ruleset_data.life_energy,
                    'endurance': ruleset_data.endurance,
                    'astral_energy': ruleset_data.astral_energy,
                    'karma_energy': ruleset_data.karma_energy,
                    'attack_base': ruleset_data.attack_base,
                    'parade_base': ruleset_data.parade_base,
                    'ranged_combat_base': ruleset_data.ranged_combat_base,
                    'initiative': ruleset_data.initiative,
                    'social_status': ruleset_data.social_status,
                    'guild_membership': ruleset_data.guild_membership,
                    'extended_data': ruleset_data.extended_data,
                }
            
            # Vorteile
            data['advantages'] = []
            for char_adv in character.character_advantages.all():
                data['advantages'].append({
                    'name': char_adv.advantage.name,
                    'level': char_adv.level,
                    'gp_cost': char_adv.gp_cost,
                    'effects': char_adv.total_effects,
                    'custom_modifiers': char_adv.custom_modifiers,
                    'is_valid': char_adv.is_valid,
                    'validation_errors': char_adv.validation_errors,
                })
            
            # Nachteile
            data['disadvantages'] = []
            for char_dis in character.character_disadvantages.all():
                data['disadvantages'].append({
                    'name': char_dis.disadvantage.name,
                    'level': char_dis.level,
                    'gp_gain': char_dis.gp_gain,
                    'effects': char_dis.total_effects,
                    'custom_modifiers': char_dis.custom_modifiers,
                    'is_valid': char_dis.is_valid,
                    'validation_errors': char_dis.validation_errors,
                })
            
            # Generierungspunkte berechnen
            gp_data = CharacterCalculationEngine.calculate_generation_points(data)
            data['generation_points'] = gp_data
            
            return data
            
        except Character.DoesNotExist:
            return None
    
    @staticmethod
    def get_reference_data() -> Dict:
        """
        Holt Referenz-Daten für Charaktererstellung
        
        Returns:
            Dictionary mit Referenz-Daten
        """
        return {
            'races': list(DSARace.objects.filter(is_active=True).values('id', 'name', 'description')),
            'cultures': list(DSACulture.objects.filter(is_active=True).values('id', 'name', 'description')),
            'professions': list(DSAProfession.objects.filter(is_active=True).values('id', 'name', 'category', 'description')),
            'advantages': list(DSAAdvantage.objects.filter(is_active=True).values('id', 'name', 'category', 'gp_cost_base', 'max_levels', 'description')),
            'disadvantages': list(DSADisadvantage.objects.filter(is_active=True).values('id', 'name', 'category', 'gp_gain_base', 'max_levels', 'description')),
        } 