# 生产消息分区原理

## 分区

Kafka 有主题（Topic）的概念，它是承载真实数据的逻辑容器，而在主题之下还分为若干个分区，也就是说 Kafka 的消息组织方式实际上是三级结构：主题 - 分区 - 消息。主题下的每条消息只会保存在某一个分区中，而不会在多个分区中被保存多份。官网上的这张图非常清晰地展示了 Kafka 的三级结构，如下所示：

![image-20221122165341926](https://tva1.sinaimg.cn/large/008vxvgGgy1h8e08wc6fdj311q0f0t9l.jpg)

**分区的作用就是提供负载均衡的能力，或者说对数据进行分区的主要原因，就是为了实现系统的高伸缩性（Scalability）**。不同的分区能够被放置到不同节点的机器上，而数据的读写操作也都是针对分区这个粒度而进行的，这样**每个节点的机器都能独立地执行各自分区的读写请求处理**。并且，我们还可以通过添加新的节点机器来增加整体系统的吞吐量。

##  分区策略

**所谓分区策略是决定生产者将消息发送到哪个分区的算法**。Kafka 为我们提供了默认的分区策略，同时它也支持你自定义分区策略。

如果要自定义分区策略，需要显式地配置生产者端的参数**partitioner.class**。

在编写生产者程序时，可以编写一个具体的类实现**org.apache.kafka.clients.producer.Partitioner**接口。这个接口也很简单，只定义了两个方法：partition()和close()，通常只需要实现最重要的 partition 方法。我们来看看这个方法的方法签名：

```java
int partition(String topic, Object key, byte[] keyBytes, Object value, byte[] valueBytes, Cluster cluster);
```

**这里的topic、key、keyBytes、value和valueBytes都属于消息数据，cluster则是集群信息（比如当前 Kafka 集群共有多少主题、多少 Broker 等）**。

Kafka 提供这么多信息，就是希望让能够充分地利用这些信息对消息进行分区，计算出它要被发送到哪个分区中。只要你自己的实现类定义好了 partition 方法，同时设置partitioner.class参数为你自己实现类的 Full Qualified Name，那么生产者程序就会按照你的代码逻辑对消息进行分区。

常见的分区策略如下

### 轮询策略

也称 Round-robin 策略，即顺序分配。默认策略。

### 随机策略

也称 Randomness 策略。所谓随机就是我们随意地将消息放置到任意一个分区上。

如果要实现随机策略版的 partition 方法，很简单，只需要两行代码即可：

```java
List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
return ThreadLocalRandom.current().nextInt(partitions.size());
```

先计算出该主题总的分区数，然后随机地返回一个小于它的正整数。

随机策略是老版本生产者使用的分区策略，在新版本中已经改为轮询了。

### 按消息健保序策略

也称 Key-ordering 策略。

Kafka 允许为每条消息定义消息键，简称为 Key。这个 Key 的作用非常大，它可以是一个有着明确业务含义的字符串，比如客户代码、部门编号或是业务 ID 等；也可以用来表征消息元数据。

一旦消息被定义了 Key，那么就可以保证同一个 Key 的所有消息都进入到相同的分区里面，由于每个分区下的消息处理都是有顺序的，故这个策略被称为按消息键保序策略，如下图所示。

![image-20221123104457720](https://tva1.sinaimg.cn/large/008vxvgGgy1h8ev7j17t3j313i08i0t4.jpg)

实现这个策略的 partition 方法同样简单，只需要下面两行代码即可：

```java
List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
return Math.abs(key.hashCode()) % partitions.size();
```

前面提到的 Kafka 默认分区策略实际上同时实现了两种策略：如果指定了 Key，那么默认实现按消息键保序策略；如果没有指定 Key，则使用轮询策略。

这样可以保证同一个 key 消息的顺序性。

### 基于地理位置的分区策略

这种策略一般只针对那些大规模的 Kafka 集群，特别是跨城市、跨国家甚至是跨大洲的集群。

可以根据 Broker 所在的 IP 地址实现定制化的分区策略。比如下面这段代码：

```java
List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
return partitions.stream().filter(p -> isSouth(p.leader().host())).map(PartitionInfo::partition).findAny().get();
```



# 生产者压缩算法

压缩（compression）秉承了用时间去换空间的经典 trade-off 思想，具体来说就是用 CPU 时间去换磁盘空间或网络 I/O 传输量，希望以较小的 CPU 开销带来更少的磁盘占用或更少的网络 I/O 传输。在 Kafka 中，压缩也是用来做这件事的。

## 压缩方式

目前 Kafka 共有两大类消息格式，社区分别称之为 V1 版本和 V2 版本。**V2 版本是 Kafka 0.11.0.0 中正式引入的**。

不论是哪个版本，Kafka 的消息层次都分为两层：**消息集合（message set）以及消息（message）**。一个消息集合中包含若干条日志项（record item），而日志项才是真正封装消息的地方。Kafka 底层的消息日志由一系列消息集合日志项组成。Kafka 通常不会直接操作具体的一条条消息，它总是**在消息集合这个层面上进行写入操作**。

V2 版本主要是针对 V1 版本的一些弊端做了修正：

- 原来在 V1 版本中，每条消息都需要执行 CRC 校验，但有些情况下消息的 CRC 值是会发生变化的。比如在 Broker 端可能会对消息时间戳字段进行更新，那么重新计算之后的 CRC 值也会相应更新；再比如 Broker 端在执行消息格式转换时（主要是为了兼容老版本客户端程序），也会带来 CRC 值的变化。鉴于这些情况，再对每条消息都执行 CRC 校验就有点没必要了，不仅浪费空间还耽误 CPU 时间，因此**在 V2 版本中，消息的 CRC 校验工作就被移到了消息集合这一层**。
- V2 版本还有一个和压缩息息相关的改进，就是保存压缩消息的方法发生了变化。之前 V1 版本中保存压缩消息的方法是把多条消息进行压缩然后保存到外层消息的消息体字段中；而 V2 版本的做法是对整个消息集合进行压缩。显然后者应该比前者有更好的压缩效果。

经测试。在相同条件下，不论是否启用压缩，V2 版本都比 V1 版本节省磁盘空间。当启用压缩时，这种节省空间的效果更加明显，就像下面这两张图展示的那样：

![image-20221124175652320](https://tva1.sinaimg.cn/large/008vxvgGgy1h8gdb8af2bj312c0cogm1.jpg)

消息（v1叫message，v2叫record）是分批次（batch）读写的，batch是kafka读写（网络传输和文件读写）的基本单位，不同版本，对相同（或者叫相似）的概念，叫法不一样。
v1（kafka 0.11.0之前）:message set, message
v2（kafka 0.11.0以后）:record batch,record
其中record batch对英语message set，record对应于message。
一个record batch（message set）可以包含多个record（message）。

## 何时压缩

在 Kafka 中，压缩可能发生在两个地方：**生产者端和 Broker 端**。

生产者程序中配置 compression.type 参数即表示启用指定类型的压缩算法。比如下面这段程序代码展示了如何构建一个开启 GZIP 的 Producer 对象：

```java
 Properties props = new Properties();
 props.put("bootstrap.servers", "localhost:9092");
 props.put("acks", "all");
 props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
 props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
 // 开启GZIP压缩
 props.put("compression.type", "gzip");
 
 Producer<String, String> producer = new KafkaProducer<>(props);
```

这里比较关键的代码行是 `props.put("compression.type", "gzip")`，它表明该 Producer 的压缩算法使用的是 GZIP。这样 Producer 启动后生产的每个消息集合都是经 GZIP 压缩过的，故而能很好地节省网络传输带宽以及 Kafka Broker 端的磁盘占用。

大部分情况下 Broker 从 Producer 端接收到消息后仅仅是原封不动地保存而不会对其进行任何修改，但是有两种例外情况就可能让 Broker 重新压缩消息。

- 情况一：Broker 端指定了和 Producer 端不同的压缩算法。

  Broker有个 `compression.type` 参数，默认值是 producer，这表示 Broker 端会“尊重”Producer 端使用的压缩算法。

  可一旦在 Broker 端设置了不同的 `compression.type` 值，可能会发生预料之外的压缩 / 解压缩操作，通常表现为 Broker 端 CPU 使用率飙升。

- 情况二：Broker 端发生了消息格式转换。

  所谓的消息格式转换主要是为了兼容老版本的消费者程序。在一个生产环境中，Kafka 集群中同时保存多种版本的消息格式非常常见。为了兼容老版本的格式，Broker 端会对新版本消息执行向老版本格式的转换。这个过程中会涉及消息的解压缩和重新压缩。除了这里的压缩之外，它还让 Kafka 丧失了**Zero Copy** 特性。

## 何时解压缩

**通常来说解压缩发生在消费者程序中**，也就是说 Producer 发送压缩消息到 Broker 后，Broker 照单全收并原样保存起来。当 Consumer 程序请求这部分消息时，Broker 依然原样发送出去，当消息到达 Consumer 端后，由 Consumer 自行解压缩还原成之前的消息。

**Producer 端压缩、Broker 端保持、Consumer 端解压缩**，Kafka 会将启用了哪种压缩算法封装进消息集合中，这样当 Consumer 读取到消息集合时，它自然就知道了这些消息使用的是哪种压缩算法。

除了在 Consumer 端解压缩，**Broker 端也会进行解压缩**。每个压缩过的消息集合在 Broker 端写入时都要发生解压缩操作，目的就是为了对消息执行各种验证。这个特性对 CPU 影响很大(新版好像有做优化：[[KAFKA-8106\] Reducing the allocation and copying of ByteBuffer when logValidator do validation. - ASF JIRA (apache.org)](https://issues.apache.org/jira/browse/KAFKA-8106))。

## 压缩算法对比

在 Kafka 2.1.0 版本之前，Kafka 支持 3 种压缩算法：**GZIP、Snappy 和 LZ4**。从 2.1.0 开始，Kafka 正式支持 **Zstandard 算法**（简写为 zstd）。

在实际使用中，GZIP、Snappy、LZ4 甚至是 zstd 的表现各有千秋。但对于 Kafka 而言，它们的性能测试结果却出奇得一致，即在**吞吐量方面：LZ4 > Snappy > zstd 和 GZIP**；而在**压缩比方面，zstd > LZ4 > GZIP > Snappy**。具体到物理资源，使用 Snappy 算法占用的网络带宽最多，zstd 最少，这是合理的，毕竟 zstd 就是要提供超高的压缩比；在 CPU 使用率方面，各个算法表现得差不多，只是在压缩时 Snappy 算法使用的 CPU 较多一些，而在解压缩时 GZIP 算法则可能使用更多的 CPU。

## 最佳实践

- Producer 端完成的压缩，启用压缩的一个条件就是 Producer 程序运行机器上的 CPU 资源要很充足。

- 如果环境中带宽资源有限，建议开启压缩。
- 客户端机器 CPU 资源有很多富余，建议你开启 zstd 压缩，这样能极大地节省网络资源消耗。

- 我们对不可抗拒的解压缩无能为力，但至少能规避掉那些意料之外的解压缩，如要兼容老版本而引入的解压缩操作就属于这类，尽量保证不要出现消息格式转换的情况。



# 消息持久化

## kafka持久化

Kafka 只对“已提交”的消息（committed message）做有限度的持久化保证。

当 Kafka 的**若干个Broker(可自定义多少个Broker)  成功地接收到一条消息并写入到日志文件后**，它们会告诉生产者程序这条消息已成功提交。此时，这条消息在 Kafka 看来就正式变为“已提交”消息了。

**有限度的持久化保证**：Kafka 不可能保证在任何情况下都做到不丢失消息，假如消息保存在 N 个 Kafka Broker 上，那么这个前提条件就是这 N 个 Broker 中至少有 1 个存活。

Kafka 是能做到不丢失消息的，只不过这些消息必须是已提交的消息，而且还要满足一定的条件。

## 消息丢失案例

### 1、生产者丢失数据

写了一个 Producer 应用向 Kafka 发送消息，最后发现 Kafka 没有保存。

目前 **Kafka Producer 是异步发送消息的**，也就是说如果调用的是 producer.send(msg) 这个 API，那么它通常会立即返回，但此时你不能认为消息发送已成功完成。调用 producer.send(msg) 就属于典型的“fire and forget”(发射后不管)，因此如果出现消息丢失，我们是无法知晓的。

解决此问题的方法非常简单：Producer 永远要使用带有回调通知的发送 API，也就是说**不要使用 producer.send(msg)，而要使用 producer.send(msg, callback)**。不要小瞧这里的 callback（回调），它能准确地告诉你消息是否真的提交成功了。一旦出现消息提交失败的情况，你就可以有针对性地进行处理。

核心论据在这里依然是成立的：**Kafka 依然不认为这条消息属于已提交消息，故对它不做任何持久化保证**。

### 2、消费者程序丢失数据

Consumer 端丢失数据主要体现在 Consumer 端要消费的消息不见了。Consumer 程序有个**“位移”**的概念，表示的是这个 Consumer 当前消费到的 Topic 分区的位置。

如图，对于 Consumer A 而言，它当前的位移值就是 9；Consumer B 的位移值是 11。

这里的“位移”类似于我们看书时使用的书签，它会标记我们当前阅读了多少页，下次翻书的时候我们能直接跳到书签页继续阅读。

消费消息有两个步骤：1、消费消息；2、更新位移

如果先更新位移，再消费消息，如果消费过程中出现宕机，再重新回来消费的时候，可能会丢失部分位移前未消费的数据。

 **维持先消费消息（阅读），再更新位移（书签）的顺序**可以能最大限度地保证消息不丢失。但是这种处理方式可能带来的问题是消息的重复处理

![image-20221128113515128](https://tva1.sinaimg.cn/large/008vxvgGgy1h8kore54kjj31220j2q4g.jpg)



另一种另开，当Consumer 程序从 Kafka 获取到消息后开启了**多个线程异步处理消息**，而 Consumer 程序自动地向前更新位移。假如其中某个线程运行失败了，它负责的消息没有被成功处理，但位移已经被更新了，因此这条消息对于 Consumer 而言实际上是丢失了。

这里的关键在于 Consumer 自动提交位移，与你没有确认书籍内容被全部读完就将书归还类似，你没有真正地确认消息是否真的被消费就“盲目”地更新了位移。

这个问题的解决方案也很简单：**如果是多线程异步处理消费消息，Consumer 程序不要开启自动提交位移，而是要应用程序手动提交位移**

## 最佳实践

### Kafka 无消息丢失的配置

- 不要使用 producer.send(msg)，而要**使用 producer.send(msg, callback)**。记住，一定要使用带有回调通知的 send 方法。
- **设置 acks = all**。acks 是 Producer 的一个参数，代表了你对“已提交”消息的定义。如果设置成 all，则表明**所有副本 Broker 都要接收到消息，该消息才算是“已提交”**。这是最高等级的“已提交”定义。
- **设置 retries 为一个较大的值**。这里的 retries 同样是 Producer 的参数，对应前面提到的 Producer 自动重试。当出现网络的瞬时抖动时，消息发送可能会失败，此时配置了 retries > 0 的 Producer 能够自动重试消息发送，避免消息丢失。
- **设置 unclean.leader.election.enable = false**。这是 Broker 端的参数，它控制的是哪些 Broker 有资格竞选分区的 Leader。如果一个 Broker 落后原先的 Leader 太多，那么它一旦成为新的 Leader，必然会造成消息的丢失。故一般都要将该参数设置成 false，即不允许这种情况的发生。
- **设置 replication.factor >= 3**。这也是 Broker 端的参数，用来设置主题的副本数。其实这里想表述的是，最好将消息多保存几份，毕竟目前防止消息丢失的主要机制就是冗余。
- **设置 min.insync.replicas > 1**。这依然是 Broker 端参数，控制的是消息至少要被写入到多少个副本才算是“已提交”。设置成大于 1 可以提升消息持久性。在实际环境中千万不要使用默认值 1。
- **确保 replication.factor > min.insync.replicas**。如果两者相等，那么只要有一个副本挂机，整个分区就无法正常工作了。我们不仅要改善消息的持久性，防止数据丢失，还要在不降低可用性的基础上完成。推荐设置成 replication.factor = min.insync.replicas + 1。
- **确保消息消费完成再提交**。Consumer 端有个参数 enable.auto.commit，最好把它设置成 false，并采用手动提交位移的方式。就像前面说的，这对于单 Consumer 多线程处理的场景而言是至关重要的。



# 高级功能

## 拦截器

基本思想就是允许应用程序在不修改逻辑的情况下，动态地实现一组可插拔的事件处理逻辑链。它能够在主业务操作的前后多个时间点上插入对应的“拦截”逻辑。下面这张图展示了 Spring MVC 拦截器的工作原理：

![image-20221128155823938](https://tva1.sinaimg.cn/large/008vxvgGgy1h8kwd5n1aaj30xw0jk76b.jpg)



可以在消息处理的前后多个时点动态植入不同的处理逻辑，比如在消息发送前或者在消息被消费后。

Kafka 拦截器自 0.10.0.0 版本被引入，目前使用的并不多。

**Kafka 拦截器分为生产者拦截器和消费者拦截器**。





































