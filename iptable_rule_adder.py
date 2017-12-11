#!/usr/bin/python

import os
import subprocess
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

## Read the authentication details from the Config file on the Kubernetes Host
config.load_kube_config(
    os.path.join(os.environ["HOME"], '.kube/config'))

## Use v1beta1 which includes network_policy related modules
v1 = client.CoreV1Api()
v1beta1 = client.ExtensionsV1beta1Api()


## Watch for Network_Policy objects
stream1 = watch.Watch().stream(v1beta1.list_network_policy_for_all_namespaces)
for event in stream1:
    ## Print the required fields from the output
    print("Event: %s %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace, event['object'].spec.pod_selector))
    ## Trigger the action when the event type is added and the metadata label contains deny in it
    if "deny" in event['object'].metadata.name and "ADDED" in event['type']:
        ## Get the namespace details to provide in the next step
        namespace=event['object'].metadata.namespace
        print namespace
        ## Watch for the namespace information when the first clause is present
        stream2 = watch.Watch().stream(v1.list_namespaced_service, namespace)
        for event in stream2:
            print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].spec.ports[0].node_port))
            ## Get the nodeport details to provide in the iptables rule
            hostport=event['object'].spec.ports[0].node_port
            print hostport
            ## Add IPtables 
            command = "iptables -A INPUT -p tcp --destination-port %s -j DROP" %(hostport)
            print command
            subprocess.call(command, shell=True)
            break
        stream2.close()
    ## Delete the IPtables when the  event type is Deleted
    if "DELETED" in event['type']:
        namespace=event['object'].metadata.namespace
        print namespace
        stream2 = watch.Watch().stream(v1.list_namespaced_service, namespace)
        for event in stream2:
            print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].spec.ports[0].node_port))
            hostport=event['object'].spec.ports[0].node_port
            print hostport
            command = "iptables -D INPUT -p tcp --destination-port %s -j DROP" %(hostport)
            print command
            subprocess.call(command, shell=True)
            break
        stream2.close()
