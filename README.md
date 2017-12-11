# Kubernetes_API_Listener

Contrail CNI-Kubernetes with Containarized Control Plane on AWS


## _Context & Topology_

![alt text](https://github.com/gokulpch/Kubernetes_API_Listener/blob/master/images/Topology.png)

###### Components:

* A single node Kubernetes cluster, tainted master to allow creation of workloads on the Master
* Calico is used as a CNI to provide Overlay networking to the Pods and Services
* A Service:NodePort is used to expose the service on the host port to provide connectivity to the pod from internet




## _Requirements_

## _Procedure_
