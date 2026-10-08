# TD 7 — Gestion des crashs et persistance d’application dans Kubernetes

## Partie 1 — Gestion des crashs

---

### 1. Consultation de l’état des pods

L’application **Mailpit** déployée dans Kubernetes ne fait pour l’instant l’objet d’aucune surveillance particulière. Kubernetes se contente uniquement de s’assurer que le conteneur tourne.

Pour observer ce comportement, on peut se connecter dans le conteneur, tuer le processus Mailpit, puis constater que Kubernetes recrée automatiquement un conteneur.

Lister les pods associés à Mailpit :

```bash
kubectl get pods -l app=mailpit
```

Exemple de sortie :

```
NAME                       READY   STATUS    RESTARTS   AGE
mailpit-5c76b9bb6c-hc7s8   1/1     Running   0          3m31s
```

**Consigne :** relever l’état initial du pod, en particulier la valeur du champ RESTARTS.

**Rendu attendu :** sortie complète de la commande et commentaire expliquant ce que représente le compteur RESTARTS.

---

### 2. Connexion au pod

La commande `exec` lance un programme dans le pod ; `-i` conserve l’entrée standard, `-t` alloue un pseudo-terminal et `--` sépare les options de la commande à exécuter.

Connexion interactive dans le conteneur :

```bash
kubectl exec -it deployment/mailpit -- sh
```

Lister les processus :

```bash
ps -ef
```

Exemple de sortie :

```
PID   USER     TIME   COMMAND
1     root     0:00   /mailpit
13    root     0:00   sh
22    root     0:00   ps -ef
```

Créer un répertoire dans le conteneur :

```bash
mkdir /tmp/test
```

Vérification :

```bash
ls -ld /tmp/test
```

Sortie attendue :

```
drwxr-xr-x 2 mailpit mailpit 4096 Apr  2 00:12 /tmp/test/
```

**Consigne :** noter la présence du répertoire /tmp/test.

**Rendu attendu :** copie des sorties ps -ef et ls -ld /tmp/test, accompagnées d’un court commentaire sur la nature temporaire du système de fichiers d’un conteneur.

---

### 3. Conteneur associé à Mailpit

Depuis un second terminal sur la machine hôte, récupérer l’identifiant du conteneur utilisé par le pod :

```bash
kubectl get pods -l app=mailpit -o \
  jsonpath="{.items[*].status.containerStatuses[*].containerID}"
```

Sortie typique :

```
containerd://6a32eb45478301522...0164c03a9d86b51f559fd29
```

L’ID est composé du préfixe `containerd://` suivi de l’identifiant unique du conteneur.

**Consigne :** identifier clairement ces deux parties.

**Rendu attendu :** identifiant exact relevé et découpage entre préfixe et identifiant unique.

---

### 4. Comportement en cas de crash

Dans le terminal connecté au conteneur, arrêter le processus principal de Mailpit (PID 1) :

```bash
kill 1
```

La session se ferme lorsque Mailpit s’arrête. Relever le code réellement obtenu ; le DOCX présente cet exemple de sortie :

```
command terminated with exit code 137
```

Vérifier l’état du pod :

```bash
kubectl get pods -l app=mailpit
```

Exemple :

```
NAME                       READY   STATUS    RESTARTS      AGE
mailpit-5c76b9bb6c-hc7s8   1/1     Running   1 (12s ago)   3m
```

Constats :

- Le conteneur a été recréé automatiquement au sein du même pod.
- Le compteur **RESTARTS** a augmenté.

Récupérer le nouvel ID du conteneur :

```bash
kubectl get pods -l app=mailpit -o \
  jsonpath="{.items[*].status.containerStatuses[*].containerID}"
```

L’identifiant est différent du précédent : un nouveau conteneur a été créé.

**Consigne :** comparer les deux identifiants et en déduire le comportement de Kubernetes.

**Rendu attendu :** ancien et nouveau `containerID`, explication du redémarrage automatique (restart policy par défaut) et observation de l’incrément du compteur `RESTARTS`.

---

### 5. État du conteneur après redémarrage

Se reconnecter dans le nouveau conteneur :

```bash
kubectl exec -it deployment/mailpit -- sh
```

Vérifier si le répertoire existe encore :

```bash
ls -ld /tmp/test
```

Résultat attendu :

```
ls: /tmp/test: No such file or directory
```

Le nouveau conteneur repart avec un système de fichiers réinitialisé. L’ancien conteneur arrêté peut rester présent jusqu’au nettoyage par kubelet.

**Consigne :** expliquer pourquoi le répertoire n’existe plus.

**Rendu attendu :** phrase expliquant la volatilité du stockage local du conteneur.

---

### 6. Conteneur vu depuis Containerd (Minikube)

Quitter le shell du conteneur avec `exit`, puis, depuis la machine hôte, se connecter à Minikube :

```bash
minikube ssh
```

Inspecter un conteneur via son ID (sans le préfixe `containerd://`) :

```bash
sudo crictl inspect <ID>
```

Extrait notable :

```
"io.kubernetes.container.restartCount": "1"
"io.kubernetes.container.name": "mailpit"
```

Lister tous les conteneurs associés à Mailpit (actifs et stoppés) :

```bash
sudo crictl ps --all --label io.kubernetes.container.name=mailpit
```

Exemple de sortie :

```
CONTAINER      IMAGE        ... NAME     ATTEMPT   POD ID
f8091a6f2539d  4de68494...   mailpit   1         d38c85c5f2607
6a32eb454789a  4de68494...   mailpit   0         d38c85c5f2607
```

Observations :

- **ATTEMPT** augmente à chaque crash.
- **CONTAINER** change à chaque relance.

**Consigne :** analyser les différences entre les entrées listées.

**Rendu attendu :** explication du cycle de vie des conteneurs et du rôle de Containerd.

---

### 7. Attention au nettoyage des conteneurs

Après les observations dans Minikube, revenir à la machine hôte avec `exit`.

Lors d’un crash, Kubernetes :

1. crée un **nouveau conteneur** ;
2. laisse l’ancien conteneur sous forme **arrêtée**.

Le nettoyage est assuré automatiquement par **kubelet** selon une politique interne de garbage collection.

Pour aller plus loin :
[https://kubernetes.io/docs/concepts/cluster-administration/kubelet-garbage-collection/](https://kubernetes.io/docs/concepts/cluster-administration/kubelet-garbage-collection/)

**Consigne :** consulter la documentation et résumer le principe général du garbage collection.

**Rendu attendu :** court paragraphe expliquant la gestion automatique du nettoyage des conteneurs et images inutilisés.

## Partie 2 — Persistance des données

### 1. Origine du besoin

Les conteneurs ont une durée de vie courte : lors d'un redémarrage ou d'un remplacement, **les données écrites dans leur couche locale ne sont pas conservées**. Pour conserver des données, Kubernetes propose des **volumes persistants** (PersistentVolume / PersistentVolumeClaim).

Ce TD montre comment :

- observer le comportement actuel de Mailpit (perte de données) ;
- configurer un **volume persistant** ;
- monter le volume dans le conteneur ;
- ajuster la configuration de Mailpit pour utiliser ce volume ;
- sécuriser le conteneur ;
- tester la persistance.

**Consigne :** expliquer en quelques lignes pourquoi un conteneur perd ses données au redémarrage et dans quels cas cela pose problème.

**Rendu attendu :** un paragraphe décrivant le lien entre cycle de vie des conteneurs et nécessité de la persistance.

---

### 2. Utilisation d’un volume persistant externe (exemple NFS)

Deux actions sont nécessaires dans un pod utilisant un stockage externe :

1. Déclarer le volume dans `spec.volumes`.
2. Monter le volume dans `spec.containers.volumeMounts`.

Exemple de principe NFS (il nécessite un serveur NFS existant ; la manipulation suivante utilise plutôt un PV `hostPath`) :

```yaml
spec:
  volumes:
    - name: nfs
      nfs:
        server: 192.168.0.1
        path: /
```

Montage dans le conteneur :

```yaml
containers:
  - name: mailpit
    image: axllent/mailpit
    volumeMounts:
      - name: nfs
        mountPath: /maildir
```

**Consigne :** analyser la correspondance entre les champs volumes.name et volumeMounts.name.

**Rendu attendu :** une phrase expliquant la relation obligatoire entre les deux éléments pour que le montage fonctionne.

---

### 3. Volumes persistants

#### a. Déclaration d'un PersistentVolume

Exemple (`pv-mailpit.yaml`) :

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-mailpit
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  capacity:
    storage: 10Mi
  hostPath:
    path: /tmp/pv-mailpit
```

#### b. Création du volume

```bash
kubectl apply -f pv-mailpit.yaml
```

**Consigne :** créer ce fichier, l’appliquer, puis vérifier sa présence avec kubectl get pv.

**Rendu attendu :** capture de la ligne correspondant à pv-mailpit dans la sortie de kubectl get pv.

#### c. Déclaration du PersistentVolumeClaim

Exemple (`pvc-mailpit.yaml`) :

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-mailpit
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  resources:
    requests:
      storage: 10Mi
  volumeName: pv-mailpit
```

Création :

```bash
kubectl apply -f pvc-mailpit.yaml
```

#### d. Consultation des PV et PVC

```bash
kubectl get persistentvolume
kubectl get pvc
```

Un PV/PVC liés affichent `STATUS = Bound`.

---

### 4. Persistance des données avec Mailpit

Nous allons modifier le déploiement pour :

1. utiliser un PVC ;
2. monter le volume `/maildir` ;
3. lancer Mailpit avec `--db-file=/maildir/mailpit.db`.

#### a. Déclaration du volume dans le Deployment

```yaml
volumes:
  - name: maildir
    persistentVolumeClaim:
      claimName: pvc-mailpit
```

#### b. Montage dans le conteneur

```yaml
volumeMounts:
  - mountPath: /maildir
    name: maildir
```

#### c. Ajout des options Mailpit

```yaml
command:
  - "./mailpit"
  - "--db-file=/maildir/mailpit.db"
```

#### d. Déploiement complet (`mailpit-with-pvc.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mailpit
  labels:
    app: mailpit
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mailpit
  template:
    metadata:
      labels:
        app: mailpit
    spec:
      volumes:
        - name: maildir
          persistentVolumeClaim: { claimName: pvc-mailpit }
      containers:
        - image: axllent/mailpit
          name: mailpit
          imagePullPolicy: IfNotPresent
          volumeMounts:
            - mountPath: /maildir
              name: maildir
          command:
            - "./mailpit"
            - "--db-file=/maildir/mailpit.db"
```

Application :

```bash
kubectl apply -f mailpit-with-pvc.yaml
```

**Consigne :** expliquer où seront écrits les fichiers de Mailpit et pourquoi ils persistent.

**Rendu attendu :** localisation du fichier mailpit.db et justification de sa persistance.

---

### 5. Test de la persistance

#### a. Installation de Mailpit en local

Les commandes du DOCX ci-dessous ciblent Linux AMD64. Sur un autre système ou une autre architecture, utiliser le binaire Mailpit correspondant.

```bash
export MPURL="https://github.com/axllent/mailpit/releases"
wget $MPURL/download/v1.18.3/mailpit-linux-amd64.tar.gz
tar xfvz mailpit-linux-amd64.tar.gz mailpit
sudo cp mailpit /usr/local/bin/mailpit
sudo ln -s /usr/local/bin/mailpit /usr/local/bin/sendmail
```

#### b. Ouverture du port SMTP

Garder ce terminal ouvert et envoyer le message depuis un autre terminal. Après le remplacement du pod, relancer le port-forward si la connexion a été interrompue.

```bash
kubectl port-forward service/mailpit 1025
```

#### c. Envoi d’un mail

Message (`email.txt`) :

```
From: Clark Kent<super@man.org>
To: Bruce Wayne<bat@man.org>
Subject: Pot de départ Wonder Woman

Salut Bruce,

J'ai ouvert une cagnotte au bureau pour le départ de Diana.
N'hésite pas à passer au bureau.
Clark
```

Envoi :

```bash
cat email.txt | sendmail -S=127.0.0.1:1025
```

---

### 6. Sécurisation du conteneur : securityContext

Copier `mailpit-with-pvc.yaml` vers `mailpit-with-pvc-and-security-context.yaml`, puis ajouter ce bloc dans le conteneur Mailpit, sous `spec.template.spec.containers`.

```yaml
securityContext:
  runAsUser: 1000
  runAsNonRoot: true
  readOnlyRootFilesystem: true
```

Application :

```bash
kubectl apply -f mailpit-with-pvc-and-security-context.yaml
```

#### Crash observé

Le conteneur redémarre car `/maildir` ne possède pas les bons droits.

---

#### Correction manuelle sur Minikube

Le DOCX propose de constater l’effet d’une modification directe des droits sur le nœud :

```bash
minikube ssh
sudo chmod 777 /tmp/pv-mailpit
exit
```

Cette manipulation de démonstration donne l’écriture à tous les utilisateurs. Pour automatiser la préparation du volume, utiliser ensuite l’initContainer ci-dessous.

### 7. Correction via initContainer

Ajouter ce bloc sous `spec.template.spec`, au même niveau que `containers` et `volumes`. L’initContainer doit pouvoir modifier le propriétaire du volume ; le `securityContext` non-root reste limité au conteneur Mailpit.

```yaml
initContainers:
  - name: init-pv
    image: axllent/mailpit
    imagePullPolicy: IfNotPresent
    volumeMounts:
      - mountPath: /maildir
        name: maildir
    command: ["chown", "-R", "1000", "/maildir"]
```

Finalisation (`mailpit-with-pvc-and-security-context.yaml`) :

- initContainer pour ajuster les droits
- conteneur Mailpit non-root + rootFS en lecture seule

Application :

```bash
kubectl apply -f mailpit-with-pvc-and-security-context.yaml
```

Envoi d’un nouveau mail :

```bash
cat email.txt | sendmail -S=127.0.0.1:1025
```

**Consigne :** expliquer la différence entre corriger les droits via Minikube et via un initContainer.

**Rendu attendu :** justification du choix de l’initContainer pour la portabilité et l’automatisation.

---

### 8. Vérification de la persistance

- Ouvrir l’interface Web Mailpit via l’ingress :

```bash
kubectl get ingress mailpit
```

- Accéder à l’URL du champ **HOSTS**.

#### Suppression du pod

```bash
kubectl delete pods -l app=mailpit
```

#### Vérification

```bash
kubectl get pods -l app=mailpit
```

Vérifier que le message précédemment reçu apparaît toujours : sa présence valide la persistance.

**Consigne :** confirmer la présence du mail après suppression du pod.

**Rendu attendu :** preuve (capture ou description) que le message apparaît toujours.

#### Consultation de l’interface Mailpit

```bash
kubectl get ingress mailpit
```

Ouvrir en HTTP le nom de la colonne `HOSTS` défini au TD6 : par exemple `mailpit.192.168.49.2.nip.io` sous Linux ou `mailpit.127.0.0.1.nip.io` avec le tunnel Docker Desktop sur macOS/Windows. Le message doit être présent dans **Inbox**.

**Consigne :** accéder à l’interface et vérifier la présence du mail.

**Rendu attendu :** confirmation écrite que le message est visible via l’interface web.

---

## Partie 3 — Classes de stockage

### 1. Origine du besoin

Le stockage manuel demande de déclarer un PV, de créer un PVC et de préparer les droits du répertoire. Une **StorageClass** (`sc`) décrit une offre de stockage et son provisioner, afin de permettre la création automatique de volumes à partir des demandes des applications.

Des classes peuvent représenter différents besoins : `ssd` pour du stockage rapide, `hdd` pour du stockage standard ou `nfs` pour du stockage partagé. Les droits d’accès restent à adapter au pilote et au contexte de sécurité de l’application.

**Consigne :** expliquer en une ou deux phrases l’intérêt d’automatiser la création des volumes persistants.

**Rendu attendu :** un paragraphe expliquant comment StorageClass simplifie le déploiement et réduit les opérations manuelles.

### 2. Liste des classes de stockage

```bash
kubectl get storageclass
```

Exemple sur Minikube :

```text
NAME                 PROVISIONER               AGE
standard (default)   k8s.io/minikube-hostpath    30d
```

**Consigne :** identifier la classe portant la mention `(default)` dans votre cluster.

**Rendu attendu :** nom de la classe par défaut, normalement `standard` dans cet environnement.

### 3. Détail d’une classe de stockage

```bash
kubectl describe sc standard
```

Extrait illustratif :

```text
Name:                  standard
IsDefaultClass:        Yes
Annotations:           storageclass.kubernetes.io/is-default-class=true
Provisioner:           k8s.io/minikube-hostpath
Parameters:            <none>
AllowVolumeExpansion:  <unset>
MountOptions:          <none>
ReclaimPolicy:         Delete
VolumeBindingMode:     Immediate
```

Le DOCX utilise l’ancienne annotation `storageclass.beta.kubernetes.io/is-default-class`. Relever celle réellement présente dans votre cluster.

**Consigne :** repérer l’entrée qui définit la classe comme classe par défaut.

**Rendu attendu :** annotation relevée et valeur associée.

### 4. Classe de stockage par défaut

Un PVC qui omet `storageClassName` utilise la classe par défaut. Une valeur explicitement vide (`storageClassName: ""`) ne demande pas cette classe.

Conserver une seule classe par défaut rend le choix prévisible. Plusieurs peuvent néanmoins coexister, notamment pendant une migration : Kubernetes choisit alors la plus récemment créée parmi les classes par défaut.

Référence : [StorageClass par défaut — Kubernetes](https://kubernetes.io/docs/concepts/storage/storage-classes/#default-storageclass).

**Consigne :** expliquer l’intérêt de conserver une seule classe par défaut et le comportement en présence de plusieurs classes par défaut.

**Rendu attendu :** une explication du choix automatique et de la règle de sélection.

### 5. Les différentes classes de stockage

#### a. Familles de pilotes

- **In-tree** : pilotes historiquement intégrés au code de Kubernetes.
- **FlexVolume** : mécanisme hérité utilisant des outils externes.
- **CSI (Container Storage Interface)** : interface permettant de développer les pilotes indépendamment du cœur de Kubernetes.

#### b. Évolution vers des pilotes indépendants

L’intégration des pilotes au cœur de Kubernetes liait leurs mises à jour à celles du cluster, compliquait la maintenance et pouvait exposer le cluster aux défauts d’un pilote. L’approche **out-of-tree** sépare leur développement de celui de Kubernetes.

**Consigne :** résumer les raisons de l’évolution des pilotes in-tree vers des pilotes indépendants.

**Rendu attendu :** un paragraphe évoquant la maintenance, les risques et la modularité.

### 6. Caractéristiques des classes de stockage

#### a. Modes d’accès

| Mode | Signification |
| --- | --- |
| `ReadWriteOnce` (RWO) | Lecture/écriture depuis un seul nœud ; plusieurs pods de ce nœud peuvent partager le volume. |
| `ReadOnlyMany` (ROX) | Lecture depuis plusieurs nœuds. |
| `ReadWriteMany` (RWX) | Lecture/écriture depuis plusieurs nœuds. |
| `ReadWriteOncePod` (RWOP) | Lecture/écriture limitée à un seul pod, avec un pilote CSI compatible. |

Référence : [Modes d’accès des volumes — Kubernetes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes).

#### b. Capacités de quelques pilotes

Le tableau ci-dessous reprend les exemples du support Word à titre de comparaison historique. Les modes disponibles et le nom du provisioner dépendent du pilote installé et de sa version ; ce tableau ne constitue pas une liste d’installations à effectuer.

| Stockage cité dans le DOCX | Modes indiqués dans le support | Provisioner cité |
| --- | --- | --- |
| AWS Elastic Block Store | RWO | `ebs.csi.aws.com` |
| Azure File | RWO, ROX, RWX | `file.csi.azure.com` |
| Azure Disk | RWO | `disk.csi.azure.com` |
| CephFS | RWO, ROX, RWX | `cephfs.csi.ceph.com` |
| Cinder | RWO | `cinder.csi.openstack.org` |
| GCE Persistent Disk | RWO, ROX | `pd.csi.storage.gke.io` |
| GlusterFS | RWO, ROX, RWX | `org.gluster.glusterfs` |
| HostPath | RWO | `kubernetes.io/host-path` |
| Quobyte | RWO, ROX, RWX | `quobyte-csi` |
| NFS | RWO, ROX, RWX | `nfs.csi.k8s.io` |
| Ceph RBD | RWO, ROX | `rbd.csi.ceph.com` |
| vSphere Volume | RWO | `csi.vsphere.vmware.com` |

Pour Minikube dans ce TD, utiliser `k8s.io/minikube-hostpath`, tel qu’affiché par `kubectl get sc`. Ne pas le remplacer par l’entrée HostPath du tableau. Un mode RWO ne signifie pas qu’un seul pod peut utiliser le volume : la contrainte porte sur le nœud.

**Consigne :** choisir deux pilotes dans le tableau et comparer les modes d’accès indiqués.

**Rendu attendu :** un tableau ou une liste donnant les modes RWO/ROX/RWX des deux exemples.

#### c. Pilotes CSI présents dans le cluster

```bash
kubectl get csidrivers
kubectl get csinode
```

La première commande liste les objets CSIDriver ; la seconde donne les objets décrivant les pilotes CSI enregistrés sur les nœuds. Avec le provisioner hostpath de Minikube, la liste des CSIDriver peut être vide.

Exemples de noms rencontrés dans d’autres environnements :

- OpenStack/OVH : `cinder.csi.openstack.org` ;
- Azure : `disk.csi.azure.com`, `file.csi.azure.com`.

**Consigne :** exécuter `kubectl get csidrivers` et relever le résultat.

**Rendu attendu :** copie de la sortie, même vide.

### 7. Déclaration d’une classe de stockage

#### a. Structure générale

Une StorageClass comporte `apiVersion`, `kind`, `metadata.name`, `provisioner` et éventuellement des `parameters`. Les champs `reclaimPolicy` et `volumeBindingMode` précisent le devenir du stockage et le moment de son provisionnement ou de sa liaison.

#### b. Création de la classe hdd

Enregistrer dans `storage-class.yaml` :

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: hdd
provisioner: k8s.io/minikube-hostpath
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

Le nom `hdd` sert ici à illustrer le choix d’une classe ; il ne change pas le matériel de stockage de Minikube.

```bash
kubectl apply -f storage-class.yaml
kubectl get sc
```

Sortie attendue lors de la création :

```text
storageclass.storage.k8s.io/hdd created
```

**Consigne :** créer le fichier, l’appliquer et vérifier l’apparition de la classe.

**Rendu attendu :** sortie de `kubectl get sc` montrant `hdd`.

### 8. Test de création automatique d’un volume persistant

Avec le provisionnement dynamique, l’application demande le stockage via un PVC ; il n’est plus nécessaire de créer manuellement son PV.

#### a. Tentative de modification du PVC existant

Enregistrer cette nouvelle définition dans `pvc-mailpit.yaml`, en remplaçant la définition manuelle précédente. Retirer `volumeName` : le volume sera choisi automatiquement.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-mailpit
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: hdd
  resources:
    requests:
      storage: 10Mi
```

```bash
kubectl apply -f pvc-mailpit.yaml
```

La modification du PVC déjà lié à la classe `manual` est refusée :

```text
The PersistentVolumeClaim "pvc-mailpit" is invalid: spec is immutable...
```

#### b. Explication et suppression des ressources de l’exercice

La classe d’un PVC lié ne se change pas ainsi. Certaines modifications, comme l’augmentation de capacité lorsque le stockage la prend en charge, sont possibles, mais pas ce changement de classe.

Cette étape crée un **nouveau stockage** : elle ne transfère pas les messages du volume précédent. Réaliser d’abord les preuves de persistance demandées en partie 2.

Supprimer le Deployment avant le PVC pour libérer son utilisation :

```bash
kubectl delete -f mailpit-with-pvc-and-security-context.yaml
kubectl delete -f pvc-mailpit.yaml
```

Le PV manuel `pv-mailpit` peut rester en état `Released` avec sa politique `Retain`. Il n’est pas réutilisé automatiquement par la classe `hdd`.

#### c. Recréation et vérification

Réutiliser le Deployment avec son initContainer et son montage du PVC :

```bash
kubectl apply -f pvc-mailpit.yaml
kubectl apply -f mailpit-with-pvc-and-security-context.yaml
kubectl get pvc pvc-mailpit
kubectl get pv
kubectl get pods -l app=mailpit
```

Vérifier que le PVC devient `Bound`, que sa classe est `hdd` et que le nom du volume a été attribué automatiquement. Le provisioner prend en charge la création du PV.

**Consigne :** expliquer pourquoi changer la StorageClass d’un PVC lié nécessite de recréer la demande dans cet exercice.

**Rendu attendu :** un paragraphe expliquant la stabilité de la liaison au stockage, accompagné de la sortie montrant le nouveau PVC lié à un PV de classe `hdd`.
