import subprocess
from enoslib.api import discover_networks, play_on, generate_inventory,run_ansible,gather_facts
from enoslib.infra.enos_vmong5k.provider import VMonG5k
from enoslib.infra.enos_vmong5k.configuration import Configuration

import logging
import time

name = "kubefed-"

clusters = ["parapluie", "parapluie","econome", "chiclet", "dahu", "petitprince"]

logging.basicConfig(level=logging.DEBUG)

master_nodes = []

duration = "02:00:00"


for i in range(0, len(clusters)):

    name_job = name + clusters[i] + str(i)

    role_name = "cluster" + str(clusters[i])
    
    conf = Configuration.from_settings(job_name=name_job,
                                       walltime=duration,
                                       image="/grid5000/virt-images/debian9-x64-base.qcow2")\
                        .add_machine(roles=[role_name],
                                     cluster=clusters[i],
                                     number=6)\
                        .finalize()
    provider = VMonG5k(conf)

    roles, networks = provider.init()
    roles = discover_networks(roles, networks)

    inventory_file = "kubefed_inventory_cluster" + str(i) + ".ini" 

    inventory = generate_inventory(roles, networks, inventory_file)

    master_nodes.append(roles[role_name][0].address)

    # Make sure k8s is not already running
    run_ansible(["reset_k8s.yml"], inventory_path=inventory_file)
    # Deploy k8s and dependencies
    run_ansible(["deploy_k8s_clusters.yml"], inventory_path=inventory_file)

# Master nodes of all clusters
print("Master nodes ........")
print(master_nodes)

# Modify k8s conctext configurations to give them unique names
subprocess.check_call("./modify_kube_config.sh %s %s %s %s %s %s " % (master_nodes[0]), str(master_nodes[1]), str(master_nodes[2]), str(master_nodes[3]), str(master_nodes[4]), str(master_nodes[5])), shell=True)
# Setup Kubernetes Federation with Cluster 0 as the host cluster and the remaining clusters as members of the federation
run_ansible(["kubefed_init.yml"], inventory_path="kubefed_inventory_cluster0.ini")
