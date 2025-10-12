# 🧱 Du monolithe aux microservices

> **Une application monolithique** regroupe toutes les fonctionnalités dans un seul programme.

---

### ⚙️ Caractéristiques

- Une **base de code unique**, un seul processus, un seul cycle de déploiement.
- Simplicité initiale ✅ mais forte **dépendance interne** ❌ entre les modules.
- Tout changement ou panne impacte **l’ensemble du système**.

📚 **Lien recommandé :**  
[BD Kubernetes par Google Cloud](https://cloud.google.com/kubernetes-engine/kubernetes-comic/)

---

# 🕰️ Historique et contexte d’évolution

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

# 🔍 Qu’est-ce qu’un microservice ?

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

# 🐳 Microservice vs Conteneur

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

# 🚢 Pourquoi la conteneurisation est essentielle

La conteneurisation répond aux limites du déploiement manuel.

✅ Avantages :

- Environnement **portable, standardisé, isolé**
- **Remplacement** plutôt que modification
- **Interopérabilité** multi-plateforme
- **Déploiement simplifié** et **résilient**

💡 Ces propriétés — _immutabilité_ et _interopérabilité_ — sont la base du **cloud-native** orchestré par **Kubernetes**.

---

# ⚠️ Limites du modèle monolithique

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

# 🧩 Vers la modularité : l’idée des microservices

- Chaque service = **code + dépendances + base de données**
- Communication via **API (HTTP, gRPC, message bus)**
- **Scalabilité horizontale** ciblée
- **CI/CD** facilité 🎯

---

# 🧠 Vue architecturale

| Aspect            | 🧱 Monolithe  | 🧩 Microservices     |
| ----------------- | ------------- | -------------------- |
| Couplage          | Fort 🔗       | Faible 🔓            |
| Déploiement       | Unique        | Indépendant          |
| Scalabilité       | Verticale     | Horizontale          |
| Résilience        | Panne globale | Isolement des pannes |
| Complexité réseau | Faible        | Élevée ⚙️            |

> 👉 Les microservices déplacent la complexité **du code vers l’infrastructure**.

---

# 🧰 Problème nouveau : l’exécution de tous ces services

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

# 💡 Exemple de transition pratique

```bash
# Monolithe initial
java -jar monolith.jar

# Microservice isolé
python3 -m http.server 8080
```

> Le service devient indépendant, mais pour en gérer **des dizaines ou centaines**, il faut les **isoler**, les **connecter** et les **orchestrer**.

➡️ Ce besoin mènera naturellement vers la **virtualisation et la conteneurisation**.

---

# 🧱 Virtualisation : l'isolation matérielle

> La virtualisation permet d’exécuter plusieurs environnements sur une même machine physique.

### 🔍 Définition

La **virtualisation** crée plusieurs **machines virtuelles (VM)** à partir de ressources physiques :

- Chaque VM possède son propre **OS**, mémoire, stockage, réseau.
- Un **hyperviseur** gère la répartition des ressources.

---

### 🧩 Types d’hyperviseurs

#### Type 1 — _Bare Metal_

- Fonctionne **directement sur le matériel**.
- Haute performance et fiabilité.
- Utilisé dans les **data centers**.

> Exemples : VMware ESXi, Hyper-V, KVM, Xen.

#### Type 2 — _Hébergé_

- Fonctionne **au-dessus d’un OS hôte**.
- Simplicité d’installation.
- Idéal pour **tests ou postes de travail**.

> Exemples : VirtualBox, VMware Workstation, Parallels.

---

### 🧠 Rôle de l’hyperviseur

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

### ✅ Avantages de la virtualisation

- Isolation complète 🧱
- Mutualisation du matériel 💰
- Portabilité 🧳
- Flexibilité 🧠
- Abstraction matérielle 🔌

💡 Exemple : un serveur physique héberge plusieurs VMs (DB, web, stockage).

---

### ⚠️ Limites

- **Surcharge mémoire** (chaque VM a son OS)
- **Démarrage lent** 🐢
- **Gestion complexe** ⚙️

➡️ Naissance de l’**Infrastructure as Code (IaC)** 💻

---

# ⚙️ Infrastructure as Code (IaC)

> L’IaC décrit l’infrastructure comme du **code déclaratif**.

- Décrit l’**état attendu** (VMs, réseaux, services)
- Automatisation de la **création et configuration**
- Facilite **versionnage, reproductibilité, CI/CD**

🧰 **Outils IaC :** Terraform, OpenTofu, Ansible, Puppet, Chef, CloudFormation, Pulumi.

---

# 🐳 De la virtualisation à la conteneurisation

> La conteneurisation **ne remplace pas** la virtualisation, elle s’appuie dessus.

- Les **VMs** assurent l’isolation matérielle 🔒
- Les **conteneurs** assurent l’isolation logicielle 🧩

💡 Kubernetes combine la **robustesse** des VMs et la **légèreté** des conteneurs.

---

# 📦 Conteneurisation : l’isolation logicielle

Un **conteneur** = code + dépendances + environnement minimal.

Contrairement à une VM, il **partage le noyau** de l’hôte.
➡️ Plus léger, plus rapide ⚡

---

### 🔧 Mécanismes Linux

- **Namespaces** → isolation (processus, utilisateurs, FS, réseau)
- **Cgroups** → contrôle des ressources (CPU, mémoire…)

---

### ⚖️ Comparaison VM vs Conteneur

| Aspect      | 💻 VM        | 📦 Conteneur |
| ----------- | ------------ | ------------ |
| Noyau       | Indépendant  | Partagé      |
| Taille      | Plusieurs Go | Quelques Mo  |
| Démarrage   | Minutes 🕐   | Secondes ⚡  |
| Isolement   | Complet      | Logique      |
| Performance | Lourde       | Légère       |

---

### 🧰 Outils de conteneurisation

- Docker 🐳 — moteur principal
- Podman / Buildah — alternatives open-source
- containerd / CRI-O — moteurs Kubernetes

---

### 🚀 Avantages

- **Légèreté**, **portabilité**, **immutabilité**
- **Interopérabilité** (standard OCI)
- **Reproductibilité** entre dev/test/prod

---

### 🧪 Exemple : conteneur NGINX

```bash
sudo docker run -d -p 8080:80 nginx
curl http://localhost:8080
```

> Le conteneur démarre en secondes et expose un service web isolé.

---

# ☸️ De la conteneurisation à l’orchestration

Quand plusieurs conteneurs doivent coopérer :

- Automatiser les déploiements ⚙️
- Gérer le réseau et les dépendances 🌐
- Assurer la tolérance aux pannes 💪
- Monter en charge 📈

➡️ Apparition des **orchestrateurs** : Docker Swarm, Mesos, **Kubernetes** 🚀

```

```
