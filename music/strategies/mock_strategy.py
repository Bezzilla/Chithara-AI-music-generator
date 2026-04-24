from .base import SongGeneratorStrategy


class MockSongGeneratorStrategy(SongGeneratorStrategy):

    MOCK_AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    MOCK_DURATION = 229.0

    def generate(self, song) -> 'Song':
        song.audio_url = self.MOCK_AUDIO_URL
        song.duration = self.MOCK_DURATION
        song.status = "SUCCESS"
        song.save()
        return song
