# 🧩 TD1 – Du Docker à MicroK8s sous Linux

## 🎯 Objectifs pédagogiques

- Installer et configurer l’environnement complet sous **Linux** (Docker, Git, Minikube, Kubectl).
- Comprendre la chaîne logique : **Docker → Image → Cluster local (Minikube)**.
- Déployer et tester une application conteneurisée.
- Vérifier le fonctionnement du fichier `~/.kube/config` et les interactions entre outils.

---

## 1️⃣ Installation et préparation de l’environnement

### 🔧 Mise à jour du système

```bash
sudo apt update && sudo apt upgrade -y
```

### 🐳 Installer Docker

```bash
sudo apt install -y docker.io
sudo systemctl enable docker --now
sudo usermod -aG docker $USER
newgrp docker
```

Vérification :

```bash
docker --version
docker ps
docker images
```

### 📦 Installer Minikube et Kubectl

```bash
sudo apt install -y curl apt-transport-https virtualbox virtualbox-ext-pack
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Vérification :

```bash
minikube version
kubectl version --client
```

### 🧰 Installer Git

```bash
sudo apt install -y git
```

Vérification :

```bash
git --version
```

---

## 2️⃣ Lancer le cluster Minikube

Démarrer le cluster avec le driver Docker :

```bash
minikube start --driver=docker
```

Vérification :

```bash
minikube status
kubectl get nodes
kubectl cluster-info
```

➡️ Le nœud doit être **Ready** et le cluster doit afficher les URL de l’API Server et du dashboard.

---

## 3️⃣ Vérifier la configuration Kubernetes (`~/.kube/config`)

Lister le contenu :

```bash
ls ~/.kube/
```

Ouvrir le fichier :

```bash
vim ~/.kube/config
```

Points à observer :

- `clusters:` → définition du cluster local (adresse API Server)
- `users:` → identifiants de connexion
- `contexts:` → combinaison cluster + user
- `current-context:` → cluster actuellement utilisé

Changer de contexte (si plusieurs existent) :

```bash
kubectl config get-contexts
kubectl config use-context minikube
```

Vérifier :

```bash
kubectl cluster-info
```

---

## 4️⃣ Créer une image Docker locale

Créer un **Dockerfile** minimal :

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

Créer un fichier `index.html` :

```html
<h1>Bienvenue sur votre premier conteneur Docker !</h1>
```

Construire et vérifier :

```bash
docker build -t demo-web:1.0 .
docker images | grep demo-web
```

Tester localement :

```bash
docker run -d -p 8080:80 demo-web:1.0
docker ps
curl http://localhost:8080
```

Arrêter et nettoyer :

```bash
docker stop $(docker ps -q)
```

---

## 5️⃣ Charger l’image dans Minikube

Construire l’image **directement dans le démon Docker de Minikube** :

```bash
eval $(minikube -p minikube docker-env)
docker build -t demo-web:1.0 .
docker images | grep demo-web
```

Vérifier que l’image est bien visible dans le cluster :

```bash
minikube image ls | grep demo-web
```

---

## 6️⃣ Déployer un Pod dans Kubernetes

Créer le Pod :

```bash
kubectl run demo-web --image=demo-web:1.0 --port=80 --image-pull-policy=Never
```

Vérifier :

```bash
kubectl get pods -o wide
```

Suivre les logs :

```bash
kubectl logs -l run=demo-web
```

Exposer le Pod localement :

```bash
kubectl port-forward pod/demo-web 8080:80
```

Tester :

```bash
curl http://localhost:8080
```

---

## 7️⃣ Observation et diagnostic

Lister les images dans Minikube :

```bash
minikube image ls
```

Lister les services et pods :

```bash
kubectl get all -o wide
```

Inspecter le Pod :

```bash
kubectl describe pod demo-web
```

Afficher l’état du cluster :

```bash
kubectl cluster-info dump | grep demo-web -A5
```

---

## 8️⃣ Utilisation de Git pour versionner le travail

Initialiser un dépôt local :

```bash
git init
git add Dockerfile index.html

git commit -m "TD1 - Création de l’image demo-web et déploiement sur Minikube"
```

Ajouter le dépôt distant :

```bash
git remote add origin https://gitlab.example.com/virtualisation/cm1-td.git
git push -u origin main
```

Vérifier :

```bash
git status
git log --oneline
```

---

## 🧠 Bilan du TD1

- Installation complète de Docker, Minikube, Kubectl et Git.
- Création, test et déploiement d’une image Docker dans un cluster local.
- Observation de `~/.kube/config` et compréhension du lien entre `kubectl` et le cluster.
- Première interaction concrète avec un Pod exécuté sur Kubernetes.

---

> 🎓 **Préparation TD2 :** Vous convertirez le fichier `docker-compose.yml` du même projet en manifestes Kubernetes (Pod, Service, Deployment).
