# 第一次作业

## 虚拟机和容器技术

### 虚拟机技术

虚拟机技术为用户提供一个完整的虚拟操作系统，包括完整的系统内核和系统镜像。其中，CPU的虚拟机技术为每台虚拟机提供处理器，每个虚拟机操作系统独享虚拟化后的CPU、内存、硬盘和IO设备等资源。

### 容器技术

容器为每个应用程序提供隔离和独立的运行空间，每个容器内包含一个完整的用户空间，每个容器内的变动不会影响其他容器的运行环境。容器之间共享一个系统内核，直接共享内存和CPU等资源。

---

## Spark和Mesos运行

### 运行环境

 * Host环境
 	* `OS: macOS Sierra 10.12.3`
 	* `Processor: 2.6 GHz Intel Core i5`
 	* `Memory: 8GB 1600 MHz DDR3`

 * 虚拟机环境
 	* `OS: Linux Ubuntu 16.04.2 LTS`
 	* `Processor: 2 cores`
 	* `Memory: 4GB`
 	* `Mesos: 1.1.0`
 	* `Spark: 2.1.0`

### 运行命令

 * 使用`spark-shell`来提交任务，运行`scala`脚本来创建job
```scala
val textFile = sc.textFile("/home/.../anyText")
val counts = textFile.flatMap(line => line.split(" "))
                .map(word => (word, 1))
                .reduceByKey(_ + _)
counts.saveAsTextFile("/home/.../anyDirectory")
```
 * 单核运行`spark-shell`的命令
```sh
./bin/spark-shell --master mesos://127.0.0.1:5050
				  --total-executor-cores 1
				  --supervise
				  --executor-memory 2G
```

 * 双核运行`spark-shell`的命令
```sh
./bin/spark-shell --master mesos://127.0.0.1:5050
				  --total-executor-cores 2
				  --supervise
				  --executor-memory 2G
```

### 测试文件

使用`C++`生成50MB多的文本文件，共计12,000,000个伪单词，单词长度从1到7不等。<br />
生成文件的代码如下：
```C++
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <ctime>
using namespace std;

const int N = 12000000;
int main() {
	srand(time(0));
	freopen("test.txt", "w", stdout);
	for(int i = 1; i <= N; i++) {
		int length = rand() % 7 + 1;
		while(length--) {
			putchar(rand() % 26 + 'a');
		}
		putchar(' ');
	}
	fclose(stdout);
	return 0;
}
```

### 运行结果

 * 单核运行结果
 	* Mesos资源使用情况
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/1core_mesos.png)

 	* Job整体运行时间
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/1core_overview.png)

 	* Map阶段运行时间
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/1core_map.png)

 	* Reduce阶段运行时间
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/1core_reduce.png)

 * 双核运行结果
 	* Mesos资源使用情况
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/2core_mesos.png)

 	* Job整体运行时间
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/2core_overview.png)

 	* Map阶段运行时间
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/2core_map.png)

 	* Reduce阶段运行时间
 	![](https://github.com/wzc1995/OperatingSystemLab/blob/master/Homework 1/2core_reduce.png)

### 时间对比
可以看到处理大规模数据时，单核确实会比双核慢。但如果待处理的文件较小，两者则基本没有区别，考虑并行通信时间甚至双核会比单核慢。<br />

### 总结
`Spark`的Master直接连接到`Mesos`上，`Spark`的驱动程序会向其Master发送任务，Master也就是`Mesos`会接收到任务然后分配资源和调度任务，运行结束后，结果会返回到`Spark Context`中。<br /><br />
整体来看，配置`Mesos`和`Spark`的过程并不是很困难，由于我之前对于分布式框架有过一些了解，所以在安装中出现的细节问题不多。<br /><br />
`Mesos`的`make`时间以及`make check`和`make install`的时间有些长，中途虚拟机待机引起了多次崩溃。<br /><br />
仔细阅读每个命令后边的`-h`很有帮助，网上的资料有些是过时的。填写`Spark`的配置文件过程中，没有注意`uri`的格式，导致Mesos无法为其分配资源，资源开头一定要是`http://`、`hdfs://`或`file://`等<br /><br />
