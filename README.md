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




## _Requirements_

## _Procedure_
