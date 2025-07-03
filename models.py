# models.py  (new file — helps keep things tidy)
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple


class TechLevel(Enum):
    AI_UTILITY = 1
    AUTONOMOUS_SYSTEMS = 2
    GENERAL_AI_NEXUS = 3


class CardType(Enum):
    # Original cards
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
    
    # New geopolitical cards
    FINANCIAL_SANCTIONS = auto()
    SECONDARY_SANCTIONS = auto()
    DUMPING_PRODUCTS = auto()
    ANTI_DUMPING = auto()
    TECH_TRANSFER = auto()
    EXPORT_CONTROLS = auto()
    DEBT_TRAP = auto()
    RARE_EARTH_EMBARGO = auto()
    REGULATORY_CLAMPDOWN = auto()
    CARBON_TARIFF = auto()


class Domain(Enum):
    """Policy domains that blocs can specialize in."""
    CYBER = "Cyber"
    TRADE = "Trade"
    FINANCE = "Finance"
    REGULATION = "Regulation"
    MILITARY = "Military"
    INFLUENCE = "Influence"


class Target(Enum):
    """Possible targets for policy cards."""
    USA = "USA"
    EU = "EU"
    CHINA = "China"
    BOTH = "Both"  # Target all other blocs


@dataclass
class PolicyCard:
    """Enhanced policy card with domain and targeting."""
    card_type: CardType
    domain: Domain
    base_cost: int  # GDP cost for single target
    

@dataclass 
class Move:
    """A player's move for the turn: card + targets."""
    card: PolicyCard
    targets: List[Target]
    

# Signature domains - each bloc gets cost discounts here
SIGNATURE_DOMAIN = {
    "USA": Domain.FINANCE,
    "EU": Domain.REGULATION,
    "China": Domain.TRADE,
}

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
    # New cards
    CardType.FINANCIAL_SANCTIONS: CardType.TRADE_DEAL,
    CardType.SECONDARY_SANCTIONS: CardType.LOBBYING_BLITZ,
    CardType.DUMPING_PRODUCTS: CardType.ANTI_DUMPING,
    CardType.ANTI_DUMPING: CardType.DUMPING_PRODUCTS,
    CardType.TECH_TRANSFER: CardType.EXPORT_CONTROLS,
    CardType.EXPORT_CONTROLS: CardType.TECH_TRANSFER,
    CardType.DEBT_TRAP: CardType.AID_RECONSTRUCTION,
    CardType.RARE_EARTH_EMBARGO: CardType.TRADE_DEAL,
    CardType.REGULATORY_CLAMPDOWN: CardType.LOBBYING_BLITZ,
    CardType.CARBON_TARIFF: CardType.TRADE_DEAL,
}

# Policy cards with full details
POLICY_CARDS = {
    CardType.CYBER_ESPIONAGE: PolicyCard(
        card_type=CardType.CYBER_ESPIONAGE,
        domain=Domain.CYBER,
        base_cost=3
    ),
    CardType.TARIFF_HIKE: PolicyCard(
        card_type=CardType.TARIFF_HIKE,
        domain=Domain.TRADE,
        base_cost=4
    ),
    CardType.PROXY_ARMS: PolicyCard(
        card_type=CardType.PROXY_ARMS,
        domain=Domain.MILITARY,
        base_cost=5
    ),
    CardType.STANDARDS_PUSH: PolicyCard(
        card_type=CardType.STANDARDS_PUSH,
        domain=Domain.REGULATION,
        base_cost=4
    ),
    CardType.DISINFORMATION: PolicyCard(
        card_type=CardType.DISINFORMATION,
        domain=Domain.INFLUENCE,
        base_cost=3
    ),
    CardType.COUNTER_INTEL: PolicyCard(
        card_type=CardType.COUNTER_INTEL,
        domain=Domain.CYBER,
        base_cost=3
    ),
    CardType.TRADE_DEAL: PolicyCard(
        card_type=CardType.TRADE_DEAL,
        domain=Domain.TRADE,
        base_cost=3
    ),
    CardType.AID_RECONSTRUCTION: PolicyCard(
        card_type=CardType.AID_RECONSTRUCTION,
        domain=Domain.INFLUENCE,
        base_cost=4
    ),
    CardType.LOBBYING_BLITZ: PolicyCard(
        card_type=CardType.LOBBYING_BLITZ,
        domain=Domain.INFLUENCE,
        base_cost=3
    ),
    CardType.CONTENT_MODERATION: PolicyCard(
        card_type=CardType.CONTENT_MODERATION,
        domain=Domain.REGULATION,
        base_cost=2
    ),
    # New cards
    CardType.FINANCIAL_SANCTIONS: PolicyCard(
        card_type=CardType.FINANCIAL_SANCTIONS,
        domain=Domain.FINANCE,
        base_cost=5
    ),
    CardType.SECONDARY_SANCTIONS: PolicyCard(
        card_type=CardType.SECONDARY_SANCTIONS,
        domain=Domain.FINANCE,
        base_cost=3
    ),
    CardType.DUMPING_PRODUCTS: PolicyCard(
        card_type=CardType.DUMPING_PRODUCTS,
        domain=Domain.TRADE,
        base_cost=4
    ),
    CardType.ANTI_DUMPING: PolicyCard(
        card_type=CardType.ANTI_DUMPING,
        domain=Domain.TRADE,
        base_cost=2
    ),
    CardType.TECH_TRANSFER: PolicyCard(
        card_type=CardType.TECH_TRANSFER,
        domain=Domain.CYBER,
        base_cost=6
    ),
    CardType.EXPORT_CONTROLS: PolicyCard(
        card_type=CardType.EXPORT_CONTROLS,
        domain=Domain.REGULATION,
        base_cost=4
    ),
    CardType.DEBT_TRAP: PolicyCard(
        card_type=CardType.DEBT_TRAP,
        domain=Domain.FINANCE,
        base_cost=5
    ),
    CardType.RARE_EARTH_EMBARGO: PolicyCard(
        card_type=CardType.RARE_EARTH_EMBARGO,
        domain=Domain.TRADE,
        base_cost=4
    ),
    CardType.REGULATORY_CLAMPDOWN: PolicyCard(
        card_type=CardType.REGULATORY_CLAMPDOWN,
        domain=Domain.REGULATION,
        base_cost=4
    ),
    CardType.CARBON_TARIFF: PolicyCard(
        card_type=CardType.CARBON_TARIFF,
        domain=Domain.REGULATION,
        base_cost=3
    ),
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
    # New cards
    CardType.FINANCIAL_SANCTIONS: {
        "description": "Freeze opponent GDP and reduce economic development",
        "effect": "financial_sanctions",
    },
    CardType.SECONDARY_SANCTIONS: {
        "description": "Force allies to join sanctions or pay penalty",
        "effect": "secondary_sanctions",
    },
    CardType.DUMPING_PRODUCTS: {
        "description": "Damage opponent's economic development",
        "effect": "dumping",
    },
    CardType.ANTI_DUMPING: {
        "description": "Protect economy and gain GDP",
        "effect": "anti_dumping",
    },
    CardType.TECH_TRANSFER: {
        "description": "Share tech with ally, both gain tech progress",
        "effect": "tech_transfer",
    },
    CardType.EXPORT_CONTROLS: {
        "description": "Block opponent tech advancement",
        "effect": "export_controls",
    },
    CardType.DEBT_TRAP: {
        "description": "Gain influence over opponent territories",
        "effect": "debt_trap",
    },
    CardType.RARE_EARTH_EMBARGO: {
        "description": "Cripple opponent's tech and military production",
        "effect": "rare_earth_embargo",
    },
    CardType.REGULATORY_CLAMPDOWN: {
        "description": "Massively increase opponent's regulatory drag",
        "effect": "regulatory_clampdown",
    },
    CardType.CARBON_TARIFF: {
        "description": "Tax opponent's GDP unless they go green",
        "effect": "carbon_tariff",
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
    chosen_targets: List[Target] = field(default_factory=list)
    
    # Lever track (0-3) for signature domain
    lever_level: int = 0

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
    def get_signature_domain(self) -> Optional[Domain]:
        """Get this bloc's signature domain for cost discounts."""
        return SIGNATURE_DOMAIN.get(self.name)
        
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
