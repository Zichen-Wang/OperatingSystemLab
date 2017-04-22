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

### 拒绝来自某一特定mac地址的访问
 * 查看服务器1001机网卡的mac地址为02:00:0d:4c:00:03，在1000服务器上键入以下命令：
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
 * 如果过滤掉本地网卡的MAC地址，则无法达到过滤的效果，仍然可以访问，原因是本地到服务器1000机经过了许多网络适配器，只能过滤掉最后一次hop中frame记录的适配器的源MAC地址。而局域网内1001机到1000机的连接只有一次hop，只通过一次ARP转换，故可以过滤掉。

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
root@oo-lab:/home/pkusei# iptables -L INPUT --line-numbers
Chain INPUT (policy DROP)
num  target     prot opt source               destination
1    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
```

### 
