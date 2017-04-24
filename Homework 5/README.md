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
网桥是工作在OSI链路层上的设备，与交换机类似，但它只有两个端口，可以将两个局域网连接起来组成一个大规模的局域网。早期的网桥通过MAC地址转换表来将网络包转发或者丢弃，后来的交换机是早期网桥的替代品，交换机也是通过MAC地址转换表将一个端口发来的包转发到另一个端口。

Linux网络设备中的Bridge与早期的网桥不太一样，Linux中的网桥可以直接从内核中接收一个数据包。网桥自身也有一个MAC地址，同时也可以设置一个IP地址，其连接着Linux内核。多个网卡（物理网卡或虚拟网卡）都可以attach到这个网桥上，然后这些网卡就会从网桥分配到新的IP地址，这些网卡之间也可以相互发送数据包，当某个网卡需要访问Internet时，则会通过网桥上的网关，通常为网桥的IP地址。当有Internet有数据包到来时，会到网桥上，然后由网桥根据MAC地址来转发数据包，Linux网络设备中的网桥很像一个的路由器。

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%205/picture/bridge.png)

如上图所示，br0是Linux中的网桥。现在有两个虚拟机，同时有两块虚拟网卡vnet0和vnet1，Host中的eth0是宿主机访问外网的物理网卡。将这三个网卡同时桥接到网桥br0上，宿主机和虚拟机以及虚拟机之间都可以互相通信。外网数据包可以发送到br0设备上，应用程序依然可以通过各个网卡获取数据包。

在VM等真实虚拟机环境中，vnet0和vnet1等虚拟网卡会分配和Host中eth0同样的IP地址段，相当于在Host的局域网中加入了2个新的设备，这样局域网内的所有设备都可以访问虚拟机。

但在docker容器中，docker0为宿主机默认的桥接卡，拥有MAC地址和IP地址，可以看做网卡，它将所有容器的虚拟网卡桥接在一起，形成一个子网。宿主机通过路由表可以访问到容器，容器之间可以通过网桥互相连通。宿主机从docker0子网中分配一个IP给容器使用，并设置docker0的IP地址为容器的默认网关。个人感觉这种方式很像NAT技术。
