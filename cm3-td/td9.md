# TD 9 — GitOps avec Flux (Minikube + GitLab)

Les commandes de terminal sont prévues pour Bash/Zsh sous Linux, macOS ou WSL. Remplacez les valeurs entre `<...>` avant utilisation. Utilisez le cluster Minikube des TD précédents.

## 1. Nettoyage du cluster

### 1.1 Objectif et justification

L’objectif de ce TD est de mettre en place une démarche **GitOps** : l’état du cluster Kubernetes doit être défini dans Git, puis appliqué automatiquement par Flux. Avant de redéployer l’infrastructure (Traefik, Prometheus) et l’application (OwnCloud) via GitOps, il est nécessaire de supprimer les déploiements existants réalisés lors des TD précédents.

Ce nettoyage est indispensable pour :

- **Éviter les conflits de contrôle** : un composant déjà présent mais non géré par Flux ne sera pas forcément aligné avec ce qui est décrit dans Git.
- **Éviter les collisions de ressources** : deux contrôleurs d’ingress ou deux stacks de monitoring peuvent provoquer des comportements incohérents (ports, services, objets Kubernetes).
- **Garantir la reproductibilité** : un cluster propre permet de valider que l’infrastructure sera recréée uniquement à partir de Git.

Dans cette section, vous allez supprimer :

- `ingress-nginx` (namespace `ingress-nginx`)
- `kube-prometheus-stack` (namespace `monitoring`, release Helm `prometheus`)
- Les ressources persistantes pouvant rester après suppression : **PV** et **CRD**.

Vous ne devez pas modifier les namespaces système (`kube-system`, `kubernetes-dashboard`, etc.) ni les applications en namespace `default` (ex. `mailpit`).

---

### 1.2 Suppression d’ingress-nginx

#### 1.2.1 Désactivation du contrôleur

Au TD6, le contrôleur a été installé avec l’addon Minikube. Désactivez-le :

```bash
minikube addons disable ingress
```

Si vous avez utilisé une installation Helm à la place de l’addon, vérifiez son nom avec `helm list -n ingress-nginx`, puis désinstallez cette release :

```bash
helm -n ingress-nginx uninstall ingress-nginx
```

Utilisez la méthode correspondant à votre installation.

**Rendu 1 — Désinstallation ingress-nginx**

Fournissez une capture d’écran montrant la commande et sa sortie.

#### 1.2.2 Suppression du namespace

Exécutez :

```
kubectl delete ns ingress-nginx --ignore-not-found
```

**Rendu 2 — Suppression du namespace ingress-nginx**

Fournissez une capture d’écran montrant la commande et sa sortie.

#### 1.2.3 Contrôle

Exécutez :

```
kubectl get ns | grep ingress-nginx
kubectl get pods -A | grep ingress-nginx
```

**Rendu 3 — Contrôle suppression ingress-nginx**

Fournissez une capture d’écran montrant les deux commandes. Elles ne doivent rien retourner.

---

### 1.3 Suppression de Prometheus (kube-prometheus-stack)

#### 1.3.1 Désinstallation Helm

La release attendue est `prometheus`.

Exécutez :

```
helm -n monitoring uninstall prometheus
```

**Rendu 4 — Désinstallation Prometheus**

Fournissez une capture d’écran montrant la commande et sa sortie.

#### 1.3.2 Suppression du namespace

Exécutez :

```
kubectl delete ns monitoring
```

**Rendu 5 — Suppression du namespace monitoring**

Fournissez une capture d’écran montrant la commande et sa sortie.

#### 1.3.3 Contrôle

Exécutez :

```
kubectl get ns | grep monitoring
kubectl get pods -A | grep monitoring
```

**Rendu 6 — Contrôle suppression monitoring**

Fournissez une capture d’écran montrant les deux commandes. Elles ne doivent rien retourner.

---

### 1.4 Nettoyage des volumes persistants (PV)

#### 1.4.1 Pourquoi nettoyer les PV

Lorsqu’une application utilise du stockage persistant, Kubernetes peut conserver des **PersistentVolumes (PV)** même après suppression des namespaces et des PVC. Ces PV “orphelins” peuvent gêner un redéploiement propre et nuire à la reproductibilité du TD.

#### 1.4.2 Lister les PV

Exécutez :

```
kubectl get pv
```

**Rendu 7 — Liste des PV**

Fournissez une capture d’écran montrant la sortie de `kubectl get pv`.

#### 1.4.3 Supprimer les PV liés à l’ancien déploiement

Supprimez chaque PV dont la colonne `CLAIM` référence `monitoring` ou `ingress-nginx` :

```
kubectl delete pv <pv_name>
```

**Rendu 8 — Suppression des PV orphelins**

Fournissez une capture d’écran montrant chaque suppression effectuée (commande + sortie).

---

### 1.5 Nettoyage des CRD (Custom Resource Definitions)

#### 1.5.1 Définition : qu’est-ce qu’une CRD ?

Une **CRD (Custom Resource Definition)** permet d’ajouter de nouveaux types de ressources à Kubernetes. Par exemple, `kube-prometheus-stack` ajoute des ressources comme `ServiceMonitor`, `PrometheusRule`, `Alertmanager`, etc. Ces ressources sont gérées par le **Prometheus Operator**.

#### 1.5.2 Pourquoi supprimer les CRD ici ?

Lors d’un `helm uninstall`, Helm ne supprime généralement pas les CRD. Dans ce TD, si elles restent présentes, vous conservez des types de ressources liés à une installation précédente, ce qui peut fausser l’état “propre” attendu avant de redéployer via GitOps.

#### 1.5.3 Vérifier la présence des CRD de Prometheus Operator

Exécutez :

```
kubectl get crd | grep monitoring.coreos.com
```

**Rendu 9 — Vérification CRD Prometheus Operator**

Fournissez une capture d’écran montrant la sortie de la commande.

#### 1.5.4 Supprimer ces CRD si elles existent

Exécutez :

```
kubectl get crd -o name | grep '\.monitoring\.coreos\.com$' |
  while IFS= read -r crd; do
    kubectl delete "$crd"
  done
```

**Rendu 10 — Suppression des CRD**

Fournissez une capture d’écran montrant la commande et sa sortie.

#### 1.5.5 Contrôle final CRD

Exécutez :

```
kubectl get crd | grep monitoring.coreos.com
```

**Rendu 11 — Contrôle suppression CRD**

Fournissez une capture d’écran montrant que la commande ne retourne rien.

---

## 2. Mise en place structurelle Git

### 2.1 Objectif

Vous allez préparer **deux dépôts Git distincts**, conformément à l’approche GitOps :

- **Dépôt “cluster”** : contient la structure GitOps et, plus tard, les ressources d’infrastructure gérées par Flux (Traefik, Prometheus).
- **Dépôt “apps”** : contient uniquement les ressources applicatives, ici OwnCloud.

Cette séparation permet de distinguer :

- ce qui décrit l’infrastructure du cluster (dépôt cluster),
- de ce qui décrit les applications (dépôt apps),

tout en conservant un historique Git clair et des droits d’accès modulables.

---

### 2.2 Création d’un espace de travail local

Créez un répertoire de travail, puis les deux répertoires de dépôts :

```
mkdir -p "$HOME/td-gitops"
cd "$HOME/td-gitops"

mkdir -p k8s-gitops-cluster
mkdir -p k8s-gitops-apps
```

**Rendu 12 — Création des répertoires de travail**

Fournissez une capture d’écran montrant :

```
pwd
ls -la
```

---

### 2.3 Initialisation du dépôt “cluster” (infrastructure)

Placez-vous dans le dépôt cluster :

```
cd k8s-gitops-cluster
git init
git branch -M main
```

Créez la structure de dossiers :

```
mkdir -p infrastructure/traefik
mkdir -p infrastructure/prometheus
mkdir -p docs
```

Ajoutez un `README` et un fichier `.gitignore` :

```bash
cat > README.md <<'EOF'
# k8s-gitops-cluster

Dépôt GitOps "cluster" : infrastructure et configuration Flux.
Contient notamment Traefik et Prometheus (déployés via Flux).
EOF
```

```bash
cat > .gitignore <<'EOF'
# Secrets et tokens
*.token
*.pat
*.env
.env
.env.*

# Kubeconfig / fichiers locaux
kubeconfig
*.kubeconfig

# OS / IDE
.DS_Store
.vscode/
.idea/
EOF
```

Créez un fichier de repère (sans configuration Kubernetes à ce stade) :

```bash
cat > docs/STRUCTURE.md <<'EOF'
# Structure attendue

- infrastructure/traefik : fichiers GitOps pour Traefik
- infrastructure/prometheus : fichiers GitOps pour Prometheus
- (les fichiers Flux seront ajoutés lors du bootstrap)
EOF
```

Effectuez un premier commit :

```
git add .
git commit -m "chore: initialise cluster repository structure"
```

**Rendu 13 — Initialisation et premier commit du dépôt cluster**

Fournissez une capture d’écran montrant :

```
git status
git log --oneline -n 3
```

**Rendu 14 — Arborescence du dépôt cluster**

Fournissez une capture d’écran montrant :

```
find . -maxdepth 3 -type d -print
```

---

### 2.4 Initialisation du dépôt “apps” (OwnCloud)

Revenez au répertoire parent, puis initialisez le dépôt apps :

```
cd ../k8s-gitops-apps
git init
git branch -M main
```

Créez la structure de dossiers :

```
mkdir -p apps/owncloud
mkdir -p docs
```

Ajoutez un `README` et un `.gitignore` :

```bash
cat > README.md <<'EOF'
# k8s-gitops-apps

Dépôt GitOps "applications" : contient les déploiements applicatifs.
Dans ce TD : OwnCloud uniquement.
EOF
```

```bash
cat > .gitignore <<'EOF'
# Secrets et tokens
*.token
*.pat
*.env
.env
.env.*

# OS / IDE
.DS_Store
.vscode/
.idea/
EOF
```

Créez un fichier de repère :

```bash
cat > docs/STRUCTURE.md <<'EOF'
# Structure attendue

- apps/owncloud : manifests/HelmRelease OwnCloud (déployé via Flux)
EOF
```

Effectuez un premier commit :

```
git add .
git commit -m "chore: initialise apps repository structure"
```

**Rendu 15 — Initialisation et premier commit du dépôt apps**

Fournissez une capture d’écran montrant :

```
git status
git log --oneline -n 3
```

**Rendu 16 — Arborescence du dépôt apps**

Fournissez une capture d’écran montrant :

```
find . -maxdepth 3 -type d -print
```

---

## 3. Configuration GitLab

### 3.1 Objectif

Dans cette partie, vous allez :

- créer deux dépôts GitLab correspondant aux deux dépôts locaux préparés à l’étape précédente ;
- configurer les mécanismes d’authentification nécessaires au GitOps ;
- produire une traçabilité claire des accès en sauvegardant les informations (URL, tokens) dans des fichiers nommés de manière explicite.

**Rappel d’architecture (à retenir)**

- Le dépôt **cluster** est le support Flux : il contient le bootstrap et l’infrastructure (Traefik, Prometheus).
- Le dépôt **apps** est consommé par Flux : il contient OwnCloud et ses ressources applicatives.

Cette séparation clarifie l’historique et permet de limiter les droits d’accès à chaque dépôt.

### 3.2 Création des dépôts sur GitLab

Sur [GitLab de l’IUT](https://iut-git.unice.fr/), créez deux projets vides : `k8s-gitops-cluster` et `k8s-gitops-apps`. Ne les initialisez pas avec un README : les premiers commits existent déjà localement.

Relevez leurs URL HTTPS de clonage, sans identifiant ni token incorporé dans l’URL.

**Rendu 17 — Dépôts GitLab créés**

Capture de la liste des projets ou des deux pages d’accueil avec leurs noms.

### 3.3 Association des dépôts locaux aux dépôts distants

#### 3.3.1 Dépôt cluster

```bash
cd "$HOME/td-gitops/k8s-gitops-cluster"
git remote add origin <URL_GITLAB_CLUSTER>
git push -u origin main
git remote -v
git log --oneline -n 3
```

**Rendu 18 — Remote et push du dépôt cluster**

Capture des remotes, des derniers commits et de la confirmation du push.

#### 3.3.2 Dépôt apps

```bash
cd "$HOME/td-gitops/k8s-gitops-apps"
git remote add origin <URL_GITLAB_APPS>
git push -u origin main
git remote -v
git log --oneline -n 3
```

**Rendu 19 — Remote et push du dépôt apps**

Capture des remotes, des derniers commits et de la confirmation du push.

### 3.4 Séparation des tokens GitLab

Préparez deux accès distincts :

- un **Personal Access Token (PAT)** pour le bootstrap du dépôt cluster ;
- un **deploy token du projet apps**, limité à la lecture du dépôt, pour la synchronisation d’OwnCloud.

Votre accès utilisateur sert aux commits et pushes locaux. Le deploy token apps sert uniquement à Flux pour lire ce dépôt.

### 3.5 Token bootstrap du dépôt cluster

Créez un PAT avec le scope `api`, depuis un compte disposant des droits nécessaires sur le projet cluster. Le bootstrap utilise l’API GitLab pour préparer son accès et écrire sa configuration. Référence : [bootstrap GitLab de Flux](https://fluxcd.io/flux/installation/bootstrap/gitlab/).

Créez un dossier local hors des dépôts Git :

```bash
mkdir -p "$HOME/td-gitops-secrets"
chmod 700 "$HOME/td-gitops-secrets"
umask 077
cat > "$HOME/td-gitops-secrets/GITLAB_TOKEN__bootstrap__cluster.txt" <<'EOF'
USAGE=bootstrap_flux_cluster_repo
GITLAB_HOST=https://iut-git.unice.fr/
REPO_ROLE=cluster (support Flux)
REPO_URL=<URL_GITLAB_CLUSTER>
TOKEN=<COLLER_ICI_LE_PAT>
EOF
chmod 600 "$HOME/td-gitops-secrets/GITLAB_TOKEN__bootstrap__cluster.txt"
```

Complétez le fichier avec un éditeur local, sans afficher le PAT dans les captures.

**Rendu 20 — Fichier token bootstrap**

```bash
ls -l "$HOME/td-gitops-secrets"
grep -v '^TOKEN=' "$HOME/td-gitops-secrets/GITLAB_TOKEN__bootstrap__cluster.txt"
```

Capture des permissions et des métadonnées, sans la ligne `TOKEN`.

### 3.6 Token de lecture du dépôt apps

Dans le projet apps, créez un **deploy token** avec le scope `read_repository`. Notez son nom d’utilisateur associé, qui peut différer de votre login personnel. Référence : [deploy tokens GitLab](https://docs.gitlab.com/user/project/deploy_tokens/).

```bash
cat > "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt" <<'EOF'
USAGE=flux_access_apps_repo
GITLAB_HOST=https://iut-git.unice.fr/
REPO_ROLE=apps (managé par Flux)
REPO_URL=<URL_GITLAB_APPS>
USERNAME=<UTILISATEUR_DU_DEPLOY_TOKEN>
TOKEN=<COLLER_ICI_LE_DEPLOY_TOKEN>
EOF
chmod 600 "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt"
```

Complétez ce fichier dans votre éditeur local.

**Rendu 21 — Fichier token apps**

```bash
ls -l "$HOME/td-gitops-secrets"
grep -v '^TOKEN=' "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt"
```

Capture des permissions et des métadonnées, sans le token.

### 3.7 Récapitulatif des accès

Les deux dépôts doivent être synchronisés avec GitLab. Les deux fichiers locaux doivent identifier clairement leur usage et leur dépôt.

**Rendu 22 — Récapitulatif des informations GitOps**

```bash
ls -1 "$HOME/td-gitops-secrets"
grep -v '^TOKEN=' "$HOME/td-gitops-secrets/GITLAB_TOKEN__bootstrap__cluster.txt"
grep -v '^TOKEN=' "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt"
```

Fournissez une capture distinguant l’accès bootstrap et l’accès de lecture apps.

## 4. Déploiement de Flux

### 4.1 Objectif

Installer le client Flux puis effectuer le bootstrap. Celui-ci installe les contrôleurs dans le namespace `flux-system` et écrit leur configuration dans `clusters/minikube/flux-system/` du dépôt cluster.

### 4.2 Installation du client Flux

```bash
curl -s https://fluxcd.io/install.sh | sudo bash
flux --version
kubectl config current-context
flux check --pre
```

Vérifiez que le contexte correspond au cluster Minikube attendu et que les prérequis Flux sont satisfaits.

**Rendu 23 — Installation de Flux CLI**

Capture de l’installation et de la version du client.

### 4.3 Export du token bootstrap

Chargez le PAT depuis le fichier local, sans imprimer sa valeur :

```bash
export GITLAB_TOKEN="$(sed -n 's/^TOKEN=//p' "$HOME/td-gitops-secrets/GITLAB_TOKEN__bootstrap__cluster.txt")"
test -n "$GITLAB_TOKEN" && echo "OK" || echo "ERREUR"
```

**Rendu 24 — Export du token GitLab**

Capture de ces commandes et du résultat du test, sans afficher la valeur du PAT.

### 4.4 Bootstrap du dépôt cluster

Remplacez `<OWNER>` par votre namespace GitLab et `<REPO_CLUSTER>` par le nom du projet cluster :

```bash
flux bootstrap gitlab \
  --hostname=iut-git.unice.fr \
  --owner=<OWNER> \
  --repository=<REPO_CLUSTER> \
  --branch=main \
  --path=clusters/minikube \
  --deploy-token-auth \
  --personal
```

Pour un projet appartenant à un **groupe**, retirez `--personal` et utilisez le chemin du groupe pour `--owner`. L’option `--deploy-token-auth` permet au bootstrap de créer son propre accès de lecture au dépôt cluster ; cet accès est distinct du deploy token apps.

Arborescence attendue :

```text
clusters/
  minikube/
    flux-system/
      gotk-components.yaml
      gotk-sync.yaml
      kustomization.yaml
```

**Rendu 25 — Bootstrap Flux**

Capture de la commande et de sa sortie.

### 4.5 Vérification dans GitLab

Ouvrez le dépôt cluster et recherchez `clusters/minikube/flux-system/`.

**Rendu 26 — Configuration Flux dans GitLab**

Capture de cette arborescence.

### 4.6 Vérification côté cluster

#### 4.6.1 Pods Flux

```bash
kubectl get pods -n flux-system
```

**Rendu 27 — Pods Flux**

Capture des pods et de leur état.

#### 4.6.2 État Flux

```bash
flux check
```

**Rendu 28 — flux check**

Capture de la sortie du contrôle.

#### 4.6.3 Sources et configurations appliquées

```bash
flux get sources all -A
flux get kustomizations -A
```

**Rendu 29 — Sources et Kustomizations Flux**

Capture des deux sorties. Les objets `flux-system` doivent être prêts avant de poursuivre.

## 5. Déploiement GitOps

### 5.1 Objectif

Un push sur le dépôt cluster doit permettre à Flux de déployer Traefik et Prometheus ; un push sur le dépôt apps doit permettre de déployer OwnCloud. Flux détecte les changements lors de ses synchronisations périodiques. Les commandes `flux reconcile` accélèrent leur prise en compte pendant le TD.

Les manifests applicatifs et les HelmRelease sont livrés par **Git**, sans `kubectl apply` ni `helm install` manuel. Le Secret d’authentification Git constitue un prérequis créé directement dans le cluster. Les exemples utilisent l’API stable `helm.toolkit.fluxcd.io/v2`, décrite dans la [documentation HelmRelease de Flux](https://fluxcd.io/flux/components/helm/helmreleases/).

### 5.2 Préparation de l’infrastructure dans le dépôt cluster

#### 5.2.1 Récupérer les fichiers du bootstrap

```bash
cd "$HOME/td-gitops/k8s-gitops-cluster"
git pull --ff-only
ls -l clusters/minikube
ls -l clusters/minikube/flux-system
```

**Rendu 30 — Fichiers Flux dans le dépôt local**

Capture des deux listes de fichiers.

#### 5.2.2 Point d’entrée Kustomize

Fichier `clusters/minikube/kustomization.yaml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ./flux-system
  - ../../infrastructure/traefik
  - ../../infrastructure/prometheus
```

Les chemins sont relatifs à `clusters/minikube/`. Complétez les dossiers référencés avant de pousser ce fichier.

**Rendu 31 — Point d’entrée GitOps**

Capture du fichier `clusters/minikube/kustomization.yaml`.

#### 5.2.3 Traefik

Créez les quatre fichiers suivants dans `infrastructure/traefik/`.

Fichier `infrastructure/traefik/namespace.yaml` :

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: traefik
```

Fichier `infrastructure/traefik/helmrepo.yaml` :

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: traefik
  namespace: traefik
spec:
  interval: 1m
  url: https://traefik.github.io/charts
```

Fichier `infrastructure/traefik/helmrelease.yaml` :

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: traefik
  namespace: traefik
spec:
  interval: 1m
  releaseName: traefik
  chart:
    spec:
      chart: traefik
      sourceRef:
        kind: HelmRepository
        name: traefik
        namespace: traefik
  values:
    ports:
      web:
        port: 8000
        expose:
          default: true
        exposedPort: 80
        protocol: TCP
        nodePort: 30080
      websecure:
        port: 8443
        expose:
          default: true
        exposedPort: 443
        protocol: TCP
        nodePort: 30443
    service:
      type: NodePort
      enabled: true
    additionalArguments:
      - --log.level=DEBUG
```

La syntaxe `expose.default` suit les [valeurs du chart Traefik](https://github.com/traefik/traefik-helm-chart/blob/master/traefik/values.yaml). L’accès applicatif de ce TD utilise HTTP ; aucune redirection forcée vers HTTPS n’est activée avant la configuration de certificats.

Fichier `infrastructure/traefik/kustomization.yaml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - helmrepo.yaml
  - helmrelease.yaml
```

**Rendu 32 — Fichiers Traefik prêts**

```bash
ls -l infrastructure/traefik
```

Capture de la liste des fichiers.

#### 5.2.4 Prometheus

Créez les quatre fichiers suivants dans `infrastructure/prometheus/`.

Fichier `infrastructure/prometheus/namespace.yaml` :

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
```

Fichier `infrastructure/prometheus/helmrepo.yaml` :

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: prometheus-community
  namespace: monitoring
spec:
  interval: 1m
  url: https://prometheus-community.github.io/helm-charts
```

Fichier `infrastructure/prometheus/helmrelease.yaml` :

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: prometheus
  namespace: monitoring
spec:
  interval: 1m
  releaseName: prometheus
  chart:
    spec:
      chart: kube-prometheus-stack
      sourceRef:
        kind: HelmRepository
        name: prometheus-community
        namespace: monitoring
  values:
    grafana:
      ingress:
        enabled: false
```

Fichier `infrastructure/prometheus/kustomization.yaml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - helmrepo.yaml
  - helmrelease.yaml
```

**Rendu 33 — Fichiers Prometheus prêts**

```bash
ls -l infrastructure/prometheus
```

Capture de la liste des fichiers.

#### 5.2.5 Push et déploiement automatique

Depuis la racine du dépôt cluster, vérifiez l’assemblage local puis poussez les manifests :

```bash
kubectl kustomize clusters/minikube > /tmp/td9-cluster.yaml
git add clusters/minikube infrastructure
git commit -m "feat: deploy Traefik and Prometheus with Flux"
git push
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization flux-system -n flux-system
kubectl get pods -n traefik
kubectl get pods -n monitoring
flux get helmreleases -A
```

La réussite de la Kustomization signifie que les objets ont été appliqués. Attendez également que les HelmRelease deviennent `Ready=True` pour confirmer la réussite des installations Helm.

**Rendu 34 — Infrastructure déployée après push**

Capture des synchronisations, des pods des deux namespaces et des HelmRelease.

### 5.3 Déclarer le dépôt apps dans le dépôt cluster

#### 5.3.1 Secret d’accès Git

Chargez les informations du fichier apps sans afficher le token :

```bash
APPS_REPO_URL="$(sed -n 's/^REPO_URL=//p' "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt")"
APPS_REPO_USERNAME="$(sed -n 's/^USERNAME=//p' "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt")"
APPS_REPO_TOKEN="$(sed -n 's/^TOKEN=//p' "$HOME/td-gitops-secrets/GITLAB_TOKEN__repo__apps-owncloud.txt")"
flux create secret git apps-repo-auth \
  --url="$APPS_REPO_URL" \
  --namespace=flux-system \
  --username="$APPS_REPO_USERNAME" \
  --password="$APPS_REPO_TOKEN"
unset APPS_REPO_TOKEN
```

**Rendu 35 — Secret d’accès au dépôt apps**

Capture de la commande utilisant les variables et de sa sortie. N’affichez ni le token ni le contenu du Secret.

#### 5.3.2 Source Git et Kustomization Flux

Fichier `clusters/minikube/apps-sync.yaml` dans le dépôt cluster :

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 1m
  url: <URL_GITLAB_APPS>
  ref:
    branch: main
  secretRef:
    name: apps-repo-auth
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 1m
  path: ./apps
  prune: true
  sourceRef:
    kind: GitRepository
    name: apps
```

Remplacez l’URL par celle de clonage HTTPS du dépôt apps. `prune: true` permet à Flux de supprimer les ressources gérées retirées de Git.

Complétez `clusters/minikube/kustomization.yaml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ./flux-system
  - ../../infrastructure/traefik
  - ../../infrastructure/prometheus
  - ./apps-sync.yaml
```

**Rendu 36 — Déclaration du dépôt apps**

Capture des deux fichiers.

#### 5.3.3 Push et vérification

```bash
cd "$HOME/td-gitops/k8s-gitops-cluster"
git add clusters/minikube
git commit -m "feat: synchronize apps repository"
git push
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization flux-system -n flux-system
flux get sources git -A
flux get kustomizations -A
```

À ce stade, la source Git `apps` doit être accessible. Sa Kustomization peut être en erreur tant que le répertoire `apps/` et ses manifests n’ont pas été poussés à l’étape suivante : Git ne conserve pas les dossiers vides créés en partie 2.

**Rendu 37 — Flux voit le dépôt apps**

Capture de la source Git et de la Kustomization apps, avec une explication de leur état.

### 5.4 Déployer OwnCloud depuis le dépôt apps

#### 5.4.1 Préparer les fichiers OwnCloud

```bash
cd "$HOME/td-gitops/k8s-gitops-apps"
```

L’exemple du support utilise le chart historique **OwnCloud 12.2.5** du dépôt Azure Marketplace et l’image Bitnami `10.11.0-debian-11-r9`. Sa disponibilité n’est pas garantie. Avant cette manipulation, vérifiez que le dépôt fournit encore ce chart :

```bash
helm show chart owncloud \
  --repo https://marketplace.azurecr.io/helm/v1/repo \
  --version 12.2.5
helm show values owncloud \
  --repo https://marketplace.azurecr.io/helm/v1/repo \
  --version 12.2.5 > /tmp/td9-owncloud-values.yaml
```

Si cette vérification échoue, un miroir de ce chart ou une version de remplacement validée par l’enseignant est nécessaire avant de poursuivre cette partie. Adaptez alors l’URL du HelmRepository. Vérifiez aussi la disponibilité des images OwnCloud et MariaDB référencées par ce chart. Ne changez pas simplement de version sans vérifier les valeurs et dépendances : les manifests ci-dessous conservent le scénario du support.

Fichier `apps/kustomization.yaml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ./owncloud
```

Fichier `apps/owncloud/namespace.yaml` :

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: owncloud1
```

Fichier `apps/owncloud/helmrepo.yaml` :

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: bitnami-aks
  namespace: flux-system
spec:
  interval: 1m
  url: https://marketplace.azurecr.io/helm/v1/repo
```

Fichier `apps/owncloud/helmrelease.yaml` :

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: release1
  namespace: owncloud1
spec:
  interval: 1m
  releaseName: release1
  chart:
    spec:
      chart: owncloud
      version: "12.2.5"
      sourceRef:
        kind: HelmRepository
        name: bitnami-aks
        namespace: flux-system
  values:
    image:
      registry: docker.io
      repository: bitnami/owncloud
      tag: 10.11.0-debian-11-r9
    replicaCount: 1
    owncloudHost: owncloud.127.0.0.1.nip.io
    owncloudUsername: admin
    owncloudPassword: "td9-owncloud-demo"
    owncloudEmail: admin@example.invalid
    allowEmptyPassword: false
    containerPorts:
      http: 8080
      https: 8443
    podSecurityContext:
      enabled: true
      fsGroup: 1001
    containerSecurityContext:
      enabled: true
      runAsUser: 1001
      runAsNonRoot: true
    mariadb:
      enabled: true
      architecture: standalone
      auth:
        rootPassword: "td9-mariadb-root-demo"
        database: bitnami_owncloud
        username: bn_owncloud
        password: "td9-mariadb-user-demo"
      primary:
        persistence:
          enabled: true
          storageClass: standard
          accessModes:
            - ReadWriteOnce
          size: 8Gi
    persistence:
      enabled: true
      storageClass: standard
      accessModes:
        - ReadWriteOnce
      size: 8Gi
    service:
      type: ClusterIP
      ports:
        http: 80
        https: 443
    ingress:
      enabled: true
      apiVersion: networking.k8s.io/v1
      hostname: owncloud.127.0.0.1.nip.io
      path: /
      annotations:
        kubernetes.io/ingress.class: traefik
      pathType: ImplementationSpecific
      tls: false
```

Cet exemple utilise des identifiants **de démonstration locale**, à ne pas réutiliser pour un service exposé. Les deux PVC demandent la classe Minikube `standard`, à vérifier avec `kubectl get sc`. Les noms de champs sont sensibles à la casse : comparez-les aux valeurs du chart récupérées plus haut.

La configuration conserve HTTP pour cet exercice ; un accès HTTPS demanderait un certificat et une configuration TLS cohérente. L’URL locale sera accessible via le port-forward décrit ci-dessous.

Fichier `apps/owncloud/kustomization.yaml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - helmrepo.yaml
  - helmrelease.yaml
```

Vérifiez l’assemblage des fichiers :

```bash
kubectl kustomize apps > /tmp/td9-apps.yaml
find apps -maxdepth 2 -type f -print
```

**Rendu 38 — Fichiers OwnCloud prêts**

Capture de l’arborescence et résultat de la vérification locale.

#### 5.4.2 Push et preuve du déploiement automatique

```bash
git add apps
git commit -m "feat: deploy OwnCloud with Flux"
git push
flux reconcile source git apps -n flux-system
flux reconcile kustomization apps -n flux-system
kubectl get ns owncloud1
kubectl get pods -n owncloud1
kubectl get pvc -n owncloud1
flux get helmreleases -A
```

Attendez que le HelmRelease `release1` soit `Ready=True`, que les pods soient prêts et que les PVC soient `Bound`. En cas d’échec, consultez les erreurs avant de conclure au déploiement :

```bash
kubectl -n owncloud1 describe helmrelease release1
kubectl -n owncloud1 get events --sort-by=.metadata.creationTimestamp
flux get sources helm -A
```

Pour tester le routage HTTP sur tous les OS, gardez un terminal ouvert avec :

```bash
kubectl -n traefik port-forward service/traefik 8080:80
```

Ouvrez `http://owncloud.127.0.0.1.nip.io:8080`. Ce tunnel sert uniquement à l’accès navigateur ; les déploiements restent gérés par Flux.

**Rendu 39 — Déploiement automatique après push apps**

Capture des synchronisations Flux, des pods OwnCloud et des HelmRelease. Indiquez le commit déployé et vérifiez que les objets sont prêts. Une erreur de téléchargement du chart ou d’une image n’est pas une preuve de déploiement réussi.
