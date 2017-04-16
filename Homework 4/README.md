# 第四次作业

## 分布式文件系统

### 1. HDFS

#### 工作原理

HDFS是采用的是主从结构，其中包含一个NameNode主结点和若干个DataNodes数据结点。主结点管理着文件系统的元数据，为所有文件建立目录树，暴露给客户端，而数据结点则管理着具体的存储。

在内部文件组织上，HDFS将一个文件分成一个或多个块，这些块存储在数据结点上，块的大小可以通过参数配置，每个文件的所有块，除了最后一个块，大小都是固定的。主结点管理文件系统命名空间的操作例如打开、关闭、重命名等，维护文件块到数据结点之间的映射关系。客户端的操作都需要向主结点申请，然后在数据结点和客户端之间打开网络通道传输。

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%204/picture/hdfsarchitecture.gif)

#### 数据备份
HDFS的文件块会创建若干份副本来保证容错性，主结点维护所有块的副本信息。数据结点会定期的向主结点汇报其所有数据块的信息。文件副本的分布位置直接影响着HDFS的可靠性和性能。一个大型的HDFS文件系统一般都是需要跨很多机架的，不同机架之间的数据传输需要经过网关，并且，同一个机架中机器之间的带宽要大于不同机架机器之间的带宽。如果把所有的副本都放在不同的机架中，这样既可以防止机架失败导致数据块不可用，又可以在读数据时利用到多个机架的带宽，并且也可以很容易的实现负载均衡。但是，如果是写数据，各个数据块需要同步到不同的机架，会影响到写数据的效率。

而在Hadoop中，如果副本数量是3的情况下，把第一个副本放到机架的一个结点上，另一个副本放到同一个机架的另一个结点上，把最后一个结点放到不同的机架上。这种策略减少了跨机架副本的个数提高了写的性能，也能够允许一个机架失败的情况，算是一个很好的权衡。

#### 读文件
客户端通过调用这个实例的open方法就可以打开系统中希望读取的文件。HDFS通过调用NameNode获取文件块的位置信息，对于文件的每一个块，NameNode会返回含有该块副本的DataNode的结点地址，另外，客户端还会根据网络拓扑来确定它与每一个DataNode的位置信息，从离它最近的那个DataNode获取数据块的副本，最理想的情况是数据块就存储在客户端所在的结点上。
```
1. 客户端发起读请求。
2. 客户端与NameNode得到文件的块及位置信息列表。
3. 客户端直接和DataNode交互读取数据。
4. 读取完成关闭连接。
```

#### 写文件
客户端通过调用这个实例的create方法就可以创建文件。HDFS会发送给NameNode一个远程过程调用，在文件系统的命名空间创建一个新文件，在创建文件前NameNode会做一些检查，如文件是否存在，客户端是否有创建权限等，若检查通过，NameNode会为创建文件写一条记录到本地磁盘的EditLog，若不通过会向客户端抛出IOException。创建成功之后HDFS会返回一个FSDataOutputStream对象，客户端由此开始写入数据。
```
1. 客户端在向NameNode请求之前先写入文件数据到本地文件系统的一个临时文件。
2. 待临时文件达到块大小时开始向NameNode请求DataNode信息。
3. NameNode在文件系统中创建文件并返回给客户端一个数据块及其对应DataNode的地址列表（列表中包含副本存放的地址）。
4. 客户端只需通过上一步得到的信息把创建的临时文件块更新到列表中的第一个DataNode；第一个DataNode在把数据块写入到磁盘中时会继续向下一个DataNode发送信息，以此类推，直到全部完成。
5. 当文件关闭，NameNode会提交这次文件创建，此时，文件在文件系统中可见。
```
#### 删除文件
```
1. 一开始删除文件，NameNode只是重命名被删除的文件到/trash目录，因为重命名操作只是元信息的变动，所以整个过程非常快。在/trash中文件会被保留一定间隔的时间（可配置，默认是6小时），在这期间，文件可以很容易的恢复，恢复只需要将文件从/trash移出即可。
2. 当指定的时间到达，NameNode将会把文件从命名空间中删除。
3. 标记删除的文件块释放空间，HDFS文件系统显示空间增加。
```

#### 特点
 * 优点：
```
1. 高容错性
  数据自动保存多个副本
  副本丢失后，自动恢复
2. 适合批处理
  移动计算而非数据
  数据位置暴露给计算框架
3. 适合大数据处理
  GB、TB、甚至PB级数据
  百万规模以上的文件数量
  10K+节点规模
4. 流式文件访问
  适合一次性写入，多次读取
  保证数据一致性
5. 可构建在廉价机器上
  通过多副本提高可靠性
  提供了容错和恢复机制
```
 * 不擅长：
```
1. 低延迟与高吞吐率的数据访问，比如毫秒级
2. 大量小文件存取
  占用NameNode大量内存
  寻道时间超过读取时间
3. 并发写入、文件随机修改
  一个文件同一个时间只能有一个写者
```

#### 使用方式
Web接口
```
NameNode和DataNode各自启动了一个内置的Web服务器，显示了集群当前的基本状态和信息。在默认配置下NameNode的首页地址是http://namenode-name:50070/。这个页面列出了集群里的所有DataNode和集群的基本状态。这个Web接口也可以用来浏览整个文件系统（使用NameNode首页上的"Browse the file system"链接）。
```

Shell命令
```
Hadoop包括一系列的类shell的命令，可直接和HDFS以及其他Hadoop支持的文件系统进行交互。bin/hadoop fs -help 命令列出所有Hadoop Shell支持的命令。而 bin/hadoop fs -help command-name 命令能显示关于某个命令的详细信息。这些命令支持大多数普通文件系统的操作，比如复制文件、改变文件权限等。它还支持一些HDFS特有的操作，比如改变文件副本数目。
```


### 2. GlusterFS

GlusterFS是大规模网络分布式文件系统，适合于云存储和媒体流处理等数据密集型任务。GlusterFS是免费和开源的软件，可以应用在任何普通的硬件上。

#### 核心术语
1. 访问控制表 Access Control Lists (ACLs)：为不同的用户和组提供不同的访问权限。
2. Brick：存储的最小基本单位，表现为服务器在可信任的存储池上的一个目录。
3. 卷 Volume：多个存储池中的brick组成的一个可挂载的虚拟存储空间。
4. 用户空间文件系统 Filesystem in Userspace (FUSE)：一个Unix内核的模块，允许非特权用户不经过改动内核代码来创建自己的文件系统。
5. 服务器端 Server：在文件系统中实际存储数据的的机器。
6. 客户端 Client：挂载卷的机器（客户端也可以在服务器端上）。

#### 卷类型
1. 哈希卷：文件通过Hash算法依次在每个brick上映射，没有冗余，但不具备容错能力。
2. 复制卷：文件同步复制到多个brick上，具备容错能力，但写性能下降，读性能上升。
3. 哈希+复制卷：同时具备哈希卷的少冗余和复制卷的容错能力。
4. 条带卷：单个文件分段存储在多个brick上，支持超大文件。
5. 哈希+条带卷：同时具有哈希卷和条带卷的有点。
6. 复制+条带卷
7. 哈希+复制+条带卷：三种基本卷的复合，通常用于类Map-Reduce应用。


#### 总体工作原理
当GlusterFS安装在某个服务器端时，会创建一个gluster管理的后台进程，这个后台进程(glusterd)在集群中的每个服务端结点都会运行。之后，便会组织形成一个可信任的服务器池，brick可以通过这个服务器池作为目录被导出，多个brick可以组合成卷。

在一个卷被创建后，glusterfsd进程开始运行在每个贡献brick的机器中。该进程会在`/var/lib/glusterd/vols`中创建配置文件，表示每个块在卷中的细节信息。客户端进程需要的配置文件也会被创建。之后，我们就可以很容易的在一个客户端机器上像本地文件一样挂载这个卷：
```
mount -t glusterfs <IP or hostname>:<volume_name> <mount_point>
```
当我们在客户端挂载该卷的时候，客户端glusterfs进程会和服务器端的glusterd进程通信。服务器端的glusterd进程会发送包含有客户端翻译表和其他一些能帮助客户端glusterfs进程直接和每个brick的glusterfsd进程通信的配置文件。

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%204/picture/glusterfs_overall_working.png)

当客户端对该卷进行文件操作系统调用时，VFS会向FUSE内核模块发送请求，该内核模块会通过`/dev/fuse`目录将请求发送到客户端的GlusterFS进程上。客户端的GlusterFS进程包含一系列由存储服务器端的glusterd进程定义的翻译器，这些翻译器包括：
1. FUSE翻译器
2. DHT翻译器：DHT翻译器将请求映射到包含所需文件或目录的正确的brick上。这里采用的是弹性Hash算法，输入参数为文件的路径。
3. AFR翻译器：如果卷的类型是复制卷，它将会复制请求并将其传递到Protocol Client翻译器上。
4. Protocol Client翻译器：该翻译器会分成若干线程，每一个线程对应卷中的一个brick，直接和每个块的glusterfsd进行通信。


#### 特点
 * 优点：
```
1. 安装部署简单方便。
2. 隐藏了元数据的概念，元数据直接以扩展属性的方式存储在文件上。
3. 兼容POSIX标准，挂载方便。
```
 * 缺点：
```
1. 用户空间文件系统操作文件的效率相比内核的文件系统可能会慢一些。
2. 每一个Brick需要与其它同卷中的Brick建立TCP长连接。
3. 列出整个文件目录的时间比较长。
```

#### 使用方式
在终端通过`gluster`命令来操作，通常用的有`gluster peer`将服务器加入存储池的命令和`gluster volume`操作卷的命令，以及操作系统系统的`mount`命令，以下是一些核心命令
```
1. gluster peer probe server2     将server2加入服务器存储池
2. gluster volume create gv0 replica 2 server1:/data/brick1/gv0 server2:/data/brick1/gv0      创建复制卷
3. gluster volume start gv0       启动卷
4. mount -t glusterfs server1:/gv0 /mnt   客户端挂载卷
```

### 3. GFS (Google File System)

HDFS最早是仿照GFS来设计开发的，故GFS和HDFS的原理很相似，都是采用主从式的架构。元信息储存在master结点上，块信息储存在多个chunk服务器上。当然这里的一个master是指逻辑上的一个，物理上可以有多个（就是可能有两台，一台用于正常的数据管理，一台用于备份）。
#### 工作原理

![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%204/picture/GFS.jpg)

1. 客户端向Master发送请求，请求信息为（文件名，块索引）。
2. Master使用心跳信息监控块服务器的状态，并向其发送指令。
3. 块服务器需要周期性的返回自己的状态给Master，以确保能够接收Master的请求。
4. Master将（块句柄，块位置）这一信息返回给客户端。
5. 客户端使用文件名和块索引作为Key进行缓存信息。然后，客户端发送请求到其中的一个副本中（通常为最近的），该请求包括（块句柄，字节范围）。对这个块的后续操作，客户端无需再和Master进行通信。
6. 块服务器将所需的块数据发送给客户端。

#### 特点
1. Google采用的存储方法是大量的、分散的普通PC机的存储方式，极大的降低了成本。
2. 对大文件数据快速的存取，这个毫无疑问是可以达到的。
3. 容错能力强，它的数据同时会在多个chunk server上进行备份，具有相当强的容错性。
4. GFS也有缺陷，GFS提供了一个类似的文件系统界面，没有像POSIX那样实现标准的API。
---

## 联合文件系统

### AUFS

AUFS是一种联合文件系统（UnionFS），联合文件系统会将不同物理位置的目录合并mount到同一个目录中。默认写在前边的上层目录是read-write的，后边的下层目录是read-only的。

#### 工作原理

AUFS在合并目录时有一系列的规则：
1. 显然目录中重复文件名的文件只保留一个呈现在最终的目录中，且只会呈现最上层的文件。
2. 默认情况下，修改在原上层的可读写目录中的文件会直接修改掉原文件。
3. 默认情况下，修改在原下层的只读目录中的文件会在原上层目录中新创建一个修改后的文件，原下层目录中的文件不会改变。
4. 若手动将所有的合并目录更改为可读写，修改重复文件名的文件也只会影响到最上层的文件。
5. 删除文件时，若删除的是原最高层目录中的文件，则会删掉原最高层目录中的文件，并且在原最高层目录中打上.wh.\*的隐藏文件标志表示屏蔽下层目录中的该文件。
6. 删除文件时，若删除的是下层只读的文件，则直接会在原最高层目录打上.wh.\*的隐藏文件标志表示屏蔽下层目录中的该文件。
7. 若删除一个文件夹后创建一个同名文件夹，若该文件夹在下层也有，则在原最高层目录新文件夹里加入原有的所有文件的隐藏文件标志。
8. 文件在原来的地方被修改时，可以通过设置udba的参数none、reval、notify来不更新、总是更新、通过消息发送更新。
9. union的目录（分支）的相关权限：
 * rw表示可写可读read-write。
 * ro表示read-only，如果你不指权限，那么除了第一个外ro是默认值，对于ro分支，其永远不会收到写操作，也不会收到查找whiteout的操作。
 * rr表示real-read-only，与read-only不同的是，rr标记的是天生就是只读的分支，这样，AUFS可以提高性能，比如不再设置inotify来检查文件变动通知。
10. 若手动将所有的合并目录更改为可读写，在挂在是可以通过设置create选项来指定新创建文件的保存的目录，如轮转、可用空间最优或二者结合等。

#### 特点
AUFS有所有Union FS的特性，把多个目录合并成同一个目录，并可以为每个需要合并的目录指定相应的权限，实时地添加、删除、修改已经被mount好的目录。而且，他还能在多个可写的branch/dir间进行负载均衡。

1. 节省存储空间：多个container可以共享base image存储。
2. 快速部署：如果要部署多个container，base image可以避免多次拷贝。
3. 内存更省：因为多个container共享base image，以及OS的disk缓存机制，多个container中的进程命中缓存内容的几率大大增加。
4. 升级更方便：相比于copy-on-write类型的FS，base image也是可以挂载为可写的，可以通过更新baseimage而一次性更新其之上的container。
5. 允许在不更改base-image的同时修改其目录中的文件，所有写操作都发生在最上层的可写层中，这样可以大大增加base image能共享的文件内容。

#### 使用方式
只需使用一条命令便可以实现挂载
```
mount -t aufs -o br=(upper)=rw:(base)=ro+wh none (rootfs)
```
例如
```
mount -t aufs -o br=/a=rw:/b=ro+wh none /mnt
```
表示将/a和/b分别以rw和ro+wh的方式合并挂载到/mnt下。

---

## 安装配置一种分布式文件系统，要求启动容错机制

### 安装GlusterFS
 * 在1000和1001上安装最新的GlusterFS 3.10服务器端版本
```
root@oo-lab:/# add-apt-repository ppa:gluster/glusterfs-3.10
root@oo-lab:/# apt update
root@oo-lab:/# apt install glusterfs-server
```

 * 在1002上安装最新的GlusterFS 3.10客户端版本
```
root@oo-lab:/# add-apt-repository ppa:gluster/glusterfs-3.10
root@oo-lab:/# apt update
root@oo-lab:/# apt install glusterfs-client
```

 * 修改1000的Host文件
```
127.0.0.1       server1
127.0.1.1       oo-lab.cs1cloud.internal        oo-lab
172.16.6.24     server2
```

 * 修改1001的Host文件
```
127.0.0.1       server2
127.0.1.1       oo-lab.cs1cloud.internal        oo-lab
172.16.6.251    server1
```

 * 在server1(1000)和server2(1001)上创建brick，作为存储池资源
```
root@oo-lab:/# mkdir -p /data/brick1
```

 * 创建一个复制卷test_volume，并启动该卷（在任意一台服务器上操作）
```
root@oo-lab:/# gluster volume create test_volume replica 2 server1:/data/brick1 server2:/data/brick1 force
# 这里需要用force来强制将brick建立在根分区上
root@oo-lab:/# gluster volume start test_volume
```

 * 查看启动卷的信息，确认启动成功
```
root@oo-lab:/# gluster volume info

Volume Name: test_volume
Type: Replicate
Volume ID: 9a73320b-44cb-4a70-a4c2-e9ee7fcc1cea
Status: Started
Snapshot Count: 0
Number of Bricks: 1 x 2 = 2
Transport-type: tcp
Bricks:
Brick1: server1:/data/brick1
Brick2: server2:/data/brick1
Options Reconfigured:
transport.address-family: inet
nfs.disable: on
```

 * 修改1002客户端的Host文件
```
127.0.0.1       localhost
127.0.1.1       oo-lab.cs1cloud.internal        oo-lab
172.16.6.251    server1
172.16.6.24     server2
```

 * 在1002客户端下创建挂载点，并挂载test_volume卷
```
root@oo-lab:/# mkdir -p /storage
root@oo-lab:/# mount -t glusterfs server1:/test_volume /storage
```

 * 在1002客户端下进行测试，往/storage里存入10个文件
```
root@oo-lab:/# for i in `seq -w 1 10`; do cp -rp /home/pkusei/test.txt /storage/copy-test-$i; done
```

 * 检查客户端挂载点的存入情况
```
root@oo-lab:/storage# ls
copy-test-01  copy-test-02  copy-test-03  copy-test-04  copy-test-05
copy-test-06  copy-test-07  copy-test-08  copy-test-09  copy-test-10
```

 * 检查每个服务器端brick中的存入情况
```
root@oo-lab:/data/brick1# ls
copy-test-01  copy-test-02  copy-test-03  copy-test-04  copy-test-05
copy-test-06  copy-test-07  copy-test-08  copy-test-09  copy-test-10
```

 * 由于创建卷的方式为复制卷且副本个数为2，故当一个服务器挂掉时，另一个服务器还保存有副本，具有容错机制。
 * 例如将server1里的`/data/brick1`抹掉后，仍然可以在客户端的`/storage`下读写文件。

---

## 将Web服务器主页从分布式文件系统挂载到docker容器中

 * 在server1(1000)和server2(1001)上各创建一个新brick，用来存储Web服务器主页
```
root@oo-lab:/# mkdir -p /data/brick2
```

 * 创建一个复制卷hw4，并启动该卷（在任意一台服务器上操作）
```
root@oo-lab:/# gluster volume create hw4 replica 2 server1:/data/brick2 server2:/data/brick2 force
root@oo-lab:/# gluster volume start hw4
```
 * 在1002客户端上挂载hw4到/html下，将主页文件index.html写入分布式文件系统
```
root@oo-lab:/# mkdir -p /html
root@oo-lab:/# mount -t glusterfs server1:/hw4 /html
root@oo-lab:/# vi /html/index.html
```

 * 首先从上次作业的镜像`ubuntu_with_nginx`中启动容器并运行bash，修改nginx服务器默认主页的位置指向要挂载主页卷的位置。具体为修改`/etc/nginx/sites-enabled/default`中root的路径为`/html`，然后退出并保存容器为`ubuntu_with_nginx_hw4`镜像。
 * 这里我是通过宿主机的`/html`挂载点，将其继续挂载到docker容器中。网上的`docker-volume-glusterfs`插件编译不通过，语法错误。
 * 从镜像`ubuntu_with_nginx_hw4`中创建后台容器并运行nginx，将宿主机的`/html`挂载到容器中的`/html`中，将容器的80端口映射到宿主机的4040端口。
```
root@oo-lab:/# docker run -v /html:/html -p 4040:80 -d --name homework4 \
ubuntu_with_nginx_hw4 nginx -g 'daemon off;'
```
 * 将1002机的4040端口映射到外网4040端口，看到服务器的主页
![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework%204/picture/nginx.png)
 * 此时可以使用`umount /html`命令解除1002客户端挂载的`/html`。通过修改分布式文件系统`/html`中的`index.html`就可以直接修改docker容器中的主页。

---

## 仿照Docker镜像工作机制完成一次镜像制作

### Docker镜像工作机制
 * 典型的Linux启动到运行需要两个FS：bootfs和rootfs
 * bootfs (boot file system)主要包含bootloader和kernel，bootloader主要是引导加载kernel，当boot成功后kernel被加载到内存中后bootfs就被解除挂载了。
 * rootfs (root file system)包含的就是典型Linux系统中的/dev、/proc、/bin、/etc等标准目录和文件。
 * 由此可见对于不同的linux发行版，bootfs基本是一致的，rootfs会有差别，因此不同的发行版可以公用bootfs典型的Linux在启动后，首先将rootfs置为只读，进行一系列检查，然后将其切换为可读写供用户使用。在docker中，起初也是将rootfs以只读方式加载并检查，然而接下来利用联合文件系统 的将一个可读写文件系统挂载在只读的rootfs之上，并且允许再次将下层的文件系统设定为只读并且向上叠加，这样多个只读层和一个可读写层的结构构成一个container的运行目录。

### 制作Docker镜像

 * 创建一个Docker容器，基础镜像为ubuntu的容器
```
root@oo-lab:/# docker create -it --name homework4 ubuntu /bin/bash
```

 * 接着启动这个容器，然后用`df -hT`命令查看当前的挂载情况
```
root@oo-lab:/# docker start -i homework4

在另一个终端中
root@oo-lab:/# df -hT
```
 * 有这样一条挂载记录
```
none  aufs  19G 7.0G  11G 41% /var/lib/docker/aufs/mnt/4d18f3bcf5c63d5c75cc1efed46a19b9a536a9e523569340dfd7e7c405dfb620
```
 * 这个目录就代表Docker根据ubuntu镜像，将其使用aufs联合文件系统挂载到`4d18f3bcf5c`这个挂载点下，容器会使用这个挂载点。
 * 到`/var/lib/docker/aufs/layers`查看层级信息
```
root@oo-lab:/var/lib/docker/aufs/layers# cat 4d18f3bcf5c63d5c75cc1efed46a19b9a536a9e523569340dfd7e7c405dfb620
4d18f3bcf5c63d5c75cc1efed46a19b9a536a9e523569340dfd7e7c405dfb620-init
34f74c50fa62e6aeb210058f900053d22e37de46d334c254f25195e2d8c7feaf
9112564abcd82ee013ebc0776cfd8af258cacd55346d35b6fd2133224b0a883b
706b5f3a094bda1e854bc2bc20552701cab2eda8e7757195dd8407f60044ec99
dbdf18520e2e69a20b0effd07cff0a33ab7f6b72ac968056353c486267fc1ef4
d762bd2635d798c2430486853c1ac1ee1253575ce01d8d82685b445ace5aa1fb
```
 * 可以看到`4d18f3bcf5c`和`4d18f3bcf5c-init`属于容器运行时创建生成的，而底下几层则是ubuntu基础镜像中存在的。其中`4d18f3bcf5c`是最上层的可读可写层。
 * 具体的文件都在`/var/lib/docker/aufs/diff`中，用`cp`命令将其保存到自己创建的目录下
```
root@oo-lab:/var/lib/docker/aufs/diff# mkdir /home/pkusei/my_images
root@oo-lab:/var/lib/docker/aufs/diff# cp -r d762bd2635d798c2430486853c1ac1ee1253575ce01d8d82685b445ace5aa1fb/ \
/home/pkusei/my_images/0
root@oo-lab:/var/lib/docker/aufs/diff# cp -r dbdf18520e2e69a20b0effd07cff0a33ab7f6b72ac968056353c486267fc1ef4/ \
/home/pkusei/my_images/1
root@oo-lab:/var/lib/docker/aufs/diff# cp -r 706b5f3a094bda1e854bc2bc20552701cab2eda8e7757195dd8407f60044ec99/ \
/home/pkusei/my_images/2
root@oo-lab:/var/lib/docker/aufs/diff# cp -r 9112564abcd82ee013ebc0776cfd8af258cacd55346d35b6fd2133224b0a883b/ \
/home/pkusei/my_images/3
root@oo-lab:/var/lib/docker/aufs/diff# cp -r 34f74c50fa62e6aeb210058f900053d22e37de46d334c254f25195e2d8c7feaf/ \
/home/pkusei/my_images/4
```

 * 在容器中安装软件包
```
root@8c026972c69a:/# apt update
root@8c026972c69a:/# apt install vim
root@8c026972c69a:/# apt install gcc
root@8c026972c69a:/# apt install python
```

 * 软件包的内容会写到最高层读写层中，即`4d18f3bcf5c`中，将其保存到`/home/pkusei/my_images`中
```
root@oo-lab:/var/lib/docker/aufs/diff# cp -r 4d18f3bcf5c63d5c75cc1efed46a19b9a536a9e523569340dfd7e7c405dfb620 \
/home/pkusei/my_images/software
```

 * 创建挂载点`/home/pkusei/my_mnt`
```
root@oo-lab:# mkdir /home/pkusei/my_mnt
```

 * 使用aufs挂载保存在`/home/pkusei/my_images/`中的所有镜像到`/home/pkusei/my_mnt`下
```
root@oo-lab:/# mount -t aufs -o br=/home/pkusei/my_images/software=ro\
:/home/pkusei/my_images/4=ro:/home/pkusei/my_images/3=ro\
:/home/pkusei/my_images/2=ro:/home/pkusei/my_images/1=ro\
:/home/pkusei/my_images/0=ro none /home/pkusei/my_mnt
```

 * 进入`/home/pkusei/my_mnt`目录，使用`docker import`命令从本地目录导入镜像
```
root@oo-lab:/home/pkusei/my_mnt# tar -c . | docker import - hw4_image
```

 * 从镜像`hw4_image`中创建运行容器
```
root@oo-lab:/# docker run -it --name test_hw4_image hw4_image /bin/bash
```
 * 可以使用之前装的`vim`、`gcc`、`python`等软件包。
```
root@fbcf64881685:/# python
Python 2.7.12 (default, Nov 19 2016, 06:48:10)
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
