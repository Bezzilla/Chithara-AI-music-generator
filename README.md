# Chithara AI Music Generator

Chithara is a web-based AI music generator that allows users to create original music tracks by specifying a title, occasion, genre, and description.

---

## Tech Stack

- **Backend:** Django 5.2 (Python)
- **Database:** SQLite (development)
- **AI Generation:** Suno API (via sunoapi.org)

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/Bezzilla/Chithara-AI-music-generator.git
cd Chithara-AI-music-generator
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```
Edit `.env` and fill in the values (see **Strategy Configuration** below).

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Start the server**
```bash
python manage.py runserver
```

**7. Open** `http://127.0.0.1:8000/` in your browser — you will land on the login page.

---

## Strategy Pattern 

Song generation uses the **Strategy design pattern**. The active strategy is selected via the `GENERATOR_STRATEGY` environment variable — no code changes required to switch.


### Mock mode (no API key required)

In `.env`:
```
GENERATOR_STRATEGY=mock
```

The mock strategy instantly marks the song as `SUCCESS` and returns a real hosted MP3. Useful for UI development and testing without spending API credits.

### Suno mode (real AI generation)

In `.env`:
```
GENERATOR_STRATEGY=suno
SUNO_API_KEY=your-suno-api-key-here
```

Get an API key from [sunoapi.org](https://sunoapi.org).


---

## Project Structure

```
Chithara-AI-music-generator/
├── chithara/
│   ├── settings.py
│   └── urls.py
├── music/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   ├── strategies/
│   │   ├── base.py              # Abstract SongGeneratorStrategy
│   │   ├── mock_strategy.py     # Mock strategy
│   │   ├── suno_strategy.py     # Suno API strategy
│   │   └── factory.py           # Reads GENERATOR_STRATEGY from .env
│   ├── services/
│   │   └── generation_service.py  # SongGenerationContext
│   ├── templates/music/
│   │   ├── login.html
│   │   └── dashboard.html
│   └── templatetags/
│       └── music_filters.py
├── .env.example
├── requirements.txt
└── manage.py
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Login page |
| GET | `/dashboard/` | Dashboard — generate songs and view library |
| POST | `/logout/` | Log out |
| GET | `/api/users/` | List all users |
| POST | `/api/songs/generate/` | Create and generate a song |
| GET | `/api/songs/<song_id>/download/` | Download song as MP3 |

---

## Deviations from Domain Model

### 1. User uses UUID instead of Google's ID
Google OAuth is out of scope for this exercise. UUID is used as a placeholder identifier. It will be replaced when OAuth is implemented.

### 2. `duration` on Song is nullable
Duration cannot be known at creation time since it depends on the AI generation result. It is populated once generation completes.

---

## CRUD Evidence (Exercise 3)

### Create & Read
![Create and Read](image.png)

### Update
![Update](image-1.png)

### Delete
![Delete](image-2.png)
