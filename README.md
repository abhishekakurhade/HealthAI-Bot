# 🩺 HealthAI-Bot

A Streamlit-based AI health assistant (voice + text) powered by OpenRouter (`openai/gpt-3.5-turbo`), containerised with Docker and deployed to **Amazon EKS** through a **Jenkins CI/CD pipeline**.

> ⚠️ This bot is not a substitute for a doctor.

---

## 🏗️ Architecture

![Architecture](images/architecture.svg)

**Flow:** Developer pushes to GitHub → Jenkins (EC2) clones, builds and pushes the Docker image to Docker Hub → `kubectl apply` deploys to EKS → a Classic Load Balancer exposes the Streamlit app to users → the app calls the OpenRouter API for LLM responses.

---

## 🧰 Tech Stack

| Layer | Tool |
|---|---|
| App | Streamlit (Python) |
| LLM | OpenRouter API (`openai/gpt-3.5-turbo`) |
| Container | Docker, Docker Hub |
| CI/CD | Jenkins |
| Orchestration | Amazon EKS (created with `eksctl`) |
| Networking | VPC, Public/Private Subnets, IGW, NAT Gateway, Classic Load Balancer |
| Region | `ap-south-1` (Mumbai) |

---

## 🔄 Jenkins CI/CD Pipeline

The pipeline (`healthai-bot`, build #9) has four stages:

1. **Clone code** – checks out `main` from GitHub
2. **Build image** – `docker build -t $IMAGE:$TAG .`
3. **Push image** – pushes `healthai-bot:<BUILD_NUMBER>` to Docker Hub
4. **Deploy to EKS** – updates the image tag in `menifest/deployment.yml` with `sed`, applies `deployment.yml` and `service.yml`, then runs `kubectl rollout status deployment --timeout=120s`

![Jenkins Pipeline](images/jenkin-pipeline.jpg)

---

## ☸️ EKS Cluster & Kubernetes Resources

Cluster `cluster01` in `ap-south-1` with a managed node group (2 × `c7i-flex.large`). The deployment runs 2 replicas behind a `LoadBalancer` service (port 80 → NodePort 31439 → container port 8501).

![EKS Cluster](images/eks-cluster.jpg)

---

## 🖥️ EC2 Instances

Three instances are running: the Jenkins server (`healthai-project`, `m7i-flex.large`, ap-south-1c) and two EKS worker nodes (`c7i-flex.large`, ap-south-1a and ap-south-1b).

![EC2 Instances](images/instances.jpg)

---

## 📈 Auto Scaling Group

The EKS node group is backed by an Auto Scaling Group (min 2, desired 2, max 2) – 2/2 instances healthy.

![Auto Scaling Group](images/autoscaling.jpg)

---

## 🌐 VPC Network

`eksctl` created a VPC with 6 subnets (public + private in each of 1a, 1b, 1c), 5 route tables, an Internet Gateway and a NAT Gateway.

![VPC Workflow](images/vpc-workflow.jpg)

---

## ⚖️ Load Balancer

A Classic Load Balancer spanning 3 Availability Zones is created automatically by the Kubernetes `LoadBalancer` service.

![Load Balancer](images/load-balancer.jpg)

---

## 🚀 Live Application

The app is reachable through the load balancer DNS name. It offers a voice input ("Tap to Speak"), a text box, and optional info cards for Diet / Exercise / Symptoms.

![Application View](images/application-view.jpg)

---

## ▶️ Run Locally

```bash
git clone https://github.com/abhishekakurhade/HealthAI-Bot.git
cd HealthAI-Bot
pip install -r requirements.txt
export OPENROUTER_API_KEY=<your-key>
streamlit run app.py
```

## 🐳 Docker

```bash
docker build -t healthai-bot .
docker run -p 8501:8501 -e OPENROUTER_API_KEY=<your-key> healthai-bot
```

> Adjust file names / env variable names above to match your repo.

---

## ☁️ Install eksctl

Run these on the Jenkins/EC2 server (Ubuntu). The AWS CLI and `kubectl` must be installed and the server needs an IAM role (or `aws configure` credentials) with permissions for EKS, EC2, IAM and CloudFormation.

```bash
# Download and install eksctl
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz
sudo mv /tmp/eksctl /usr/local/bin

# Verify
eksctl version
```

---

## ☸️ Create EKS Cluster and Node Group

**1. Create the cluster (control plane + VPC, without worker nodes):**

```bash
eksctl create cluster \
  --name cluster01 \
  --region ap-south-1 \
  --without-nodegroup
```

**2. Create a managed node group (2 × c7i-flex.large):**

```bash
eksctl create nodegroup \
  --cluster cluster01 \
  --region ap-south-1 \
  --name node-group \
  --node-type c7i-flex.large \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 2 \
  --managed
```

**3. Connect kubectl to the cluster and verify:**

```bash
aws eks update-kubeconfig --name cluster01 --region ap-south-1

eksctl get cluster
eksctl get nodegroup --cluster cluster01
kubectl get nodes
```

**4. Deploy the app manually (Jenkins does this automatically on each build):**

```bash
kubectl apply -f menifest/deployment.yml -n default
kubectl apply -f menifest/service.yml -n default
kubectl get all
```

**Clean up (to avoid AWS charges):**

```bash
eksctl delete cluster --name cluster01 --region ap-south-1
```

---

## 👤 Author

**Abhishek Kurhade** – [GitHub](https://github.com/abhishekakurhade)
