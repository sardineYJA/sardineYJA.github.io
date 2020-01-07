---
layout: post
title: "Linux C++ 线程池"
date: 2019-11-05
description: "Linux C++ 常用案例"
tag: C&C++

---

## 线程池

创建固定数量的线程池，当有新连接加入到任务队列中，线程池使用一条线程处理，如果线程池用满，新连接等待。

相比java的NIO的Selector，此案例只能一条线程处理一个连接。


# 案例

## 任务封装类

```C++
#ifndef __TASK_H__
#define __TASK_H__
 
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <deque>
#include <string>  
#include <pthread.h> 

using namespace std;

/** 
 * 执行任务的类，设置accept()描述符并执行 
 */  
class CTask {

protected:
    string m_strTaskName;        // 任务的名称
    int connfd;                  // Client 接收的地址
 
public:
    CTask() = default;           // 该函数比用户自己定义的默认构造函数获得更高的代码效
    CTask(string taskName);

    int Run();
    void SetConnFd(int data);   // 设置接收的套接字连接号
    int GetConnFd();
};

#endif
```

```C++
#include "Task.h"  

CTask::CTask(string taskName) 
{
	m_strTaskName = taskName;
}


void CTask::SetConnFd(int data)  
{  
    connfd = data;  
}  
 
int CTask::GetConnFd()
{
    return connfd;
}

int CTask::Run()
{
    int connfd = GetConnFd();
    struct timeval tv;

    while(1)
    {
        fd_set rfds;    
        FD_ZERO(&rfds);
        int maxfd = 0;
        int retval = 0;
        FD_SET(connfd, &rfds);
        if (maxfd < connfd){
            maxfd = connfd;
        }
        tv.tv_sec = 10;
        tv.tv_usec = 0;    
        retval = select(maxfd+1, &rfds, NULL, NULL, &tv);
        if (retval == -1){                  // == -1 负值：select错误 
            printf("select error\n");
        } else if (retval == 0) {           // == 0 等待超时，没有可读写或错误的文件
            // printf("no any message\n");
        } else {

            char buf[1024];
            memset(buf, 0, sizeof(buf));
            int recvlen = recv(connfd, buf, sizeof(buf), 0);

            printf("from %d recv size：%d\n", connfd, recvlen);
            if (recvlen == 0) { // 如果0则*it客户端已经断开
                printf("%d：Client disconnect!\n", connfd);
                break;
            } else {
                printf("%s", buf);
            }
        }      
    }
    close(connfd);
    return 0;
}
```

## 线程池封装类

```C++
#ifndef __THREADPOOL_H__
#define __THREADPOOL_H__

#include "Task.h"
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

using namespace std; 

/** 
 * 线程池类的实现 
 */  
class CThreadPool  
{  
private:  
    static  deque<CTask*> m_deqTaskList;      /** 任务队列 */  
    static  bool shutdown;                    /** 线程退出标志 */           
    int     m_iThreadNum;                     /** 线程池中启动的线程数 */  
    pthread_t   *pthread_id;  
      
    static pthread_mutex_t m_pthreadMutex;    /** 线程同步锁 */  
    static pthread_cond_t m_pthreadCond;      /** 线程同步的条件变量 */  
  
protected:  
    static void* ThreadFunc(void * threadData); /** 新线程的线程回调函数 */  
    static int MoveToIdle(pthread_t tid);       /** 线程执行结束后，把自己放入到空闲线程中 */  
    static int MoveToBusy(pthread_t tid);       /** 移入到忙碌线程中去 */  
      
    int Create();                               /** 创建线程池中的线程 */  
  
public:  
    CThreadPool(int threadNum = 10);  /** 默认10个线程*/
    int AddTask(CTask *task);         /** 把任务添加到任务队列中 */  
    int StopAll();                    /** 使线程池中的线程退出 */  
    int getTaskSize();                /** 获取当前任务队列中的任务数 */  
};  
  
#endif 
```

```C++
#include "ThreadPool.h"

/**
* 初始化数据
*/
deque<CTask*> CThreadPool::m_deqTaskList;         // 任务列表  
bool CThreadPool::shutdown = false;  
      
pthread_mutex_t CThreadPool::m_pthreadMutex = PTHREAD_MUTEX_INITIALIZER;   
pthread_cond_t CThreadPool::m_pthreadCond = PTHREAD_COND_INITIALIZER;  
  
/** 
 * 线程池管理类构造函数 
 */  
CThreadPool::CThreadPool(int threadNum)  
{  
    this->m_iThreadNum = threadNum;  
    cout << "Will ready create " << threadNum << " threads" << endl;  
    Create();       //*创建对象时便创建线程。
}
 
/** 
 * 创建线程 
 */  
int CThreadPool::Create()  
{  
    pthread_id = (pthread_t*)malloc(sizeof(pthread_t) * m_iThreadNum);  
    for(int i = 0; i < m_iThreadNum; i++)  
    {   // （线程标识符指针，设置线程属性，线程运行函数地址，运行函数的参数）
        pthread_create(&pthread_id[i], NULL, ThreadFunc, NULL);  
    }  
    return 0;  
}

/** 
 * 线程回调函数 
 */
void* CThreadPool::ThreadFunc(void* threadData)  
{  
    pthread_t tid = pthread_self();  
    while (1)  
    {  
 
        //* 线程开启时先上锁 */
        pthread_mutex_lock(&m_pthreadMutex);  
        while (m_deqTaskList.size() == 0 && !shutdown)  
        {  
            //* 没有任务时，线程等待状态（条件变量）*/
            pthread_cond_wait(&m_pthreadCond, &m_pthreadMutex);  
        }  
          
        if (shutdown)  
        {  
            pthread_mutex_unlock(&m_pthreadMutex);  
            printf("thread %lu will exit\n", pthread_self());  
            pthread_exit(NULL);   
        }  
          
        printf("tid %lu run\n", tid);  
            
        /** 
        * 取任务队列并处理之 
        */ 
 
        CTask* task = m_deqTaskList.front();  
        m_deqTaskList.pop_front();
 
        //* 取完任务后释放锁*/
        pthread_mutex_unlock(&m_pthreadMutex);  
          
        task->Run(); /** 执行任务 */  
         
    }  
    return (void*)0;  
}  
 
/** 
 * 往任务队列里边添加任务并发出线程同步信号 
 */  
int CThreadPool::AddTask(CTask *task)  
{  
    pthread_mutex_lock(&m_pthreadMutex);  
    this->m_deqTaskList.push_back(task);  
    pthread_mutex_unlock(&m_pthreadMutex); 
 
    // * 添加任务 条件变量发信号，非阻塞  */
    pthread_cond_signal(&m_pthreadCond);
    // 发送一个信号给另外一个(并非多个)正在处于阻塞等待状态的线程,使其脱离阻塞状态,继续执行.
    // 如果没有线程处在阻塞等待状态, pthread_cond_signal也会成功返回。
    return 0;  
}  

/** 
 * 停止所有线程 
 */  
int CThreadPool::StopAll()  
{  
    /** 避免重复调用 */  
    if (shutdown)  
    {  
        return -1;    
    }  
    printf("Now will end all threads!!\n");  
    /** 唤醒所有等待线程，线程池要销毁了 */  
    shutdown = true;  
    pthread_cond_broadcast(&m_pthreadCond);  
      
    /** 阻塞等待线程退出，否则就成僵尸了 */  
    for (int i = 0; i < m_iThreadNum; i++)  
    {   // pthread_join用来等待一个线程的结束(线程标识符，返回值)
        pthread_join(pthread_id[i], NULL);    
    }  
      
    free(pthread_id);  
    pthread_id = NULL;  
      
    /** 销毁条件变量和互斥体 */  
    pthread_mutex_destroy(&m_pthreadMutex);  
    pthread_cond_destroy(&m_pthreadCond);  
      
    return 0;  
}  
 
/** 
 * 获取当前队列中任务数 
 */  
int CThreadPool::getTaskSize()  
{  
    return m_deqTaskList.size();      
}  
```

## Server端

```C++
#include "Task.h"
#include "ThreadPool.h"

int main(int argc, char* argv[])
{
    int sock_server = socket(AF_INET, SOCK_STREAM, 0);     // AF_INET IPV4; SOCK_STREAM TCP
    if (sock_server == -1) {
        printf("create socket error: %s(errno: %d)\n", strerror(errno), errno);
        exit(1);
    }
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(7800);
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock_server, (struct sockaddr* ) &servaddr, sizeof(servaddr))==-1) {
        perror("bind error : ");
        exit(1);
    }
    if (listen(sock_server, 20) == -1) {
        perror("listen error : ");
        exit(1);
    }
    socklen_t len = sizeof(sock_server);

    // 创建线程池
    CThreadPool thPool(20);
 
    while(1)
    {
       int connectfd = accept(sock_server, (struct sockaddr*)&servaddr, &len);
       if(connectfd < 0)
       {
           printf("Client [%d] connect failed.", connectfd);
       }
       //收到客户端请求，即添加到任务队列去
       else
       {
           CTask* task=new CTask("T1");
           task->SetConnFd(connectfd);
           thPool.AddTask(task);
       }
      
    }
    close(sock_server);
    return 0;
}
```

## Client端

```C++
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/shm.h>

#include "define.h"

int main()
{
    int sock_cli;
    fd_set rfds;          // 文件描述符的集合
    struct timeval tv;
    int retval, maxfd;

    // 定义sockfd
    sock_cli = socket(AF_INET,SOCK_STREAM, 0);
    // 定义sockaddr_in
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(7800);                       // 服务器端口
    servaddr.sin_addr.s_addr = inet_addr("172.16.7.124");  // 服务器ip

    // 连接服务器，成功返回0，错误返回-1
    if (connect(sock_cli, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("connect error : ");
        exit(1);
    }

    while(1)
    {
        /*把可读文件描述符的集合清空*/
        FD_ZERO(&rfds);     // 每次循环都要清空集合，否则不能检测描述符变化  
        /*把标准输入的文件描述符加入到集合中*/
        FD_SET(0, &rfds);   // （文件描述符0、1、2）=>（stdin、stdout、stderr）
        maxfd = 0;
        /*把当前连接的文件描述符加入到集合中*/
        FD_SET(sock_cli, &rfds);
        /*找出文件描述符集合中最大的文件描述符*/    
        if (maxfd < sock_cli)
            maxfd = sock_cli;
        /*设置超时时间*/
        tv.tv_sec = 5;     // select()最多等待时间，对阻塞操作则为NULL，一定等到监视文件描述符集合中某个文件描述符发生变化为止
        tv.tv_usec = 0;    // 每次select前必须设置才起作用 
        /*等待聊天*/   // readfds、writefds 和exceptfds 描述词组，是用来回传该描述词的读，写或例外的状况，这里只需检查读
        retval = select(maxfd+1, &rfds, NULL, NULL, &tv);

        if(retval == -1)                 // == -1 负值：select错误
        {
            printf("select出错，客户端程序退出\n");
            break;
        }
        else if(retval == 0)             // == 0 等待超时，没有可读写或错误的文件
        {
            // printf("no any message\n");
            continue;
        }
        else
        {
            /*服务器发来了消息*/
            if(FD_ISSET(sock_cli, &rfds)){    // 检查sock_cli文件描述符是否可读写
                char recvbuf[1024];
                int len;
                len = recv(sock_cli, recvbuf, sizeof(recvbuf),0);
                printf("recv 大小：%d\n", len);
                // 如果是0则*it已经断开
                if (len == 0) {
                    printf("服务器断开，客户端程序退出\n");
                    break;
                } 
                printf("%s", recvbuf);
                memset(recvbuf, 0, sizeof(recvbuf));  // 初始化值
            }
            /*用户输入信息了,开始处理信息并发送*/
            if(FD_ISSET(0, &rfds)){           // 检查0输入文件描述符是否可读写 
                char sendbuf[1024];
                fgets(sendbuf, sizeof(sendbuf), stdin);
                int len = send(sock_cli, sendbuf, strlen(sendbuf),0); //发送
                printf("send 大小：%d\n", len);
                memset(sendbuf, 0, sizeof(sendbuf));
            }
        }
    }
    close(sock_cli);
    return 0;
}
```
## make

```
g++ -o testMySql -I/usr/include/mysql/ MySqlDB.cpp testMySql.cpp -L/usr/lib64/mysql/ -lmysqlclient -lz
g++ XLClient.cpp -o XLClient -std=c++11
```

# reference

https://blog.csdn.net/qq_38506897/article/details/81135648
