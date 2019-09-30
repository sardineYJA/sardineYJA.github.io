---
layout: post
title: "python基础复习"
date: 2018-03-09
description: "简单复习python语法"
tag: Python

---

# 知识点

## Python 解释器：

1. CPython 就是用 C 语言开发的了，是官方标准实现，拥有良好的生态，所以应用也就最为广泛了。
2. IPython 是在 CPython 的基础之上在交互式方面得到增强的解释器（http://ipython.org/）。
3. Jython 是专为 Java 平台设计的 Python 解释器（http://www.jython.org/），它把 Python 代码编译成 Java 字节码执行。
4. PyPy 目标是执行速度。采用JIT技术，对Python代码进行动态编译（注意不是解释），所以可以显著提高Python代码的执行速度。
5. IronPython 和Jython类似，只不过IronPython是运行在微软.Net平台上的Python解释器，可以直接把Python代码编译成.Net的字节码。


## 语法知识

可以同时为多个变量赋值，如a, b = 1, 2。

a/b 返回一个浮点数，a//b 返回一个整数。

用a + bj,或者complex(a,b)表示， 复数的实部a和虚部b都是浮点型。

反斜杠转义特殊字符，如不想让反斜杠发生转义，可以在字符串前面添加一个 r，表示原始字符串。

Python 字符串不能被改变。向一个索引位置赋值，比如word[0] = 'm'会导致错误。

元组中只含一个元素时，需在元素后面添加逗号，否则括号会被当作运算符使用。

字典中的键必须不可变，所以可以用数字，字符串或元组充当，而用列表就不行。

集合（set）是一个无序的不重复元素序列。

^ 按位异或运算符：当两对应的二进位相异时，结果为1

~ 按位取反运算符：对数据的每个二进制位取反，即把1变为0，把0变为1。

```python
    # 翻转字符串
    # 第一个参数 -1 表示最后一个元素
    # 第二个参数为空，表示移动到列表末尾
    # 第三个参数为步长，-1 表示逆向
    inputWords=inputWords[-1::-1]    # 'I like runoob' --> runoob like I
```


## 可变/不可变对象

Python中有可变对象和不可变对象之分。可变对象创建后可改变但地址不会改变，即变量指向的还是原来的变量；不可变对象创建之后便不能改变，如果改变则会指向一个新的对象。

Python3 的六个标准数据类型中：

不可变数据（3 个）：Number（数字）、String（字符串）、Tuple（元组）

可变数据（3 个）：List（列表）、Dictionary（字典）、Set（集合）


## 函数传递参数

Python中函数参数是引用传递（注意不是值传递）。对于不可变类型（`数值型、字符串、元组`），因变量不能修改，所以运算不会影响到变量自身；而对于可变类型（`列表、字典、集合`）来说，函数体运算可能会更改传入的参数变量。

```python
def test_add(a):
    a += a
a = 1
print(a)           # 1
test_add(a)
print(a)           # 1
a_list = [1, 2]
print(a_list)      # [1, 2]
test_add(a_list)
print(a_list)      # [1, 2, 1, 2]
```

## is 和 == 的区别

只要 a 和 b 的值相等，a == b 就会返回True，而只有 id(a) 和 id(b) 相等时，a is b 才返回 True。 is 的作用是用来检查对象的标示符是否一致，也就是比较两个对象在内存中的地址是否一样，而 == 是用来检查两个对象是否相等。在检查 a is b 的时候，其实相当于检查 id(a) == id(b)。而检查 a == b 的时候，实际是调用了对象 a 的 __eq()__ 方法，a == b 相当于 a.__eq__(b)。 is 返回True表明这两个对象指向同一块内存，值也一定相同。

Python里和None比较时，是 is None 而不是 == None，因为None在Python里是个单例对象，一个变量如果是None，它一定和None指向同一个内存地址。而 == None背后调用的是__eq__，而__eq__可以被重载。

## + 和 join 的区别

字符串是不可变对象，当用操作符+连接字符串的时候，每执行一次+都会申请一块新的内存，然后复制上一个+操作的结果和本次操作的右操作符到这块内存空间，因此用+连接字符串的时候会涉及好几次内存申请和复制。而join在连接字符串的时候，会先计算需要多大的内存存放结果，然后一次性申请所需内存并将字符串复制过去，这是为什么join的性能优于+的原因。所以在连接字符串数组的时候，应考虑优先使用join。

## \__new__和__init__的区别

1. \__new__是在实例创建之前被调用的，因为它的任务就是创建实例然后返回该实例对象，是个静态方法。
2. \__init__是当实例对象创建完成后被调用的，然后设置对象属性的一些初始值，通常用在初始化一个类实例的时候。是一个实例方法。
3. \__new__先被调用，\__init__后被调用，\__new__的返回值（self实例）将传递给__init__方法的第一个参数，然后__init__给这个实例设置一些参数。


## with 上下文管理器

实现了__enter__和__exit__方法的对象就称之为上下文管理器。
1. \__enter__一般用于资源分配，如打开文件、连接数据库、获取线程锁；
2. \__exit__一般用于资源释放，如关闭文件、关闭数据库连接、释放线程锁。


## Python2和Python3的编码

python2内容进行编码（默认ascii）,而python3对内容进行编码的默认为utf-8。在python2 中是不区分bytes和str类型的。在python3中bytes和str中是区分的，str的所有操作bytes都支持。
在Python2中，普通字符串是以8位ASCII码进行存储的，而Unicode字符串则存储为16位unicode字符串，这样能够表示更多的字符集。使用的语法是在字符串前面加上前缀 u。
在Python3中，所有的字符串都是Unicode字符串。
```python
# Python2
import sys
sys.getdefaultencoding()  # 'ascii'
# Python3
import sys
sys.getdefaultencoding()  # 'utf-8'
```

1. ascii     最多只能用8位来表示（一个字节），即：2**8 = 256，所以，ASCII码最多只能表示 256 个符号。
2. unicode   万国码，任何一个字符==两个字节
3. utf-8     万国码的升级版  一个中文字符==三个字节   英文是一个字节  欧洲的是 2个字节
4. gbk       国内版本  一个中文字符==2个字节   英文是一个字节
5. gbk 转 utf-8  需通过媒介 unicode


## 深/浅拷贝

浅拷贝只是增加了一个指针指向一个存在的地址，而深拷贝是增加一个指针并且开辟了新的内存，这个增加的指针指向这个新的内存，采用浅拷贝的情况，释放内存，会释放同一内存，深拷贝就不会出现释放同一内存的错误。


## re 的 match 和 search 区别

1. re.match 尝试从字符串的起始位置匹配一个模式，如果不是起始位置匹配成功的话，match()就返回none。
2. re.search 扫描整个字符串并返回第一个成功的匹配。

## 列表赋值

a=[1,2,3,4,5]，b=a和b=a[:]有区别

```python
a = [1,2,3,4,5]
b = a
b1 = a[:]
print(b)       #  [1, 2, 3, 4, 5]
b.append(6)
print("a",a)   # a [1, 2, 3, 4, 5, 6]
print("b",b)   # b [1, 2, 3, 4, 5, 6]  传递引用
print("b1",b1) # b1 [1, 2, 3, 4, 5]    拷贝
```

## 迭代器

迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。迭代器只能往前不会后退。
迭代器：含有__iter__和__next__方法 (包含__next__方法的可迭代对象就是迭代器)。

```python
data_list = [1,2,3,4]
it = iter(data_list)
print(next(it))   # 1
print(next(it))   # 2
```

把一个类作为迭代器使用，需要在类中实现__iter__() 和 \__next__() 方法，
StopIteration异常用于标识迭代的完成，防止出现无限循环的情况，在__next__()方法中可以设置
在完成指定循环次数后触发 StopIteration 异常来结束迭代。

```python
class MyNumbers:
	def __iter__(self):
		self.a = 1
		return self

	def __next__(self):
		if self.a <= 20:
			x = self.a
			self.a += 1
			return x
		else:
			raise StopIteration

myclass = MyNumbers()
myiter = iter(myclass)
for x in myiter:
	print(x)

```

## 生成器

使用了 yield 的函数被称为生成器（generator）。
包括含有yield这个关键字，生成器也是迭代器，调动next把函数变成迭代器。

```python
# yield 实现斐波列数
import sys
def fibonacci(n):   # 生成器函数 - 菲波那切数列
	a, b, counter = 0, 1, 0
	while True:
		if (counter > n):
			return
		yield a
		a, b = b, a+b
		counter += 1

f = fibonacci(10)    # f 是一个迭代器，由生成器返回生成
while True:
	try:
		print(next(f), end=' ')
	except StopIteration:
		sys.exit()

```

## 闭包

bar()在foo()的代码块中定义。我们称bar是foo的内部函数。在bar的局部作用域中可以直接访问foo局部作用域中定义的m、n变量。简单的说，这种内部函数可以使用外部函数变量的行为，就叫闭包。

```python
def foo():
    m=3
    n=5
    def bar():
        a=4
        return m+n+a
    return bar
bar =  foo()
bar()          # 12
```


## \*args和 \*\*kwargs的区别

1. \*args 用来将参数打包成tuple给函数

```python
def function(*args):
    print(args, type(args))
function(1)                 # (1,) <class 'tuple'>

def function(x, y, *args):  # (x, y, *args, z) 会报错
    print(x, y, args)
function(1, 2, 3, 4, 5)     # 1 2 (3, 4, 5)
```

2. \*\*kwargs 打包关键字参数成dict给函数

```python
def function(**kwargs):
    print(kwargs)
function(a=1, b=2, c=3)           # {'a': 1, 'b': 2, 'c': 3}

def function(arg,*args,**kwargs):
    print(arg,args,kwargs)
function(6,7,8,9,a=1, b=2, c=3)   # 6 (7, 8, 9) {'a': 1, 'b': 2, 'c': 3}
```

`参数arg、*args、**kwargs三个参数的位置必须是一定的。必须是(arg,*args,**kwargs)这个顺序，否则程序会报错。`

## 垃圾回收机制

python采用的是引用计数机制为主，标记-清除和分代收集两种机制为辅的策略。
python里每一个东西都是对象，它们的核心就是一个结构体：PyObject
```C++
 typedef struct_object {
 int ob_refcnt;
 struct_typeobject *ob_type;
} PyObject;
```
PyObject是每个对象必有的内容，其中ob_refcnt就是做为引用计数。当一个对象有新的引用时，它的ob_refcnt就会增加，当引用它的对象被删除，它的ob_refcnt就会减少
当引用计数为0时，该对象生命就结束了。

### 引用计数机制的优点：
1. 简单
2. 实时性：一旦没有引用，内存就直接释放了。不用像其他机制等到特定时机。
3. 实时性还带来一个好处：处理回收内存的时间分摊到了平时。

### 引用计数机制的缺点：
1. 维护引用计数消耗资源
2. 循环引用

```python
list1 = []
list2 = []
list1.append(list2)
list2.append(list1)
```

list1与list2相互引用，如果不存在其他对象对它们的引用，list1与list2的引用计数也仍然为1，所占用的内存永远无法被回收，这将是致命的。
对于如今的强大硬件，缺点1尚可接受，但是循环引用导致内存泄露，注定python还将引入新的回收机制。(标记清除和分代收集)

针对循环引用的情况：有一个“孤岛”或是一组未使用的、互相指向的对象，但是谁都没有外部引用。换句话说，程序不再使用这些节点对象了，所以希望Python的垃圾回收机制能够足够智能去释放这些对象并回收它们占用的内存空间。但是这不可能，因为所有的引用计数都是1而不是0。Python的引用计数算法不能够处理互相指向自己的对象。你的代码也许会在不经意间包含循环引用并且你并未意识到。事实上，当你的Python程序运行的时候它将会建立一定数量的“浮点数垃圾”，Python的GC不能够处理未使用的对象因为应用计数值不会到零。 这就是为什么Python要引入Generational GC算法的原因！ 

『标记清除（Mark—Sweep）』算法是一种基于追踪回收（tracing GC）技术实现的垃圾回收算法。它分为两个阶段：第一阶段是标记阶段，GC会把所有的『活动对象』打上标记，第二阶段是把那些没有标记的对象『非活动对象』进行回收。那么GC又是如何判断哪些是活动对象哪些是非活动对象的呢？对象之间通过引用（指针）连在一起，构成一个有向图，对象构成这个有向图的节点，而引用关系构成这个有向图的边。从根对象（root object）出发，沿着有向边遍历对象，可达的（reachable）对象标记为活动对象，不可达的对象就是要被清除的非活动对象。根对象就是全局变量、调用栈、寄存器。

分代垃圾回收算法的核心行为：垃圾回收器会更频繁的处理新对象。一个新的对象即是你的程序刚刚创建的，而一个来的对象则是经过了几个时间周期之后仍然存在的对象。Python会在当一个对象从零代移动到一代，或是从一代移动到二代的过程中提升(promote)这个对象。

### gc的逻辑：

1. 分配内存
2. 发现超过阈值了
3. 触发垃圾回收
4. 将所有可收集对象链表放到一起
5. 遍历, 计算有效引用计数
6. 分成 有效引用计数=0 和 有效引用计数 > 0 两个集合
7. 大于0的, 放入到更老一代
8. =0的, 执行回收
9. 回收遍历容器内的各个元素, 减掉对应元素引用计数(破掉循环引用)
10. 执行-1的逻辑, 若发现对象引用计数=0, 触发内存回收
11. python底层内存管理机制回收内存



# 参考

1. https://www.cnblogs.com/pinganzi/p/6646742.html

2. https://blog.csdn.net/xiongchengluo1129/article/details/80462651

3. https://www.runoob.com/w3cnote/python-func-decorators.html
