# AppArmor

参考：http://www.lenky.info/archives/2014/05/2405

https://kubernetes.io/zh/docs/tutorials/clusters/apparmor/

## 简介

AppArmor是一款与SeLinux类似的安全框架/工具，其主要作用是控制应用程序的各种权限，例如对某个目录/文件的读/写，对网络端口的打开/读/写等等。

在 CentOS 7 中，SELinux 合并进了内核并且默认启用强制Enforcing模式，与之不同的是，openSUSE 和 Ubuntu 使用的是 AppArmor 。

## 常识部分

- Apparmor的profile配置文件均保存在目录`/etc/apparmor.d`

- Apparmor使用内核标准安全文件系统机制`（/sys/kernel/security）`来加载和监控profiles文件。而虚拟文件`/sys/kernel/security/apparmor/profiles`里记录了当前加载的profiles文件

- 一个profile文件定义好之后，当其对应的应用程序启动（比如firefox），它也就自动激活生效。有两种模式，分别为：

  - complain：应用程序发生了超过其权限之外的动作时，Apparmor会进行log记录，但是不会阻止应用程序相关动作的成功执行。
  - enforce：应用程序发生了超过其权限之外的动作时，Apparmor会进行log记录，并且会阻止应用程序相关动作的成功执行。

- 通过命令aa-complain或aa-enforce可以切换profile文件的状态。这需要先安装对应的utils工具：`apt-get install apparmor-utils`

  ```shell
  lenky@local:~$ sudo aa-complain tcpdump
  Setting /usr/sbin/tcpdump to complain mode.
  lenky@local:~$ sudo aa-enforce tcpdump
  Setting /usr/sbin/tcpdump to enforce mode
  # 做了这种修改后需要重启apparmor，Apparmor的启动、停止等操作的相关命令如下：
  Start : sudo /etc/init.d/apparmor start
  Stop : sudo /etc/init.d/apparmor stop
  reload: sudo /etc/init.d/apparmor reload
  Show status: sudo /etc/init.d/apparmor status
  ```

- 其他命令

  ```shell
  apt-get install apparmor-profiles # 安装额外的AppArmor-profile文件
  apparmor_status # 查看当前AppArmor的状态
  # aa-unconfined用来显示系统里那些拥有tcp/udp端口，但又未处于apparmor监控之下的进程
  aa-unconfined 
  # aa-genprof命令用来生成一个profile文件,实例：利用命令sudo aa-genprof nginx生成nginx的一个profile文件。
  aa-genprof nginx
  # 
  ```

  

## 使用 AppArmor 限制容器对资源的访问

### 前提

- Kubernetes 版本至少是 v1.4

- AppArmor 内核模块已启用

  ```shell
   cat /sys/module/apparmor/parameters/enabled
   Y
  ```

- 如果运行环境不是 Docker，它将拒绝运行带有 AppArmor 选项的 Pod

  ```shell
  kubectl get nodes -o=jsonpath=$'{range .items[*]}{@.metadata.name}: {@.status.nodeInfo.containerRuntimeVersion}\n{end}'
  ```

- 配置文件已加载 -- 通过指定每个容器都应使用 AppArmor 配置文件，AppArmor 应用于 Pod。如果指定的任何配置文件尚未加载到内核， Kubelet (>=v1.4) 将拒绝 Pod。通过检查 `/sys/kernel/security/apparmor/profiles` 文件，可以查看节点加载了哪些配置文件。例如:

  ```shell
  sudo cat /sys/kernel/security/apparmor/profiles | sort
  ```

还可以通过检查节点就绪状况消息来验证节点上的 AppArmor 支持

```shell
kubectl get nodes -o=jsonpath=$'{range .items[*]}{@.metadata.name}: {.status.conditions[?(@.reason=="KubeletReady")].message}\n{end}'
```

### pod指定使用的AppArmor 配置文件运行

```shell
container.apparmor.security.beta.kubernetes.io/<container_name>: <profile_ref>
```

`<container_name>` 的名称是容器的简称，用以描述简介

`<profile_ref>`指定配置文件，格式：

- `runtime/default` 应用运行时的默认配置
- `localhost/<profile_name>` 应用在名为 `<profile_name>` 的主机上加载的配置文件
- `unconfined` 表示不加载配置文件

生成配置文件事例：

```shell
NODES=(
    # The SSH-accessible domain names of your nodes
    gke-test-default-pool-239f5d02-gyn2.us-central1-a.my-k8s
    gke-test-default-pool-239f5d02-x1kf.us-central1-a.my-k8s
    gke-test-default-pool-239f5d02-xwux.us-central1-a.my-k8s)
    
# 生成k8s-apparmor-example-deny-write profile文件
for NODE in ${NODES[*]}; do ssh $NODE 'sudo apparmor_parser -q <<EOF
#include <tunables/global>

profile k8s-apparmor-example-deny-write flags=(attach_disconnected) {
  #include <abstractions/base>

  file,

  # Deny all file writes.
  deny /** w,
}
EOF'
done
```

还可以通过检查容器的 proc attr，直接验证容器的根进程是否以正确的配置文件运行

```shell
kubectl exec <pod_name> cat /proc/1/attr/current
```

# PodsecurityPolicy

参考：https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/

## 简介

*Pod 安全策略（Pod Security Policy）* 是集群级别的资源，它能够控制 Pod 规约 中与安全性相关的各个方面。 [PodSecurityPolicy](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.22/#podsecuritypolicy-v1beta1-policy) 对象定义了一组 Pod 运行时必须遵循的条件及相关字段的默认值，只有 Pod 满足这些条件 才会被系统接受。 Pod 安全策略允许管理员控制如下方面：

| **控制的角度**                 | **字段名称**                                                 |
| :----------------------------- | ------------------------------------------------------------ |
| 运行特权容器                   | [`privileged`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#privileged) |
| 使用宿主名字空间               | [`hostPID`、`hostIPC`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#host-namespaces) |
| 使用宿主的网络和端口           | [`hostNetwork`, `hostPorts`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#host-namespaces) |
| 控制卷类型的使用               | [`volumes`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#volumes-and-file-systems) |
| 使用宿主文件系统               | [`allowedHostPaths`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#volumes-and-file-systems) |
| 允许使用特定的 FlexVolume 驱动 | [`allowedFlexVolumes`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#flexvolume-drivers) |
| 分配拥有 Pod 卷的 FSGroup 账号 | [`fsGroup`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#volumes-and-file-systems) |
| 以只读方式访问根文件系统       | [`readOnlyRootFilesystem`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#volumes-and-file-systems) |
| 设置容器的用户和组 ID          | [`runAsUser`, `runAsGroup`, `supplementalGroups`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#users-and-groups) |
| 限制 root 账号特权级提升       | [`allowPrivilegeEscalation`, `defaultAllowPrivilegeEscalation`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#privilege-escalation) |
| Linux 权能字（Capabilities）   | [`defaultAddCapabilities`, `requiredDropCapabilities`, `allowedCapabilities`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#capabilities) |
| 设置容器的 SELinux 上下文      | [`seLinux`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#selinux) |
| 指定容器可以挂载的 proc 类型   | [`allowedProcMountTypes`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#allowedprocmounttypes) |
| 指定容器使用的 AppArmor 模版   | [annotations](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#apparmor) |
| 指定容器使用的 seccomp 模版    | [annotations](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#seccomp) |
| 指定容器使用的 sysctl 模版     | [`forbiddenSysctls`,`allowedUnsafeSysctls`](https://kubernetes.io/zh/docs/concepts/policy/pod-security-policy/#sysctl) |

*Pod 安全策略* 由设置和策略组成，它们能够控制 Pod 访问的安全特征。这些设置分为如下三类：

- *基于布尔值控制* ：这种类型的字段默认为最严格限制的值。
- *基于被允许的值集合控制* ：这种类型的字段会与这组值进行对比，以确认值被允许。
- *基于策略控制* ：设置项通过一种策略提供的机制来生成该值，这种机制能够确保指定的值落在被允许的这组值中。

## 启用PodsecurityPolicy

```shell
# kube-apiserver配置文件添加配置：/etc/kubernetes/manifests/kube-apiserver.yaml
- --enable-admission-plugins=NodeRestriction,PodSecurityPolicy
# 重启kubelet
systemctl restart kubelet
```





