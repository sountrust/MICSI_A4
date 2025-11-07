# TD 4 – Gestion par kubectl d’une application

---

## Partie 1 – Manipulation d’un déploiement et accès direct à une application via kubectl

### 1. Suppression d’un déploiement

Lors du précédent chapitre, l’application **Mailpit** a été déployée à l’aide du dashboard Kubernetes. Même si cela n’a pas été fait manuellement, il est possible de poursuivre ce TD avec les instructions suivantes.

Lister les déploiements existants :

```bash
kubectl get deployment
```

Exemple :

```
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
mailpit   1/1     1            1           8d
```

Supprimer le déploiement :

```bash
kubectl delete deployment mailpit
```

Sortie attendue :

```
deployments.apps "mailpit" deleted
```

Vérifier ensuite la liste des pods :

```bash
kubectl get pods
```

Résultat temporaire :

```
NAME                       READY   STATUS        RESTARTS   AGE
mailpit-69bd8f74cb-kl9p5   1/1     Terminating   2          8d
```

Après quelques secondes :

```
No resources found.
```

---

### 2. Création d’un déploiement

Créer un déploiement :

```bash
kubectl create deployment mailpit --image=axllent/mailpit
```

Sortie :

```
deployment.apps/mailpit created
```

---

### 3. État du déploiement

Afficher les déploiements :

```bash
kubectl get deployment
```

Exemple :

```
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
mailpit   1/1     1            1           3m
```

Pour plus de détails :

```bash
kubectl describe deployment mailpit
```

Exemple abrégé :

```
Name:                   mailpit
Namespace:              default
Labels:                 app=mailpit
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=mailpit
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
Pod Template:
  Labels:  app=mailpit
  Containers:
    mailpit:
      Image:        axllent/mailpit
      Port:         <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
NewReplicaSet:   mailpit-5bcf98ffcd (1/1 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  2m    deployment-controller  Scaled up replica set mailpit-5bcf98ffcd to 1
```

Les informations clés :

- stratégie de mise à jour (_RollingUpdate_) ;
- labels de sélection ;
- image déployée ;
- état du déploiement et événements récents.

---

### 4. Mécanisme des ReplicaSet

#### a. Consultation des ReplicaSet

Chaque déploiement gère un ou plusieurs objets **ReplicaSet**, qui maintiennent les pods associés.

```bash
kubectl get replicaset
```

Exemple :

```
NAME                 DESIRED   CURRENT   READY   AGE
mailpit-5bcf98ffcd   1         1         1       2m2s
```

#### b. Description d’un ReplicaSet

```bash
kubectl describe rs mailpit-5bcf98ffcd
```

Extrait :

```
Name:           mailpit-5bcf98ffcd
Namespace:      default
Selector:       app=mailpit,pod-template-hash=5bcf98ffcd
Labels:         app=mailpit
Controlled By:  Deployment/mailpit
Replicas:       1 current / 1 desired
Pods Status:    1 Running / 0 Waiting / 0 Failed
Containers:
  mailpit:
    Image:  axllent/mailpit
Events:
  Type    Reason            Age   From                   Message
  ----    ------            ----  ----                   -------
  Normal  SuccessfulCreate  3m11s replicaset-controller  Created pod: mailpit-5bcf98ffcd-nl4l9
```

Les **Events** répertorient les actions effectuées sur les pods et permettent le diagnostic des anomalies.

---

### 5. État du pod

#### a. Liste des pods

```bash
kubectl get pods
```

Exemple :

```
NAME                       READY   STATUS    RESTARTS   AGE
mailpit-5bcf98ffcd-nl4l9   1/1     Running   0          17s
```

Suivi en temps réel :

```bash
kubectl get pods --watch
```

Arrêt avec `Ctrl+C`.

#### b. Description d’un pod

```bash
kubectl describe pod mailpit-5bcf98ffcd-nl4l9
```

Exemple abrégé :

```
Name:         mailpit-5bcf98ffcd-nl4l9
Namespace:    default
Node:         minikube/192.168.122.67
Labels:       app=mailpit
Status:       Running
IP:           172.17.0.5
Controlled By: ReplicaSet/mailpit-5bcf98ffcd
Containers:
  mailpit:
    Image: axllent/mailpit
Events:
  Normal  Scheduled  5m37s  default-scheduler  Successfully assigned default/mailpit-5bcf98ffcd-nl4l9 to minikube
  Normal  Pulling    5m36s  kubelet            Pulling image "axllent/mailpit"
  Normal  Started    5m35s  kubelet            Started container mailpit
```

---

### 6. Accès aux logs du conteneur

```bash
kubectl logs mailpit-5bcf98ffcd-nl4l9
```

Sortie typique :

```
... level=info msg="[smtpd] starting on [::]:1025 (no encryption)"
... level=info msg="[http] starting on [::]:8025"
... level=info msg="[http] accessible via http://localhost:8025/"
```

---

### 7. Accès à l’application Mailpit

```bash
kubectl port-forward deployment/mailpit 8025
```

Accès : [http://127.0.0.1:8025](http://127.0.0.1:8025)

#### Compatibilité selon l’OS

| Système                                      | Commande                                       | Particularités                                                    |
| -------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------- |
| **Linux / macOS / Windows (Docker Desktop)** | `kubectl port-forward deployment/mailpit 8025` | Fonctionne de manière identique (port redirigé vers 127.0.0.1).   |
| **Windows avec WSL2**                        | Exécuter dans WSL2                             | Accès via `http://localhost:8025` depuis le navigateur de l’hôte. |

La commande reste active tant qu’elle tourne. Interrompre avec `Ctrl+C`. En cas de redéploiement, relancer la commande.

---

## Partie 2 – Exposition de services

### 1. Pourquoi un service ?

Un **Service** fournit un point d’accès stable pour une application. Il :

- crée un nom DNS interne ;
- redirige automatiquement vers les nouveaux pods ;
- répartit la charge entre plusieurs réplicas.

### 2. Création du service

```bash
kubectl expose deployment/mailpit --port 1025,8025
```

Sortie :

```
service/mailpit exposed
```

### 3. Vérification du service

Ouvrir un shell dans le pod :

```bash
kubectl exec -it deployment/mailpit -- sh
```

Puis :

```bash
getent hosts mailpit
```

Résultat :

```
10.107.51.181 mailpit.default.svc.cluster.local mailpit
```

### 4. En cas d’absence de shell

#### a. Pod éphémère

```bash
kubectl debug mailpit-b69794cd7-9zdpj -it --image=alpine
getent hosts mailpit
exit
```

#### b. Pod temporaire

```bash
kubectl run -it --rm test-mailpit --image=alpine sh
nslookup mailpit
exit
```

---

### 5. Résilience et scalabilité

#### a. Monter en charge

```bash
kubectl scale deployment mailpit --replicas=2
```

Vérification :

```bash
kubectl get deployment mailpit
kubectl get pods -l app=mailpit
```

#### b. Arrêt temporaire

```bash
kubectl scale deployment mailpit --replicas=0
```

Redémarrage :

```bash
kubectl scale deployment mailpit --replicas=1
```

---

### Compatibilité selon l’environnement

| Système                              | Commandes                      | Particularités                                             |
| ------------------------------------ | ------------------------------ | ---------------------------------------------------------- |
| **Linux / macOS**                    | Identiques                     | DNS du cluster géré par CoreDNS.                           |
| **Windows (Docker Desktop)**         | Identiques (PowerShell / WSL2) | Doivent être exécutées dans la même instance que Minikube. |
| **Images légères (Alpine, BusyBox)** | `nslookup`, `getent hosts`     | En cas d’absence, lancer un pod temporaire.                |
