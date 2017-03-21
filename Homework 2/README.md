# 第二次作业

## Mesos组成结构

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/architecture.jpg)

上图表明了Mesos的主要组成部分。Mesos架构主要由四部分组成：master、slave(agent)、Framework的scheduler和executor。外加一个故障恢复的zookeeper。

Master是整个系统的核心，主要任务是进行资源的分配，负责管理各个framework的scheduler和各个slave，slaves会定期向master汇报自己的资源情况，Master因此可以得到资源分配表来决定给每个运行框架提供多少的资源。资源的分配调度机制通过一个独立的`Allocation Module`的组件来完成，可以用户自己来写或者完善。Master存在单点故障的问题，该问题由zookeeper来启用备用机解决。

Slave负责不定期的接收并执行来自master的命令并管理节点上的任务，并为各个任务分配资源。Slave将自己的资源量发送给master。当用户的提交任务运行时，slave会将任务放到包含固定资源的`Linux Container`中运行，达到资源隔离的效果。

Framework是指外部的计算框架，如Spark、Hadoop、MPI等。这些框架可以通过注册的方式注册到Mesos来进行统一的管理和资源分配。这就要求这些框架提供一个scheduler模块，负责在框架和Master之间传递资源。先由master通过scheduler告诉框架有哪些资源可以用，这些资源再由外部框架决定是否接受，接收后使用自己的策略进行内部的任务分配，将各个任务分配好的结果通过scheduler返回给master进行提交运行。

Executor主要用于在slave上启动框架内部的任务。由于不同的框架，任务执行的接口和方式都不一样。当一个新的框架要接入mesos时，需要一个对应的executor，告诉mesos该如何启动任务。

下图是一个简单的Mesos工作流程：
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/architecture-example.jpg)

1. 当出现以下几种事件中的一种时，会触发资源分配行为：新框架注册、框架注销、增加节点、出现空闲资源等；
2. Mesos Master中的Allocator模块为某个框架分配资源，并将资源封装到ResourceOffersMessage（Protocal Buffer Message）中，通过网络传输给SchedulerProcess；
3. SchedulerProcess调用用户编写的Scheduler中的resourceOffers函数（不能版本可能有变动），告之有新资源可用；
4. 用户的Scheduler调用MesosSchedulerDriver中的launchTasks()函数，告之将要启动的任务；
5. SchedulerProcess将待启动的任务封装到LaunchTasksMessage（Protocal Buffer Message）中，通过网络传输给Mesos Master；
6. Mesos Master将待启动的任务封装成RunTaskMessage发送给各个Mesos Slave；
7. Mesos Slave收到RunTaskMessage消息后，将之进一步发送给对应的ExecutorProcess；
8. ExecutorProcess收到消息后，进行资源本地化，并准备任务运行环境，最终调用用户编写的Executor中的launchTask启动任务（如果Executor尚未启动，则先要启动Executor。

总的来说Mesos是一个二级调度机制，第一级是向框架提供总的资源，第二级由框架自身进行二次调度然后将结果返回给Mesos。
<br />
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/overall.png)

---
Master部分在`/path/to/mesos/src/master`下，`main.cpp`是入口程序，其内部会生成一个master对象，该对象开始监听信息。

Slave部分在`/path/to/mesos/src/slave`下，同样`main.cpp`是slave的入口程序，在处理完若干参数后会生成一个slave对象，该对象开始监听信息并发送状态给master对象。

MesosSchedulerDriver的启动模块在`/path/to/mesos/src/sched/sched.cpp`下，它创建一个scheduler的进程等待framework通过http的方式来注册，相当于给外部framework提供了一个接口。

MesosExecutorDriver的启动模块在`/path/to/mesos/src/exec/exec.cpp`下，同理它创建了一个executor进程等待framework通过http的方式注册。

## 框架在Mesos上的运行过程，并与传统操作系统进行对比

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/cluster-overview.png)

上图表示了Spark的整体运行框架。当运行Mesos的时候，Mesos的master代替上图中Cluster Master作为Spark的Master。

如果一个Spark驱动程序提交一个作业并开始分发调度作业相关的任务，将会由Mesos来决定每个任务分发到哪台机器上。Mesos在调度短期任务的时候，会根据提交的任务来动态分配资源，而不需要依赖于静态的资源划分。

Spark在启动后会在Mesos的Master上进行注册，master始终监听来自外部框架的信息。具体需要注册scheduler和executor。注册完毕后，Spark会生成Spark context。此时Master会向Spark报告此时的资源情况，Spark如果需要执行任务则会检查资源是否符合要求，若符合则会接收资源然后在内部进行调度，将结果返回给Master，由Master去调用slave上的Spark executor来执行任务。

### 对比
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/os-and-mesos.png)

 * 相同点：操作系统内核和Mesos都是提供了资源的抽象，操作系统内核将真正的物理资源如CPU、内存、GPU、网卡和IO设备等进行抽象管理和分配；而Mesos是将若干个计算机能提供的计算资源如CPU的核数、总的运行内存、总的GPU资源等进行管理和调度。

 * 不同点：传统操作系统中，进程请求内存资源时，操作系统会立即响应，在物理内存中开辟地址空间将其映射到虚存上，若物理内存空间不足则会将一部分物理内存放到硬盘的交换空间中；而Mesos则会向外部框架提供资源信息，外部框架可以选择拒绝或者接受。这是因为要保证正在运行的任务的资源一直存在。


## Master和Slave初始化过程

### Master
Master的启动代码是从`/path/to/mesos/src/master/main.cpp`的main函数开始的。

1. `master::Flags flags`解析命令行参数和环境变量。Mesos封装了Google的gflags来解析命令行参数和环境变量，在`/path/to/mesos/src/master/flags.cpp`里有对flags封装的代码。
```C++
Try<flags::Warnings> load = flags.load("MESOS_", argc, argv);
```

2. `process::firewall::install(move(rules))`即如果有参数`--firewall_rules`则会添加规则。
3.`ModuleManager::load(flags.modules.get())`即如果有参数`--modules`或者`--modules_dir=dirpath`，则会将路径中的so文件装载进来。
4. 创建`allocator`的一个实例。
```C++
const string allocatorName = flags.allocator;
Try<Allocator*> allocator = Allocator::create(allocatorName);
```
5. 接下来是一些hook和zookeeper的其他参数处理。
6. 最后启动master线程对master初始化操作，该初始化文件在`/path/to/mesos/src/master.cpp`中，
```C++
void Master::initialize()
{
	LOG(INFO) << "Master " << info_.id() << " (" << info_.hostname() << ")"
			<< " started on " << string(self()).substr(7);
	LOG(INFO) << "Flags at startup: " << flags;
	...
```
 * 初始化role，并设置weight权值。
 * 初始化allocator。
```C++
allocator->initialize(
	flags.allocation_interval,
	defer(self(), &Master::offer, lambda::_1, lambda::_2),
	defer(self(), &Master::inverseOffer, lambda::_1, lambda::_2),
	weights,
	flags.fair_sharing_excluded_resource_names);
```
 * 监听消息，注册处理函数。
 * 竞争成为master中的leader，或检查当前的leader。

### Slave
Slave的启动是从`/path/to/mesos/src/slave/main.cpp`中的main函数开始的。

1. `slave::Flags flags`解析命令行参数和环境变量。
```C++
Try<flags::Warnings> load = flags.load("MESOS_", argc, argv);
```
2. `process::firewall::install(move(rules))`如果有参数--firewall_rules则会添加规则。
3. `ModuleManager::load(flags.modules.get())`如果有参数--modules或者--modules_dir=dirpath，则会将路径中的so文件load进来。
4. 初始化Containerizer
```C++
Fetcher fetcher;
Try<Containerizer*> containerizer =
    Containerizer::create(flags, false, &fetcher);
```
在`/path/to/mesos/src/slave/containerizer/containerizer.cpp`中有create函数
```C++
Try<Containerizer*> Containerizer::create(
    const Flags& flags,
    bool local,
    Fetcher* fetcher)
```
接下来是根据配置文件获取一系列的containerizer类型并放到set中，然后根据类型来创建containerizer。
5. Detect Master的leader对象。
6. 创建垃圾收集器，状态更新器，资源检测器。
7. 启动slave线程进行slave初始化，该初始化文件在`/path/to/mesos/src/slave/slave.cpp`里面。
```C++
void Slave::initialize()
{
	LOG(INFO) << "Mesos agent started on " << string(self()).substr(5);
	LOG(INFO) << "Flags at startup: " << flags;
	...
}
```
 * 在检查了一些列system环境和http相关设置后，首先进行资源预估器的初始化
```C++
Try<Nothing> initialize =
    resourceEstimator->initialize(defer(self(), &Self::usage));
...
initialize = qosController->initialize(defer(self(), &Self::usage));
```
 * 根据参数`--work-dir`创建工作目录，检查资源是否分配到位。
 * 初始化attributes、hostname和statusUpdateManager。
 * 接下来注册一系列处理函数。

## Mesos资源调度算法
调度器的初始化在`/path/to/mesos/src/master/allocator/allocator.cpp`中，然后用hierarchicalDRF算法进行资源的分配。该算法文件在`/path/to/mesos/src/master/allocator/mesos/hierarchical.cpp`中。同时用`sorter.hpp`来对framework进行排序。
 * DRF全称为`Dominant Resource Fairness (DRF)`。DRF采用公平分配的方法，将多种资源在不需要静态划分的情况下进行公平分配。
 * Min-max算法是最大化最小值，在进行单一资源分配时，相当于对该资源分成`N`份，每个用户`1/N`。多种资源存在时，如CPU，内存、硬盘、网络等，同理也可以进行min-max算法分配。
 * 比如现在有`<9 CPU, 18 GB RAM>`，有两个用户，其中用户A运行的任务的需求向量为`<1 CPU, 4 GB RAM>`，用户B运行的任务的需求向量为`<3 CPU，1 GB RAM>`，用户可以执行尽量多的任务来使用系统的资源。
 * 在上述方案中，A的每个任务消耗总CPU的1/9和总内存的2/9，所以A的dominant resource是内存；B的每个任务消耗总CPU的1/3和总内存的1/18，所以B的dominant resource为CPU。DRF会均衡用户的dominant shares，执行3个用户A的任务，执行2个用户B的任务。三个用户A的任务总共消耗了`<3 CPU，12 GB RAM>`，两个用户B的任务总共消耗了`<6 CPU，2 GB RAM>`；在这个分配中，每一个用户的dominant share是相等的，用户A获得了2/3的RAM，而用户B获得了2/3的CPU。
 * 以上的这个分配可以用如下方式计算出来：x和y分别是用户A和用户B的分配任务的数目，那么用户A消耗了`<x CPU，4x GB RAM>`，用户B消耗了`<3y CPU，y GB RAM>`，在图三中用户A和用户B消耗了同等dominant resource；用户A的dominant share为4x/18，用户B的dominant share为3y/9。所以DRF分配可以通过求解以下的优化问题来得到：
```
max(x,y) #(Maximize allocations)
subject to

x + 3y <= 9 #(CPU constraint)
4x + y <= 18 #(Memory Constraint)
2x/9 = y/3 #(Equalize dominant shares)
```
 * 最后解出x=3以及y=2，因而用户A获得`<3 CPU，12 GB RAM>`，B得到`<6 CPU，2 GB RAM>`。

## 写一个完成简单工作的框架

我使用Python完成了一项数组求和的工作，使用了pymesos这个包。<br />
性能上比串行程序慢了很多，因为都是在本地虚拟机上跑的，10个tasks和通信以及文件读写开销是很大的，所以比串行慢可以理解。<br />
我在pymesos的包中找到了example，并仔细阅读了example，发现example就是直接无限制启动task，然后在标准错误输出中打印字符串。我将其扩展改造，写了以下两个Python文件：
 * [scheduler.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/code/scheduloer.py) GetSumScheduler类的定义和整个framework的入口函数
 * [executor.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/code/executor.py) GetSumExecutor类的定义

### Scheduler部分代码执行过程
1. 初始化exeuctor信息，包括名称、执行路径和资源信息等。
2. 初始化framework信息，包括名称、用户信息和Host。
3. 初始化scheduler驱动，这个类封装在pymesos包中，使程序员摆脱了底层相关的事情，直接调用API即可。
4. 增加信号处理函数，Ctrl + C。
5. 开启运行的线程，然后用while等待线程。
6. 进入GetSumScheduler类，其构造函数首先会读文件，然后将数据平均分成10份，然后创建10个task，每个task执行一份数据。启动task的过程基本是example里写好的，但是需要再定义一个frameworkMessage方法来接收从executor执行回来的结果。
7. 在updateStatus中判断是否10个tasks的任务执行完毕，若完毕则可以结束scheduler。

### Executor部分代码执行过程
1. 先发送当前的状态信息，初始化时状态为RUNNING
2. 接着执行核心的部分，这里很简单，只是求和。
3. 执行结束后会再发送FINISHED的信息。
（注意如果executor代码发生异常，则可能会卡在RUNNING和FINISHED之间，这里需要再处理）

 * 运行时的状态
 ![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/runningInfo.png)

 * 运行结果
 ![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/result.png)

---
存在的不足：<br />
 * 功能上比较简陋，只实现了求和，因为没有学过并行程序设计，暂时没有更好的idea。
 * 由于完成时间比较仓促，程序的鲁棒性很差，没有进行各种的异常处理，可能导致莫名其妙的错误。
 * 数据和Task的分配方式基本都是靠人工，没有考虑到数据的特点。
 * 运行速度慢，可能和Python语言特性有关。但大部分时间都花在初始化和结束task，可以发现从RUNNING到FINISHED速度很快说明真正计算的部分耗时很少。