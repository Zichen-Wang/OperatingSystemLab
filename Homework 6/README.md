# 第六次作业

## 阅读Paxos算法的材料并用自己的话简单叙述
 * 以下仅简述一下Paxos算法的流程，不做详细的证明。
 * 首先，整个分布式系统中，可以假设有三种角色：proposer，acceptor和learner。系统的核心目标是尽快达成一致，通过一项proposal。其中Learner只负责学习通过的proposal。而proposer可以提交proposal，acceptor负责审核通过proposal。每个结点可以扮演其中多个角色。

### proposal的选定
 * 本着先来后到的原则，每个proposal均有不同的编号，且编号大的proposal有更高的优先级。为了简单，假设每个proposal中包含一个value值。
 * 整个Paxos算法分为两个阶段：
  1. prepare阶段：
  1.1 proposer选择一个提案编号n，然后向acceptors的某个majority集合的成员发送编号为n的prepare请求。
  1.2 如果一个acceptor收到一个编号为n的prepare请求，且n大于它已经响应的所有prepare请求的编号，那么它就会保证不会再通过(accept)任何编号小于n的提案，同时将它已经通过的`最大`编号的提案(如果存在的话)作为响应。

  2. accpet阶段：
  2.1 如果proposer收到来自半数以上的acceptor对于它的prepare请求(编号为n)的响应，那么它就会发送一个针对编号为n，value值为v的提案的accept请求给acceptors，在这里v是收到的响应中编号`最大`的提案的值(value)，如果响应中不包含提案，那么它就是任意值。
  2.2 如果acceptor收到一个针对编号n的提案的accept请求，只要它还未对编号大于n的prepare请求作出响应，它就可以通过这个提案。
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
 * 在默认的/tmp/zookeeper/目录下创建myid文件，按照主机顺序写入1、2或3，在myid文件中配置的ID号必须与在zoo.cfg文件中指定的ID号一致
```
#1000
root@oo-lab:/home/pkusei/zookeeper-3.4.10# mkdir /var/lib/zookeeper
root@oo-lab:/home/pkusei/zookeeper-3.4.10# echo "1" > /tmp/zookeeper/myid
#1001
root@oo-lab:/home/pkusei/zookeeper-3.4.10# mkdir /var/lib/zookeeper
root@oo-lab:/home/pkusei/zookeeper-3.4.10# echo "2" > /tmp/zookeeper/myid
#1002
root@oo-lab:/home/pkusei/zookeeper-3.4.10# mkdir /var/lib/zookeeper
root@oo-lab:/home/pkusei/zookeeper-3.4.10# echo "3" > /tmp/zookeeper/myid
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

 *
