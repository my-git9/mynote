[toc]

# 索引

正向索引是通过key找value,反向索引通过value找key

## 正向索引

- 以文档ID为关键字，表中记录文档中每个字的位置信息

- 建立索引时候结构简单，易于维护

- 检索效率低，只能在一些简单的场景下使用

  <img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815180326108.png" alt="image-20210815180326108" style="zoom:50%;" />



## 反向索引

- 反向索引，也叫倒排索引

- 倒排索引一字或词为关键字进行索引，表中关键字对应的记录表记录了出现这个字或词的所有文档
- 一个表项就是一个字断，它记录改文档的ID和字符在该文档的位置情况
- 优缺点
  - 查询时候可以一次得到查询关键字所对应的所有文档，查询效率高于正排索引
  - 由于每个字或词对应的文档数量在动态变化，所以倒排表的建立和维护都较为复杂

## 倒排索引组成

倒排索引主要由单词词典(Term Dictionary)和倒排列表(Posting List)组成





<img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815182018252.png" alt="image-20210815182018252" style="zoom:50%;" />





### 单词词典

- 记录所有文档的单词，一般比较大，记录单词到倒排列表的关联信息。
- 单词词典一般用B+Trees来实现，存储在内存

<img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815215858500.png" alt="image-20210815215858500" style="zoom:50%;" />

### 倒排列表

- 倒排列表记载了出现过某个单词的所有文档的文档列表及单词在该文档出现的信息和频率（作关联性算分），没条记录记为一个倒排项（Posting）。
- 倒排列表存储在磁盘文件中，主要包含以下信息
  - 文档ID
  - 单词频率(TF)
  - 位置（Position）
  - 偏移(Offset)

<img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815220446359.png" alt="image-20210815220446359" style="zoom:50%;" />

- 单词字段和倒排列表整合在一起的结构如下

  <img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815220644825.png" alt="image-20210815220644825" style="zoom:50%;" />

## 索引的更新策略

<img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815221517469.png" alt="image-20210815221517469" style="zoom:50%;" />

<img src="/Users/xin/Library/Application Support/typora-user-images/image-20210815222108955.png" alt="image-20210815222108955" style="zoom:40%;" />

### 常用的索引更新策略

完全重建策略、再合并策略、原地更新策略、混合策略

# 分词器

## 定义

- 文本分析就是将全文本转换一系列单词(term/token)的过程，也叫分词。Analysis是通过Analyzer来实现的。

- 分词器的作用就是把整篇文档，按一定的语义切分成一个一个的词条，目标是提升文档的召回率，并降低无效数据的噪音

  - recall召回率，也叫可搜索行，指搜索的时候，增加能够搜索到的结果的数量

  - 降噪：只降低文档中一些低相关性词条对整体搜索排序结果的干扰

    

## 组成

- 分词器(analyzer)都由三块构件块组成的：character filters,tokenizers,token filters

  - Character filters字符过滤器
    - 在一段文本进行分词之前，先进行预处理
    - 比如说过滤html标签(<span>hello</ span> -----> hello), & ------> and

  - tokenizers分词器
    - 英文分词可以根据空格将单词分开，中文分词比较复杂，可以根据机器学习算法来分词
  - Token filters Token过滤器
    - 将划分的单词进行加工
    - 大小写转换，去掉词(如停用词像"a","and","the"等)，或者增加词（如同义词像"jump"和"leap"）

- Analyzer = Character filters(0+个)+tokenizers(1个)+Token filters（0+个）

## 内置分词器

- Standard Analyzer:标准分词器，按词切分，小写处理。提供了基于语法的标记化（基于Unicode文本分割算法）
- Simple Analyzer:按照非字母切分（符号被过滤），小写处理。只要不是字母的字符，就将文本解析成term，所有的term都是小写的
- Whitespace Analyzer：按照空格切分，不转大小写
- Stop  Analyzer：小写过滤器，停用词过滤（the,a,is）
- Keyword Analyzer：不分词，直接将输入当作输出
- Patter Analyzer：正则表达式，默认\W+
- Language ：提供30多种语言的分词器
- Customer Analyzer：自定义分词器

## 中文分词器

- IK分词器

# 安装注意

- jdk

  最新版本es需要的jdk版本较高，需要修改jdk环境变量(JAVA_HOME)指向es自带的jdk(bin/elasticsearch-env)

- gc 收集器

  修改config/jvm.options，默认CMS 垃圾收集器，jdk9CMS 垃圾收集器开始被标为'@Deprecated'，JDK 11支持的为'G1'和'ZGC'

  将'-XX:+UserConcMarkSweepGC'改为：'-XX:+UserG1GC'

- 不能以root用户跑elastic,需要新增用户

- Elastic search.yaml

  - cluster.name

  - node.name
  - network.host
  - http.port
  - discovery.seed.hosts
  - cluster.initial_master_nodes
  - client.tarnsport.ping_timeout

- 用户线程

  ```
  vim /etc/security/limits.conf
  # es是用户名
  es soft nofile 65535
  es hard nofile 65535
  es soft nproc 4096
  es soft nproc 4096
  ```

- 最大虚拟内存区域vm.max_map_count[65530]太低

  ```
  vim /etc/sysctl.conf
  vm.max_map_count = 262144
  ```

  

# es存储结构

## 与数据库类比

| 数据库              | 表              | 记录               | 列字段          | 表结构定义scheme      |
| ------------------- | --------------- | ------------------ | --------------- | --------------------- |
| ***Elasticsearch*** | ***索引index*** | ***文档Document*** | ***字断Field*** | ***字段定义mapping*** |

## 索引

- 索引是文档（Document）的容器，是一类文档的集合
- 索引（名词）
  - 类比关系数据库的database
  - 索引由其名称(全小写字母)进行标识

- 索引（动词）
  - 保存一个文档到索引的过程
  - 类似于与SQL语句的insert和updata

- 倒排索引

## 类型type

7.x以后不建议使用，将来会废弃，7.0开始一个索引只能创建一个Type为_doc

## 文档Document

index中单条记录称为document,等同于关系数据库表中的行。

## 字段filed

# ES基本命令

```GET/PUT/POST/DELETE```格式

```
POST /uri  # 创建
DELETE /uri/xxx  # 删除
PUT /uri/xxx  # 更新或创建
GET /uri/xxx  # 查看
es中，如果不确定文档的id，那边修改用POST,他可以自己生成唯一的ID,如果确定ID，就可以使用PUT,当然也可以使用POST
PUT,GET,DELETE是幂等(一定时间内每一次取值都是一样的)的，POST不一定是幂等。
```

## 集群相关命令

- _cat命令
  - _cat系列提供了一个查询es集群状态的接口
  - ?v参数，染输出内容有表头；pretty让输出缩进更规范
  - ![image-20210817003116786](/Users/xin/Library/Application Support/typora-user-images/image-20210817003116786.png)

## 索引CURD命令

- 创建索引命名全部小写，不能用_开头，中间不能使用逗号

- 创建索引

  ```curl -XPUT http://1.1.1.1/test?pretty```

- 查看索引

  ```curl -XGET http://1.1.1.1/test?pretty```

- 删除索引

  ```curl -XDELETE http://1.1.1.1/test?pretty```

# mapping

Mapping是定义Document及其包含的field如何存储和索引的过程。例如，使用mapping来定义：

- 哪些字符串字段应被视为全文字段。
- 哪些字段包含数字、日期或地理位置。
- 文档中所有字段的值是否应该被索引到全部[`_all`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-all-field.html)字段中。
- 日期值 的[格式](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-date-format.html)。
- 自定义规则来控制[动态添加字段](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/dynamic-mapping.html)的映射 。

## mapping type

每个索引都包含一个mapping type，用来决定document如何被索引

索引类型包括：

- [Meta-fields](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-fields.html)

  Meta-fields 用于自定义如何处理文档的相关元数据。Meta-fields的例子 包括 [`_index`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-index-field.html), [`_type`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-type-field.html), [`_id`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-id-field.html), and [`_source`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-source-field.html) 字段。

- [Fields](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-types.html) **or** properties

  mapping 类型包含字段列表或`properties`与文档相关的字段列表

## 字段数据类型

每个字段都有一个数据type，可以是：

- 简单的类型：[`text`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/text.html), [`keyword`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/keyword.html), [`date`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/date.html), [`long`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/number.html), [`double`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/number.html), [`boolean`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/boolean.html), [`ip`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/ip.html)等
- 复杂类型(支持 JSON 分层性质的类型)：[`object`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/object.html),[`nested`](https://www.elastic.co/guide/en/elasticsearch/refernce/6.0/nested.html)等

- 特殊类型：[`geo_point`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/geo-point.html), [`geo_shape`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/geo-shape.html), 或[`completion`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/search-suggesters-completion.html)等

为了不同的目的以不同的方式索引相同的字段通常很有用。例如，一个`string`字段可以被[索引](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-index.html)为一个`text`用于全文搜索的`keyword`字段，以及一个用于排序或聚合的字段。或者，您可以使用[`standard`分析器](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/analysis-standard-analyzer.html)、 [`english`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/analysis-lang-analyzer.html#english-analyzer)分析器和 [`french`分析器](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/analysis-lang-analyzer.html#french-analyzer)来索引字符串字段。

这就是*多字段*的目的。大多数数据类型通过[`fields`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/multi-fields.html)参数支持多字段。

## 动态mapping

字段和映射类型在使用前不需要定义。由于动态mapping，新的字段名称将自动添加，只需索引文档即可。新字段既可以添加到顶级映射类型，也可以添加到内部[`object`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/object.html) 和[`nested`](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/nested.html)字段。

该[动态映射](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/dynamic-mapping.html)规则可经配置以定制用于新字段的映射。

## analyser分词器

![image-20210817234436970](/Users/xin/Library/Application Support/typora-user-images/image-20210817234436970.png)

## index是否被索引

index可用户设置字段是否被索引，默认为true，false即为不可搜索

![image-20210817234557768](/Users/xin/Library/Application Support/typora-user-images/image-20210817234557768.png)

## null_value空值默认值

需要对Null值实现搜索时使用，只有keyword类型才支持设定null_value

![image-20210817234803374](/Users/xin/Library/Application Support/typora-user-images/image-20210817234803374.png)

## 防止mapping爆炸

在索引中定义太多字段会导致映射爆炸，从而导致内存不足错误和难以恢复的情况。这个问题可能比预期的更常见。例如，考虑这样一种情况，其中插入的每个新文档都会引入新字段。这在动态映射中很常见。每次文档包含新字段时，这些字段都会在索引的映射中结束。对于少量数据，这并不令人担忧，但随着映射的增长，它可能会成为一个问题。以下设置允许您限制可以手动或动态创建的字段映射的数量，以防止不良文档导致映射爆炸：

**`index.mapping.total_fields.limit`**

索引中的最大字段数。默认值为`1000`。

**`index.mapping.depth.limit`**

field的最大深度，以内部object的数量来衡量。例如，如果所有字段都在根对象级别定义，则深度为1。如果有一个对象映射，则深度为2等。默认为`20`。

**`index.mapping.nested_fields.limit`**

`nested`索引中 的最大字段数，默认为`50`。索引具有 100 个嵌套字段的 1 个文档实际上索引了 101 个文档，因为每个嵌套文档都被索引为一个单独的隐藏文档。

## 更新现有字段mapping

除了记录在案的地方，**现有的字段映射无法更新**。更改映射意味着使已编入索引的文档无效。相反，你应该创建正确映射一个新的索引和[reindex](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/docs-reindex.html)的数据转换成指数

## mapping事例

```
curl -X PUT "localhost:9200/my_index?pretty" -H 'Content-Type: application/json' -d' # 创建一个index(my_index)
{
  "mappings": {
    "doc": {  # 添加一个名为doc的类型
      "properties": { #指定字段或属性
        "title":    { "type": "text"  },  # 	
指定该title字段包含text值
        "name":     { "type": "text"  },  # 指定该name字段包含text值。
        "age":      { "type": "integer" },  # 指定该age字段包含integer值。
        "created":  { #指定该created字段包含date两种可能格式的值。
          "type":   "date", 
          "format": "strict_date_optional_time||epoch_millis"
        }
      }
    }
  }
}
'
```

# 分片与备份

- 分片分为两种，主分片和副本：

  - 主分片用于解决数据水平扩张问题，通过分片将数据分布到集群的所有节点上
    - 一个分片是一个运行的ES实例
    - 分片数载索引创建时指定，后续不允许修改，处分reindex

  - 副本用以解决数据高可用的问题，副本是主分片的拷贝
    - 副本分片数，可以动态调整
    - 增加副本数，还可以在一定程度上提高服务的高可用(读取的吞吐)

- 分片的设定

  - 分片的设置过大，数量少
    - 导致后续无法增加节点实现水平扩展
    - 单个分片数据量过大，导致数据重新分片耗时

  - 分片设置的过小，数量多
    - 影响搜索结果的相关性打分，影响数据统计的准确性
    - 单个节点上过多分片，会导致资源浪费，同时会影响性能
    - 7.0之后，默认分片是1，解决了over-sharding的问题
      - shard也是一种资源，shard过多会影响集群的稳定性。因为shard过多，元信息会变多，这些元信息会占用堆内存。shard过多也会影响数据读写性能，因为每个读写请求都需要一个线程。

# 数据变更流程

## 写数据流程

### Shard和Replication的路由规则

- 每个index由多个shard组成，每个shard有一个主节点和多个副本节点，副本个数可配。
- 但每次写入的时候，写入请求会先根据_routing规则选择发给哪个shard
  - Index Request中可以设置使用哪个Filed的值作为路由规则
  - 如果index没有设置，则使用Mapping中的设置
  - 如果mapping中也没有设置，则使用id作为路由参数，然后通过_id的Hash值选择出Primary shard

- 请求会发数据给Primary shard，在Primary shard 上执行通过后，再从primary shard上将请求同时发给多个Repliset shard

### 数据安全策略

- Elasticsearch 里为了减少磁盘IO保证读写性能，一般每搁一段时间才会把Lucene的Segment写入磁盘持久化

- elasticsearch学习了数据库中的处理方式：增加CommitLog模块，Elasticsearch中叫做TransLog

- 写完TransLog后，刷新TransLog数据到磁盘上，写磁盘成功后，请求返回给用户。

- 具体操作细节

  - 与数据库不同，数据库是先写CommitLog，然后写内存，而Elasticsearch是先将数据写内存，最后写TransLog

  - 写buffer后，文档是不可被搜索的，需要通过Refresh把内存的对象转成完整的Segment后，然后再次reopen后才能被搜索

  - 一般这个时间设置为1s，导致写入es的文档，最快1s才能被搜索到

  - segment里的文档可以被搜索到，但是尚未写入硬盘，如果发生断电，这些文档可能会丢失

  - es会在每搁5s或者是一次写入请求后将translog写入磁盘，操作记录被写入磁盘，es才会将操作成功的结果返回给客户端

  - translog  -----保证安全--->  (buffer + segment)

  - 每搁一秒会生成一个新的segment，而translog文件将越来越大

  - 每搁30分钟或者translog文件变得很大，则执行一次fsync操作。此时所有在文件系统缓存的segment将被写入磁盘，而translog将被删除

    <img src="/Users/xin/Library/Application Support/typora-user-images/image-20210822210605710.png" alt="image-20210822210605710" style="zoom:50%;" />

### 写流程详细策略

![image-20210822221700284](/Users/xin/Library/Application Support/typora-user-images/image-20210822221700284.png)

- 红色为协调节点
- 绿色为主节点
- 蓝色为从节点

## 数据删除流程

- 删除请求时，提交的时候会生成一个.del文件，里面将某个doc标识为deleted状态，那么搜索的时候根据.del文件就知道这个doc被删除了，客户端搜索的时候，发现数据在.del文件中标志为删除的就不会被搜索出来

## 数据更新流程

- es的索引不能修改，更新和删除操作不能直接在原索引上执行

- 收到update请求后，从segment或者translog读取同id完整的doc，记录版本号为v1=345

- 将版本号v1的全量doc和请求中的部分字段doc合并为一个完整的doc，同时更新内存中的versionmap

- 获取到完整的doc后，updata请求就变成了post/put请求

- 加锁

- 再次从versionmap中读取该id的最大版本号v2=346

- 检查版本是否冲突(V1=V2)，如果冲突，则退回开始的"Update doc"阶段，重新执行。如果不冲突，则执行最新的Add请求。

- 在Index Doc阶段，首先将Version + 1得到V3，再将Doc加入到Lucene中去，Luncene会先删除同id下的已存在doc id，然后再增加新Doc。写入Luncene成功后，将当前V3更新到VersionMap中。

- 释放锁，部分更新流程结束。

  <img src="/Users/xin/Library/Application Support/typora-user-images/image-20210822221106617.png" alt="image-20210822221106617" style="zoom:50%;" />

## 数据查询过程

- 查询的过程大体上分为查询(query)和取回(fetch)两个阶段
- 这个节点的任务是广播请求到所有相关切片，并将它们的响应整合成全局排序后的结果集合，这个结果集合会返回给客户端
- 查询过程
  - 当一个节点接收到一个搜索请求，则这个节点就成了协调节点
  - 如果客户端要求返回结果排序从第from开始的数量size的结果集，则每个节点生成一个from+size大小的结果集
  - 分片仅会返回一个轻量级的结果给协调节点，包含结果集中的每一个文档的ID和进行排序所需要的信息
  - 协调节点会将所有分片的结果汇总，并进行全局排序，得到最终的查询排序结果

- 取回过程
  - 分片获取文档返回给协调节点；协调节点将结果返回给客户端

- 相关性计算
  - 判别文档与搜索条件的相关性
  - TFIDF
  - BM25评分算法

# 实时性与可靠性

## 实时性

- 根据id取数据(index/_doc/1)是实时(RT)的，根据条件取数据是近实时的(NRT)(实时性由refresh控制，默认是1s)

## 可靠性

- 搜索系统数据丢失时，从其他存储系统导过来一份rebuild就OK
- es可以通过设置translog的flush频率来控制可靠性
- 出于性能考虑会设置每5s或1min flush一次，间隔时间越长，可靠性越低



