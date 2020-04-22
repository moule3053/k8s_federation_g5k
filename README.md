# k8s_federation_g5k
Deploy Kubernetes Federation v2 on VMs in Grid5000

A python code and ansible playbook to deploy Kubernetes Federation v2 on Grid5000 VMs.

First, it deploys Kubernetes v1.14.0 on all clusters using kubeadm (very basic setup, nothing fancy).

Then using the `kubefed_init.sh` script, deploy Prometheus on each cluster, and then setup Kubernetes Federation v2 release v0.1.0-rc6.

Needs enoslib https://gitlab.inria.fr/discovery/enoslib

To run:
Replace relevant fields in the `k8s_federation_g5k.py` and run
`python3 k8s_federation_g5k.py`
