---
layout: post
title: "RPC 原理"
date: 2019-10-18
description: "RPC 原理"
tag: Distributed Service

---


# RPC

RPC(Remote Procedure Call Protocol) 远程过程调用协议，一种通过网络从远程计算机程序上请求服务，而不需要了解底层网络技术的协议。

RPC采用客户机/服务器模式。请求程序就是一个客户机，而服务提供程序就是一个服务器。首先，客户机调用进程发送一个有进程参数的调用信息到服务进程，然后等待应答信息。在服务器端，进程保持睡眠状态直到调用信息到达为止。当一个调用信息到达，服务器获得进程参数，计算结果，发送答复信息，然后等待下一个调用信息，最后，客户端调用进程接收答复信息，获得进程结果，然后调用执行继续进行。

![png](/images/posts/all/RPC流程图.png)


## 使用 RPC 场景

业务越来越多、应用也越来越多时，有些功能已经不能简单划分开来或者划分不出来。此时，可以将公共业务逻辑抽离出来，将之组成独立的服务Service应用 。而原有的、新增的应用都可以与那些独立的Service应用交互，以此来完成完整的业务功能。所以此时需一种高效的应用程序之间的通讯手段来完成这种需求，即RPC。


## RPC 程序实现结构图

![png](/images/posts/all/RPC程序实现结构图.png)

user 就是 client 端，当 user 想发起一个远程调用时，它实际是通过本地调用user-stub。
user-stub 负责将调用的接口、方法和参数通过约定的协议规范进行编码并通过本地的 RPCRuntime 实例传输到远端的实例。
远端 RPCRuntime 实例收到请求后交给 server-stub 进行解码后发起本地端调用，调用结果再返回给 user 端。

![png](/images/posts/all/RPC程序实现组件图.png)

RPC 服务方通过 RpcServer 去导出（export）远程接口方法，而客户方通过 RpcClient 去引入（import）远程接口方法。
客户方像调用本地方法一样去调用远程接口方法，RPC 框架提供接口的代理实现，实际的调用将委托给代理 RpcProxy。
代理封装调用信息并将调用转交给RpcInvoker 去实际执行。在客户端的RpcInvoker 通过连接器RpcConnector 去维持与服务端的通道RpcChannel，并使用RpcProtocol 执行协议编码（encode）并将编码后的请求消息通过通道发送给服务方。

RPC 服务端接收器 RpcAcceptor 接收客户端的调用请求，同样使用RpcProtocol 执行协议解码（decode）。解码后的调用信息传递给RpcProcessor 去控制处理调用过程，最后再委托调用给RpcInvoker 去实际执行并返回调用结果。

## 各个部分的详细职责

- RpcServer 负责导出（export）远程接口  

- RpcClient 负责导入（import）远程接口的代理实现  

- RpcProxy 远程接口的代理实现  

- RpcInvoker 客户方实现，负责编码调用信息和发送调用请求到服务方并等待调用结果返回；服务方实现，负责调用服务端接口的具体实现并返回调用结果  

- RpcProtocol 负责协议编/解码  

- RpcConnector 负责维持客户方和服务方的连接通道和发送数据到服务方  

- RpcAcceptor 负责接收客户方请求并返回请求结果  

- RpcProcessor 负责在服务方控制调用过程，包括管理调用线程池、超时时间等  

- RpcChannel 数据传输通道  



## 序列化

两方面会直接影响 RPC 的性能，一是传输方式，二是序列化。

序列化方式：毕竟是远程通信，需要将对象转化成二进制流进行传输。不同的RPC框架应用的场景不同，在序列化上也会采取不同的技术。 就序列化而言，Java 提供了默认的序列化方式，但在高并发的情况下，这种方式将会带来一些性能上的瓶颈，于是市面上出现了一系列优秀的序列化框架，比如：Protobuf、Kryo、Hessian、Jackson 等，它们可以取代 Java 默认的序列化，从而提供更高效的性能。

编码内容：出于效率考虑，编码的信息越少越好（传输数据少），编码的规则越简单越好（执行效率高）。如下是编码需具备的信息：
```
-- 调用编码 --
1. 接口方法
   包括接口名、方法名
2. 方法参数
   包括参数类型、参数值
3. 调用属性
   包括调用属性信息，例如调用附件隐式参数、调用超时时间等

-- 返回编码 --
1. 返回结果
   接口方法中定义的返回值
2. 返回码
   异常返回码
3. 返回异常信息
   调用异常信息
```


# 实例

## 服务端提供客户端所期待的服务，一般包括三个部分：服务接口，服务实现以及服务的注册暴露

```java
public interface HelloService {
    String hello(String name);
    String hi(String msg);
}
```

```java
public class HelloServiceImpl implements HelloService{
    @Override
    public String hello(String name) {
        return "Hello " + name;
    }
    @Override
    public String hi(String msg) {
        return "Hi, " + msg;
    }
}
```

```java
public class RpcProvider {
    public static void main(String[] args) throws Exception {
        HelloService service = new HelloServiceImpl();
        // RPC框架将服务暴露出去，供客户端消费
        RpcFramework.export(service,  1234);
    }
}
```

## 客户端消费服务端所提供的服务，一般包括两个部分：服务接口和服务引用

```java
public class RpcConsumer {
    public static void main(String[] args) throws Exception {
        // 由RpcFramework生成的HelloService的代理
        HelloService service = RpcFramework.refer(HelloService.class, "127.0.0.1", 1234);
        String hello = service.hello("World");
        System.out.println("客户端接收到远程调用的结果：" + hello);
    }
}
```

## RPC框架原型实现

```java
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Arrays;

public class RpcFramework {

    /**
     * 暴露服务
     *
     * @param service 服务实现
     * @param port    服务端口
     * @throws Exception
     */
    public static void export (final Object service, int port) throws Exception {
        if (service == null) {
            throw new IllegalArgumentException("service instance == null");
        }
        if (port <= 0 || port > 65535) {
            throw new IllegalArgumentException("Invalid port " + port);
        }
        System.out.println("Export service " + service.getClass().getName() + " on port " + port);

        // 建立Socket服务器
        ServerSocket server = new ServerSocket(port);
        for (;;) {
            try {
                // 监听Socket请求
                final Socket socket = server.accept();
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            try {
                                // 获取请求流，Server解析并获取请求
                                // 构建对象输入流，从源中读取对象到程序中
                                ObjectInputStream input = new ObjectInputStream(socket.getInputStream());
                                try {
                                    System.out.println("\nServer解析请求：");
                                    String methodName = input.readUTF();
                                    System.out.println("mathodName : " + methodName);

                                    // 泛型与数组是不兼容的，除了通配符作泛型参数以外
                                    Class<?>[] parameterTypes = (Class<?>[])input.readObject();
                                    System.out.println("parameterTypes : " + Arrays.toString(parameterTypes));
                                    Object[] arguments = (Object[])input.readObject();
                                    System.out.println("arguments : " + Arrays.toString(arguments));

                                    // Server 处理请求，进行响应
                                    ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
                                    try {
                                        // service类型为Object的（可以发布任何服务），故只能通过反射调用处理请求
                                        // 反射调用，处理请求
                                        Method method = service.getClass().getMethod(methodName, parameterTypes);
                                        Object result = method.invoke(service, arguments);
                                        System.out.println("\nServer 处理并响应：");
                                        System.out.println("result : " + result);
                                        output.writeObject(result);
                                    } catch (Throwable t) {
                                        output.writeObject(t);
                                    } finally {
                                        output.close();
                                    }
                                } finally {
                                    input.close();
                                }
                            } finally {
                                socket.close();
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }).start();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }


    public static <T> T refer(final Class<T> interfaceClass, final String host, final int port) throws Exception {
        if (interfaceClass == null) {
            throw new IllegalArgumentException("Interface class == null");
        }

        // JDK 动态代理的约束，只能实现对接口的代理
        if (!interfaceClass.isInterface()) {
            throw new IllegalArgumentException("The " + interfaceClass.getName() + " must be interface class!");
        }
        if (host == null || host.length() == 0) {
            throw new IllegalArgumentException("Host == null");
        }
        if (port < 0 || port > 65535) {
            throw new IllegalArgumentException("Invalid port " + port);
        }
        System.out.println("Get remote service " + interfaceClass.getName() + " from server " + host + ":" + port);

        // JDK 动态代理
        T proxy = (T) Proxy.newProxyInstance(interfaceClass.getClassLoader(), new Class<?>[]{interfaceClass},
                new InvocationHandler() {
                    // invoke方法本意是对目标方法的增强，在这里用于发送RPC请求和接收响应
                    @Override
                    public Object invoke(Object proxy, Method method, Object[] arguments) throws Throwable {
                        // 创建Socket客户端，并与服务端建立链接
                        Socket socket = new Socket(host, port);
                        try {
                            // 客户端像服务端进行请求，并将请求参数写入流中
                            // 将对象写入到对象输出流，并将其发送到Socket流中
                            ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
                            try {
                                // 发送请求
                                System.out.println("\nClient发送请求：");
                                output.writeUTF(method.getName());
                                System.out.println("methodName : " + method.getName());
                                output.writeObject(method.getParameterTypes());
                                System.out.println("parameterTypes : " + Arrays.toString(method.getParameterTypes()));
                                output.writeObject(arguments);
                                System.out.println("arguments : " + Arrays.toString(arguments));

                                // 客户端读取并返回服务端的响应
                                ObjectInputStream input = new ObjectInputStream(socket.getInputStream());
                                try {
                                    Object result = input.readObject();
                                    if (result instanceof Throwable) {
                                        throw (Throwable)result;
                                    }
                                    System.out.println("\nClient 收到响应：");
                                    System.out.println("result : " + result);
                                    return result;
                                } finally {
                                    input.close();
                                }
                            } finally {
                                output.close();
                            }
                        } finally {
                            socket.close();
                        }
                    }
                });
        return proxy;
    }

}

```



# reference 

https://github.com/wangzhiwubigdata/God-Of-BigData

