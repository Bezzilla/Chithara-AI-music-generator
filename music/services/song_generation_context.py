from django.conf import settings
from music.strategies.song_generator_strategy import SongGeneratorStrategy


class SongGenerationContext:

    def __init__(self, strategy: SongGeneratorStrategy = None):
        if strategy is not None:
            self._strategy = strategy
        else:
            self._strategy = self._select_strategy()

    def _select_strategy(self) -> SongGeneratorStrategy:
        name = getattr(settings, "GENERATOR_STRATEGY", "mock").lower()
        if name == "suno":
            from music.strategies.suno_strategy import SunoSongGeneratorStrategy
            return SunoSongGeneratorStrategy()
        from music.strategies.mock_strategy import MockSongGeneratorStrategy
        return MockSongGeneratorStrategy()

    def set_strategy(self, strategy: SongGeneratorStrategy):
        self._strategy = strategy

    def generate(self, song):
        return self._strategy.generate(song)
