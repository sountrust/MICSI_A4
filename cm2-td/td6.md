# TD 6 — Ingress et reverse proxy

---

## Partie 1 : Introduction et activation du contrôleur Ingress

### 1. Origine du besoin

Dans les sections précédentes, une application a été déployée sur Kubernetes. Cependant, elle n’est pas accessible depuis l’extérieur sans utiliser la commande :

```bash
kubectl port-forward
```

Cette commande ouvre un tunnel temporaire vers un pod donné. Elle est suffisante pour un test ponctuel, mais inadaptée pour une utilisation durable ou la mise en production.

Kubernetes fournit un mécanisme conçu pour ce besoin : les objets **Ingress**. Un objet Ingress joue le rôle d’un point d’entrée HTTP(S) pour le cluster.

Sous-commandes utiles :

```bash
kubectl get ingress
kubectl describe ingress
kubectl create -f ingress.yaml
kubectl apply -f ingress.yaml
```

### 2. Rôle d’un proxy inverse

Un **proxy inverse** est un composant placé en amont d’un ou plusieurs serveurs afin d’étendre leurs capacités. Il est couramment utilisé pour :

- accéder à un programme interne non exposé directement ;
- répartir la charge sur plusieurs réplicas ;
- assurer le chiffrement HTTPS et la compression ;
- centraliser la sécurité (filtrage, authentification) ;
- mutualiser les accès et réduire l’usage d’adresses IP publiques.

Logiciels courants : **Apache HTTPD**, **Nginx**, **HAProxy**, **Traefik**.

Dans Kubernetes, ces outils sont masqués par une couche d’abstraction : le **contrôleur Ingress (Ingress Controller)**.

Schéma logique :

```
Client (navigateur)
   ↓
Ingress Controller (proxy inverse)
   ↓
Service Kubernetes
   ↓
Pod(s) applicatif(s)
```

### 3. Activation du contrôleur Ingress dans Minikube

Activer le module Ingress :

```bash
minikube addons enable ingress
```

Vérifier le déploiement :

```bash
kubectl get namespaces
```

Les pods du contrôleur se trouvent dans le namespace `ingress-nginx` :

```bash
kubectl -n ingress-nginx get pods -l app.kubernetes.io/name
```

**Points d’attention :**

| Élément            | Description                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| **Moteur**         | Nginx est activé par défaut, mais d’autres contrôleurs peuvent être installés. |
| **Espace de noms** | `ingress-nginx`                                                                |
| **Ports écoutés**  | 80 (HTTP), 443 (HTTPS)                                                         |
| **Accessibilité**  | Nécessite un tunnel sur macOS/Windows.                                         |

**Particularités selon l’OS :**

| Système           | Particularité                                  | Action requise                 |
| ----------------- | ---------------------------------------------- | ------------------------------ |
| **Linux**         | Le contrôleur est joignable via `minikube ip`. | Aucune action supplémentaire.  |
| **macOS/Windows** | Minikube fonctionne dans une VM.               | Lancer `sudo minikube tunnel`. |

---

## Partie 2 : Déclaration d’une règle Ingress et accès via le tunnel

### 4. Déclaration d’une règle Ingress

Exemple minimal :

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mailpit
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mailpit
                port:
                  number: 8025
```

Application :

```bash
kubectl apply -f mailpit/ingress.yaml
```

### 5. Consultation des règles Ingress

```bash
kubectl get ingress
kubectl describe ingress mailpit
```

Sortie exemple :

```
NAME      CLASS   HOSTS   ADDRESS        PORTS   AGE
mailpit   nginx   *       192.168.49.2   80      51s
```

### 6. Accès au service exposé

```bash
minikube ip
```

Exemple : `192.168.49.2`

Accès : `http://192.168.49.2`

### 7. Spécificités liées au tunnel Minikube

#### a. Principe

Sous macOS et Windows, utiliser :

```bash
sudo minikube tunnel
```

Le terminal doit rester ouvert.

#### b. Vérification du tunnel

```bash
sudo lsof -iTCP:80 -sTCP:LISTEN
sudo lsof -iTCP:443 -sTCP:LISTEN
```

#### c. Accès selon l’OS

| Système     | Accès                   | Remarque           |
| ----------- | ----------------------- | ------------------ |
| **Linux**   | `http://$(minikube ip)` | Tunnel optionnel   |
| **macOS**   | `http://127.0.0.1`      | Tunnel obligatoire |
| **Windows** | `http://127.0.0.1`      | Tunnel obligatoire |

### 9. Vérification du fonctionnement

Depuis le cluster :

```bash
kubectl run curlpod --rm -it --image=curlimages/curl --restart=Never -- curl -v http://mailpit:8025
```

Depuis le navigateur :

- Linux : `http://$(minikube ip)`
- macOS/Windows : `http://127.0.0.1`

---

## Partie 3 – Hôtes virtuels et nip.io

### 11. Hôte virtuel par défaut

Un **hôte virtuel** permet à un serveur HTTP (Apache, Nginx, IIS...) d’héberger plusieurs sites web sur une même adresse IP. Sans hôte spécifié, toutes les requêtes sont redirigées vers Mailpit.

### 12. Présentation du mécanisme nip.io

`nip.io` permet d’associer automatiquement un nom DNS à une IP locale :

- `192.168.49.2.nip.io`
- `mailpit.192.168.49.2.nip.io`

Cela contourne la nécessité d’un domaine réel.

### 13. Configuration du serveur DNS

Certaines box bloquent la résolution _rebind_ pour `127.0.0.1` ou `192.168.x.x`.
Tester :

```bash
dig +short 192.168.0.1.nip.io
```

Si aucune réponse :

1. Désactiver la protection DNS rebinding sur la box.
2. Modifier `/etc/hosts`.
3. Utiliser des DNS publics (Google : `8.8.8.8`, `8.8.4.4`).

#### Sous Ubuntu/Linux

```bash
nmcli con mod "Connexion filaire 1" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli con mod "Connexion filaire 1" ipv4.ignore-auto-dns yes
nmcli con down "Connexion filaire 1"
nmcli con up "Connexion filaire 1"
```

#### Sous macOS

```bash
networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4
dig +short 192.168.0.1.nip.io
```

#### Sous Windows / WSL2

Modifier les DNS dans les propriétés réseau ou sous WSL2 :

```bash
echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" | sudo tee /etc/resolv.conf
wsl --shutdown && wsl
```

---

## 14. Création d’un hôte virtuel pour Mailpit

| Système             | Adresse de base          | Exemple de domaine            |
| ------------------- | ------------------------ | ----------------------------- |
| **Linux**           | `$(minikube ip)`         | `mailpit.192.168.49.2.nip.io` |
| **macOS / Windows** | `127.0.0.1` (via tunnel) | `mailpit.127.0.0.1.nip.io`    |

> 💡 L’adresse correspond à celle par laquelle le contrôleur Ingress est joignable.

### Exemple de fichier `mailpit/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mailpit
spec:
  rules:
    - host: "mailpit.127.0.0.1.nip.io" # ou "mailpit.192.168.49.2.nip.io" sous Linux
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mailpit
                port:
                  number: 8025
```

Application :

```bash
kubectl apply -f mailpit/
```

### Vérification de l’accès

- **Linux :** `http://mailpit.$(minikube ip).nip.io`
- **macOS / Windows :** `http://mailpit.127.0.0.1.nip.io`

Sans hôte virtuel, la requête vers `http://127.0.0.1` ou `http://192.168.49.2` renvoie :

```html
<html>
  <head>
    <title>404 Not Found</title>
  </head>
  <body>
    <center><h1>404 Not Found</h1></center>
    <hr />
    <center>nginx</center>
  </body>
</html>
```

### Interprétation

Le mécanisme d’**hôte virtuel (VirtualHost)** est en place :

- Le contrôleur Nginx redirige selon le nom DNS utilisé.
- Permet la publication de plusieurs applications HTTP distinctes via un seul point d’entrée (ports 80/443).
