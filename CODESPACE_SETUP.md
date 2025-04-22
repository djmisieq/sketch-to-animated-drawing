# Instrukcja uruchomienia w GitHub Codespaces

Ten dokument zawiera szczegółowe instrukcje dotyczące uruchomienia projektu "Sketch-to-Animated-Drawing" w środowisku GitHub Codespaces.

## 1. Utworzenie Codespace

1. Przejdź do głównej strony repozytorium na GitHub (https://github.com/djmisieq/sketch-to-animated-drawing)
2. Kliknij zielony przycisk "Code"
3. Wybierz zakładkę "Codespaces"
4. Kliknij na "Create codespace on main"

## 2. Konfiguracja środowiska

GitHub Codespaces automatycznie skonfiguruje środowisko deweloperskie na podstawie pliku `.devcontainer/devcontainer.json`. Proces ten obejmuje:

- Instalację Python 3.12
- Instalację FFmpeg
- Instalację Poetry (menedżer zależności Python)
- Instalację Node.js i pnpm
- Uruchomienie usług Docker (PostgreSQL, Redis, Minio)

Ten proces może potrwać kilka minut przy pierwszym uruchomieniu.

## 3. Instalacja zależności

Po utworzeniu Codespace, otwórz terminal (Ctrl+` lub Terminal → New Terminal) i wykonaj następujące polecenia:

```bash
# Instalacja zależności Pythona
cd /workspaces/sketch-to-animated-drawing
poetry install

# Instalacja zależności frontendowych
cd frontend
pnpm install
cd ..
```

## 4. Inicjalizacja bazy danych i Minio

Usługi PostgreSQL, Redis i Minio są już uruchomione, ale musimy skonfigurować bucket Minio:

```bash
# Utwórz bucket dla plików
mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc mb myminio/sketches
```

## 5. Uruchomienie aplikacji

Teraz możesz uruchomić aplikację. Potrzebujesz trzech terminali:

### Terminal 1: Serwer FastAPI

```bash
cd /workspaces/sketch-to-animated-drawing
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Worker Celery

```bash
cd /workspaces/sketch-to-animated-drawing
poetry run celery -A app.tasks worker --loglevel=info
```

### Terminal 3: Frontend React

```bash
cd /workspaces/sketch-to-animated-drawing/frontend
pnpm dev
```

## 6. Dostęp do aplikacji

Po uruchomieniu wszystkich komponentów, Codespaces udostępni porty:

- Frontend: port 5173 - dostępny jako zakładka "Simple Browser" lub przekierowany lokalnie
- Backend API: port 8000
- Minio Console: port 9001 (login: minioadmin, hasło: minioadmin)

Aby otworzyć frontend, kliknij na zakładkę "PORTS" w dolnej części okna VS Code, znajdź port 5173 i kliknij ikonę globusa, aby otworzyć go w przeglądarce.

## 7. Testowanie aplikacji

Możesz przetestować aplikację przesyłając plik JPG lub PNG (max 10 MB) poprzez interfejs użytkownika. Proces konwersji powinien trwać nie dłużej niż 90 sekund, po czym będziesz mógł pobrać wygenerowany film MP4.

## Rozwiązywanie problemów

1. **Problem z uruchomieniem usług Docker:**
   ```bash
   docker compose down
   docker compose up -d
   ```

2. **Problem z zależnościami Poetry:**
   ```bash
   poetry update
   ```

3. **Problem z dostępem do bazy danych:**
   Sprawdź, czy PostgreSQL działa:
   ```bash
   docker compose ps
   ```
   Jeśli nie, zrestartuj:
   ```bash
   docker compose restart postgres
   ```

4. **Problem z frontendem:**
   ```bash
   cd frontend
   rm -rf node_modules
   pnpm install
   ```

## Uwagi dla deweloperów

- Kod źródłowy w Codespaces jest zsynchronizowany z repozytorium. Możesz tworzyć gałęzie i commitować zmiany bezpośrednio z Codespaces.
- Wszystkie zmiany dokonane w Codespaces są tymczasowe, dopóki nie zostaną zapisane w repozytorium.
- Codespaces ma limit czasowy bezczynności (zazwyczaj 30 minut). Po tym czasie zostanie wstrzymany, a uruchomione usługi zostaną zatrzymane.
