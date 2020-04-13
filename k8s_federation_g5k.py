import subprocess
from enoslib.api import discover_networks, play_on, generate_inventory,run_ansible,gather_facts
from enoslib.infra.enos_vmong5k.provider import VMonG5k
from enoslib.infra.enos_vmong5k.configuration import Configuration

import logging
import time

name = "g5k-federation-1"

clusters = ["parapluie", "parapluie","econome", "chiclet", "dahu", "petitprince"]

logging.basicConfig(level=logging.DEBUG)

master_nodes = []

duration = "08:00:00"


for i in range(0, len(clusters)):

    name_job = name + clusters[i]

    role_name = "cluster" + str(clusters[i])
    
    if i == 0:
        node_type = "n2-standard-4"
    else:
        node_type = "rpi-4g"

    conf = Configuration.from_settings(job_name=name_job,
                                       walltime=duration,
                                       image="/home/mutamiru/k8s_base_image.qcow2")\
                        .add_machine(roles=[role_name],
                                     cluster=clusters[i],
                                     flavour=node_type,
                                     number=6)\
                        .finalize()
    provider = VMonG5k(conf)

    roles, networks = provider.init()
    roles = discover_networks(roles, networks)

    inventory_file = "kubefed_inventory_cluster" + str(i) + ".ini" 

    inventory = generate_inventory(roles, networks, inventory_file)


    master_nodes.append(roles[role_name][0].address)


    run_ansible(["/root/all_clusters.yml"], inventory_path=inventory_file)
    run_ansible(["reset-site.yaml"], inventory_path=inventory_file)
    config_file = "k8s-cluster-all.yml"
    run_ansible([config_file], inventory_path=inventory_file)

print("master nodes ........")
print(master_nodes)

# Modify k8s conctext configurations to give them unique names
#subprocess.check_call("./modify_kube_config.sh %s %s %s %s " % (master_nodes[0]), str(master_nodes[1]), str(master_nodes[2]),str(master_nodes[3])), shell=True)
subprocess.check_call("./modify_kube_config.sh " % (master_nodes), shell=True)
run_ansible(["kubefed_init.yml"], inventory_path="kubefed_inventory_cluster0.ini")
