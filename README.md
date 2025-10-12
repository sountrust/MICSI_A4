# Du monolithe aux microservices

Une application monolithique regroupe toutes les fonctionnalités dans un seul programme.

- Une base de code unique, un seul processus, un seul cycle de déploiement.
- Simplicité initiale mais forte dépendance interne entre les modules.
- Tout changement ou panne impacte l’ensemble du système.

Lien recommandé : [BD Kubernetes par Google Cloud](https://cloud.google.com/kubernetes-engine/kubernetes-comic/)

---

# Historique et contexte d'évolution

Dans les années 1990–2000, la majorité des applications d’entreprise étaient **monolithiques**.

- Modèle client-serveur : un serveur central, un code unique.
- Les mises à jour exigeaient souvent l’arrêt complet du service.
- La montée en charge reposait sur du matériel plus puissant (scalabilité verticale).

Progressivement, plusieurs facteurs ont poussé à découper le monolithe :

- **Complexification** des systèmes (nombre croissant de fonctionnalités).
- **Émergence du web** et besoin d’intégration entre services externes.
- **Nouveaux paradigmes** de développement collaboratif (DevOps, intégration continue).

Les premiers découpages se sont appuyés sur des **protocoles légers** et des **API standardisées** :

- **SOAP (1999)** et les _Web Services_ XML → premières tentatives d’interopérabilité.
- **REST (2000)** → communication simple sur HTTP avec formats légers (JSON, XML).
- **gRPC (2015)** → protocole binaire efficace basé sur HTTP/2 et Protobuf.

Ces technologies ont permis à des modules indépendants de dialoguer entre eux, amorçant la transition vers les microservices.

---

# Qu’est-ce qu’un microservice ?

Un **microservice** est une unité logique et fonctionnelle d’une application.

- Il implémente une fonction métier unique (ex. : facturation, authentification, API produit).
- Il s’exécute de manière **indépendante**, souvent sur une instance séparée.
- Chaque microservice a son propre cycle de développement et de déploiement.

Les microservices communiquent entre eux par des **APIs légères**, favorisant :

- la **modularité** du code,
- la **tolérance aux pannes**,
- la **scalabilité horizontale** (chaque service peut être répliqué selon la charge).

Cependant, cette modularité introduit de nouveaux défis : gestion de l’infrastructure, du réseau et du déploiement.

---

# Microservice vs conteneur

❌ Un **microservice n’est pas un conteneur**.

- Le microservice est un **concept logiciel** (composant applicatif indépendant).
- Le conteneur est un **mécanisme d’exécution** (environnement isolé pour un processus).

✔️ Un **conteneur** héberge souvent un **microservice** :

- Il contient le code, les dépendances et le runtime nécessaires à l’exécution.
- Il garantit la cohérence entre environnements de développement et de production.
- Il assure **l’immutabilité** : un conteneur déployé ne change pas, il est remplacé lors d’une mise à jour.
- Il offre **l’interopérabilité** : le même conteneur fonctionne sur tout hôte supportant un moteur de conteneurisation.

---

# Pourquoi la conteneurisation est essentielle

La conteneurisation répond aux limites des microservices déployés manuellement.

- Elle fournit un **environnement portable, standardisé et isolé**.
- Elle favorise l’**immutabilité** : on remplace les instances au lieu de les modifier.
- Elle favorise l’**interopérabilité** : les images fonctionnent sur n’importe quel système compatible.
- Elle simplifie le **déploiement et la montée en charge automatique**.
- Elle permet la **résilience** : les conteneurs peuvent être recréés automatiquement.

Ces deux propriétés — **immutabilité** et **interopérabilité** — sont au cœur de la philosophie cloud-native que Kubernetes orchestre à grande échelle.

---

# Limites du modèle monolithique

- Difficulté à faire évoluer ou à corriger sans recompiler tout le projet.
- Scalabilité uniquement **verticale** (plus de CPU/RAM sur une seule machine).
- Déploiement lent et risqué : un bug peut interrompre tout le service.
- Couplage fort entre équipes et technologies : impossible de faire cohabiter plusieurs stacks.

Exemple de processus monolithique :

```bash
java -jar application-complete.jar
```

Un seul binaire qui contient API, interface web, logique métier et accès aux données.

---

# Vers la modularité : l’idée des microservices

Le découpage en **microservices** vise à isoler chaque fonction dans un service autonome.

- Chaque microservice possède son propre code, ses dépendances, et sa base de données.
- Communication par API (HTTP, gRPC, message bus…).
- Permet une **scalabilité horizontale** : on réplique uniquement les parties sollicitées.
- Facilite les pipelines CI/CD : chaque service peut être testé et déployé indépendamment.

---

# Du point de vue architectural

| Aspect                | Monolithe     | Microservices                     |
| --------------------- | ------------- | --------------------------------- |
| **Couplage**          | Fort          | Faible                            |
| **Déploiement**       | Unique        | Indépendant                       |
| **Scalabilité**       | Verticale     | Horizontale                       |
| **Résilience**        | Panne globale | Isolement des pannes              |
| **Complexité réseau** | Faible        | Élevée (API, discovery, sécurité) |

Les microservices déplacent la complexité du code vers l’infrastructure réseau.

---

# Problème nouveau : comment exécuter tous ces services ?

Avec plusieurs microservices, chaque composant doit :

- Être isolé de manière fiable.
- Communiquer avec les autres services.
- Être mis à jour et supervisé sans perturber le reste.

Cela demande un **mécanisme d’isolation et de gestion** :
➡️ **la virtualisation** pour séparer les environnements,
➡️ **la conteneurisation** pour isoler les processus applicatifs.

Les deux technologies sont complémentaires :

- La virtualisation fournit la base matérielle.
- La conteneurisation offre la flexibilité logicielle.

---

# Exemple de transition pratique

Une équipe passe d’un monolithe à un premier microservice :

```bash
# Monolithe initial
java -jar monolith.jar

# Microservice isolé
python3 -m http.server 8080
```

Le service est désormais indépendant…
Mais pour en gérer **dizaines ou centaines**, il faudra les **isoler**, les **connecter** et les **orchestrer**.

➡️ Ce besoin mènera naturellement vers la virtualisation et la conteneurisation.

# Virtualisation : l'isolation matérielle

La virtualisation est la première étape vers la mutualisation efficace des ressources informatiques. Elle permet de faire fonctionner plusieurs systèmes d’exploitation et environnements logiciels sur un même matériel physique ou sur un ensemble de matériels agrégés.

---

# Définition et principe

La **virtualisation** consiste à créer plusieurs environnements indépendants appelés **machines virtuelles (VM)** à partir d’un ensemble de ressources physiques.

- Chaque VM dispose de son propre système d’exploitation, de son espace mémoire, de son stockage et de ses interfaces réseau.
- Ces environnements sont totalement isolés les uns des autres.
- Un **hyperviseur** orchestre la répartition et l’utilisation des ressources physiques.

Mais un hyperviseur ne se contente pas de diviser les ressources :

- Il peut **agréger plusieurs ressources matérielles de même type** (par exemple plusieurs processeurs physiques ou disques) pour les présenter comme une seule ressource virtuelle.
- Il peut ensuite **rediviser** cette ressource agrégée en plusieurs ressources virtuelles indépendantes des ressources matérielles sous-jacentes.

Ainsi, la virtualisation permet de découpler totalement l’environnement d’exécution des contraintes matérielles réelles.

---

# Les deux grands types d’hyperviseurs

### Hyperviseur de type 1 – _bare-metal_

- Fonctionne directement sur le matériel physique.
- Il gère le CPU, la mémoire, le stockage et le réseau sans passer par un OS hôte.
- Performances élevées, fiabilité accrue.
- Utilisé dans les environnements serveurs et data centers.

**Exemples :** VMware ESXi, Microsoft Hyper-V, KVM, Xen.

### Hyperviseur de type 2 – _hébergé_

- Fonctionne au-dessus d’un système d’exploitation déjà existant.
- Il virtualise les ressources fournies par l’OS hôte.
- Plus simple à installer, adapté aux postes de travail ou environnements de test.

**Exemples :** VirtualBox, VMware Workstation, Parallels Desktop.

---

# Rôle de l'hyperviseur

L’hyperviseur agit comme une couche d’abstraction entre le matériel et les machines virtuelles.

- Il **alloue dynamiquement** les ressources physiques selon les besoins des VMs.
- Il **isole** les environnements virtuels pour éviter toute interférence.
- Il **agrège** ou **fractionne** les ressources matérielles de manière transparente.

Schéma conceptuel :

```
Matériel physique (CPU, RAM, disque, réseau)
   ↓
Hyperviseur
   ↓ ↓ ↓
VM1 (Linux) | VM2 (Windows) | VM3 (Ubuntu Server)
```

---

# Avantages de la virtualisation

- **Isolation complète** : chaque VM est un environnement indépendant.
- **Mutualisation** : meilleure utilisation des ressources matérielles.
- **Portabilité** : les VMs peuvent être déplacées ou copiées sur d’autres hôtes.
- **Flexibilité** : création rapide d’environnements de test ou de production.
- **Abstraction** : indépendance entre le matériel réel et les environnements exécutés.

Exemple pratique : un serveur physique peut héberger plusieurs services (base de données, serveur web, stockage) chacun dans sa propre VM.

---

# Limites de la virtualisation

- **Surcharge système** : chaque VM embarque un OS complet → consommation mémoire importante.
- **Temps de démarrage élevé** comparé aux conteneurs.
- **Complexité de gestion** : maintenance et mises à jour multiples.

Pour répondre à cette complexité, de nouvelles approches sont apparues :

### Infrastructure as Code (IaC)

L’**Infrastructure as Code** propose une approche **déclarative** de la gestion des environnements.

- L’administrateur ou le développeur **décrit l’état attendu** de l’infrastructure (réseaux, machines, services, règles).
- Un outil d’automatisation se charge de **créer, configurer ou mettre à jour** les ressources pour atteindre cet état.
- Cette approche rapproche la gestion d’infrastructure de la logique logicielle : versionnage, réutilisation, et reproductibilité.

**Exemples d’outils IaC :**

- Terraform / OpenTofu : gestion d’infrastructures multi-clouds.
- Ansible, Puppet, Chef : automatisation des configurations.
- CloudFormation, Pulumi : gestion déclarative native du cloud.

Cette logique **déclarative**, déjà au cœur de la virtualisation moderne, sera reprise et amplifiée dans la conteneurisation et l’orchestration (voir section 4 sur Kubernetes).

---

# De la virtualisation à la conteneurisation

La conteneurisation ne remplace pas la virtualisation, elle s’appuie sur elle.

- Les VMs assurent l’isolation matérielle.
- Les conteneurs assurent l’isolation logicielle (niveau processus).

En pratique :

- Un cluster Kubernetes est souvent déployé **sur des VMs** (dans le cloud ou sur un hyperviseur local).
- Les conteneurs s’exécutent **à l’intérieur** de ces VMs.

Ce modèle combine la **sécurité et la robustesse de la virtualisation** avec la **légèreté et la rapidité des conteneurs**, fondant les architectures modernes dites _cloud-native_.

Conteneurisation : l’isolation logicielle

La conteneurisation représente une évolution de la virtualisation : elle isole non plus des systèmes d’exploitation entiers, mais des processus au sein d’un même noyau.

⸻

Définition et principe

Un conteneur est une unité d’exécution légère et portable qui regroupe :
• le code applicatif,
• ses dépendances (bibliothèques, configurations),
• et un environnement système minimal nécessaire à son fonctionnement.

Contrairement à une VM, un conteneur partage le noyau de l’hôte et n’embarque pas d’OS complet. Cela le rend beaucoup plus léger et rapide à déployer.

⸻

Mécanismes sous-jacents : isolation et contrôle

Les conteneurs reposent sur deux briques fondamentales du noyau Linux :
• Namespaces : isolation des espaces de noms (processus, utilisateurs, réseau, système de fichiers…). Chaque conteneur a sa propre vision du système.
• Cgroups (Control Groups) : limitation et suivi des ressources utilisées (CPU, mémoire, E/S disque, réseau).

Ces mécanismes permettent à plusieurs conteneurs de coexister sans interférer les uns avec les autres.

⸻

Comparaison VM vs Conteneur

Aspect Machine virtuelle Conteneur
Noyau Indépendant Partagé avec l’hôte
Taille Plusieurs Go Quelques Mo
Temps de démarrage Minutes Secondes
Isolement Complet (OS dédié) Logique (processus)
Performance Plus lourde Légère

⸻

Outils de conteneurisation
• Docker : moteur de conteneurisation le plus répandu, simplifie la création et la gestion d’images.
• Podman / Buildah : alternatives open-source à Docker, compatibles avec le standard OCI.
• containerd / CRI-O : moteurs utilisés dans les clusters Kubernetes.

⸻

Avantages de la conteneurisation
• Légèreté : exécution rapide, faible empreinte mémoire.
• Portabilité : même image exécutable sur toute plateforme compatible.
• Immutabilité : un conteneur ne change pas après son déploiement, il est remplacé par une nouvelle version.
• Interopérabilité : standardisation via les spécifications OCI (Open Container Initiative).
• Reproductibilité : même environnement de dev, test et production.

⸻

Exemple pratique : un conteneur simple

# Télécharger et exécuter un conteneur NGINX

sudo docker run -d -p 8080:80 nginx

# Vérifier le fonctionnement

curl http://localhost:8080

Le conteneur démarre en quelques secondes, expose un service web et s’exécute de manière isolée du reste du système.

⸻

De la conteneurisation à l’orchestration

Quand les applications nécessitent plusieurs conteneurs interconnectés (base de données, API, front-end, monitoring), il devient nécessaire de :
• automatiser les déploiements,
• gérer les dépendances et le réseau,
• assurer la tolérance aux pannes et la montée en charge.

Ces besoins ont conduit à l’apparition des orchestrateurs de conteneurs comme Docker Swarm, Mesos et surtout Kubernetes.
