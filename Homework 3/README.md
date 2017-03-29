# 第三次作业

## 安装配置Docker

在服务器上安装成功，下图是运行hello-world的截图

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/dockerInfo.png)

## 介绍Docker基本命令

### docker run
#### 含义：
 * docker run是在新的容器中运行一个进程。 它使用自己的文件系统、网络、独立的进程树开启新的进程。用于开启新进程的IMAGE可以定义在容器中运行的进程的默认配置，连接到的网络环境等等，但是docker run会将控制权转交给开启容器的操作者，所以docker run有比其它docker命令更多的选项。

 * docker run命令必须指定一个容器运行的镜像IMAGE。镜像的开发者可以指定一些默认配置比如：分离或前台运行、容器鉴定、网络设置、运行时的CPU和内存。

 * 如果当前的IMAGE没有下载或准备好，docker run会和docker pull IMAGE一样在加载容器运行镜像之前自动下载该镜像和所有的依赖。
#### 用法
 * `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`
#### 选项
 * `--add-host value`             添加自定义的host到IP地址映射 (host:ip) 默认是空
 * `-a, --attach value`           依附到STDIN、STDOUT、STDERR。在前端运行环境下，docker run在容器中开启的进程可以依附到控制台的标准输入、输出和错误输出，用-a选项来指定即可。
