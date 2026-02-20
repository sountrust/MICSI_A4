# 🧭 TD2 – Du Compose à Kubernetes pas à pas

**Durée :** 2h
**Objectif :** Comprendre comment traduire une application multi-conteneurs Docker Compose vers une architecture Kubernetes, en observant chaque étape de l'orchestration.

---

## ⚙️ 1. Prérequis et vérifications

Assurez-vous que Minikube et Docker sont installés.

```bash
minikube version
docker version
```

🧪 **Vérification :** Les deux commandes doivent retourner une version valide.

---

### Démarrer Minikube

```bash
minikube start --driver=docker
```

🧪 **Vérification :**

```bash
minikube status
kubectl cluster-info
```

Vous devez voir les composants `kubelet`, `apiserver` et `kubeconfig` en **Running**.

---

## 🧱 2. Comprendre la pile (rappel)

Minikube tourne **dans Docker**, mais utilise **containerd** pour exécuter les Pods.

```
Hôte Linux
 └── Docker (driver)
       └── Conteneur Minikube
             ├── kubelet
             ├── apiserver
             └── containerd (runtime des pods)
```

> Docker sert à héberger Minikube, et Minikube exécute les conteneurs avec `containerd`.

🧪 **Vérification :**

```bash
minikube ssh
ps aux | grep containerd
exit
```

---

## 📦 3. Rappel : l'application Docker Compose

Fichier `docker-compose.yml` fourni :

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:80"
    environment:
      - DB_HOST=db
      - DB_USER=app
      - DB_PASS=example
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: example
    volumes:
      - data:/var/lib/postgresql/data
volumes:
  data:
```

> Cette application comporte un service **web** et un service **PostgreSQL** avec un volume persistant.

---

## 🧩 4. Construction et chargement des images

Construire l'image localement avec Docker :

```bash
docker build -t demo-web:1.0 .
```

🧪 **Vérification :**

```bash
docker images | grep demo-web
```

Charger l'image dans Minikube :

```bash
minikube image load demo-web:1.0
```

🧪 **Vérification :**

```bash
minikube image ls | grep demo-web
```

> L'image doit apparaître dans le registre interne du cluster.

---

## ☸️ 5. Variables d'environnement et ConfigMap / Secret

Créer une **ConfigMap** pour les variables non sensibles :

```bash
kubectl create configmap web-config \
  --from-literal=DB_HOST=db \
  --from-literal=DB_USER=app
```

Créer un **Secret** pour les informations sensibles :

```bash
kubectl create secret generic db-secret \
  --from-literal=DB_PASS=example \
  --from-literal=POSTGRES_PASSWORD=example
```

🧪 **Vérification :**

```bash
kubectl get configmaps
kubectl get secrets
```

---

## 🧱 6. Déploiement de la base de données PostgreSQL

Créer un fichier `db-deploy.yaml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: postgres
          image: postgres:15
          envFrom:
            - secretRef:
                name: db-secret
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: data
          emptyDir: {}
```

Appliquer le déploiement :

```bash
kubectl apply -f db-deploy.yaml
```

🧪 **Vérification :**

```bash
kubectl get pods
kubectl describe pod -l app=db
```

---

## 🌐 7. Service pour la base de données

Créer `db-svc.yaml` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  selector:
    app: db
  ports:
    - port: 5432
      targetPort: 5432
```

Appliquer :

```bash
kubectl apply -f db-svc.yaml
kubectl get svc
```

🧪 **Vérification :** Le service `db` doit apparaître avec un **ClusterIP** assigné.

---

## 🧱 8. Déploiement du service web

Créer `web-deploy.yaml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: demo-web:1.0
          ports:
            - containerPort: 80
          envFrom:
            - configMapRef:
                name: web-config
            - secretRef:
                name: db-secret
```

Appliquer le déploiement :

```bash
kubectl apply -f web-deploy.yaml
```

🧪 **Vérification :**

```bash
kubectl get pods -l app=web -o wide
kubectl describe pod -l app=web
```

---

## 🌍 9. Service d'exposition du web

Créer `web-svc.yaml` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 5000
      targetPort: 80
```

Appliquer :

```bash
kubectl apply -f web-svc.yaml
kubectl get svc web
```

Récupérer l'URL d'accès via Minikube :

```bash
minikube service web --url
```

🧪 **Vérification :**
Tester l'URL dans un navigateur ou via `curl`.

```bash
curl $(minikube service web --url)
```

---

## 🔍 10. Observation et résultats

Lister les ressources :

```bash
kubectl get all
```

Observer la répartition des Pods :

```bash
kubectl get pods -o wide
```

🧪 **Vérification :** Deux Pods `web` doivent répondre et un Pod `db` doit tourner.

---

## 💾 11. Versionnement et sauvegarde

```bash
git add *.yaml
git commit -m "TD2: déploiement web + db Kubernetes avec ConfigMap et Secret"
git push origin main
```

---

## 🧭 12. Installation et utilisation de Lens

Lens est un outil graphique pour observer le cluster Kubernetes.

Installation :

```bash
sudo snap install kontena-lens --classic
```

Lancer Lens, puis ajouter le cluster Minikube :

1. Ouvrir Lens.
2. Cliquer sur **Add Cluster**.
3. Importer automatiquement le contexte depuis `~/.kube/config`.
4. Ouvrir le cluster.

🧪 **Vérification :** Vous devez voir les Pods, Deployments et Services en vert.

---

## ✅ 13. Synthèse

| Élément       | Docker Compose | Kubernetes                          |
| ------------- | -------------- | ----------------------------------- |
| Services      | `services:`    | Deployments + Services              |
| Ports         | `ports:`       | `Service.spec.ports`                |
| Variables env | `environment:` | `ConfigMap` / `Secret` + `envFrom`  |
| Volumes       | `volumes:`     | `PersistentVolumeClaim` (plus tard) |

> Kubernetes gère la **déclaration d'un état** et sa **réconciliation automatique**.

🎯 Fin du TD2 : les étudiants savent déployer une application Compose en Kubernetes avec des variables d'environnement et visualiser son état avec Lens.
