# Instrukcja dla kontrybutorów

## Status projektu

Aplikacja Sketch-to-Animated-Drawing jest aktualnie w fazie rozwoju. Poniżej znajduje się lista zrealizowanych i bieżących zadań:

### Zrealizowane

- ✅ Konfiguracja środowiska deweloperskiego (GitHub Codespaces)
- ✅ Konfiguracja bazy danych PostgreSQL, Redis i Minio
- ✅ Podstawowa struktura aplikacji FastAPI z endpointami
- ✅ Moduł wektoryzacji obrazów rastrowych do SVG
- ✅ Moduł animacji SVG
- ✅ Moduł renderowania MP4
- ✅ Podstawowy interfejs React z ekranami Upload, Status, Pobierz
- ✅ Integracja z Blenderem do generowania animacji ręki
- ✅ Testy dla głównych modułów

### W toku

- 🔄 Rozszerzone testy end-to-end
- 🔄 Optymalizacja wydajności (szczególnie renderowania)
- 🔄 Refaktoryzacja kodu i poprawa jakości
- 🔄 Dokumentacja API i kodu

### Planowane

- 📅 Rozszerzenie funkcjonalności (dodatkowe opcje animacji)
- 📅 Wersja Pro z dodatkowymi funkcjami
- 📅 Wdrożenie w środowisku produkcyjnym

## Uruchomienie projektu lokalnie

Aby uruchomić projekt lokalnie, wykonaj następujące kroki:

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

5. Uruchom serwer FastAPI:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

6. Uruchom worker Celery:
   ```bash
   poetry run celery -A app.tasks worker --loglevel=info
   ```

7. Uruchom frontend:
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

## Wymagania dla kontrybutorów

### Konwencje kodu

- **Python**: Używaj formatera `ruff` i `mypy` dla typów. Docstrings w formacie Google.
- **TypeScript/React**: Używaj ESLint i Prettier.
- **Commitów**: Używaj czasownikowych komunikatów w trybie rozkazującym.

### Proces Pull Request

1. Stwórz nową gałąź dla swojej funkcji (`feature/*`) lub poprawki błędu (`bugfix/*`).
2. Wykonaj zmiany, upewniając się, że kod jest pokryty testami (minimum 80%).
3. Użyj `pre-commit` do sprawdzenia jakości kodu przed commitem.
4. Wyślij PR z dokładnym opisem zmian.

### Ważne uwagi

- Rozmiar pliku wejściowego jest ograniczony do 10 MB.
- Czas renderowania powinien być ≤ 90 sekund na CPU.
- Aplikacja używa vtracer do wektoryzacji obrazów, upewnij się, że jest zainstalowany.
- Aplikacja używa Blendera do animacji ręki, upewnij się, że jest zainstalowany.

## Struktura projektu

```
sketch-to-animated-drawing/
├── app/                     # Kod backendu
│   ├── __init__.py
│   ├── config.py            # Konfiguracja aplikacji
│   ├── db.py                # Moduł bazy danych
│   ├── main.py              # Główna aplikacja FastAPI
│   ├── models.py            # Modele danych
│   ├── storage.py           # Obsługa przechowywania plików
│   ├── tasks.py             # Zadania Celery
│   ├── vectorizer.py        # Moduł wektoryzacji
│   ├── animator.py          # Moduł animacji SVG
│   └── renderer.py          # Moduł renderowania MP4
├── frontend/                # Kod frontendu
│   ├── public/
│   └── src/
│       ├── components/      # Komponenty React
│       ├── pages/           # Strony aplikacji
│       ├── services/        # Usługi API
│       └── ...
├── scripts/                 # Skrypty pomocnicze
│   └── hand_animator.py     # Skrypt Blendera do animacji ręki
├── tests/                   # Testy
│   ├── __init__.py
│   ├── test_health.py       # Test endpointu health
│   └── test_vectorizer.py   # Testy modułu wektoryzacji
├── .devcontainer/           # Konfiguracja GitHub Codespaces
├── docker-compose.yml       # Konfiguracja usług Docker
└── pyproject.toml           # Konfiguracja Poetry
```

## Licencje

- **Kod:** MIT
- **Grafika ręki i modele Blender:** CC-0 lub autorskie
- **Dataset QuickDraw:** CC BY

## Kontakt

W przypadku pytań lub sugestii, utwórz issue w repozytorium.
