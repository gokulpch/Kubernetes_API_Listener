# Kubernetes_API_Listener
Problem definition: Build an agent that listens to kubernetes Policy definition via Kubernetes api server and programs the host iptable on which the container is running. The Demo video shows an operational work-flow.

## _Topology & Context_

![alt text](https://github.com/gokulpch/Kubernetes_API_Listener/blob/master/images/Topology.png)

###### Components:

* A single node Kubernetes cluster, tainted master to allow creation of workloads on the Master
* Calico is used as a CNI to provide Overlay networking to the Pods and Services
* A Service:NodePort is used to expose the service on the host port to provide connectivity to the pod from internet

###### Context:

* A user wants to control access to the Web app running on Kubernetes with IPTABLES/Net-Filters on the Host where the Pod is located. Nodeport, one of the default way that Kubernetes uses to expose the service to the internet using the host port (default-range: 30000-32767) is used in this scenario to expose the service to the internet.
* An agent snippet which constantly listens on EVENT's posted by Kube-API is used to capture the metadata output and seamlessly add the IPTABLE rules on the host getting the information from the K8's-Service whenever a Network-Policy (Ingress) with default-deny or deny is added to Kubernetes (default Network Policy object-K8's).

## _Demo_

* Audio Enabled. Click the image below to watch the video.

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/pDAgJVyHeDM/0.jpg)](https://youtu.be/pDAgJVyHeDM)


## _Kubernetes API_

* Kubernetes Provides API with various in-built functions to List, Create and Delete K8's objects.

A sample output of List_NetworkPolicies_AllNamespaces:

```
Event: ADDED default-deny policy-namespace {'match_expressions': None, 'match_labels': {u'name': 'apache-web'}}
{'raw_object': {u'kind': u'NetworkPolicy', u'spec': {u'policyTypes': [u'Ingress'], u'podSelector': {u'matchLabels': {u'name': u'apache-web'}}}, u'apiVersion': u'extensions/v1beta1', u'metadata': {u'name': u'default-deny', u'generation': 1, u'namespace': u'policy-namespace', u'resourceVersion': u'67166', u'creationTimestamp': u'2017-12-11T03:13:48Z', u'selfLink': u'/apis/extensions/v1beta1/namespaces/policy-namespace/networkpolicies/default-deny', u'uid': u'4df9a0af-de21-11e7-837b-047d7bb73c6a'}}, u'object': {'api_version': 'extensions/v1beta1',
 'kind': 'NetworkPolicy',
 'metadata': {'annotations': None,
              'cluster_name': None,
              'creation_timestamp': datetime.datetime(2017, 12, 11, 3, 13, 48, tzinfo=tzutc()),
              'deletion_grace_period_seconds': None,
              'deletion_timestamp': None,
              'finalizers': None,
              'generate_name': None,
              'generation': 1,
              'initializers': None,
              'labels': None,
              'name': 'default-deny',
              'namespace': 'policy-namespace',
              'owner_references': None,
              'resource_version': '67166',
              'self_link': '/apis/extensions/v1beta1/namespaces/policy-namespace/networkpolicies/default-deny',
              'uid': '4df9a0af-de21-11e7-837b-047d7bb73c6a'},
 'spec': {'egress': None,
          'ingress': None,
          'pod_selector': {'match_expressions': None,
                           'match_labels': {u'name': 'apache-web'}},
          'policy_types': ['Ingress']}}, u'type': u'ADDED'}
```

## _Procedure_

* Import necessary modules. Client enables the connection to the API endpoint, Config reads the authentication details from the cluster config, Watch constantly polls the information from Kubernetes_API, Subprocess is used to run shell command to add the IPtables, APIException is used for error/exception handling.

```
import os
import subprocess
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
```

* Read the kubernetes cluster authentication from the default location. This enables the code to procure the required admin authentication details.

```
config.load_kube_config(
    os.path.join(os.environ["HOME"], '.kube/config'))
```

* Declare the API objects/modules. Kubernetes has a beta module with added libraries.

```
v1 = client.CoreV1Api()
v1beta1 = client.ExtensionsV1beta1Api()
```

* Two streams are used in this scenario. One: watch Network_Policy creation in all namespaces and Two: watch Service creation in the particular namespace derived from Stream1.

```
stream1 = watch.Watch().stream(v1beta1.list_network_policy_for_all_namespaces)
stream2 = watch.Watch().stream(v1.list_namespaced_service, namespace)
```

* A For loop is used to constantly print the values of the objects when created.

```
for event in stream1:
    print("Event: %s %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace, event['object'].spec.pod_selector))
    hostport=event['object'].spec.ports[0].node_port


for event in stream2:
    print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].spec.ports[0].node_port))
    hostport=event['object'].spec.ports[0].node_port
```

* A conditional IF loop is used to capture the Object information when specific EVENTS occur. If the conditions are staisfied then a subprocess module is used to add the IPTABLES on the Host with the specific Port_Number derived from the Service. The same way the IPTABLES are deleted if the event type is DELETED.

```
if "deny" in event['object'].metadata.name and "ADDED" in event['type']:
        namespace=event['object'].metadata.namespace
        stream2 = watch.Watch().stream(v1.list_namespaced_service, namespace)
        for event in stream2:
            print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].spec.ports[0].node_port))
            hostport=event['object'].spec.ports[0].node_port
            print hostport
            command = "iptables -A INPUT -p tcp --destination-port %s -j DROP" %(hostport)
            print command
            subprocess.call(command, shell=True)
            break
        stream2.close()


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
```

## _Caveats and Limitations with the Solution_

The solution above depends on the label of the network_policy, the users have a hard constraint on creating a policy which should contain "default" in the policy_name (lack a logic to read the rule construct from the metadata) and may not be able to handle the multiple rule additions in specific cases.

Flannel, doesn't support network policy. Canal, Calico, Weave etc. provides support for network policy through a policy-controller where in users has to define a default-deny on the namespaces and provide specific rules in the network_policy to allow and dis-allow traffic:


The rule below will result in all traffic to all Pods in the Namespace to be denied.
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

In the case that you have publicly exposed a Service through Ingress and you have a default-deny policy in place or just want to limit that traffic to a specific ports.
```
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-external
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from: []
    ports:
    - port: 80
    - port: 8143
    - port: 8080
    - port: 9090
```

In this scenario the user is limiting a set of ports to allow the traffic from internet where in the calio policy-engine automatically adds these as IPTABLES on the host. When user is using a specific port as the NodePort it should be in one of the ports that a network policy contains and the containers in the namespace should have the ports in the list as container_ports.
```
'kind': 'NetworkPolicy',
 'metadata': {'annotations': None,
              'cluster_name': None,
              'creation_timestamp': datetime.datetime(2017, 12, 11, 10, 25, 8, tzinfo=tzutc()),
              'deletion_grace_period_seconds': None,
              'deletion_timestamp': None,
              'finalizers': None,
              'generate_name': None,
              'generation': 1,
              'initializers': None,
              'labels': None,
              'name': 'allow-external',
              'namespace': 'default',
              'owner_references': None,
              'resource_version': '95633',
              'self_link': '/apis/extensions/v1beta1/namespaces/default/networkpolicies/allow-external',
              'uid': '8fac8508-de5d-11e7-837b-047d7bb73c6a'},
 'spec': {'egress': None,
          'ingress': [{'_from': None,
                       'ports': [{'port': 80, 'protocol': 'TCP'},
                                 {'port': 8143, 'protocol': 'TCP'},
                                 {'port': 8080, 'protocol': 'TCP'},
                                 {'port': 9090, 'protocol': 'TCP'}]}],
          'pod_selector': {'match_expressions': None,
                           'match_labels': {u'app': 'web'}},
          'policy_types': ['Ingress']}}, u'type': u'ADDED'}
```

## _Enhanced Solution_

An enhanced solution should:

* Take the global network policy and namespaced network policy into account
* Should contain a logic which can get information of default_deny on the namespace
* A logic to associate the namespace deny rule with the global network_polcy object
* Use IPTABLE pyhton bindings to dynamically read multiple port information and program the same on the host
