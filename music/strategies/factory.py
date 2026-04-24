from django.conf import settings
from .base import SongGeneratorStrategy


def get_generator_strategy() -> SongGeneratorStrategy:
    strategy_name = getattr(settings, "GENERATOR_STRATEGY", "mock").lower()
    print(f"[Factory] GENERATOR_STRATEGY={repr(strategy_name)}")
    if strategy_name == "suno":
        from .suno_strategy import SunoSongGeneratorStrategy
        return SunoSongGeneratorStrategy()
    from .mock_strategy import MockSongGeneratorStrategy
    return MockSongGeneratorStrategy()
