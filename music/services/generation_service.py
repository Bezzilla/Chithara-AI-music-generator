from music.strategies.base import SongGeneratorStrategy
from music.strategies.factory import get_generator_strategy


class SongGenerationContext:

    def __init__(self, strategy: SongGeneratorStrategy = None):
        self._strategy = strategy or get_generator_strategy()

    def set_strategy(self, strategy: SongGeneratorStrategy):
        self._strategy = strategy

    def generate(self, song):
        return self._strategy.generate(song)
