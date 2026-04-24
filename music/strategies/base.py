from abc import ABC, abstractmethod


class SongGeneratorStrategy(ABC):

    @abstractmethod
    def generate(self, song) -> 'Song':
        """Generate audio for a Song instance. Returns the updated Song."""
