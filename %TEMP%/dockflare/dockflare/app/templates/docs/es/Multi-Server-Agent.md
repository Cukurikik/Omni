# DockFlare Agent y arquitectura multiservidor

DockFlare 3.0 introduce un modelo de ejecución distribuido que le permite gestionar túneles de Cloudflare en varios hosts Docker. El **Master** de DockFlare coordina la configuración, mientras que los **agentes** ligeros se ejecutan junto a sus cargas de trabajo y mantienen sincronizada su instancia local de `cloudflared`.

Esta guía explica la arquitectura, el modelo de seguridad y el flujo de trabajo paso a paso para desplegar agentes.

---

## ¿Por qué usar agentes?

- **Separar la ejecución de la capa de ingress**: mantenga las cargas de trabajo cerca de los usuarios sin perder un único plano de control.
- **Visibilidad por host**: supervise el heartbeat, el estado del túnel y el historial de comandos de cada agente.
- **Tokens de privilegio mínimo**: revoque agentes comprometidos sin afectar al Master ni a otros hosts.
- **Actualizaciones resilientes**: los agentes siguen sirviendo tráfico con su última configuración conocida si el Master no está disponible temporalmente.

---

## Componentes de un vistazo

| Componente             | Responsabilidad                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| **Master (DockFlare)** | Aloja la interfaz web, almacena el estado, reconcilia las reglas ingress deseadas y emite comandos.       |
| **Redis**              | Capa compartida para caché, heartbeats de agentes y comandos en cola.                                     |
| **DockFlare Agent**    | Contenedor sin interfaz que observa eventos locales de Docker, ejecuta comandos y gestiona `cloudflared`. |
| **cloudflared**        | Gestiona la conexión real del túnel a Cloudflare para cada agente.                                        |

El Master y Redis suelen ejecutarse juntos, mientras que los agentes se ejecutan junto a las cargas de trabajo, incluso en redes remotas.

---

## Requisitos previos

- DockFlare Master ≥ v3.0 con Redis configurado (`REDIS_URL` definido). De forma opcional, especifique `REDIS_DB_INDEX` para aislar los datos de otros contenedores que usen la misma instancia de Redis.
- Token API de Cloudflare con permisos de Tunnel + Access, igual que en versiones anteriores.
- Docker en cada host que planee gestionar.
- (Opcional) Un segmento de red dedicado o una VPN entre el Master y los agentes si no expone el Master públicamente.

---

## Resumen del flujo de trabajo

1. **Genere una clave API de agente** en la interfaz web de DockFlare (`Agents → Generate Key`).
2. **Despliegue el contenedor DockFlare Agent** en el host remoto, proporcionando la URL del Master y la clave.
3. El agente **se registra** en el Master y aparece con estado _Pending_.
4. Desde la interfaz web del Master, **apruebe** el agente y asígnele o cree un túnel de Cloudflare para ese host.
5. El Master pone los comandos en cola; el agente los recupera, aplica la configuración e informa del estado y del heartbeat. DockFlare detecta automáticamente la zona de destino para cada nombre de host y solo recurre a la zona predeterminada cuando la detección falla.
6. A medida que los contenedores se inician o se detienen en el host del agente, este transmite los eventos de vuelta al Master, que actualiza DNS, las políticas de Access y las reglas ingress del túnel.

---

## Despliegue del DockFlare Agent

El agente se publica como `alplat/dockflare-agent:latest` en Docker Hub.

Existen dos métodos de despliegue — elija el que mejor se adapte a su configuración:

### Opción A — Script de despliegue en una línea (recomendado, opt-in)

Si ha configurado **Cloudflare Zero Trust** en el Master (`Agents → Setup Zero Trust`), DockFlare puede generar un script bash completamente preconfigurado para cada clave API de agente. El script:

- Comprueba que `docker compose` está disponible
- Crea la red Docker `cloudflare-net` si no existe
- Escribe un archivo `docker-compose.yml` con los cuatro valores requeridos incorporados (`DOCKFLARE_MASTER_URL`, `DOCKFLARE_API_KEY`, `CF_ACCESS_CLIENT_ID`, `CF_ACCESS_CLIENT_SECRET`)
- Inicia la pila del agente de inmediato

Para utilizarlo: vaya a `Agents → (fila de clave) → Deploy Agent → Quick Deploy`, copie el script y péguelo en una sesión SSH en el servidor de destino. No es necesario configurar un archivo `.env`.

> Esta opción requiere que la funcionalidad de Cloudflare Zero Trust esté configurada en el Master. Consulte la sección [Modelo de seguridad](#modelo-de-seguridad) para más detalles.

### Opción B — Configuración manual con Compose

Para entornos donde gestiona sus propios archivos de configuración:

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

`docker-compose.yml` mínimo en el host del agente:

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

- Ejecute `docker network create cloudflare-net` una vez para aprovisionar la red compartida utilizada por el Master y los agentes.
- El socket proxy limita la superficie de la API de Docker a la que puede acceder el agente; solo se exponen las capacidades configuradas con `1`.
- La imagen del agente se ejecuta como el usuario sin privilegios `dockflare` (UID/GID 65532). Asegúrese de que los directorios montados, como `/app/data`, sean escribibles por esa cuenta.
- Complete un archivo `.env` con al menos `DOCKFLARE_MASTER_URL` y `DOCKFLARE_API_KEY`; todas las demás variables son anulaciones opcionales.

---

## Modelo de seguridad

- **Clave API del Master**: protege la API administrativa. La interfaz web solo la muestra después de hacer clic en _Show master API key_.
- **Claves API de agente**: únicas por agente. Revocar una clave bloquea inmediatamente nuevas inscripciones y comandos desde ese host.
- **Tokens de servicio de Cloudflare Zero Trust** _(opt-in)_: cuando están configurados, DockFlare crea una aplicación de Cloudflare Access limitada a `/api/v2/agents/` con una política `non_identity`. Los agentes presentan las cabeceras `CF-Access-Client-Id` y `CF-Access-Client-Secret` en cada solicitud, que Cloudflare valida en el edge antes de que el tráfico llegue al Master. Esto añade una segunda capa de autenticación además de la clave API del agente. El acceso por navegador de los administradores sigue funcionando mediante una política `bypass` en la misma aplicación. Actívelo desde `Agents → Setup Zero Trust`.
- **Redis**: se usa para colas y cachés; protéjalo con contraseña y ACL de red si se ejecuta fuera de una LAN de confianza.
- **Transporte**: ejecute el Master detrás de HTTPS, por ejemplo mediante Cloudflare Tunnel, para que el tráfico del agente vaya cifrado en tránsito.
- **Ejecución de privilegio mínimo**: el contenedor del agente se ejecuta como el usuario `dockflare` (UID/GID 65532) y depende del socket proxy para limitar el acceso a Docker a la inspección de contenedores y al control de su ciclo de vida.

### Endurecimiento recomendado

1. Guarde las claves de agente en una bóveda o gestor de contraseñas y rótelas periódicamente.
2. Active **Cloudflare Zero Trust** en el Master para una capa de autenticación adicional en el edge de Cloudflare (`Agents → Setup Zero Trust`).
3. **No desactive el inicio de sesión con contraseña** — use proveedores OAuth/OIDC para obtener la comodidad del single sign-on sin asumir riesgos de seguridad. Si debe desactivarlo, tenga en cuenta que esto crea una vulnerabilidad de red en Docker por la que cualquier contenedor de la misma red puede eludir la autenticación externa. Consulte [Acceso a la interfaz web - Desactivar el inicio de sesión con contraseña](Accessing-the-Web-UI.md#disabling-password-login) para ver todas las implicaciones de seguridad.
4. Utilice túneles independientes por agente para mantener el aislamiento de privilegio mínimo.
5. Supervise la página `Agents` para detectar huecos en el heartbeat. Los nodos sin conexión pueden eliminarse directamente desde la interfaz.

---

## Solución de problemas

| Síntoma                           | Solución                                                                                                                        |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| El agente se queda en `pending`   | Asegúrese de que se haya registrado con la clave API correcta y apruébelo desde la interfaz web.                                |
| Los comandos no desaparecen nunca | Confirme la conectividad con Redis y que los relojes de los contenedores del agente estén sincronizados.                        |
| DNS no se actualiza               | El Master debe poder llegar a Cloudflare y el agente debe enviar eventos de contenedores; revise `docker logs dockflare-agent`. |
| Heartbeat offline                 | Compruebe la ruta de red entre el agente y el Master; los problemas de firewall o TLS son causas habituales.                    |

---

## Próximos pasos

- Revise la guía de inicio rápido en el README del repositorio para confirmar que Redis está configurado.
- Consulte el registro de cambios para ver cambios incompatibles y notas de migración.
- Considere activar Cloudflare Zero Trust para una autenticación reforzada de los agentes (`Agents → Setup Zero Trust`).

Buena gestión de túneles. 🚇
