# 第三次作业

## 安装配置Docker

在服务器上安装成功，下图是运行hello-world的截图

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/dockerInfo.png)

---

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
 * `docker images [OPTIONS] [REPOSITORY[:TAG]]`

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
 * `docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]`

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
 * `docker build [OPTIONS] PATH | URL | -`

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

---

### 6. 容器命令 docker exec
#### 含义
 * 在一个运行中的容器中执行新的命令。

#### 用法
 * `docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`

#### 选项
```
-d, --detach         分离模式：在后台运行命令。
--detach-keys        为分离后的容器重写钥匙序列。
--help               打印帮助。
-i, --interactive    没有被依附的情况下保持标准输入的依附。
--privileged         为容器提供一些特权，默认是关闭。开启时容器可以访问到任何的设备，可以访问到容器外的任何内容。
-t, --tty            为容器分配一个虚假的TTY控制台。
-u, --user           用户名，格式：<名称|uid>[:<组名称|gid>]
```

#### CONTAINER 和 COMMAND 含义同上

#### 例子
1. `docker exec -it my_container /bin/bash` <br />
在运行中的my_container容器中打开一个新的控制台，并保持输入依附。
2. `docker exec my_container cat /etc/hosts` <br />
在运行中的my_container容器中输出`/etc/hosts`的内容。



## 创建镜像并搭建服务器
### 创建一个基础镜像为ubuntu的docker镜像
命令：`root@oo-lab:/# docker run -i -t --name homework -p 9999:80 ubuntu /bin/bash` <br />
容器名为homework，并将容器的80端口映射到宿主机的9999端口。
### 加入nginx服务器
命令：
```
root@578f606816b5:/# apt update
root@578f606816b5:/# apt install nginx -y
```
### 启动nginx服务器
命令：`root@578f606816b5:/# nginx`

### 利用tail命令将访问日志输出到标准输出流
* 命令：`root@578f606816b5:/# tail -f /var/log/nginx/access.log`

* 再把虚拟机的端口9999映射到外网IP的端口9999 <br />
首次访问`162.105.174.39:9999`，网页截图和访问日志：
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/helloNginx.png)
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/nginxLog.png)

### 编辑Web服务器主页
 * 在容器中`/var/www/html/`目录下添加`index.html`。
 * 重新访问`162.105.174.39:9999`，网页截图：
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/myPage.png)

### 将现在的容器内容制作成镜像，方便在后台运行该容器并开启nginx服务器
 * 首先停止该容器：`root@578f606816b5:/# exit`
 * 制作新镜像：`root@oo-lab:/# docker commit homework ubuntu_with_nginx`
 * 在后台启动带新镜像的容器http_server，并将容器端口80映射到宿主机端口9999，接着以前台方式运行nginx：<br />
 `root@oo-lab:/# docker run -d --name http_server -p 9999:80 ubuntu_with_nginx nginx -g 'daemon off;'`
 * 当前容器运行情况为：
```
root@oo-lab:/# docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                           PORTS                  NAMES
96c5b22c509b        ubuntu_with_nginx   "nginx -g 'daemon off"   18 hours ago        Up 2 seconds                       0.0.0.0:9999->80/tcp   http_server
578f606816b5        ubuntu              "/bin/bash"              19 hours ago        Exited (0) 12 seconds ago                                  homework
```

### 创建一个自己定义的network，模式为bridge
 * 命令：`root@oo-lab:/# docker network create -d bridge my-bridge-network`
 * 当前网络定义情况为：
```
root@oo-lab:/# docker network ls
NETWORK ID          NAME                    DRIVER              SCOPE
b669753e111a        bridge                  bridge              local
64149ba635bf        host                    host                local
66a03170958b        my-bridge-network       bridge              local
3433aea97d81        none                    null                local
```
 * 新定义的bridge网络配置为：
 ```
 root@oo-lab:/# docker network inspect my-bridge-network
[
    {
        "Name": "my-bridge-network",
        "Id": "66a03170958b3d34381f4147fdeed278069f61e4249a748f2d98a727ad832e6c",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1/16"
                }
            ]
        },
        "Internal": false,
        "Containers": {
            "96c5b22c509b8a601bf0a8c78bffed7b60122f845c18240a42b676c74fca6d5f": {
                "Name": "http_server",
                "EndpointID": "e1acca3a431e3d1667bae369699c3f76b9e3ce5ca97be7a447cdccc991f4692b",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {}
    }
]
 ```

### 让自己配的web服务器容器连到这一网络中
* 由于Docker容器创建的时候会自动加入Docker自带的默认bridge网络，该网络的子网为`172.17.0.1`，首先从容器中断掉这个网络（非必须）<br />
`root@oo-lab:/# docker network disconnect bridge http_server`
* 加入自己定义的network：`root@oo-lab:/# docker network connect my-bridge-network http_server`

### 通过宿主机访问容器内的web服务器
 * 先通过`root@oo-lab:/# docker inspect http_server`查看web服务器容器的IP地址为`172.18.0.2`。
 * 宿主机访问web服务器命令：`root@oo-lab:/# curl 172.18.0.2:80`
 * 返回结果：
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/curl.png)

---

## Docker容器网络模式
### bridge模式
 * 在默认情况下，docker会在宿主机上建立一个`docker0`的网桥，相当于一个虚拟的交换机，所有的容器在默认情况下会连接到这个虚拟的交换机上。
 * docker在安装后也会自动创建一个自带的bridge网络配置，用`docker network inspect bridge`可以看到这个网络配置的详细信息。其中发现这个网络创建的一个子网就是`172.17.0.1/16`，容器在默认情况下会自动加入这个子网。加入后容器可以通过这个网关将数据包转发到主机的网卡上，进而连接外网。
 * bridge模式的网络可以创建多个。当docker操作者新创建一个bridge时，其网关也会变化，如创建后的`my-bridge-network`网关为`172.18.0.1/16`。
 * 在同一个bridge中的容器网络可以互通，宿主机也可以ping处在bridge网络的容器。
 * 容器可以加入多个bridge网络，通过`docker network connect`或`docker network disconnect`来可以自由连接或断开bridge网络。

### host模式
 * 在这个模式下，docker不会为容器创建单独的网络命名空间namespace，而是共享主机的network namespace。也就是说：容器可以直接访问主机上所有的网络信息。
 * 这个模式的网络仅可以创建一个，即docker安装时已经创建好的host。
 * 让容器运行在host模式，可以在启动容器的命令行添加`--network host`，即`root@oo-lab:/# docker run -it --network host ubuntu /bin/bash`。
 * 进入后的配置完全和主机一样，终端的前缀提示符也完全一样，显示是`root@oo-lab`。一开始我还很困惑为什么没有反应，结果是已经进入了该容器内。
 * 一旦容器连接到了host模式，就不能再连接到其他模式和断开host模式，即不能通过`docker network connect`或`docker network disconnect`来操作该容器的网络。
 * 这种模式最大的缺点是：容器都是直接共享主机网络空间的，如果出现任何的网络冲突都会出错，比如在这个模式下无法启动两个都监听在80端口的容器。

### null模式
 * 这种模式正如名字说明的那样：不做配置。容器有自己的`network namespace`，但是没有做任何的网络配置，仅仅有本地回环网络`127.0.0.1`。
 * 这个模式的网络仅可以创建一个，即docker安装时已经创建好的none。
 * 让容器运行在null模式，可以在启动容器的命令行添加`--network none`，即`root@oo-lab:/# docker run -it --network none ubuntu /bin/bash`。
 * 和host模式类似，一旦容器连接到了null模式，就不能再连接到其他模式和断开null模式，即不能通过`docker network connect`或`docker network disconnect`来操作该容器的网络。

### overlay模式
 * 使用docker内置的swarm来管理结点，首先在第一台主机上输入命令`docker swarm init`，便会创建一个swarm的管理结点。
```
root@oo-lab:/# docker swarm init
Swarm initialized: current node (dcemal5p2w9y3eo9sh5ctmm8t) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join \
    --token SWMTKN-1-28vqn6goedmwbpl4bbts2hvcxp8m4mrntyveabh7jddh274g13-3bq2a4f6taw2ptciw1tj8amap \
    172.16.6.251:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```
 * 接着在第二和第三台主机上输入以上添加worker的命令。
```
root@oo-lab:/# docker swarm join \
>     --token SWMTKN-1-28vqn6goedmwbpl4bbts2hvcxp8m4mrntyveabh7jddh274g13-3bq2a4f6taw2ptciw1tj8amap \
>     172.16.6.251:2377
This node joined a swarm as a worker.
```
 * 在第一台主机也就是Leader上查看结点：
```
root@oo-lab:/# docker node ls
ID                           HOSTNAME  STATUS  AVAILABILITY  MANAGER STATUS
086y3mxmhs8xl2prs5fh2c5wo    oo-lab    Ready   Active
bn2joyo560kft2t7x1im7ttgg    oo-lab    Ready   Active
dcemal5p2w9y3eo9sh5ctmm8t *  oo-lab    Ready   Active        Leader
```
 * 这时候在每个主机下的`docker network`都会出现名为`ingress`的overlay模式的网络和`docker_gwbridge`的bridge模式网络。
 * `ingress`网络主要用来做负载均衡，为边界mesh路由而准备的网络。它不能被`docker run`或者`docker create`使用，也不能被`docker service create`来创建服务。
 * `docker_gwbridge`可以让容器和集群外产生外部连接。
 * 这时手动创建一个overlay网络：`root@oo-lab:/# docker network create -d overlay my-multi-host-network`。
 * swarm集群不能创建非集群的普通容器，需要创建`docker service`，使用如下命令创建一个名为my-web的nginx网络服务，并且创建3个tasks，将Leader容器中的80端口映射到宿主机8888端口上。<br />
 `docker service create --replicas 3 --network my-multi-host-network --name my-web -p 8888:80 nginx`
 * 此时另外两个主机上也会出现`my-multi-host-network`的overlay网络和`nginx`镜像。
 * 再将Leader宿主机的8888端口映射到外网的8888端口，即可看到nginx主页。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/nginxSwarm.png)
 * overlay配合swarm是典型的master-slave架构，该网络模式主要用于docker服务和集群的创建。而其他的网络模式都是local模式，只能在本地网络中访问，任何和外部操作都需要经过主机做端口映射。overlay网络通过一个新的网段来管理一个集群，通过注册的方式来发现新结点，避免了普通模式下通讯的繁琐。

---

## 阅读mesos中负责与docker交互的源码

### mesos与docker的交互
 * `/path/to/mesos/src/docker/`是executor调用docker运行的源代码。这个目录下有三个主要文件，分别是`executor.cpp`、`docker.cpp`和`spec.cpp`。`docker.cpp`和`spec.cpp`被`executor`所调用。
 * 先说`docker.cpp`。`docker.cpp`相当于一个命令组装器，负责将解析出来的配置文件一一对应成docker命令。其中有`version`、`create`（包括容器的创建和镜像的创建）、`run`（最核心）、`stop`、`kill`、`rm`、`inspect`、`ps`和`pull`，以及一些错误处理的函数。
 * `spec.cpp`负责解析发来的配置文件。将`cantainerInfo`、`commandInfo`等配置信息解析成C++的map类。
 * `executor.cpp`是核心代码，这里实现了一个简单的执行docker容器的executor。这份代码负责执行一个docker容器，然后重定向日志输出文件到配置好的标准输出和标准错误输出。它仅仅启动一个简单的task，也就是docker容器，然后会在这个任务结束或者死亡的时候退出。
 * 这里边定义了两个类，一个是`executor`的进程类，包括注册、启动task、结束task等基本的mesos方法。另一个是`docker`的执行类，这个类运行在之前定义的executor进程类上。
 * `executor.cpp`中的入口函数在`main`函数中：
 1. 处理传进来的参数和环境变量flag，检查`docker`、`container`、`sandbox_directory`和`mapped_directory`是否存在。
 2. 加载`task_environment`核心的配置文件，该文件为JSON格式，交给`spec.cpp`去解析。
 3. 配置不推荐使用的`MESOS_EXECUTOR_SHUTDOWN_GRACE_PERIOD`和已经被废弃的`stop_timeout`。
 4. 验证docker参数。
 5. 在docker执行类中运行docker容器。

### docker类中的run函数
 * `docker.hpp`定义了docker类，这个类主要是用来将参数组装成真正的docker命令。
 * run函数定义在`docker.cpp`中。
 1. 添加docker的选项`-H`，这是用来在daemon模式下绑定socker，path和socker在class中已经有定义。
```C++
vector<string> argv;
argv.push_back(path);
argv.push_back("-H");
argv.push_back(socket);
argv.push_back("run");
```
 2. 检查是否有privilege，即在特权模式下运行docker。
```C++
if (dockerInfo.privileged()) {
    argv.push_back("--privileged");
}
```
 3. 检查是否有resource，分配CPU份额和内存资源。
```C++
if (resources.isSome()) {
    // TODO(yifan): Support other resources (e.g. disk).
    Option<double> cpus = resources.get().cpus();
    if (cpus.isSome()) {...}
    Option<Bytes> mem = resources.get().mem();
    if (mem.isSome()) {...}
}
```
 4. 检查添加env环境变量。
```C++
if (env.isSome()) {
    foreachpair (string key, string value, env.get()) {
        argv.push_back("-e");
        argv.push_back(key + "=" + value);
    }
}
```
 5. 检查commandInfo中的环境变量设置。
 6. 手动添加`MESOS_SANDBOX`和`MESOS_CONTAINER_NAME`两个环境变量。
```C++
argv.push_back("-e");
argv.push_back("MESOS_SANDBOX=" + mappedDirectory);
argv.push_back("-e");
argv.push_back("MESOS_CONTAINER_NAME=" + name);
```
 7. 检查是否有挂载外部磁盘卷的选项volume。
 8. 映射sandbox目录到容器中mapped目录。
```C++
argv.push_back("-v");
argv.push_back(sandboxDirectory + ":" + mappedDirectory);
```
 9. 配置网络`--net`。有host、bridge、none模式和用户自定义网络。
```C++
argv.push_back("--net");
string network;
switch (dockerInfo.network()) {
    ...
}
argv.push_back(network);
```
 10. 检查添加hostname选项，不能和host模式的网络一起出现。
 11. 配置端口映射，host和none模式下不能进行端口映射。
 12. 检查添加外部设备。
 13. 将commandInfo中的shell命令添加到`--entrypoint`选项中，并执行`/bin/bash`。
```C++
if (commandInfo.shell()) {
    argv.push_back("--entrypoint");
    argv.push_back("/bin/sh");
}
```
 14. 添加容器名和指定镜像名。
```C++
argv.push_back("--name");
argv.push_back(name);
argv.push_back(image);
```
 15. 最后添加运行容器后的命令和参数。
 16. 运行容器。
```C++
Try<Subprocess> s = subprocess(
      path,
      argv,
      Subprocess::PATH("/dev/null"),
      _stdout,
      _stderr,
      nullptr,
      environment);
```
---

## 写一个framework，以容器的方式运行task
 * 用python实现，源代码：[scheduler.py](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/code/scheduloer.py)
 * 底层通信接口引用自`pymesos`库，鸣谢`douban`。
 * 代码执行过程：
 1. 初始化framework信息。
```python
# Framework info
framework = Dict()
framework.user = getpass.getuser()
framework.name = "DockerFramework"
framework.hostname = socket.gethostname()
```
 2. 使用底层包提供的接口注册driver，使用默认的executor。
```python
# Use default executor
driver = MesosSchedulerDriver(
  DockerScheduler(),
  framework,
  master,
  use_addict=True,
)
```
 3. 增加信号处理函数，Ctrl + C。
 4. 初始化和运行driver线程，然后主线程死循环等待driver线程。
```python
def run_driver_thread():
    driver.run()

driver_thread = Thread(target=run_driver_thread, args=())
driver_thread.start()

print('Scheduler running, Ctrl+C to quit.')
signal.signal(signal.SIGINT, signal_handler)
while driver_thread.is_alive():
    time.sleep(1)
```
 5. driver线程运行后会进入`DockerScheduler`类中。
 6. 在接收了master提供的资源后，便开始初始化dockerInfo、containerInfo和commandInfo。
```python
# DockerInfo
DockerInfo = Dict()
DockerInfo.image = 'ubuntu_with_nginx'
DockerInfo.network = 'HOST'

# ContainerInfo
ContainerInfo = Dict()
ContainerInfo.type = 'DOCKER'
ContainerInfo.docker = DockerInfo

# CommandInfo used for starting nginx
CommandInfo = Dict()
CommandInfo.shell = False
CommandInfo.value = 'nginx'
# It is so tricky!!!!
CommandInfo.arguments = ['-g', 'daemon off;']
```
 7. 汇总信息到task上。
```python
task = Dict()
task_id = str(uuid.uuid4())
task.task_id.value = task_id
task.agent_id.value = offer.agent_id.value
task.name = 'A simple docker task'
task.container = ContainerInfo
task.command = CommandInfo

task.resources = [
    dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
    dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
]
```
 8. 打印task信息，启动task，同时task计数器加1。并会更新task信息。因为这里只需要启动1个task，所以在启动完task之后线程就会返回。
```python
print("Launching a task")
self.launched_task += 1
driver.launchTasks(offer.id, [task], filters)
```
```python
def statusUpdate(self, driver, update):
    logging.debug('Status update TID %s %s',
                  update.task_id.value,
                  update.state)
    if update.state == 'TASK_RUNNING':
        print('Task is running!')
```
 9. 此后由于线程没有结束，进程便会死循环。
 * `mesos agent`开启命令
```
sudo ./mesos-agent.sh --master=172.16.6.251:5050 --work_dir=/var/lib/mesos \
--ip=172.16.6.24 --hostname=162.105.174.39 --containerizers=docker,mesos \
--image_providers=docker --isolation=docker/runtime`
```
 * 以后台方式运行framework：`pkusei@oo-lab:~/hw3$ python scheduler.py 172.16.6.251 &`
 * 当前docker容器运行情况：
```
root@oo-lab:/home/pkusei# docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
689c4ea883f5        ubuntu_with_nginx   "nginx -g 'daemon off"   34 seconds ago      Up 33 seconds                           mesos-0fdc533b-0f48-4757-8e85-1554f3eef141-S0.89525051-adee-4811-a76f-a4a1f52fa5b8
```
 * 退出ssh后，由于在后台运行，该task会一直在运行状态。（也可以终止掉该task，docker容器仍然会继续运行）
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/task.png)
 * 将agent机器的80端口映射到外网的80端口后，访问`162.105.174.39:80`，可以看到自定义的主页。
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%203/picture/final.png)
