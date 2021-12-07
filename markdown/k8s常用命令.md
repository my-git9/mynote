# 调度

污点：

```
	kubectl taint nodes node1 key=value:NoSchedule
	kubectl taint nodes node1 key=value:NoExecute
	kubectl taint nodes node1 key=value:PreferNoSchedule
	去污：
		kubectl taint nodes kube11 key:NoSchedule-
	设置节点为不可调度：
		kubectl ucordon <node name>
	可调度：kubectl uncordon <node name>
驱除pod:
	kubectl drain <node name>
	kubectl drain [node-name] --force --ignore-daemonsets --delete-local-data #忽略daemonset
```



# 权限

## 生成kubeconfig管理集群

- 准备clusterrole，这里面直接使用cluster-admin

- 创建serviceaccount

  ```yaml
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: test
    namespace: default
  ```

- 创建clusterrolebinding或rolebinding

  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRoleBinding
  metadata:
    name: test-rolebinding
    namespace: default
  subjects:
  - kind: ServiceAccount
    namespace: default
    name: test
  roleRef:
    kind: ClusterRole
    name: cluster-admin
    apiGroup: rbac.authorization.k8s.io
  ```

- 获取serviceaccount 的token

  ```shell
  TOKEN_NAME=$(kubectl get secret -n default | grep test | awk '{print $1}')
  TOKEN=$(kubectl get secret $TOKEN_NAME  -o jsonpath={.data.token} -n default | base64 -d)
  ```

- 配置kubeconfig

  ```shell
  kubectl config set-cluster kubernetes --embed-certs=true --server="${API_SERVER}" --certificate-authority=/etc/kubernetes/pki/ca.crt --kubeconfig=test.kubeconfig
  kubectl config set-credentials test --token=$TOKEN --kubeconfig=test.kubeconfig
  kubectl config set-context test --cluster=kubernetes --user=test --kubeconfig=test.kubeconfig
  kubectl config set current-context test --kubeconfig=test.kubeconfig
  kubectl config set contexts.test.namespace default --kubeconfig=test.kubeconfig
  ```

- 测试

  ```shell
  kubectl get po --kubeconfig=test.kubeconfig
  ```

- 脚本---针对单个命名空间管理员权限

  ```shell
  NAME=$1
  API_SERVER="https://10.23.3.116:16443" #更换集群 apiserver 地址。
  mkdir $NAME
  #if [ $? -eq 0 ]; then
  #  echo "Account already exists."
  #  exit 1
  #fi
  kubectl get ns $NAME
  if [ $? -eq 0 ]; then
    echo "Namespaces already exists."
  #  exit 1
  fi
  echo "Start create kubeconfig for $i..."
  cat << EOF  > $NAME/$NAME.yaml
  apiVersion: v1
  kind: Namespace
  metadata:
    name: $NAME
  ---
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: $NAME
    namespace: default
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: $NAME-rolebinding
    namespace: $NAME
  subjects:
  - kind: ServiceAccount
    namespace: default
    name: $NAME
  roleRef:
    kind: ClusterRole
    name: mesh
    apiGroup: rbac.authorization.k8s.io
  EOF
  kubectl apply -f $NAME/$NAME.yaml
  TOKEN_NAME=$(kubectl get secret -n default | grep $NAME | awk '{print $1}')
  TOKEN=$(kubectl get secret $TOKEN_NAME  -o jsonpath={.data.token} -n default | base64 -d)
  kubectl config set-cluster kubernetes --embed-certs=true --server="${API_SERVER}" --certificate-authority=/etc/daocloud/dce/certs/ca.crt --kubeconfig=./$NAME/$NAME.kubeconfig
  kubectl config set-credentials $NAME --token=$TOKEN --kubeconfig=./$NAME/$NAME.kubeconfig
  kubectl config set-context $NAME --cluster=kubernetes --user=$NAME --kubeconfig=./$NAME/$NAME.kubeconfig
  kubectl config set current-context  $NAME  --kubeconfig=./$NAME/$NAME.kubeconfig
  kubectl config set contexts.$NAME.namespace $NAME --kubeconfig=./$NAME/$NAME.kubeconfig
  ```

- 注意

  - 如果生成针对多个命名空间的管理员权限，只需要在多个命名空间下创rolebinding指向某一个命名空间下的serviceaccount即可