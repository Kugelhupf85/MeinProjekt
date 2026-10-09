"""
Character Calculation Engine for DSA 4.1
Handles automatic calculations of derived values and validation
"""

from typing import Dict, List, Tuple, Optional
from django.core.exceptions import ValidationError


class CharacterCalculationEngine:
    """Engine für automatische Berechnungen von DSA 4.1 Charakterwerten"""
    
    @staticmethod
    def calculate_derived_values(core_attributes: Dict, race_modifiers: Optional[Dict] = None, 
                                advantages: Optional[List] = None) -> Dict:
        """
        Berechnet abgeleitete Werte basierend auf Grundeigenschaften
        
        Args:
            core_attributes: Dictionary mit den 8 Grundattributen
            race_modifiers: Optional race modifiers
            advantages: Optional list of character advantages
            
        Returns:
            Dictionary mit abgeleiteten Werten
        """
        if not core_attributes:
            return {}
        
        # Basis-Berechnungen nach DSA 4.1 Regeln
        derived = {
            'LE': (core_attributes.get('KO', 0) * 2) + core_attributes.get('KK', 0) + 6,  # Lebensenergie
            'AU': (core_attributes.get('KO', 0) * 2) + core_attributes.get('GE', 0) + 6,  # Ausdauer
            'MR': (core_attributes.get('MU', 0) + core_attributes.get('KL', 0) + core_attributes.get('KO', 0)) // 5,  # Magieresistenz
            'INI': (core_attributes.get('MU', 0) + core_attributes.get('GE', 0)) // 2,     # Initiative
            'AT': (core_attributes.get('MU', 0) + core_attributes.get('GE', 0) + core_attributes.get('KK', 0)) // 5,  # Attacke-Basis
            'PA': (core_attributes.get('IN', 0) + core_attributes.get('GE', 0) + core_attributes.get('KK', 0)) // 5,  # Parade-Basis
            'FK': (core_attributes.get('IN', 0) + core_attributes.get('FF', 0) + core_attributes.get('KK', 0)) // 5,  # Fernkampf-Basis
            'GS': 8  # Standard Geschwindigkeit
        }
        
        # Rassen-Modifikatoren anwenden
        if race_modifiers:
            for key, modifier in race_modifiers.items():
                if key in derived:
                    derived[key] += modifier
        
        # Vorteile/Nachteile anwenden
        if advantages:
            for advantage in advantages:
                effects = advantage.get('effects', {})
                if 'life_points_bonus' in effects:
                    derived['LE'] += effects['life_points_bonus']
                if 'life_points_penalty' in effects:
                    derived['LE'] += effects['life_points_penalty']  # penalty is negative
        
        return derived
    
    @staticmethod
    def validate_character_rules(character_data: Dict) -> List[str]:
        """
        Validiert DSA 4.1 Charaktererstellungsregeln
        
        Args:
            character_data: Dictionary mit Charakterdaten
            
        Returns:
            List of validation error messages
        """
        errors = []
        attrs = character_data.get('core_attributes', {})
        
        # Attributs-Maximum prüfen
        max_attr = character_data.get('generation_data', {}).get('attribute_maximum', 14)
        for attr, value in attrs.items():
            if value > max_attr:
                errors.append(f"{attr} ({value}) überschreitet Maximum ({max_attr})")
            if value < 8:
                errors.append(f"{attr} ({value}) ist unter Minimum (8)")
        
        # Generierungspunkte prüfen
        total_gp_used = sum(attrs.values()) - 64  # 8 Attribute * 8 Basis-Punkte
        max_gp = character_data.get('generation_data', {}).get('generation_points_max', 110)
        
        if total_gp_used > max_gp:
            errors.append(f"Generierungspunkte überschritten: {total_gp_used}/{max_gp}")
        
        # Vorteile/Nachteile prüfen
        advantages = character_data.get('advantages', [])
        disadvantages = character_data.get('disadvantages', [])
        
        # Inkompatible Vorteile prüfen
        advantage_names = [adv.get('name') for adv in advantages]
        for advantage in advantages:
            incompatible = advantage.get('incompatible_with', [])
            for inc in incompatible:
                if inc in advantage_names:
                    errors.append(f"Vorteil '{advantage.get('name')}' inkompatibel mit '{inc}'")
        
        # Inkompatible Nachteile prüfen
        disadvantage_names = [dis.get('name') for dis in disadvantages]
        for disadvantage in disadvantages:
            incompatible = disadvantage.get('incompatible_with', [])
            for inc in incompatible:
                if inc in disadvantage_names:
                    errors.append(f"Nachteil '{disadvantage.get('name')}' inkompatibel mit '{inc}'")
        
        return errors
    
    @staticmethod
    def calculate_generation_points(character_data: Dict) -> Dict:
        """
        Berechnet Generierungspunkte-Verbrauch
        
        Args:
            character_data: Dictionary mit Charakterdaten
            
        Returns:
            Dictionary mit GP-Informationen
        """
        attrs = character_data.get('core_attributes', {})
        advantages = character_data.get('advantages', [])
        disadvantages = character_data.get('disadvantages', [])
        
        # Attributs-Punkte
        base_attr_points = 64  # 8 Attribute * 8
        total_attr_points = sum(attrs.values())
        attr_gp_used = total_attr_points - base_attr_points
        
        # Vorteile-Punkte
        advantage_gp_used = 0
        for advantage in advantages:
            level = advantage.get('level', 1)
            gp_cost = advantage.get('gp_cost_base', 0) + (advantage.get('gp_cost_per_level', 0) * (level - 1))
            advantage_gp_used += gp_cost
        
        # Nachteile-Punkte (gewonnen)
        disadvantage_gp_gained = 0
        for disadvantage in disadvantages:
            level = disadvantage.get('level', 1)
            gp_gain = disadvantage.get('gp_gain_base', 0) + (disadvantage.get('gp_gain_per_level', 0) * (level - 1))
            disadvantage_gp_gained += gp_gain
        
        total_gp_used = attr_gp_used + advantage_gp_used - disadvantage_gp_gained
        
        return {
            'attribute_points_used': attr_gp_used,
            'advantage_points_used': advantage_gp_used,
            'disadvantage_points_gained': disadvantage_gp_gained,
            'total_points_used': total_gp_used,
            'points_remaining': 110 - total_gp_used  # Standard DSA 4.1
        }
    
    @staticmethod
    def apply_race_modifiers(base_attributes: Dict, race_modifiers: Dict) -> Dict:
        """
        Wendet Rassen-Modifikatoren auf Basis-Attribute an
        
        Args:
            base_attributes: Basis-Attribute
            race_modifiers: Rassen-Modifikatoren
            
        Returns:
            Modifizierte Attribute
        """
        modified_attributes = base_attributes.copy()
        
        for attr, modifier in race_modifiers.items():
            if attr in modified_attributes:
                modified_attributes[attr] += modifier
        
        return modified_attributes
    
    @staticmethod
    def apply_culture_bonuses(talents: Dict, culture_bonuses: Dict) -> Dict:
        """
        Wendet Kultur-Boni auf Talente an
        
        Args:
            talents: Charakter-Talente
            culture_bonuses: Kultur-Boni
            
        Returns:
            Modifizierte Talente
        """
        modified_talents = talents.copy()
        
        for talent, bonus in culture_bonuses.items():
            if talent in modified_talents:
                modified_talents[talent] += bonus
        
        return modified_talents
    
    @staticmethod
    def validate_profession_requirements(attributes: Dict, profession_requirements: Dict) -> Tuple[bool, str]:
        """
        Validiert Profession-Anforderungen
        
        Args:
            attributes: Charakter-Attribute
            profession_requirements: Profession-Anforderungen
            
        Returns:
            Tuple (is_valid, error_message)
        """
        for attr, required_value in profession_requirements.items():
            if attributes.get(attr, 0) < required_value:
                return False, f"Attribut {attr} ({attributes.get(attr, 0)}) unter Anforderung ({required_value})"
        
        return True, "Alle Anforderungen erfüllt"
    
    @staticmethod
    def calculate_talent_check(talent_value: int, governing_attributes: List[int], 
                              difficulty: str = 'B') -> Dict:
        """
        Berechnet Talent-Probe
        
        Args:
            talent_value: Talent-Wert
            governing_attributes: Regierende Attribute
            difficulty: Schwierigkeit (A-E)
            
        Returns:
            Dictionary mit Probe-Informationen
        """
        # Schwierigkeitsfaktoren nach DSA 4.1
        difficulty_factors = {
            'A': 1,
            'B': 2,
            'C': 3,
            'D': 4,
            'E': 5
        }
        
        factor = difficulty_factors.get(difficulty, 2)
        
        # Durchschnitt der regierenden Attribute
        avg_attributes = sum(governing_attributes) / len(governing_attributes)
        
        # Probe-Wert berechnen
        probe_value = talent_value + avg_attributes
        
        return {
            'talent_value': talent_value,
            'avg_attributes': avg_attributes,
            'difficulty_factor': factor,
            'probe_value': probe_value,
            'difficulty': difficulty
        } 