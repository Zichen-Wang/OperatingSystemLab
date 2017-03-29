# 第三次作业

## 安装配置Docker

在服务器上安装成功，下图是运行hello-world的截图

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/dockerInfo.png)

## 介绍Docker基本命令

### 容器命令 docker run
#### 含义：
 * docker run是在新的容器中运行一个进程。 它使用自己的文件系统、网络、独立的进程树开启新的进程。用于开启新进程的IMAGE可以定义在容器中运行的进程的默认配置，连接到的网络环境等等，但是docker run会将控制权转交给开启容器的操作者，所以docker run有比其它docker命令更多的选项。

 * docker run命令必须指定一个容器运行的镜像IMAGE。镜像的开发者可以指定一些默认配置比如：分离或前台运行、容器鉴定、网络设置、运行时的CPU和内存。

 * 如果当前的IMAGE没有下载或准备好，docker run会和docker pull IMAGE一样在加载容器运行镜像之前自动下载该镜像和所有的依赖。
#### 用法
 * `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`
#### 选项
<pre>
 * `--add-host value`             添加自定义的host到IP地址映射(host:ip)。
 * `-a, --attach value`           依附到STDIN、STDOUT、STDERR。在前端运行环境下，docker run在容器中开启的进程可以依附到控制台的标准输入、输出和错误输出，用-a选项来指定即可。
 * `--blkio-weight value`         限制IO带宽的相对权重，从10到1000。
 * `--blkio-weight-device value`  限制特定设备的IO带宽的相对权重。格式为`DEVICE_NAME:WEIGHT`。
 * `--cap-add value`              赋予该容器里进程的Linux Capabilities，即可以有杀掉其他进程的能力，重启的能力等等。
 * `--cap-drop value`             剥夺该容器里进程的Linux Capabilities。
 * `--cgroup-parent string`       可以为该容器指定parent的cgroup。Docker使用了Linux中的cgroup来实现容器的资源管理限制，所以child cgroup可以继承parent的cgroup的一些属性。
 * `--cidfile string`             将该容器的ID写到文件中。
 * `--cpu-percent int`            限制CPU利用率（仅在Windows下可用）。
 * `--cpu-period int`             Linux下限制CPU的使用周期。
 * `--cpu-quota int`              Linux下限制CPU的使用份额。
 * `-c, --cpu-shares int`         CPU份额（相对权重），表示各个容器将按照权重来分整个CPU的利用率。默认为0表示最大值。
 * `--cpuset-cpus string`         绑定容器到指定CPU上运行，例如：`0-3`、`0,1`等。
 * `--cpuset-mems string`         绑定容器到指定内存上运行，例如：`0-3`、`0,1`等。（仅在NUMA非统一内存访问架构系统上有效）
 * `-d, --detach`                 在后台运行容器并且打印容器号。默认不在后台运行。
 * `--detach-keys string`         为分离后的容器重写钥匙序列。
 * `--device value`               为容器添加宿主机的设备。例如：`--device=/dev/sdc:/dev/xvdc:rwm`。
 * `--device-read-bps value`      限制某个设备读的速率，单位是‘字节/秒’。例如：`--device-read-bps=/dev/sda:1mb`。
 * `--device-read-iops value`     限制某个设备读的速率，单位是‘IO/秒’。例如：`--device-read-iops=/dev/sda:1000`。
 * `--device-write-bps value`     限制某个设备写的速率，单位是‘字节/秒’。例如：`--device-write-bps=/dev/sda:1mb`。
 * `--device-write-iops value`    限制某个设备写的速率，单位是‘IO/秒’。例如：`--device-write-iops=/dev/sda:1000`。
 * `--disable-content-trust`      跳过镜像验证，默认为开启。
 * `--dns value`                  设置自定义的DNS服务器。
 * `--dns-opt value`              设置自定义的DNS选项。
 * `--dns-search value`           设置自定义DNS搜索域。如果不希望设置搜索域，使用`--dns-search=`。
 * `--entrypoint string`          重写镜像默认的入口指令ENTRYPOINT。如果操作者希望在镜像开始时运行一些其他的命令，可以用这个选项重写。
 * `-e, --env value`              为容器内部运行设置环境变量。
 * `--env-file value`             从外部文件读入环境变量。
 * `--expose value`               设置一个或一个范围内的端口。例如：`--expose=3300-3310`。通知Docker该容器在运行时要监听指定的端口，Docker利用这个信息去和其他容器互联以及设置宿主机的端口转发。
 * `--group-add value`            添加额外可以合并的组。
 * `--health-cmd string`          运行检查健康度的命令。
 * `--health-interval duration`   运行检查健康度命令的时间间隔。
 * `--health-retries int`         连续失败多少次需要报告不健康。
 * `--health-timeout duration`    运行一次检查健康度命令的允许的最长时间。
 * `--help`                       打印帮助。
 * `-h, --hostname string`        设置容器的主机名。在容器内部可用。
 * `-i, --interactive`            在attach选项没有打开的情况下也保持依附标准输入STDIN，默认是关闭状态。
 * `--io-maxbandwidth string`     为系统设备设置最大IO带宽（仅Windows可用）。
 * `--io-maxiops uint`            为系统设备设置最大IO速率（仅Windows可用）。
 * `--ip string`                  容器的IPv4地址。例如：172.30.100.104。和`--net`选项为用户定义的网络同时用。
 * `--ip6 string`                 容器的IPv6地址。例如：2001:db8::33。和`--net`选项为用户定义的网络同时用。
 * `--ipc string`                 IPC进程间通讯命名空间。
 * `--isolation string`           该选项指定了容器的分离技术。Windows下是hyperv，Linux下是default。
 * `--kernel-memory string`       限制内核内存。格式: <数字>[<单位>] b, k, m 或 g。
 * `-l, --label value`            为容器设置元数据。例如：`--label com.example.key=value`。
 * `--label-file value`           从外部文件读取元数据。
 * `--link value`                 和其他容器设置关联。格式：<名称 或 id>:别名 或 <名称 或 id>。
 * `--link-local-ip value`        设置容器本地连接的IPv4或IPv6地址。
 * `--log-driver string`          容器的日志驱动。
 * `--log-opt value`              容器的日志选项。
 * `--mac-address string`         容器的MAC地址。例如：92:d0:c6:0a:29:33。
 * `-m, --memory string`          容器内存限制。格式: <数字>[<单位>] b, k, m 或 g。当为0时表示不限制。
 * `--memory-reservation string`  设置容器内存保留大小。当容器检测到内存不足时，会强制限制应用程序的内存使用在该值以下。
 * `--memory-swap string`         设置容器内存加交换空间的总大小。-1表示无限制的交换空间。
 * `--memory-swappiness int`      调整容器内存的swappiness，即是积极的使用物理内存还是交换空间(0-100)，默认是-1。
 * `--name string`                给容器赋一个名字。
 * `--network string`             将容器连接到网络，默认是default。
 * `--network-alias value`        为容器添加网络范围内的别名。
 * `--no-healthcheck`             禁用容器的健康度检查。
 * `--oom-kill-disable`           禁用Out-Of-Memory kill，即内核为了运行杀死占用过多内存的进程。
 * `--oom-score-adj int`          调整主机的OOM偏好，从-1000到1000。
 * `--pid string`                 进程号的命名空间。默认是创建私有的进程号命名空间。
 * `--pids-limit int`             调整容器的进程号限制，-1表示不限制。
 * `--privileged`                 为容器提供一些特权，默认是关闭。开启时容器可以访问到任何的设备，可以访问到容器外的任何内容。
 * `-p, --publish value`          对宿主机公开容器的端口号。
 * `-P, --publish-all`            将容器所有的端口号映射到宿主机的某个任意的端口上。
 * `--read-only`                  挂载在容器上的文件系统为只读。
 * `--restart string`             当一个容器退出后的重启策略。
 * `--rm`                         当容器退出时自动移除容器。
 * `--runtime string`             Runtime to use for this container (?)
 * `--security-opt value`         容器的安全选项。
 * `--shm-size string`            容器共享内存/dev/shm大小，默认为64MB。
 * `--sig-proxy`                  为进程代理接收信号，默认为开启。
 * `--stop-signal string`         停止容器运行的信号，默认为SIGTERM。
 * `--storage-opt value`          容器的存储驱动选项。
 * `--sysctl value`               sysctl动态修改内核参数的选项。
 * `--tmpfs value`                挂载tmpfs档案储存目录。
 * `-t, --tty`                    为容器分配一个虚假的TTY控制台。
 * `--ulimit value`               Ulimit选项。Ulimit用于限制shell启动进程所占用的资源。
 * `-u, --user string`            用户名，格式：<名称|uid>[:<组名称|gid>]
 * `--userns string`              用户的命名空间。
 * `--uts string`                 UTS命名空间。UTS命名空间用于设置主机名和对该命名空间中正在运行的进程可见的域。
 * `-v, --volume value`           绑定挂载的卷。
 * `--volume-driver string`       可选的容器卷参数。
 * `--volumes-from value`         为指定的容器挂载卷。
 * `-w, --workdir string`         容器内部的工作目录。
</pre>
