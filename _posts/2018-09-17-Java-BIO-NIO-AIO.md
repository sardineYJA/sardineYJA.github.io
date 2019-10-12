---
layout: post
title: "BIO,NIO,AIO通信"
date: 2018-09-17
description: "BIO,NIO,AIO通信"
tag: Java

---


## 概念

* 同步：同步IO时，Java自己处理IO读写

* 异步：异步IO时，Java将IO读写委托给OS处理，需要将数据缓冲区地址和大小传给OS，OS需要支持异步IO操作API

* 阻塞：阻塞IO时，Java调用会一直阻塞到读写完成才返回

* 非阻塞：非阻塞IO时，如果不能读写Java调用会马上返回，当IO事件分发器会通知可读写时再继续进行读写，不断循环直到读写完成


## Java对BIO、NIO、AIO的支持

* Java BIO (blocking I/O)：同步并阻塞，服务器实现模式为`一个连接一个线程`，即客户端有连接请求时服务器端就需要启动一个线程进行处理，如果这个连接不做任何事情会造成不必要的线程开销，当然可以通过线程池机制改善。

* Java NIO (non-blocking I/O)： 同步非阻塞，服务器实现模式为`一个请求一个线程`，即客户端发送的连接请求都会注册到多路复用器上，多路复用器轮询到连接`有I/O请求时`才启动一个线程进行处理。

* Java AIO(NIO.2) (Asynchronous I/O) ： 异步非阻塞，服务器实现模式为`一个有效请求一个线程`，客户端的I/O请求都是由OS先完成了再通知服务器应用去启动线程进行处理。


## BIO、NIO、AIO适用场景分析:

* BIO方式适用于连接数目比较小且固定的架构，对服务器资源要求比较高，并发局限于应用中，JDK1.4以前的唯一选择，但程序直观简单易理解。

* NIO方式适用于连接数目多且连接比较短（轻操作）的架构，比如聊天服务器，并发局限于应用中，编程比较复杂，JDK1.4开始支持。

* AIO方式使用于连接数目多且连接比较长（重操作）的架构，比如相册服务器，充分调用OS参与并发操作，编程比较复杂，JDK7开始支持。


-----|BIO|伪异步I/O|NIO|AIO
:---:|:---:|:---:|:---:|:---:
客户端个数：I/O线程|1:1|M:N(M可大于N)|M:1(1个I/O线程处理多个客户端连接)|M:0(不需要启动额外的I/O线程，被动回调)
I/O类型|阻塞|阻塞|非阻塞|非阻塞


# BIO

![png](/images/posts/all/传统BIO通信模型图.png)

采用BIO通信模型的服务端，通常由`一个独立的Acceptor线程`负责监听客户端的连接，它接收到客户端连接请求之后为每个客户端`创建一个新的线程`进行链路处理。

```java
public class BIOServer {
    private static final int PORT = 8888;
    public static void main(String[] args) throws IOException {
        serverStart(PORT);
    }

    public static void serverStart(int port) throws IOException {
        ServerSocket server = null;
        BufferedReader br = null;
        PrintWriter pw = null;

        server = new ServerSocket(port);
        System.out.println("启动服务器");

        int num = 1;
        while(true) {
            Socket socket = server.accept();
            br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            System.out.println("接收客户端的数据：" + br.readLine());
            pw = new PrintWriter(socket.getOutputStream(), true);
            pw.println("这是服务端发的数据，给 "+num+" 号客户端");
            num++;
            // 可以在这里开启新线程 new Thread();处理每一个连接
        }
    }
}

```

```java
public class BIOClient {
    private static final String HOST = "127.0.0.1";
    private static final int PORT = 8888;

    public static void main(String[] args) throws IOException {
        send(HOST, PORT);
    }

    public static void send(String url, int port) throws IOException {
        BufferedReader br = null;
        PrintWriter pw = null;
        Socket socket = null;
        int myid = 2;

        socket = new Socket(url, port);
        System.out.println("启动客户端");
        br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        pw = new PrintWriter(socket.getOutputStream(), true);
        pw.println("这是客户端 "+myid+" 号发的数据");
        System.out.println("接收服务器端的数据：" + br.readLine());
    }
}
```



# 伪异步

由于BIO一个客户端需要一个线程去处理，因此进行优化，后端使用线程池来处理多个客户端的请求接入，形成客户端个数M：线程池最大的线程数N的比例关系，其中M可以远远大于N，通过线程池可以灵活的调配线程资源，设置线程的最大值，防止由于海量并发接入导致线程耗尽。

```java
ExecutorService executorService = Executors.newCachedThreadPool();
...
while(true) {
    ...   // 只需要将线程加入到线程池即可
    executorService.execute(new Runnable() {...})
    ...
}
```


# NIO

```java
public class NIOServer {
    public static void main(String[] args) throws IOException {
        System.out.println("服务器开启");

        ServerSocketChannel sChannel = ServerSocketChannel.open(); // 创建通道
        sChannel.configureBlocking(false);                     // 切换成非阻塞模式
        sChannel.bind(new InetSocketAddress(8888));       // 绑定连接
        Selector selector = Selector.open();                    // 获取选择器
        sChannel.register(selector, SelectionKey.OP_ACCEPT);    // 注册指定监听事件

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
                    ByteBuffer buffer = ByteBuffer.allocate(1024);
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

https://blog.csdn.net/guanghuichenshao/article/details/79375967

https://blog.csdn.net/yswKnight/article/details/79347833

