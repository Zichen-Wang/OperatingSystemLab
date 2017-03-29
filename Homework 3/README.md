# 第三次作业

## 安装配置Docker

在服务器上安装成功，下图是运行hello-world的截图

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/dockerInfo.png)

## 介绍Docker基本命令

### 1. 容器命令 docker run
#### 含义：
 * docker run是在新的容器中运行一个进程。 它使用自己的文件系统、网络、独立的进程树开启新的进程。用于开启新进程的IMAGE可以定义在容器中运行的进程的默认配置，连接到的网络环境等等，但是docker run会将控制权转交给开启容器的操作者，所以docker run有比其它docker命令更多的选项。

 * docker run命令必须指定一个容器运行的镜像IMAGE。镜像的开发者可以指定一些默认配置比如：分离或前台运行、容器鉴定、网络设置、运行时的CPU和内存。

 * 如果当前的IMAGE没有下载或准备好，docker run会和docker pull IMAGE一样在加载容器运行镜像之前自动下载该镜像和所有的依赖。
#### 用法
 * `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`
#### 选项
```
--add-host value             添加自定义的host到IP地址映射(host:ip)。
-a, --attach value           依附到STDIN、STDOUT、STDERR。在前端运行环境下，docker run在容器中开启的进程可以依附到控制台的标准输入、输出和错误输出，用-a选项来指定即可。
--blkio-weight value         限制IO带宽的相对权重，从10到1000。
--blkio-weight-device value  限制特定设备的IO带宽的相对权重。格式为DEVICE_NAME:WEIGHT。
--cap-add value              赋予该容器里进程的Linux Capabilities，即可以有杀掉其他进程的能力，重启的能力等等。
--cap-drop value             剥夺该容器里进程的Linux Capabilities。
--cgroup-parent string       可以为该容器指定parent的cgroup。Docker使用了Linux中的cgroup来实现容器的资源管理限制，所以child cgroup可以继承parent的cgroup的一些属性。
--cidfile string             将该容器的ID写到文件中。
--cpu-percent int            限制CPU利用率（仅在Windows下可用）。
--cpu-period int             Linux下限制CPU的使用周期。
--cpu-quota int              Linux下限制CPU的使用份额。
-c, --cpu-shares int         CPU份额（相对权重），表示各个容器将按照权重来分整个CPU的利用率。
--cpuset-cpus string         绑定容器到指定CPU上运行，例如：0-3、0,1等。
--cpuset-mems string         绑定容器到指定内存上运行，例如：0-3、0,1等。（仅在NUMA非统一内存访问架构系统上有效）
-d, --detach                 在后台运行容器并且打印容器号。默认不在后台运行。
--detach-keys string         为分离后的容器重写钥匙序列。
--device value               为容器添加宿主机的设备。例如：--device=/dev/sdc:/dev/xvdc:rwm。
--device-read-bps value      限制某个设备读的速率，单位是‘字节/秒’。例如：--device-read-bps=/dev/sda:1mb。
--device-read-iops value     限制某个设备读的速率，单位是‘IO/秒’。例如：--device-read-iops=/dev/sda:1000。
--device-write-bps value     限制某个设备写的速率，单位是‘字节/秒’。例如：--device-write-bps=/dev/sda:1mb。
--device-write-iops value    限制某个设备写的速率，单位是‘IO/秒’。例如：--device-write-iops=/dev/sda:1000。
--disable-content-trust      跳过镜像验证，默认为开启。
--dns value                  设置自定义的DNS服务器。
--dns-opt value              设置自定义的DNS选项。
--dns-search value           设置自定义DNS搜索域。如果不希望设置搜索域，使用--dns-search=。
--entrypoint string          重写镜像默认的入口指令ENTRYPOINT。如果操作者希望在镜像开始时运行一些其他的命令，可以用这个选项重写。
-e, --env value              为容器内部运行设置环境变量。
--env-file value             从外部文件读入环境变量。
--expose value               设置一个或一个范围内的端口。例如：--expose=3300-3310。通知Docker该容器在运行时要监听指定的端口，Docker利用这个信息去和其他容器互联以及设置宿主机的端口转发。
--group-add value            添加额外可以合并的组。
--health-cmd string          运行检查健康度的命令。
--health-interval duration   运行检查健康度命令的时间间隔。
--health-retries int         连续失败多少次需要报告不健康。
--health-timeout duration    运行一次检查健康度命令的允许的最长时间。
--help                       打印帮助。
-h, --hostname string        设置容器的主机名。在容器内部可用。
-i, --interactive            在attach选项没有打开的情况下也保持依附标准输入STDIN，默认是关闭状态。
--io-maxbandwidth string     为系统设备设置最大IO带宽（仅Windows可用）。
--io-maxiops uint            为系统设备设置最大IO速率（仅Windows可用）。
--ip string                  容器的IPv4地址。例如：172.30.100.104。和--net选项为用户定义的网络同时用。
--ip6 string                 容器的IPv6地址。例如：2001:db8::33。和--net选项为用户定义的网络同时用。
--ipc string                 IPC进程间通讯命名空间。
--isolation string           该选项指定了容器的分离技术。Windows下是hyperv，Linux下是default。
--kernel-memory string       限制内核内存。格式: <数字>[<单位>] b, k, m 或 g。
-l, --label value            为容器设置元数据。例如：--label com.example.key=value。
--label-file value           从外部文件读取元数据。
--link value                 和其他容器设置关联。格式：<名称 或 id>:别名 或 <名称 或 id>。
--link-local-ip value        设置容器本地连接的IPv4或IPv6地址。
--log-driver string          容器的日志驱动。
--log-opt value              容器的日志选项。
--mac-address string         容器的MAC地址。例如：92:d0:c6:0a:29:33。
-m, --memory string          容器内存限制。格式: <数字>[<单位>] b, k, m 或 g。当为0时表示不限制。
--memory-reservation string  设置容器内存保留大小。当容器检测到内存不足时，会强制限制应用程序的内存使用在该值以下。
--memory-swap string         设置容器内存加交换空间的总大小。-1表示无限制的交换空间。
--memory-swappiness int      调整容器内存的swappiness，即是积极的使用物理内存还是交换空间(0-100)，默认是-1。
--name string                给容器赋一个名字。
--network string             将容器连接到网络，默认是default。
--network-alias value        为容器添加网络范围内的别名。
--no-healthcheck             禁用容器的健康度检查。
--oom-kill-disable           禁用Out-Of-Memory kill，即内核为了运行杀死占用过多内存的进程。
--oom-score-adj int          调整主机的OOM偏好，从-1000到1000。
--pid string                 进程号的命名空间。默认是创建私有的进程号命名空间。
--pids-limit int             调整容器的进程号限制，-1表示不限制。
--privileged                 为容器提供一些特权，默认是关闭。开启时容器可以访问到任何的设备，可以访问到容器外的任何内容。
-p, --publish value          对宿主机公开容器的端口号。
-P, --publish-all            将容器所有的端口号映射到宿主机的某个任意的端口上。
--read-only                  挂载在容器上的文件系统为只读。
--restart string             当一个容器退出后的重启策略。
--rm                         当容器退出时自动移除容器。
--runtime string             Runtime to use for this container (?)
--security-opt value         容器的安全选项。
--shm-size string            容器共享内存/dev/shm大小，默认为64MB。
--sig-proxy                  为进程代理接收信号，默认为开启。
--stop-signal string         停止容器运行的信号，默认为SIGTERM。
--storage-opt value          容器的存储驱动选项。
--sysctl value               sysctl动态修改内核参数的选项。
--tmpfs value                挂载tmpfs档案储存目录。
-t, --tty                    为容器分配一个虚假的TTY控制台。
--ulimit value               Ulimit选项。Ulimit用于限制shell启动进程所占用的资源。
-u, --user string            用户名，格式：<名称|uid>[:<组名称|gid>]
--userns string              用户的命名空间。
--uts string                 UTS命名空间。UTS命名空间用于设置主机名和对该命名空间中正在运行的进程可见的域。
-v, --volume value           绑定挂载的卷。
--volume-driver string       可选的容器卷参数。
--volumes-from value         为指定的容器挂载卷。
-w, --workdir string         容器内部的工作目录。
```
#### IMAGE
 * 这里需要指定一个镜像名。如果在本地找不到，则会从镜像库中下载。

#### COMMAND ARGS...
 * 运行镜像时给出一个命令，这个命令可以携带参数。

#### 例子
1. `docker run --read-only --tmpfs /run --tmpfs /tmp -i -t ubuntu /bin/bash` <br />
运行ubuntu镜像，运行镜像时执行bash命令。启动容器时将进程的标准输出依附到控制台上，容器的文件系统为只读，但为了处理一些临时写的文件，需要挂载tmpfs临时的档案目录。
2. `docker run -p 8080:80 -d -i -t ubuntu/httpd` <br />
运行带有apache服务器的ubuntu镜像，在后台运行，将容器的80端口映射到宿主机的8080端口。
3. `docker run -v /home/pkusei:/data1 -i -t ubuntu bash` <br />
运行ubuntu镜像，运行镜像时执行bash命令。启动容器时将宿主机的/home/pkusei目录挂载到容器的/data1目录下。

---

### 2. 镜像命令 docker images
#### 含义
 * 这个命令用来列举在本地的镜像。包括镜像名称、版本号、镜像ID、创建时间和大小。

#### 用法
`docker images [OPTIONS] [REPOSITORY[:TAG]]`

#### 选项
```
-a, --all               展示所有的镜像（默认隐藏中间过程的镜像）。
--digests               展示摘要，sha256哈希值。
-f, --filter value      根据条件来过滤输出。
--format string         用go模板格式化输出。
--help                  打印帮助。
--no-trunc              打印原始的镜像ID信息，不经过裁剪。
-q, --quiet             仅打印镜像ID。
```

#### 例子
1. `docker images` <br />
直接展示所有镜像的信息，效果等同于`docker images -a`或`docker images --all`。
2. `docker images -q --no-trunc` <br />
仅打印不经过裁剪的镜像ID。

---

### 3. 网络管理命令 docker network
`docker network`下面有6个子命令，分别是：
 * `docker network connect` 将一个容器连接入网络。
 * `docker network create` 创建一个网络。
 * `docker network disconnect` 将一个容器断开网络。
 * `docker network inspect` 展示一个或多个网络的详细信息。
 * `docker network ls` 列举网络。
 * `docker network rm` 移除一个或多个网络。

#### (1) `docker network connect`
 * 含义：将一个容器连接入网络。在相同网络内的容器可以相互通信。
 * 用法：`docker network connect [OPTIONS] NETWORK CONTAINER`
 * 选项：
```
--alias value             为容器添加网络域的别名。
--help                    打印帮助。
--ip string               IP地址。
--ip6 string              IPv6地址。
--link value              添加到其他容器的链接。
--link-local-ip value     为容器添加本地链接。
```
 * NETWORK: 可以使用网络的名字或者ID。
 * CONTAINER: 可以使用容器的名字或者ID。
 * 例子：`docker network connect simple-network 123ffe481a1f` <br />
 将容器123ffe481a1f加入simple-network网络。

#### (2) `docker network create`
 * 含义：创建一个网络。
 * 用法：`docker network create [OPTIONS] NETWORK`
 * 选项：
```
--aux-address value         给网络驱动用的附属IPv4或IPv6地址。
-d, --driver string         指定管理网络的驱动。默认是bridge。
--gateway value             为子网指定IPv4或IPv6网关。
--help                      打印帮助。
--internal                  限制外部访问该网络。
--ip-range value            从一段子域中为容器分配IP。
--ipam-driver string        IP地址管理驱动。默认为default。
--ipam-opt value            指定IP地址管理驱动的选项。
--ipv6                      激活IPv6网络。
--label value               为网络设置元数据。
-o, --opt value             为网络驱动指定选项。
--subnet value              设置在CIDR无类别域间路由中的子网。(?)
```
 * 例子：`docker network create -d bridge my-bridge-network` <br />
 用bridge网络驱动创建my-bridge-network网络。

#### (3) `docker network disconnect`
 * 含义：将容器断开指定的网络。
 * 用法：`docker network disconnect [OPTIONS] NETWORK CONTAINER`
 * 选项：
```
-f, --force                 强制使容器断开指定网络。
--help                      打印帮助。
```
 * NETWORK 和 CONTAINER 含义同上
 * 例子：`docker network disconnect simple-network 8befde452085` <br />
 断开容器8befde452085的simple-network网络。


#### (4) `docker network inspect`
 * 含义：展示一个或多个网络的细节信息。返回JSON数据结构。
 * 用法：`docker network inspect [OPTIONS] NETWORK [NETWORK...]`
 * 选项：
```
-f, --format string         使用给定的go模板格式化输出。
--help                      打印帮助。
```
 * 例子：`docker network inspect simple-network my-bridge-network` <br />
 展示simple-network和my-bridge-network网络信息。

#### (5) `docker network ls`
 * 含义：展示所有网络。
 * 用法：`docker network ls [OPTIONS]`
 * 选项：
```
-f, --filter value          提供过滤选项。例如：dangling=true。
--help                      打印帮助。
--no-trunc                  打印原始的网络ID信息，不经过裁剪。
-q, --quiet                 仅打印网络ID。
```
 * 例子：`docker network ls --no-trunc -q` <br />
 仅打印不经过裁剪的网络ID。

#### (6) `docker network rm`
 * 含义：移除一个或多个网络。
 * 用法：`docker network rm NETWORK [NETWORK...]`
 * 选项：
```
--help                      打印帮助。
```
 * 例子：`docker network rm simple-network my-bridge-network` <br />
 移除simple-network和my-bridge-network网络。

---

### 4. 创建镜像命令 docker commit
#### 含义
 * 从一个现存的容器中通过指定名字和ID来创建新版本的镜像。新版本镜像需要包含容器的文件系统、磁盘卷、标签。
 * 可以用`Dockerfile`文件来生成协助创建新版本镜像。

#### 用法
`docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]`

#### 选项
```
-a, --author string           指定作者。例如："John Hannibal Smith <hannibal@a-team.com>"。
-c, --change value            当创建镜像的时候使用Dockerfile中的指令。支持的指令有：CMD|ENTRYPOINT|ENV|EXPOSE|LABEL|ONBUILD|USER|VOLUME|WORKDIR
--help                        打印帮助。
-m, --message string          提交时候的说明。
-p, --pause                   提交的时候暂停容器的运行。
```
#### CONTAINER
 * 可以使用容器的名字或者ID。

#### REPOSITORY
 * 指定镜像仓库，可以是本地存储。
 * 可以指定远程镜像仓库，如docker hub，也可自建仓库来存放image。

#### 例子
在原始ubuntu镜像中安装了gcc，然后退出容器。<br />
执行`docker commit 650a07b1d3d1 ubuntu_with_gcc` <br />
可以将刚刚结束的容器650a07b1d3d1制作成ubuntu_with_gcc镜像。

---

### 5. 创建镜像命令 docker build
#### 含义
 * 从指定的路径中读取`Dockerfile`文件来创建生成一个新的镜像。

#### 用法
`docker build [OPTIONS] PATH | URL | -`

#### 选项
```
--build-arg value             设置创建时环境变量
                              例如：--build-arg=http_proxy="http://some.proxy.url"，来创建一个http_proxy的环境变量
                              通过build-arg选项传递的参数将作为在容器中的命令运行时的环境。

--cgroup-parent string        为容器选择父cgroup。
--cpu-period int              限制CPU的使用周期。
--cpu-quota int               限制CPU的使用份额。
-c, --cpu-shares int          CPU份额（相对权重），表示各个容器将按照权重来分整个CPU的利用率。
--cpuset-cpus string          绑定容器到指定CPU上运行，例如：0-3、0,1等。
--cpuset-mems string          绑定容器到指定内存上运行，例如：0-3、0,1等。（仅在NUMA非统一内存访问架构系统上有效）
--disable-content-trust       跳过镜像验证，默认为开启。
-f, --file string             Dockerfile的文件名（默认是'PATH/Dockerfile'）。
--force-rm                    总是移除中间过程的镜像。build失败也会移除。默认为关闭。
--help                        打印帮助
--isolation string            该选项指定了容器的分离技术。Windows下是hyperv，Linux下是default。
--label value                 为容器设置元数据。例如：--label com.example.key=value。
-m, --memory string           容器内存限制。格式: <数字>[<单位>] b, k, m 或 g。当为0时表示不限制。
--memory-swap string          设置容器内存加交换空间的总大小。-1表示无限制的交换空间。
--no-cache                    在创建过程中不使用cache。默认为关闭。
--pull                        总是试图创建一个新版本的镜像。默认为关闭。
-q, --quiet                   成功是不打印镜像的ID。默认为关闭。
--rm                          创建成功后移除中介的容器。默认为开启。
--shm-size string             容器共享内存/dev/shm大小，默认为64MB。
-t, --tag value               名称和和可选的标签。格式为'名称:标签'。
--ulimit value                Ulimit选项。Ulimit用于限制shell启动进程所占用的资源。
```

#### PATH | URL | -
 * 设置`Dockerfile`文件所在的路径。

#### 例子
1. `docker build .` <br />
在当前目录使用`Dockerfile`文件创建一个新的镜像。
2. `docker build --rm=false .` <br />
在当前目录使用`Dockerfile`文件创建一个新的镜像，并保留中间过程镜像。
3. `docker build -t fedora/jboss:1.0 .` <br />
在当前目录使用`Dockerfile`文件创建一个新的镜像，名称为fedora下的jboss，版本为1.0。
4. `docker build github.com/scollier/purpletest` <br />
在github.com的仓库中找到远程目录，然后用其中的`Dockerfile`文件创建镜像。
