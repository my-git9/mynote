

## rule规则示例

1、pod.cpu.utilization cpu使用率

2、pod.memory.utilization memory使用率

3、pod.disk.utilization disk使用率

4、pod.network.receive_bytes 网络流入流量

5、pod.network.transmit_bytes 网络流出流量

6、pod.restarted.count pod重启次数

7、pod.status.phase.not.running pod处于非运行状态次数

总共需要以上7个监控指标，加上pod_name pod_ip appId unitId unitNo的label

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  annotations:
    meta.helm.sh/release-name: dx-insight
    meta.helm.sh/release-namespace: dx-insight
  generation: 4
  labels:
    app: prometheus-operator
    app.kubernetes.io/managed-by: Helm
    chart: prometheus-operator-9.3.2
    heritage: Helm
    operated_by: admin
    release: dx-insight
  name: dsp-relabel.record
  namespace: dx-insight
spec:
  groups:
  - name: node.rules
    rules:
    - expr: |-
        label_join(
            label_join(label_join(label_join(kube_pod_labels, 'app_id', '', 'label_appId'), 'unit_id', '', 'label_unitId'), 'unit_no', '' ,'label_unitNo')
          * on(namespace, pod) group_left(host_ip, node, pod_ip)
            kube_pod_info,
          'pod_name', '', 'pod'
        )
      record: kube_pod_labels:label
    - expr: |-
        (
          sum(rate(container_cpu_usage_seconds_total{image!=""}[1m])) by (namespace, pod)
          /
          (sum(container_spec_cpu_quota{image!=""} / 100000 ) by (namespace, pod)) * 100
        ) * on (namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_cpu_utilization
    - expr: |-
        (
          sum(container_memory_working_set_bytes{image!=""}) by (namespace, pod)
          /
          sum(container_spec_memory_limit_bytes{image!=""}) by (namespace,pod)
          * 100
        ) * on (namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_memory_utilization
    - expr: |-
        (
          sum(container_fs_usage_bytes{image!="", container!="POD"}) by (namespace, pod)
          /1024/1024/1024/10*100
        ) * on (namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_disk_utilization
    - expr: |-
        sum by (namespace, pod) (irate(container_network_receive_bytes_total[5m]))
        * on (namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_network_receive_bytes
    - expr: |-
        sum by (namespace, pod) (irate(container_network_transmit_bytes_total[5m]))
        * on (namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_network_transmit_bytes
    - expr: |-
        sum(increase(kube_pod_container_status_restarts_total[5m])) by (namespace, pod)
        * on(namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_restarted_count
    - expr: |-
        sum(kube_pod_status_phase{phase!="Running"}) by (namespace, pod)
        * on(namespace, pod) group_left(pod_name, app_id, unit_id, unit_no, host_ip, node, pod_ip)
        kube_pod_labels:label
      record: pod_status_phase_not_running
```

