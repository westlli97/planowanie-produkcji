# Kontekst i zasady pracy Agenta AI

**Projekt:** Aplikacja komunikacji Biuro -- Produkcja (Modular Monolith)  
**Dokumentacja źródłowa (czytaj TYLKO wskazane sekcje z planu, nie ładuj całych plików):**
- `ZALOZENIA_TECHNICZNE.md` – architektura, stos, konwencje kodu.
- `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` – reguły biznesowe i uprawnienia.
- `PLAN_WDROZENIA.md` – aktualny stan prac i lista kroków.

## 1. Twarde reguły technologiczne
- **Stack:** Python, Django, Django Templates, HTMX, Alpine.js, Tailwind CSS, PostgreSQL, Django Channels + Redis, Pytest, Ruff.
- **Zakazy:** Brak React/Vue, brak osobnego REST API (chyba że plan wyraźnie wskazuje), brak logiki biznesowej w `views.py` (używaj `services.py` do zapisu i `selectors.py` do złożonych odczytów).
- **Język:** Kod, nazwy modeli, zmiennych i komentarze w kodzie po **angielsku**. Teksty interfejsu użytkownika (UI) po **polsku**.
- **Bezpieczeństwo:** Każda operacja i uprawnienie muszą być weryfikowane po stronie serwera. Ukrycie przycisku w HTML to nie zabezpieczenie.
- **UI:** Podejście *mobile-first*, wspólny `base.html` i komponenty w `templates/components/`.

## 2. Protokół wykonania pojedynczego kroku (Optymalizacja tokenów)
1. Odczytaj z `PLAN_WDROZENIA.md` **wyłącznie** pierwszy nieukończony krok `[ ]`.
2. Jeśli potrzebujesz szczegółów, odczytaj **tylko** sekcje wymienione w polu `Źródła:` tego kroku. Nie czytaj całych plików dokumentacji.
3. Zaimplementuj kod w kolejności: `models.py` (migracje) -> `services.py` / `selectors.py` -> `forms.py` -> `views.py` -> `templates/`.
4. Napisz testy w `pytest` pokrywające wszystkie punkty z sekcji `Kryteria akceptacji (DoD)`.
5. Uruchom w terminalu: `ruff check .` oraz `pytest`. Napraw ewentualne błędy.
6. Oznacz krok jako ukończony `[x]` w `PLAN_WDROZENIA.md`, zrób `git commit` i **ZATRZYMAJ SIĘ** – czekaj na polecenie kontynuacji od użytkownika.