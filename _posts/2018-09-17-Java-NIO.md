---
layout: post
title: "Asynchronous Non-Blocking I/O"
date: 2018-09-17
description: "NIO"
tag: Java

---

# NIO

## 特点

- 事件驱动模型
- 单线程处理多任务
- 非阻塞I/O
- 基于block的传输比基于流的传输更加高效
- 基于Reactor线程模型
- 更高级的IO函数zero-copy
- IO多路复用提高java网络应用的可伸缩性和实用性


## 核心

- Channel
- Buffers
- Selectors

## Channels and Buffers

NIO是基于通道（Channel）和缓冲区（Buffer）进行操作，数据总是从通道读取到缓冲区中，或者从缓冲区写入到通道中。

## Selectors

选择器用于监听多个通道的事件（比如：连接打开，数据到达）。
仅用单个线程来处理多个Channels的好处是，只需要更少的线程来处理通道。
线程之间上下文切换的开销很大，而且每个线程都要占用系统的一些资源（如内存）。

## 主要实现类

- FileChannel：从文件中读写数据
- DatagramChannel：能通过UDP读写网络中的数据
- SocketChannel：能通过TCP读写网络中的数据
- ServerSocketChannel：可以监听新进来的TCP连接，对于新连接都会创建SockChannel

- ByteBuffer
- CharBuffer
- DoubleBuffer
- FloatBuffer
- IntBuffer
- LongBuffer
- ShortBuffer


## Buffer 使用

1. 写入数据到Buffer
2. 调用flip()方法
3. 从Buffer中读取数据
4. 调用clear()方法或者compact()方法

Buffer基本属性：capacity(容量)、limit(限制)和position(位置)

flip函数：buffer读写转换。即position为0，读写时，不断移动，直到limit位置。


## Selector 使用

1. Selector的创建：Selector selector = Selector.open();
2. 将Channel注册到Selector上：SelectableChannel.register();


## NIO 服务端建立过程

1. ServerSocketChannel.open()：创建服务器的Channel
2. Channel.configureBlocking(false)：配置非阻塞模式
3. Channel.bind()：绑定端口
4. Selector.open()：打开Selector
5. Channel.register()：注册Channel和关注的事件到Selector上
6. Selector.select()：轮询拿到已经就绪的事件

# 案例

```java
public class NIOServer {
    public static void main(String[] args) throws IOException {
        System.out.println("服务器开启");

        ServerSocketChannel sChannel = ServerSocketChannel.open(); // 创建通道
        sChannel.configureBlocking(false);                        // 切换成非阻塞模式
        sChannel.bind(new InetSocketAddress(8888));              // 绑定连接
        Selector selector = Selector.open();                    // 获取选择器
        sChannel.register(selector, SelectionKey.OP_ACCEPT);   // 注册指定监听事件

        while (selector.select() > 0) {   // 轮训式 获取选择"已经准备就绪"的事件
            Iterator<SelectionKey> iterator = selector.selectedKeys().iterator();

            while (iterator.hasNext()) {
                SelectionKey sk = iterator.next();    // 获取准备就绪的事件
                if (sk.isAcceptable()) {
                    SocketChannel socketChannel = sChannel.accept();  // 获取客户端连接
                    socketChannel.configureBlocking(false);           // 设置阻塞模式
                    socketChannel.register(selector, SelectionKey.OP_READ);  // 将通道注册到服务器上

                } else if (sk.isReadable()) {
                    SocketChannel socketChannel = (SocketChannel)sk.channel();
                    ByteBuffer buffer = ByteBuffer.allocate(1024);    // 容量1024
                    int len=0;
                    while ((len=socketChannel.read(buffer)) > 0) {    // 读取数据
                        buffer.flip(); 
                        System.out.println(new String(buffer.array(), 0, len));
                        buffer.clear();
                    }
                }
            }
            iterator.remove();
        }
        sChannel.close();
    }
}
```

```java
public class NIOClient {
    public static void main(String[] args) throws IOException {
        System.out.println("客户端启动");
        SocketChannel sChannel = SocketChannel.open(     // 创建管道
                new InetSocketAddress("127.0.0.1", 8888));
        sChannel.configureBlocking(false);               // 切换成非阻塞
        ByteBuffer allocate = ByteBuffer.allocate(1024); // 缓冲区大小

        Scanner scanner = new Scanner(System.in);
        System.out.println("输入：");
        while (scanner.hasNext()) {
            System.out.println("输入：");
            String str = scanner.next();
            allocate.put((new Date().toString()+"\n"+str).getBytes());
            allocate.flip();
            sChannel.write(allocate);
            allocate.clear();
        }
        sChannel.close();
    }
}
```


# reference

https://blog.csdn.net/u013096088/article/details/78638245

https://github.com/wangzhiwubigdata/God-Of-BigData
