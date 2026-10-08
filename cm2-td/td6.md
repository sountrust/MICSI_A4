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

Les règles de routage sont décrites dans des ressources YAML, indépendamment du moteur utilisé. Dans ce TD, le contrôleur fourni par l’addon Minikube est basé sur Nginx.

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

Exemple de sortie :

```text
NAME                                       READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-kvlb4         0/1     Completed   0          3m49s
ingress-nginx-admission-patch-pm5vt          0/1     Completed   1          3m49s
ingress-nginx-controller-85457b87bd-xnkgn    1/1     Running     0          3m49s
```

Le pod `ingress-nginx-controller-*` effectue les fonctions de proxy inverse. Les pods `admission-*` assurent la préparation des certificats et des règles d’admission ; leur état `Completed` est normal une fois leur tâche terminée.

**Points d’attention :**

| Élément            | Description                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| **Moteur**         | Nginx est activé par défaut, mais d’autres contrôleurs peuvent être installés. |
| **Espace de noms** | `ingress-nginx`                                                                |
| **Ports écoutés**  | 80 (HTTP), 443 (HTTPS)                                                         |
| **Accessibilité**  | Avec Docker Desktop sur macOS/Windows, l’accès local nécessite un tunnel.     |

**Particularités selon l’OS :**

| Système           | Particularité                                  | Action requise                 |
| ----------------- | ---------------------------------------------- | ------------------------------ |
| **Linux**         | Accès via `minikube ip`, selon le pilote utilisé. | Tunnel généralement facultatif. |
| **macOS / Windows avec Docker Desktop** | Le cluster fonctionne dans un environnement virtualisé. | Utiliser le tunnel décrit en partie 2. |

---

## Partie 2 : Déclaration d’une règle Ingress et accès via le tunnel

### 4. Déclaration d’une règle Ingress

La ressource comprend un en-tête (`apiVersion`, `kind`), des informations d’identification (`metadata`) et les règles de routage (`spec`). Enregistrer cet exemple dans `mailpit/ingress.yaml` :

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

L’étoile dans la colonne `HOSTS` indique que cette règle ne filtre pas sur un nom d’hôte : les requêtes correspondant au chemin `/` sont dirigées vers le service `mailpit`.

### 6. Accès au service exposé

```bash
minikube ip
```

Exemple : `192.168.49.2`

Accès : `http://192.168.49.2`, si l’adresse du nœud est joignable depuis la machine hôte. Avec Docker Desktop sur macOS/Windows, utiliser le tunnel présenté ci-dessous.

### 7. Spécificités liées au tunnel Minikube

#### a. Principe

Sur macOS et Windows avec Docker Desktop, les points d’entrée du cluster ne sont pas directement accessibles depuis la machine hôte. Le tunnel permet d’exposer localement les ports HTTP (80) et HTTPS (443).

Sous Linux, le besoin d’un tunnel dépend du pilote Minikube utilisé (`docker`, `kvm2`, `none`, etc.).

#### b. Commande à exécuter

Sous macOS ou dans l’environnement WSL utilisé pour ce TD :

```bash
sudo minikube tunnel
```

Sous Windows PowerShell ou CMD, ouvrir le terminal **en administrateur** et exécuter la commande sans `sudo` :

```powershell
minikube tunnel
```

Le terminal doit rester ouvert tant que l’accès au cluster est nécessaire. La sortie du tunnel doit annoncer son démarrage et l’exposition du service/Ingress `mailpit`.

#### c. Vérification du tunnel

Sous macOS/Linux, vérifier l’écoute sur les ports 80 et 443 :

```bash
sudo lsof -iTCP:80 -sTCP:LISTEN
sudo lsof -iTCP:443 -sTCP:LISTEN
```

Si aucun processus n’écoute, vérifier les messages du tunnel et le relancer avec les privilèges nécessaires.

### 8. Accès selon le système d’exploitation

| Système     | Accès                   | Remarque           |
| ----------- | ----------------------- | ------------------ |
| **Linux**   | IP renvoyée par `minikube ip`, par exemple `http://192.168.49.2` | Selon le pilote, tunnel facultatif |
| **macOS avec Docker Desktop** | `http://127.0.0.1` | Tunnel actif |
| **Windows avec Docker Desktop** | `http://127.0.0.1` | Tunnel actif avec droits administrateur |

### 9. Vérification du fonctionnement

#### a. Depuis le cluster

Vérifier que le service Mailpit répond à l’intérieur du cluster :

```bash
kubectl run curlpod --rm -it --image=curlimages/curl --restart=Never -- curl -v http://mailpit:8025
```

La réponse attendue contient `HTTP/1.1 200 OK` et le HTML de Mailpit. Ce test vérifie l’accès au service ; l’accès via l’Ingress est vérifié ensuite depuis le navigateur.

#### b. Depuis le navigateur

- Linux : ouvrir l’adresse renvoyée par `minikube ip`, précédée de `http://`.
- macOS/Windows avec Docker Desktop : ouvrir `http://127.0.0.1` avec le tunnel actif.

L’interface de Mailpit doit s’afficher.

### 10. Diagnostic en cas d’échec

Vérifier successivement les points suivants.

#### a. État du contrôleur Ingress

```bash
kubectl get pods -n ingress-nginx
```

Le pod du contrôleur doit être `Running` et prêt (`READY` à `1/1`). Les pods des tâches `admission-*` peuvent être `Completed`.

#### b. État du tunnel

Sous macOS/Linux :

```bash
sudo lsof -iTCP:80 -sTCP:LISTEN
sudo lsof -iTCP:443 -sTCP:LISTEN
```

Si le tunnel est nécessaire mais n’écoute pas, le relancer comme indiqué à la section 7. Sous Windows PowerShell/CMD, vérifier les messages dans le terminal administrateur où tourne `minikube tunnel`.

#### c. Journaux du contrôleur

```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=50
```

#### d. Passage automatique en HTTPS

Certains navigateurs tentent d’utiliser HTTPS automatiquement. En cas de refus de connexion, vérifier le protocole de l’URL et l’écoute sur le port correspondant. Les exemples de ce TD utilisent HTTP ; aucune configuration TLS applicative n’est définie ici.

---

## Partie 3 – Hôtes virtuels et nip.io

### 11. Hôte virtuel et nip.io

#### a. Hôte virtuel par défaut

Un **hôte virtuel** permet à un serveur HTTP (Apache, Nginx, IIS...) d’héberger plusieurs sites web sur une même adresse IP. Sans hôte spécifié, toutes les requêtes sont redirigées vers Mailpit.

Le proxy utilise notamment le nom d’hôte de la requête pour sélectionner l’application. Une règle sans hôte convient pour une seule application, mais ne permet pas de distinguer plusieurs sites par leur nom.

#### b. Présentation du mécanisme nip.io

Le champ `spec.rules.host` d’un Ingress attend un nom DNS, et non une adresse IP seule. Une adresse IP utilisée directement dans ce champ entraîne une erreur de validation.

`nip.io` permet d’associer automatiquement un nom DNS à une IP locale :

- `192.168.49.2.nip.io`
- `mailpit.192.168.49.2.nip.io`

Le service `nip.io` extrait l’IP contenue dans le nom et la renvoie lors de la résolution DNS. Cela permet de créer plusieurs noms pointant vers la même machine sans gérer son propre domaine.

### 12. Configuration du serveur DNS

Certaines box bloquent la résolution _rebind_ pour `127.0.0.1` ou `192.168.x.x`.
Tester :

```bash
dig +short 192.168.0.1.nip.io
```

Le résultat attendu est `192.168.0.1`. En l’absence de réponse, la protection contre le DNS rebinding peut être en cause. Les solutions proposées sont :

1. Désactiver la protection DNS rebinding sur la box.
2. Modifier `/etc/hosts`.
3. Utiliser des DNS publics (Google : `8.8.8.8`, `8.8.4.4`).

#### a. Sous Ubuntu/Linux

Lister les connexions disponibles :

```bash
nmcli connection show
```

Remplacer `Connexion filaire 1` par le nom de la connexion à configurer, puis modifier les DNS et redémarrer la connexion :

```bash
nmcli con mod "Connexion filaire 1" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli con mod "Connexion filaire 1" ipv4.ignore-auto-dns yes
nmcli con down "Connexion filaire 1"
nmcli con up "Connexion filaire 1"
dig +short 192.168.0.1.nip.io
```

#### b. Sous macOS

Configurer les DNS dans les réglages réseau de macOS, ou utiliser la commande suivante. Remplacer `Wi-Fi` par le nom du service réseau si nécessaire :

```bash
networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4
dig +short 192.168.0.1.nip.io
```

#### c. Sous Windows / WSL2

Dans les propriétés de la carte réseau Windows, ouvrir les propriétés **IPv4**, sélectionner la configuration manuelle des serveurs DNS et saisir :

- DNS préféré : `8.8.8.8` ;
- DNS auxiliaire : `8.8.4.4`.

Pour la variante WSL2 décrite dans ce TD, si la résolution échoue, éditer `/etc/resolv.conf` dans WSL2 pour y renseigner :

```text
nameserver 8.8.8.8
nameserver 8.8.4.4
```

Depuis **PowerShell ou CMD**, arrêter puis relancer WSL :

```powershell
wsl --shutdown
wsl
```

Dans WSL, vérifier à nouveau la résolution :

```bash
dig +short 192.168.0.1.nip.io
```

Le résultat attendu est `192.168.0.1`.

---

### 13. Création d’un hôte virtuel pour Mailpit

Modifier `mailpit/ingress.yaml` pour ajouter le champ `host` sous `spec.rules`. Choisir un nom contenant l’adresse par laquelle le contrôleur est accessible :

| Système             | Adresse de base          | Exemple de domaine            |
| ------------------- | ------------------------ | ----------------------------- |
| **Linux**           | `$(minikube ip)`         | `mailpit.192.168.49.2.nip.io` |
| **macOS / Windows avec Docker Desktop** | `127.0.0.1` (via tunnel) | `mailpit.127.0.0.1.nip.io` |

> 💡 L’adresse correspond à celle par laquelle le contrôleur Ingress est joignable.

#### a. Exemple de fichier `mailpit/ingress.yaml`

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

#### b. Vérification de l’accès

- **Linux :** remplacer l’IP par celle obtenue avec `minikube ip`, par exemple `http://mailpit.192.168.49.2.nip.io`.
- **macOS / Windows avec Docker Desktop :** `http://mailpit.127.0.0.1.nip.io`, avec le tunnel actif.

Après l’ajout du champ `host`, une requête vers l’adresse IP seule (`http://127.0.0.1` ou `http://192.168.49.2`) ne correspond plus au nom configuré. En l’absence d’une autre règle correspondante, elle renvoie :

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

#### c. Interprétation

Le mécanisme d’**hôte virtuel (VirtualHost)** est en place :

- Le contrôleur Nginx redirige selon le nom DNS utilisé.
- Chaque application peut avoir sa propre règle Ingress et son nom DNS, tout en partageant le même point d’entrée HTTP (ou HTTPS si TLS est configuré).
