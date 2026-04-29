# Agent DockFlare i architektura wieloserwerowa

DockFlare 3.0 wprowadza rozproszony model działania, który pozwala zarządzać tunelami Cloudflare na wielu hostach Docker. **Master** DockFlare koordynuje konfigurację, a lekkie **agenty** działają obok Twoich obciążeń i utrzymują lokalną instancję `cloudflared` w synchronizacji z masterem.

Ten przewodnik wyjaśnia architekturę, model zabezpieczeń i krok po kroku pokazuje wdrożenie agentów.

---

## Dlaczego warto używać agentów?

- **Rozdzielenie warstwy sterowania od warstwy ruchu** – możesz utrzymywać obciążenia blisko użytkowników, zachowując jedną płaszczyznę sterowania.
- **Widoczność na poziomie hosta** – monitorujesz heartbeat, stan tunelu i historię poleceń dla każdego agenta.
- **Tokeny o minimalnych uprawnieniach** – unieważniaj skompromitowanych agentów bez wpływu na Master ani inne hosty.
- **Odporne aktualizacje** – agenci nadal obsługują ruch z ostatnią znaną konfiguracją, jeśli Master jest tymczasowo niedostępny.

---

## Komponenty w skrócie

| Składnik               | Odpowiedzialność                                                                                                  |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Master (DockFlare)** | Udostępnia panel administracyjny, przechowuje stan, uzgadnia docelowe reguły ingress i wydaje polecenia.          |
| **Redis**              | Odpowiada za cache, heartbeat agentów i kolejkę poleceń.                                                          |
| **Agent DockFlare**    | Kontener bez interfejsu, który obserwuje lokalne zdarzenia Dockera, wykonuje polecenia i uruchamia `cloudflared`. |
| **cloudflared**        | Obsługuje rzeczywiste połączenie tunelowe z Cloudflare dla każdego agenta.                                        |

Master i Redis zwykle działają razem, a agenci uruchamiani są obok obciążeń, także w zdalnych sieciach.

---

## Wymagania wstępne

- DockFlare Master ≥ v3.0 ze skonfigurowanym Redisem (`REDIS_URL` ustawione). Opcjonalnie można podać `REDIS_DB_INDEX`, aby odizolować dane od innych kontenerów korzystających z tej samej instancji Redis.
- Token API Cloudflare z uprawnieniami Tunnel + Access, taki sam jak w poprzednich wersjach.
- Środowisko Docker na każdym hoście, którym planujesz zarządzać.
- (Opcjonalnie) Dedykowany segment sieci lub VPN pomiędzy Masterem a agentami, jeśli nie wystawiasz Mastera publicznie.

---

## Przegląd przepływu pracy

1. **Wygeneruj klucz API agenta** w panelu DockFlare (`Agents → Generate Key`).
2. **Wdróż kontener agenta DockFlare** na zdalnym hoście, przekazując adres URL Mastera i klucz.
3. Agent **rejestruje się** w Masterze i pojawia się ze statusem _Pending_.
4. Z poziomu interfejsu Mastera **zatwierdź** agenta i przypisz mu lub utwórz tunel Cloudflare dla tego hosta.
5. Master umieszcza polecenia w kolejce, a agent regularnie je pobiera, stosuje konfigurację i raportuje stan oraz heartbeat. DockFlare automatycznie wykrywa strefę docelową dla każdej nazwy hosta i wraca do strefy domyślnej tylko wtedy, gdy wykrywanie się nie powiedzie.
6. Gdy kontenery są uruchamiane lub zatrzymywane na hoście agenta, agent przesyła zdarzenia z powrotem do Mastera, który aktualizuje DNS, zasady Access i reguły ingress tunelu.

---

## Wdrażanie agenta DockFlare

Agent jest publikowany jako `alplat/dockflare-agent:latest` w Docker Hub.

Dostępne są dwie metody wdrożenia — należy wybrać tę, która odpowiada konfiguracji środowiska:

### Opcja A — Jednolinijkowy skrypt wdrożeniowy (zalecane, opt-in)

Jeśli na Masterze skonfigurowano **Cloudflare Zero Trust** (`Agents → Setup Zero Trust`), DockFlare może wygenerować w pełni wstępnie skonfigurowany skrypt bash dla każdego klucza API agenta. Skrypt:

- Sprawdza, czy `docker compose` jest dostępne
- Tworzy sieć Docker `cloudflare-net`, jeśli nie istnieje
- Zapisuje plik `docker-compose.yml` z wbudowanymi wszystkimi czterema wymaganymi wartościami (`DOCKFLARE_MASTER_URL`, `DOCKFLARE_API_KEY`, `CF_ACCESS_CLIENT_ID`, `CF_ACCESS_CLIENT_SECRET`)
- Natychmiast uruchamia stos agenta

Aby z niego skorzystać: przejdź do `Agents → (wiersz klucza) → Deploy Agent → Quick Deploy`, skopiuj skrypt i wklej go do sesji SSH na docelowym serwerze. Konfiguracja pliku `.env` nie jest wymagana.

> Ta opcja wymaga skonfigurowania funkcji Cloudflare Zero Trust na Masterze. Szczegóły zawiera sekcja [Model zabezpieczeń](#model-zabezpieczeń).

### Opcja B — Ręczna konfiguracja Compose

Dla środowisk, w których samodzielnie zarządzasz plikami konfiguracyjnymi:

```bash
# .env on the agent host
DOCKFLARE_MASTER_URL=https://dockflare.example.com
DOCKFLARE_API_KEY=agent_api_key_goes_here
DOCKER_HOST=tcp://docker-socket-proxy:2375
# Optional: pin the cloudflared image (accepts repo:tag or repo@sha256:<digest>)
# Defaults to cloudflare/cloudflared:latest when not set
CLOUDFLARED_IMAGE=cloudflare/cloudflared:latest
LOG_LEVEL=info
TZ=Europe/Zurich
# Optional: Cloudflare Zero Trust service token (generated by the master)
CF_ACCESS_CLIENT_ID=
CF_ACCESS_CLIENT_SECRET=
```

Minimalny `docker-compose.yml` na hoście agenta:

```yaml
services:
  docker-socket-proxy:
    image: tecnativa/docker-socket-proxy:v0.4.1
    container_name: docker-socket-proxy
    restart: unless-stopped
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock
      - CONTAINERS=1
      - EVENTS=1
      - NETWORKS=1
      - IMAGES=1
      - POST=1
      - PING=1
      - EXEC=1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - dockflare-internal

  dockflare-agent:
    image: alplat/dockflare-agent:latest
    container_name: dockflare-agent
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - DOCKER_HOST=${DOCKER_HOST:-tcp://docker-socket-proxy:2375}
      - TZ=${TZ:-UTC}
      - LOG_LEVEL=${LOG_LEVEL:-info}
    volumes:
      - agent_data:/app/data
    depends_on:
      - docker-socket-proxy
    networks:
      - cloudflare-net
      - dockflare-internal

volumes:
  agent_data:

networks:
  cloudflare-net:
    name: cloudflare-net
    external: true
  dockflare-internal:
    name: dockflare-internal
```

- Uruchom `docker network create cloudflare-net` jeden raz, aby przygotować współdzieloną sieć używaną przez Mastera i agentów.
- Socket proxy ogranicza zakres Docker API dostępny dla agenta; udostępniane są tylko możliwości ustawione na `1`.
- Obraz agenta działa jako nieuprzywilejowany użytkownik `dockflare` (UID/GID 65532). Upewnij się, że zamontowane katalogi, takie jak `/app/data`, są zapisywalne dla tego konta.
- Uzupełnij plik `.env` co najmniej o `DOCKFLARE_MASTER_URL` i `DOCKFLARE_API_KEY`; wszystkie pozostałe zmienne są opcjonalnymi nadpisaniami.

---

## Model zabezpieczeń

- **Klucz API Mastera** – chroni administracyjne API. Interfejs pokazuje go dopiero po kliknięciu _Show master API key_.
- **Klucze API agentów** – unikalne dla każdego agenta. Unieważnienie klucza natychmiast blokuje dalsze rejestracje i polecenia z tego hosta.
- **Tokeny serwisowe Cloudflare Zero Trust** _(opt-in)_ – po skonfigurowaniu DockFlare tworzy aplikację Cloudflare Access o zakresie `/api/v2/agents/` z polityką `non_identity`. Agenci dołączają nagłówki `CF-Access-Client-Id` i `CF-Access-Client-Secret` do każdego żądania, które Cloudflare weryfikuje na krawędzi sieci, zanim ruch dotrze do Mastera. Dodaje to drugą warstwę uwierzytelniania ponad kluczem API agenta. Dostęp przeglądarki administratorów nadal działa dzięki polityce `bypass` w tej samej aplikacji. Włącz przez `Agents → Setup Zero Trust`.
- **Redis** – używany do kolejek i cache; zabezpiecz go hasłem i sieciowymi ACL-ami, jeśli działa poza zaufaną siecią LAN.
- **Transport** – uruchom Mastera za HTTPS, na przykład przez Cloudflare Tunnel, aby ruch agentów był szyfrowany podczas przesyłania.
- **Uruchomienie z minimalnymi uprawnieniami** – kontener agenta działa jako użytkownik `dockflare` (UID/GID 65532) i korzysta z socket proxy, aby ograniczyć dostęp do Dockera do inspekcji kontenerów i sterowania ich cyklem życia.

### Zalecane utwardzenie

1. Przechowuj klucze agentów w sejfie lub menedżerze haseł i regularnie je rotuj.
2. Włącz **Cloudflare Zero Trust** na Masterze, aby uzyskać dodatkową warstwę uwierzytelniania na krawędzi Cloudflare (`Agents → Setup Zero Trust`).
3. **Nie wyłączaj logowania hasłem**. Zamiast tego użyj dostawców OAuth/OIDC, aby zapewnić wygodę single sign-on bez ryzyka dla bezpieczeństwa. Jeśli musisz wyłączyć logowanie hasłem, pamiętaj, że tworzy to lukę w zabezpieczeniach sieci Docker: każdy kontener w tej samej sieci może ominąć zewnętrzne uwierzytelnianie. Zobacz [Accessing the Web UI - Disabling Password Login](Accessing-the-Web-UI.md#disabling-password-login), aby poznać pełne konsekwencje bezpieczeństwa.
4. Używaj oddzielnych tuneli dla każdego agenta, aby zachować izolację minimalnych uprawnień.
5. Monitoruj stronę `Agents` pod kątem przerw w heartbeat; węzły offline można usunąć bezpośrednio z interfejsu.

---

## Rozwiązywanie problemów

| Objaw                           | Rozwiązanie                                                                                                              |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Agent utknął w `pending`        | Upewnij się, że zarejestrował się przy użyciu właściwego klucza API, a następnie zatwierdź go w interfejsie.             |
| Polecenia nie znikają z kolejki | Sprawdź łączność z Redisem i synchronizację zegarów w kontenerach agentów.                                               |
| DNS się nie aktualizuje         | Master musi mieć dostęp do Cloudflare, a agent musi wysyłać zdarzenia kontenerów; sprawdź `docker logs dockflare-agent`. |
| Heartbeat offline               | Sprawdź ścieżkę sieciową między agentem a Masterem; częstą przyczyną są problemy z firewallem lub TLS.                   |

---

## Kolejne kroki

- Przejrzyj Quick Start w README repozytorium, aby upewnić się, że Redis jest skonfigurowany.
- Sprawdź dziennik zmian pod kątem zmian niekompatybilnych i uwag migracyjnych.
- Rozważ włączenie Cloudflare Zero Trust w celu wzmocnienia uwierzytelniania agentów (`Agents → Setup Zero Trust`).

Miłego tunelowania! 🚇
