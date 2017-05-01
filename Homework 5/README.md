# 第五次作业

## Linux内核对IP数据包的处理

Linux下有很多网络数据控制工具，Netfilter是最知名最常用的一个。它在Linux内核中是一个软件框架，不仅具有网络地址转换（NAT）的功能，也具备数据包内容修改、以及数据包过滤等防火墙功能。利用运作于用户空间的应用软件，如iptable等，来控制Netfilter，系统管理者可以管理通过Linux操作系统的各种网络数据包。

iptables过滤ip数据包。这是netfilter提供的功能，netfilter将一些回调函数挂载到内核网络协议栈的网络层ip协议上，一旦有ip数据包经过，回调函数将拦截数据包并交由一系列函数处理，再决定该数据包的去留。而一系列Hooks的“挂载点”就是下面提到的规则链，下图展示了netfilter在网络层过滤ip数据包的简要流程：

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%205/picture/package-traversal-1.png)

刚刚收到的ip数据包将触发挂在PREROUTING上的回调函数，如果该节点的规则允许通过，将进行网络地址转换。然后是进行路由判断，如果是本机，则触发INPUT上的回调函数，通过过滤规则后，放行并进入本机上层协议栈；如果不是本机，则触发FORWARD上的回调函数，通过过滤规则和网络地址转换后，就进入POSTROUTING的处理阶段。由本机上层协议栈发出的数据包，需要经过路由判断下一个到达的网络节点，然后进行网络地址转换（因为初始的包源地址和目标地址相同需要重新设置目标地址）接着就和FORWARD过来的包一样，规则过滤，网络地址转换进入POSTROUTING阶段封包发出。

### iptables里的表

1. filter表 — 表示iptables的默认表，它具有三种内建链：
 * INPUT链：处理来自外部的数据。
 * OUTPUT链：处理向外发送的数据。
 * FORWARD链：将数据转发到本机的其他网卡设备上。

2. nat表 - nat表有三种内建链：
 * PREROUTING链：处理刚到达本机并在路由转发前的数据包，它会转换数据包中的目标IP地址。
 * POSTROUTING链：处理即将离开本机的数据包，它会转换数据包中的源IP地址。
 * OUTPUT链：处理本机产生的数据包。

---

## iptables功能测试

### 拒绝来自某一特定IP地址的访问
 * 查看本地的IP地址为10.2.67.113，在1000服务器上键入以下命令：
```
root@oo-lab:/# iptables -A INPUT -s 10.2.67.113 -j REJECT
```
 * ssh连接会立即挂断，所有从本地到1000服务器的web服务也均无法访问。
```
ssh: connect to host 162.105.174.39 port 1000: Connection refused
```

 * 从燕云或者其他IP地址登陆后查看iptables，INPUT链中有如下规则：
```
root@oo-lab:/# iptables -L INPUT --line-numbers
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination
1    REJECT     all  --  10.2.67.113          anywhere             reject-with icmp-port-unreachable
```
 * 这条规则会拒绝来自IP地址为10.2.67.113的数据包。
 * 删除刚定义的规则，恢复10.2.67.113的访问：
```
root@oo-lab:/# iptables -D INPUT 1 （1为规则编号)
或者
root@oo-lab:/# iptables -D INPUT -s 10.2.67.113 -j REJECT
```
 * 因为在同一北大局域网内，数据包的源IP地址并没有经过NAT转换而改变，故可以过滤掉本机的IP。

### 拒绝来自某一特定MAC地址的访问
 * 查看服务器1001机网卡的MAC地址为02:00:0d:4c:00:03，在1000服务器上键入以下命令：
```
root@oo-lab:/# iptables -A INPUT -m mac --mac-source 02:00:0d:4c:00:03 -j REJECT
```
 * 从1001机无法ssh登陆到1000机，也无法ping通1000机。
 * 查看1000机的iptables，INPUT链中有如下规则：
```
root@oo-lab:/# iptables -L INPUT --line-numbers
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination
1    REJECT     all  --  anywhere             anywhere             MAC 02:00:0D:4C:00:03 reject-with icmp-port-unreachable
```
 * 这条规则会拒绝来自网卡MAC地址02:00:0d:4c:00:03的数据包。
 * 删除刚定义的规则，恢复02:00:0d:4c:00:03的访问：
```
root@oo-lab:/# iptables -D INPUT 1
```
 * 如果过滤掉本地网卡的MAC地址，则无法达到过滤的效果，仍然可以访问，原因是本地到服务器1000机经过了许多广播域，但只能过滤掉最后一次传输的广播域中frame记录的源MAC地址。而局域网内1001机到1000机在同一广播域，故可以过滤掉。

### 只开放本机的http服务，其余协议与端口均拒绝
 * 在服务器1000机上键入以下命令：
```
root@oo-lab:/# iptables -A INPUT -p tcp --dport 80 -j ACCEPT
root@oo-lab:/# iptables -P INPUT DROP
```
 * 先添加过滤规则，使得http服务可以通过，然后设置默认规则为DROP。
 * 此时可以访问1000机的80端口，其他端口均无法访问。
 * 通过燕云查看1000机的iptables，INPUT链中有如下规则：
```
root@oo-lab:/# iptables -L INPUT --line-numbers
Chain INPUT (policy DROP)
num  target     prot opt source               destination
1    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
```
 * 在燕云上恢复原状：
```
root@oo-lab:/# iptables -P INPUT ACCEPT
root@oo-lab:/# iptables -D INPUT 1
```

### 拒绝回应来自某一特定IP地址的ping命令
 * 在服务器1000机上键入以下命令：
```
root@oo-lab:/# iptables -A INPUT -p icmp --icmp-type 8 -s 172.16.6.24 -j REJECT
```
 * ping命令通过向目标主机发送`Internet Control Message Protocol (ICMP)`的Echo请求包和等待ICMP的Echo响应来操作，所以如上的规则可以禁止1001机向1000机ping。
 * 效果如下：
```
root@oo-lab:/# ping 172.16.6.251
PING 172.16.6.251 (172.16.6.251) 56(84) bytes of data.
From 172.16.6.251 icmp_seq=1 Destination Port Unreachable
From 172.16.6.251 icmp_seq=2 Destination Port Unreachable
From 172.16.6.251 icmp_seq=3 Destination Port Unreachable
^C
--- 172.16.6.251 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2000ms
```
 * 恢复原状：
```
root@oo-lab:/# iptables -D INPUT 1
```

---

## Linux网络设备工作原理

### Bridge
网桥是工作在OSI链路层上的设备，只有两个端口，可以将两个局域网隔离连接起来组成一个大规模的局域网。早期的网桥通过学习得到的MAC地址转换表来将网络包转发或者丢弃。后来的交换机是早期网桥的替代品，拥有多个端口，交换机也是通过MAC地址转换表将一个端口发来的包转发到另一个端口。

Linux内核支持的网桥与单纯的物理网桥或交换机不同，交换机仅仅是一个二层设备，对于接收到的报文，要么转发广播，要么丢弃。而Linux内核的机器本身就是一台主机，有可能就是数据包的目标。其接收到的数据包不仅可以转发广播，也有可能向上传送到Linux网络协议栈，从而交给上层的应用程序。Linux内核是通过一个虚拟的网桥设备来实现桥接的，这个虚拟设备可以绑定若干个以太网接口设备，从而将它们桥接起来。

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%205/picture/bridge.jpg)

如上图所示，网桥设备br0绑定了eth0和eth1。对于网络协议栈的上层来说，只看得到br0，因为桥接是在数据链路层实现的，上层不需要关心桥接的细节。于是协议栈上层需要发送的数据包被送到br0，网桥设备的处理代码再来判断数据包该被转发到eth0或是eth1，或者两者皆是；反过来，从eth0或从eth1接收到的数据包被提交给网桥的处理代码，在这里会判断报文该转发、丢弃、或提交到上层协议栈。

如果设置网桥仅用来交换数据，那么可以不用设置IP地址。如果设置网桥需要与主机通信或者与Internet通信，则需要分配IP地址，并在主机中设置相应的路由表。例如，在Docker容器中，主机docker0的IP地址为172.17.0.1，作为网关使用，而各个容器的虚拟网卡的IP地址段就是172.17.0.0/24，网桥可以看做网关，容器可以通过网桥访问Internet，主机也可以和网桥上的设备双向通信。

### VLAN设备
VLAN设备主要是构造相互隔离的虚拟局域网络，使用虚拟化技术，可以将一个母设备的网卡虚拟出若干个子设备，子设备之间相互隔离，只能向母设备发送数据。以Linux中的802.1.q VLAN设备为例，母设备相当于现实世界中的交换机Trunk端口，用于连接上级网络，子设备相当于普通接口用于连接下级网络。当数据在母子设备间传递时，内核将会根据802.1.q VLAN Tag进行对应操作。母子设备之间是一对多的关系，一个母设备可以有多个子设备，一个子设备只有一个母设备。当一个子设备有一包数据需要发送时，数据将被加入VLAN Tag然后从母设备发送出去。当母设备收到一包数据时，它将会分析其中的VLAN Tag，如果有对应的子设备存在，则把数据转发到那个子设备上并根据设置移除VLAN Tag，否则丢弃该数据。

这里的数据流有方向，当母设备主动请求发送数据时，数据并不会向子设备发送；同理子设备接收到的数据不会再进入母设备。可以把VLAN母子设备作为一个整体想象为现实世界中的802.1.q交换机，下级接口通过子设备连接到寄主Linux系统网络里，上级接口同过母设备连接到上级网络，当母设备是物理网卡时上级网络是外界真实网络，当母设备是另外一个Linux虚拟网络设备时上级网络仍然是寄主Linux系统网络。

需要注意的是母子VLAN设备拥有相同的MAC地址，可以把它当成现实世界中802.1.q交换机的MAC，因此多个VLAN设备会共享一个MAC。当一个母设备拥有多个 VLAN子设备时，子设备之间是隔离的，不存在Bridge那样的交换转发关系。如果子设备间想要交换数据，就需要将子设备attach到bridge上。

### TAP设备
TAP设备是一种让用户态程序向内核协议栈注入数据的设备。当一个TAP设备被创建时，在Linux设备文件目录下将会生成一个对应char设备，用户程序可以像打开普通文件一样打开这个文件进行读写。当执行write()操作时，数据进入TAP设备，此时对于Linux网络层来说，相当于TAP设备收到了一包数据，请求内核接受它，如同普通的物理网卡从外界收到一包数据一样，不同的是其实数据来自Linux上的一个用户程序。Linux收到此数据后将根据网络配置进行后续处理，从而完成了用户程序向Linux内核网络层注入数据的功能。当用户程序执行read()请求时，相当于向内核查询TAP设备上是否有需要被发送出去的数据，有的话取出到用户程序里，完成TAP设备的发送数据功能。

利用TAP设备可以实现虚拟机的虚拟网卡功能，在宿主机内核中创建虚拟网卡，并且用TAP设备连接到用户态应用程序中的虚拟机中的虚拟网卡，他们之间相互连接。虚拟机应用程序通过read()/write()操作，和本机网络核心进行通讯。

### VETH设备
VETH设备和TAP设备比较类似，它是一种成对出现的点对点网络设备，从一端输入的数据会到达另一端。VETH从名字上来看是Virtual ETHernet的缩写，它的作用很简单，就是要把从一个网络域发出的数据包转发到另一个域。容器技术采用的是VETH设备，一个在容器之中，另一个在容器之外，即在宿主机上能看到的。

---

## Calico容器网络的收发数据包的过程

### 配置一个最简单的Calico集群为例来说明数据包的传输过程

 * etcd是用来监控集群状态的一个后台程序，时刻检测集群是否运行在正确的状态上。
 * 使用apt分别在三台主机上安装etcd，并使用service命令关掉自动开启etcd后台程序。
```
root@oo-lab:/# apt install etcd
...
root@oo-lab:/# service etcd stop
```
 * 分别在三台主机上添加如下命令来创建etcd集群环境
```
etcd --name node0 --initial-advertise-peer-urls http://172.16.6.251:2380 \
--listen-peer-urls http://172.16.6.251:2380 \
--listen-client-urls http://172.16.6.251:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://172.16.6.251:2379 \
--initial-cluster-token etcd-cluster-hw5 \
--initial-cluster node0=http://172.16.6.251:2380,node1=http://172.16.6.24:2380,node2=http://172.16.6.8:2380 \
--initial-cluster-state new
```

```
etcd --name node1 --initial-advertise-peer-urls http://172.16.6.24:2380 \
--listen-peer-urls http://172.16.6.24:2380 \
--listen-client-urls http://172.16.6.24:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://172.16.6.24:2379 \
--initial-cluster-token etcd-cluster-hw5 \
--initial-cluster node0=http://172.16.6.251:2380,node1=http://172.16.6.24:2380,node2=http://172.16.6.8:2380 \
--initial-cluster-state new
```

```
etcd --name node2 --initial-advertise-peer-urls http://172.16.6.8:2380 \
--listen-peer-urls http://172.16.6.8:2380 \
--listen-client-urls http://172.16.6.8:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://172.16.6.8:2379 \
--initial-cluster-token etcd-cluster-hw5 \
--initial-cluster node0=http://172.16.6.251:2380,node1=http://172.16.6.24:2380,node2=http://172.16.6.8:2380 \
--initial-cluster-state new
```
 * 检查配置状态：在任何一台主机上检查均可
```
root@oo-lab:/# etcdctl cluster-health
member a8d6151f6d1ce8cf is healthy: got healthy result from http://172.16.6.24:2379
member d73533619b65f9ed is healthy: got healthy result from http://172.16.6.8:2379
member e975c267eac0b1bc is healthy: got healthy result from http://172.16.6.251:2379
cluster is healthy
```
 * 在三台主机上修改docker daemon，使docker支持etcd。注意，如果之前启动过其他集群网络，需要先关闭。例如如果启动过swarm集群，则需要在每个主机上退出该网络`docker swarm leave --force`，然后再配置docker daemon。
```
root@oo-lab:/# service docker stop    # 停止后台的docker服务
root@oo-lab:/# dockerd --cluster-store etcd://172.16.6.251:2379 &
# 在后台启动docker daemon，不需要再使用service
```
 * 在三台主机上安装Calico，按照官网步骤即可
```
root@oo-lab:/# wget -O /usr/local/bin/calicoctl https://github.com/projectcalico/calicoctl/releases/download/v1.1.3/calicoctl
root@oo-lab:/# chmod +x /usr/local/bin/calicoctl
```
 * 分别启动Calico容器，注意需要指定ip和name
```
root@oo-lab:/# calicoctl node run --ip 172.16.6.251 --name node0
```
 * 检查启动情况
```
root@oo-lab:/# calicoctl node status
Calico process is running.

IPv4 BGP status
+--------------+-------------------+-------+----------+-------------+
| PEER ADDRESS |     PEER TYPE     | STATE |  SINCE   |    INFO     |
+--------------+-------------------+-------+----------+-------------+
| 172.16.6.24  | node-to-node mesh | up    | 10:12:10 | Established |
| 172.16.6.8   | node-to-node mesh | up    | 10:11:51 | Established |
+--------------+-------------------+-------+----------+-------------+

IPv6 BGP status
No IPv6 peers found.
```
 * 创建Calico的IP池，只需在某一台主机上。192.0.2.0/24为拥有256个ip地址的子网
```
root@oo-lab:/# cat << EOF | calicoctl create -f -
- apiVersion: v1
  kind: ipPool
  metadata:
    cidr: 192.0.2.0/24
EOF
```
 * 创建驱动为calico的docker网络，只需在某一台主机上
```
root@oo-lab:/# docker network create --driver calico --ipam-driver calico-ipam --subnet=192.0.2.0/24 my_net
```
 * 在三个主机上分别创建测试容器
```
root@oo-lab:/# docker run -it --net my_net --name test_calico_0 --ip 192.0.2.100 ubuntu_with_ip /bin/bash
```
```
root@oo-lab:/# docker run -it --net my_net --name test_calico_1 --ip 192.0.2.101 ubuntu_with_ip /bin/bash
```
```
root@oo-lab:/# docker run -it --net my_net --name test_calico_2 --ip 192.0.2.102 ubuntu_with_ip /bin/bash
```
 * 进行ping测试
```
root@cb67426d00da:/# ping 192.0.2.102 -c 4
PING 192.0.2.102 (192.0.2.102): 56 data bytes
64 bytes from 192.0.2.102: icmp_seq=0 ttl=62 time=0.679 ms
64 bytes from 192.0.2.102: icmp_seq=1 ttl=62 time=0.484 ms
64 bytes from 192.0.2.102: icmp_seq=2 ttl=62 time=0.312 ms
64 bytes from 192.0.2.102: icmp_seq=3 ttl=62 time=0.384 ms
--- 192.0.2.102 ping statistics ---
4 packets transmitted, 4 packets received, 0% packet loss
round-trip min/avg/max/stddev = 0.312/0.465/0.679/0.138 ms
```
 * 至此Calico的初步尝试搭建工作已经完成。
 * 默认情况下，在同一网络中的容器可以互通，在不同网络中的容器则不可以互通。

### 数据包的传输
 * Calico的原理是通过修改每个主机节点上的iptables和路由表规则，实现容器间数据路由和访问控制，并通过Etcd协调节点配置信息的。因此Calico服务本身和许多分布式服务一样，需要运行在集群的每一个节点上。

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%205/picture/calico.png)

 * Felix:Calico Agent，跑在每台需要运行Workload的节点上，主要负责配置路由及ACLS等信息来确保Endpoint的连通状态。

 * etcd:分布式键值存储，主要负责网络元数据一致性，确保Calico网络状态的准确性。

 * BGP Client (BIRD): 主要负责把Felix写入Kernel的路由信息分发到当前Calico网络，确保Workload间的通信的有效性。

 * BGP Route Reflector (BIRD)：大规模部署时使用，摒弃所有节点互联的mesh模式，通过一个或者多个BGP Route Reflector来完成集中式的路由分发。


 * 每当创建一个新的docker容器的Calico网络，Calico系统便会自动维护Kernel的路由表，添加数据包的转发规则。
```
root@oo-lab:/# ip route
...
blackhole 192.0.2.64/26  proto bird
192.0.2.100 dev calic1364fb7922  scope link
192.0.2.101 via 172.16.6.24 dev ens32  proto bird
192.0.2.102 via 172.16.6.8 dev ens32  proto bird
...
```
 * 同时我又创建运行了新的容器ip为192.2.0.200，则路由表也会跟着变化
```
root@oo-lab:/# ip route
...
blackhole 192.0.2.64/26  proto bird
192.0.2.100 dev calic1364fb7922  scope link
192.0.2.101 via 172.16.6.24 dev ens32  proto bird
192.0.2.102 via 172.16.6.8 dev ens32  proto bird
blackhole 192.0.2.192/26  proto bird
192.0.2.200 dev calic46e85858c2  scope link
...
```
 * 整个数据流也非常的清晰和简单
```
container 1 -> veth -> (172.16.6.251)host 1 -> one or more hops -> (172.16.6.24)host 2 -> veth -> (calicxxxx)container 2
```
 * 这样，跨主机的容器间通信就建立起来了，而且整个数据流中没有NAT、隧道，不涉及封包和拆包。

## 调研另一种容器网络方案，比较其与Calico的优缺点。

### Weave

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%205/picture/weave.png)

如上图所示，在每一个部署Docker的主机（可能是物理机也可能是虚拟机）上都部署有一个W（即Weave router，它本身也可以以一个容器的形式部署）。Weave网络是由这些weave routers组成的对等端点（peer）构成，每个对等的一端都有自己的名字，其中包括一个可读性好的名字用于表示状态和日志的输出，一个唯一标识符用于运行中相互区别，即使重启Docker主机名字也保持不变，这些名字默认是mac地址。

Weave创建一个网桥，并且在网桥和每个容器之间创建一个veth对，Weave run的时候就可以给每个veth的容器端分配一个ip和相应的掩码。veth的网桥这端就是Weave router容器，并在Weave launch的时候分配好ip和掩码。

Weave router学习获取MAC地址对应的主机，结合这个信息和网络之间的拓扑关 系，可以帮助router做出判断并且尽量防止将每个包都转发到每个对端。Weave可以在拓扑关系不断发生变化的部分连接的网络进行路由。

### Calico与Weave比较
#### Calico优势
 * 基于iptable/linux kernel包转发效率高，损耗低。
 * 容器间网络三层隔离。
 * 网络拓扑直观易懂，平行式扩展，可扩展性强。

#### Calico劣势
 * Calico仅支持TCP, UDP, ICMP andICMPv6协议。
 * Calico没有加密数据路径。 用不可信网络上的Calico建立覆盖网络是不安全的。
 * 没有IP重叠支持。

#### Weave优势
 * 支持主机间通信加密。
 * 支持跨主机多子网通信。

#### Weave劣势
 * 网络封装是一种传输开销，对网络性能会有影响，不适用于对网络性能要求高的生产场景。
