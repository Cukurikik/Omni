# DockFlare-Agent und Multi-Server-Architektur

DockFlare 3.0 führt ein verteiltes Ausführungsmodell ein, mit dem Sie Cloudflare-Tunnel über mehrere Docker-Hosts hinweg verwalten können. Der DockFlare **Master** koordiniert die Konfiguration, während leichtgewichtige **Agenten** neben Ihren Workloads laufen und ihre lokale `cloudflared`-Instanz mit dem Master synchron halten.

Dieser Leitfaden erklärt die Architektur, das Sicherheitsmodell und den schrittweisen Workflow für die Bereitstellung von Agenten.

---

## Warum Agenten?

- **Compute von der Ingress-Steuerung entkoppeln** – halten Sie Ihre Workloads in der Nähe der Benutzer, während Sie eine einzige Kontrollebene beibehalten.
- **Sichtbarkeit pro Host** – überwachen Sie Heartbeat, Tunnelstatus und Befehlshistorie für jeden Agenten.
- **Token mit geringsten Rechten** – kompromittierte Agenten können widerrufen werden, ohne den Master oder andere Hosts anzutasten.
- **Erhöhte Ausfallsicherheit** – Agenten bedienen den Verkehr weiterhin mit ihrer zuletzt bekannten Konfiguration, wenn der Master vorübergehend nicht erreichbar sein sollte.

---

## Komponenten im Überblick

| Komponente             | Verantwortlichkeit                                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| **Master (DockFlare)** | Hostet die Web-UI, speichert den Status, gleicht gewünschte Ingress-Regeln ab und erteilt Befehle.        |
| **Redis**              | Backplane für Caching, Agenten-Heartbeats und anstehende Befehle in der Warteschlange.                    |
| **DockFlare Agent**    | Headless-Container, der lokale Docker-Ereignisse beobachtet, Befehle ausführt und `cloudflared` betreibt. |
| **cloudflared**        | Behandelt die eigentliche Tunnelverbindung zu Cloudflare pro Agent.                                       |

Master und Redis laufen typischerweise zusammen, während Agenten neben Workloads laufen (möglicherweise in anderen Netzwerken).

---

## Voraussetzungen

- DockFlare Master ≥ v3.0 mit konfiguriertem Redis (`REDIS_URL` gesetzt). Optional können Sie `REDIS_DB_INDEX` festlegen, um Daten von anderen Containern zu isolieren, die dieselbe Redis-Instanz verwenden.
- Cloudflare API-Token mit Tunnel- + Access-Berechtigungen (gleich wie in früheren Versionen).
- Docker-Laufzeit auf jedem Host, den Sie verwalten möchten.
- (Optional) Spezielles Netzwerksegment oder VPN zwischen Master und Agenten, wenn Sie den Master nicht öffentlich zugänglich machen.

---

## Workflow-Übersicht

1. **Agenten-API-Schlüssel generieren** in der DockFlare UI (`Agents → Generate Key`).
2. **DockFlare Agent-Container ausrollen** auf dem Remote-Host, wobei Master-URL und Schlüssel übergeben werden.
3. Der Agent **registriert** sich beim Master und erscheint mit dem Status _Pending_.
4. In der Master-UI **enrolen Sie den Agenten** (freischalten) – weisen Sie ihm einen Cloudflare Tunnel zu oder erstellen Sie einen neuen Tunnel für diesen Host.
5. Der Master reiht Befehle ein; der Agent **ruft diese ab (polls)**, wendet die Konfiguration an und meldet Status/Heartbeat. DockFlare erkennt die Zielzone für jeden Hostnamen automatisch (und fällt nur auf die Standardzone zurück, wenn die Erkennung fehlschlägt).
6. Wenn Container auf dem Host des Agenten gestartet oder gestoppt werden, streamt der Agent Ereignisse an den Master zurück, der wiederum DNS, Zugriffsrichtlinien und Tunnel-Eingangsregeln aktualisiert.

---

## Bereitstellung des DockFlare Agenten

Der Agent wird als `alplat/dockflare-agent:latest` auf Docker Hub veröffentlicht.

Es gibt zwei Bereitstellungsmethoden – wählen Sie die für Ihr Setup passende:

### Option A – Einzeiler-Bereitstellungsskript (empfohlen, Opt-in)

Wenn Sie **Cloudflare Zero Trust** auf dem Master konfiguriert haben (`Agents → Setup Zero Trust`), kann DockFlare für jeden Agenten-API-Schlüssel ein vollständig vorkonfiguriertes Bash-Skript generieren. Das Skript:

- Prüft, ob `docker compose` verfügbar ist
- Erstellt das Docker-Netzwerk `cloudflare-net`, falls es noch nicht existiert
- Schreibt eine `docker-compose.yml` mit allen vier erforderlichen Werten (`DOCKFLARE_MASTER_URL`, `DOCKFLARE_API_KEY`, `CF_ACCESS_CLIENT_ID`, `CF_ACCESS_CLIENT_SECRET`)
- Startet den Agenten-Stack sofort

Zur Verwendung: gehen Sie zu `Agents → (Schlüsselzeile) → Deploy Agent → Quick Deploy`, kopieren Sie das Skript und fügen Sie es in eine SSH-Sitzung auf dem Zielserver ein. Es ist keine `.env`-Datei erforderlich.

> Diese Option erfordert, dass das Cloudflare Zero Trust-Feature auf dem Master konfiguriert ist. Details finden Sie im Abschnitt [Sicherheitsmodell](#sicherheitsmodell).

### Option B – Manuelle Compose-Konfiguration

Für Umgebungen, in denen Sie Ihre eigenen Konfigurationsdateien verwalten:

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

Minimale `docker-compose.yml` auf dem Agenten-Host:

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

- Führen Sie `docker network create cloudflare-net` einmal aus, um das gemeinsame Netzwerk für Master und Agenten bereitzustellen.
- Der Socket-Proxy begrenzt die Docker-API-Oberfläche, die der Agent erreichen kann; nur die auf `1` gesetzten Fähigkeiten sind erreichbar.
- Das Agenten-Image läuft als der unprivilegierte `dockflare`-Benutzer (UID/GID 65532). Stellen Sie sicher, dass gemountete Verzeichnisse wie `/app/data` von diesem Konto beschrieben werden können.
- Füllen Sie eine `.env`-Datei mit mindestens `DOCKFLARE_MASTER_URL` und `DOCKFLARE_API_KEY` aus; alle anderen Variablen sind optionale Overrides.

---

## Sicherheitsmodell

- **Master API Key** – schützt die administrative API. Die UI zeigt ihn erst an, nachdem Sie auf _Show master API key_ geklickt haben.
- **Agent API Keys** – eindeutig pro Agent. Ein Widerruf sperrt sofort weitere Registrierungen und Befehle von diesem Host.
- **Cloudflare Zero Trust Service-Tokens** _(Opt-in)_ – wenn konfiguriert, erstellt DockFlare eine Cloudflare Access-Anwendung, die auf `/api/v2/agents/` beschränkt ist, mit einer `non_identity`-Richtlinie. Agenten übermitteln bei jeder Anfrage die Header `CF-Access-Client-Id` und `CF-Access-Client-Secret`, die Cloudflare am Edge validiert, bevor der Traffic den Master erreicht. Dies fügt zusätzlich zum Agenten-API-Key eine zweite Authentifizierungsschicht hinzu. Der Browser-Zugriff für Administratoren funktioniert weiterhin über eine `bypass`-Richtlinie auf derselben Anwendung. Aktivieren Sie es über `Agents → Setup Zero Trust`.
- **Redis** – wird für Queues und Caches verwendet; sichern Sie Redis (Passwort + Network ACLs), wenn es außerhalb eines vertrauenswürdigen LANs läuft.
- **Transport** – betreiben Sie den Master hinter HTTPS (zum Beispiel via Cloudflare Tunnel), damit der Agent-Traffic verschlüsselt ist.
- **Least-Privilege Runtime** – der Agent-Container läuft als `dockflare`-User (UID/GID 65532) und verwendet den Socket-Proxy, um Docker-Zugriff auf Container-Inspection und Lifecycle-Operationen zu begrenzen.

### Empfohlene Härtung

1. Bewahren Sie Agent Keys in einem Vault/Passwortmanager auf und rotieren Sie sie regelmäßig.
2. Aktivieren Sie **Cloudflare Zero Trust** auf dem Master für eine zusätzliche Authentifizierungsschicht am Cloudflare-Edge (`Agents → Setup Zero Trust`).
3. **Deaktivieren Sie das Passwort-Login nicht** – verwenden Sie stattdessen OAuth/OIDC-Anbieter für SSO-Komfort ohne Sicherheitsrisiken. Falls Sie das Passwort-Login unbedingt deaktivieren müssen, beachten Sie, dass dies eine Docker-Netzwerk-Sicherheitslücke schafft, durch die Container im selben Netzwerk externe Authentifizierung umgehen können. Details siehe [Zugriff auf die Web-UI - Passwort-Anmeldung deaktivieren](Accessing-the-Web-UI.md#disabling-password-login).
4. Nutzen Sie nach Möglichkeit einen eigenen Tunnel pro Agent, um Privilegien sauber zu isolieren.
5. Überwachen Sie in der UI unter `Agents` Heartbeat-Lücken; offline Nodes können direkt aus der UI entfernt werden.

---

## Fehlerbehebung

| Symptom                          | Lösung                                                                                                                            |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Agent bleibt in `pending`        | Stellen Sie sicher, dass er mit dem richtigen API Key registriert ist, und enrolen Sie ihn in der UI.                             |
| Commands werden nie abgearbeitet | Prüfen Sie die Redis-Konnektivität und dass die Container-Uhren (Clock) synchron sind.                                            |
| DNS wird nicht aktualisiert      | Der Master muss Cloudflare erreichen können und der Agent muss Container-Events senden; prüfen Sie `docker logs dockflare-agent`. |
| Heartbeat ist offline            | Prüfen Sie den Network Path zwischen Agent und Master; häufige Ursachen sind Firewall- oder TLS-Probleme.                         |

---

## Nächste Schritte

- Überprüfen Sie den aktualisierten Schnellstart im README, um sicherzustellen, dass Redis eingerichtet ist.
- Prüfen Sie das Changelog auf Breaking Changes und Migrationshinweise.
- Erwägen Sie, Cloudflare Zero Trust für eine verstärkte Agenten-Authentifizierung zu aktivieren (`Agents → Setup Zero Trust`).

Viel Spaß beim Tunnelbau! 🚇
