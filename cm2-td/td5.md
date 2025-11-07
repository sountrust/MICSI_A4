# TD 5 – Automatisation de déploiement par fichier YAML

---

## Partie 1 – Création et mise à jour d’objets Kubernetes via des fichiers YAML

### 1. Mécanisme de création et de mise à jour

Dans les chapitres précédents, l’application **Mailpit** a été déployée de deux manières :

- via le dashboard Kubernetes ;
- via la commande `kubectl create`.

Dans ces deux cas, la définition complète de l’objet (au format YAML) a été transmise à l’API Kubernetes.

Pour aller plus loin (mises à jour, Ingress, automatisation), il est préférable de manipuler directement ces fichiers YAML.

La commande `kubectl apply` est utilisée pour la gestion déclarative :

- elle crée un objet s’il n’existe pas ;
- elle met à jour un objet existant si le fichier a été modifié.

---

### 2. Structure YAML d’un déploiement

#### a. Quelques rappels

- `kubectl get deployment -o wide` : affiche les déploiements avec plus d’informations.
- `kubectl describe deployment <nom>` : affiche les détails complets de l’objet (labels, stratégie, réplicas, etc.).

#### b. Récupération d’une structure YAML

```bash
kubectl get deployment mailpit -o yaml
```

Exemple :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mailpit
  name: mailpit
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mailpit
  template:
    metadata:
      labels:
        app: mailpit
    spec:
      containers:
        - image: axllent/mailpit
          name: mailpit
```

> De nombreux champs sont ajoutés automatiquement (UID, timestamps, status). Ils ne doivent pas être repris dans un fichier modèle.

#### c. Édition d’un déploiement existant

```bash
kubectl edit deployment mailpit
```

Un éditeur (souvent _vi_) s’ouvre avec la définition complète de l’objet. Une fois modifié et sauvegardé, Kubernetes met à jour le déploiement.

> ⚠️ En cas d’erreur YAML, Kubernetes refusera la modification.

Pour changer d’éditeur :

```bash
export EDITOR=nano
```

> Mieux vaut modifier un fichier versionné et appliquer les changements avec `kubectl apply`.

#### d. Génération d’un squelette YAML

Créer un modèle minimal :

```bash
kubectl create deployment mailpit --image=axllent/mailpit \
  --dry-run=client -o yaml
```

Sortie :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mailpit
  labels:
    app: mailpit
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mailpit
  template:
    metadata:
      labels:
        app: mailpit
    spec:
      containers:
        - name: mailpit
          image: axllent/mailpit
```

Sauvegarde :

```bash
kubectl create deployment mailpit --image=axllent/mailpit \
  --dry-run=client -o yaml > mailpit-deployment.yaml
```

#### e. Création d’un déploiement depuis un fichier

```bash
kubectl apply -f mailpit-deployment.yaml
```

Résultats possibles :

- `deployment.apps/mailpit created` → création ;
- `deployment.apps/mailpit configured` → mise à jour.

> Un message _missing last-applied-configuration_ peut apparaître lors du premier apply, c’est normal.

#### f. Suppression depuis un fichier

```bash
kubectl delete -f mailpit-deployment.yaml
```

Sortie typique :

```
deployment.apps "mailpit" deleted
```

#### g. Idempotence et réentrance

Une commande est **idempotente** si la relancer ne modifie plus l’état. `kubectl apply` vise cet objectif :

```
deployment.apps/mailpit unchanged
```

Pour y parvenir, supprimer les champs non stables :

- `creationTimestamp`
- `strategy: {}`
- `resources: {}`
- `status: {}`

Version corrigée :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mailpit
  labels:
    app: mailpit
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mailpit
  template:
    metadata:
      labels:
        app: mailpit
    spec:
      containers:
        - name: mailpit
          image: axllent/mailpit
```

Résultat :

```
deployment.apps/mailpit configured
deployment.apps/mailpit unchanged
```

---

## 3. Création du service Mailpit

#### a. Génération du fichier YAML

```bash
kubectl expose deployment/mailpit --port 1025,8025 \
  --dry-run=client -o yaml
```

Sortie :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mailpit
  labels:
    app: mailpit
spec:
  ports:
    - name: port-1
      port: 1025
      targetPort: 1025
    - name: port-2
      port: 8025
      targetPort: 8025
  selector:
    app: mailpit
```

Sauvegarde :

```bash
kubectl expose deployment/mailpit --port 1025,8025 \
  --dry-run=client -o yaml > mailpit-service.yaml
```

#### b. Application du fichier service

```bash
kubectl apply -f mailpit-service.yaml
```

Sortie : `service/mailpit configured`

#### c. Idempotence du service

Supprimer `creationTimestamp` et `status` pour rendre le fichier stable :

```
service/mailpit unchanged
```

---

## Compatibilité et remarques selon le système d’exploitation

| Système                                      | Commandes inchangées                   | Particularités                                                         |
| -------------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------- |
| **Linux / macOS / Windows (Docker Desktop)** | `apply`, `delete`, `expose` identiques | Fichiers YAML éditables dans n’importe quel IDE (VS Code, nano, etc.). |
| **Windows (WSL2)**                           | Identique à Linux                      | Fichiers accessibles sous `/mnt/c/...`.                                |
| **macOS (Minikube / Docker Desktop)**        | Idem                                   | Préférer iTerm2 ou le terminal Docker Desktop.                         |

---

## Partie 2 – Sélecteurs, labels et regroupement d’objets

### 4. Mécanisme de sélecteur et labels

Lors de la création du service `mailpit`, la commande `kubectl expose` ajoute un **selector** qui relie le service aux pods du déploiement.

#### a. Exemple de mise à jour d’image

Si l’image change (`axllent/mailpit:v1.17`) :

- un nouveau ReplicaSet est créé ;
- un nouveau pod démarre ;
- l’ancien est supprimé.

Le service reste disponible grâce à son selector `app=mailpit`.

#### b. Structure d’exemple

```yaml
metadata:
  labels:
    app: mailpit
    version: v1
selector:
  app: mailpit
```

> Les selectors sont **immuables** : il faut supprimer puis recréer l’objet pour les modifier.

#### c. Sélection d’objets par label

```bash
kubectl get pods -l app=mailpit
kubectl get svc -l app=mailpit
kubectl get deploy -l app=mailpit
```

---

### 5. Regroupement de la création des éléments

#### a. Création d’un groupe d’objets

Organisation :

```bash
mkdir mailpit
mv mailpit-deployment.yaml mailpit/deployment.yaml
mv mailpit-service.yaml mailpit/service.yaml
kubectl apply -f ./mailpit
```

Sortie :

```
deployment.apps/mailpit unchanged
service/mailpit unchanged
```

#### b. Consultation de l’état d’un groupe

```bash
kubectl get -f ./mailpit
```

Exemple :

```
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/mailpit   1/1     1            1           20m
NAME             TYPE       CLUSTER-IP      PORT(S)            AGE
service/mailpit  ClusterIP  10.106.104.97   1025/TCP,8025/TCP  20m
```

---

### 6. Structure des objets Kubernetes

#### a. Interrogation avec `kubectl explain`

```bash
kubectl explain service
```

Extrait :

```
KIND:     Service
VERSION:  v1
FIELDS:
  apiVersion   <string>
  kind         <string>
  metadata     <Object>
  spec         <Object>
  status       <Object>
```

Afficher un champ particulier :

```bash
kubectl explain service.status
```

#### b. Référence de l’API Kubernetes

Documentation officielle : [https://kubernetes.io/docs/reference/](https://kubernetes.io/docs/reference/)

---

## Compatibilité et remarques selon le système d’exploitation

| Système                                      | Commandes inchangées                           | Particularités                           |
| -------------------------------------------- | ---------------------------------------------- | ---------------------------------------- |
| **Linux / macOS / Windows (Docker Desktop)** | `apply`, `get`, `explain`, `delete` identiques | Lecture récursive des répertoires YAML.  |
| **Windows (WSL2)**                           | Peut appliquer depuis `/mnt/c/...`             | Sauvegarder avec fin de ligne UNIX (LF). |
| **macOS (Minikube / Docker Desktop)**        | Identique à Linux                              | Éviter les encodages CRLF.               |

---

## Synthèse

À la fin de ce TD, vous devez être capable de :

1. Générer des fichiers YAML pour un **Deployment** et un **Service**.
2. Créer, mettre à jour et supprimer ces objets avec `kubectl apply` / `kubectl delete`.
3. Garantir l’idempotence (résultat `unchanged`).
4. Utiliser **labels** et **selectors** pour relier pods et services.
5. Gérer plusieurs fichiers regroupés dans un répertoire.
6. Consulter la structure d’un objet avec `kubectl explain` et la documentation officielle.
