# namespace
作用：隔离内核资源
## 分类
- Mount namespace：文件系统挂载点
- UTS namespace：主机名
- IPC namespace：POSIX进程间通信消息 队列
- PID namespace：进程PID数字空间
- network namespace：IP地址
- user namespace：user

Linux的namespace给里面的进程造成了两个错觉
- 它是系统里唯一的进程
- 它独享系统的所有资源
默认情况下，Linux进程处在和宿主机相同的namespace，即初始的根namespace里，默 认享有全局系统资源。
# networknamespaces简单操作

## 基本操作

- 创建namespace

  ```shell
  ip netns add netns1
  ```

- 进入网络命名空间，并做一些配置

  ```shell
  [root@10-23-22-99 ~]# ip netns exec netns1 ip link list
  1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN mode DEFAULT group default qlen 1000
      link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
  ```

- 列出系统namespace
```shell
[root@10-23-22-99 ~]# ip netns list
netns1
```
- 删除namespace

```shell
ip netns delete netns1
# 上面这条命令实际上并没有删除netns1这个network namespace， 它只是移除了这个network namespace对应的挂载点。只要里面还有进程运行着，network namespace便会一直存在。
```

## 简单配置

- network namespace自带的lo设备状 态还是DOWN的，因此，当尝试访问本地回环地址时，网络也是不通的。

```shell
[root@10-23-22-99 ~]# ip netns exec netns1 ping 127.0.0.1
connect: 网络不可达
```

- 如果想访问本地回环地址，首先需要进入netns1这个 network namespace，把设备状态设置成UP

```shell
[root@10-23-22-99 ~]# ip netns exec netns1 ip link set dev lo up

[root@10-23-22-99 ~]# ip netns exec netns1 ping 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.071 ms
```

- 如果我们想与外界 (比如主机上的网卡)进行通信，就需要在namespace里再创建一对虚拟的 以太网卡，即所谓的veth pair，veth pair总是成对出现且相互连接，它就像Linux的双向管道(pipe)，报文从veth pair一端进去就会由另一端收到。

  下面的命令将创建一对虚拟以太网卡，然后把veth pair的一端放到 netns1 network namespace。

  ```shell
  # 创建一对veth pair
  [root@10-23-22-99 ~]# ip link add veth0 type veth peer name veth1
  # 将其中一端放入netns1 namespace
  [root@10-23-22-99 ~]# ip link set veth1 netns netns1
  ```

  将两张网卡设置成UP状态，并绑定ip

  ```shell
  [root@10-23-22-99 ~]# ip netns exec netns1 ifconfig veth1 10.1.1.1/24 up
  [root@10-23-22-99 ~]# ifconfig veth0 10.1.1.2/24 up
  ```

  测试网络联通

  ```shell
  # 外面ping里面
  [root@10-23-22-99 ~]# ping 10.1.1.1
  PING 10.1.1.1 (10.1.1.1) 56(84) bytes of data.
  64 bytes from 10.1.1.1: icmp_seq=1 ttl=64 time=0.345 ms
  64 bytes from 10.1.1.1: icmp_seq=2 ttl=64 time=0.062 ms
  
  # 里面ping外面
  [root@10-23-22-99 ~]# ip netns exec netns1 ping  10.1.1.2
  PING 10.1.1.2 (10.1.1.2) 56(84) bytes of data.
  64 bytes from 10.1.1.2: icmp_seq=1 ttl=64 time=0.285 ms
  ```

- 不同namespace 路由表和防火墙隔离

  ```shell
  root@10-23-22-99 ~]# ip netns exec netns1 iptables -L -n
  Chain INPUT (policy ACCEPT)
  target     prot opt source               destination
  
  Chain FORWARD (policy ACCEPT)
  target     prot opt source               destination
  
  Chain OUTPUT (policy ACCEPT)
  target     prot opt source               destination
  
  [root@10-23-22-99 ~]# ip netns exec netns1 route -n
  Kernel IP routing table
  Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
  10.1.1.0        0.0.0.0         255.255.255.0   U     0      0        0 veth1
  ```

- 将veth1设备移动到1命名空间下

  ```shell
  [root@10-23-22-99 ~]# ip netns exec netns1 ip link set veth1 netns 1
  [root@10-23-22-99 ~]# ip netns exec netns1 route -n
  Kernel IP routing table
  Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
  
  # 再移回去
  [root@10-23-22-99 ~]# nsenter -m -n -t 1
  [root@10-23-22-99 /]# ip link set veth1 netns netns1
  
  [root@10-23-22-99 ~]# ip netns exec netns1 ip link
  1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
      link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
  4: veth1@if5: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000
      link/ether 32:64:cf:31:d5:d2 brd ff:ff:ff:ff:ff:ff link-netnsid 0
  ```

  

## 维持**namespace**存在:**/proc/PID/ns**

```shell
[root@10-23-22-99 ~]# ls -l /proc/1/ns/
总用量 0
lrwxrwxrwx. 1 root root 0 10月 28 21:57 ipc -> ipc:[4026531839]
lrwxrwxrwx. 1 root root 0 10月 28 21:54 mnt -> mnt:[4026531840]
lrwxrwxrwx. 1 root root 0 10月 28 21:54 net -> net:[4026531956]
lrwxrwxrwx. 1 root root 0 10月 28 21:57 pid -> pid:[4026531836]
lrwxrwxrwx. 1 root root 0 10月 28 21:57 user -> user:[4026531837]
lrwxrwxrwx. 1 root root 0 10月 28 21:57 uts -> uts:[4026531838]
```

### 作用

- 确定某两个进程是否属于同一个 namespace。如果两个进程在同一个namespace中，那么这两个进 程/proc/PID/ns目录下对应符号链接文件的inode数字(即上文例子中[]内 的数字，例如4026531839，也可以通过stat()系统调用获取返回结构体的 st_ino字段)会是一样的。
- 当我们打开这 些文件时，只要文件描述符保持open状态，对应的namespace就会一直存 在，哪怕这个namespace里的所有进程都终止运行了。**之前版本的Linux内核，要想保持namespace存在，需要在 namespace里放一个进程(当然，不一定是运行中的)，这种做法在一些场 景下有些笨重(虽然Kubernetes就是这么做的)。因此，Linux内核提供的黑 科技允许:只要打开文件描述符，不需要进程存在也能保持namespace存 在!**









