# 🧭 TD3 – Le tableau de bord Kubernetes (Dashboard)

## 1. Présentation

Le **Dashboard Kubernetes** est une interface web officielle permettant de visualiser et gérer les ressources d’un cluster.
Il offre une vue d’ensemble claire sur les déploiements, les services, les pods ou encore les namespaces.

💡 Pour un débutant, c’est un excellent point de départ : il rend concret le fonctionnement interne du cluster.

⚠️ En revanche, pour les environnements de production, il est déconseillé de l’exposer publiquement, car le Dashboard dispose souvent de privilèges élevés.

---

## 2. Utilisation sur un service managé

Sur les plateformes Kubernetes managées (GKE, EKS, AKS, OpenShift), le Dashboard n’est pas toujours installé par défaut.
Chaque fournisseur propose sa propre interface, mais il reste possible d’y déployer le Dashboard officiel.

🔗 Documentation officielle :
[https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)

---

## 3. Activation du Dashboard dans Minikube

Sous **Minikube**, le Dashboard est un **addon** prêt à être activé :

```bash
minikube addons enable dashboard
```

Sortie typique :

```bash
Using image kubernetesui/dashboard:v2.3.1
Using image kubernetesui/metrics-scraper:v1.0.7
Some dashboard features require the metrics-server addon.
To enable all features please run:
  minikube addons enable metrics-server
The 'dashboard' addon is enabled
```

Pour activer toutes les fonctionnalités :

```bash
minikube addons enable metrics-server
```

---

## 4. Accéder au Dashboard

Lancer l’interface web :

```bash
minikube dashboard
```

Cette commande :

- crée un tunnel sécurisé,
- lance le serveur local du Dashboard,
- ouvre le navigateur par défaut.

💡 Si la page ne s’ouvre pas, copie-colle l’URL affichée dans le terminal (souvent `http://127.0.0.1:xxxxx/...`).

---

## 5. Structure et navigation du Dashboard

Le Dashboard s’ouvre dans un navigateur, connecté automatiquement via le contexte `minikube`.

### Organisation générale

- **Barre latérale gauche** : familles d’objets Kubernetes (Workloads, Services, Configurations, Cluster, etc.)
- **Zone centrale** : détails des objets sélectionnés.

### Catégories principales

| Catégorie            | Contenu                                | Description                                |
| -------------------- | -------------------------------------- | ------------------------------------------ |
| Workloads            | Deployments, ReplicaSets, Pods, Jobs   | Applications déployées et leur état        |
| Services & Ingresses | Services, Endpoints, Ingress Rules     | Points d’accès réseau internes et externes |
| Config & Storage     | ConfigMaps, Secrets, PersistentVolumes | Configuration et stockage persistant       |
| Cluster              | Namespaces, Nodes, Events              | Informations globales du cluster           |
| Custom Resources     | CRD, opérateurs                        | Extensions Kubernetes personnalisées       |

💡 Chaque section correspond à une commande `kubectl get <type>` (ex. Workloads → Pods = `kubectl get pods`).

---

## 6. Création d’un premier déploiement : Mailpit

### Observation préalable

Dans **Config & Storage**, on trouve un secret `default-token`, créé automatiquement dans chaque namespace.
Il permet aux Pods d’accéder à l’API interne de Kubernetes via un **service account**.

### a. Présentation de Mailpit

Application de test :

- Fournit un serveur SMTP local simulé,
- Offre une interface web pour visualiser les mails,
- Idéale pour tester les déploiements simples.

Image Docker : `axllent/mailpit`
Documentation : [https://github.com/axllent/mailpit](https://github.com/axllent/mailpit)

### b. Déploiement depuis le Dashboard

1. Ouvre **Workloads → Deployments**
2. Clique sur **+ CREATE**
3. Choisis **Create from form**
4. Renseigne :
   - App name : `mailpit`
   - Container image : `axllent/mailpit`
   - Namespace : `default`
   - Replica count : `1`

5. Clique sur **Deploy**

Le Dashboard affiche ton application dans la liste des déploiements.

🧩 Vérifie que l’état du pod est **Running** et `READY` = 1/1.

---

## 7. Suivre et comprendre un déploiement

### a. Consulter l’état du déploiement

Menu : **Workloads → Deployments**

Les colonnes affichées :

- READY → Pods prêts
- UP-TO-DATE → synchronisés avec la dernière version
- AVAILABLE → accessibles
- AGE → durée depuis le lancement

### Détails du déploiement

En cliquant sur `mailpit`, tu obtiens :

- Nom, namespace, labels, annotations
- Stratégie de mise à jour (RollingUpdate)
- Liste des pods et ReplicaSets
- Événements récents

### Rôle du ReplicaSet

Chaque **Deployment** utilise un **ReplicaSet** pour maintenir le nombre de pods.
Lors d’une mise à jour, un nouveau ReplicaSet est créé pendant que l’ancien reste actif temporairement.

---

### b. Observation du ReplicaSet et des Pods

Le ReplicaSet maintient l’état souhaité du déploiement.

Depuis la fiche du déploiement, clique sur le **ReplicaSet actif** pour consulter :

- Nom (généré automatiquement : ex. `mailpit-xxxxxx`)
- Image utilisée
- Nombre de pods actifs
- Services associés
- Événements récents

💡 Un déploiement peut avoir plusieurs ReplicaSets, correspondant à différentes versions.

### c. Analyse d’un Pod

En cliquant sur un **Pod** associé :

- IP interne, ports exposés
- Conteneur et image
- Conditions (Ready, Initialized, Scheduled)
- Volumes, événements, logs

---

### d. Journaux d’activité

Clique sur **View Logs** dans la barre supérieure :
Affiche la sortie standard du conteneur (stdout).
Permet de diagnostiquer les erreurs (CrashLoopBackOff, ImagePullError, etc.).

---

### e. Mise à l’échelle (scaling)

1. Dans **Workloads → Deployments**
2. Menu ⋮ → **Scale**
3. Entrez `2` → **Apply**

🧩 Kubernetes crée automatiquement un second pod via le même ReplicaSet.

---

### f. Mise à jour (rolling update)

1. Ouvre le déploiement `mailpit`
2. Clique sur ✏️ **Edit**
3. Modifie :

```yaml
image: axllent/mailpit:latest
```

4. Enregistre avec **Save**

Un nouveau ReplicaSet est créé et les pods sont mis à jour progressivement.

---

## 8. Présentation de l’outil kubectl

### 1️⃣ – Préambule

`kubectl` est la CLI de référence pour interagir avec Kubernetes :

- création, suppression, modification d’objets
- observation de l’état du cluster
- exécution et logs

---

### 2️⃣ – Consultation des objets

```bash
kubectl get <type>
```

Exemple :

```bash
kubectl get namespaces
```

Sortie typique :

```
NAME                   STATUS   AGE
default                Active   19h
kube-system            Active   19h
kubernetes-dashboard   Active   19h
```

💡 `kubectl get ns` est un alias.
`kubectl get all -n kube-system` affiche tous les objets d’un namespace.

---

### 3️⃣ – Les Pods : unité d’exécution

Le **Pod** est l’unité minimale d’exécution.
Il peut contenir plusieurs conteneurs partageant la même IP et les mêmes volumes.

```bash
kubectl get pods
```

Exemple :

```
NAME                         READY   STATUS    RESTARTS   AGE
mailpit-77fd4ffc75-h8vv9     1/1     Running   0          3m15s
```

Pour plus de détails :

```bash
kubectl describe pod mailpit-77fd4ffc75-h8vv9
```

---

### 4️⃣ – Les Nodes du cluster

Les **nœuds** (nodes) sont les machines physiques ou virtuelles hébergeant les Pods.

#### a. Connexion à la machine Minikube

```bash
minikube ssh
hostname
```

Sortie : `minikube`

#### b. Liste des nœuds

```bash
kubectl get nodes
```

Exemple :

```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   44m   v1.29.3
```

#### c. Vue détaillée

```bash
kubectl get nodes -o wide
```

Affiche : IP interne, OS, version du noyau, runtime (`containerd://1.6.24`).

---

## 9. Le moteur Containerd de Minikube

### 1️⃣ – Initialisation

Minikube utilise **Containerd** comme moteur de conteneurs (runtime).
Il gère le téléchargement, l’exécution et l’isolation des conteneurs.

Connexion :

```bash
minikube ssh
```

Lister les namespaces internes :

```bash
sudo ctr namespace ls
```

Sortie :

```
NAME      LABELS
k8s.io
```

💡 `k8s.io` → utilisé par Kubernetes.
Les namespaces ici sont internes à Containerd, sans lien avec ceux de Kubernetes.

---

### 2️⃣ – Lister les conteneurs Kubernetes

```bash
sudo ctr -n k8s.io containers ls
```

Affiche tous les conteneurs exécutés par Kubernetes.

---

### 3️⃣ – Utiliser crictl (interface CRI)

Kubernetes communique avec Containerd via la **Container Runtime Interface (CRI)**.
Le client standard est **crictl**.

Lister les conteneurs :

```bash
sudo crictl ps
```

Filtrer par label (exemple : etcd) :

```bash
sudo crictl ps --label=io.kubernetes.container.name=etcd
```

Inspecter un conteneur :

```bash
sudo crictl inspect <ID>
```

---

### 4️⃣ – Résumé des outils

| Outil   | Rôle                             | Usage                          |
| ------- | -------------------------------- | ------------------------------ |
| ctr     | Client bas niveau de Containerd  | Debug interne                  |
| crictl  | Interface CRI standard           | Observation et diagnostic      |
| kubectl | Interface utilisateur Kubernetes | Gestion déclarative du cluster |

💡 **Chaîne d’exécution :**
`kubectl → CRI → Containerd → OS`

C’est cette chaîne qui permet à Kubernetes d’exécuter et d’orchestrer tes conteneurs.
