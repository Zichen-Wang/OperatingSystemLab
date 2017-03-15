# 第二次作业

## Mesos组成结构

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/architecture.jpg)

上图表明了Mesos的主要组成部分。Mesos架构主要由四部分组成：master、slave(agent)、Framework的scheduler和executor。外加一个故障恢复的zookeeper。

Master是整个系统的核心，主要任务是进行资源的分配，负责管理各个framework的scheduler和各个slave，slaves会定期向master汇报自己的资源情况，Master因此可以得到资源分配表来决定给每个运行框架提供多少的资源。资源的分配调度机制通过一个独立的`Allocation Module`的组件来完成，可以用户自己来写或者完善。Master存在单点故障的问题，该问题由zookeeper来启用备用机解决。

Slave负责不定期的接收并执行来自master的命令并管理节点上的任务，并为各个任务分配资源。Slave将自己的资源量发送给master。当用户的提交任务运行时，slave会将任务放到包含固定资源的`Linux Container`中运行，达到资源隔离的效果。

Framework是指外部的计算框架，如Spark、Hadoop、MPI等。这些框架可以通过注册的方式注册到Mesos来进行统一的管理和资源分配。这就要求这些框架提供一个scheduler模块，负责在框架和Master之间传递资源。先由master通过scheduler告诉框架有哪些资源可以用，这些资源再由外部框架决定是否接受，接收后使用自己的策略进行内部的任务分配，将各个任务分配好的结果通过scheduler返回给master进行提交运行。

Executor主要用于在slave上启动框架内部的任务。由于不同的框架，任务执行的接口和方式都不一样。当一个新的框架要接入mesos时，需要一个对应的executor，告诉mesos该如何启动任务。

下图是一个简单的Mesos资源调度步骤：
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/architecture-example.jpg)

 * Slave向master汇报自己的资源情况
 * master向scheduler发送可以提供的资源情况，让framework决定是否使用
 * framework决定使用该资源，并自行将资源分好，将描述交给master
 * master按照描述将资源落实到每个任务上执行

---
Master部分在`/path/to/mesos/src/master`下，`main.cpp`是入口程序，其内部会生成一个master对象，该对象开始监听信息。

Slave部分在`/path/to/mesos/src/slave`下，同样`main.cpp`是slave的入口程序，在处理完若干参数后会生成一个slave对象，该对象开始监听信息并发送状态给master对象。

MesosSchedulerDriver的启动模块在`/path/to/mesos/src/sched/sched.cpp`下，它创建一个scheduler的进程等待framework通过http的方式来注册，相当于给外部framework提供了一个接口。

MesosExecutorDriver的启动模块在`/path/to/mesos/src/exec/exec.cpp`下，同理它创建了一个executor进程等待framework通过http的方式注册。