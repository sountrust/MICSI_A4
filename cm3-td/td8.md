# TD 8 — Déploiement d’applications avec Helm dans Kubernetes

Ce TD a pour objectif de vous familiariser avec Helm, l’outil de packaging pour Kubernetes. Vous apprendrez à l’installer, à gérer les dépôts de charts, à rechercher, installer, mettre à jour et supprimer une application complète (WordPress + MariaDB).

Vous devrez fournir des captures d’écran à chaque étape importante afin de prouver l’exécution des commandes.

---

## 1. Présentation de Helm

Helm a été conçu pour simplifier l’installation, la gestion et la mise à jour d’applications dans Kubernetes. Avant son apparition, chaque administrateur devait maintenir manuellement de nombreux fichiers YAML et orchestrer les installations de logiciels complexes (Elasticsearch, Prometheus, Grafana, WordPress, etc.).

Les charts Helm permettent d’automatiser ce travail et d’éviter les erreurs de configuration.

Helm fonctionne en version 3 comme un client autonome s’appuyant directement sur l’API Kubernetes. Il ne dépend ni de kubectl, ni d’un composant serveur supplémentaire (Tiller n’existe plus depuis Helm 2).

---

## 2. Déploiement de Helm

### 2.1 Installation du client Helm

#### a. Installation avec Arkade

L’installation la plus simple se fait via Arkade :

```
arkade get helm
```

Après téléchargement, Arkade annonce l’installation du binaire.

**Capture attendue :** fin de l’installation.

Pour installer une version spécifique :

```
arkade get helm@v3.14.2
```

#### b. Installation manuelle

Si vous n’utilisez pas Arkade :

```
wget https://get.helm.sh/helm-v3.15.2-linux-amd64.tar.gz
tar xfvz helm-v3.15.2-linux-amd64.tar.gz
sudo cp linux-amd64/helm /usr/local/bin/helm
```

Vérifiez le bon fonctionnement :

```
helm
```

Affichez ensuite la version :

```
helm version
```

**Capture attendue :** sortie de `helm version`.

### 2.2 Utilisation du même contexte que kubectl

Helm utilise automatiquement le fichier `~/.kube/config`.

Si `kubectl` fonctionne, Helm fonctionnera également.

---

## 3. Recherche et ajout de charts Helm

### 3.1 Recherche d’un chart

Testez la recherche d’un chart WordPress :

```
helm search repo wordpress
```

Lors du premier essai, aucun résultat n’apparaît car aucune source de charts n’est configurée.

### 3.2 Ajout du dépôt Bitnami

Ajoutez la source de charts Bitnami :

```
helm repo add bitnami https://charts.bitnami.com/bitnami
```

Listez les dépôts configurés :

```
helm repo list
```

**Capture attendue :** dépôt Bitnami présent.

### 3.3 Mise à jour du cache Helm

```
helm repo update
```

Recherchez à nouveau WordPress :

```
helm search repo wordpress
```

Vous devez maintenant voir au moins :

- `bitnami/wordpress`

**Capture attendue :** sortie montrant `bitnami/wordpress`.

---

## 4. Installation du chart WordPress

### 4.1 Terminologie

- Le **chart** est le package Helm (ex. : `bitnami/wordpress`).
- L’**installation** est une instance du chart (ex. : `wordpress`, `wordpress-compta`).

### 4.2 Installation initiale

Installez WordPress dans le namespace `default` :

```
helm install wordpress bitnami/wordpress
```

Helm affiche un résumé complet de l’installation.

**Capture attendue :** sortie complète du déploiement, avec `STATUS = deployed`.

Si vous n’avez pas accès à Helm sur la machine exécutant kubectl, vous pouvez générer les YAML :

```
helm template wordpress bitnami/wordpress | kubectl apply -f -
```

---

## 5. Installer WordPress proprement

L’installation précédente reste fonctionnelle, mais dans ce TD vous allez installer WordPress pour le service “compta”, dans un espace de noms dédié.

### 5.1 Création du namespace et installation

Installez WordPress dans un namespace dédié :

```
helm install wordpress-compta bitnami/wordpress \
    --namespace intranet \
    --create-namespace
```

**Capture attendue :** sortie de Helm montrant le déploiement dans `intranet`.

L’installation `wordpress` dans `default` existe toujours — vous en aurez besoin plus tard.

### 5.2 Mise à jour de l’installation

La mise à jour d’un chart déjà installé se fait ainsi :

```
helm upgrade wordpress-compta bitnami/wordpress \
    --namespace intranet
```

Note : le namespace n’est plus modifiable après installation.

### 5.3 Récupération des mots de passe

Récupérez le mot de passe WordPress :

```
export WORDPRESS_PASSWORD=$(kubectl get secret --namespace intranet \
  wordpress-compta -o jsonpath="{.data.wordpress-password}" | base64 -d)
```

Récupérez le mot de passe MariaDB (root) :

```
export MARIADB_ROOT_PASSWORD=$(kubectl get secret --namespace intranet \
  wordpress-compta-mariadb -o jsonpath="{.data.mariadb-root-password}" | base64 -d)
```

Récupérez le mot de passe MariaDB (utilisateur WordPress) :

```
export MARIADB_PASSWORD=$(kubectl get secret --namespace intranet \
  wordpress-compta-mariadb -o jsonpath="{.data.mariadb-password}" | base64 -d)
```

**Capture attendue :** coller dans le compte-rendu les trois valeurs récupérées.

### 5.4 Suppression puis réinstallation avec paramètres définis

Pour supprimer l’installation :

```
helm uninstall wordpress-compta --namespace intranet
```

Puis supprimer son PVC :

```
kubectl -n intranet delete pvc --selector app.kubernetes.io/instance=wordpress-compta
```

Réinstallation avec mots de passe spécifiés :

```
helm install wordpress-compta bitnami/wordpress \
    --namespace intranet \
    --create-namespace \
    --set wordpressPassword=$WORDPRESS_PASSWORD \
    --set mariadb.auth.rootPassword=$MARIADB_ROOT_PASSWORD \
    --set mariadb.auth.password=$MARIADB_PASSWORD
```

**Capture attendue :** nouvelle installation avec paramètres appliqués.

---

## 6. Exploration des données Helm

Pour observer les valeurs réellement utilisées :

```
helm -n intranet get values wordpress-compta
```

Affichez aussi l’historique Helm :

```
kubectl -n intranet get secret -l owner=helm
```

Vous devez voir plusieurs versions du chart :

- `sh.helm.release.v1.wordpress-compta.v1`
- `sh.helm.release.v1.wordpress-compta.v2`
- ...

**Capture attendue :** versions obtenues.

---

## 7. Commande Helm standardisée

Pour éviter les erreurs de contexte, utilisez systématiquement cette forme :

```
helm upgrade --install wordpress-compta bitnami/wordpress \
    --namespace intranet \
    --create-namespace
```

Elle fonctionne autant pour une première installation que pour une mise à jour.

---

## 8. Visualisation de l’état des déploiements Helm

Listez les installations du namespace courant :

```
helm ls
```

Listez toutes les installations du cluster :

```
helm ls -A
```

Exemple d’attendu :

- `wordpress        default     deployed`
- `wordpress-compta intranet    deployed`

---

## 9. Suppression d’un déploiement

Supprimez l’installation WordPress du namespace default :

```
helm delete wordpress --keep-history
```

Vérifiez qu’aucun pod ne reste :

```
kubectl get pods
```

Puis dans le namespace intranet :

```
kubectl -n intranet get pods
```

**Capture attendue :** sortie des commandes.

---

## 10. Annulation d’une suppression (rollback)

Helm garde l’historique :

```
helm ls --all
```

Restaurez une version :

```
helm rollback wordpress 1
```

**Capture attendue :** sortie contenant “Rollback was a success”.

---

## 11. Purge définitive

Pour supprimer le chart définitivement :

```
helm delete wordpress
```

Liste finale :

```
helm ls -A
```

Seul `wordpress-compta` doit rester déployé.

**Capture attendue :** sortie des commandes.

---

# TD 8 — Partie Monitoring (Prometheus / Alertmanager / Grafana)

## Suite : Mise en place du Monitoring avec Prometheus, Alertmanager et Grafana

---

## Mise en place de Prometheus

### 1. À propos de Prometheus

Prometheus est un outil de surveillance construit autour d’une base de données de séries temporelles. L’alimentation de cette base de données est réalisée par l’outil lui-même en allant scruter à intervalle régulier les différents points d’acquisition de la donnée. La communication s’appuie sur le protocole HTTP et les points de collecte sont appelés des exporteurs.

Ces exporteurs sont de plus en plus intégrés directement dans les applications du marché. Lorsque ce n’est pas le cas (pour les bases de données, par exemple), un process doit être lancé afin de permettre de faire le pont entre Prometheus et le produit à surveiller.

Dans le contexte des conteneurs, Prometheus s’intègre particulièrement bien pour plusieurs raisons :

- rapide et léger : Prometheus est particulièrement optimisé ;
- dynamique : Prometheus détecte en continu les créations et suppressions de services et/ou pods.

Autre point important : la plupart des briques Kubernetes disposent nativement d’un point de collecte Prometheus. L’intégration en est donc fortement facilitée.

Le projet est soutenu par la fondation CNCF.

Consultez : [https://prometheus.io](https://prometheus.io)

**Rendu attendu :**
En 3 à 4 lignes, expliquer pourquoi Prometheus est bien adapté aux environnements Kubernetes.

---

### 2. Fonctionnement de Prometheus

#### a. Architecture de Prometheus

Schéma d’architecture extrait du site prometheus.io.

#### b. Le moteur Prometheus

Le serveur Prometheus prend en charge plusieurs opérations :

- scruter l’état des éléments à surveiller à l’aide d’exporteurs ;
- stocker les métriques dans un moteur TSDB ;
- exposer ces métriques via une API REST.

Il supporte des mécanismes de découverte automatique, notamment Kubernetes.

#### c. Les exporteurs Prometheus

Les exporteurs exposent des métriques sous forme texte.

Exemple :

```
# HELP metric1.
# TYPE metric1 gauge
metric1 1

# HELP metric2.
# TYPE metric2 counter
metric2 1

# HELP info Information about the application.
# TYPE info gauge
info{version="v1"} 1
```

Chaque métrique est un couple clé/valeur, éventuellement enrichi de labels.

---

### 3. Installation de Prometheus

#### a. Choix du chart Prometheus

Deux charts Helm existent :

- `prometheus-community/prometheus`
- `prometheus-community/kube-prometheus-stack`

Le second inclut Grafana, Alertmanager et les règles de surveillance.

**Rendu attendu :**
Indiquer lequel des deux charts serait le plus adapté pour une entreprise souhaitant une installation complète, et pourquoi.

#### b. Qu’est-ce qu’un opérateur ?

Un opérateur utilise des Custom Resource Definitions (CRD) pour automatiser des déploiements complexes (bases de données, certificats, Prometheus…).

**Rendu attendu :**
Citer un autre opérateur Kubernetes connu et son rôle (en une phrase).

#### c. Déploiement de l’opérateur Prometheus

Ajout du dépôt Helm :

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```

**Fichier `prometheus-operator.yaml` — Version Minikube**

Configuration pour Minikube — Aucun Ingress public, pas de TLS, pas de DNS

```yaml
alertmanager:
  ingress:
    enabled: false
  service:
    type: NodePort

grafana:
  persistence:
    enabled: true
  ingress:
    enabled: false
  service:
    type: NodePort
```

Déploiement du chart avec ce fichier :

```
helm upgrade --install prometheus \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f prometheus-operator.yaml
```

Accès après installation

Accès Grafana

- Via NodePort : `minikube service -n monitoring prometheus-grafana`
- Ou via port-forward : `kubectl -n monitoring port-forward svc/prometheus-grafana 3000:80`

Accès Alertmanager

- Via NodePort : `minikube service -n monitoring prometheus-kube-prometheus-alertmanager`
- Ou via port-forward : `kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-alertmanager 9093:9093`

**Rendu attendu :**
Trois captures :

- l’ajout du dépôt Helm,
- un extrait du fichier `prometheus-operator.yaml`,
- la sortie de la commande `helm upgrade --install`.

#### d. Pods démarrés

Commande :

```
kubectl -n monitoring get pods -w
```

Liste des pods obtenus, incluant Grafana, kube-state-metrics et l’opérateur.

**Rendu attendu :**
Capture d’écran de la commande et explication du rôle de `kube-state-metrics` (2 lignes).

#### e. Objets déploiements

```
kubectl -n monitoring get deployment
```

Déploiements générés : Grafana, Alertmanager, kube-state-metrics, opérateur Prometheus.

**Rendu attendu :**
Identifier dans la sortie :

- le déploiement Grafana
- le déploiement de l’opérateur
  (+ explication de la différence entre un exporteur et un opérateur)

#### f. Nouvelles ressources Prometheus

Le chart crée plusieurs CRD : Prometheus, PrometheusRule, ServiceMonitor, AlertManager, etc.

Consultation :

```
kubectl -n monitoring get prometheus
```

Consultation du pod :

```
kubectl -n monitoring get pods -l app.kubernetes.io/name=prometheus
```

**Rendu attendu :**
Capture du `kubectl get prometheus` + expliquer pourquoi Prometheus utilise un volume persistant.

#### g. DaemonSet : node exporter

Liste :

```
kubectl -n monitoring get pods -l app.kubernetes.io/name=prometheus-node-exporter
```

**Rendu attendu :**
Capture + réponse à : Pourquoi utilise-t-on un DaemonSet pour node-exporter ?

---

## 4. Priorisation des briques de surveillance

### a. Problème de la surveillance

Les composants de monitoring doivent passer avant les applications classiques.

### b. Déclaration des classes de priorité

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: monitoring-node
description: Priority for monitoring nodes.
value: 101000
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: monitoring-cluster
description: Priority for monitoring cluster.
value: 100000
```

Application :

```
kubectl apply -f priority-class.yaml
```

**Rendu attendu :**
Capture de `kubectl get priorityclass`.

### c. Modification du déploiement de Prometheus

Les champs suivants doivent être complétés dans le chart :

- `prometheus-node-exporter.priorityClassName`
- `prometheus.priorityClassName`

**Rendu attendu :**
Extrait YAML montrant la présence de `priorityClassName` et justification (2 à 3 lignes) de l’intérêt de prioriser le monitoring.

---

# Utilisation de Prometheus

## 1. Fonctionnement des métriques

### a. Consultation des métriques de Prometheus

Le moteur Prometheus expose ses propres métriques sur le port 9090, via le chemin `/metrics`.

Pour y accéder, établissez un tunnel vers le service Prometheus :

```
kubectl -n monitoring port-forward svc/prometheus-operated 9090
```

Ouvrez ensuite :

- [http://localhost:9090/metrics](http://localhost:9090/metrics)

**Rendu attendu :**
Capture d’écran de la page `/metrics` + commentaire (2–3 lignes) expliquant :

- que représente une métrique,
- comment se présentent clés, valeurs et labels.

### b. Présentation de l’interface de Prometheus

Avec le port-forward actif, ouvrez :

- [http://localhost:9090](http://localhost:9090)

Testez la requête suivante :

- `node:node_num_cpu:sum`

Cliquez sur Execute, puis sur Graph.

**Rendu attendu :**
Captures :

- requête dans la zone de saisie
- résultat graphique

Commentaire : expliquer ce que représente cette métrique.

### c. Métriques de Kubernetes

Grâce aux exporteurs fournis dans le chart (kube-state-metrics notamment), Prometheus remonte automatiquement :

- utilisation CPU / mémoire des pods
- I/O réseau et disque
- état des volumes
- évènements API Kubernetes

Il est aussi possible d’ajouter des métriques applicatives personnalisées via des objets ServiceMonitor.

### d. Déclaration des points de collecte dans Kubernetes

Liste des règles de collecte créées automatiquement par kube-prometheus-stack :

```
kubectl -n monitoring get servicemonitor
```

Affichez la définition complète :

```
kubectl -n monitoring get servicemonitor prometheus-kube-prometheus-operator -o yaml
```

**Rendu attendu :**
Extrait YAML (capture) contenant :

- `endpoints`
- `namespaceSelector`
- `matchLabels`

* commentaire expliquant leur rôle en 3–5 lignes.

### e. Consultation des points de collecte dans Prometheus

Accédez à :

- Status → Targets

**Rendu attendu :**
Capture de la page Targets, encadrant une ligne de target, avec un court commentaire expliquant UP/DOWN.

---

## 2. Définition des alertes

### a. Consultation de la liste des alertes

```
kubectl -n monitoring get prometheusrule
```

### b. Structure d’une règle d’alerte

```
kubectl -n monitoring get PrometheusRule prometheus-kube-prometheus-prometheus -o yaml
```

**Rendu attendu :**
Extrait YAML montrant `alert`, `expr`, `for`, `labels` + commentaire expliquant comment l’alerte se déclenche.

### c. Définition d’alertes (avec record)

Certaines requêtes complexes sont d’abord enregistrées via un champ `record`.

---

## 3. Gestionnaire d’alertes (Alertmanager)

### a. Rôle du gestionnaire d’alertes

Après déclenchement d’une alerte, Alertmanager :

- applique une temporisation,
- groupe les alertes,
- applique des règles de routage,
- envoie des notifications (Slack, email…).

### b. Consultation du gestionnaire d’alertes

Listez les instances AlertManager :

```
kubectl -n monitoring get AlertManager
```

### c. Configuration des alertes dans Alertmanager

Dans l’interface web, recherchez : `critical`.

**Rendu attendu :**
Capture de la liste montrant au moins une alerte critique + commentaire indiquant pourquoi certaines alertes sont normales dans un cluster managé.

### d. Désactivation des alertes scheduler / manager (clusters managés)

Modifier :

- `kubeControllerManager.enabled=false`
- `kubeScheduler.enabled=false`

Puis appliquer :

```
helm upgrade --install prometheus stable/prometheus-operator \
  --namespace monitoring \
  -f prometheus-operator.yaml
```

**Rendu attendu :**
Capture avant/après montrant la disparition des alertes scheduler/controller-manager.

### e. Configuration de l’envoi des notifications (ex. Slack)

Bloc à ajouter dans `alertmanager → config` :

```yaml
global:
  slack_api_url: "URL_API_SLACK"

receivers:
  - name: "null"
  - name: default-receiver
    slack_configs:
      - channel: "#monitoring"
        send_resolved: true

route:
  receiver: default-receiver
  repeat_interval: 3h
  routes:
    - match:
        alertname: Watchdog
      receiver: "null"
    - match:
        severity: warning
      receiver: "null"
```

Test :

```
export SLACK_HOOK=URL_API_SLACK
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Hello, World!"}' \
  $SLACK_HOOK
```

Appliquer :

```
helm upgrade --install prometheus stable/prometheus-operator \
  --namespace monitoring \
  -f prometheus-operator.yaml
```

**Rendu attendu :**
Capture Slack montrant réception d’un message de test ou d’une alerte Prometheus.

---

# Tableaux de bord Grafana

## 1. Présentation de Grafana

Grafana est un outil de visualisation permettant d’afficher graphiquement des données issues de multiples sources (datasources). Il supporte notamment :

- bases temporelles : Prometheus, InfluxDB, Graphite,
- moteurs NoSQL : Elasticsearch,
- bases SQL : PostgreSQL, MySQL.

Les données sont affichées dans des tableaux de bord (dashboards).

---

## 2. Configuration de Grafana

### a. Branchement au moteur Prometheus

Les datasources sont configurées via des ConfigMap portant le label : `grafana_datasource=1`.

Pour les consulter :

```
kubectl -n monitoring get configmap -l grafana_datasource=1
```

**Rendu attendu :**
Capture du ConfigMap + commentaire expliquant :

- quelle datasource est déclarée,
- quelle URL est utilisée,
- ce que signifie `isDefault: true`.

### b. Définition des tableaux de bord

Les dashboards sont stockés dans des ConfigMap portant le label : `grafana_dashboard=1`.

Liste :

```
kubectl -n monitoring get configmap -l grafana_dashboard=1
```

**Rendu attendu :**
Capture de la liste des dashboards + commentaire sur l’intérêt d’avoir ces dashboards pré-installés.

---

## 3. Interface Grafana

Accès via l’URL configurée lors du déploiement.

Identifiants par défaut :

- `admin`
- `prom-operator`

**Rendu attendu :**
Capture d’un tableau de bord fourni + commentaire expliquant ce que montre le graphique.

---

## 4. Sécurisation de l’accès à Grafana

Grafana peut être sécurisé via :

- LDAP,
- OAuth2,
- SSO entreprise.

Exemple OAuth2 Google via Helm :

```yaml
grafana:
  persistence:
    enabled: true

  grafana.ini:
    server:
      root_url: "https://grafana.eni.yannig.ovh"
    auth.google:
      enabled: true
      client_id: XxXxXxXxXxXx
      client_secret: YyYyYyYyYyYy
      scopes: https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email
      auth_url: https://accounts.google.com/o/oauth2/auth
      token_url: https://accounts.google.com/o/oauth2/token
      allowed_domains: my-company.org
      allow_sign_up: true
```

**Rendu attendu :**
Petit texte expliquant en 3–5 lignes :

- à quoi sert OAuth,
- pourquoi sécuriser Grafana,
- ce que change `allowed_domains`.
