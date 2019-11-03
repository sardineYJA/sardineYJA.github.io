---
layout: post
title: "adb 常用命令"
date: 2018-03-01
description: "adb 常用命令"
tag: Interest

---

## 前言

以前使用过安卓手机的挂机软件，不过基本上要root。简单控制手机发现adb命令也可以


## adb

adb即Android Debug Bridge，就是可以通过窗口命令，使在pc端可以调试安卓移动端的一个工具包。主要存放在sdk安装目录下的platform-tools文件夹中。

下载：https://developer.android.com/studio/releases/platform-tools.html

设置环境变量，手机开启开发者模式，打开`USB调试`

测试命令：

```sh
adb devices   # 查看设备

adb shell     # 进入shell

adb shell screencap -p /sdcard/1.png   # 屏幕截图，保存到内存卡

adb pull /sdcard/1.png D:/1.png        # 将图片上传到D盘

adb push D:/1.png /sdcard/1.png        # 将D盘图片上传到SD卡

adb shell input touchscreen swipe x1 y1 x2 y2 time  
# 从[x1,x2]点滑动到[x2,y2]点，然后滑动的时间（毫秒）
# 例：adb shell input touchscreen swipe 170 180 170 180 500

adb shell wm size  # 查看屏幕分辨率

```


## 手机设置

手机坐标以左上角为原点，向右表示x轴，向下表示y轴

可以在开发者选项中开启：指针位置。即可以获取某个点的具体坐标


## 跳一跳案例

参考网上adb命令对跳一跳小程序的测试：

主要思想：手机截图，将图片上传到PC端，在面板打开图片，点击起点与终点，计算触碰屏幕时间。


截图命令：`adb shell screencap -p [图片路径]`

模拟滑动事件：`adb shell input touchscreen swipe x1 y1 x2 y2 time`

滑动参数可以看到，从[x1,x2]点滑动到[x2,y2]点，然后滑动的时间。


> IOException: Cannot run program "adb": CreateProcess error=2, 系统找不到指定的文件。

设置adb环境变量后，依然报错。因为 IDEA 无法识别 adb 环境路径，重启 IDEA 即可。



```java
public class Point {
	public int x;
	public int y;
}
```

```java
public class Utils {	
	public static void jump(int time){    // 触碰手机
		try {
	        Runtime.getRuntime().exec("adb shell input touchscreen swipe 170 187 170 187 " + time);
	    } catch (Exception e) {
	        e.printStackTrace();
	    }
	}
	
	public static void screen(){       // 截图并上传
		try {
	        Process p1 = Runtime.getRuntime().exec("adb shell screencap -p /sdcard/jump.png");
	        p1.waitFor();
	        Process p2 = Runtime.getRuntime().exec("adb pull /sdcard/jump.png D:\\jump.png");
	        p2.waitFor();
	    } catch (Exception e) {
	    }
	}

	public static int calDistance(Point p1, Point p2){        // 两点之间的距离
		return (int)Math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y));
	}

}
```

```java
public class PhoneImagePanel extends JPanel{
	private Image image=null; 
	@Override
	public void paint(Graphics g){
		try {
			Utils.screen();
			//这个路径需要自己设定
			image = ImageIO.read(new File("D:\\jump.png"));
			//这个图像展示大小需要自己设定，这里用的是Pixel手机1080*1920，我缩减一半
			g.drawImage(image, 0, 0, 540, 960, null);
		} catch (Exception e) {
			e.printStackTrace();
		}

	}
}
```

```java
public class WXJumpGame extends JFrame{
	private PhoneImagePanel phoneImgPanel = null;
	private boolean isFirst = true;
	private Point prePoint = new Point();
	private Point curPoint = new Point();

	public WXJumpGame(){
		phoneImgPanel = new PhoneImagePanel();
		this.add(phoneImgPanel);
		this.setSize(540, 960);
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		this.setVisible(true);
		// 给图像面板添加鼠标点击事件
		phoneImgPanel.addMouseListener(new MouseListener() {
			
			@Override
			public void mousePressed(MouseEvent event) {
				// 每次在跳动之前，需要点击球柱的起跳点，也就是中心点
				if(isFirst){
					prePoint.x = event.getX();
					prePoint.y = event.getY();
					isFirst = false;
					return;
				}
				curPoint.x = event.getX();
				curPoint.y = event.getY();
				// 使用勾股定理计算跳跃的距离
				int distance = Utils.calDistance(prePoint, curPoint);
				// 这个定值是需要手动调解出来的，每个手机尺寸或许不一样，需要自己手动调节
				int time = (int)(distance/0.37);
				Utils.jump(time);
				System.out.println("distance:"+distance+",time:"+time);
				// 这里的时间是为了等待截图绘制图片到面板中，时间也是需要自己设定，不然图像绘制会出现错乱
				try {
					Thread.sleep(3000);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				// 为了下一次能够点击起跳点
				isFirst = true;
				// 跳完了，就开始刷新面板，获取最新的手机屏幕信息
				phoneImgPanel.validate();
				phoneImgPanel.repaint();
			}
			
			@Override
			public void mouseReleased(MouseEvent event) {}
			
			@Override
			public void mouseExited(MouseEvent event) {}
			
			@Override
			public void mouseEntered(MouseEvent event) {}
			
			@Override
			public void mouseClicked(MouseEvent event) {}
		});
	}

	public static void main(String[] args){
		new WXJumpGame();
	}

}
```

## 获取 adb 返回值

```java
public static String InputStream2String(InputStream inputStream){
    String result="";
    BufferedReader br=new BufferedReader(new InputStreamReader(inputStream));
    String temp="";
    while ((temp=br.readLine())!=null){
        result+=temp+"\n";
    return result;
}

public static void main(String[] args) throws IOException {
    Process adb_version = Runtime.getRuntime().exec("adb version");
    System.out.println(InputStream2String(adb_version.getInputStream()));

}
```

# Python 版

之前想测试一下连点器的，发现subprocess.check_output执行需要大约1秒。
如果想要短时间连点，还是不合适。

```python
import subprocess  # 执行adb命令
import re
import time

def connectDevcie():
    '''检查设备是否连接成功，如果成功返回True，否则返回False'''
    try:
        deviceInfo = subprocess.check_output('adb devices')
        '''如果没有链接设备或者设备读取失败，第二个元素为空'''
        deviceInfo = bytes.decode(deviceInfo)    # 字节转字符串
        deviceInfo = deviceInfo.split("\r\n")
        if deviceInfo[1] == '':    #没有一个设备连接
            return False
        else:
            return True
    except:
        print("connect error")

if __name__ == "__main__":

    i = 0
    while(True):
        time.sleep(0.001)
        subprocess.check_output('adb shell input tap 400 400')    # 此命令执行时间将近1s
        print("第" + i + "次点击屏幕")
        i += 1
    print('OK')
```




