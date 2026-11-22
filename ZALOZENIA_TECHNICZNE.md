# Założenia techniczne aplikacji komunikacji biuro--produkcja

**Status:** dokument roboczy -- ustalenia wstępne\
**Wersja:** 0.1

## 1. Cel dokumentu

Ten dokument opisuje uzgodnione założenia technologiczne i
architektoniczne aplikacji webowej służącej do komunikacji pomiędzy
biurem a produkcją. Nie opisuje szczegółowo procesów biznesowych -- te
znajdują się w osobnym pliku `LOGIKA_BIZNESOWA.md`.

## 2. Główne założenia

-   Aplikacja będzie dostępna przez przeglądarkę internetową na
    komputerach i smartfonach.
-   Interfejs będzie responsywny i projektowany w pierwszej kolejności z
    myślą o wygodnej obsłudze na telefonie.
-   Dostęp do aplikacji będzie wymagał logowania.
-   Dostęp do funkcji i danych będzie kontrolowany po stronie serwera na
    podstawie ról, grup i uprawnień.
-   Aplikacja będzie rozwijana jako jeden system, z logicznym podziałem
    na niezależne moduły.
-   Na obecnym etapie nie planujemy mikroserwisów ani osobnego frontendu
    w React.
-   Architektura powinna umożliwiać późniejsze dodawanie modułów oraz
    integrację z systemem ERP bez przebudowy podstaw aplikacji.

## 3. Ustalony stos technologiczny

  -----------------------------------------------------------------------
  Obszar                  Technologia             Zastosowanie
  ----------------------- ----------------------- -----------------------
  Język                   Python                  Główny język aplikacji

  Backend                 Django                  Routing, logowanie,
                                                  ORM, formularze,
                                                  uprawnienia i logika
                                                  serwerowa

  Widoki                  Django Templates        Generowanie stron HTML
                                                  po stronie serwera

  Dynamiczne fragmenty UI HTMX                    Aktualizowanie części
                                                  strony bez pełnego
                                                  przeładowania

  Lekkie interakcje UI    Alpine.js               Proste zachowania po
                                                  stronie przeglądarki

  CSS                     Tailwind CSS            Responsywny wygląd i
                                                  wspólne style
                                                  komponentów

  Baza danych             PostgreSQL              Trwałe przechowywanie
                                                  danych

  Komunikacja w czasie    Django Channels +       Aktualizacje i
  rzeczywistym            WebSocket               powiadomienia dla
                                                  aktywnych sesji

  Broker / cache          Redis                   Obsługa warstwy
                                                  komunikacji
                                                  asynchronicznej i
                                                  ewentualnego cache

  Testy                   Pytest                  Testy logiki, uprawnień
                                                  i procesów

  Jakość kodu             Ruff                    Lintowanie i
                                                  formatowanie kodu
                                                  Python

  Kontrola wersji         Git                     Historia zmian i
                                                  możliwość bezpiecznego
                                                  cofania zmian
  -----------------------------------------------------------------------

### 3.1. Zasady użycia technologii

-   Django pozostaje głównym i centralnym frameworkiem aplikacji.
-   Django Templates odpowiadają za renderowanie stron.
-   HTMX służy do interakcji wymagających komunikacji z serwerem bez
    przeładowania całej strony.
-   Alpine.js należy stosować oszczędnie, do niewielkich interakcji
    lokalnych, np. otwierania menu, modali czy rozwijanych sekcji.
-   JavaScript pisany samodzielnie należy ograniczać do przypadków, w
    których powyższe rozwiązania nie wystarczają.
-   Nie tworzymy osobnego API REST dla każdej funkcji tylko dlatego, że
    jest to możliwe. API dodamy, jeśli pojawi się konkretny klient lub
    integracja, która go wymaga.
-   WebSocket i Web Push to dwa różne mechanizmy. WebSocket obsługuje
    aktywne połączenie z aplikacją, a Web Push może w przyszłości
    dostarczać powiadomienia systemowe, gdy aplikacja nie jest aktywnie
    otwarta.
-   Redis należy wprowadzić w konfiguracji wymaganej przez wybraną
    architekturę Channels i zadania asynchroniczne. Nie należy dodawać
    dodatkowych usług bez konkretnego uzasadnienia.

## 4. Architektura aplikacji

Przyjmujemy architekturę **Modular Monolith**:

-   jeden projekt Django;
-   jedna główna aplikacja wdrożeniowa;
-   wspólna baza danych PostgreSQL;
-   podział na moduły Django według odpowiedzialności biznesowej;
-   brak komunikacji sieciowej pomiędzy wewnętrznymi modułami -- moduły
    współpracują w ramach jednego projektu;
-   granice modułów powinny być czytelne, aby można je było rozwijać i
    testować niezależnie.

Przykładowy podział:

``` text
project/
├── config/
│   ├── settings/
│   ├── urls.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   ├── requests/
│   ├── production/
│   ├── notifications/
│   ├── planning/
│   └── dashboard/
├── templates/
│   ├── base.html
│   ├── components/
│   ├── layouts/
│   └── pages/
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
├── tests/
├── manage.py
└── requirements.txt
```

Nazwy i ostateczna liczba modułów mogą zostać doprecyzowane podczas
projektowania szczegółowego.

## 5. Organizacja kodu i utrzymywalność

### 5.1. Odpowiedzialności plików

W miarę potrzeb moduły mogą zawierać:

-   `models.py` -- modele danych i ich podstawowe reguły;
-   `views.py` -- obsługa żądań HTTP i wybór odpowiedzi;
-   `forms.py` -- formularze i walidacja danych wejściowych;
-   `urls.py` -- adresy URL modułu;
-   `services.py` -- operacje i procesy biznesowe, które nie powinny być
    rozproszone po widokach;
-   `selectors.py` -- złożone zapytania i odczyt danych, jeśli ich
    wydzielenie poprawi czytelność;
-   `tests/` -- testy modułu.

Nie należy tworzyć plików i warstw wyłącznie dla samego wzorca. Podział
ma rozwiązywać realny problem czytelności lub odpowiedzialności.

### 5.2. Wspólne elementy interfejsu

-   Wspólny szablon bazowy strony (`base.html`).
-   Wspólne komponenty: nawigacja, nagłówek, komunikaty, przyciski, pola
    formularzy, okna modalne i elementy statusów.
-   Nie kopiujemy tych samych fragmentów HTML do wielu ekranów.
-   Zmiana wspólnego komponentu powinna być możliwa w jednym miejscu.
-   Interfejs ma być spójny wizualnie i funkcjonalnie.

### 5.3. Zasady jakości

-   Nie duplikować logiki biznesowej.
-   Nie umieszczać całej logiki w `views.py`.
-   Nie łączyć niezależnych procesów biznesowych w jeden model lub moduł
    bez uzasadnienia.
-   Stosować czytelne nazwy po angielsku w kodzie; teksty interfejsu dla
    użytkowników będą po polsku.
-   Walidować dane po stronie serwera, niezależnie od walidacji
    przeglądarkowej.
-   Testować krytyczne reguły biznesowe i uprawnienia.
-   Nie traktować ukrycia przycisku w interfejsie jako zabezpieczenia --
    każda operacja musi być autoryzowana po stronie serwera.
-   Używać migracji Django do zmian schematu bazy danych.
-   Nie wprowadzać zależności ani bibliotek bez określenia, jaki problem
    rozwiązują.

## 6. Użytkownicy, logowanie i uprawnienia

-   Używamy systemu uwierzytelniania Django.
-   Przed utworzeniem pierwszych migracji należy zaprojektować własny
    model użytkownika oparty na `AbstractUser`, jeśli będzie potrzebny.
-   Uprawnienia będą oparte na grupach/rolach i uprawnieniach
    przypisanych do konkretnych działań.
-   Kontrola dostępu musi być realizowana po stronie serwera.
-   Należy rozróżniać uwierzytelnienie (kim jest użytkownik) od
    autoryzacji (co może zrobić).
-   Panel Django Admin może służyć do administracji technicznej i
    zarządzania danymi, ale nie zastępuje docelowego interfejsu
    operacyjnego dla biura i produkcji.

## 7. Interfejs i urządzenia mobilne

Interfejs powinien:

-   działać na komputerach, tabletach i smartfonach;
-   być projektowany mobile-first;
-   ograniczać liczbę kliknięć i ilość tekstu wymaganego od pracownika
    produkcji;
-   stosować duże, czytelne przyciski i pola formularzy;
-   zapewniać wyszukiwanie, filtrowanie i czytelne statusy;
-   unikać szerokich tabel na telefonach -- w razie potrzeby prezentować
    rekordy jako karty lub uproszczone widoki;
-   informować o stanie połączenia i wyniku wykonanej operacji;
-   zabezpieczać przed przypadkowym wielokrotnym wysłaniem formularza.

W przyszłości można rozważyć PWA, instalację aplikacji na ekranie
głównym, skanowanie kodów oraz powiadomienia systemowe.

## 8. Powiadomienia i komunikacja

### Etap podstawowy

-   Powiadomienia będą zapisywane w bazie danych.
-   WebSocket przez Django Channels będzie dostarczał aktualizacje
    użytkownikom z aktywną sesją.
-   Odbiorcy powiadomień będą wyznaczani na podstawie reguł biznesowych
    i uprawnień.
-   Utrata połączenia WebSocket nie może powodować utraty samego
    powiadomienia -- po ponownym otwarciu aplikacji użytkownik powinien
    móc pobrać nieprzeczytane powiadomienia z bazy.

### Etap późniejszy

-   Web Push dla powiadomień systemowych na obsługiwanych urządzeniach i
    przeglądarkach.
-   Ewentualne preferencje użytkownika dotyczące typów powiadomień.
-   Dodatkowe kanały komunikacji tylko wtedy, gdy pojawi się uzasadniona
    potrzeba.

## 9. Testowanie i kontrola zmian

-   Git będzie używany od początku projektu.
-   Większe funkcje powinny być rozwijane w małych, sprawdzalnych
    etapach.
-   Po każdej istotnej zmianie uruchamiamy odpowiednie testy.
-   Krytyczne procesy: logowanie, uprawnienia, tworzenie zgłoszeń,
    zmiany statusów, przypisywanie zadań i powiadomienia muszą mieć
    testy.
-   Nie należy przechodzić do kolejnego etapu, jeśli poprzedni nie
    działa i nie został zweryfikowany.
-   Zmiany bazy danych muszą być wykonywane przez migracje i sprawdzane
    na środowisku testowym.

## 10. Kierunek rozwoju

Architektura powinna umożliwiać stopniowe dodawanie:

1.  modułu zgłoszeń produkcyjnych;
2.  modułu zadań i przydziałów;
3.  komentarzy i załączników;
4.  planowania produkcji;
5.  raportów i zestawień;
6.  integracji z ERP;
7.  PWA i powiadomień Web Push;
8.  skanowania kodów kreskowych lub QR.

Nie zakładamy implementowania wszystkich tych funkcji od razu.

## 11. Decyzje pozostające do ustalenia

Poniższe kwestie nie są jeszcze ostatecznie rozstrzygnięte:

-   sposób hostowania aplikacji i środowisko produkcyjne;
-   sposób obsługi zadań asynchronicznych poza WebSocket;
-   czy i kiedy wdrożyć PWA oraz Web Push;
-   zasady kopii zapasowych i odtwarzania danych;
-   szczegółowy model użytkownika i sposób zarządzania kontami;
-   polityka przechowywania załączników;
-   szczegółowy proces wdrażania zmian (CI/CD);
-   wymagania dotyczące dostępu spoza sieci firmowej.

## 12. Zasada nadrzędna

**Wybieramy najprostsze rozwiązanie, które spełnia aktualne wymagania i
nie blokuje rozsądnego rozwoju aplikacji.** Nie dodajemy technologii,
warstw ani abstrakcji tylko dlatego, że są popularne. Priorytetem są:
mała ilość zbędnego kodu, czytelność, bezpieczeństwo, testowalność i
łatwość utrzymania.
