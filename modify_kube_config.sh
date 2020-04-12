#!/bin/bash

i=0
for cluster in "$@"
do
scp -oStrictHostKeyChecking=no mulugeta@$cluster:~/.kube/config ~/.kube/cluster$i
sed -i 's/kubernetes-admin/k8s-admin-cluster'$i'/g' ~/.kube/cluster$i
sed -i 's/name: kubernetes/name: cluster'$i'/g' ~/.kube/cluster$i
sed -i 's/cluster: kubernetes/cluster: cluster'$i'/g' ~/.kube/cluster$i
scp ~/.kube/cluster$i mulugeta@$1:~/.kube/
i=$((i+1))
done
