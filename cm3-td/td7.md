# TD 7 — Gestion des crashs d’application

---

## 1. Consultation de l’état des pods

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

---

## 2. Connexion au pod

Connexion interactive dans le conteneur :

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

---

## 3. Conteneur associé à Mailpit

Récupérer l’identifiant du conteneur utilisé par le pod :

```bash
kubectl get pods -l app=mailpit -o \
  jsonpath="{.items[*].status.containerStatuses[*].containerID}"
```

Sortie typique :

```
containerd://6a32eb45478301522...0164c03a9d86b51f559fd29
```

L’ID est composé du préfixe `containerd://` suivi de l’identifiant unique du conteneur.

---

## 4. Comportement en cas de crash

Tuer le processus principal de Mailpit :

```bash
kill 1
```

La connexion est interrompue avec le message :

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

- Le pod a redémarré automatiquement.
- Le compteur **RESTARTS** a augmenté.

Récupérer le nouvel ID du conteneur :

```bash
kubectl get pods -l app=mailpit -o \
  jsonpath="{.items[*].status.containerStatuses[*].containerID}"
```

L’identifiant est différent du précédent : un new conteneur a été créé.

---

## 5. État du conteneur après redémarrage

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

Le crash a provoqué la _destruction complète_ du conteneur, et non un simple redémarrage du même conteneur.

---

## 6. Conteneur vu depuis Containerd (Minikube)

Connexion à la machine Minikube :

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

---

## 7. Attention au nettoyage des conteneurs

Lors d’un crash, Kubernetes :

1. crée un **nouveau conteneur** ;
2. laisse l’ancien conteneur sous forme **arrêtée**.

Le nettoyage est assuré automatiquement par **kubelet** selon une politique interne de garbage collection.

Pour aller plus loin :
[https://kubernetes.io/docs/concepts/cluster-administration/kubelet-garbage-collection/](https://kubernetes.io/docs/concepts/cluster-administration/kubelet-garbage-collection/)

# TD 7 — Persistance des données dans Kubernetes

## 1. Origine du besoin

Les conteneurs ont une durée de vie courte : lors d'un redémarrage ou d'un remplacement, **toutes les données internes disparaissent**. Pour conserver des données, Kubernetes propose des **volumes persistants** (PersistentVolume / PersistentVolumeClaim).

Ce TD montre comment :

- observer le comportement actuel de Mailpit (perte de données) ;
- configurer un **volume persistant** ;
- monter le volume dans le conteneur ;
- ajuster la configuration de Mailpit pour utiliser ce volume ;
- sécuriser le conteneur ;
- tester la persistance.

---

## 2. Utilisation d’un volume persistant externe (exemple NFS)

Deux actions sont nécessaires dans un pod utilisant un stockage externe :

1. Déclarer le volume dans `spec.volumes`.
2. Monter le volume dans `spec.containers.volumeMounts`.

Exemple d'utilisation NFS :

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

---

## 3. Volumes persistants

### a. Déclaration d'un PersistentVolume

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

### b. Création du volume

```bash
kubectl apply -f pv-mailpit.yaml
```

### c. Déclaration du PersistentVolumeClaim

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

### d. Consultation des PV et PVC

```bash
kubectl get persistentvolume
kubectl get pvc
```

Un PV/PVC liés affichent `STATUS = Bound`.

---

## 4. Persistance des données avec Mailpit

Nous allons modifier le déploiement pour :

1. utiliser un PVC ;
2. monter le volume `/maildir` ;
3. lancer Mailpit avec `--db-file=/maildir/mailpit.db`.

### a. Déclaration du volume dans le Deployment

```yaml
volumes:
  - name: maildir
    persistentVolumeClaim:
      claimName: pvc-mailpit
```

### b. Montage dans le conteneur

```yaml
volumeMounts:
  - mountPath: /maildir
    name: maildir
```

### c. Ajout des options Mailpit

```yaml
command:
  - "./mailpit"
  - "--db-file=/maildir/mailpit.db"
```

### d. Déploiement complet (`mailpit-with-pvc.yaml`)

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

---

## 5. Test de la persistance

### a. Installation de Mailpit en local

```bash
export MPURL="https://github.com/axllent/mailpit/releases"
wget $MPURL/download/v1.18.3/mailpit-linux-amd64.tar.gz
tar xfvz mailpit-linux-amd64.tar.gz mailpit
sudo cp mailpit /usr/local/bin/mailpit
sudo ln -s /usr/local/bin/mailpit /usr/local/bin/sendmail
```

### b. Ouverture du port SMTP

```bash
kubectl port-forward service/mailpit 1025
```

### c. Envoi d’un mail

Message (`email.txt`) :

```
From: Clark Kent<super@man.org>
To: Bruce Wayne<bat@man.org>
Subject: Pot de départ Wonder Woman

Salut Bruce,

J'ai ouvert une cagnotte pour le départ de Diana.
Clark
```

Envoi :

```bash
cat email.txt | sendmail -S=127.0.0.1:1025
```

---

## 6. Sécurisation du conteneur : securityContext

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

### Crash observé

Le conteneur redémarre car `/maildir` ne possède pas les bons droits.

---

## 7. Correction via initContainer

Définition :

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

---

## 8. Vérification de la persistance

- Ouvrir l’interface Web Mailpit via l’ingress :

```bash
kubectl get ingress mailpit
```

- Accéder à l’URL du champ **HOSTS**.

### Suppression du pod

```bash
kubectl delete pods -l app=mailpit
```

### Vérification

```bash
kubectl get pods -l app=mailpit
```

Le message précédemment reçu apparaît toujours : la persistance fonctionne.

---

## 9. Conclusion

Dans ce TD, vous avez appris :

- la différence entre stockage interne au conteneur et volume persistant ;
- comment déclarer un PV et un PVC ;
- comment monter un volume dans un Deployment ;
- comment adapter Mailpit pour utiliser un stockage durable ;
- comment sécuriser un conteneur (securityContext) ;
- comment utiliser un initContainer pour préparer un volume.

Ces notions servent de base pour les futurs TD portant sur :

- `ConfigMap` et `Secret` ;
- `StatefulSet` ;
- stratégies de déploiement avancées.
