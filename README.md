# 🧠 Cours Kubernetes – Architecture, déploiements et GitOps

## 🎯 Objectifs du module

Ce module vise à maîtriser **les principes fondamentaux de Kubernetes** et leur mise en œuvre **en conditions réalistes** :

- des **cours magistraux (CM)** pour introduire les concepts et la théorie,
- des **travaux dirigés (TD)** pour pratiquer étape par étape,
- une progression qui conduit vers une méthode de déploiement moderne : **GitOps avec Flux**.

L’objectif est de rendre l’étudiant **autonome dans l’exploitation d’un cluster Kubernetes local (Minikube)** : déploiement d’applications, exposition réseau, isolation, observabilité, puis automatisation des déploiements à partir de Git.

---

## 🗂️ Structure du dépôt

| Dossier/Fichier | Description                                                                                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CM1.md`        | Conteneurisation, Docker, et mise en place de Minikube. Transition Docker → Kubernetes, découverte des composants du cluster, premières manipulations `kubectl`. |
| `CM2.md`        | Modèle déclaratif, structure YAML, objets Kubernetes (Namespace, Deployment, Service, Ingress, NetworkPolicy). Logique d’isolation et de connectivité interne.   |
| `CM3.md`        | Exposition, observabilité et supervision : services, ingress, métriques, principes de monitoring et préparation au déploiement automatisé.                       |
| `cm1-td/td1.md` | Mise en place de l’environnement de travail (outils, validation Minikube, premiers contrôles).                                                                   |
| `cm1-td/td2.md` | Premier déploiement applicatif, observation des Pods/Services, premières opérations de diagnostic.                                                               |
| `cm1-td/td3.md` | Inspection du cluster (Dashboard/CLI), compréhension des ressources et premières explorations réseau.                                                            |
| `cm2-td/td4.md` | Ingress Controller avec **Traefik** en environnement local, exposition des applications et règles de routage.                                                    |
| `cm2-td/td5.md` | Monitoring avec **Prometheus** : principes, déploiement, vérifications et lecture de métriques.                                                                  |
| `cm2-td/td6.md` | Approfondissement : supervision, objets avancés, diagnostic et contrôle de la visibilité applicative.                                                            |
| `cm3-td/td7.md` | Packaging applicatif avec Helm : recherche, installation, upgrade, rollback.                                                                                     |
| `cm3-td/td8.md` | Déploiements complets avec Helm et bonnes pratiques (valeurs, namespaces, persistance).                                                                          |
| `cm3-td/td9.md` | **GitOps avec Flux** : infrastructure (Traefik + Prometheus) et application (OwnCloud) déployées automatiquement depuis Git.                                     |
| `assets/`       | Styles et ressources associées (ex. CSS pour export PDF).                                                                                                        |
| `out/`          | Répertoire de sortie (ex. PDFs générés). Doit rester hors versionnement.                                                                                         |

---

## 🧩 Progression pédagogique

### CM1 – Fondations : conteneurisation et cluster local

- Du conteneur Docker à l’orchestrateur Kubernetes
- Architecture d’un cluster : Control Plane, Nodes, Pods
- Commandes de base : `kubectl`, `minikube`
- Mise en place et validation de l’environnement

**TD1 à TD3** : mise en pratique sur Minikube, inspection des ressources, compréhension des objets et premiers diagnostics.

---

### CM2 – Déclaratif, réseau, isolation

- YAML : structure, lisibilité et bonnes pratiques
- Manifests Kubernetes : `metadata`, `spec`, `selector`, labels
- Namespaces : organisation et périmètre d’administration
- Services & DNS interne
- Ingress : exposition HTTP(S) via Traefik
- NetworkPolicies : contrôle des flux

**TD4 à TD6** : exposition réseau avec Traefik, supervision et premières approches d’observabilité.

---

### CM3 – Déploiement industrialisé : Helm puis GitOps

- Helm : charts, releases, upgrade/rollback
- Déploiement d’applications packagées et paramétrables
- Infrastructure & applications pilotées par Git : **GitOps**
- Introduction à Flux : synchronisation, réconciliation et traçabilité

**TD7 à TD9** : Helm puis déploiement GitOps complet (Traefik + Prometheus + OwnCloud) à partir de deux dépôts Git.

---

## 🧰 Prérequis techniques

- Linux Ubuntu 22.04+ (VM ou bare-metal)
- Docker Engine / Containerd
- Minikube 1.33+
- kubectl
- Git
- (Optionnel) Lens

---

## 🚀 Pour commencer

```bash
# Cloner le dépôt
git clone https://iut-git.unice.fr/pimbert/virtualadvanced.git
cd virtualadvanced

# Démarrer Minikube
minikube start --cpus=6 --memory=8g

# Vérifier l’installation
kubectl cluster-info
kubectl get nodes
```
