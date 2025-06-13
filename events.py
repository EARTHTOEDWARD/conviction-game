# events.py - Random event deck for Conviction v2.0

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from models import Bloc
    from conviction import ConvictionGame


@dataclass
class Event:
    name: str
    description: str
    effect: Callable[["Bloc", "ConvictionGame"], None]


def pandemic_resurgence(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Pandemic disrupts technology infrastructure."""
    if bloc.tech_level > 0:
        bloc.tech_level = max(0, bloc.tech_level - 1)
        bloc.cohesion = max(0, bloc.cohesion - 1)
        game.last_results.append(
            f"{bloc.name}: Pandemic resurgence - tech level -1, cohesion -1"
        )
    else:
        bloc.gdp_tokens = max(0, bloc.gdp_tokens - 2)
        game.last_results.append(f"{bloc.name}: Pandemic economic impact - GDP -2")


def cyber_breakthrough(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Major cybersecurity advancement."""
    bloc.tech_level = min(3, bloc.tech_level + 1)
    bloc.trust_score = min(5, bloc.trust_score + 1)
    game.last_results.append(
        f"{bloc.name}: Cyber breakthrough - tech level +1, trust +1"
    )


def trade_war_escalation(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Global trade tensions increase regulatory burden."""
    bloc.regulatory_drag = min(10, bloc.regulatory_drag + 2)
    bloc.gdp_tokens = max(0, bloc.gdp_tokens - 1)
    game.last_results.append(
        f"{bloc.name}: Trade war impact - regulatory drag +2, GDP -1"
    )


def cultural_renaissance(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Cultural movement boosts soft power."""
    bloc.cultural_influence = min(5, bloc.cultural_influence + 2)
    bloc.cohesion = min(5, bloc.cohesion + 1)
    game.last_results.append(
        f"{bloc.name}: Cultural renaissance - cultural influence +2, cohesion +1"
    )


def economic_summit_success(bloc: "Bloc", game: "ConvictionGame") -> None:
    """International cooperation reduces friction."""
    bloc.regulatory_drag = max(0, bloc.regulatory_drag - 1)
    bloc.trust_score = min(5, bloc.trust_score + 1)
    bloc.gdp_tokens = min(20, bloc.gdp_tokens + 3)
    game.last_results.append(
        f"{bloc.name}: Economic summit success - drag -1, trust +1, GDP +3"
    )


def infrastructure_crisis(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Critical infrastructure failure."""
    bloc.economic_development = max(1, bloc.economic_development - 1)
    bloc.military_posture = max(0, bloc.military_posture - 1)
    game.last_results.append(
        f"{bloc.name}: Infrastructure crisis - economic development -1, military -1"
    )


def diplomatic_scandal(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Major diplomatic incident damages trust."""
    bloc.trust_score = max(0, bloc.trust_score - 2)
    bloc.cultural_influence = max(0, bloc.cultural_influence - 1)
    # Break random alliance if any exist
    if bloc.alliances:
        ally = random.choice(list(bloc.alliances))
        game.break_alliance(bloc.name, ally)
    game.last_results.append(
        f"{bloc.name}: Diplomatic scandal - trust -2, cultural influence -1"
    )


def technological_espionage(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Espionage activities discovered."""
    bloc.trust_score = max(0, bloc.trust_score - 1)
    bloc.regulatory_drag = min(10, bloc.regulatory_drag + 1)
    # But gain some tech advantage
    bloc.tech_level = min(3, bloc.tech_level + 1)
    game.last_results.append(
        f"{bloc.name}: Tech espionage exposed - trust -1, drag +1, tech +1"
    )


def climate_cooperation(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Climate accords boost international standing."""
    bloc.cultural_influence = min(5, bloc.cultural_influence + 1)
    bloc.trust_score = min(5, bloc.trust_score + 1)
    bloc.economic_development = min(5, bloc.economic_development + 1)
    game.last_results.append(
        f"{bloc.name}: Climate cooperation - cultural +1, trust +1, development +1"
    )


def financial_market_volatility(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Market turbulence affects resources."""
    if bloc.gdp_tokens > 5:
        bloc.gdp_tokens = max(0, bloc.gdp_tokens - 3)
        game.last_results.append(f"{bloc.name}: Market volatility - GDP -3")
    else:
        bloc.gdp_tokens = min(20, bloc.gdp_tokens + 2)
        game.last_results.append(f"{bloc.name}: Market correction - GDP +2")


def social_media_influence(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Social media campaign affects public opinion."""
    if random.random() < 0.5:
        bloc.cultural_influence = min(5, bloc.cultural_influence + 1)
        bloc.cohesion = min(5, bloc.cohesion + 1)
        game.last_results.append(
            f"{bloc.name}: Viral social campaign - cultural +1, cohesion +1"
        )
    else:
        bloc.cohesion = max(0, bloc.cohesion - 1)
        bloc.trust_score = max(0, bloc.trust_score - 1)
        game.last_results.append(
            f"{bloc.name}: Social media backlash - cohesion -1, trust -1"
        )


def military_modernization(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Military technology advancement."""
    bloc.military_posture = min(5, bloc.military_posture + 1)
    bloc.tech_level = min(3, bloc.tech_level + 1)
    bloc.gdp_tokens = max(0, bloc.gdp_tokens - 2)  # Expensive
    game.last_results.append(
        f"{bloc.name}: Military modernization - military +1, tech +1, GDP -2"
    )


# Global events that affect all blocs
def global_economic_boom(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Global economic growth benefits everyone."""
    bloc.gdp_tokens = min(20, bloc.gdp_tokens + 2)
    bloc.trust_score = min(5, bloc.trust_score + 1)


def global_recession(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Global economic downturn hurts everyone."""
    bloc.gdp_tokens = max(0, bloc.gdp_tokens - 2)
    bloc.regulatory_drag = min(10, bloc.regulatory_drag + 1)


def global_ai_breakthrough(bloc: "Bloc", game: "ConvictionGame") -> None:
    """Major AI advancement affects all blocs."""
    bloc.tech_level = min(3, bloc.tech_level + 1)
    bloc.regulatory_drag = min(10, bloc.regulatory_drag + 1)  # Disruptive


EVENT_DECK = [
    Event(
        "Pandemic Resurgence",
        "Health crisis disrupts technology and social cohesion",
        pandemic_resurgence,
    ),
    Event(
        "Cyber Security Breakthrough",
        "Major advancement in cybersecurity capabilities",
        cyber_breakthrough,
    ),
    Event(
        "Trade War Escalation",
        "International trade tensions increase regulatory burden",
        trade_war_escalation,
    ),
    Event(
        "Cultural Renaissance",
        "Cultural movement enhances soft power and unity",
        cultural_renaissance,
    ),
    Event(
        "Economic Summit Success",
        "International cooperation reduces friction and boosts economy",
        economic_summit_success,
    ),
    Event(
        "Infrastructure Crisis",
        "Critical infrastructure failure impacts development",
        infrastructure_crisis,
    ),
    Event(
        "Diplomatic Scandal",
        "Major diplomatic incident damages international trust",
        diplomatic_scandal,
    ),
    Event(
        "Technological Espionage",
        "Espionage activities discovered, mixed consequences",
        technological_espionage,
    ),
    Event(
        "Climate Cooperation",
        "Climate accords boost international standing",
        climate_cooperation,
    ),
    Event(
        "Financial Market Volatility",
        "Market turbulence with unpredictable effects",
        financial_market_volatility,
    ),
    Event(
        "Social Media Influence",
        "Social media campaign with uncertain outcomes",
        social_media_influence,
    ),
    Event(
        "Military Modernization",
        "Military technology advancement program",
        military_modernization,
    ),
]

# Global events that affect all players
GLOBAL_EVENT_DECK = [
    Event(
        "Global Economic Boom",
        "Worldwide economic growth benefits all blocs",
        global_economic_boom,
    ),
    Event(
        "Global Recession",
        "Economic downturn affects all blocs negatively",
        global_recession,
    ),
    Event(
        "Global AI Breakthrough",
        "Major AI advancement disrupts all blocs",
        global_ai_breakthrough,
    ),
]


def draw_random_event() -> Event:
    """Draw a random event from the main deck."""
    return random.choice(EVENT_DECK)


def draw_global_event() -> Event:
    """Draw a random global event that affects all blocs."""
    return random.choice(GLOBAL_EVENT_DECK)


def should_trigger_global_event() -> bool:
    """Determine if a global event should trigger this turn (20% chance)."""
    return random.random() < 0.2
