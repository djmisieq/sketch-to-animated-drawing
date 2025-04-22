# Sketch-to-Animated-Drawing

Aplikacja do konwersji szkiców (JPG/PNG) na animowane filmy MP4/WEBM 1080p 30 fps, przedstawiające proces rysowania konturu przez animowaną rękę.

## Funkcje

- Upload plików JPG/PNG (≤ 10 MB)
- Konwersja rastrowego szkicu na format wektorowy (SVG)
- Tworzenie animacji procesu rysowania
- Renderowanie filmu MP4 z animowaną ręką
- REST API z endpointami `/jobs`, `/status/{id}`, `/result/{id}`
- Interfejs webowy dla użytkownika
- Kolejka zadań z Celery i Redis
- Przechowywanie plików w Minio (kompatybilne z S3)

## Technologie

- Backend: FastAPI (Python 3.12) + Pydantic v2
- Frontend: React 18 + Vite + TypeScript + shadcn/ui
- Kolejka: Celery 5 + Redis
- Baza danych: PostgreSQL 16
- Storage: Minio (S3-compatible)
- Wektoryzacja: vtracer CLI
- Animacja: drawsvg (stroke-dashoffset)
- Render wideo: MoviePy + FFmpeg
- Ręka: Blender 3.x (Grease Pencil)
- Środowisko deweloperskie: GitHub Codespaces (Ubuntu 22.04)

## Rozpoczęcie pracy

### Konfiguracja środowiska deweloperskiego

Projekt został skonfigurowany do pracy w GitHub Codespaces. Po otwarciu repozytorium w Codespace, wszystkie zależności zostaną automatycznie zainstalowane.

Alternatywnie, można uruchomić projekt lokalnie:

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/djmisieq/sketch-to-animated-drawing.git
   cd sketch-to-animated-drawing
   ```

2. Zainstaluj Poetry (menedżer zależności Python):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Zainstaluj zależności:
   ```bash
   poetry install
   ```

4. Uruchom usługi Docker:
   ```bash
   docker-compose up -d
   ```

### Uruchomienie aplikacji

1. Uruchom serwer FastAPI:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

2. Uruchom worker Celery:
   ```bash
   poetry run celery -A app.tasks worker --loglevel=info
   ```

3. Uruchom frontend:
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

## API Endpoints

- `GET /health` - Endpoint zdrowia aplikacji
- `POST /api/v1/jobs` - Utworzenie nowego zadania (upload pliku)
- `GET /api/v1/jobs/{job_id}` - Pobranie statusu zadania
- `GET /api/v1/jobs` - Lista wszystkich zadań
- `GET /api/v1/result/{job_id}` - Pobranie wyniku zadania (URL do wideo)

## Roadmap

- Sprint 1: Raster → SVG → animowane SVG; test_pipeline_basic ≤ 120 s CPU
- Sprint 2: Render MP4 + panel Upload/Status/Pobierz; film ≤ 90 s
- Sprint 3: Ręka 3-D (Blender) + overlay; demo MP4
- Sprint 4: Kolejka jobów + testy E2E; coverage ≥ 80 %

## Licencje

- Kod: MIT
- Grafika ręki i modele Blender: CC-0 lub autorskie
- Dataset QuickDraw: CC BY
