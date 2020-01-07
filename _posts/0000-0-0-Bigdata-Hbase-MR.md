---
layout: post
title: "Hbase MapReduce"
date: 2019-09-10
description: "Hbase 系列"
tag: Bigdata

---

# 官方案例

## 临时环境

```sh
export HBASE_HOME=/.../hbase
export HADOOP_HOME=/.../hadoop
export HADOOP_CLASSPATH=`${HBASE_HOME}/bin/hbase mapredcp`
# hbase mapredcp 查看HBase执行MapReduce所依赖的Jar包
```

当然可以写进profile(推荐写进去)
```sh
vi /etc/profile
source /etc/profile
```

## 统计student表行数：
```sh
yarn jar lib/hbase-server-2.0.1.jar org.apache.hadoop.hbase.mapreduce.RowCounter student
# 或者
hbase rowcounter student
```

## 导入数据：student.tsv
```sh
# \t 隔开
1002	liu     male    33
1003	fang    female  21
```

```sh
yarn jar lib/hbase-server-2.0.1.jar  \
org.apache.hadoop.hbase.mapreduce.ImportTsv  \
-Dimporttsv.columns=HBASE_ROW_KEY,info:name,info:sex,info:age student  \
hdfs://172.16.7.124:9000/student.tsv
```
也可自定义分隔符：-Dimporttsv.separator=","


## BulkLoad方式导入

BulkLoad会将tsv/csv格式的文件编程hfile文件，然后再进行数据的导入，这样可以避免大量数据导入时造成的集群写入压力过大。

tsv/csv文件转为HFile：
```sh
yarn jar lib/hbase-server-2.0.1.jar  \
org.apache.hadoop.hbase.mapreduce.ImportTsv  \
-Dimporttsv.bulk.output=/bulk_out  \
-Dimporttsv.columns=HBASE_ROW_KEY,info:name,info:sex,info:age student  \
hdfs://172.16.7.124:9000/student.tsv
```

HFile导入：
```sh
yarn jar lib/hbase-mapreduce-2.0.1.jar completebulkload  \
hdfs://172.16.7.124:9000/bulk_out student
```



# Java API 操作 Hbase

## 依赖

```xml
<dependency>
    <groupId>org.apache.hbase</groupId>
    <artifactId>hbase-client</artifactId>
    <version>1.3.1</version>
</dependency>
<dependency>
    <groupId>org.apache.hbase</groupId>
    <artifactId>hbase-server</artifactId>
    <version>1.3.1</version>
</dependency>
```


## 错误

> Exception in thread "main" org.apache.hadoop.hbase.client.RetriesExhaustedException: Failed after attempts=36, exceptions:
> java.net.SocketTimeoutException: callTimeout=60000, callDuration=73456: 124-centos7-ismg04
> Caused by: java.net.UnknownHostException: 124-centos7-ismg04

解决：C:\Windows\System32\drivers\etc\hosts写入服务器名

```sh
172.16.7.124 124-centos7-ismg04  # 根据自身修改
```


```java
public static Configuration conf;
static {
    conf = HBaseConfiguration.create();
    conf.set("hbase.zookeeper.quorum", "172.16.7.124");
    conf.set("hbase.zookeeper.property.clientPort", "2181");
}

// 判断表是否存在
public static boolean isTableExist(String tableName) throws IOException {
    HBaseAdmin admin = new HBaseAdmin(conf);
    return admin.tableExists(tableName);
}

// 创建表
public static void createTable(String tableName, String... columnFamily) throws IOException {
    HBaseAdmin admin = new HBaseAdmin(conf);
    if (isTableExist(tableName)) {
        System.out.println("表" + tableName + "已存在");
    } else {
        // 创建表属性对象，表名需要转字节
        HTableDescriptor descriptor = new HTableDescriptor(TableName.valueOf(tableName));
        // 创建多个列族
        for (String cf: columnFamily) {
            descriptor.addFamily(new HColumnDescriptor(cf));
        }
        // 根据对表的配置，创建表
        admin.createTable(descriptor);
        System.out.println("表" + tableName + "创建成功");
    }
}

// 删除表
public static void dropTable(String tableName) throws IOException {
    HBaseAdmin admin = new HBaseAdmin(conf);
    if (isTableExist(tableName)) {
        admin.disableTable(tableName);
        admin.deleteTable(tableName);
        System.out.println("表" + tableName + "删除成功！");
    } else {
        System.out.println("表" + tableName + "不存在！");
    }
}

// 插入数据
public static void addRowData(String tableName, String rowKey, String columnFamily,
                              String column, String value) throws IOException {
    HTable hTable = new HTable(conf, tableName);
    Put put = new Put(Bytes.toBytes(rowKey));
    put.add(Bytes.toBytes(columnFamily), Bytes.toBytes(column), Bytes.toBytes(value));
    hTable.put(put);
    hTable.close();
    System.out.println("插入数据成功");
}

// 删除多行数据
public static void deleteMultiRow(String tableName, String... rows) throws IOException {
    HTable hTable = new HTable(conf, tableName);
    List<Delete> deleteList = new ArrayList<Delete>();
    for (String row: rows) {
        Delete delete = new Delete(Bytes.toBytes(row));
        deleteList.add(delete);
    }
    hTable.delete(deleteList);
    hTable.close();
}

// 得到所有数据
public static void getAllRows(String tableName) throws IOException {
    HTable hTable = new HTable(conf, tableName);
    Scan scan = new Scan();   // 用于扫描region对象
    ResultScanner resultScanner = hTable.getScanner(scan);
    for (Result result: resultScanner) {
        Cell[] cells = result.rawCells();
        for (Cell cell: cells) {
            System.out.print("行键：" + Bytes.toString(CellUtil.cloneRow(cell)) + "\t");
            System.out.print("列族：" + Bytes.toString(CellUtil.cloneFamily(cell)) + "\t");
            System.out.print("列：" + Bytes.toString(CellUtil.cloneQualifier(cell)) + "\t");
            System.out.print("值：" + Bytes.toString(CellUtil.cloneValue(cell)) + "\n");
        }
    }
}

// 得到一行数据
public static void getRow(String tableName, String rowKey) throws IOException {
    HTable hTable = new HTable(conf, tableName);
    Get get = new Get(Bytes.toBytes(rowKey));
    Result result = hTable.get(get);
    for (Cell cell: result.rawCells()) {
        System.out.print("行键：" + Bytes.toString(result.getRow()) + "\t");
        System.out.print("行键：" + Bytes.toString(CellUtil.cloneRow(cell)) + "\t");
        System.out.print("列族：" + Bytes.toString(CellUtil.cloneFamily(cell)) + "\t");
        System.out.print("列：" + Bytes.toString(CellUtil.cloneQualifier(cell)) + "\t");
        System.out.print("值：" + Bytes.toString(CellUtil.cloneValue(cell)) + "\t");
        System.out.print("时间戳：" + cell.getTimestamp() + "\n");
    }
}

// 等到指定“列族:列”的一行数据
public static void getRowQualifier(String tableName, String rowKey,
                                   String family, String qualifier) throws IOException {
    HTable hTable = new HTable(conf, tableName);
    Get get = new Get(Bytes.toBytes(rowKey));
    get.addColumn(Bytes.toBytes(family), Bytes.toBytes(qualifier));
    Result result = hTable.get(get);
    for (Cell cell: result.rawCells()) {
        System.out.print("行键：" + Bytes.toString(result.getRow()) + "\t");
        System.out.print("列族：" + Bytes.toString(CellUtil.cloneFamily(cell)) + "\t");
        System.out.print("列：" + Bytes.toString(CellUtil.cloneQualifier(cell)) + "\t");
        System.out.print("值：" + Bytes.toString(CellUtil.cloneValue(cell)) + "\n");
    }
}
```

```java
public static void main(String[] args) throws IOException {
    System.out.println(isTableExist("student"));
    getAllRows("student");
    getRow("student", "1001");
    getRowQualifier("student", "1001", "info", "name");

    System.out.println("======================================");
    createTable("person", "info");
    addRowData("person", "001", "info", "name", "yang");
    addRowData("person", "001", "info", "age", "23");
    addRowData("person", "001", "info", "sex", "male");
    getAllRows("person");
    dropTable("person");

}
```

# MR案例

将student表中的一部分数据，通过MR迁入到student2表中


## ReadMapper
```java
public class ReadMapper extends TableMapper<ImmutableBytesWritable, Put> {
    @Override
    protected void map(ImmutableBytesWritable key, Result value, Context context) throws IOException, InterruptedException {
        Put put = new Put(key.get());   // 读取每一行
        for (Cell cell: value.rawCells()) {
            if ("info".equals(Bytes.toString(CellUtil.cloneFamily(cell)))) {
                // 只保留name,sex列
                if ("name".equals(Bytes.toString(CellUtil.cloneQualifier(cell)))) {
                    put.add(cell);
                } else if ("sex".equals(Bytes.toString(CellUtil.cloneQualifier(cell)))) {
                    put.add(cell);
                }
            }
        }
        // 读取到的每行数据写入到context中作为map的输出
        context.write(key, put);
    }
}
```

## WriteReducer
```java
public class WriteReducer extends TableReducer<ImmutableBytesWritable, Put, NullWritable> {
    @Override
    protected void reduce(ImmutableBytesWritable key, Iterable<Put> values, Context context) throws IOException, InterruptedException {
        // 将每行数据写进表
        for (Put put : values) {
            context.write(NullWritable.get(), put);
        }
    }
}
```

## MRJob
```java
public class MRJob extends Configured implements Tool {
    @Override
    public int run(String[] args) throws Exception {
        Configuration conf = this.getConf();
        Job job = Job.getInstance(conf, this.getClass().getSimpleName());
        job.setJarByClass(MRJob.class);

        // 配置Job
        Scan scan = new Scan();
        scan.setCacheBlocks(false);
        scan.setCaching(500);

        // 设置Mapper，注意导入的是mapreduce包下的，mapred包是老版本
        TableMapReduceUtil.initTableMapperJob(
                "student",               // 表名
                scan,                          // 扫描控制器
                ReadMapper.class,              // 设置Mapper类
                ImmutableBytesWritable.class,  // 设置Mapper输出key类型
                Put.class,                     // 设置Mapper输出value值类型
                job                            // 设置给哪个JOB
        );

        // 设置Reducer
        TableMapReduceUtil.initTableReducerJob(
                "student2",
                WriteReducer.class,
                job
        );
        job.setNumReduceTasks(1);  // 设置Reduce数量，最少1个

        boolean isSuccess = job.waitForCompletion(true);
        if (!isSuccess) {
            throw new IOException("Job running with error");
        }
        return isSuccess ? 0 : 1;
    }
}
```

```java
public static void main(String[] args) throws Exception {
    Configuration conf = HBaseConfiguration.create();
    conf.set("hbase.zookeeper.quorum", "172.16.7.124");
    conf.set("hbase.zookeeper.property.clientPort", "2181");
    int status = ToolRunner.run(conf, new MRJob(), args);
    System.exit(status);
}
```

# MR案例 从HDFS读取

从HDFS上的文件中读取数据，所以Mapper可直接继承自HDFS的Mapper。

## ReadFromHDFSMapper
```java
public class ReadFromHDFSMapper extends Mapper<LongWritable, Text, ImmutableBytesWritable, Put> {
    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // 从HDFS中读取
        String line = value.toString();
        String[] values = line.split("\t");
        String rowKey = values[0];
        String name = values[1];
        String sex = values[2];
        String age = values[3];

        // 初始化rowKey
        ImmutableBytesWritable rowKeyWritable = new ImmutableBytesWritable(Bytes.toBytes(rowKey));
        // 初始化put
        Put put = new Put(Bytes.toBytes(rowKey));
        put.add(Bytes.toBytes("info"), Bytes.toBytes("name"), Bytes.toBytes(name));
        put.add(Bytes.toBytes("info"), Bytes.toBytes("sex"), Bytes.toBytes(sex));
        put.add(Bytes.toBytes("info"), Bytes.toBytes("age"), Bytes.toBytes(age));
        context.write(rowKeyWritable, put);
    }
}
```

## FromHDFSMRJob
```java
public class FromHDFSMRJob extends Configured implements Tool {
    @Override
    public int run(String[] args) throws Exception {
        Configuration conf = this.getConf();
        Job job = Job.getInstance(conf, this.getClass().getSimpleName());
        job.setJarByClass(FromHDFSMRJob.class);

        Path inPath = new Path("hdfs://172.16.7.124:9000/student.tsv");
        FileInputFormat.addInputPath(job, inPath);

        // 设置Mapper
        job.setMapperClass(ReadFromHDFSMapper.class);
        job.setMapOutputKeyClass(ImmutableBytesWritable.class);
        job.setMapOutputValueClass(Put.class);

        // 设置Reducer
        TableMapReduceUtil.initTableReducerJob(
                "student2",
                WriteReducer.class,
                job
        );
        job.setNumReduceTasks(1);  // 设置Reduce数量，最少1个

        boolean isSuccess = job.waitForCompletion(true);
        if (!isSuccess) {
            throw new IOException("Job running with error");
        }
        return isSuccess ? 0 : 1;
    }
}
```


