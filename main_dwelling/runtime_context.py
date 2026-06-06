from dataclasses import dataclass

from main_dwelling import config as dwelling_config


@dataclass(frozen=True)
class MainDwellingRuntimeContext:
    exterior_texture_path: str
    porch_deck_texture_path: str


def get_main_dwelling_runtime_context() -> MainDwellingRuntimeContext:
    """Return runtime paths used by orchestration-time helper calls."""
    return MainDwellingRuntimeContext(
        exterior_texture_path=dwelling_config.get_texture_path(
            "thermal-redwood--shou-sugi-ban--char--brushed--black-rainscreen-117-1235-mm-architextures.jpg"
        ),
        porch_deck_texture_path=dwelling_config.get_texture_path(
            "knotted-timber-staggered-1995-mm-architextures.jpg"
        ),
    )
