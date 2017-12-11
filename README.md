# Kubernetes_API_Listener

Contrail CNI-Kubernetes with Containarized Control Plane on AWS

## _Topology & Context_

![alt text](https://github.com/gokulpch/Kubernetes_API_Listener/blob/master/images/Topology.png)

###### Components:

* A single node Kubernetes cluster, tainted master to allow creation of workloads on the Master
* Calico is used as a CNI to provide Overlay networking to the Pods and Services
* A Service:NodePort is used to expose the service on the host port to provide connectivity to the pod from internet

###### Context:

* A user wants to control access to the Web app running on Kubernetes with IPTABLES/Net-Filters on the Host where the Pod is located. Nodeport, one of the default way that Kubernetes uses to expose the service to the internet using the host port (default-range: 30000-32767) is used in this scenario to expose the service to the internet.
* An agent snippet which constantly listens on EVENT's posted by Kube-API is used to capture the metadata output and seamlessly add the IPTABLE rules on the host getting the information from the K8's-Service whenever a Network-Policy (Ingress) with default-deny or deny is added to Kubernetes (default Network Policy object-K8's).

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
