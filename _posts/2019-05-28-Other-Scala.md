---
layout: post
title: "Scala 语法复习"
date: 2019-05-28
description: "语法复习"
tag: Other

---

# Scala

## 安装

1. 需先安装JDK，并配置环境

2. 安装Scala，并配置环境

## 编译
1. scalac Hello.scala 编译为字节码
2. scala Hello        JVM虚拟机运行字节码

```java
object Hello {
	def main(args:Array[String]):Unit = {
		println("Hello")
	}
}
```

## 数据类型

1. Unit 表示无值，等同void

2. Null 表示空应用

3. Nothing 最低端类，是任何其他类型的子类型

4. Any 是所有其他类的超类

5. AnyRef 是所以引用类的基类


## 语法

1. 语句末尾分号可选

2. import java.awt._  // 引用包内所有成员

3. import java.awt.{Color, Font}  // 引用多个

4. import java.util.{HashMap => JavaHashMap} // 重命名

5. import java.util.{HashMap =>_ , _ } // 引入了util包的所有成员，但是HashMap被隐藏了

6. var 变量，val 常量不可修改

7. val xmax, ymax = 100    // xmax, ymax都声明为100

8. val 可以定义函数，def定义方法

```Java
class Test {
	def m(x:Int) = x + 3
	val f = (x:Int) => x +3
}
```

9. 定义方法：

```java
def functionName([列表参数]) : [return type] = {
	function body
	return [expr]
}
```

10. 数组，索引使用的是括号

```java
var z = new Array[String](2)
z(0) = "String1"
z(1) = "String2"
```

11. 数组

```java
var mylist = Array(1,2,3,4,5)
for (x <- mylist) {
	println(x)
}
for (i <- 0 to (list.length -1)) {
	println(mylist(x))
}

var mylist2 = concat(mylist, mylist)  // 数组合并

var mylist3 = range(10, 20, 2)  // 10到20（不含），间隔为2
// 10 12 14 16 18
```

12. 多维数组：ofDim[Int](3,3)

```java
var myMatrix = ofDim[Int](3,3)
for (i <- 0 to 2) {
	for (i <- 0 to 2) {
		myMatrix(i)(j) = i*j
	}
}
```


## 可变集合 和 不可变集合

1. List 线性存储，可存放重复对象
`val x = List(1,2,3)`

2. Set 没有重复对象
`val x = Set(1,3,5)`

3. Map 键值对
`val x = Map("one"->1, "two"->2, "three"->3)`

4. 元组 不同类型的值的集合
`val x = (10, "String")`

5. Option 容器
`val x:Option[Int] = Some(5)`

6. Iteration 迭代器

```java
val it = Iterator("String", "baidu", "google")
while (it.hasNext()) {
	println(it.next())
}
```

## 空值

1. null 是一个关键字而不是对象

2. Option的两个子类：None和Some

3. None 是一个实例对象


## 类

```java
import java.io._

class Point(xc:Int, yc:Int) {
	var x:Int = xc
	var y:Int = yc

	def move(dx:Int, dy:Int) {
		x = x + dx
		y = y + dy
	}

	override def toString = getClass.getName + x + y

}

object Test {
	def main(args:Array[String]) {
		val pt = new Point(10, 10)
		pt.move(20, 20)
	}
}
```

## 继承

1. 重写一个非抽象方法必须使用override修饰(父子都要)

2. 只有主构造函数才可以往基类的构造函数写参数

3. 在子类中重写超类的抽象方法时，不需要使用override

4. 只允许继承一个父类

```java
class Location(override val xc:Int, override val yc:Int, val zc:Int)
	extends Point(xc, yc) {
		var z:Int = zc
		
		def move(dx:Int, dy:Int, dz:Int) {
			...
		}

		override def toString = super.toString + z
	}
```

## 伴生对象

单例对象与某个类同名，则是此类的伴生对象，类和伴生对象可互相访问其私有成员

```java
//  私有构造函数
class Marker private(val color:String) {
	override def toString(): String = "颜色：" + color
}

object Marker {
	private val markers:Map[String, Marker] = Map(
		"red" -> new Marker("red")
		"blue" -> new Marker("blue")
		)

	def apply(color:String) = {
		if (markers.contains(color)) markers(color) else null
	}

	def main(args:Array[String]) {
		println(Marker("red"))
	}
}
```


## Trait 特征（相当于接口）

trait 可多继承

```java
trait Equal {
	// 未实现的方法
	def isEqual(x:Any):Boolean
	def isNotEqual(x:Any):Boolean = !isEqual
}
```

## 模式匹配

按顺序逐一匹配

```java
def matchTest(x:Any): Any = x match {
	case 1 => "one"
	case "two" => 2
	case y:Int => "scala.Int"
	case _ => "default"
}
```

## 异常处理

```java
import java.io._
object Test {
	def main(args: Array[String]) {
		try {
			val f = new FileReader("1.txt")
		} catch {
			case ex: FileNotFoundException => {
				println("Missing file exception")
			}
			case ex: IOException => {
				println("IO Exception")
			}
		} finally {
			println("Exiting")
		}
	}
}
```


