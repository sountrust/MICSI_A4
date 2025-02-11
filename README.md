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
