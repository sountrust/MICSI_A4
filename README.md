# 🧠 Cours Kubernetes – Architecture, déploiement et orchestration

## 🎯 Objectifs du module

Ce module vise à comprendre **les principes fondamentaux de Kubernetes** à travers :

- des **cours magistraux (CM)** pour introduire les concepts et la théorie,
- des **travaux dirigés (TD)** pour expérimenter pas à pas,
- et des **supports pratiques** permettant la manipulation sur Minikube et Git.

L’objectif est de rendre l’étudiant **autonome dans la mise en œuvre et l’observation d’un cluster Kubernetes**, du déploiement d’une simple application à la gestion de services exposés et isolés.

---

## 🗂️ Structure du dépôt

| Dossier/Fichier    | Description                                                                                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CM1.md`           | Introduction à la conteneurisation, Docker, et mise en place de Minikube. Comprend la transition entre Docker et Kubernetes, la découverte des composants d’un cluster et la manipulation initiale via `kubectl`. |
| `CM2.md`           | Compréhension des fichiers YAML, création d’objets Kubernetes (Namespace, Deployment, Service, Ingress, NetworkPolicy). Introduction à la logique déclarative et à l’isolation des ressources.                    |
| `TD1/`             | Travaux dirigés – Installation de Docker, Git et Minikube sous Linux. Vérifications d’environnement et configuration initiale du cluster.                                                                         |
| `TD2/`             | Travaux dirigés – Création et déploiement d’une première application dans Minikube (depuis une image Docker). Découverte du `kubectl apply` et observation des Pods.                                              |
| `TD3/`             | Travaux dirigés – Exploration du **Kubernetes Dashboard** et utilisation de **kubectl** pour consulter et interagir avec les objets. Introduction à Containerd et `crictl`.                                       |
| `TD4/` _(à venir)_ | Travaux dirigés – Exposition d’applications avec Ingress et observation des métriques (Lens, Prometheus, metrics-server).                                                                                         |
| `assets/`          | Schémas, captures et diagrammes Mermaid (architecture réseau, hiérarchie YAML, flux de données).                                                                                                                  |

---

## 🧩 Progression pédagogique

### CM1 – Introduction à Kubernetes et conteneurisation

- Du conteneur Docker à l’orchestrateur Kubernetes
- Architecture d’un cluster : Control Plane, Nodes, Pods
- Commandes de base `kubectl`, `minikube`
- Installation et environnement de travail

**TD1 & TD2** : mise en pratique et premiers déploiements sur Minikube.

---

### CM2 – Structure, isolation et exposition

- Définition et syntaxe du format YAML
- Structure d’un manifest Kubernetes
- Multi-ressources et logique déclarative
- Notion de namespace, isolation logique
- Exposition via Service et Ingress
- Sécurité réseau avec les NetworkPolicies

**TD3** : exploration du tableau de bord et inspection des ressources avec `kubectl`.

---

### CM3 (prévisionnel) – Observabilité et supervision

- Introduction à **Lens**, **Prometheus** et **metrics-server**
- Visualisation des ressources et suivi du cluster
- Monitoring des Pods et métriques système
- Analyse des logs et scaling automatique (HPA)

**TD4** : mise en place du monitoring, Ingress Controller (Traefik), métriques réseau.

---

## 🧰 Prérequis techniques

- Linux Ubuntu 22.04+ (VM ou bare-metal)
- Docker Engine / Containerd
- Minikube 1.33+
- kubectl CLI
- Git (pour cloner et versionner les TD)
- (Optionnel) Lens pour visualisation graphique

---

## 🚀 Pour commencer

```bash
# Cloner le dépôt
git clone https://gitlab.univ.example.com/cours/kubernetes.git
cd kubernetes

# Démarrer Minikube
minikube start --cpus=6 --memory=8g

# Vérifier l’installation
kubectl cluster-info
kubectl get nodes
```

---

## 🧭 Navigation

- 📘 [CM1 – Découverte de Kubernetes et Minikube](./CM1.md)
- 📘 [CM2 – YAML, Namespaces et exposition réseau](./CM2.md)
- 🧪 [TD1 – Installation et configuration](./TD1/)
- 🧪 [TD2 – Premier déploiement](./TD2/)
- 🧪 [TD3 – Dashboard et kubectl](./TD3/)

---

## 📚 Licence et utilisation

Ce support est destiné à un usage pédagogique dans le cadre du module _Administration de systèmes et services – Kubernetes_.
Toute reproduction ou diffusion doit mentionner l’auteur et l’université.

---

> _« Kubernetes n’est pas une technologie à apprendre, c’est un écosystème à apprivoiser. »_ 🌀
