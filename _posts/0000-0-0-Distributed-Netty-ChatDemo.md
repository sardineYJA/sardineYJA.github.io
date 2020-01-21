---
layout: post
title: "Netty 网络聊天案例"
date: 2019-10-24
description: "Netty 网络聊天案例"
tag: Distributed Service

---


# 项目验证

项目链接：https://github.com/sardineYJA/Netty-ChatDemo

## 指令

```sh
# 单聊
sendToUser: toUserId message

# 退出登录
logout

# 创建群聊
createGroup

# 查看群聊人员 
listGroupMembers: groupId

# 加入群聊
joinGroup: groupId

# 退出群聊
quitGroup: groupId

# 发送群消息
sendToGroup: groupId message
```

## 增加新功能

1. Command 增加新协议指令
2. 增加相关的 RequestPacket 和 ResponsePacket
3. PacketCodec 的 Map 增加相关 Packet 序列化
4. 创建 RequestPacketHandler 和 ResponsePacketHandler 类
5. Server 增加 RequestPacketHandler 和 Client 增加 ResponsePacketHandler


## 单例模式

注意：增加`@ChannelHandler.Sharable`，否则出错

```java
// 加上注解标识，表明该 handler 是可以多个 channel 共享的
@ChannelHandler.Sharable
public class PacketCodecHandler extends MessageToMessageCodec<ByteBuf, Packet> {
    ...
}
```

```java
// ch.pipeline().addLast(new PacketDecoder());
// ch.pipeline().addLast(new PacketEncoder());
// 合并上面两个，使用单例模式，防止每次有新连接产生过多小对象
ch.pipeline().addLast(PacketCodecHandler.INSTANCE);
```


# 通信协议编解码


## 通信协议设计

魔数(0x12345678)|版本号(1)|序列化算法|指令|数据长度|数据(Packet对象序列化)
:---:|:---:|:---:|:---:|:---:|:---:
4字节|1字节|1字节|1字节|4字节|N字节


## 序列化

```java
public interface SerializerAlgorithm {
    // json 序列化标识
    byte JSON = 1;
}
```

```java
public interface Serializer {

    byte JSON_SERIALIZER = 1;
    Serializer DEFAULT = new JSONSerializer();

    byte getSerializerAlgorithm();        // 序列化算法
    byte[] serialize(Object object);      // 序列化
    <T> T deserialize(Class<T> clazz, byte[] bytes);  // 反序列化
}
```

```java
public class JSONSerializer implements Serializer {
    @Override
    public byte getSerializerAlgorithm() {
        return SerializerAlgorithm.JSON;
    }

    @Override
    public byte[] serialize(Object object) {
        return JSON.toJSONBytes(object);  // Alibaba的json序列化
    }

    @Override
    public <T> T deserialize(Class<T> clazz, byte[] bytes) {
        return JSON.parseObject(bytes, clazz);
    }
}
```


## 实现协议

```java
public abstract class Packet {
    // 协议版本
    private Byte version = 1;

    // Setter&Getter 
    ...

    public abstract Byte getCommand();  // 指令
}
```

```java
public interface Command {
    Byte LOGIN_REQUEST = 1;   // 指令
}
```

```java
public class LoginRequestPacket extends Packet {
    private Integer userId;
    private String username;
    private String password;

    // Setter&Getter 
    ...

    @Override
    public Byte getCommand() {
        return LOGIN_REQUEST;
    }
}
```

```java
public class PacketCodeC {
    private static final int MAGIC_NUMBER = 0x12345678;
    private static final Map<Byte, Class<? extends Packet>> packetTypeMap;
    private static final Map<Byte, Serializer> serializerMap;

    static {
        packetTypeMap = new HashMap<>();
        packetTypeMap.put(LOGIN_REQUEST, LoginRequestPacket.class);

        serializerMap = new HashMap<>();
        Serializer serializer = new JSONSerializer();
        serializerMap.put(serializer.getSerializerAlgorithm(), serializer);
    }
    // Packet对象编码ByteBuf
    public ByteBuf encode(Packet packet) {
        ByteBuf byteBuf = ByteBufAllocator.DEFAULT.ioBuffer();
        byte[] bytes = Serializer.DEFAULT.serialize(packet);

        byteBuf.writeInt(MAGIC_NUMBER);
        byteBuf.writeByte(packet.getVersion());
        byteBuf.writeByte(Serializer.DEFAULT.getSerializerAlgorithm());
        byteBuf.writeByte(packet.getCommand());
        byteBuf.writeInt(bytes.length);
        byteBuf.writeBytes(bytes);

        return byteBuf;
    }
    // ByteBuf解码成Packet对象
    public Packet decode(ByteBuf byteBuf) {
        byteBuf.skipBytes(4);   // 跳过协议
        byteBuf.skipBytes(1);   // 跳过版本号
        byte serializeAlgorithm = byteBuf.readByte();
        byte command = byteBuf.readByte();
        int length = byteBuf.readInt();
        byte[] bytes = new byte[length];
        byteBuf.readBytes(bytes);

        Class<? extends Packet> requestType = getRequestType(command);
        Serializer serializer = getSerializer(serializeAlgorithm);

        if (requestType != null && serializer != null) {
            return serializer.deserialize(requestType, bytes);
        }
        return null;
    }

    private Serializer getSerializer(byte serializeAlgorithm) {
        return serializerMap.get(serializeAlgorithm);
    }

    private Class<? extends Packet> getRequestType(byte command) {
        return packetTypeMap.get(command);
    }
}
```





# reference

https://www.jianshu.com/p/a4e03835921a


