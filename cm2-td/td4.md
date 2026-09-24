# TD 4 – Gestion d’une application Kubernetes avec `kubectl`

## Objectifs

À l’issue du TD, vous pourrez créer et inspecter un Deployment, suivre les Pods et les ReplicaSets, consulter les journaux, accéder temporairement à une application, créer un Service et modifier le nombre de réplicas.

> **Préalable.** Vérifiez le contexte avec `kubectl config current-context`. Les commandes ci-dessous supposent que vous travaillez dans le namespace `default` et que le contexte sélectionné est celui du cluster de TD. Les noms de Pods, adresses IP, âges et événements présentés sont des exemples : vos résultats seront différents. Ne supprimez aucune ressource d’un autre contexte.

## Partie 1 – Déploiement et accès direct à Mailpit

### 1. Supprimer le Deployment précédent

Mailpit a été créé dans le Dashboard lors de la séance précédente. Listez d’abord les Deployments :

```bash
kubectl get deployment
```

```text
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
mailpit   1/1     1            1           8d
```

Supprimez **uniquement** ce Deployment :

```bash
kubectl delete deployment mailpit
```

```text
deployment.apps "mailpit" deleted
```

Observez les Pods aussitôt après :

```bash
kubectl get pods
```

```text
NAME                       READY   STATUS        RESTARTS   AGE
mailpit-69bd8f74cb-kl9p5   1/1     Terminating   2          8d
```

Après quelques instants, le Pod disparaît. Si aucun autre Pod n’existe dans `default`, la réponse peut être `No resources found in default namespace.`. La suppression du Deployment entraîne celle des ReplicaSets et Pods qu’il contrôle ; elle ne supprime pas automatiquement un éventuel Service ou volume persistant créé séparément. Si un Service `mailpit` existe déjà, signalez-le avant la partie 2.

### 2. Créer un Deployment depuis la ligne de commande

La commande `kubectl create deployment` reçoit le nom du Deployment et l’image à exécuter :

```bash
kubectl create deployment mailpit --image=axllent/mailpit
```

```text
deployment.apps/mailpit created
```

Le Deployment demande ici un réplica. Son Pod est créé progressivement ; patientez si l’image doit être téléchargée.

### 3. Examiner l’état du Deployment

```bash
kubectl get deployment
kubectl get deployment mailpit -o wide
kubectl describe deployment mailpit
```

Exemples abrégés :

```text
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
mailpit   1/1     1            1           3m
```

```text
Name:                   mailpit
Namespace:              default
Selector:               app=mailpit
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
Pod Template:
  Labels:  app=mailpit
  Containers:
    mailpit:
      Image: axllent/mailpit
      Port:  <none>
Conditions:
  Type         Status  Reason
  Available    True    MinimumReplicasAvailable
  Progressing  True    NewReplicaSetAvailable
Events:
  Normal  ScalingReplicaSet  ...  Scaled up replica set mailpit-... to 1
```

Repérez la stratégie `RollingUpdate`, le sélecteur, l’image, le nombre de réplicas et les événements. **`Port: <none>` signifie qu’aucun `containerPort` n’est déclaré ; cela n’empêche pas l’application d’écouter sur un port ni `kubectl port-forward` de fonctionner.**

### 4. Comprendre le ReplicaSet

Un Deployment gère un ReplicaSet qui maintient le nombre demandé de Pods. Lors d’une mise à jour du modèle des Pods, un nouveau ReplicaSet peut être créé ; les anciens peuvent être conservés pour permettre un retour à la version précédente.

```bash
kubectl get replicaset
```

```text
NAME                 DESIRED   CURRENT   READY   AGE
mailpit-5bcf98ffcd   1         1         1       2m
```

Reprenez **le nom affiché dans votre terminal** :

```bash
kubectl describe rs mailpit-5bcf98ffcd
```

```text
Name:           mailpit-5bcf98ffcd
Selector:       app=mailpit,pod-template-hash=5bcf98ffcd
Controlled By:  Deployment/mailpit
Replicas:       1 current / 1 desired
Pods Status:    1 Running / 0 Waiting / 0 Failed
Events:
  Normal  SuccessfulCreate  ...  Created pod: mailpit-5bcf98ffcd-nl4l9
```

Le suffixe du ReplicaSet correspond au hash du modèle de Pod. Les événements permettent de suivre les créations et certains échecs ; les redémarrages et leurs causes se vérifient aussi dans la description du Pod et ses événements.

### 5. Inspecter le Pod

```bash
kubectl get pods
kubectl get pods --watch
```

Arrêtez le suivi avec `Ctrl+C`. Exemple de résultat :

```text
NAME                       READY   STATUS    RESTARTS   AGE
mailpit-5bcf98ffcd-nl4l9   1/1     Running   0          17s
```

Décrivez le Pod en remplaçant le nom d’exemple :

```bash
kubectl describe pod mailpit-5bcf98ffcd-nl4l9
```

```text
Name:          mailpit-5bcf98ffcd-nl4l9
Namespace:     default
Node:          minikube-137/192.168.58.2
Labels:        app=mailpit
Status:        Running
IP:            10.244.0.7
Controlled By: ReplicaSet/mailpit-5bcf98ffcd
Events:
  Normal  Scheduled  ...  Successfully assigned default/mailpit-... to minikube-137
  Normal  Pulling    ...  Pulling image "axllent/mailpit"
  Normal  Started    ...  Started container mailpit
```

Les valeurs de `Node` et `IP` dépendent de votre cluster. Relevez le nœud, l’IP, le contrôleur et les événements du Pod.

### 6. Lire les journaux

```bash
kubectl logs deployment/mailpit
```

On peut aussi cibler un Pod précis : `kubectl logs <nom-du-pod>`. Si le Pod contient plusieurs conteneurs, ajoutez `-c <nom-du-conteneur>`. Dans les journaux de Mailpit, recherchez l’écoute SMTP sur **1025** et l’interface HTTP sur **8025** ; leur formulation exacte varie selon l’image.

### 7. Ouvrir temporairement l’interface web

```bash
kubectl port-forward deployment/mailpit 8025:8025
```

```text
Forwarding from 127.0.0.1:8025 -> 8025
Forwarding from [::1]:8025 -> 8025
```

Ouvrez [http://127.0.0.1:8025](http://127.0.0.1:8025). Laissez le terminal ouvert puis arrêtez la redirection avec `Ctrl+C`. Le ciblage du Deployment évite de recopier le nom d’un Pod ; **une session en cours s’interrompt néanmoins si le Pod sélectionné est remplacé** et doit être relancée. Un port occupé sur la machine locale provoque une erreur : arrêtez l’autre transfert ou utilisez, par exemple, `8080:8025` et ouvrez `http://127.0.0.1:8080`.

| Environnement | Accès depuis le navigateur |
|---|---|
| Linux, macOS, Windows avec Docker Desktop | Ouvrir `http://127.0.0.1:8025` sur la machine qui exécute `kubectl`. |
| Windows avec commande exécutée dans WSL2 | Essayer `http://localhost:8025` depuis Windows ; selon la configuration réseau de WSL2, utiliser le navigateur dans WSL ou adapter le transfert. |

> **Lien avec Lens.** `kubectl port-forward` peut cibler le Deployment même sans Service ni port déclaré dans le Pod. Le transfert lancé dans un terminal n’apparaît pas parmi les sessions créées par Lens. Dans Lens, la création depuis un Pod dépend de l’affichage d’un port déclaré ; la fiche d’un Service offre une autre entrée lorsque ce Service existe.

## Partie 2 – Service, découverte et nombre de réplicas

### 1. Pourquoi créer un Service ?

L’IP et le nom d’un Pod peuvent changer lorsqu’il est remplacé. Un Service fournit une **adresse logique stable** et sélectionne les Pods à partir de leurs labels. Un Service `ClusterIP` possède un nom DNS interne et peut diriger le trafic vers plusieurs Pods prêts. La résolution DNS donne normalement l’IP du Service, et non une entrée DNS réécrite pour chaque nouveau Pod. Ce nom est réservé au cluster : il ne rend pas l’application directement accessible depuis le navigateur de l’hôte.

### 2. Exposer les deux ports de Mailpit

```bash
kubectl expose deployment/mailpit --port 1025,8025
```

```text
service/mailpit exposed
```

Dans cette version de `kubectl`, la liste séparée par des virgules crée deux ports TCP dans le Service : SMTP sur **1025** et HTTP sur **8025**. Chacun cible le même numéro de port sur le Pod. Kubernetes leur attribue des noms distincts (`port-1` et `port-2`), obligatoires dans un Service à plusieurs ports. Le Service sélectionne les Pods portant `app=mailpit`. Vérifiez :

```bash
kubectl get service mailpit
kubectl describe service mailpit
kubectl get endpointslice -l kubernetes.io/service-name=mailpit
```

Dans le cluster de TD, `kubectl get service mailpit -o yaml` confirme les deux entrées : `port-1` pour `1025/TCP` et `port-2` pour `8025/TCP`. Pour attribuer des noms explicites comme `smtp` et `http`, définissez le Service dans un manifeste YAML. Voir la [documentation des Services](https://kubernetes.io/docs/concepts/services-networking/service/).

### 3. Vérifier la résolution DNS depuis un Pod

Essayez d’abord d’ouvrir un shell dans le Pod applicatif :

```bash
kubectl exec -it deployment/mailpit -- sh
```

Si un shell est disponible, exécutez `getent hosts mailpit` **si `getent` est installé**, puis `exit`. Exemple :

```text
10.107.51.181  mailpit.default.svc.cluster.local mailpit
```

L’adresse obtenue varie d’un cluster à l’autre. En l’absence de shell ou d’outil DNS dans l’image Mailpit, lancez plutôt un Pod de test temporaire :

```bash
kubectl run test-mailpit --rm -it --restart=Never --image=busybox:1.36 -- nslookup mailpit
```

Exemple :

```text
Name:    mailpit.default.svc.cluster.local
Address: 10.107.51.181
```

Selon la configuration du résolveur, la réponse peut comporter plusieurs lignes supplémentaires. Le Pod de test est supprimé après la commande. Le nom complet `mailpit.default.svc.cluster.local` est utilisable depuis les autres namespaces, tandis que le nom court `mailpit` fonctionne usuellement dans le namespace `default` du Pod appelant.

> **Pour aller plus loin :** `kubectl debug <nom-du-pod> -it --image=busybox:1.36 -- sh` ajoute un conteneur de diagnostic éphémère au Pod existant. Réservez cette variante à un exercice de débogage : ce conteneur n’est pas effacé de l’objet Pod par la seule commande `exit`. Voir la [documentation de `kubectl debug`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_debug/).

### 4. Changer le nombre de réplicas

Passez à deux Pods :

```bash
kubectl scale deployment/mailpit --replicas=2
kubectl get deployment mailpit
kubectl get pods -l app=mailpit
```

Exemple :

```text
deployment.apps/mailpit scaled
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
mailpit   2/2     2            2           6m
```

Le Service peut distribuer de nouvelles connexions entre les Pods disponibles. **Attention : Mailpit conserve ici les messages dans chaque instance séparément.** Avec deux réplicas sans stockage et configuration partagés, une interface web peut afficher des messages différents selon le Pod atteint : cette manipulation illustre la mécanique de réplication, pas une configuration Mailpit hautement disponible.

Pour arrêter temporairement les Pods tout en conservant le Deployment et le Service :

```bash
kubectl scale deployment/mailpit --replicas=0
kubectl get pods -l app=mailpit
```

Après la phase `Terminating`, aucun Pod ne répondra au Service. Relancez ensuite l’application :

```bash
kubectl scale deployment/mailpit --replicas=1
kubectl rollout status deployment/mailpit
```

### Questions de synthèse

1. Quel objet demande un nombre de réplicas et quel objet crée concrètement les Pods ?
2. Pourquoi `kubectl port-forward deployment/mailpit 8025:8025` fonctionne-t-il alors que `Port: <none>` figure dans la description ?
3. Quelle différence existe entre l’adresse `127.0.0.1:8025` du port forwarding et le nom DNS `mailpit.default.svc.cluster.local` ?
4. Que deviennent le Deployment, le Service et les Pods après `--replicas=0` ?
5. Pourquoi deux réplicas Mailpit peuvent-ils produire des boîtes de réception différentes dans cette configuration ?
