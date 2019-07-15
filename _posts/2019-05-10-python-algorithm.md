---
layout: post
title: "python数据结构"
date: 2019-05-10
description: "简单复习python数据结构"
tag: python

---

# 队列

```python
class Queue:
    def __init__(self, size):
        self.size = size   # 队列容量
        self.front = -1    # 头指针
        self.rear = -1     # 尾指针
        self.queue = []    # 列表表示队列

    def enqueue(self, ele):  # 入队
        if self.is_full():
            raise Exception('queue is full')
        else:
            self.queue.append(ele)
            self.rear += 1

    def dequeue(self):       # 出队
        if self.is_empty():
            raise Exception('queue is empty')
        else:
            self.queue.pop(0)
            self.front += 1

    def is_full(self):
        return self.rear-self.front+1 == self.size

    def is_empty(self):
        return self.front == self.rear

    def show_queue(self):
        print(self.queue)


if __name__ == '__main__':
    q = Queue(10)
    for i in range(6):
        q.enqueue(i)
    q.show_queue()
    for i in range(3):
        q.dequeue()
    q.show_queue()

```

# 堆栈

```python
# 堆栈
class Stack:
    def __init__(self, size):
        self.size = size   # 堆栈容量
        self.stack = []    # 列表表示堆栈
        self.top = -1      # 栈顶索引

    def push(self, x):     # 入栈
        if self.is_full():
            raise Exception('stack is full')
        else:
            self.stack.append(x)
            self.top += 1

    def pop(self):        # 出栈
        if self.is_empty():
            raise Exception('stack is empty')
        else:
            self.top -= 1
            self.stack.pop()

    def is_full(self):
        return self.top+1 == self.size

    def is_empty(self):
        return self.top == -1

    def show_stack(self):
        print(self.stack)

if __name__ == '__main__':
    s = Stack(10)
    for i in range(6):
        s.push(i)
    s.show_stack()
    for i in range(3):
        s.pop()
    s.show_stack()
```

# 哈希表

```python
class HashTable:
    def __init__(self, size):
        self.count = size      # 最大表长
        # 使用list作为哈希表元素保存方法
        self.elem = [None for i in range(size)]

    def hash(self, key):
        return key % self.count    # 散列函数采用除留余数法

    def insert_hash(self, key):    # 插入关键字到哈希表
        print(key)
        address = self.hash(key)   # 散列地址
        print(address)
        while self.elem[address] is not None:   # 发生冲突
            address = (address+1) % self.count
        print(address)
        self.elem[address] = key
        print(self.elem)

    def search_hash(self, key):    # 查找关键字
        start = address = self.hash(key)
        while self.elem[address] != key:
            address = (address+1) % self.count
            if not self.elem[address] or address == start:
                return False    # 说明没找到或者循环到了开始的位置
        return True

if __name__ == '__main__':
    list_a = [0, 12, 67, 56, 16, 25, 37, 22, 29, 15, 47, 48, 34]
    hash_table = HashTable(len(list_a))
    for i in list_a:
        hash_table.insert_hash(i)

    for i in hash_table.elem:
        print((i, hash_table.elem.index(i)))

    print(hash_table.search_hash(15))
    print(hash_table.search_hash(33))
```

# 单链表

```python

class Node(object):     # 节点
    def __init__(self, elem):
        self.elem = elem
        self.next = None

class SingleLinkList(object):
    def __init__(self, node=None):
        # 在传入头结点时则接收，在没有传入时，就默认头结点为空
        self.__head = node

    def is_empty(self):       # 链表是否为空
        return self.__head == None

    def length(self):         # 链表长度
        cur = self.__head     # cur游标，遍历节点
        count = 0
        while cur is not None:
            count += 1
            cur = cur.next
        return count

    def travel(self):         # 遍历整个链表
        cur = self.__head
        while cur is not None:
            print(cur.elem, end=' ')
            cur = cur.next
        print('\n')

    def add(self, item):      # 在链表头添加元素
        node = Node(item)
        node.next = self.__head
        self.__head = node

    def append(self, item):   # 在链表尾部添加元素
        node = Node(item)
        if self.is_empty():
            self.__head = node
        else:
            cur = self.__head
            while cur.next != None:
                cur = cur.next
            cur.next = node

    def insert(self, pos, item):   # 指定位置添加元素
        if pos <= 0:
            self.add(item)         # 插入到头部
        elif pos > self.length()-1:
            self.append(item)      # 插入到尾部
        else:
            per = self.__head
            count = 0
            while count < pos-1:
                count += 1
                per = per.next
            # 当循环退出，pre指向pos-1位置
            node = Node(item)
            node.next = per.next
            per.next = node

    def remove(self, item):      # 删除节点
        cur = self.__head
        pre = None
        while cur != None:
            if cur.elem == item:
                if cur == self.__head:
                    self.__head = cur.next
                else:
                    pre.next = cur.next
                break
            else:
                pre = cur
                cur = cur.next

    def search(self, item):    # 查找节点是否存在
        cur = self.__head
        while cur:
            if cur.elem == item:
                return True
            else:
                cur = cur.next
        return False

    def reverse(self):            # 反向链表
        if self.__head is None:   # 空链表没有翻转
            return
        pre = self.__head
        cur = pre.next
        pre.next = None
        while cur:
            temp = cur.next
            cur.next = pre
            pre = cur
            cur = temp
        self.__head = pre


if __name__ == '__main__':
    li = SingleLinkList()
    print(li.is_empty())
    print(li.length())

    li.append(3)
    li.add(999)
    li.insert(-3, 110)
    li.insert(99, 111)
    print(li.is_empty())
    print(li.length())
    li.travel()
    li.remove(3)

    li.travel()
    print(li.search(110))

    print('测试翻转：')
    li.reverse()
    li.travel()


```

# 二叉树

```python
class Node(object):
    def __init__(self, value=None, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class Tree(object):
    def __init__(self):
        self.root = Node()   # 根节点
        self.queue = []      # 辅助队列，协助树的生成

    def add(self, value):
        node = Node(value)
        if self.root.value is None:     # 增加根节点
            self.root = node
            self.queue.append(self.root)
        else:
            current_node = self.queue[0]   # 获取第一个元素
            if current_node.left is None:
                current_node.left = node
                self.queue.append(node)
            else:
                current_node.right = node
                self.queue.append(node)
                self.queue.pop(0)          # 第一个元素出队列

    # 前序遍历，根左右
    def preorder_traversal(self, root):
        if root is None:
            return
        print(root.value, end=' ')
        self.preorder_traversal(root.left)
        self.preorder_traversal(root.right)

    # 中序遍历，左根右
    def inorder_traversal(self, root):
        if root is None:
            return
        self.inorder_traversal(root.left)
        print(root.value, end=' ')
        self.inorder_traversal(root.right)

    # 后序遍历，左右根
    def postorder_traversal(self, root):
        if root is None:
            return
        self.postorder_traversal(root.left)
        self.postorder_traversal(root.right)
        print(root.value, end=' ')

    # 层次遍历
    def level_travelsal(self, root):
        if root is None:
            return
        q = []
        q.append(root)
        while q:
            node = q.pop(0)
            if node.left is not None:
                q.append(node.left)
            if node.right is not None:
                q.append(node.right)
            print(node.value, end=' ')


if __name__ == '__main__':
    tree = Tree()
    for i in range(10):
        tree.add(i)
    tree.preorder_traversal(tree.root)
    print()
    tree.inorder_traversal(tree.root)
    print()
    tree.postorder_traversal(tree.root)
    print()
    tree.level_travelsal(tree.root)

```

# 排序伪代码
```python
## 每轮在最右找比temp小的，在最左找比temp大的
def quick_sort(data, low, high):
    i , j = low, high
    temp = data[i]
    while i < j:
        while(i < j && temp <= data[j]):
            j-=1
        if i < j:
            data[i] = data[j]
            i+=1
        while(i < j && data[i] < temp):
            i+=1
        if i < j:
            data[j] = data[i]
            j-=1
    data[i] = temp
    if low < i:
        quick_sort(data, low, i-1)
    if i < high:
        quick_sort(data, j+1, high)


# 在 n 轮中每轮有 n-i 轮前后两两比较
def bubble_sort(data):
    n = len(data)
    for i in range(n):
        for j in range(n-i):
            if data[j] > data[j+1]:
                temp = data[j]
                data[j] = data[j+1]
                data[j+1] = temp 


# 归并排序
def merge(data, swap, k):
    m = 0
    n = len(data)
    l1 = 0
    while (l1+k <= n-1):
        l2 = l1 + k
        u1 = l2 - 1
        u2 = (l2+k-1 <= n-1) ? l2+k-1 : n-1

        # 两个有序合并,小数先进swap
        for (i=l1, j=l2; i<=u1, j<=u2; m++)
            if data[i] <= data[j]:
                swap[m] = data[i]
                i += 1
            else:
                swap[m] = data[j]
                j += 1

        # 组2先归并完
        while i <= u1:
            swap[m] = data[i]
            m++
            i++
        # 组1先归并完
        while j <=u2:
            swap[m] = data[j]
            m++
            j++

        l1 = u2+1   # 接下两组进行归并

    for (i=l1; i<n; i++, m++) # 奇数，剩余最后一组
        swap[m] = data[i]


def merge_sort(data):
    n = len(data)
    k = 1         # 每组数据的个数
    while k < n:
        merge(data, swap, k)
        k = 2*k   # 每组数据个数2倍增长

```