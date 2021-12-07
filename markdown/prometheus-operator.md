

# Kube-prometheus

参考：https://github.com/prometheus-operator/kube-prometheus

https://github.com/prometheus-operator/prometheus-operator

## 架构图

![image-20210808171928437](/Users/xin/Library/Application Support/typora-user-images/image-20210808171928437.png)

## 安装步骤

- 拉取源码

```git clone git@github.com:prometheus-operator/kube-prometheus.git```

### 代码文件简介

#### Yaml文件位置

```
cd kube-prometheus/manifests
```

![image-20210808202341634](/Users/xin/Library/Application Support/typora-user-images/image-20210808202341634.png)

#### 组成

主要由以下几种组成

alertmanage-* : alertmanage 相关yaml

blackbox-exporter-*： blackbox-exporter相关yaml文件，blackbox-exporter资料：https://github.com/prometheus/blackbox_exporter

node-exporter-* ： node exporter 相关yaml文件 (node指标)

kube-state-metrics*：kube-state-metrics 相关yaml文件(pod状态指标) 

prometheus-adapter*

prometheus-*：prometheus相关

kubernetes-* :kubernetes(kubelet等)相关组件采集

*-prometheusRule:指标采集及告警的规则

#### yaml调整

- kubernetes-*：kubernetes相关组件采集

拓展：kubernetes相关组件的信息采集主要来从集群主机的1025*端口获取metrics数据

```
[root@dce-10-23-3-215 ~]# ss -ntlp |grep 1025
LISTEN     0      4096      [::]:10250                 [::]:*                   users:(("kubelet",pid=11901,fd=33))
LISTEN     0      4096      [::]:10251                 [::]:*                   users:(("kube-scheduler",pid=20025,fd=9))
LISTEN     0      4096      [::]:10252                 [::]:*                   users:(("kube-controller",pid=19885,fd=5))
LISTEN     0      4096      [::]:10253                 [::]:*                   users:(("kube-keepalived",pid=25414,fd=10))
LISTEN     0      4096      [::]:10254                 [::]:*                   users:(("kube-keepalived",pid=25414,fd=11))
LISTEN     0      4096      [::]:10255                 [::]:*                   users:(("kubelet",pid=11901,fd=31))
LISTEN     0      4096      [::]:10256                 [::]:*                   users:(("kube-proxy",pid=22076,fd=18))
LISTEN     0      4096      [::]:10257                 [::]:*                   users:(("kube-controller",pid=19885,fd=6))
LISTEN     0      4096      [::]:10258                 [::]:*                   users:(("keepalived-clou",pid=28449,fd=3))
LISTEN     0      4096      [::]:10259                 [::]:*                   users:(("kube-scheduler",pid=20025,fd=10))
```

其中kubelet的metrics采集端口，10250是https的，10255是http的

kube-scheduler的metrics采集端，10259是https的，10251是http的

Kube-controller的metrics采集端，10257是https的，10252是http的

测试：在主机上curl相关端口/metrics，即可获取相关metrics，如获取kubelet相关指标只需```curl http://127.0.0.1:10255/metrics```即可

- kubernetes-serviceMonitorKubeScheduler.yaml

- kubernetes-serviceMonitorKubeControllerManager.yaml

- kubernetes-serviceMonitorKubelet.yaml

  Yaml文件中相关信息采集默认采用https的端口，即10250端口，这样我们需要将port的端口改为http-metrics

  ![image-20210808213221801](/Users/xin/Library/Application Support/typora-user-images/image-20210808213221801.png)

#### 部署

```kubectl apply .```

查看crd文件

```
kubeclt get crd |grep monitoring.coreos.com
```

## 自定义operator监控项

### 步骤

- 创建一个ServiceMonitor对象，用户Prometheus添加监控项

  查看已存在的ServiceMonitor：

  ![image-20210808221548064](/Users/xin/Library/Application Support/typora-user-images/image-20210808221548064.png)

  ![image-20210808222002436](/Users/xin/Library/Application Support/typora-user-images/image-20210808222002436.png)

- 为ServiceMonitor对象关联metrics数据接口的一个Service对象

  ![image-20210808222254678](/Users/xin/Library/Application Support/typora-user-images/image-20210808222254678.png)

  ![image-20210808222407573](/Users/xin/Library/Application Support/typora-user-images/image-20210808222407573.png)

- 确保Service对象可以正确获取metrics数据

## 自定义operator告警

### prometheus告警规则

注意：Prometheus 的所有配置文件都会放在容器的/etc/prometheus位置

![image-20210808235548562](/Users/xin/Library/Application Support/typora-user-images/image-20210808235548562.png)

其中PrometheusRule的对应配置文件放在rules目录下：

![image-20210808235647663](/Users/xin/Library/Application Support/typora-user-images/image-20210808235647663.png)





- 新建一个PrometheusRule对象(或者在原有的上面修改)

  新建PrometheusRule的注意：

  查看crd资源 prometheuses.monitoring.coreos.com ，里面的ruleSelector选项

  ![image-20210808231000372](/Users/xin/Library/Application Support/typora-user-images/image-20210808231000372.png)

  新建的PrometheusRule资源要包含ruleSelector里面的标签

- 查看已有的PrometheusRule

  ```
  kubectl get PrometheusRule
  ```

  ![image-20210808231704795](/Users/xin/Library/Application Support/typora-user-images/image-20210808231704795.png)

### alertmanger配置

- 查看alertmanagers.monitoring.coreos.com信息

  ![image-20210808233253791](/Users/xin/Library/Application Support/typora-user-images/image-20210808233253791.png)

alertmanager的配置文件为secret格式，查看configSecret对应的secret资源对象

![image-20210808233500916](/Users/xin/Library/Application Support/typora-user-images/image-20210808233500916.png)

转译一下看一下内容：

![image-20210808233618555](/Users/xin/Library/Application Support/typora-user-images/image-20210808233618555.png)

如果需要修改配置文件的话，需要先将配置写在一个文件中，修改后进行base64编码，将结果替换到这个secret中

## Prometheus operator高级配置

***注意：prometheuses.monitoring.coreos.com 所有可编辑的参数可参考：https://github.com/prometheus-operator/prometheus-operator/blob/master/Documentation/api.md#prometheus***

#### 添加服务发现

- 将配置写入一个文件

  ![image-20210809001834042](/Users/xin/Library/Application Support/typora-user-images/image-20210809001834042.png)

- 创建secret

  ```
  kubectl create secret generic test-job --from-file=test-job.yaml
  ```

- 修改prometheuses.monitoring.coreos.com

  添加additionalScrapeConfigs键值

  ![image-20210809002122762](/Users/xin/Library/Application Support/typora-user-images/image-20210809002122762.png)

- 查看配置

  ![image-20210809002243815](/Users/xin/Library/Application Support/typora-user-images/image-20210809002243815.png)

### 数据持久化配置

![image-20210809004112446](/Users/xin/Library/Application Support/typora-user-images/image-20210809004112446.png)













































