#!/bin/bash 

KUBECONFIG=~/.kube/cluster0:~/.kube/cluster1:~/.kube/cluster2:~/.kube/cluster3:~/.kube/cluster4:~/.kube/cluster5 kubectl config view --flatten > ~/.kube/config

for i in {0..5}
do
kubectl config rename-context k8s-admin-cluster$i@kubernetes cluster$i
done

# Install helm3
wget --tries=0 https://get.helm.sh/helm-v3.0.2-linux-amd64.tar.gz
tar xzvf helm-v3.0.2-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/
helm repo add stable https://kubernetes-charts.storage.googleapis.com/
helm repo update

# Deploy Prometheus
for i in {0..5}
do
kubectl config use-context cluster$i; kubectl create ns monitoring; helm install stable/prometheus-operator --generate-name --set grafana.service.type=NodePort --set prometheus.service.type=NodePort --set prometheus.prometheusSpec.scrapeInterval="5s" --namespace monitoring; kubectl config use-context cluster0
done

#Install helm2
wget --tries=0 https://get.helm.sh/helm-v2.16.1-linux-amd64.tar.gz
tar xzvf helm-v2.16.1-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm2

kubectl config use-context cluster0
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: tiller
    namespace: kube-system
EOF

helm2 init --service-account tiller

# Install kubefedctl
wget --tries=0 https://github.com/kubernetes-sigs/kubefed/releases/download/v0.1.0-rc6/kubefedctl-0.1.0-rc6-linux-amd64.tgz
tar xzvf kubefedctl-0.1.0-rc6-linux-amd64.tgz
mv kubefedctl /usr/local/bin/

# Add helm chart
sleep 30
kubectl config use-context cluster0
helm2 repo add kubefed-charts https://raw.githubusercontent.com/kubernetes-sigs/kubefed/master/charts

# Deploy KubeFed
helm2 install kubefed-charts/kubefed --name-template kubefed --version=0.1.0-rc6 --namespace kube-federation-system

# Join clusters
sleep 30
for i in {1..5}
do
kubefedctl join cluster$i --cluster-context cluster$i --host-cluster-context cluster0 --v=2
done

echo "DONE. Kubernetes Federation is setup."
