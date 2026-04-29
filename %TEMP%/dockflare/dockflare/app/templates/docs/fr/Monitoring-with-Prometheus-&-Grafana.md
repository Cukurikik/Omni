# Surveillance avec Prometheus & Grafana

L'agent `cloudflared` géré par DockFlare peut exposer un large éventail de mesures de performances et d'état de santé au format Prometheus. En collectant et en visualisant ces métriques, vous pouvez obtenir des informations précieuses sur le trafic, la latence et les taux d'erreur de votre tunnel.

Ce guide explique comment activer le point de terminaison des métriques et fournit une configuration rapide pour une pile de surveillance à l'aide de Prometheus et Grafana.

## Étape 1 : Activer le point de terminaison des métriques dans DockFlare

La première étape consiste à demander à DockFlare d'activer le point de terminaison des métriques Prometheus sur son agent `cloudflared` géré.

Vous pouvez le faire en définissant la variable d'environnement `CLOUDFLARED_METRICS_PORT` pour votre conteneur DockFlare.

**Exemple `docker-compose.yml` :**

```yaml
services:
  dockflare:
    image: alplat/dockflare:stable
    # ... other settings
    environment:
      # Enable the metrics endpoint on port 2000 inside the container
      - CLOUDFLARED_METRICS_PORT=2000
```

Lorsque vous redémarrez DockFlare avec cette variable, il recréera automatiquement son agent `cloudflared` géré avec le serveur de métriques activé sur le port spécifié.

**Remarque :** Cette fonctionnalité n'est disponible que dans le **Mode interne** par défaut. Si vous utilisez le [Mode externe](External-cloudflared-Mode.md), vous êtes responsable de l'activation du point de terminaison des métriques sur votre propre agent `cloudflared`.

## Étape 2 : Configurer une pile de surveillance

Si vous ne disposez pas déjà d'une pile de surveillance, vous pouvez en configurer une rapidement à l'aide de Docker Compose. Le référentiel DockFlare fournit un exemple de configuration dans le répertoire `/examples`.

Pour un guide complet par copier-coller sur la façon de configurer Prometheus et Grafana pour surveiller DockFlare, veuillez vous référer au fichier **[`grafana quick setup.md`](https://github.com/ChrispyBacon-dev/DockFlare/blob/main/examples/grafana%20quick%20setup.md)** dans le référentiel.

Ce guide vous guidera à travers :

1. Création de la structure de répertoires nécessaire.
2. Ajout des services Prometheus et Grafana à votre `docker-compose.yml`.
3. Configuration de Prometheus pour extraire les métriques de l'agent `cloudflared`.
4. Provisionnement automatique de Grafana avec la source de données Prometheus.

## Étape 3 : Importez le tableau de bord Grafana prédéfini

Pour faciliter la visualisation, DockFlare fournit un tableau de bord Grafana prédéfini conçu pour fonctionner parfaitement avec les métriques exposées par l'agent `cloudflared`.

1. Le tableau de bord est disponible sous **[`dashboard.json`](https://github.com/ChrispyBacon-dev/DockFlare/blob/main/examples/dashboard.json)** dans le répertoire `/examples` du référentiel.
2. Téléchargez ce fichier.
3. Connectez-vous à votre instance Grafana.
4. Allez dans la section « Tableaux de bord » et cliquez sur « Importer ».
5. Téléchargez le fichier `dashboard.json`.
6. Sélectionnez votre source de données Prometheus et importez le tableau de bord.

Vous aurez désormais un aperçu complet des performances de votre tunnel Cloudflare, y compris le nombre de requêtes, les taux d'erreur, la latence de connexion, etc.

![Exemple de tableau de bord Grafana](../static/images/grafana_dashboard_example.png)
