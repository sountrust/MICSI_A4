# CM3 – Gestion de la durabilité et de l’état dans Kubernetes

## Bloc 1 enrichi — Du déploiement éphémère à la supervision du cluster

---

## 1. Contexte général : du déploiement éphémère à la production

Dans Kubernetes, **les conteneurs sont par définition éphémères** : ils peuvent être détruits et recréés à tout moment selon les besoins du cluster.
Cette caractéristique garantit la résilience, mais impose de comprendre **comment l’état et la durabilité sont gérés**.

> **Objectif du CM3** : comprendre comment Kubernetes maintient la stabilité, la santé et la persistance des applications, malgré la nature éphémère des conteneurs.

Ce cours aborde :

- la **réaction du cluster aux crashs** ;
- la **surveillance des applications** (readiness, liveness) ;
- la **gestion des ressources et de la persistance** ;
- et la **supervision du cluster lui-même**.

---

## 2. Gestion des crashs et de l’état des pods

### 2.1 Cycle de vie d’un Pod

Un **Pod** encapsule un ou plusieurs conteneurs partageant le même réseau et stockage. Il traverse plusieurs états :

| État                 | Description                                                           |
| -------------------- | --------------------------------------------------------------------- |
| **Pending**          | Le pod a été accepté mais ses conteneurs ne sont pas encore démarrés. |
| **Running**          | Tous les conteneurs sont lancés et fonctionnent.                      |
| **Succeeded**        | Tous les conteneurs se sont terminés sans erreur.                     |
| **Failed**           | Au moins un conteneur s’est arrêté avec une erreur.                   |
| **CrashLoopBackOff** | Le conteneur échoue et redémarre en boucle.                           |

#### Commandes utiles

```bash
kubectl get pods -w
kubectl describe pod <nom>
kubectl logs <nom>
```

Exemple :

```bash
NAME           READY   STATUS             RESTARTS   AGE
mailpit-7d89   1/1     Running            0          5m
api-5f86d4c    0/1     CrashLoopBackOff   3          2m
```

### 2.2 Comportement en cas de crash

Lorsqu’un conteneur échoue :

1. Le **kubelet** (agent de nœud) détecte l’échec.
2. Il consulte la **politique de redémarrage** :

   ```yaml
   restartPolicy: Always
   ```

3. Il relance automatiquement le conteneur.

Ce mécanisme assure une **auto-guérison basique** du cluster.

### 2.3 Rôle du runtime (Containerd)

Le kubelet s’appuie sur le **container runtime** (souvent _Containerd_ ou _CRI-O_) pour :

- créer et exécuter les conteneurs ;
- gérer les systèmes de fichiers et réseaux ;
- superviser leur état.

Sous Minikube :

```bash
minikube ssh
sudo ctr containers list
```

> Le conteneur peut subsister temporairement même après la suppression du pod Kubernetes.

### 2.4 CrashLoopBackOff

Cet état indique que Kubernetes tente périodiquement de redémarrer un conteneur en échec, avec une **désactivation exponentielle** des tentatives.

```bash
Warning  BackOff  kubelet  Back-off restarting failed container
```

### 2.5 Nettoyage et persistance

- Les fichiers dans le conteneur (ex: `/tmp/data`) sont **perdus** à la suppression.
- Seules les données montées sur un **volume persistant** (PersistentVolume) survivent.

> 💡 _Nous verrons dans la suite comment rendre ces données persistantes._

---

## 2 bis. Santé du cluster et supervision des pods systèmes

### 2.6 Namespace `kube-system`

Ce namespace contient les **pods essentiels** au fonctionnement du cluster.
Ils assurent les fonctions de réseau, de planification, de contrôle et de stockage.

```bash
kubectl get pods -n kube-system
```

Exemples : CoreDNS, etcd, kube-apiserver, kube-scheduler, kubelet, etc.

### 2.7 Services vitaux du cluster

| Composant                      | Rôle principal                                                          |
| ------------------------------ | ----------------------------------------------------------------------- |
| **CoreDNS**                    | Résolution interne de noms entre pods et services.                      |
| **etcd**                       | Base de données clé-valeur stockant l’état du cluster.                  |
| **kube-apiserver**             | API du plan de contrôle : interface et cohérence des données dans etcd. |
| **kube-scheduler**             | Affectation des pods aux nœuds disponibles.                             |
| **controller-manager**         | Application des boucles de réconciliation.                              |
| **kube-proxy**                 | Routage du trafic entre services et pods.                               |
| **kindnet / calico / flannel** | Gestion du réseau inter-pods.                                           |
| **minikube addons manager**    | Gestion des extensions locales.                                         |
| **kubelet**                    | Agent exécutant les conteneurs sur chaque nœud.                         |

Observation :

```bash
kubectl logs <pod> -n kube-system
```

### 2.8 Configuration du plan de contrôle

Les pods systèmes des nœuds maîtres sont définis dans `/etc/kubernetes/manifests`.
Chaque fichier correspond à un composant vital (API server, controller, scheduler...).

Exemple :

```bash
minikube ssh
ls /etc/kubernetes/manifests
cat kube-apiserver.yaml
```

- Si un fichier manifest est supprimé → le pod disparaît.
- Si le fichier est restauré → le pod est recréé automatiquement.

> ⚙️ **Le kubelet gère ces pods statiques localement**, indépendamment de l’API server.

### 2.9 Monitoring du cluster avec un DaemonSet (ex: Glances)

#### Origine du besoin

Kubernetes expose des métriques applicatives, mais il est souvent nécessaire de surveiller aussi les **ressources système** de chaque nœud.

#### Le DaemonSet

Un **DaemonSet** déploie un pod sur chaque nœud du cluster.

Exemple : déploiement de Glances pour superviser les performances locales.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: glances
spec:
  selector:
    matchLabels:
      app: glances
  template:
    metadata:
      labels:
        app: glances
    spec:
      containers:
        - name: glances
          image: nicolargo/glances:latest
          ports:
            - containerPort: 61208
          volumeMounts:
            - mountPath: /var/run/docker.sock
              name: docker-sock
      volumes:
        - name: docker-sock
          hostPath:
            path: /var/run/docker.sock
```

#### Contrôle du déploiement

```bash
kubectl get daemonsets
kubectl get pods -l app=glances -o wide
```

#### Tolérances et taints

Pour exécuter Glances sur les nœuds maîtres : ajouter des **tolerations**.

---

### Synthèse du bloc 1

- Les pods sont éphémères mais Kubernetes assure leur **auto-récupération**.
- Le **kubelet** et **Containerd** pilotent le cycle de vie des conteneurs.
- Le namespace `kube-system` contient les **services vitaux** du cluster.
- Les **manifests statiques** permettent de maintenir le plan de contrôle.
- Les **DaemonSets** servent à déployer des agents de monitoring (ex : Glances) sur chaque nœud.

---

## Bloc 2 — Surveillance et gestion des ressources

---

## 3. Surveillance de l’application : readiness et liveness probes

### 3.1 Pourquoi surveiller ?

Un pod peut être **en cours d’exécution** sans être **fonctionnel**.
Les probes (ou sondes) permettent à Kubernetes de **tester automatiquement la santé** et la disponibilité des conteneurs.

Kubernetes définit **trois types de sondes fonctionnelles**, chacune ayant un rôle spécifique :

| Type de sonde       | Objectif principal                                       | Comportement                                                        |
| ------------------- | -------------------------------------------------------- | ------------------------------------------------------------------- |
| **Liveness Probe**  | Vérifie si le conteneur est _toujours vivant_.           | Redémarre le conteneur s’il échoue.                                 |
| **Readiness Probe** | Vérifie si le conteneur est _prêt à recevoir du trafic_. | Retire le pod du Service jusqu’à rétablissement.                    |
| **Startup Probe**   | Vérifie si le conteneur _a fini de démarrer_.            | Donne plus de temps au démarrage avant d’activer les autres sondes. |

---

### 💡 À propos des chemins `/healthz` et `/ready`

Dans Kubernetes (et dans de nombreux frameworks modernes), les applications exposent souvent des **points d’entrée de supervision** :

| Endpoint                         | Usage courant | Description                                                       |
| -------------------------------- | ------------- | ----------------------------------------------------------------- |
| **`/healthz`**                   | Liveness      | Vérifie que l’application répond encore — elle n’est pas bloquée. |
| **`/ready`** ou **`/readiness`** | Readiness     | Vérifie que l’application est prête à recevoir des requêtes.      |
| **`/metrics`**                   | Monitoring    | Sert à exporter des métriques vers Prometheus ou d’autres outils. |

> Ces endpoints sont libres mais ont été **standardisés par convention** : Kubernetes n’impose pas leur nom, mais beaucoup d’outils et frameworks les reconnaissent.

---

### 3.2 Méthodes techniques de probes

Chaque type de sonde (liveness, readiness, startup) peut utiliser l’une des méthodes suivantes pour effectuer son test :

| Méthode technique | Description                                            | Exemple              |
| ----------------- | ------------------------------------------------------ | -------------------- |
| **HTTP GET**      | Vérifie la réponse d’un endpoint HTTP.                 | `/healthz`, `/ready` |
| **TCP Socket**    | Vérifie qu’un port réseau est accessible.              | port 8080            |
| **Exec Command**  | Exécute une commande locale et vérifie le code retour. | `ps aux`             |

Exemple de déclaration dans un manifest :

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5

readinessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

### 3.3 Bonnes pratiques

- Toujours prévoir un **délai initial** (`initialDelaySeconds`) pour laisser l’application démarrer.
- Adapter la fréquence de test (`periodSeconds`) à la durée moyenne de réponse.
- Définir des seuils de tolérance (`failureThreshold`, `successThreshold`).
- Aligner les endpoints de test avec la logique applicative réelle.

> ⚠️ Évitez les tests superflus : une sonde trop agressive peut redémarrer inutilement un conteneur.

---

### 3.4 Exemple : application Flask

Une application Flask expose souvent un endpoint `/healthz` ou `/ping` pour les probes :

```python
from flask import Flask
app = Flask(__name__)

@app.route('/healthz')
def health():
    return 'OK', 200
```

La déclaration de pod :

```yaml
containers:
  - name: web
    image: myapp:latest
    ports:
      - containerPort: 5000
    livenessProbe:
      httpGet:
        path: /healthz
        port: 5000
      initialDelaySeconds: 5
      periodSeconds: 5
```

Résultat : si Flask cesse de répondre, Kubernetes redémarre automatiquement le conteneur.

---

## 4. Gestion des ressources : CPU et mémoire

### 4.1 Pourquoi limiter les ressources ?

Kubernetes mutualise les ressources entre plusieurs pods sur un même nœud.
Définir des **limites** et **demandes** permet :

- d’assurer une **équité de répartition**,
- d’éviter qu’un pod monopolise le CPU ou la RAM,
- d’améliorer la planification et la stabilité du cluster.

---

### 4.2 Déclaration des ressources

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

- `requests` : quantité garantie pour le conteneur.
- `limits` : plafond maximal autorisé.

> 🧮 1 CPU = 1000m (millicores). Une limite de `500m` correspond à 50 % d’un cœur.

---

### 4.3 Effets des dépassements

- Si la **mémoire dépasse** la limite → le conteneur est tué (_OOMKill_).
- Si la **CPU dépasse** la limite → le conteneur est ralenti, mais pas tué.

Cas observables :

```bash
kubectl describe pod <nom>
# Chercher les événements 'OOMKilled' ou 'Throttling CPU'
```

---

### 4.4 Réservation et surallocation

Kubernetes permet une **surallocation contrôlée** : plusieurs pods peuvent demander plus que la capacité totale du nœud, mais seuls les plus prioritaires seront servis selon la charge.

C’est le rôle du **scheduler**, qui arbitre les ressources disponibles.

---

### 4.5 Priorités des pods

Kubernetes introduit des **PriorityClasses** pour définir l’ordre de traitement lors d’une saturation :

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000
preemptionPolicy: PreemptLowerPriority
```

Déclaration dans un pod :

```yaml
spec:
  priorityClassName: high-priority
```

> 🔹 Si les ressources manquent, un pod de haute priorité peut **préempter** un autre de priorité inférieure.

---

### Synthèse du bloc 2

- Les **probes** garantissent la santé et la disponibilité des pods.
- Les **liveness**, **readiness** et **startup** tests contrôlent respectivement la vitalité, la disponibilité et le démarrage.
- Les **requests** et **limits** gèrent la consommation de ressources.
- Les **PriorityClasses** assurent la continuité des services essentiels.

> 💡 Ces notions combinées permettent à Kubernetes d’assurer la **qualité de service (QoS)** et la **résilience applicative** du cluster.

---

## Bloc 3 — Persistance des données et StatefulSets (version finale consolidée)

---

## 5. Persistance des données

### 5.1 Pourquoi la persistance est-elle nécessaire ?

Les pods Kubernetes sont **éphémères** : lors d’un redémarrage, leur système de fichiers est reconstruit à partir de l’image du conteneur. Toute donnée stockée en local est donc **perdue**.

Pour les applications manipulant des données (bases de données, services de messagerie, journaux, etc.), il faut un moyen de **préserver ces informations entre les cycles de vie des pods**.
Kubernetes propose pour cela un modèle de **volumes persistants** qui découple la durée de vie du stockage de celle des pods.

---

## 5.2 Création manuelle : PV + PVC liés statiquement

### a. Étape 1 — Définir un PersistentVolume (PV)

Un **PersistentVolume** représente une ressource de stockage **physique ou logique** disponible dans le cluster.
Il peut correspondre à un disque local, un partage NFS, un périphérique iSCSI, etc.

Exemple :

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-demo
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/demo
```

Ce volume est stocké localement sur le nœud dans le répertoire `/data/demo`.

---

### b. Étape 2 — Créer un PersistentVolumeClaim (PVC)

Un **PersistentVolumeClaim** est la **demande d’un pod** pour un volume persistant.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Lorsque le PVC est créé :

- Kubernetes recherche un PV compatible (taille, mode d’accès, disponibilité) ;
- s’il en trouve un, il le **lie automatiquement** (`Bound`).

Vérification :

```bash
kubectl get pv,pvc
```

---

### c. Étape 3 — Utiliser le PVC dans un Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
spec:
  containers:
    - name: demo
      image: busybox
      command: ["sleep", "3600"]
      volumeMounts:
        - mountPath: /mnt/data
          name: demo-volume
  volumes:
    - name: demo-volume
      persistentVolumeClaim:
        claimName: pvc-demo
```

Le pod aura accès au répertoire `/data/demo` du nœud sous `/mnt/data` dans le conteneur.

---

## 5.3 Du modèle statique au modèle dynamique (StorageClass)

La méthode précédente exige de **créer manuellement chaque PV** avant de pouvoir le réclamer via un PVC.
C’est lourd à maintenir et inadapté aux environnements dynamiques (multi-nœuds, cloud, etc.).

Pour pallier cela, Kubernetes introduit les **StorageClasses**, qui permettent le **provisionnement automatique** de volumes persistants.

### a. StorageClass : principe

Une **StorageClass** définit _comment_ Kubernetes crée un volume :

- quel **provisioner** utiliser (ex. driver CSI, hostPath, EBS, Ceph, NFS, etc.) ;
- quelle **politique de réclamation** appliquer ;
- quel **moment** choisir pour l’allocation (immédiate ou différée).

Exemple :

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: k8s.io/minikube-hostpath
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

---

### b. PVC dynamique

Lorsqu’un PVC fait référence à une StorageClass, Kubernetes **crée automatiquement un PV** adapté à la demande :

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-dyn
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  storageClassName: standard
```

À la création du PVC :

- un nouveau PV est généré automatiquement par le provisioner spécifié ;
- le PVC et le PV sont liés (`Bound`).

Aucune définition de PV n’est requise manuellement.

Vérification :

```bash
kubectl get pv,pvc
```

> 💡 L’administrateur ne déclare plus de volumes à l’avance : Kubernetes provisionne à la volée via la StorageClass.

---

### ⚠️ Limite importante du provisionnement dynamique

> Le provisionnement dynamique **ne garantit pas la portabilité du stockage** entre les nœuds.
>
> - Si la StorageClass repose sur un **stockage en réseau** (NFS, CephFS, Longhorn, OpenEBS, CSI Cloud, etc.), le volume est accessible depuis n’importe quel nœud.
> - Si elle repose sur un **disque local** (`hostPath`, `local`), le PV reste attaché à un seul nœud. Kubernetes doit planifier le pod sur ce même nœud pour qu’il puisse accéder à ses données.
>   Ce comportement est géré via `WaitForFirstConsumer` et `nodeAffinity`.
>
> 👉 En résumé : le modèle dynamique est efficace lorsqu’un **backend réseau** rend les volumes accessibles à tous les nœuds du cluster.

---

### c. Comparatif entre volumes statiques et dynamiques

| Aspect             | PV/PVC statiques                  | StorageClass dynamique           |
| ------------------ | --------------------------------- | -------------------------------- |
| Création du volume | Manuelle (PV défini avant le PVC) | Automatique par Kubernetes       |
| Liens PV–PVC       | Correspondance obligatoire        | Gérés par le provisioner         |
| Portabilité        | Limitée (souvent locale)          | Optimale avec stockage réseau    |
| Cas d’usage        | Démonstration, disque local       | Clusters multi-nœuds, cloud, CSI |

---

## 5.4 Modes d’accès, sécurité et typologie des stockages

### a. Modes d’accès disponibles

| Mode                        | Signification                         | Cas d’usage                    |
| --------------------------- | ------------------------------------- | ------------------------------ |
| **ReadWriteOnce (RWO)**     | Lecture/écriture par un seul nœud.    | Disque local, base de données. |
| **ReadOnlyMany (ROX)**      | Lecture seule depuis plusieurs nœuds. | Fichiers statiques, images.    |
| **ReadWriteMany (RWX)**     | Lecture/écriture par plusieurs nœuds. | NFS, CephFS, GlusterFS.        |
| **ReadWriteOncePod (RWOP)** | Accès exclusif par un seul pod.       | Sécurité renforcée.            |

### b. Sécurité et permissions

L’accès en écriture dépend des droits POSIX sur le volume monté.
Il est possible de spécifier un **securityContext** :

```yaml
securityContext:
  runAsUser: 1000
  fsGroup: 1000
```

Ainsi, le système de fichiers applique les permissions correspondant à l’utilisateur du conteneur.

### c. Types de backend

| Type                 | Description                          | Particularités                                          |
| -------------------- | ------------------------------------ | ------------------------------------------------------- |
| **hostPath / local** | Stockage local du nœud.              | Rapide, mais non partagé.                               |
| **NFS**              | Partage réseau simple.               | Compatible RWX, facile à configurer.                    |
| **CSI Driver**       | Interface standard pour le stockage. | Supporte de nombreux backends (Ceph, EBS, Azure, etc.). |
| **CephFS / RBD**     | Stockage distribué en réseau.        | Haute disponibilité, compatible VM.                     |
| **Cloud storage**    | EBS (AWS), Persistent Disk (GCP)...  | Provisionnement dynamique complet.                      |

---

## 6. StatefulSets et bases de données

### 6.1 Limites des Deployments

Les **Deployments** conviennent aux applications _stateless_.
Pour les bases de données, caches et services nécessitant une identité stable, on utilise un **StatefulSet**.

> ⚠️ Kubernetes ne gère pas la cohérence applicative : la réplication, la concurrence en écriture et la synchronisation sont du ressort du moteur de base de données.

---

### 6.2 Caractéristiques d’un StatefulSet

| Fonction        | Description                                                    |
| --------------- | -------------------------------------------------------------- |
| Identité stable | Les pods sont nommés séquentiellement (`app-0`, `app-1`, ...). |
| Volume dédié    | Chaque pod possède son propre PVC.                             |
| Ordre contrôlé  | Création et suppression ordonnées.                             |
| Stabilité       | Chaque pod conserve son nom et son volume après redémarrage.   |

---

### 6.3 Exemple : MariaDB avec StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mariadb
spec:
  selector:
    matchLabels:
      app: mariadb
  serviceName: mariadb
  replicas: 1
  template:
    metadata:
      labels:
        app: mariadb
    spec:
      containers:
        - name: mariadb
          image: mariadb:10.11
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mariadb-secret
                  key: root-password
          ports:
            - containerPort: 3306
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 2Gi
```

#### Points clés :

- `volumeClaimTemplates` crée un **PVC par pod** (`data-mariadb-0`, `data-mariadb-1`, ...).
- Si `replicas > 1`, chaque instance est indépendante sauf configuration de réplication.
- Pour la cohérence :
  - utiliser une réplication interne (ex : **MariaDB Galera**, **MySQL Group Replication**) ;
  - exposer les pods via un **Service Headless** (`clusterIP: None`) ;
  - gérer les transactions côté SGBD.

---

### 6.4 Vérification et gestion

```bash
kubectl get statefulsets
kubectl get pods -l app=mariadb
kubectl get pvc | grep mariadb
```

Chaque pod possède son volume personnel.
Le redimensionnement :

```bash
kubectl scale statefulset mariadb --replicas=3
```

> Kubernetes orchestre les pods et volumes, **pas la logique transactionnelle**.

---

### 6.5 ConfigMaps et Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mariadb-secret
type: Opaque
data:
  root-password: bXlzZWNyZXRwYXNzCg== # base64("mysecretpass")
```

Les **Secrets** et **ConfigMaps** permettent de stocker la configuration et les mots de passe de manière sécurisée.
Ils sont _namespaced_ et non persistants, mais liés au cycle de vie du déploiement.

---

### 🧠 Synthèse du bloc 3

- Les **PV/PVC** assurent la persistance des données.
- Les **StorageClasses** permettent un **provisionnement dynamique** des volumes.
- Cette automatisation n’est pertinente que si le **stockage est en réseau** et accessible à tous les nœuds.
- Les **modes d’accès**, **droits**, et **types de backend** déterminent la souplesse du stockage.
- Les **StatefulSets** gèrent la stabilité des applications avec état, mais la **cohérence des données** relève des moteurs applicatifs.

> 💡 Kubernetes ne se limite pas à redémarrer des conteneurs : il orchestre la **durabilité**, la **stabilité** et la **persistance** des applications au sein d’environnements distribués.

---
