# k8s_federation_g5k
Deploy Kubernetes Federation v2 on Grid5000 hosts

A python code and ansible playbook to deploy Kubernetes Federation v2 on Grid5000 VMs.

First, deploys Kubernetes v1.14.0 on all clusters using kubeadm (very basic setup, nothing fancy).

Then using the `kubefed_init.sh` script, deploy Prometheus on each cluster, and then setup Kubernetes Federation v2 release v0.1.0-rc6.

Needs enoslib https://gitlab.inria.fr/discovery/enoslib
