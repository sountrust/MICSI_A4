---
# 📘 Table des matières
[TOC]
---

# 1️⃣ – Du monolithe aux microservices

> **Une application monolithique** regroupe toutes les fonctionnalités dans un seul programme.

---

## ⚙️ Caractéristiques

- Une **base de code unique**, un seul processus, un seul cycle de déploiement.
- Simplicité initiale ✅ mais forte **dépendance interne** ❌ entre les modules.
- Tout changement ou panne impacte **l’ensemble du système**.

📚 **Lien recommandé :**  
[BD Kubernetes par Google Cloud](https://cloud.google.com/kubernetes-engine/kubernetes-comic/)

---

## 🕰️ Historique et contexte d’évolution

Dans les années **1990–2000**, la majorité des applications d’entreprise étaient **monolithiques** :

- Architecture **client-serveur**
- Mises à jour nécessitant l’arrêt complet du service 🛑
- Scalabilité **verticale** (plus de matériel)

---

### 🚀 Les causes de l’évolution

- **Complexification** des systèmes
- **Émergence du web** et besoin d’intégration
- Nouveaux modèles **DevOps / CI/CD**

---

### 🌐 Les premières interconnexions

| Technologie | Année | Description                                  |
| ----------- | ----- | -------------------------------------------- |
| **SOAP**    | 1999  | Web Services XML (interopérabilité initiale) |
| **REST**    | 2000  | Communication simple HTTP (JSON / XML)       |
| **gRPC**    | 2015  | Protocole binaire performant basé sur HTTP/2 |

💬 Ces standards ont permis la communication entre modules indépendants, amorçant la **transition vers les microservices**.

---

## 🔍 Qu’est-ce qu’un microservice ?

Un **microservice** = une **unité fonctionnelle autonome** d’une application.

🧩 Il :

- Implémente une **fonction métier unique** (ex : facturation, login…)
- S’exécute **indépendamment**
- Possède son **cycle de vie propre**

---

### 🌉 Communication

Les microservices échangent via des **APIs légères**, favorisant :

- la **modularité** du code 🧠
- la **tolérance aux pannes** ⚡
- la **scalabilité horizontale** 📈

> ⚠️ Mais cette liberté ajoute une **complexité d’infrastructure** : réseau, monitoring, orchestration…

---

## 🐳 Microservice vs Conteneur

| ❌ Mythe                       | ✔️ Réalité                                                                                     |
| ------------------------------ | ---------------------------------------------------------------------------------------------- |
| Un microservice = un conteneur | Le microservice est **une idée logicielle**, le conteneur est **un environnement d’exécution** |

---

### 🧠 En résumé :

- **Microservice** → concept fonctionnel
- **Conteneur** → mécanisme technique

💡 Un conteneur **héberge souvent** un microservice :

- Inclut code + dépendances + runtime
- Assure **cohérence** entre environnements
- Garantit **immutabilité** et **interopérabilité**

---

## 🚢 Pourquoi la conteneurisation est essentielle

La conteneurisation répond aux limites du déploiement manuel.

✅ Avantages :

- Environnement **portable, standardisé, isolé**
- **Remplacement** plutôt que modification
- **Interopérabilité** multi-plateforme
- **Déploiement simplifié** et **résilient**

💡 Ces propriétés — _immutabilité_ et _interopérabilité_ — sont la base du **cloud-native** orchestré par **Kubernetes**.

---

## ⚠️ Limites du modèle monolithique

- Difficulté d’évolution et de correction
- Scalabilité **verticale uniquement**
- Déploiement **lent et risqué**
- **Couplage fort** entre équipes et technologies

Exemple :

```bash
java -jar application-complete.jar
```

> 🧱 Un seul binaire contenant API, UI, logique métier et données.

---

## 🧩 Vers la modularité : l’idée des microservices

- Chaque service = **code + dépendances + base de données**
- Communication via **API (HTTP, gRPC, message bus)**
- **Scalabilité horizontale** ciblée
- **CI/CD** facilité 🎯

---

## 🧠 Vue architecturale

| Aspect            | 🧱 Monolithe  | 🧩 Microservices     |
| ----------------- | ------------- | -------------------- |
| Couplage          | Fort 🔗       | Faible 🔓            |
| Déploiement       | Unique        | Indépendant          |
| Scalabilité       | Verticale     | Horizontale          |
| Résilience        | Panne globale | Isolement des pannes |
| Complexité réseau | Faible        | Élevée ⚙️            |

> 👉 Les microservices déplacent la complexité **du code vers l’infrastructure**.

---

## 🧰 Problème nouveau : l’exécution de tous ces services

Chaque microservice doit :

- Être **isolé** de manière fiable 🧳
- **Communiquer** avec les autres services 🌐
- Être **mis à jour** sans perturber le reste ♻️

➡️ Cela demande un **mécanisme d’isolation et de gestion** :

- **Virtualisation** pour séparer les environnements 💻
- **Conteneurisation** pour isoler les processus 🧱

Les deux sont **complémentaires** :

- Virtualisation → base matérielle ⚙️
- Conteneurisation → flexibilité logicielle 🧩

---

## 💡 Exemple de transition pratique

```bash
# Monolithe initial
java -jar monolith.jar

# Microservice isolé
python3 -m http.server 8080
```

> Le service devient indépendant, mais pour en gérer **des dizaines ou centaines**, il faut les **isoler**, les **connecter** et les **orchestrer**.

➡️ Ce besoin mènera naturellement vers la **virtualisation et la conteneurisation**.

---

# 2️⃣ – Virtualisation : l’isolation matérielle

> La virtualisation permet d’exécuter plusieurs environnements sur une même machine physique.

## 🔍 Définition

La **virtualisation** crée plusieurs **machines virtuelles (VM)** à partir de ressources physiques :

- Chaque VM possède son propre **OS**, mémoire, stockage, réseau.
- Un **hyperviseur** gère la répartition des ressources.

---

## 🧩 Types d’hyperviseurs

### Type 1 — _Bare Metal_

- Fonctionne **directement sur le matériel**.
- Haute performance et fiabilité.
- Utilisé dans les **data centers**.

> Exemples : VMware ESXi, Hyper-V, KVM, Xen.

### Type 2 — _Hébergé_

- Fonctionne **au-dessus d’un OS hôte**.
- Simplicité d’installation.
- Idéal pour **tests ou postes de travail**.

> Exemples : VirtualBox, VMware Workstation, Parallels.

---

## 🧠 Rôle de l’hyperviseur

- Alloue dynamiquement les ressources 💾
- Isole les environnements 🔒
- Agrège ou fractionne le matériel selon les besoins ⚙️

```
Matériel physique (CPU, RAM, disque)
   ↓
Hyperviseur
   ↓ ↓ ↓
VM1 (Linux) | VM2 (Windows) | VM3 (Ubuntu)
```

---

## ✅ Avantages de la virtualisation

- Isolation complète 🧱
- Mutualisation du matériel 💰
- Portabilité 🧳
- Flexibilité 🧠
- Abstraction matérielle 🔌

💡 Exemple : un serveur physique héberge plusieurs VMs (DB, web, stockage).

---

## ⚠️ Limites

- **Surcharge mémoire** (chaque VM a son OS)
- **Démarrage lent** 🐢
- **Gestion complexe** ⚙️

➡️ Naissance de l’**Infrastructure as Code (IaC)** 💻

---

## ⚙️ Infrastructure as Code (IaC)

> L’IaC décrit l’infrastructure comme du **code déclaratif**.

- Décrit l’**état attendu** (VMs, réseaux, services)
- Automatisation de la **création et configuration**
- Facilite **versionnage, reproductibilité, CI/CD**

🧰 **Outils IaC :** Terraform, OpenTofu, Ansible, Puppet, Chef, CloudFormation, Pulumi.

---

## 🐳 De la virtualisation à la conteneurisation

> La conteneurisation **ne remplace pas** la virtualisation, elle s’appuie dessus.

- Les **VMs** assurent l’isolation matérielle 🔒
- Les **conteneurs** assurent l’isolation logicielle 🧩

💡 Kubernetes combine la **robustesse** des VMs et la **légèreté** des conteneurs.

---

# 3️⃣ – Conteneurisation : l’isolation logique

Un **conteneur** = code + dépendances + environnement minimal.

Contrairement à une VM, il **partage le noyau** de l’hôte.  
➡️ Plus léger, plus rapide ⚡

## 🔧 Mécanismes Linux

- **Namespaces** → isolation (processus, utilisateurs, FS, réseau)
- **Cgroups** → contrôle des ressources (CPU, mémoire…)

---

## ⚖️ Comparaison VM vs Conteneur

| Aspect      | 💻 VM        | 📦 Conteneur |
| ----------- | ------------ | ------------ |
| Noyau       | Indépendant  | Partagé      |
| Taille      | Plusieurs Go | Quelques Mo  |
| Démarrage   | Minutes 🕐   | Secondes ⚡  |
| Isolement   | Complet      | Logique      |
| Performance | Lourde       | Légère       |

---

## 🧰 Outils de conteneurisation

- Docker 🐳 — moteur principal
- Podman / Buildah — alternatives open-source
- containerd / CRI-O — moteurs Kubernetes

---

## 🚀 Avantages

- **Légèreté**, **portabilité**, **immutabilité**
- **Interopérabilité** (standard OCI)
- **Reproductibilité** entre dev/test/prod

---

## 🧪 Exemple : conteneur NGINX

```bash
sudo docker run -d -p 8080:80 nginx
curl http://localhost:8080
```

> Le conteneur démarre en secondes et expose un service web isolé.

---

# 4️⃣ – Kubernetes : orchestrer les conteneurs virtualisés

Quand plusieurs conteneurs doivent coopérer :

- Automatiser les déploiements ⚙️
- Gérer le réseau et les dépendances 🌐
- Assurer la tolérance aux pannes 💪
- Monter en charge 📈

➡️ Apparition des **orchestrateurs** : Docker Swarm, Mesos, **Kubernetes** 🚀

## Orchestration & Kubernetes — "état désiré" et réconciliation

> **Objectif** — Comprendre comment Kubernetes orchestre des applications conteneurisées en appliquant un **modèle déclaratif** ("état désiré") et des **boucles de réconciliation**. Découvrir les **objets clés** (Pod, Deployment, Service, Ingress) et la mécanique d'auto-rétablissement (_self‑healing_).

---

## 🎯 Résultats d'apprentissage

- Expliquer le principe **déclaratif** : on décrit _ce qu'on veut_, pas _comment le faire_.
- Décrire le cycle **réconciliation → action → observation** dans Kubernetes.
- Identifier les **composants** : API Server, etcd, Scheduler, Controllers, Kubelet, Runtime.
- Lire/écrire des **manifestes YAML** pour Pods / Deployments / Services / Ingress.
- Mettre à l'échelle (scaling) et comprendre l'**auto‑guérison** (remplacement de Pods).

---

## 🧠 Déclaratif vs impératif

- **Impératif** : "exécute ces commandes dans cet ordre" → fragile, non idempotent.
- **Déclaratif** : "voici **l'état désiré** du système" → le contrôleur converge vers cet état.

> **Parallèle IaC** : Terraform/Ansible décrivent l'infra ; **Kubernetes** décrit l'état applicatif (et réseau/stockage associés) au niveau **service**.

---

## 🔁 Boucle de réconciliation (vue système)

```mermaid
flowchart LR
  subgraph User[Développeur]
    A(Manifeste YAML: état désiré)
  end
  A -->|kubectl/apply| B[API Server]
  B --> C[(etcd\nstocke état désiré)]
  B --> D[Controllers]
  D --> E{Compare\nétat réel ?}
  E -- non --> F[Créer/Remplacer/Scaler Pods]
  F --> G[Kubelet sur Nodes]
  G --> H[Containers (containerd/CRI-O)]
  H --> I[États et événements]
  I --> D
  E -- oui --> J[Convergence]
```

---

## 🧱 Objets fondamentaux

- **Pod** : plus petite unité déployable (un ou plusieurs conteneurs + réseau/volumes partagés).
- **ReplicaSet** : garantit _n_ réplicas identiques d'un Pod (généré par un Deployment).
- **Deployment** : stratégie de mise à jour (rolling update), historique, rollback.
- **Service** : point d'accès réseau stable vers un ensemble de Pods (ClusterIP / NodePort / LoadBalancer).
- **Ingress** : règles HTTP(S) vers des Services (via un _Ingress Controller_ — ex. Traefik).
- **Namespace** : cloisonnement logique (quotas, RBAC, isolation).
- **ConfigMap/Secret** : configuration externe & données sensibles.

---

## 📄 Pod minimal (lecture seule)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  labels: { app: demo }
spec:
  containers:
    - name: web
      image: nginx:1.25
      ports: [{ containerPort: 80 }]
      resources:
        requests: { cpu: "100m", memory: "64Mi" }
        limits: { cpu: "300m", memory: "128Mi" }
      readinessProbe:
        httpGet: { path: "/", port: 80 }
        initialDelaySeconds: 3
        periodSeconds: 5
```

---

## 📦 Deployment (état désiré réplicas=3)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deploy
  labels: { app: web }
spec:
  replicas: 3
  selector: { matchLabels: { app: web } }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 1, maxSurge: 1 }
  template:
    metadata: { labels: { app: web } }
    spec:
      containers:
        - name: web
          image: nginx:1.25
          ports: [{ containerPort: 80 }]
          resources:
            requests: { cpu: "100m", memory: "64Mi" }
            limits: { cpu: "300m", memory: "128Mi" }
          livenessProbe:
            httpGet: { path: "/", port: 80 }
            initialDelaySeconds: 5
            periodSeconds: 10
```

---

## 🌐 Service + Ingress (exposition HTTP locale)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-svc
spec:
  type: ClusterIP
  selector: { app: web }
  ports:
    - port: 80
      targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ing
  annotations:
    kubernetes.io/ingress.class: traefik
spec:
  rules:
    - host: web.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-s
```
