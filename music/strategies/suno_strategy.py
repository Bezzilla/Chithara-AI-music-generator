import time
import threading
import requests
from django.conf import settings
from .base import SongGeneratorStrategy


class SunoSongGeneratorStrategy(SongGeneratorStrategy):

    GENERATE_URL = "https://api.sunoapi.org/api/v1/generate"
    RECORD_URL   = "https://api.sunoapi.org/api/v1/generate/record-info"
    POLL_INTERVAL = 5   # seconds between polls
    MAX_POLLS     = 60  # 5 minutes total

    def generate(self, song) -> 'Song':
        task_id = self._create_task(song)
        song.task_id = task_id
        song.status = "PENDING"
        song.save()

        # Poll in background so the API returns immediately
        thread = threading.Thread(target=self._poll_until_done, args=(song,), daemon=True)
        thread.start()

        return song

    def _headers(self):
        return {
            "Authorization": f"Bearer {settings.SUNO_API_KEY}",
            "Content-Type": "application/json",
        }

    def _create_task(self, song):
        prompt = song.description if song.description else song.title
        payload = {
            "prompt": prompt,
            "style": song.genre.lower().replace("_", " "),
            "title": song.title,
            "customMode": True,
            "instrumental": False,
            "model": "V3_5",
            "callBackUrl": "http://localhost:8000/api/callback/",
        }
        resp = requests.post(self.GENERATE_URL, json=payload, headers=self._headers(), timeout=30)
        print(f"[Suno] POST status: {resp.status_code}")
        print(f"[Suno] POST response: {resp.text}")
        resp.raise_for_status()
        data = resp.json()

        data_field = data.get("data") or {}
        task_id = data_field.get("taskId") or data.get("taskId")
        if not task_id:
            raise ValueError(f"Suno API did not return a taskId. Response: {data}")
        return task_id

    def _poll_until_done(self, song):
        for attempt in range(self.MAX_POLLS):
            time.sleep(self.POLL_INTERVAL)
            try:
                resp = requests.get(
                    self.RECORD_URL,
                    params={"taskId": song.task_id},
                    headers=self._headers(),
                    timeout=30,
                )
                data = resp.json()
                print(f"[Suno] Poll #{attempt + 1} response: {data}")

                data_field = data.get("data") or {}
                task_status = data_field.get("status", "")
                response_field = data_field.get("response") or {}
                clips = response_field.get("sunoData") or []

                print(f"[Suno] task status: {task_status}, clips found: {len(clips)}")

                if task_status in ("FAILED", "ERROR"):
                    song.refresh_from_db()
                    song.status = "FAILED"
                    song.save()
                    print(f"[Suno] Song {song.song_id} failed.")
                    return

                if task_status == "SUCCESS" and clips:
                    clip = clips[0]
                    audio_url = clip.get("audioUrl") or clip.get("streamAudioUrl")
                    song.refresh_from_db()
                    song.audio_url = audio_url
                    song.duration  = float(clip.get("duration") or 0)
                    song.status    = "SUCCESS"
                    song.save()
                    print(f"[Suno] Song {song.song_id} done. audio_url={song.audio_url}")
                    return

            except Exception as e:
                print(f"[Suno] Poll #{attempt + 1} error: {e}")
                continue

        # Timed out
        print(f"[Suno] Song {song.song_id} timed out.")
        song.refresh_from_db()
        song.status = "FAILED"
        song.save()
