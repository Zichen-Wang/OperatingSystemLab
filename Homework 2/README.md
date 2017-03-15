# 第二次作业

## Mesos组成结构

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%202/architecture.jpg)

上图表明了Mesos的主要组成部分。Mesos有master进程，其管理运行在云端每个结点上的slave进程，同时有一个分布式框架在这些slave结点上运行任务。

Master主要任务是进行资源的分配，slaves会定期向master汇报自己的资源情况，Master因此可以得到资源分配表来决定给每个运行框架提供多少的资源。资源的分配调度机制通过一个`allocation module`的组件来完成，可以用户自己来写或者完善。