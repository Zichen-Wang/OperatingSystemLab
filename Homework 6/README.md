# 第六次作业

## 阅读Paxos算法的材料并用自己的话简单叙述
 * 以下仅简述一下Paxos算法的流程，不做详细的证明。
 * 首先，整个分布式系统中，可以假设有三种角色：proposer，acceptor和learner。系统的核心目标是尽快达成一致，通过一项proposal。其中Learner只负责学习通过的proposal。而proposer可以提交proposal，acceptor负责审核通过proposal。每个结点可以扮演其中多个角色。

### proposal的选定
 * 本着先来后到的原则，每个proposal均有不同的编号，且编号大的proposal有更高的优先级。为了简单，假设每个proposal中包含一个value值。
 * 整个Paxos算法分为两个阶段：
  1. prepare阶段：
 * 1.1 proposer选择一个提案编号n，然后向acceptors的某个majority集合的成员发送编号为n的prepare请求。
 * 1.2 如果一个acceptor收到一个编号为n的prepare请求，且n大于它已经响应的所有prepare请求的编号，那么它就会保证不会再通过(accept)任何编号小于n的提案，同时将它已经通过的`最大`编号的提案(如果存在的话)作为响应。

  2. accpet阶段：
 * 2.1 如果proposer收到来自半数以上的acceptor对于它的prepare请求(编号为n)的响应，那么它就会发送一个针对编号为n，value值为v的提案的accept请求给acceptors，在这里v是收到的响应中编号`最大`的提案的值(value)，如果响应中不包含提案，那么它就是任意值。
 * 2.2 如果acceptor收到一个针对编号n的提案的accept请求，只要它还未对编号大于n的prepare请求作出响应，它就可以通过这个提案。
 * 需要注意，两个阶段中的同一个proposer发送的两次请求具有相同的编号。

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/paxos.png)
 * 可以简单描述为：proposer先从大多数acceptors那里学习提案的最新内容，然后根据学习到的编号最大的提案内容组成新的提案提交，如果提案获得大多数acceptors的投票通过就意味着提案被通过。
 * 由于学习提案和通过提案的acceptors集合都超过了半数，所以一定能学到最新通过的提案值，两次提案通过的acceptors集合中也一定存在一个公共的acceptor，在满足约束条件b时这个公共的acceptor时保证了数据的一致性，于是Paxos协议又被称为多数派协议。
 * 算法的本质便是：两个多数集合至少有一个公共成员。把全局信息存储在多数集合返回的统计结果上。

### learners获取被选定的value值
 * 为了获取被选定的值，一个learner必须确定一个提案已经被半数以上的acceptor通过。最明显的算法是，让每个acceptor，只要它通过了一个提案，就通知所有的learners，将它通过的提案告知它们。这可以让learners尽快的找出被选定的值，但是它需要每个acceptor都要与每个learner通信，所需通信的次数等于二者个数的乘积。
 * 可以利用以上的算法来让learner产生一个proposal，来快速确定accpetors是否已经选定了一个value。

### 防止产生活锁
 * 很容易发现，仅仅采用以上的算法无法保证能合理的选定一个proposal：在该情况下，两个proposers持续地生成编号递增的一系列proposal，但是没有proposal会被选定。Proposer p 为一个编号为n1的proposal完成了阶段1，然后另一个Proposer q 为编号为n2(n2 > n1)的proposal完成了阶段1。Proposer p 的针对编号n1的proposal的Phase2的所有accept请求被忽略，因为acceptors已经承诺不再通过任何编号小于n2的proposal。这样Proposer p 就会用一个新的编号n3(n3 > n2)重新开始并完成阶段1，这又会导致在阶段2里Proposer q 的所有accept请求被忽略，如此循环往复产生活锁。
 * 为了解决这个问题，需要`唯一`指定一个proposer来向大多数acceptors发送阶段2的请求。如果当前有其他proposer发送了更大编号的prepare请求，则被指定的proposer可以获取其proposal然后发送一个更大编号的prepare请求，保证不会发生活锁。


---

## 模拟Raft协议工作的一个场景并叙述处理过程
 * 首先启动5个节点的集群，初始状态下，集群所有节点初始化为follower状态，并随机产生一个倒计时。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_0.png)
---
 * 当某个结点倒计时结束后，他就认为此时master挂了，会变为candidate，并向其他结点发送vote。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_1.png)
---
 * 不幸的是，如果有多个结点在相近的时间成为candidate，有可能每个结点都收不到超过半数的投票，此时会继续等待一个随机倒计时。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_2.png)
---
 * 倒计时结束后，会变为candidate，开启新一轮投票，直到某个candidate收到超过半数的投票。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_3.png)
---
 * 选举出新的leader S1，任期是3。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_4.png)
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_5.png)
---
 * 所有客户端的请求都必须经过leader来进行，如果leader不存在，则集群无法进行get和put操作。写入的日志需要经过prepare和commit两个阶段。
 * 第一阶段，请求在leader写入后，下一次心跳会统计所有能接收到请求的follower，此时该请求没有写入任何节点包括leader的磁盘上。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_6.png)
---
 * 第二阶段，在收到超过一半结点的ACK之后，leader将该请求写到自己的磁盘上，然后在下一次心跳发送commit，让follower写入。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_7.png)
---
 * 如果挂掉的follower不超过集群结点的一半，则集群可以正常工作，在恢复后会立即得到同步的日志。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_8.png)
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_9.png)
 * 日志可以落后，但绝不会不一致。
---
 * 当leader挂了之后，随着其他follow结点的超时等待，会重新竞选leader，但leader只会在日志最多的follow结点中产生。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_10.png)
 * 新leader会逐渐让之前落后日志的follow追平日志。

---
 * 如果leader挂之前有了提交但未经过prepare阶段的日志，则新leader并不会care这些之前的请求，当原leader恢复后，也会清空这些请求，保持和新leader的日志一致。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_11.png)
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/raft_12.png)
 * 新leader结点会覆盖旧leader的uncommitted请求。

 * 以上图片均截图自网站[Raft Consensus Algorithm](https://raft.github.io/)。

---
## 简述Mesos的容错机制并验证
 * master结点的容错：master结点的状态仅仅为活跃slave、活跃的framework和运行中的task的列表。这些信息足够计算出每个框架使用多少资源以及分配策略。一旦某个master结点挂掉，那么运行中的task会继续在executor中运行，但新的task无法分配。Mesos使用热备份技术，运用ZooKeeper同时配置多个备份的master，当一个活跃的master宕机时，slave和scheduler可以连接到新被选举出的备份的master上，使其成为活跃的master。
 * slave或executor出现错误：Mesos将slave和executor崩溃信息发送到framework的调度器上，framework可以根据失败的信息来决定接下来的动作。
 * 调度器崩溃：Mesos允许一个框架注册多个调度器，当一个崩溃时，另一个将会被Mesos通知然后接管。这项工作需要有framework本身运用自己的算法来在多个scheduler上备份自己的状态。


### 安装配置zookeeper，实验Mesos的容错机制
 * 由于master挂掉的情况最为致命，而slave或executor出现错误是完全可以由framework本身接收并进行处理的，所以以下仅实验master结点宕机时，启动备份的master。
 * 下载zookeeper，直接从官网wget即可。
 * 分别修改三台主机zookeeper的配置文件
```
pkusei@oo-lab:~/zookeeper-3.4.10/conf$ cp zoo_sample.cfg zoo.cfg
pkusei@oo-lab:~/zookeeper-3.4.10/conf$ vi zoo.cfg
# 修改dataDir为
dataDir=/var/lib/zookeeper
# 添加以下内容
# master server
server.1=172.16.6.251:2888:3888
server.2=172.16.6.24:2888:3888
server.3=172.16.6.8:2888:3888
```
 * 在/var/lib/zookeeper/目录下创建myid文件，按照主机顺序写入1、2或3，在myid文件中配置的ID号必须与在zoo.cfg文件中指定的ID号一致
```
#1000
root@oo-lab:/home/pkusei/zookeeper-3.4.10# mkdir /var/lib/zookeeper
root@oo-lab:/home/pkusei/zookeeper-3.4.10# echo "1" > /var/lib/zookeeper/myid
#1001
root@oo-lab:/home/pkusei/zookeeper-3.4.10# mkdir /var/lib/zookeeper
root@oo-lab:/home/pkusei/zookeeper-3.4.10# echo "2" > /var/lib/zookeeper/myid
#1002
root@oo-lab:/home/pkusei/zookeeper-3.4.10# mkdir /var/lib/zookeeper
root@oo-lab:/home/pkusei/zookeeper-3.4.10# echo "3" > /var/lib/zookeeper/myid
```
 * 可以分别查看当前zookeeper集群的状态，为follower或者leader
```
pkusei@oo-lab:~/zookeeper-3.4.10$ bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /home/pkusei/zookeeper-3.4.10/bin/../conf/zoo.cfg
Mode: follower
```
 * 启动mesos_master，需要注意必须强制指定log_dir否则会出现错误，为了方便在web端查看，分别指定了端口号
```
nohup ./mesos-master.sh --zk=zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos \
--quorum=2 --ip=172.16.6.251 --port=5050 --cluster=mesos_with_zookeeper \
--hostname=162.105.174.39 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
> master.log 2>&1 &

nohup ./mesos-master.sh --zk=zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos \
--quorum=2 --ip=172.16.6.24 --port=6060 --cluster=mesos_with_zookeeper \
--hostname=162.105.174.39 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
> master.log 2>&1 &

nohup ./mesos-master.sh --zk=zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos \
--quorum=2 --ip=172.16.6.8 --port=7070 --cluster=mesos_with_zookeeper \
--hostname=162.105.174.39 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
> master.log 2>&1 &
```
 * 观察日志，可以看到172.16.6.251被选举为leading_master
```
I0512 11:29:54.610090 29936 contender.cpp:152] Joining the ZK group
I0512 11:29:54.611486 29922 master.cpp:1951] Successfully attached file '/var/log/mesos/lt-mesos-master.INFO'
I0512 11:29:54.616618 29938 contender.cpp:268] New candidate (id='4') has entered the contest for leadership
I0512 11:29:54.618340 29939 detector.cpp:152] Detected a new leader: (id='4')
I0512 11:29:54.619429 29939 group.cpp:697] Trying to get '/mesos/json.info_0000000004' in ZooKeeper
I0512 11:29:54.621386 29939 zookeeper.cpp:259] A new leading master (UPID=master@172.16.6.251:5050) is detected
I0512 11:29:54.621654 29939 master.cpp:2017] Elected as the leading master!    # *************
I0512 11:29:54.621700 29939 master.cpp:1560] Recovering from registrar
I0512 11:29:54.624681 29940 log.cpp:553] Attempting to start the writer
I0512 11:30:01.500174 29937 network.hpp:432] ZooKeeper group memberships changed
I0512 11:30:01.500725 29937 group.cpp:697] Trying to get '/mesos/log_replicas/0000000003' in ZooKeeper
I0512 11:30:01.503473 29937 group.cpp:697] Trying to get '/mesos/log_replicas/0000000004' in ZooKeeper
I0512 11:30:01.509407 29937 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.6.24:6060, log-replica(1)@172.16.6.251:5050 }
I0512 11:30:01.516458 29938 replica.cpp:493] Replica received implicit promise request from __req_res__(2)@172.16.6.251:5050 with proposal 58
I0512 11:30:01.520164 29938 replica.cpp:342] Persisted promised to 58
I0512 11:30:01.533937 29938 coordinator.cpp:238] Coordinator attempting to fill missing positions
I0512 11:30:01.535210 29939 log.cpp:569] Writer started with ending position 674
I0512 11:30:01.550254 29941 registrar.cpp:362] Successfully fetched the registry (924B) in 6.927803904secs
I0512 11:30:01.557935 29941 registrar.cpp:461] Applied 1 operations in 205553ns; attempting to update the registry
I0512 11:30:01.562288 29937 coordinator.cpp:348] Coordinator attempting to write APPEND action at position 675
I0512 11:30:01.566249 29943 replica.cpp:537] Replica received write request for position 675 from __req_res__(4)@172.16.6.251:5050
I0512 11:30:01.573554 29937 replica.cpp:691] Replica received learned notice for position 675 from @0.0.0.0:0
I0512 11:30:01.579977 29939 registrar.cpp:506] Successfully updated the registry in 21.918976ms
I0512 11:30:01.580322 29939 registrar.cpp:392] Successfully recovered registrar
I0512 11:30:01.581406 29942 coordinator.cpp:348] Coordinator attempting to write TRUNCATE action at position 676
I0512 11:30:01.584313 29937 replica.cpp:537] Replica received write request for position 676 from __req_res__(6)@172.16.6.251:5050
I0512 11:30:01.592535 29943 replica.cpp:691] Replica received learned notice for position 676 from @0.0.0.0:0
I0512 11:30:01.595165 29942 master.cpp:1676] Recovered 3 agents from the registry (929B); allowing 10mins for agents to re-register
I0512 11:30:06.163594 29942 network.hpp:432] ZooKeeper group memberships changed
I0512 11:30:06.163946 29942 group.cpp:697] Trying to get '/mesos/log_replicas/0000000003' in ZooKeeper
I0512 11:30:06.166087 29942 group.cpp:697] Trying to get '/mesos/log_replicas/0000000004' in ZooKeeper
I0512 11:30:06.168519 29942 group.cpp:697] Trying to get '/mesos/log_replicas/0000000005' in ZooKeeper
I0512 11:30:06.174268 29936 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.6.8:7070, log-replica(1)@172.16.6.24:6060, log-replica(1)@172.16.6.251:5050 }
```

```
I0512 11:30:01.523761 38958 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.6.24:6060, log-replica(1)@172.16.6.251:5050 }
I0512 11:30:01.525985 38961 replica.cpp:493] Replica received implicit promise request from __req_res__(1)@172.16.6.251:5050 with proposal 58
I0512 11:30:01.529628 38956 detector.cpp:152] Detected a new leader: (id='4')
```

```
I0512 11:30:06.180690 32771 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.6.24:6060, log-replica(1)@172.16.6.251:5050 }
I0512 11:30:06.188443 32769 detector.cpp:152] Detected a new leader: (id='4')
```
 * 分别在三个机子上各启动一个agent
```
nohup ./mesos-agent.sh --master=zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos --work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.6.251 --port=5051 \
--hostname=162.105.174.39 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &

nohup ./mesos-agent.sh --master=zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos --work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.6.24 --port=5052 \
--hostname=162.105.174.39 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &

nohup ./mesos-agent.sh --master=zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos --work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.6.8 --port=5053 \
--hostname=162.105.174.39 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &
```
 * 启动一个无限输出hello的样例framework
```
root@oo-lab:/home/pkusei/test_example# python scheduler.py zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos
```
* 在没有master错误的情况下，运行状态良好
```
root@oo-lab:/home/pkusei/test_example# python scheduler.py zk://172.16.6.251:2181,172.16.6.24:2181,172.16.6.8:2181/mesos
Scheduler running, Ctrl+C to quit.
DEBUG:root:Status update TID 422961a9-bbf1-446c-b499-ed0bc4c89413 TASK_RUNNING
DEBUG:root:Status update TID 757d48a9-c09f-4503-8f47-35fcf0d79306 TASK_RUNNING
DEBUG:root:Status update TID e292e9b1-56ea-4818-b312-367acacbe7da TASK_RUNNING
DEBUG:root:Status update TID 3f681a8a-92f6-4cb7-b188-c00ea9baf859 TASK_RUNNING
DEBUG:root:Status update TID ead238e0-f0fa-4245-96a5-a101ff004205 TASK_RUNNING
DEBUG:root:Status update TID 05dba2b4-f5fe-4cf7-af0c-e556e8a8cd80 TASK_RUNNING
DEBUG:root:Status update TID adf30ce2-c997-41ec-9588-ea7eddb7390e TASK_RUNNING
DEBUG:root:Status update TID 8a15f955-2ccf-4b01-a04e-ce52d14013d3 TASK_RUNNING
DEBUG:root:Status update TID cba0b0aa-f238-41e3-a7db-e6bb55366f69 TASK_RUNNING
DEBUG:root:Status update TID c4bb6648-217c-4c56-ab25-40bc1fd53549 TASK_RUNNING
DEBUG:root:Status update TID 46133bd4-58d2-430b-b171-091fae2d3bd8 TASK_RUNNING
DEBUG:root:Status update TID ec42f0c0-64d7-43ab-9db0-93f34fa6381f TASK_RUNNING
DEBUG:root:Status update TID ba9fbee6-5268-4e6d-a207-baf2ab0c65b0 TASK_RUNNING
DEBUG:root:Status update TID 45baefc6-6718-4396-b280-c51c2c083f91 TASK_RUNNING
DEBUG:root:Status update TID a81b51ee-dbb6-4ef0-8028-b16410abf9c6 TASK_RUNNING
DEBUG:root:Status update TID 08cd421e-6e30-40d1-ad29-834627c86591 TASK_RUNNING
DEBUG:root:Status update TID fd3d2b2c-93b3-4806-90b4-a9c36ed1bb2c TASK_RUNNING
DEBUG:root:Status update TID be1ad4d7-5cf3-42dd-90b4-8c32dd14acd0 TASK_RUNNING
DEBUG:root:Status update TID 422961a9-bbf1-446c-b499-ed0bc4c89413 TASK_FINISHED
DEBUG:root:Status update TID 757d48a9-c09f-4503-8f47-35fcf0d79306 TASK_FINISHED
DEBUG:root:Status update TID e292e9b1-56ea-4818-b312-367acacbe7da TASK_FINISHED
DEBUG:root:Status update TID ee81340b-d1ed-47a6-b43d-259fbd56b6b5 TASK_RUNNING
DEBUG:root:Status update TID 64e39042-794f-4768-8443-4814a35fb545 TASK_RUNNING
DEBUG:root:Status update TID 02c5583a-575d-4a64-bb3a-70fa8eb63668 TASK_RUNNING
DEBUG:root:Status update TID 3f681a8a-92f6-4cb7-b188-c00ea9baf859 TASK_FINISHED
...
```
 * 接下来stop掉172.16.6.251的master进程
```
root@oo-lab:# kill -SIGSTOP 29922
```
 * 观察新成为leading_master的日志
```
I0512 12:01:12.015262 38960 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.6.8:7070, log-replica(1)@172.16.6.24:6060 }
I0512 12:01:14.020196 38959 detector.cpp:152] Detected a new leader: (id='5')
I0512 12:01:14.020581 38959 group.cpp:697] Trying to get '/mesos/json.info_0000000005' in ZooKeeper
I0512 12:01:14.022831 38959 zookeeper.cpp:259] A new leading master (UPID=master@172.16.6.24:6060) is detected
I0512 12:01:14.023264 38959 master.cpp:2017] Elected as the leading master!
I0512 12:01:14.024456 38959 master.cpp:1560] Recovering from registrar
```

```
I0512 12:01:14.021719 32773 zookeeper.cpp:259] A new leading master (UPID=master@172.16.6.24:6060) is detected
I0512 12:01:14.023607 32768 master.cpp:2030] The newly elected leader is master@172.16.6.24:6060 with id c0b5ec15-d4a8-4265-8372-aa06d5a5c4c9
I0512 12:01:14.037674 32775 replica.cpp:493] Replica received implicit promise request from __req_res__(1)@172.16.6.24:6060 with proposal 59
I0512 12:01:14.039046 32775 replica.cpp:342] Persisted promised to 59
```
 * 他会从日志目录中恢复之前leading_master的日志，然后继续执行task，framework丝毫未受到影响。
 * 恢复172.16.6.251的master进程的执行，发现它找不到了新master，然后会自杀
```
I0512 12:05:36.977052 29938 master.cpp:2030] The newly elected leader is None
Lost leadership... committing suicide!
```
 * 需要重启挂掉的master进程才可以继续参与zookeeper，通常由守护进程来完成。需要重启原因是它被踢出了zookeeper的quorum，为了确保不在未知的状态下进行通信。


## 综合作业

### 容器入口程序
 * 首先要求将docker容器组成etcd集群，并且在etcd选举出的master结点上部署jupyter nodebook。这里我用python脚本作为docker容器的入口命令。 入口代码[start.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/code/start.py)的整体设计思路如下：
 1. 首先需要启动ssh服务，使用分布式文件系统目录共享authorized_keys，在后边会说到。
```python
def start_ssh():
    os.system('ssh-keygen -f /home/admin/.ssh/id_rsa -t rsa -N ""')
	  os.system('echo "admin" | sudo -S bash -c "cat /home/admin/.ssh/id_rsa.pub >> /ssh_info/authorized_keys"')
	  os.system('/usr/sbin/service ssh start')
```

 2. 启动etcd主进程，这里启动5个容器组成集群，ip地址分别为192.168.0.100到192.168.0.104
```python
def start_etcd(ip_addr):
    args = ['/usr/local/bin/etcd', '--name', 'node' + ip_addr[-1], \
    '--data-dir', '/var/lib/etcd', \
    '--initial-advertise-peer-urls', 'http://' + ip_addr + ':2380', \
    '--listen-peer-urls', 'http://' + ip_addr + ':2380', \
    '--listen-client-urls', 'http://' + ip_addr + ':2379,http://127.0.0.1:2379', \
    '--advertise-client-urls', 'http://' + ip_addr + ':2379', \
    '--initial-cluster-token', 'etcd-cluster-hw6', \
    '--initial-cluster', 'node0=http://192.168.0.100:2380,node1=http://192.168.0.101:2380,node2=http://192.168.0.102:2380,node3=http://192.168.0.103:2380,node4=http://192.168.0.104:2380', \
    '--initial-cluster-state', 'new']
    subprocess.Popen(args)
```

 3. 由于需要维护每个hosts表，需要etcd的kv对来记录当前集群的信息，然后更新hosts表。接下来以某个容器为例，来说明etcd启动后的工作流程：这里需要一个主循环，来持续向etcd集群发送消息，检查自己是否为leader。
 3.1. 如果是leader并且是第一次成为leader，先启动jupyter notebook，然后清理上次leader死掉后的在kv对中的/hosts目录，创建kv对/hosts/0192.168.0.10x -> 192.168.0.10x（这里使用0开头表示是leader）。在分布式kv对中更新/hosts目录的存活时间为30秒，这是为了如果有follower死掉，可以在30秒重新创建/hosts目录然后清除掉死掉的follower信息。
 3.2 如果是follower，则继续尝试创建kv对/hosts/192.168.0.10x -> 192.168.0.10x。
 3.3 经过试验，使用etcdctl mk命令不会重复创建kv对，也不会刷新/hosts目录的ttl剩余存活时间。
```python
def main():

	f = os.popen("ifconfig cali0 | grep 'inet addr' | cut -d ':' -f 2 | cut -d ' ' -f 1")
	ip_addr = f.read().strip('\n')

	start_ssh()
	start_etcd(ip_addr)

	leader_flag = 0
	watch_flag = 0
	stats_url = 'http://127.0.0.1:2379/v2/stats/self'
	stats_request = urllib.request.Request(stats_url)
	while True:
		try:
			stats_reponse = urllib.request.urlopen(stats_request)
		except urllib.error.URLError as e:
			print('[WARN] ', e.reason)
			print('[WARN] Wating etcd...')

		else:
			if watch_flag == 0:
				watch_flag = 1
				watch_dog(ip_addr)

			stats_json = stats_reponse.read().decode('utf-8')
			data = json.loads(stats_json)


			if data['state'] == 'StateLeader':
				if leader_flag == 0:
					leader_flag = 1

					args = ['/usr/local/bin/jupyter', 'notebook', '--NotebookApp.token=', '--ip=0.0.0.0', '--port=8888']
					subprocess.Popen(args)

					os.system('/usr/local/bin/etcdctl rm /hosts')
					os.system('/usr/local/bin/etcdctl mk /hosts/0' + ip_addr + ' ' + ip_addr)
					os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')
				else:
					os.system('/usr/local/bin/etcdctl mk /hosts/0' + ip_addr + ' ' + ip_addr)


			elif data['state'] == 'StateFollower':
				leader_flag = 0
				os.system('/usr/local/bin/etcdctl mk /hosts/' + ip_addr + ' ' + ip_addr)

		time.sleep(1)
```
 4. 同时，在这个主循环中，需要新启动一个守护进程来触发[watch.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/code/watch.py)，来监控/hosts目录的更新变化，检测到有新创建的kv对后，即使更新hosts文件。已经存在的kv对再创建时不会触发守护进程。
```python
def watch_dog(ip_addr):
	args = ['/usr/local/bin/etcdctl', 'exec-watch', '--recursive', '/hosts', '--', '/usr/bin/python3', '/home/admin/code/watch.py', ip_addr]
	subprocess.Popen(args)
```
 5. [watch.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/code/watch.py)部分细节如下，需要从环境变量中找到触发守护进程的信息。`expire`为/hosts目录存活时间到0并且当前容器时leader，则需要重新创建并且更新时间为30s；`create`为新创建的kv对，则更新hosts表，如果当前容器时follower则自己继续发送创建kv对的信息。
```python
def main(ip_addr):
	action = os.getenv('ETCD_WATCH_ACTION')

	stats_url = 'http://127.0.0.1:2379/v2/stats/self'
	stats_request = urllib.request.Request(stats_url)

	stats_reponse = urllib.request.urlopen(stats_request)
	stats_json = stats_reponse.read().decode('utf-8')
	data = json.loads(stats_json)

	print('[INFO] Processing', action)

	if action == 'expire':
		if data['state'] == 'StateLeader':
			os.system('/usr/local/bin/etcdctl mk /hosts/0' + ip_addr + ' ' + ip_addr)
			os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')

	elif action == 'create':
		edit_hosts()
		if data['state'] == 'StateFollower':
			os.system('/usr/local/bin/etcdctl mk /hosts/' + ip_addr + ' ' + ip_addr)
```
 6. 更新hosts表，这里通过编辑/etc/hosts文件来更改hosts。由于只有root用户才能直接编辑/etc/hosts，普通用户不可以，但可以通过完全复制或追加的方式更新。这里新创建/tmp/hosts文件，然后将其复制到/etc/hosts上。由于可能同时有多个创建信息到达，守护进程触发多个[watch.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/code/watch.py)进程，需要将/tmp/hosts加锁编辑防止冲突。
```python
def edit_hosts():
	f = os.popen('/usr/local/bin/etcdctl ls --sort --recursive /hosts')
	hosts_str = f.read()


	hosts_arr = hosts_str.strip('\n').split('\n')
	hosts_fd = open('/tmp/hosts', 'w')

    # acquire the lock
	fcntl.flock(hosts_fd.fileno(), fcntl.LOCK_EX)

	hosts_fd.write('127.0.0.1 localhost cluster' + '\n')
	i = 0
	for host_ip in hosts_arr:
		host_ip = host_ip[host_ip.rfind('/') + 1:]
		if host_ip[0] == '0':
			hosts_fd.write(host_ip[1:] + ' cluster-' + str(i) + '\n')
		else:
			hosts_fd.write(host_ip + ' cluster-' + str(i) + '\n')
		i += 1

	hosts_fd.flush()
	os.system('/bin/cp /tmp/hosts /etc/hosts')

    # release the lock automatically
	hosts_fd.close()
```
 * 到此容器入口代码就写好了，为了防止占用过多资源，会在主循环的每轮循环中睡眠1秒。

### 分布式存储
 * 我采用的是glusterfs分布式存储，在三个宿主机上开启glusterfs服务，然后创建共享目录，挂载到容器中的/home/admin/shared_folder中，此时shared_folder就是所有容器的共享目录，但需要sudo或者root权限可以往里写文件。

### ssh相互免密码登陆
 * ssh免密码登陆的原理：假设现在本机是A，目标机是B，则A需要在本地生成私钥id_rsa和公钥id_rsa.pub，然后将id_rsa.pub追加到B的authorized_keys中。这样A连接B时，B首先会检查authorized_keys中是否存在A机，如果存在则将A的私钥和该authorized_keys的条目进行比对，比对通过则给予免密登陆，不通过则需要密码。
 * 在本实验中，使用分布式文件系统glusterfs，创建共享目录和authorized_keys文件，在Dockerfile中修改sshd_config使sshd进程查找时找到该共享文件。
 * 对应入口程序的代码如下
```python
def start_ssh():
    # generate ssh private and public key
	os.system('ssh-keygen -f /home/admin/.ssh/id_rsa -t rsa -N ""')
    # add the public key to shared 'authorized_keys' file
	os.system('echo "admin" | sudo -S bash -c "cat /home/admin/.ssh/id_rsa.pub >> /ssh_info/authorized_keys"')
    # start ssh service
	os.system('/usr/sbin/service ssh start')
```

### Dockerfile
 * 下面是Dockerfile，由于每个容器都有可能成为master，故都采用相同的镜像。
```
FROM ubuntu:latest

MAINTAINER wzc

RUN apt update && apt install -y sudo python3-pip ssh net-tools curl vim
RUN pip3 install --upgrade pip && pip3 install jupyter

RUN useradd -ms /bin/bash admin && adduser admin sudo && echo 'admin:admin' | chpasswd
RUN mkdir /home/admin/first_folder

# 下载最新版etcd
RUN wget -P /root https://github.com/coreos/etcd/releases/download/v3.1.7/etcd-v3.1.7-linux-amd64.tar.gz && tar -zxf /root/etcd-v3.1.7-linux-amd64.tar.gz -C /root
RUN ln -s /root/etcd-v3.1.7-linux-amd64/etcd /usr/local/bin/etcd && ln -s /root/etcd-v3.1.7-linux-amd64/etcdctl /usr/local/bin/etcdctl

# 修改sshd配置文件
RUN mkdir /var/run/sshd
RUN echo 'AuthorizedKeysFile /ssh_info/authorized_keys' >> /etc/ssh/sshd_config

RUN echo 'The password is "admin" for user "admin" by default. There are 5 containers running as a cluster and the ip addresses of the cluster are "192.168.0.100", "192.168.0.101", "192.168.0.102", "192.168.0.103" and "192.168.0.104". The hostname of each node is "cluster-X", where "X" is from 0 to 4. The Internet access is available. You can install any software packages using "sudo apt". Contents in "shared_folder" can be accessed from any host.\n' > /home/admin/README.txt

# 导入入口地址代码，code目录和Dockerfile放在一起
ADD code/ /home/admin/code/

# 创建共享目录
RUN mkdir /home/admin/shared_folder

USER admin
WORKDIR /home/admin

# 入口进程
CMD ["/usr/bin/python3", "/home/admin/code/start.py"]
```

### 代理
 * 由于现在不确定master所在的容器以及宿主机，需要重写代理脚本。每个主机不断发送http请求查找etcd的master。如果master在1000上，则直接将其代理到1000机的8888端口。如果master在1001机或者1002机上，则不仅需要将其代理到相应主机的8888端口，1000机的代理还需要知道当前master在哪，将1001机或1002机的8888端口代理到自己1000机的8888端口。
 * [proxy_0.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/code/proxy_0.py)是提前运行在1000机上的代理脚本
```python
while True:
    # check if master is running on the 192.168.0.10x in 1000 host
	for i in range(5):
		stats_url = 'http://192.168.0.10' + str(i) + ':2379/v2/stats/self'
		stats_request = urllib.request.Request(stats_url)
		try:
			stats_reponse = urllib.request.urlopen(stats_request, timeout = 2)
		except (urllib.error.URLError, socket.timeout):
			print('[INFO] Node 192.168.0.10' + str(i), 'is not running on this host')
		else:
			stats_json = stats_reponse.read().decode('utf-8')
			data = json.loads(stats_json)
			if data['state'] == 'StateLeader':
				print('[INFO] Have found master: 192.168.0.10' + str(i))
				if last_master != i:

					if last_master != -1:
						last_pid.kill()

					args = ['/usr/local/bin/configurable-http-proxy', \
					'--default-target=http://192.168.0.10' + str(i) + ':8888', \
					'--ip=' + ip_addr, '--port=8888']
					last_pid = subprocess.Popen(args)
					last_master = i

				else:
					print('[INFO] Master has not changed')

    # check if master is running on 1001 host
	stats_url = 'http://172.16.6.24:8888'
	stats_request = urllib.request.Request(stats_url)
	try:
		stats_reponse = urllib.request.urlopen(stats_request, timeout = 2)
	except (urllib.error.URLError, http.client.RemoteDisconnected, socket.timeout):
		print('[INFO] Master is not running on host 172.16.6.24')
	else:
		print('[INFO] Have found master on: 172.16.6.24')
		if last_master != 5:

			if last_master != -1:
				last_pid.kill()

			args = ['/usr/local/bin/configurable-http-proxy', \
			'--default-target=http://172.16.6.24:8888', \
			'--ip=' + ip_addr, '--port=8888']
			last_pid = subprocess.Popen(args)
			last_master = 5


    # check if master is running on 1002 host
	stats_url = 'http://172.16.6.8:8888'
	stats_request = urllib.request.Request(stats_url)
	try:
		stats_reponse = urllib.request.urlopen(stats_request, timeout = 2)
	except (urllib.error.URLError, http.client.RemoteDisconnected, socket.timeout) as e:
		print('[INFO] Master is not running on host 172.16.6.8')
	else:
		print('[INFO] Have found master on: 172.16.6.8')
		if last_master != 6:

			if last_master != -1:
				last_pid.kill()

			args = ['/usr/local/bin/configurable-http-proxy', \
			'--default-target=http://172.16.6.8:8888', \
			'--ip=' + ip_addr, '--port=8888']
			last_pid = subprocess.Popen(args)
			last_master = 6


	sys.stdout.flush()
	time.sleep(5)
```
 * [proxy_1.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/code/proxy_1.py)是提前运行在1001机和1002机上的代理脚本，原理类似，只需要检查容器中是否有master即可。
 * 以nohup的形式在后台运行
```
pkusei@oo-lab:~/hw6$ nohup python3 proxy_0.py > proxy.log 2>&1 &
or
pkusei@oo-lab:~/hw6$ nohup python3 proxy_1.py > proxy.log 2>&1 &
```
### framework
 * 此时的framework就很好写了，直接改造第三次作业的framework，添加ip，hostname，volume和network的参数即可
```python
for offer in offers:
	cpus = self.getResource(offer.resources, 'cpus')
	mem = self.getResource(offer.resources, 'mem')
	if self.launched_task == TASK_NUM:
		return
	if cpus < TASK_CPU or mem < TASK_MEM:
		continue
	# ip
	ip = Dict()
	ip.key = 'ip'
	ip.value = '192.168.0.10' + str(self.launched_task)

	# hostname
	hostname = Dict()
	hostname.key = 'hostname'
	hostname.value = 'cluster'

	# volume1
	volume1 = Dict()
	volume1.key = 'volume'
	volume1.value = '/home/pkusei/hw6/ssh_docker:/ssh_info'

	# volume2
	volume2 = Dict()
	volume2.key = 'volume'
	volume2.value = '/home/pkusei/hw6/data_docker:/home/admin/shared_folder'


	# NetworkInfo
	NetworkInfo = Dict()
	NetworkInfo.name = 'my_net'

	# DockerInfo
	DockerInfo = Dict()
	DockerInfo.image = 'ubuntu_jupyter_etcd'
	DockerInfo.network = 'USER'
	DockerInfo.parameters = [ip, hostname, volume1, volume2]

	# ContainerInfo
	ContainerInfo = Dict()
	ContainerInfo.type = 'DOCKER'
	ContainerInfo.docker = DockerInfo
	ContainerInfo.network_infos = [NetworkInfo]

	# CommandInfo
	CommandInfo = Dict()
	CommandInfo.shell = False

	task = Dict()
	task_id = 'node' + str(self.launched_task)
	task.task_id.value = task_id
	task.agent_id.value = offer.agent_id.value
	task.name = 'Docker task'
	task.container = ContainerInfo
	task.command = CommandInfo

	task.resources = [
		dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
		dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
	]

	self.launched_task += 1
	driver.launchTasks(offer.id, [task], filters)
```
### 测试
 * 启动framework
```
pkusei@oo-lab:~/hw6$ nohup python scheduler.py 172.16.6.251 > scheduler.log 2>&1 &
```
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/tasks.png)

 * 查看162.105.174.39:8888
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/jupyter.png)

 * 在jupyter上通过新建Terminal，可以看到master的ip地址
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/master.png)

 * 查看hosts表，可以发现刚才master是cluster-0的hostname
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/hosts.png)

 * ssh免密相互登陆
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/ssh.png)

 * 在root或使用sudo可以往shared_folder里写入文件，在其他容器可以看到
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/shared.png)

 * 停止某个follower容器，稍等30秒左右，查看hosts表，对比可以发现hosts表会自动补全空缺
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/hosts_kill_follower.png)

 * 再次开启刚才的follower容器，可以发现集群hosts恢复原状
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/hosts_recover_follower.png)

 * 停止master容器，稍等30秒左右，查看hosts表
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/hosts_kill_master.png)

 * 再次开启之前的master容器，可以发现之前的容器作为follower再次加入集群
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%206/picture/hosts_recover_master.png)

 * 唯一的不足就是在停止了某个容器后，mesos就会报告该task变成failed，重新开启后也不会恢复。
