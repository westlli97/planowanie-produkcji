# Logika biznesowa aplikacji komunikacji biuro--produkcja

**Status:** dokument roboczy -- wymagania wstępne

**Wersja:** 0.3

## 1. Cel aplikacji

Aplikacja ma usprawnić przepływ informacji pomiędzy biurem a produkcją.
Ma umożliwiać zgłaszanie potrzeb produkcyjnych, obsługę zgłoszeń przez
biuro, przekazywanie zadań pracownikom oraz informowanie właściwych osób
o nowych zdarzeniach.

Podstawowe założenie: pracownik powinien móc wykonać potrzebną czynność
szybko, bez konieczności korzystania z rozbudowanego systemu ERP.

## 2. Główne obszary funkcjonalne

1. Użytkownicy, logowanie i uprawnienia.

2. Zgłoszenia z produkcji do biura.

3. Obsługa i realizacja zgłoszeń przez biuro.

4. Zadania tworzone przez biuro i przydzielane produkcji.

5. Powiadomienia i komunikacja w czasie rzeczywistym.

6. W przyszłości: planowanie produkcji, raporty i integracja z ERP.

## 3. Użytkownicy i role

Aplikacja będzie dostępna wyłącznie dla zalogowanych użytkowników.

Wstępnie wyróżniamy następujące grupy użytkowników:

* **Produkcja** -- pracownicy zgłaszający potrzeby i realizujący
  przydzielone zadania.

* **Biuro** -- pracownicy obsługujący zgłoszenia, uzupełniający
  informacje i tworzący zadania.

* **Kierownictwo / nadzór** -- użytkownicy, którzy mogą potrzebować
  szerszego wglądu, nadzoru lub raportowania.

* **Administrator** -- zarządzanie kontami, grupami, uprawnieniami i
  konfiguracją.

To są role robocze, a nie ostateczna lista. Dostęp do czynności będzie
wynikał z konkretnych uprawnień, a nie wyłącznie z nazwy roli.

### 3.1. Przykładowe uprawnienia

Uprawnienie               Znaczenie

`request.create`          Utworzenie zgłoszenia
`request.view_own`        Podgląd własnych zgłoszeń
`request.view_all`        Podgląd wszystkich zgłoszeń
`request.change_status`   Zmiana statusu zgłoszenia
`request.assign`          Przypisanie osoby obsługującej
`request.erp_edit`        Uzupełnienie lub zmiana numeru ERP
`task.create`             Utworzenie zadania
`task.assign`             Przydzielenie zadania osobie lub grupie
`task.view_assigned`      Podgląd zadań przypisanych użytkownikowi
`task.change_status`      Zmiana statusu zadania
`user.manage`             Zarządzanie użytkownikami

Lista wymaga doprecyzowania. Uprawnienia muszą być sprawdzane po stronie
serwera przy każdej operacji.

## 4. Zgłoszenia z produkcji do biura

### 4.1. Cel

Pracownik produkcji może przesłać do biura informację o potrzebie
związanej z konkretnym indeksem ERP / materiałem / produktem.

### 4.2. Utworzenie zgłoszenia

Wstępnie formularz zgłoszenia zawiera:

* indeks ERP -- identyfikator pozycji, której dotyczy zgłoszenie;

* opis -- wyjaśnienie potrzeby lub problemu;

* autora -- przypisywanego automatycznie na podstawie zalogowanego
  użytkownika;

* datę i godzinę utworzenia -- nadawaną automatycznie przez serwer.

Użytkownik nie powinien samodzielnie wpisywać autora ani daty
utworzenia.

**Wstępne założenie:** jedno zgłoszenie dotyczy jednego indeksu / jednej
pozycji. Możliwość dodania wielu pozycji do jednego zgłoszenia pozostaje
do decyzji *(zaktualizowano w sekcji 14.10)*.

Do ustalenia pozostają m.in. obowiązkowość indeksu, ilość, jednostka
miary, priorytet, termin i możliwość dodawania zdjęć lub plików *(rozstrzygnięto w sekcji 14)*.

### 4.3. Obsługa zgłoszenia przez biuro

Pracownik biura powinien móc:

* wyświetlić listę zgłoszeń;

* otworzyć szczegóły zgłoszenia;

* zmienić status;

* przypisać osobę odpowiedzialną za obsługę;

* uzupełnić numer referencyjny z ERP;

* w przyszłości dodawać komentarze i załączniki *(zaktualizowano w sekcji 14.12 -- brak funkcji czatu)*.

Na pierwszym etapie numer ERP będzie wpisywany ręcznie. W przyszłości
możliwa jest integracja, która może pobierać lub weryfikować dane w ERP.

### 4.4. Proponowane statusy zgłoszenia

Wstępna propozycja:

Status         Znaczenie

Nowe           Zgłoszenie zostało utworzone i oczekuje na obsługę
W trakcie      Ktoś rozpoczął obsługę
Oczekuje       Dalsza obsługa wymaga informacji lub działania z zewnątrz
Zrealizowane   Zgłoszenie zostało obsłużone
Anulowane      Zgłoszenie zostało anulowane

Ostateczne statusy, dozwolone przejścia i osoby uprawnione do ich zmiany
wymagają zatwierdzenia *(reguły uprawnień doprecyzowano w sekcji 14.12)*.

### 4.5. Historia zgłoszenia

Zmiany statusu i istotne operacje powinny być zapisywane w historii, a
nie tylko nadpisywać poprzednie wartości.

Historia może obejmować:

* utworzenie zgłoszenia;

* zmianę statusu;

* przypisanie lub zmianę osoby odpowiedzialnej;

* uzupełnienie lub zmianę numeru ERP;

* dodanie komentarza;

* inne istotne modyfikacje.

Każdy wpis historii powinien zawierać autora zdarzenia i czas jego
wystąpienia. Zakres dokładnie rejestrowanych zmian wymaga
doprecyzowania.

## 5. Zadania tworzone przez biuro dla produkcji

Zadania produkcyjne są odrębnym obszarem od zgłoszeń.

### 5.1. Cel

Pracownik biura może utworzyć zadanie i przydzielić je:

* konkretnemu pracownikowi;

* grupie pracowników;

* ewentualnie kilku osobom, jeśli taki sposób przydziału zostanie
  zatwierdzony.

### 5.2. Wstępne dane zadania

Potencjalne pola:

* tytuł;

* opis;

* osoba lub grupa przypisana;

* autor zadania;

* data utworzenia;

* termin realizacji;

* priorytet;

* status;

* opcjonalne powiązanie ze zgłoszeniem lub indeksem ERP.

Nie wszystkie pola są jeszcze zatwierdzone.

### 5.3. Widok pracownika produkcji

Pracownik powinien mieć prosty widok pokazujący przede wszystkim:

* zadania przypisane do niego;

* zadania przypisane do jego grupy, jeśli ma do nich dostęp;

* status i priorytet;

* termin;

* szczegóły zadania;

* możliwość wykonania dozwolonej zmiany statusu.

Interfejs powinien ograniczać liczbę kliknięć i ilość tekstu wymaganego
od pracownika.

### 5.4. Statusy zadań

Statusy zadań należy zdefiniować osobno od statusów zgłoszeń. Wstępna
propozycja:

* Nowe;

* Przyjęte do realizacji;

* W trakcie;

* Zablokowane / oczekuje;

* Zrealizowane;

* Anulowane.

Lista i dozwolone przejścia wymagają zatwierdzenia.

## 6. Powiadomienia

### 6.1. Cel

Użytkownik powinien otrzymać informację o zdarzeniach, które wymagają
jego uwagi lub dotyczą jego pracy.

Przykładowe zdarzenia:

* nowe zgłoszenie z produkcji;

* zmiana statusu zgłoszenia;

* przypisanie osoby odpowiedzialnej;

* utworzenie zadania;

* przypisanie zadania użytkownikowi lub jego grupie;

* zmiana statusu zadania;

* komentarz lub inna istotna aktualizacja.

### 6.2. Zasady działania

* Powiadomienie powinno być kierowane do właściwych użytkowników, a
  nie automatycznie do wszystkich.

* Powiadomienia powinny być zapisywane, aby nie ginęły przy chwilowym
  braku połączenia.

* Dla użytkownika aktywnie korzystającego z aplikacji aktualizacja
  powinna być dostarczana w czasie rzeczywistym *(doprecyzowano w sekcji 14.13)*.

* Po powrocie do aplikacji użytkownik powinien móc zobaczyć
  nieprzeczytane powiadomienia.

* W przyszłości można dodać powiadomienia systemowe przeglądarki /
  telefonu.

Szczegółowe reguły odbiorców i możliwość konfigurowania powiadomień
wymagają doprecyzowania.

## 7. Rozdzielenie zgłoszeń, zadań i powiadomień

Należy zachować rozdział pomiędzy trzema pojęciami:

* **Zgłoszenie** -- potrzeba lub problem przekazany z produkcji do
  biura.

* **Zadanie** -- czynność zlecona pracownikowi lub grupie do
  wykonania.

* **Powiadomienie** -- informacja o zdarzeniu dotyczącym użytkownika.

Powiadomienie nie jest samym zgłoszeniem ani zadaniem. Może informować o
utworzeniu lub zmianie jednego z tych obiektów.

Zgłoszenie i zadanie mogą być ze sobą powiązane, ale nie należy
zakładać, że każde zgłoszenie automatycznie tworzy zadanie.

## 8. Wstępny model danych

Poniższa lista opisuje potencjalne encje biznesowe, a nie zatwierdzony
schemat bazy danych.

Encja                               Odpowiedzialność

User                                Konto użytkownika

Group / Permission                  Grupy i uprawnienia

ProductionRequest                   Zgłoszenie z produkcji do biura

RequestHistory                      Historia zmian zgłoszenia

RequestComment                      Komentarze do zgłoszenia, jeśli
zostaną wdrożone

ProductionTask                      Zadanie dla produkcji

TaskAssignment                      Przydział zadania osobie lub grupie

TaskHistory                         Historia zmian zadania

Notification                        Zdarzenie powiadomienia

NotificationRecipient               Odbiorca, stan odczytania
powiadomienia

ERPReference                        Dane lub identyfikatory powiązane z
ERP, jeśli uzasadni to projekt

Nazwy, relacje i pola modeli zostaną określone podczas projektowania
bazy danych.

## 9. Integracja z ERP

Integracja z ERP jest planowana jako późniejszy etap.

### Etap początkowy

* Zgłoszenie przechowuje własny identyfikator aplikacyjny.

* Numer ERP jest osobnym polem / referencją i może być wpisywany
  ręcznie przez uprawnionego pracownika biura.

* Nie wolno utożsamiać wewnętrznego numeru zgłoszenia z numerem ERP.

### Etap przyszły

Możliwe funkcje integracji:

* wyszukiwanie i weryfikacja indeksów;

* pobieranie danych o pozycji;

* przekazywanie danych do ERP;

* automatyczne pobieranie numeru dokumentu lub zlecenia ERP;

* sprawdzanie stanu realizacji.

Sposób integracji zależy od możliwości i interfejsów konkretnego systemu
ERP. Nie jest jeszcze ustalony.

## 10. Zasady obsługi na urządzeniach mobilnych

* Pracownik produkcji powinien móc szybko utworzyć zgłoszenie na
  smartfonie.

* Najważniejsze informacje powinny być widoczne bez przewijania dużej
  liczby elementów.

* Przyciski i pola powinny być wygodne do obsługi dotykiem.

* Listy rekordów na małym ekranie powinny być prezentowane w czytelnej
  formie, np. jako karty.

* Należy jasno informować, czy operacja się powiodła.

* Należy zapobiegać przypadkowemu ponownemu wysłaniu tego samego
  formularza.

* W przyszłości można rozważyć skanowanie kodów kreskowych lub QR w
  celu szybszego wprowadzania indeksów *(doprecyzowano w sekcji 14.13 -- obsługa kodów Code-128 w kolejnych etapach)*.

## 11. Proponowana kolejność wdrożenia

### Etap 1 -- fundament

* logowanie;

* uzytkownicy i grupy;

* uprawnienia;

* wspólny interfejs;

* podstawowe pulpity;

* responsywność.

### Etap 2 -- zgłoszenia

* tworzenie zgłoszeń;

* automatyczny autor i czas utworzenia;

* lista i szczegóły zgłoszeń;

* statusy;

* przypisywanie osoby obsługującej;

* ręczne uzupełnianie numeru ERP;

* historia;

* powiadomienia w czasie rzeczywistym.

### Etap 3 -- zadania produkcyjne

* tworzenie zadań przez biuro;

* przydzielanie osób i grup;

* widok zadań pracownika;

* statusy i priorytety;

* historia zadań.

### Etap 4 -- rozszerzenia

* komentarze;

* zdjęcia i załączniki;

* dodatkowe reguły powiadomień;

* raporty;

* planowanie produkcji;

* PWA / Web Push, jeśli będzie potrzebne;

* skanowanie kodów Code-128.

### Etap 5 -- integracja ERP

* analiza możliwości integracyjnych;

* mapowanie danych;

* odczyt i ewentualny zapis danych;

* obsługa błędów i ponawiania operacji.

## 12. Kwestie wymagające decyzji

Poniższe pytania pozostają otwarte lub zostały rozstrzygnięte w sekcji 14:

 1. **Ustalono:** jedno zgłoszenie może zawierać wiele pozycji;
    szczegółowa logika znajduje się w sekcji 14.10.

 2. **Ustalono:** obowiązek podania indeksu ERP zależy od rodzaju
    zgłoszenia; szczegółowa logika znajduje się w sekcji 14.9.

 3. **Ustalono:** zgłoszenie umożliwia podanie ilości i jednostki miary
    dla każdej pozycji, ale oba pola są opcjonalne; szczegóły w sekcji 14.10.1.

 4. **Ustalono:** poziomy priorytetów (Normalny, Pilny) oraz opcjonalne
    terminy realizacji i zasady ich edycji zdefiniowano w sekcjach 14.11 oraz 14.12.

 5. **Ustalono:** pracownik produkcji widzi wszystkie zgłoszenia i zamówienia
    indeksów (w zakładkach Otwarte i Zrealizowane), natomiast w przypadku
    zadań widzi wyłącznie zadania przypisane do niego lub jego grupy;
    szczegóły w sekcji 14.12.

 6. **Ustalono:** statusy zgłoszeń i zamówień mogą zmieniać uprawnione role
    oraz osoby/grupy skonfigurowane przez administratora; szczegóły w sekcji 14.12.

 7. **Ustalono:** komentarz można dodać wyłącznie podczas tworzenia zgłoszenia
    (brak funkcji komunikatora / wymiany wiadomości); szczegóły w sekcji 14.12.

 8. **Ustalono:** zadanie może być realizowane przez wiele osób
    jednocześnie; szczegółowa logika znajduje się w sekcji 14.5.

 9. **Ustalono:** zadania ogólne są widoczne dla pracowników
    przypisanego działu; zadania indywidualne są widoczne dla
    wskazanego pracownika oraz osób pełniących nadzór zgodnie
    z uprawnieniami. Szczegóły znajdują się w sekcji 14.5.

10. **Ustalono:** reguły powiadomień w czasie rzeczywistym dla biura i
    produkcji opisano w sekcji 14.13.

11. **Ustalono:** w pierwszej wersji nie będzie skanowania kodów; obsługa
    kodów Code-128 zostanie dodana w późniejszym etapie (sekcja 14.13).

12. Jakie dokładnie informacje i operacje mają być wymieniane z ERP?

## 13. Zasada nadrzędna

Aplikacja ma usprawniać przepływ informacji, a nie odtwarzać cały system
ERP. Każda funkcja powinna mieć jasno określonego użytkownika, cel,
reguły dostępu i rezultat. Najpierw wdrażamy prosty, działający proces
zgłoszeń i zadań, a dopiero potem rozbudowujemy go o kolejne możliwości.

# 14. Uzupełnienia i decyzje biznesowe ustalone w dalszej analizie

**Status:** ustalenia zaakceptowane przez użytkownika

**Ważność:** poniższe ustalenia doprecyzowują wcześniejsze sekcje. W przypadku
sprzeczności z wcześniejszym opisem pierwszeństwo mają zasady z tej sekcji.

## 14.1. Typ pracownika, struktura organizacyjna i funkcje

Należy rozdzielić trzy niezależne obszary danych użytkownika:

1. **Typ pracownika** – np. pracownik biurowy lub pracownik produkcji.

2. **Struktura organizacyjna** – działy, grupy i podgrupy, do których należy
   użytkownik.

3. **Funkcje pełnione przez użytkownika** – np. pracownik, brygadzista,
   kierownik. Użytkownik może mieć kilka funkcji jednocześnie.

Przykładowo jedna osoba może być pracownikiem produkcji, operatorem
konkretnej maszyny oraz brygadzistą.

Funkcja brygadzisty, kierownika ani inna funkcja nadzorcza nie powinna
zastępować typu pracownika ani przynależności organizacyjnej.

## 14.2. Dynamiczna struktura organizacyjna

Struktura organizacyjna nie może być zaszyta na stałe w kodzie aplikacji.

Administrator powinien mieć możliwość samodzielnego:

* tworzenia działów, grup i podgrup;

* tworzenia kolejnych poziomów struktury bez z góry narzuconego limitu
  głębokości;

* zmieniania nazw i struktury;

* dezaktywowania nieużywanych elementów;

* przypisywania użytkowników do odpowiednich elementów struktury.

Przykładowe elementy to biuro, produkcja, pakowalnia, szlifiernia,
operatorzy laserów, operatorzy maszyn i inne jednostki dodawane w miarę
potrzeb. Lista przykładów nie jest zamknięta ani zakodowana na stałe.

Interfejs dodawania i edycji użytkownika musi być dynamiczny. Dostępne
typy, działy, grupy, podgrupy i funkcje powinny być pobierane z aktualnej
konfiguracji systemu. Dodanie nowego działu, grupy, podgrupy, stanowiska
lub funkcji przez administratora nie może wymagać zmiany kodu aplikacji.

## 14.3. Przynależność użytkownika do działów i grup

Użytkownik może należeć do wielu działów lub grup jednocześnie.

Należy rozróżnić:

* **Główną przynależność** – podstawowy dział/grupa użytkownika.

* **Dodatkowe przynależności** – pozostałe działy lub grupy, w których
  użytkownik może wykonywać pracę.

Dodatkowe przypisania będą wykorzystywane incydentalnie i nie mogą
automatycznie zmieniać głównej przynależności użytkownika.

Przykład: operator laserów może jednorazowo pomagać w pakowalni. Nadal
pozostaje przypisany do swojego głównego działu, ale może otrzymywać
dodatkowe przypisania związane z innym działem.

Brygadzista musi być przypisany do działu lub działów, nad którymi
sprawuje nadzór. Nie musi nadzorować tylko jednego działu.

## 14.4. Funkcje i uprawnienia użytkowników

Użytkownik może mieć jednocześnie kilka funkcji, np. pracownik,
brygadzista i kierownik.

System powinien mieć domyślne zestawy uprawnień wynikające z funkcji
użytkownika lub typu pracownika. **Administrator ma pełną dowolność
w definiowaniu własnych funkcji, tworzeniu dla nich zestawów domyślnych
uprawnień oraz ich nadawaniu.** Ponadto administrator musi mieć możliwość
indywidualnego nadawania i odbierania konkretnych uprawnień dla wybranego
użytkownika lub całej grupy (np. uprawnienia do edycji terminów czy zmiany
statusów).

Administrator może również nadać wybranemu użytkownikowi funkcję
**Administratora**, co daje takiej osobie pełny dostęp do wszystkich
funkcji i danych w systemie.

Uprawnienia powinny być możliwe do skonfigurowania niezależnie od samej
nazwy funkcji. Należy rozdzielić:

* funkcję użytkownika;

* zakres danych, do których ma dostęp;

* konkretne czynności, które może wykonywać.

Wstępne zasady widoczności:

* pracownik produkcji widzi wszystkie zgłoszenia i zamówienia indeksów,
  natomiast w obszarze zadań widzi wyłącznie zadania przeznaczone dla
  jego grupy oraz zadania indywidualnie mu przypisane (szczegóły w sekcji 14.12);

* brygadzista widzi zadania działu lub działów, do których został
  przypisany;

* kierownik i osoba zarządzająca produkcją mają dostęp do wszystkich
  informacji dotyczących zadań i produkcji;

* administrator zarządza konfiguracją, użytkownikami i uprawnieniami
  oraz posiada dostęp do wszystkich obszarów systemu.

Powyższe zasady stanowią domyślne zachowanie. Indywidualne uprawnienia
użytkownika lub grupy mogą je rozszerzać lub ograniczać zgodnie z konfiguracją
administratora. Uprawnienia muszą być weryfikowane po stronie serwera.

## 14.5. Przydzielanie i widoczność zadań

Zadania mogą być kierowane do:

* całego działu lub grupy – zadanie ogólne, widoczne dla pracowników
  przypisanych do danego działu/grupy;

* konkretnego pracownika – zadanie indywidualne, widoczne dla wskazanej
  osoby oraz osób mających odpowiedni dostęp nadzorczy, w szczególności
  brygadzisty właściwego działu i kierownika.

**Przekazywanie zadań indywidualnych:** wyłącznie **brygadzista** ma
uprawnienie do przekazania zadania indywidualnego i przypisania go do
innej osoby.

Zadanie ogólne działu nie jest automatycznie przypisane do jednej osoby.
Pracownik, który chce je realizować, klika **„Rozpocznij”**. W ten sposób
staje się uczestnikiem realizacji zadania.

Inni pracownicy, którzy widzą zadanie, mogą dołączyć do jego realizacji
przyciskiem **„Dołącz”**. Zadanie może mieć jednocześnie wielu aktywnych
uczestników.

### 14.5.1. Opuszczanie zadania

Każdy uczestnik może samodzielnie opuścić zadanie w dowolnym momencie,
bez pytania pozostałych uczestników o zgodę i bez konieczności
zakończenia całego zadania.

Przy opuszczaniu zadania:

* system zapisuje dokładną datę i godzinę opuszczenia;

* użytkownik może dodać opcjonalną adnotację wyjaśniającą powód
  opuszczenia, np. „brak kartonów”, „awaria maszyny” lub „przejście do
  innego zadania”;

* komentarz nie jest wymagany i jego brak nie może blokować opuszczenia;

* opuszczenie zadania nie zmienia automatycznie statusu całego zadania
  na zrealizowane.

Jeżeli jedna osoba opuści zadanie, a pozostali uczestnicy nadal je
realizują, zadanie pozostaje w trakcie i pozostali mogą kontynuować pracę.

Jeżeli ostatni aktywny uczestnik opuszcza zadanie bez jego zakończenia,
zadanie pozostaje niezrealizowane i może zostać ponownie podjęte przez
uprawnionego pracownika.

### 14.5.2. Kończenie zadania

Każdy aktywny uczestnik może samodzielnie oznaczyć całe zadanie jako
**zrealizowane**, jeżeli uzna, że zostało wykonane.

Nie jest wymagana zgoda pozostałych uczestników. Jeżeli zadanie
realizuje kilka osób, każda z nich może zakończyć całe zadanie dla
wszystkich uczestników.

**Potwierdzenie zakończenia (monit UX):** przed zatwierdzeniem zakończenia
zadania system musi wyświetlić użytkownikowi okno dialogowe (monit) z
pytaniem potwierdzającym chęć zakończenia oraz listą wszystkich aktualnie
aktywnych uczestników zadania, np.: *„Czy na pewno chcesz zakończyć
zadanie, w którym aktualnie pracują: [lista aktywnych pracowników]?”*.

Zakończenie zadania kończy udział wszystkich aktywnych uczestników i
powinno zostać zapisane w historii wraz z informacją:

* kto zakończył zadanie;

* kiedy to nastąpiło;

* jaki status został ustawiony;

* jacy uczestnicy byli aktywni w momencie zakończenia.

Zdarzenie zakończenia musi być widoczne w historii zadania dla osób,
które mają dostęp do tego zadania.

### 14.5.3. Ponowne dołączanie

Pracownik może dołączyć do tego samego zadania ponownie dowolną liczbę
razy, również po wcześniejszym opuszczeniu go.

Każde ponowne rozpoczęcie udziału tworzy nowy, odrębny wpis
uczestnictwa. Wcześniejsze wpisy nie mogą być nadpisywane ani usuwane.

### 14.5.4. Historia uczestnictwa i szczegóły zadania

Każda osoba, która otworzy szczegóły zadania i ma prawo dostępu do tego
zadania, powinna widzieć szczegółową historię uczestnictwa.

Historia powinna pokazywać wszystkich pracowników, którzy kiedykolwiek
podjęli zadanie, a dla każdego okresu uczestnictwa co najmniej:

* imię i nazwisko pracownika;

* datę i godzinę rozpoczęcia udziału;

* datę i godzinę opuszczenia zadania, jeżeli nastąpiło;

* informację, czy dana osoba nadal uczestniczy w realizacji;

* opcjonalną adnotację dodaną przy opuszczaniu zadania.

Jeżeli ta sama osoba dołączała do zadania kilka razy, każdy okres
uczestnictwa powinien być pokazany jako osobny wpis.

Historia powinna być trwała i nie może znikać po ponownym dołączeniu,
opuszczeniu ani zakończeniu zadania.

## 14.6. Zamówienia materiałów / indeksów przez produkcję

Aplikacja powinna posiadać obszar umożliwiający pracownikom zgłaszanie
potrzeby zamówienia brakującego materiału lub indeksu.

Każdy użytkownik powinien mieć dostęp do wszystkich zamówień – bez ograniczenia
wynikającego z działu lub funkcji. Zamówienia oraz zgłoszenia prezentowane
są w dwóch głównych widokach (zakładkach):

* **Otwarte** – zawierające aktywne zgłoszenia i zamówienia w trakcie realizacji;

* **Zrealizowane** – zawierające historyczne, zakończone pozycje.

### 14.6.1. Wyszukiwanie aktywnych zamówień

Przed utworzeniem kolejnego zamówienia pracownik powinien móc
wyszukać indeks lub materiał wśród już istniejących zamówień w widoku **Otwarte**.

Wyniki wyszukiwania powinny pozwalać ustalić, czy dany indeks został
już zamówiony, oraz pokazywać co najmniej datę złożenia zamówienia.

Celem jest ograniczenie wielokrotnego zamawiania tego samego materiału
bez sprawdzenia wcześniejszych zgłoszeń.

### 14.6.2. Zamówienia zrealizowane

Zrealizowane zamówienia dostępne są w osobnym oknie/widoku **Zrealizowane**.

Widok ten również musi posiadać wyszukiwarkę, aby można było sprawdzić,
czy dany indeks był wcześniej zamawiany i kiedy miało miejsce ostatnie
zamówienie.

Historia zamówień musi umożliwiać wyszukiwanie zarówno wśród zamówień
aktywnych, jak i zrealizowanych.

## 14.7. Wpływ zmian organizacyjnych na historię

Historia zadań i uczestnictwa musi zachować informacje o osobach,
które brały udział w realizacji, nawet jeżeli później zmieni się ich
główny dział, dodatkowa przynależność, funkcja lub stanowisko.

Zmiana przypisania organizacyjnego użytkownika nie może przepisywać
ani usuwać historycznych wpisów uczestnictwa.

## 14.8. Konsekwencje dla modelu danych

Powyższe wymagania należy uwzględnić podczas projektowania bazy danych.
W szczególności model powinien umożliwiać:

* dynamiczną, hierarchiczną strukturę organizacyjną o dowolnej
  głębokości;

* wiele przypisań użytkownika do działów i grup z rozróżnieniem
  przynależności głównej i dodatkowej;

* wiele funkcji przypisanych do jednego użytkownika oraz pełną
  konfigurowalność funkcji i zestawów uprawnień przez administratora;

* domyślne uprawnienia dla funkcji oraz indywidualne nadpisania uprawnień
  dla grup i pojedynczych użytkowników (np. edycja terminów, zmiana statusów);

* przypisanie zadania do działu/grupy albo konkretnego użytkownika wraz
  z historią przekazania zadania przez brygadzistę;

* wielu równoczesnych uczestników jednego zadania oraz automatyczne
  domknięcie aktywnych sesji uczestnictwa przy zakończeniu zadania;

* wiele okresów uczestnictwa tej samej osoby w tym samym zadaniu;

* osobny czas rozpoczęcia i opuszczenia dla każdego okresu
  uczestnictwa;

* opcjonalną adnotację przy opuszczeniu;

* trwałą historię zakończenia zadania;

* wyszukiwanie zamówień materiałów wśród aktywnych (Otwarte) i zrealizowanych
  rekordów;

* rozróżnienie rodzajów zgłoszeń oraz powiązanie wielu pozycji z jednym
  zgłoszeniem (w tym osobnych komentarzy dodawanych przy tworzeniu,
  opcjonalnych ilości i jednostek miary: `szt.`, `metry`);

* opcjonalne terminy realizacji zgłoszeń;

* rejestrowanie historii nadawania i zmian priorytetów (`Normalny`, `Pilny`)
  dla zgłoszeń oraz zadań produkcyjnych.

To są wymagania biznesowe. Dokładne nazwy tabel, relacje, ograniczenia
i sposób implementacji zostaną ustalone podczas projektowania bazy
danych.

## 14.9. Rodzaje zgłoszeń i obowiązkowość indeksu ERP

Przy tworzeniu zgłoszenia użytkownik musi mieć możliwość wyboru rodzaju
zgłoszenia spośród dwóch opcji:

1. **Zamawianie indeksów** – zgłoszenie potrzeby zamówienia lub
   uzupełnienia materiałów.

2. **Inne zgłoszenie** – zgłoszenie problemu, awarii, potrzeby lub innej
   sprawy wymagającej obsługi przez biuro.

Obowiązek podania indeksu ERP zależy od wybranego rodzaju zgłoszenia.
Zgłoszenie typu **„Inne zgłoszenie”** może zostać utworzone bez
podawania indeksu ERP.

## 14.10. Wiele pozycji w jednym zgłoszeniu i dane pozycji

Jedno zgłoszenie może zawierać wiele indeksów ERP lub pozycji.

Zasady działania formularza zgłoszenia:

* formularz rozpoczyna się od jednego wpisu (jednej pozycji);

* użytkownik może kliknąć przycisk **„Dodaj kolejną pozycję”**;

* pod istniejącą pozycją dynamicznie pojawia się kolejny zestaw pól;

* użytkownik może dodawać dowolną liczbę pozycji;

* każda pozycja posiada własne, niezależne dane;

* dane jednej pozycji nie mogą automatycznie nadpisywać ani kopiować się
  do pozostałych pozycji.

Każda pozycja w zgłoszeniu (w tym zamówieniu materiałów) zawiera następujące pola:

* **indeks ERP** (wymagany przy zamawianiu indeksów);

* **ilość** (opcjonalnie);

* **jednostka miary** (opcjonalnie – dostępne wartości: **szt.**, **metry**);

* **komentarz** lub dodatkowe informacje przypisane do konkretnej pozycji.

### 14.10.1. Opcjonalność ilości i jednostki miary

Ilość oraz jednostka miary są polami całkowicie opcjonalnymi.

Pracownik może:

* zamówić konkretną ilość materiału;

* zgłosić, że materiału jest mało, bez podawania aktualnej ilości;

* zgłosić potrzebę uzupełnienia zapasu bez określania ilości zamawianej.

**Wymaganie dotyczące interfejsu (UX):** interfejs użytkownika musi
wyraźnie sugerować, że ilość i jednostka miary są opcjonalne. Brak tych
informacji nie może powodować błędów walidacji ani sugerować, że
zgłoszenie jest niekompletne.

## 14.11. Hierarchia nadawania i zmiany priorytetów

W systemie dostępne są dwa poziomy priorytetów (zarówno dla zgłoszeń,
jak i dla zadań produkcyjnych):

1. **Normalny**

2. **Pilny**

Ustalono wspólną logikę zarządzania priorytetami dla obu obszarów aplikacji:

Czynność                        Zgłoszenie                  Zadanie produkcyjne

Nadanie priorytetu              Zamawiający                 Zlecający pracę
Zmiana priorytetu               Brygadzista / kierownik     Brygadzista / kierownik
Zmiana przez zwykłego pracownika Niedozwolona               Niedozwolona

### 14.11.1. Priorytet zgłoszenia / zamówienia

Użytkownik          Może nadać priorytet            Może zmienić priorytet

Zamawiający         Tak                             Nie
Brygadzista         Tak                             Tak
Kierownik           Tak                             Tak
Zwykły pracownik    Zgodnie z rolą zamawiającego    Nie

Zamawiający może określić ważność swojego zgłoszenia już podczas jego
tworzenia. Brygadzista i kierownik mogą później zmienić priorytet zgodnie
z zakresem swoich uprawnień. Zwykły pracownik nie może zmienić
priorytetu po utworzeniu zgłoszenia.

### 14.11.2. Priorytet zadania produkcyjnego

Użytkownik                            Może nadać priorytet   Może zmienić priorytet

Osoba zlecająca pracę                 Tak                    Nie
Brygadzista                           Tak                    Tak
Kierownik                             Tak                    Tak
Zwykły pracownik realizujący zadanie  Nie                    Nie

Osoba zlecająca pracę określa priorytet podczas tworzenia zadania.
Brygadzista i kierownik mogą modyfikować ten priorytet na późniejszym
etapie. Pracownik wykonujący zadanie nie może samodzielnie nadawać ani
zmieniać jego priorytetu.

### 14.11.3. Historia priorytetów

Każde nadanie lub zmiana priorytetu (zarówno w zgłoszeniach, jak i w
zadaniach produkcyjnych) musi być trwale rejestrowana w historii.

Wpis w historii priorytetów musi zawierać co najmniej:

* poprzedni priorytet (lub informację o jego pierwszym nadaniu);

* nowy priorytet;

* osobę wykonującą czynność;

* dokładną datę i godzinę zmiany.

## 14.12. Widoczność, terminy realizacji, statusy i komentarze w zgłoszeniach

### 14.12.1. Widoczność zgłoszeń a widoczność zadań

Należy zachować wyraźne rozróżnienie widoczności między dwoma głównymi procesami:

* **Zgłoszenia i zamówienia indeksów:** pracownik produkcji widzi **wszystkie**
  zgłoszenia i zamówienia w systemie (nie tylko swoje), podzielone na dwie
  zakładki/okna: **Otwarte** oraz **Zrealizowane**.

* **Zadania produkcyjne:** pracownik produkcji widzi **wyłącznie** zadania
  przypisane bezpośrednio do niego lub do grupy/działu, którego jest członkiem.

### 14.12.2. Terminy realizacji zgłoszeń

Zgłoszenia mogą posiadać **termin realizacji**, ale pole to jest **opcjonalne**.

**Uprawnienia do edycji terminów:**

* Administrator musi mieć w interfejsie administracyjnym możliwość nadania
  uprawnienia do edycji terminów wybranym grupom lub konkretnym użytkownikom.

* Użytkownik z nadaną funkcją Administratora posiada dostęp do edycji terminów
  oraz wszystkich innych operacji w systemie.

### 14.12.3. Zmiana statusów zgłoszeń i zamówień

Domyślnie statusy zgłoszeń oraz zamówień indeksów mogą zmieniać:

* pracownik biurowy;

* osoba, która zleciła dane zamówienie / utworzyła zgłoszenie;

* brygadzista;

* administrator.

Interfejs zarządzania uprawnieniami musi pozwalać administratorowi na
elastyczne nadawanie i odbieranie uprawnień do zmiany statusów poszczególnym
grupom użytkowników.

### 14.12.4. Zasady komentowania zgłoszeń

Aplikacja **nie pełni roli komunikatora** i nie przewiduje prowadzenia
wielowątkowej wymiany wiadomości (czatu) pod zgłoszeniem.

Pracownik może dodać komentarz wyłącznie w momencie tworzenia zgłoszenia
(jako opis/uwagi do poszczególnych pozycji).

## 14.13. Powiadomienia w czasie rzeczywistym oraz obsługa kodów kreskowych

### 14.13.1. Komunikaty ekranowe w czasie rzeczywistym

System musi wyświetlać bezpośrednie komunikaty (powiadomienia na ekranie)
użytkownikom, którzy mają aktualnie otwartą stronę aplikacji w przeglądarce:

* **Pracownik biurowy** otrzymuje komunikat natychmiast po pojawieniu się
  nowego wpisu (zgłoszenia/zamówienia) z produkcji.

* **Pracownik produkcji** otrzymuje komunikat natychmiast po pojawieniu się
  nowego wpisu lub zadania, które bezpośrednio go dotyczy.

### 14.13.2. Skanowanie kodów kreskowych

W pierwszej wersji (MVP) aplikacji funkcja skanowania kodów nie będzie
implementowana.

Skanowanie zostanie dodane w późniejszym etapie rozwoju systemu i będzie
obsługiwać kody w standardzie **Code-128** (oraz opcjonalnie kody 2D).

## 14.14. Kwestie nadal otwarte

Poniższe kwestie nie zostały jeszcze rozstrzygnięte:

1. Jakie dokładnie informacje i operacje mają być wymieniane z ERP podczas
   docelowej integracji?

2. Jakie dokładnie statusy (poza podziałem na widoki Otwarte i Zrealizowane)
   będą obowiązywały dla zamówień materiałów i zgłoszeń?