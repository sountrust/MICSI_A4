---
marp: true
theme: default
size: 16:9
paginate: true
lang: fr
style: |
  section { font-family: Arial, sans-serif; font-size: 26px; line-height: 1.32; padding: 44px 58px; justify-content: flex-start; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  h3 { font-size: 31px; }
  h4 { font-size: 28px; }
  h1, h2, h3, h4 { color: #19364c; margin: 0 0 20px; }
  p, ul, ol, blockquote { margin: 0 0 18px; }
  li { margin: 0 0 10px; }
  pre { font-size: 21px; line-height: 1.2; margin: 8px 0 16px; }
  table { font-size: 23px; width: 100%; }
  th, td { padding: 9px 12px; }
  section::after { font-size: 17px; color: #657480; }
---

# CM4 – Persistance des données et applications avec état dans Kubernetes

Ce cours constitue la **seconde partie : conserver les données et l’identité des
applications**. Il prolonge le [CM3 — Cycle de vie, surveillance et ressources](CM3.md).

> **Objectif du CM4** : comprendre comment dissocier la durée de vie des données de celle des Pods et utiliser les StatefulSets pour les applications nécessitant une identité stable.

---

## Plan du CM4

- **1. Persistance des données** : besoin de persistance, PV/PVC statiques, provisionnement dynamique, modes d’accès, permissions et backends.
- **2. StatefulSets et bases de données** : limites des Deployments, caractéristiques des StatefulSets, exemple MariaDB, gestion des réplicas, ConfigMaps et Secrets.
- **3. CRD et Operators** : étendre l’API et automatiser la gestion d’une application.

---

## 1. Persistance des données

### 1.1 Pourquoi la persistance est-elle nécessaire ?

Les Pods Kubernetes sont **éphémères**.

Lorsqu’un conteneur est recréé, sa couche inscriptible repart de l’image et les données
qui y avaient été écrites sont perdues.

Les données montées depuis un volume suivent, elles, la durée de vie de ce volume :
`emptyDir` survit aux redémarrages de conteneurs du même Pod ; un volume persistant peut
survivre au remplacement du Pod.

---

### 1.1 Pourquoi la persistance est-elle nécessaire ? — suite

Pour les applications manipulant des données (bases de données, services de messagerie,
journaux, etc.), il faut un moyen de **préserver ces informations entre les cycles de
vie des pods**. Kubernetes propose pour cela un modèle de **volumes persistants** qui
découple la durée de vie du stockage de celle des pods.

---

## 1.2 Création manuelle : PV + PVC liés statiquement

### a. Étape 1 — Définir un PersistentVolume (PV)

Un **PersistentVolume** représente une ressource de stockage **physique ou logique**
disponible dans le cluster. Il peut correspondre à un disque local, un partage NFS, un
périphérique iSCSI, etc.

---

### a. Définir un PV — manifest

Exemple :

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-demo
spec:
  storageClassName: ""
  persistentVolumeReclaimPolicy: Retain
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/demo
    type: DirectoryOrCreate
```

---

### a. Définir un PV — portée de l’exemple

Ce volume utilise le répertoire `/data/demo` du nœud.

Cet exemple `hostPath` est destiné à une **démonstration sur un cluster mono-nœud** : il
ne garantit pas que les mêmes données seront accessibles depuis un autre nœud. `Retain`
conserve le stockage après la libération du PV et nécessite une gestion manuelle de sa
réutilisation.

---

### b. Étape 2 — Créer un PersistentVolumeClaim (PVC)

Un **PersistentVolumeClaim** est un objet représentant une **demande de stockage** dans
un namespace. Un ou plusieurs Pods de ce namespace peuvent le référencer, sous réserve
des contraintes du volume.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-demo
spec:
  storageClassName: ""
  volumeName: pv-demo
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

---

### b. Créer un PVC — liaison et vérification

Lorsque le PVC est créé :

- ici, `volumeName` désigne explicitement `pv-demo` et `storageClassName: ""` désactive l’usage de la StorageClass par défaut ;
- Kubernetes vérifie notamment la capacité, les modes d’accès, la classe et la disponibilité du PV, puis effectue la **liaison** (`Bound`) si les conditions sont satisfaites. Sans `volumeName`, il peut rechercher un PV compatible.

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

## 1.3 Du modèle statique au modèle dynamique (StorageClass)

La méthode précédente exige de **créer manuellement chaque PV** avant de pouvoir le
réclamer via un PVC. Cela peut être lourd à maintenir dans les environnements où les
demandes de stockage sont nombreuses et variables.

Le provisionnement statique reste néanmoins valable, notamment pour utiliser un stockage
existant.

Pour pallier cela, Kubernetes introduit les **StorageClasses**, qui permettent le
**provisionnement automatique** de volumes persistants.

---

### a. StorageClass : principe

Une **StorageClass** définit _comment_ Kubernetes crée un volume :

- quel **provisioner** utiliser (souvent un pilote CSI ou un provisioner externe adapté au backend) ;
- quelle **politique de récupération** (`reclaimPolicy`) appliquer : `Delete` peut supprimer le PV et le stockage sous-jacent après suppression du PVC, tandis que `Retain` les conserve pour une gestion manuelle ;
- quel **moment** choisir pour l’allocation (immédiate ou différée).

---

### a. StorageClass — exemple Minikube

Exemple propre à Minikube, qui suppose que son provisioner hostPath est activé. Une
classe `standard` peut déjà exister : la vérifier avec `kubectl get storageclass
standard -o yaml` avant toute création.

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

Lorsqu’un PVC fait référence à une StorageClass dotée d’un provisioner opérationnel et
qu’aucun PV existant compatible n’est disponible, le provisioner peut **créer
automatiquement un PV** adapté à la demande :

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

---

### b. PVC dynamique — moment de la liaison

Avec `Immediate`, le provisionnement et la liaison sont déclenchés dès la création du
PVC.

Si le backend et le provisioner satisfont la demande, le PVC passe à `Bound` ; sinon il
peut rester `Pending`.

Avec `WaitForFirstConsumer`, l’opération attend un Pod consommateur afin de prendre en
compte les contraintes de placement.

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
> - Un **backend réseau ou cloud** peut permettre l’accès depuis plusieurs nœuds ou le rattachement successif du volume à différents nœuds. Les modes d’accès, les contraintes de zone et les capacités du pilote restent à respecter.
> - Un **volume local** dépend du nœud où se trouvent les données. Un PV de type `local` déclare une `nodeAffinity` ; `WaitForFirstConsumer` permet de coordonner la liaison avec le placement du Pod. Un simple `hostPath` ne fournit pas automatiquement cette coordination.
>
> 👉 Le provisionnement dynamique est utile avec du stockage réseau **ou local**, à condition de disposer d’un provisioner adapté. L’automatisation de la création et l’accessibilité depuis les nœuds sont deux propriétés distinctes.
---

### c. Comparatif entre volumes statiques et dynamiques

| Aspect             | PV/PVC statiques                  | StorageClass dynamique           |
| ------------------ | --------------------------------- | -------------------------------- |
| Création du volume | Manuelle (PV défini avant le PVC) | Automatique par Kubernetes       |
| Liens PV–PVC | Liaison par Kubernetes entre une demande et un PV compatible | Provisionnement si nécessaire, puis liaison par Kubernetes |
| Portabilité | Dépend du backend et de sa topologie | Dépend du backend et de sa topologie |
| Cas d’usage | Stockage existant ou gestion manuelle | Automatisation de nouvelles demandes, avec provisioner adapté |

---

## 1.4 Modes d’accès, sécurité et typologie des stockages

### a. Modes d’accès disponibles

| Mode                        | Signification                         | Cas d’usage                    |
| --------------------------- | ------------------------------------- | ------------------------------ |
| **ReadWriteOnce (RWO)**     | Lecture/écriture par un seul nœud.    | Disque local, base de données. |
| **ReadOnlyMany (ROX)**      | Lecture seule depuis plusieurs nœuds. | Fichiers statiques, images.    |
| **ReadWriteMany (RWX)**     | Lecture/écriture par plusieurs nœuds. | NFS, CephFS, GlusterFS.        |
| **ReadWriteOncePod (RWOP)** | Lecture/écriture par un seul Pod dans le cluster. | Exclusivité à l’échelle du Pod ; nécessite un volume CSI et un pilote compatible. |

---

### a. Modes d’accès — portée des garanties

`ReadWriteOnce` signifie **un seul nœud**, pas un seul Pod : plusieurs Pods du même nœud
peuvent utiliser le volume si le backend le permet. Les modes disponibles dépendent du
pilote et ne remplacent pas les permissions du système de fichiers.

---

### b. Sécurité et permissions

L’accès en écriture dépend des droits POSIX sur le volume monté. Pour un volume de type
système de fichiers, il est possible de spécifier un **securityContext au niveau du
Pod** (`spec.securityContext`) :

```yaml
securityContext:
  runAsUser: 1000
  fsGroup: 1000
```

`runAsUser` fixe l’UID des processus ; `fsGroup` ajoute un groupe pour l’accès aux
volumes et peut entraîner un ajustement de leurs permissions, selon le type de volume et
le pilote CSI.

Cela ne rend pas automatiquement inscriptible tout stockage, notamment un `hostPath` :
les droits du backend doivent être compatibles.

---

### c. Types de backend

| Type                 | Description                          | Particularités                                          |
| -------------------- | ------------------------------------ | ------------------------------------------------------- |
| **hostPath / local** | Stockage local du nœud. | `hostPath` monte un chemin du nœud ; un PV `local` intègre une affinité de nœud. Les données ne sont pas partagées automatiquement. |
| **NFS**              | Partage réseau simple.               | Compatible RWX, facile à configurer.                    |
| **Pilote CSI** | Implémentation de l’interface standard CSI, plutôt qu’un backend en soi. | Connecte Kubernetes à un backend (Ceph, EBS, Azure, etc.), selon les fonctionnalités du pilote. |

---

### c. Types de backend — suite

| Type | Description | Particularités |
| --- | --- | --- |
| **CephFS / RBD** | Système de fichiers distribué / stockage bloc distribué. | CephFS et RBD ont des usages et modes d’accès différents ; la disponibilité dépend de la configuration du cluster Ceph. |
| **Stockage cloud** | EBS (AWS), Persistent Disk (GCP), etc. | Provisionnement via un pilote adapté ; contraintes d’attachement et de topologie à respecter. |

---

## 2. StatefulSets et bases de données

### 2.1 Limites des Deployments

Les **Deployments** conviennent aux applications dont les réplicas sont
interchangeables, notamment les applications _stateless_.

Ils peuvent aussi monter un PVC.

Un **StatefulSet** est adapté lorsque chaque instance doit conserver une identité stable
et, si nécessaire, un stockage qui lui est associé ; le seul fait d’utiliser une base de
données ou un cache n’impose pas ce choix.

> ⚠️ Kubernetes ne gère pas la cohérence applicative : la réplication, la concurrence en écriture et la synchronisation sont du ressort du moteur de base de données.

---

### 2.2 Caractéristiques d’un StatefulSet

| Fonction        | Description                                                    |
| --------------- | -------------------------------------------------------------- |
| Identité stable | Les pods sont nommés séquentiellement (`app-0`, `app-1`, ...). |
| Volume dédié | Avec `volumeClaimTemplates`, chaque Pod reçoit ses propres PVC. |
| Ordre contrôlé | Par défaut (`OrderedReady`), création ordonnée et réduction du nombre de réplicas en ordre inverse ; `Parallel` modifie ce comportement. |
| Stabilité | Un Pod de remplacement reprend le même nom ordinal et les PVC conservés ; son UID et son adresse IP peuvent changer. |

---

### 2.3 Exemple : MariaDB avec StatefulSet

L’exemple suppose une StorageClass par défaut capable de provisionner le stockage
demandé.

Le Secret `mariadb-secret`, présenté en section 2.5, doit être créé dans le même
namespace **avant le démarrage des conteneurs**.

Le Service headless suivant fournit l’identité réseau référencée par `serviceName` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mariadb
spec:
  clusterIP: None
  selector:
    app: mariadb
  ports:
    - name: mysql
      port: 3306
      targetPort: 3306
```

---

### 2.3 Exemple : MariaDB — StatefulSet

Le StatefulSet :

**Manifest unique — fragment 1/3.** À réunir dans cet ordre.

<!-- yaml-fragment: mariadb 1/3 -->
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
```

---

### 2.3 Exemple : MariaDB — StatefulSet (suite)

**Manifest unique — fragment 2/3.** À réunir dans cet ordre.

<!-- yaml-fragment: mariadb 2/3 -->
```yaml
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
```

---

### 2.3 Exemple : MariaDB — StatefulSet (suite)

**Manifest unique — fragment 3/3.** À réunir dans cet ordre.

<!-- yaml-fragment: mariadb 3/3 -->
```yaml
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 2Gi
```

---

### 2.3 Exemple : MariaDB — points clés

- `volumeClaimTemplates` crée un **PVC par pod** (`data-mariadb-0`, `data-mariadb-1`, ...).
- Si `replicas > 1`, chaque instance est indépendante sauf configuration de réplication.
- Pour la cohérence, configurer les mécanismes adaptés du SGBD (par exemple MariaDB Galera pour MariaDB, ou MySQL Group Replication pour MySQL) et gérer les transactions côté SGBD.
- Le **Service headless** (`clusterIP: None`) permet la découverte des instances par DNS ; il ne configure ni la réplication ni la cohérence des données.

---

### 2.4 Vérification et gestion

```bash
kubectl get statefulsets
kubectl get pods -l app=mariadb
kubectl get pvc | grep mariadb
```

Chaque pod possède son volume personnel. Augmentation du nombre de réplicas, à titre de
démonstration :

```bash
kubectl scale statefulset mariadb --replicas=3
```

> Avec ce manifest, cette commande crée trois instances indépendantes, chacune avec son stockage. Elle ne produit pas une base répliquée ni une base unique plus puissante. Kubernetes orchestre les Pods et volumes, **pas la logique transactionnelle**.

---

### 2.5 ConfigMaps et Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mariadb-secret
type: Opaque
data:
  root-password: bXlzZWNyZXRwYXNz
```

---

### 2.5 ConfigMaps et Secrets — rôle et durée de vie

Le mot de passe de l’exemple est `mysecretpass`, encodé en base64 sans saut de ligne
final.

Les **ConfigMaps** stockent de la configuration non confidentielle.

Les **Secrets** sont destinés aux données sensibles, telles que les mots de passe.
**Base64 est un encodage, pas un chiffrement** : la confidentialité dépend notamment du
contrôle d’accès et du chiffrement au repos configuré pour les Secrets.

Le mot de passe ci-dessus est un exemple pédagogique.

---

### 2.5 ConfigMaps et Secrets — durée de vie

Ces objets sont _namespaced_ et conservés dans l’état du cluster, généralement stocké
dans etcd.

Leur durée de vie est indépendante de celle des Pods et du Deployment qui les utilisent,
sauf mécanisme explicite de propriété ou de suppression.

Ils ne servent pas à stocker les données applicatives d’une base.

---

## 3. Étendre Kubernetes : CRD et Operators

### 3.1 Définir une CRD

Une **CRD** (*CustomResourceDefinition*) déclare un nouveau type de ressource dans l’API
Kubernetes.

`Deployment`, `Namespace` et `PersistentVolume` sont des types natifs. Un type ajouté
par CRD devient lui aussi accessible avec `kubectl`.

La CRD décrit le nom du type, son groupe API, ses versions, sa portée et le schéma de
ses champs.

**La définition est un objet `CustomResourceDefinition`, de portée cluster.** Les
instances peuvent être limitées à un namespace ou avoir une portée cluster, selon la
définition.

---

### 3.2 Définition, instance et contrôleur

| Élément | Rôle | Exemple pédagogique |
| --- | --- | --- |
| CRD | Définir un type et ses champs | Le type `Database` |
| Ressource personnalisée (CR) | Déclarer une instance de ce type | `Database` nommée `cours-db` |
| Contrôleur | Observer les objets et agir | Créer ou ajuster les ressources de la base |

**Une CRD seule ne lance aucun conteneur.** L’API peut accepter et stocker une instance
sans qu’un contrôleur agisse dessus.

---

### 3.3 Lire une définition — identité du type

Exemple pédagogique : `Database` n’est pas un type natif. Les deux fragments suivants
forment **un seul manifest CRD**.

<!-- yaml-fragment: database-crd 1/2 -->
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.formation.example.org
spec:
  group: formation.example.org
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
  versions:
    - name: v1alpha1
      served: true
      storage: true
```

---

### 3.3 Lire une définition — schéma (suite)

**Fragment 2/2** : à placer après le précédent, avec cette indentation.

<!-- yaml-fragment: database-crd 2/2 -->
```yaml
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [replicas]
              properties:
                replicas:
                  type: integer
                  minimum: 1
```

Le schéma contraint ici `spec.replicas` à un entier supérieur ou égal à 1. `served`
expose la version ; `storage` désigne celle utilisée pour le stockage.

---

### 3.4 Créer une ressource personnalisée

Après enregistrement de la CRD, cette instance peut être créée :

```yaml
apiVersion: formation.example.org/v1alpha1
kind: Database
metadata:
  name: cours-db
  namespace: default
spec:
  replicas: 2
```

`apiVersion` et `kind` correspondent au type déclaré par la CRD. `metadata.name`
identifie l’instance ; `spec` porte la demande.

**Cet exemple n’installe aucun contrôleur : aucune base n’est créée.**

---

### 3.5 Du contrôleur à l’Operator

Un **Operator** associe des ressources personnalisées à un ou plusieurs contrôleurs pour
automatiser la gestion d’une application.

Son contrôleur effectue une **réconciliation** :

1. Lire l’état souhaité dans la ressource personnalisée. 2. Observer les ressources et
l’état de l’application. 3. Effectuer les actions nécessaires, puis recommencer.

Pour une base, il peut gérer des StatefulSets, Services et PVC, ainsi que des
sauvegardes ou une configuration de réplication, **selon les fonctionnalités de
l’Operator choisi**.

---

### 3.5 Du contrôleur à l’Operator — responsabilités

Le StatefulSet fournit une identité stable et des volumes par instance. L’Operator
ajoute des procédures propres à l’application.

Le moteur de base de données reste responsable des transactions et de l’exécution de la
réplication.

**Installer les CRD et exécuter le contrôleur sont deux opérations distinctes**, même si
un même outil d’installation les prend en charge.

Un contrôleur arrêté n’empêche pas nécessairement d’enregistrer des CR, mais il
n’applique plus les changements qui dépendent de lui.

---

### 3.6 Retrouver les objets dans le cluster

Après installation de la CRD pédagogique :

```bash
kubectl get crd databases.formation.example.org
kubectl api-resources --api-group=formation.example.org
kubectl explain database.spec --api-version=formation.example.org/v1alpha1
kubectl get databases -n default
kubectl get database cours-db -n default -o yaml
```

Les dernières commandes supposent que l’instance a été créée.

**La CRD décrit le type ; `kubectl get databases` liste ses instances.** Ces commandes
n’indiquent pas, à elles seules, qu’un contrôleur fonctionne.

---

### 3.7 Lien avec le CM5

Les extensions installées peuvent ajouter des objets tels que `ServiceMonitor` et
`PrometheusRule`.

Dans un manifest de ressource personnalisée, les champs de `spec` sont définis par le
schéma du type installé.

Ainsi, **`spec.groups[].rules` est un chemin de champs** dans un objet `PrometheusRule`,
et non un type d’objet Kubernetes autonome.

Le CM5 utilisera ces notions pour la supervision et les outils déclaratifs.

---

### 🧠 Synthèse du CM4

- Les **PV/PVC** découplent le stockage du cycle de vie des Pods ; la durabilité effective dépend du backend et des politiques de récupération.
- Les **StorageClasses** permettent un **provisionnement dynamique** des volumes.
- Cette automatisation peut servir au stockage **local ou réseau** ; elle ne garantit pas l’accessibilité depuis tous les nœuds.
- Les **modes d’accès**, **droits**, et **types de backend** déterminent la souplesse du stockage.
---

### Synthèse du CM4 — suite

- Les **StatefulSets** gèrent la stabilité des applications avec état, mais la **cohérence des données** relève des moteurs applicatifs.

- Les **CRD** étendent l’API ; les **Operators** automatisent des opérations propres aux applications.

> 💡 Kubernetes ne se limite pas à redémarrer des conteneurs : il orchestre la **durabilité**, la **stabilité** et la **persistance** des applications au sein d’environnements distribués.

---

### Références pour les CRD et Operators

- [Kubernetes — Ressources personnalisées](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
- [Kubernetes — Définir une CRD](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)
- [Kubernetes — Modèle Operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)

<!-- Présentation : les séparateurs --- sont des changements de diapositive.
Les fragments YAML identifiés sont à réunir sans les titres ni les clôtures Markdown.
Les parties 1 et 2 suivent l’ordre du CM4 original. -->
