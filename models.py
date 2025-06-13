# models.py  (new file — helps keep things tidy)
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set


class TechLevel(Enum):
    AI_UTILITY = 1
    AUTONOMOUS_SYSTEMS = 2
    GENERAL_AI_NEXUS = 3


class CardType(Enum):
    CYBER_ESPIONAGE = auto()
    TARIFF_HIKE = auto()
    PROXY_ARMS = auto()
    STANDARDS_PUSH = auto()
    DISINFORMATION = auto()
    COUNTER_INTEL = auto()
    TRADE_DEAL = auto()
    AID_RECONSTRUCTION = auto()
    LOBBYING_BLITZ = auto()
    CONTENT_MODERATION = auto()


# Card counter relationships (rock-paper-scissors style)
COUNTER_TABLE = {
    CardType.CYBER_ESPIONAGE: CardType.COUNTER_INTEL,
    CardType.TARIFF_HIKE: CardType.TRADE_DEAL,
    CardType.PROXY_ARMS: CardType.AID_RECONSTRUCTION,
    CardType.STANDARDS_PUSH: CardType.LOBBYING_BLITZ,
    CardType.DISINFORMATION: CardType.CONTENT_MODERATION,
    CardType.COUNTER_INTEL: CardType.CYBER_ESPIONAGE,
    CardType.TRADE_DEAL: CardType.TARIFF_HIKE,
    CardType.AID_RECONSTRUCTION: CardType.PROXY_ARMS,
    CardType.LOBBYING_BLITZ: CardType.STANDARDS_PUSH,
    CardType.CONTENT_MODERATION: CardType.DISINFORMATION,
}

# Card effects when successful (not countered)
CARD_EFFECTS = {
    CardType.CYBER_ESPIONAGE: {
        "description": "Steal tech progress from opponent",
        "effect": "steal_tech",
    },
    CardType.TARIFF_HIKE: {
        "description": "Reduce opponent GDP generation",
        "effect": "reduce_gdp",
    },
    CardType.PROXY_ARMS: {
        "description": "Boost military posture vs opponent",
        "effect": "boost_military",
    },
    CardType.STANDARDS_PUSH: {
        "description": "Increase regulatory drag on opponents",
        "effect": "increase_drag",
    },
    CardType.DISINFORMATION: {
        "description": "Reduce opponent cohesion and trust",
        "effect": "reduce_cohesion",
    },
    CardType.COUNTER_INTEL: {
        "description": "Boost trust score and reduce drag",
        "effect": "boost_trust",
    },
    CardType.TRADE_DEAL: {
        "description": "Boost GDP generation and cultural influence",
        "effect": "boost_economy",
    },
    CardType.AID_RECONSTRUCTION: {
        "description": "Gain satellite influence and cohesion",
        "effect": "boost_influence",
    },
    CardType.LOBBYING_BLITZ: {
        "description": "Reduce regulatory drag and boost cultural influence",
        "effect": "boost_lobbying",
    },
    CardType.CONTENT_MODERATION: {
        "description": "Boost cohesion and cultural influence",
        "effect": "boost_moderation",
    },
}


@dataclass
class ProxyRegion:
    name: str
    controlling_bloc: Optional[str] = None  # "USA" / "EU" / "China"
    influence_die: int = 3  # Starts neutral (1-6; 1-2 USA, 3-4 Neutral, 5-6 rival)


@dataclass
class Bloc:
    """A major power in the game (USA, EU, China)."""

    name: str
    satellites: List[str] = field(default_factory=list)

    # Economic & resource pool
    gdp_tokens: int = 5

    # NEW: Budgeting system
    current_budget: Dict[str, int] = field(
        default_factory=lambda: {
            "military": 0,
            "technology": 0,
            "culture": 0,
            "infrastructure": 0,
            "diplomacy": 0,
        }
    )

    # Economic infrastructure
    economic_development: int = 1  # multiplier for GDP generation

    # Card selection for this turn
    chosen_card: Optional["CardType"] = None

    # Domain scores (0–5 scale unless noted)
    tech_level: int = 0
    military_posture: int = 0
    cultural_influence: int = 0
    cohesion: int = 5  # replaces conviction_score

    # Friction / bureaucratic drag
    regulatory_drag: int = 0  # replaces friction_score
    trust_score: int = 5

    # Diplomacy graph
    alliances: Set[str] = field(default_factory=set)

    colour: str = ""  # useful for ASCII map

    # ---------- helpers ----------
    def effective_drag(self) -> int:
        """Drag after trust is netted out."""
        return max(self.regulatory_drag - self.trust_score, 0)

    def tech_bonus(self) -> int:
        return {0: 0, 1: 1, 2: 2, 3: 5}[self.tech_level]  # tweak later

    def generate_gdp_income(self, controlled_territories: int = 0) -> int:
        """Calculate GDP income for this turn based on economic development and territories."""
        base_income = 3  # Base GDP generation
        territory_income = (
            controlled_territories * 2
        )  # Income from controlled supply centers
        development_bonus = (
            self.economic_development * 1
        )  # Bonus from economic development
        cohesion_bonus = max(0, (self.cohesion - 3))  # Bonus for high cohesion

        total_income = (
            base_income + territory_income + development_bonus + cohesion_bonus
        )

        # Regulatory drag reduces income efficiency
        drag_penalty = self.effective_drag()
        net_income = max(
            1, total_income - drag_penalty
        )  # Always generate at least 1 GDP

        return net_income

    def allocate_budget(self, allocations: Dict[str, int]) -> bool:
        """Allocate available GDP tokens to different budget categories."""
        total_allocated = sum(allocations.values())

        if total_allocated > self.gdp_tokens:
            return False  # Can't spend more than available

        # Reset current budget and apply allocations
        self.current_budget = {
            "military": allocations.get("military", 0),
            "technology": allocations.get("technology", 0),
            "culture": allocations.get("culture", 0),
            "infrastructure": allocations.get("infrastructure", 0),
            "diplomacy": allocations.get("diplomacy", 0),
        }

        # Spend the allocated GDP tokens
        self.gdp_tokens -= total_allocated

        return True

    def spend_budget(self) -> List[str]:
        """Apply budget spending effects and return list of results."""
        results = []

        # Military spending
        if self.current_budget["military"] > 0:
            military_gain = min(
                2, self.current_budget["military"]
            )  # Max 2 points per turn
            old_military = self.military_posture
            self.military_posture = min(5, self.military_posture + military_gain)
            actual_gain = self.military_posture - old_military
            if actual_gain > 0:
                results.append(f"Military spending: +{actual_gain} Military Posture")

        # Technology spending
        if self.current_budget["technology"] > 0:
            tech_progress = self.current_budget["technology"]
            # Technology advancement requires more investment at higher levels
            threshold = 3 + self.tech_level * 2
            if tech_progress >= threshold and self.tech_level < 3:
                self.tech_level += 1
                self.regulatory_drag += 1  # Tech advancement causes friction
                results.append(
                    f"Technology breakthrough: Advanced to Tech Level {self.tech_level}!"
                )
                results.append("Growing pains: +1 Regulatory Drag")
            else:
                results.append(
                    f"Technology research: {tech_progress}/{threshold} progress toward next level"
                )

        # Cultural spending
        if self.current_budget["culture"] > 0:
            culture_gain = min(2, self.current_budget["culture"])
            old_culture = self.cultural_influence
            self.cultural_influence = min(5, self.cultural_influence + culture_gain)
            actual_gain = self.cultural_influence - old_culture
            if actual_gain > 0:
                results.append(f"Cultural programs: +{actual_gain} Cultural Influence")

        # Infrastructure spending
        if self.current_budget["infrastructure"] > 0:
            infra_spending = self.current_budget["infrastructure"]
            if infra_spending >= 3:  # Major infrastructure investment
                self.economic_development += 1
                self.regulatory_drag = max(
                    0, self.regulatory_drag - 1
                )  # Better infrastructure reduces drag
                results.append(
                    "Infrastructure development: +1 Economic Development, -1 Regulatory Drag"
                )
            elif infra_spending >= 2:  # Moderate investment
                self.cohesion = min(5, self.cohesion + 1)
                results.append("Infrastructure maintenance: +1 Cohesion")
            else:  # Minor investment
                results.append("Minor infrastructure repairs: No immediate effect")

        # Diplomatic spending
        if self.current_budget["diplomacy"] > 0:
            diplo_gain = min(2, self.current_budget["diplomacy"])
            old_trust = self.trust_score
            self.trust_score = min(5, self.trust_score + diplo_gain)
            actual_gain = self.trust_score - old_trust
            if actual_gain > 0:
                results.append(f"Diplomatic initiatives: +{actual_gain} Trust Score")

        # Clear budget after spending
        self.current_budget = {k: 0 for k in self.current_budget.keys()}

        return results

    def bloc_vp(self) -> int:
        """Calculate victory points for this bloc using the new scoring system."""
        # Base victory points from core attributes
        vp = 0

        # GDP tokens contribute to victory
        vp += self.gdp_tokens

        # Tech level provides exponential advantage
        vp += self.tech_bonus()

        # Military posture provides direct victory points
        vp += self.military_posture * 2

        # Cultural influence provides victory points
        vp += self.cultural_influence

        # Cohesion provides stability bonus
        vp += self.cohesion

        # Satellite states provide victory points
        vp += len(self.satellites) * 3

        # Alliance network provides diplomatic victory points
        vp += len(self.alliances) * 2

        # Penalty for high regulatory drag
        vp -= self.effective_drag()

        return max(0, vp)  # Victory points can't be negative

    def to_dict(self):
        return {
            "name": self.name,
            "satellites": self.satellites,
            "gdp_tokens": self.gdp_tokens,
            "current_budget": self.current_budget,
            "economic_development": self.economic_development,
            "chosen_card": self.chosen_card.name if self.chosen_card else None,
            "tech_level": self.tech_level,
            "military_posture": self.military_posture,
            "scores": {
                "cohesion": self.cohesion,
                "cultural_influence": self.cultural_influence,
                "regulatory_drag": self.regulatory_drag,
                "trust": self.trust_score,
                "effective_drag": self.effective_drag(),
            },
            "alliances": list(self.alliances),
            "victory_points": self.bloc_vp(),
        }
