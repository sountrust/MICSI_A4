# Setting Up an Azure Managed Kubernetes Cluster (AKS)

## Creating a Managed Kubernetes Cluster on Azure via the Portal

### Step 1: Log in to Azure Portal
- Go to [Azure Portal](https://portal.azure.com/)
- Sign in with your Azure account.

### Step 2: Create a Resource Group
- In the **Azure Portal**, search for "Resource groups."
- Click **Create** and provide:
  - **Resource Group Name**: `myResourceGroup`
  - **Region**: Choose a nearby region to minimize costs (e.g., `East US`).
- Click **Review + Create** and then **Create**.

### Step 3: Create an AKS Cluster
- In the **Azure Portal**, search for "Kubernetes services."
- Click **Create** > **Create a Kubernetes cluster**.
- Provide the following details:
  - **Subscription**: Select your active subscription.
  - **Resource Group**: Choose `myResourceGroup`.
  - **Cluster Name**: `myAKSCluster`
  - **Region**: Same as the resource group.
  - **Prometheus**: Disable Prometheus metrics
  - **Node Count**: Set to **1** to minimize costs.
  - **Authentication Method**: Use **System-assigned managed identity**.
- Click **Review + Create**, then **Create**.
- Wait for the deployment to complete.

---

## Installing Essential Kubernetes Tools

To efficiently manage the Kubernetes cluster, the following tools must be installed:

### Step 1: Install kubectl

#### MacOS:
```sh
brew install kubectl
```
#### Windows:
Using Chocolatey:
```sh
choco install kubernetes-cli -y
```
Using Winget:
```sh
winget install -e --id Kubernetes.kubectl
```
#### Linux (Debian/Ubuntu):
```sh
sudo apt update
sudo apt install -y kubectl
```

Verify installation:
```sh
kubectl version --client
```

### Step 2: Install Azure CLI

#### MacOS:
```sh
brew install azure-cli
```
#### Windows:
```sh
winget install -e --id Microsoft.AzureCLI
```
#### Linux (Debian/Ubuntu):
```sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Verify installation:
```sh
az version
```

### Step 3: Install Helm
Helm is a package manager for Kubernetes.

#### MacOS:
```sh
brew install helm
```
#### Windows:
```sh
choco install kubernetes-helm -y
```
#### Linux:
```sh
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Verify installation:
```sh
helm version
```

### Step 4: Install Flux CLI
Flux is a GitOps tool used to automate Kubernetes deployments.

```sh
curl -s https://fluxcd.io/install.sh | sudo bash
```

Verify installation:
```sh
flux --version
```

### Step 5: Install Lens IDE
Lens is a Kubernetes IDE for visualizing and managing clusters.

Download and install Lens from [Lens Website](https://k8slens.dev/)

---

## Connecting to Your AKS Cluster

### Step 1: Log in to Azure CLI
```sh
az login
```
Follow the authentication steps in the browser.

### Step 2: Retrieve Cluster Credentials
```sh
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
```
This command retrieves the kubeconfig file for your cluster.

### Step 3: Verify Connection
```sh
kubectl get nodes
```
If successful, you should see the list of nodes in your cluster.

### Step 4: Retrieve Cluster IP (Load Balancer)
To find the external IP of the cluster’s load balancer:
```sh
kubectl get svc --all-namespaces
```
Alternatively, in the Azure Portal:
- Navigate to your **AKS Cluster**.
- Click on **Services and Ingress**.
- Locate the **LoadBalancer** service to find the external IP.

Share the external IP and the chosen name with the instructor to create a DNS entry in Cloudflare:
```
Format: [name].sountrust.fr
```

---

## Creating a Local Project and Pushing to GitLab/Github

### Step 1: Create a Local Project Directory
```sh
mkdir my-k8s-project
cd my-k8s-project
```

### Step 2: Copy and Paste the README File
Save this `README.md` file inside your `my-k8s-project` directory.

### Step 3: Initialize Git Repository
```sh
git init
```

### Step 4: Add Files to Git
```sh
git add .
```

### Step 5: Commit the Changes
```sh
git commit -m "Initial commit with README"
```

### Step 6: Push to GitLab Server
1. Request an account from the instructor.
2. Once you have your GitLab account, create a new repository.
3. Link your local repository to the GitLab remote:
   ```sh
   git remote add origin https://baowlab.sountrust.fr/micsi_a4/your-repository.git or https://github.com
   ```
4. Push the changes to GitLab/Github:
   ```sh
   git push -u origin main
   ```

Now your project is stored in GitLab/Github, ready for further development!

---

## Setting Up Traefik Reverse Proxy

To enable reverse proxy capabilities, you will copy the provided `values.yaml` file into your repository and deploy Traefik using Helm.

### Step 1: Create a Traefik Directory in Your Repository
```sh
mkdir -p traefik
cd traefik
```

### Step 2: Copy the Provided `values.yaml`
Manually copy and paste the content of the `values.yaml` file provided by the instructor into a new file in your repository:

1. Open the `traefik/values.yaml` file in your instructor GitLab repository.
2. Copy its entire content.
3. On your local machine, inside the `traefik` directory, create the file:
   ```sh
   nano values.yaml
   ```
4. Paste the copied content into the file.
5. Save and exit (`CTRL + X`, then `Y`, then `Enter`).

### Step 3: Commit and Push the Changes to GitLab
```sh
git add traefik/values.yaml
git commit -m "Added values.yaml for Traefik"
git push origin main
```

### Step 4: Deploy Traefik with Helm
Run the following commands to deploy Traefik in your AKS cluster:
```sh
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm install traefik traefik/traefik -n default -f traefik/values.yaml
```

### Step 5: Verify Traefik Deployment
Check if Traefik is running successfully:
```sh
kubectl get pods -n default
```

Once this is done, your Traefik reverse proxy should be operational.


# Setting Up Kubernetes Cluster Components

## Setting Up Cert-Manager for SSL Certificates

Cert-Manager is used to manage TLS certificates automatically within the Kubernetes cluster.

### Step 1: Install Cert-Manager Using kubectl
Run the following command to install Cert-Manager:
```sh
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.0/cert-manager.yaml
```
This deploys Cert-Manager into your cluster.

### Step 2: Verify Cert-Manager Deployment
Check if Cert-Manager is running successfully:
```sh
kubectl get pods -n cert-manager
```
Ensure that all Cert-Manager pods are in the `Running` state before proceeding.

### Step 3: Create a Cluster-Issuer Configuration
To configure Cert-Manager to issue certificates using ACME (Let's Encrypt), create a new directory for the cluster issuer configuration.
```sh
mkdir -p certmanager
cd certmanager
```

### Step 4: Copy the Provided `cluster-issuer-acme.yaml`
Manually copy and paste the content of the `cluster-issuer-acme.yaml` file provided by the instructor into a new file in your repository:

1. Open the `certmanager/cluster-issuer-acme.yaml` file in your GitLab repository.
2. Copy its entire content.
3. On your local machine, inside the `certmanager` directory, create the file:
   ```sh
   nano cluster-issuer-acme.yaml
   ```
4. Paste the copied content into the file.
5. Save and exit (`CTRL + X`, then `Y`, then `Enter`).

### Step 5: Commit and Push the Changes to GitLab
```sh
git add certmanager/cluster-issuer-acme.yaml
git commit -m "Added cluster-issuer configuration for Cert-Manager"
git push origin main
```

### Step 6: Apply the Cluster Issuer Configuration
```sh
kubectl apply -f certmanager/cluster-issuer-acme.yaml
```
This registers Cert-Manager to issue SSL certificates using Let's Encrypt for your Kubernetes cluster.

Once this is done, Cert-Manager will handle SSL certificate provisioning automatically.
# Setting Up Kubernetes GitOps with Flux

## Prerequisites
Flux requires write access to a Git repository where it will store Kubernetes manifests for deployment automation. You must first generate a personal access token (PAT) for authentication.

### Step 1: Generate a Personal Access Token (PAT)
#### GitHub:
1. Go to **GitHub** > **Settings** > **Developer settings** > **Personal access tokens**.
2. Click **Generate new token**.
3. Select scopes:
   - `repo` (Full control of repositories)
   - `write:packages`
   - `read:org` (if working with organization repositories)
4. Click **Generate Token** and copy the generated token.

#### GitLab:
1. Go to **GitLab** > **User Settings** > **Access Tokens**.
2. Enter a name for the token.
3. Select scopes:
   - `api`
   - `write_repository`
4. Click **Create Personal Access Token** and copy the generated token.

### Step 2: Set the Token as an Environment Variable
For convenience, store the token in an environment variable so Flux can use it without manual entry.
```sh
export GIT_AUTH_TOKEN=<your-generated-token>
```
Ensure this variable is set in your shell configuration (`~/.bashrc` or `~/.zshrc`) for persistence.

## Bootstrapping Flux with GitHub and GitLab
Flux needs to be bootstrapped into your Kubernetes cluster to begin monitoring repositories and deploying configurations.

### Step 1: Install Flux CLI
If not already installed:
```sh
curl -s https://fluxcd.io/install.sh | sudo bash
```
Verify installation:
```sh
flux --version
```

### Step 2: Bootstrap Flux
#### GitHub Bootstrap:
```sh
flux bootstrap github \
  --owner=<github-username-or-org> \
  --repository=<repo-name> \
  --branch=main \
  --path=clusters/my-cluster \
  --personal \
  --token-auth
```

#### GitLab Bootstrap:
```sh
flux bootstrap gitlab \
  --owner=<gitlab-username-or-group> \
  --repository=<repo-name> \
  --branch=main \
  --path=clusters/my-cluster \
  --token-auth
```

This command sets up Flux in your Kubernetes cluster, linking it to the specified repository, which it will watch for configuration changes.

## Creating a Repository for Application Configurations
To store and manage application configurations (e.g., OwnCloud), create a separate repository.

### Step 1: Create a Local Repository for App Configurations
```sh
mkdir -p flux-apps
cd flux-apps
```

### Step 2: Initialize a Git Repository
```sh
git init
```

### Step 3: Create a Folder for OwnCloud Configurations
```sh
mkdir owncloud
cd owncloud
```

### Step 4: Define the Kubernetes Manifests for OwnCloud
Inside the `owncloud` directory, create Kubernetes deployment and service manifests.

1. Create a `kustomization.yaml` file:
   ```yaml
   resources:
     - deployment.yaml
     - service.yaml
   ```

2. Create a basic `deployment.yaml` file:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: owncloud
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: owncloud
     template:
       metadata:
         labels:
           app: owncloud
       spec:
         containers:
           - name: owncloud
             image: owncloud:latest
             ports:
               - containerPort: 80
   ```

3. Create a `service.yaml` file:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: owncloud-service
   spec:
     selector:
       app: owncloud
     ports:
       - protocol: TCP
         port: 80
         targetPort: 80
   ```

### Step 5: Commit and Push the Configuration Repository
```sh
git add .
git commit -m "Initial commit with OwnCloud manifests"
git push origin main
```

### Step 6: Create flux secret 
#### Gitlab
```sh
flux create secret git flux-deploy-authentication \
  --url=https://gitlab.com/owner/votre_projet_de_deploiement \
  --namespace=flux-system \
  --username="$kube_deploy_user_access" \
  --password="$kube_deploy_token_access"
```

#### Github:
```sh
flux create secret git flux-deploy-authentication \
  --url=https://github.com/owner/votre_projet_de_deploiement \
  --namespace=flux-system \
  --username="$kube_deploy_user_access" \
  --password="$kube_deploy_token_access"
```

## Step 7: Kustomize your flux autodeploy
#### File location: your-repository/flux/microk8s-configuration.yaml
 ```yaml
 ---
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: GitRepository
metadata:
  name: flux-apps 
  namespace: flux-system
spec:
  interval: 1m0s
  ref:
    branch: main
  secretRef:
    name: flux-deploy-authentication
  url: url-de-votre-repos

---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: owncloud-apps
  namespace: flux-system
spec:
  interval: 1m0s
  path: ./owncloud
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-apps
    namespace: flux-system

```
