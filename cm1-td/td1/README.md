# 🧱 TD1 — Du conteneur Docker à l’orchestrateur local (MicroK8s / Minikube)

> 🌟 **Objectif :** comprendre la continuité entre Docker et Kubernetes, en déployant une image construite localement sur un mini-cluster.

Durée : 1h
Pré-requis : notions de base en Docker (images, conteneurs)
Matériel : poste personnel avec Docker Desktop ou Snap Docker + MicroK8s / Minikube

---

## 1️⃣ – Introduction et but du TD

Dans ce premier TD, vous allez :

- créer une image Docker personnalisée à partir d’un `Dockerfile`,
- l’exécuter localement pour valider son fonctionnement,
- puis la déployer sur un cluster local (Minikube ou MicroK8s).

> 💡 Vous verrez que Kubernetes orchestre les **mêmes conteneurs Docker**, mais d’une manière **déclarative et scalable**.

---

## 2️⃣ – Préparation de l’environnement

### a. Vérifiez Docker

```bash
docker --version
docker run hello-world
```

Vous devez obtenir un message confirmant l’installation.

### b. Installez un orchestrateur local

**Option 1 – MicroK8s (Linux)** :

```bash
sudo snap install microk8s --classic
sudo microk8s status --wait-ready
sudo microk8s enable dns dashboard ingress
```

**Option 2 – Minikube (Windows/macOS/Linux)** :

```bash
minikube start
kubectl get nodes
```

---

## 3️⃣ – Création d’une image Docker

Créez un dossier `td1` puis ajoutez un fichier `Dockerfile` :

```dockerfile
# Application web simple
FROM nginx:1.25-alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
```

Et un fichier `index.html` :

```html
<h1>Hello Kubernetes 👋</h1>
<p>Déployé depuis Docker vers MicroK8s</p>
```

### a. Construction de l’image

```bash
docker build -t demo-web:1.0 .
docker images
```

### b. Test local

```bash
docker run -d -p 8080:80 demo-web:1.0
curl http://localhost:8080
```

> 🧠 L’image Docker contient tout ce qu’il faut pour exécuter votre mini-application.

---

## 4️⃣ – Déploiement sur Minikube / MicroK8s

### a. Charger l’image locale dans le cluster

**Minikube :**

```bash
minikube image load demo-web:1.0
```

**MicroK8s :**

```bash
microk8s ctr images import demo-web:1.0
```

### b. Créer un manifeste `pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-web
  labels:
    app: demo-web
spec:
  containers:
    - name: web
      image: demo-web:1.0
      ports:
        - containerPort: 80
```

### c. Appliquer le manifeste

```bash
kubectl apply -f pod.yaml
kubectl get pods
```

> Si le pod est en statut **Running**, il est bien déployé sur votre cluster local.

---

## 5️⃣ – Tester l’application dans le cluster

**Option 1 – Port-forwarding (universel)** :

```bash
kubectl port-forward pod/demo-web 8080:80
```

Puis ouvrez [http://localhost:8080](http://localhost:8080)

**Option 2 – Service exposé (facultatif)** :

```bash
kubectl expose pod demo-web --port=80 --type=NodePort
kubectl get svc
```

---

## 6️⃣ – Observation et nettoyage

```bash
kubectl describe pod demo-web
kubectl logs demo-web
kubectl delete pod demo-web
```

---

## 7️⃣ – 📦 Comparaison Docker vs Kubernetes

| Action                     | Docker           | Kubernetes                     |
| -------------------------- | ---------------- | ------------------------------ |
| Lancer un conteneur        | `docker run`     | `kubectl apply -f pod.yaml`    |
| Exposer un port            | `-p 8080:80`     | `Service` ou `port-forward`    |
| Supprimer                  | `docker rm`      | `kubectl delete`               |
| Gérer plusieurs conteneurs | `docker compose` | `Deployment`                   |
| État de l’application      | Non conservé     | **Déclaratif (state desired)** |

---

## 8️⃣ – Versionner avec Git

### a. Initialisez votre dépôt local

```bash
git init
git add .
git commit -m "TD1 - image Docker + Pod Kubernetes"
```

### b. Rattachez votre dépôt distant

```bash
git remote add origin https://gitlab.com/votre-organisation/cm1-tds.git
git push -u origin main
```

> 💡 Le dépôt Git devient votre **support de soumission** : code + manifestes + notes.

---

## 🧭 À la fin du TD

Vous devez être capable de :

- construire et tester une image Docker,
- la charger dans Minikube ou MicroK8s,
- la déployer sous forme de Pod,
- comprendre que Kubernetes orchestre vos images, pas autre chose.

---

### ✅ Travail à rendre (sur Git ou Moodle)

- Le `Dockerfile`
- Le `index.html`
- Le `pod.yaml`
- Une capture d’écran du pod **Running**
- Une courte phrase :

  > “En une phrase : que fait Kubernetes de plus que Docker ici ?”
