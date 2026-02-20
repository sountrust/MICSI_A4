# TD 9 — GitOps avec Flux (Minikube + GitLab)

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

#### 1.2.1 Désinstallation Helm

Exécutez :

```
helm -n ingress-nginx uninstall ingress-nginx
```

**Rendu 1 — Désinstallation ingress-nginx**

Fournissez une capture d’écran montrant la commande et sa sortie.

#### 1.2.2 Suppression du namespace

Exécutez :

```
kubectl delete ns ingress-nginx
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
kubectl get crd | awk '/monitoring.coreos.com/ {print $1}' | xargs -r kubectl delete crd
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
mkdir -p td-gitops
cd td-gitops

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

- Le dépôt **cluster** est le **support Flux** : Flux y stocke sa configuration (bootstrap) et l’infrastructure
