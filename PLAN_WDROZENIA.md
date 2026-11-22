# Plan wdrożenia aplikacji Biuro -- Produkcja (Roadmap dla Agenta)

**Instrukcja:** Realizuj dokładnie jeden krok na raz. Po spełnieniu kryteriów DoD oznacz krok jako `[x]` i zakończ turę.

---

## Faza 0: Fundament i szkielet projektu

### [x] Krok 0.1: Inicjalizacja projektu Django i narzędzi jakości
- **Źródła:** `ZALOZENIA_TECHNICZNE.md` (sekcje 3, 4, 9)
- **Zakres:**
  - Utwórz strukturę katalogów: `config/settings/`, `apps/` (`core`, `accounts`, `requests`, `production`, `notifications`, `dashboard`), `templates/` (`components/`, `layouts/`, `pages/`), `static/`, `tests/`.
  - Skonfiguruj PostgreSQL, Redis, `pytest` (`pytest-django`) oraz `ruff`.
- **Kryteria akceptacji (DoD):**
  - `python manage.py check` przechodzi bez błędów.
  - `pytest` i `ruff check .` uruchamiają się poprawnie.

### [x] Krok 0.2: Szablon bazowy i komponenty UI (`core`)
- **Źródła:** `ZALOZENIA_TECHNICZNE.md` (sekcje 3.1, 5.2, 7)
- **Zakres:**
  - Podepnij Tailwind CSS, HTMX i Alpine.js w `templates/base.html` (projektowanie *mobile-first*).
  - Stwórz reużywalne komponenty w `templates/components/`: nawigacja mobilna/desktopowa, kontener na modale HTMX, kontener na komunikaty *toast*, odznaki statusów i priorytetów.
- **Kryteria akceptacji (DoD):**
  - Widok testowy renderuje `base.html` oraz komponenty bez błędów szablonów.

---

## Faza 1: Użytkownicy, struktura i uprawnienia (`accounts`)

### [x] Krok 1.1: Model użytkownika i logowanie
- **Źródła:** `ZALOZENIA_TECHNICZNE.md` (sekcja 6), `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcja 14.1)
- **Zakres:**
  - Utwórz własny model `User` (`AbstractUser`) z polem typu pracownika (`OFFICE` / `PRODUCTION`).
  - Wdróż widoki logowania/wylogowania i wymóg autoryzacji dla całej aplikacji.
- **Kryteria akceptacji (DoD):**
  - Testy `pytest` weryfikujące logowanie, wylogowanie i przekierowanie niezalogowanych użytkowników.

### [x] Krok 1.2: Dynamiczna struktura organizacyjna
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 14.2, 14.3)
- **Zakres:**
  - Modele `OrganizationUnit` (drzewo działów/grup/podgrup o dowolnej głębokości, flaga aktywności) oraz `UserMembership` (rozróżnienie na przynależność główną `is_primary=True` i dodatkowe `is_primary=False`).
  - Operacyjny panel w aplikacji dla administratora do zarządzania strukturą i przypisaniami użytkowników.
- **Kryteria akceptacji (DoD):**
  - Testy tworzenia wielopoziomowej struktury i przypisania jednego użytkownika do wielu działów z zachowaniem głównego działu.

### [x] Krok 1.3: Dynamiczne funkcje i silnik uprawnień
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcja 14.4)
- **Zakres:**
  - Modele `JobFunction` (tworzone i edytowane dowolnie przez admina, z zestawem domyślnych uprawnień) oraz indywidualne nadpisania uprawnień dla użytkowników i grup (`PermissionOverride`).
  - Funkcja `Administratora` dająca pełny dostęp do systemu.
  - Serwis autoryzacji w `apps/accounts/services.py` sprawdzający uprawnienia po stronie serwera.
- **Kryteria akceptacji (DoD):**
  - Testy `pytest` sprawdzające dziedziczenie uprawnień z funkcji, nadpisania dla grupy/użytkownika oraz pełny dostęp admina.

---

## Faza 2: Zgłoszenia i zamówienia indeksów (`requests`)

### [x] Krok 2.1: Modele zgłoszeń, pozycji i historii
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 4.4, 14.8, 14.9, 14.10, 14.11)
- **Zakres:**
  - Model `ProductionRequest`: rodzaj (`INDEX_ORDER` / `OTHER`), priorytet (`NORMAL` / `URGENT`), opcjonalny `due_date`, status, `erp_reference_number`, autor, daty.
  - Model `RequestItem`: `erp_index` (wymagany tylko dla `INDEX_ORDER`), opcjonalna `quantity`, opcjonalna `unit` (`PCS` / `METERS`), niezależny `comment`.
  - Modele `RequestHistory` oraz `PriorityHistory` (stara wartość, nowa wartość, autor, czas).
- **Kryteria akceptacji (DoD):**
  - Migracje i testy walidacji (brak błędu przy pustej ilości/jednostce; brak wymogu indeksu dla `OTHER`).

### [x] Krok 2.2: Formularz tworzenia zgłoszenia (HTMX)
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 14.9, 14.10, 14.10.1)
- **Zakres:**
  - Formularz *mobile-first* z wyborem rodzaju zgłoszenia i priorytetu (`Normalny` / `Pilny`).
  - Dynamiczne dodawanie kolejnych pozycji przyciskiem **„Dodaj kolejną pozycję”** (HTMX) bez nadpisywania wpisanych wcześniej pól.
  - Wyraźne oznaczenie w UX, że ilość i jednostka są opcjonalne; zabezpieczenie przed podwójnym wysłaniem.
- **Kryteria akceptacji (DoD):**
  - Testy POST tworzące zgłoszenie z 1 oraz z 3 pozycjami i osobnymi komentarzami.

### [ ] Krok 2.3: Widoki list (Otwarte / Zrealizowane) i wyszukiwarka
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 14.6, 14.12.1)
- **Zakres:**
  - Widok dostępny dla wszystkich zalogowanych (zarówno Biuro, jak i cała Produkcja) podzielony na zakładki: **Otwarte** oraz **Zrealizowane**.
  - Wyszukiwarka indeksów ERP działająca przez HTMX w obu zakładkach.
- **Kryteria akceptacji (DoD):**
  - Testy weryfikujące, że pracownik produkcji widzi zgłoszenia innych osób i może wyszukać indeks w obu zakładkach.

### [ ] Krok 2.4: Obsługa zgłoszeń, zmiana statusów, priorytetów i terminów
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 4.3, 14.11, 14.12.2, 14.12.3, 14.12.4)
- **Zakres:**
  - Szczegóły zgłoszenia (bez funkcji czatu/odpowiadania — tylko podgląd komentarzy z utworzenia).
  - Zmiana statusu przez biuro, autora, brygadzistę, admina lub uprawnione grupy; wpisywanie numeru ERP przez biuro.
  - Zmiana priorytetu po utworzeniu: wyłącznie brygadzista/kierownik/admin (zapis w `PriorityHistory`).
  - Edycja terminu realizacji: wyłącznie użytkownicy/grupy z nadanym uprawnieniem przez admina.
- **Kryteria akceptacji (DoD):**
  - Testy autoryzacji (`403` dla zwykłego pracownika próbującego zmienić priorytet lub termin po utworzeniu) oraz testy zapisu historii.

---

## Faza 3: Zadania produkcyjne (`production`)

### [ ] Krok 3.1: Modele zadań i sesji uczestnictwa
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 5.2, 5.4, 14.5, 14.7, 14.8)
- **Zakres:**
  - Model `ProductionTask`: tytuł, opis, przypisanie do `OrganizationUnit` (zadanie ogólne) lub konkretnego `User` (zadanie indywidualne), priorytet (`NORMAL`/`URGENT`), termin, status, opcjonalne powiązanie z `ProductionRequest`.
  - Model `TaskParticipation`: `task`, `user`, `started_at`, `left_at` (null = aktywny), `leave_note` (opcjonalna adnotacja).
  - Model `TaskHistory` (zapis zdarzeń, w tym zakończenia zadania i przekazania).
- **Kryteria akceptacji (DoD):**
  - Migracje i testy potwierdzające możliwość wielokrotnego uczestnictwa tego samego pracownika w jednym zadaniu.

### [ ] Krok 3.2: Tworzenie, widoczność i przekazywanie zadań
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 14.5, 14.11.2, 14.12.1)
- **Zakres:**
  - Formularz tworzenia zadania i nadawania początkowego priorytetu przez zlecającego.
  - `selectors.py`: pracownik produkcji widzi **wyłącznie** zadania swojego działu/grupy oraz indywidualne przypisane do niego; brygadzista widzi nadzorowane działy; kierownik widzi wszystko.
  - Akcja **Przekaż zadanie** (zmiana przypisanego pracownika w zadaniu indywidualnym) — dozwolona **wyłącznie** dla brygadzisty (i admina).
- **Kryteria akceptacji (DoD):**
  - Testy izolacji widoczności zadań między działami oraz testy uprawnień przekazywania zadania.

### [ ] Krok 3.3: Cykl życia zadania (Rozpocznij, Dołącz, Opuść, Zakończ)
- **Źródła:** `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 14.5.1, 14.5.2, 14.5.3, 14.5.4)
- **Zakres:**
  - Przyciski HTMX: **„Rozpocznij”** / **„Dołącz”** (tworzy nowy rekord `TaskParticipation`).
  - Przycisk **„Opuść”**: otwiera modal z opcjonalnym polem adnotacji, ustawia `left_at` bez zamykania całego zadania.
  - Przycisk **„Zakończ zadanie”**: najpierw pobiera listę aktywnych uczestników i wyświetla modal potwierdzający z ich imionami i nazwiskami; po potwierdzeniu zamyka wszystkie aktywne `TaskParticipation`, ustawia status na Zrealizowane i zapisuje wpis w `TaskHistory`.
  - Widok pełnej historii uczestnictwa w szczegółach zadania.
- **Kryteria akceptacji (DoD):**
  - Testy scenariusza: dołączenie 2 osób -> opuszczenie przez 1 z adnotacją -> ponowne dołączenie -> zakończenie zadania i weryfikacja zamknięcia wszystkich aktywnych sesji.

---

## Faza 4: Powiadomienia w czasie rzeczywistym i Pulpity (`notifications` & `dashboard`)

### [ ] Krok 4.1: Powiadomienia w bazie i WebSocket (Django Channels)
- **Źródła:** `ZALOZENIA_TECHNICZNE.md` (sekcja 8), `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcja 14.13.1)
- **Zakres:**
  - Konfiguracja ASGI, `Django Channels` i `Redis`.
  - Modele `Notification` oraz `NotificationRecipient` (`is_read`).
  - Wyzwalanie powiadomień przy: nowym zgłoszeniu/zamówieniu (dla biura), nowym zadaniu/zmianie dotyczącej konkretnego pracownika (dla produkcji).
  - Consumer WebSocket wysyłający komunikat na ekran (HTMX/Alpine toast) aktywnym użytkownikom oraz widok nieprzeczytanych powiadomień.
- **Kryteria akceptacji (DoD):**
  - Testy `pytest` weryfikujące zapis `NotificationRecipient` w bazie dla właściwych odbiorców oraz test połączenia WebSocket.

### [ ] Krok 4.2: Pulpity startowe (`dashboard`) i dopracowanie Mobile-First
- **Źródła:** `ZALOZENIA_TECHNICZNE.md` (sekcja 7), `logika_biznesowa_aplikacji_komunikacji_biuro_produkcja.md` (sekcje 5.3, 10)
- **Zakres:**
  - Ekran główny po zalogowaniu: szybkie akcje („Nowe zgłoszenie / Zamów indeks”), lista aktywnych zadań użytkownika/działu, podsumowanie otwartych i pilnych zgłoszeń (dla biura/kierownictwa).
  - Weryfikacja responsywności (karty zamiast szerokich tabel na mobile) oraz dodanie atrybutów przygotowujących pole `erp_index` pod przyszły skaner kodów **Code-128** (sekcja 14.13.2).
- **Kryteria akceptacji (DoD):**
  - Pełny test E2E ścieżki od zgłoszenia potrzeby przez produkcję po realizację zadania, `ruff check .` oraz `pytest` na zielono.






