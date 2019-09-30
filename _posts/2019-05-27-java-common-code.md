---
layout: post
title: "Common Code"
date: 2019-05-27
description: "Common Code"
tag: Java

---

## 日志信息

slf4j(Simple Logging Facade for Java)，是一系列的日志接口，是Java中所有日志框架的抽象

创建src/main/resources/log4j.properties

```
log4j.rootCategory=INFO, console
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.target=System.err
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n
```

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
public static Logger logger = LoggerFactory.getLogger(Xxx.class);
logger.error("Error Message!");
logger.warn("Warn Message!");
logger.info("Info Message!");
logger.debug("Debug Message!");
```

## 获取当前时间

```java
import java.text.SimpleDateFormat;
import java.util.Date;
SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
System.out.println(df.format(new Date()));
// 2019-08-19 17:50:46

import java.sql.Timestamp;
Timestamp currentTime = new Timestamp(System.currentTimeMillis());
System.out.println(currentTime);
// 2019-08-19 17:50:46.452
```

## 批量转码

```java
import java.io.*;
import java.util.ArrayList;
// 批量文件转码
public class ToEncode {
	
	public static void main(String[] args) throws IOException {
		String inPathStr = "D:/in";
		String outPathStr = "D:/out";    // 不需要事先创建
		convertEncode(new File(inPathStr), outPathStr, "GBK", "utf-8");
		System.out.println("Main is complete");
	}
	 
	public static void convertEncode(File file, String outPathStr, String inEncode, String outEncode)  {
		
	    if (file.isFile() && file.getName().endsWith(".md")) {
	        BufferedReader br = null;
	        PrintStream out = null;
			try {
				// 以InputEncode编码读取
				br = new BufferedReader(new InputStreamReader(new FileInputStream(file), inEncode));
				ArrayList<String> lines = new ArrayList<String>();
		        String line;
		        while ((line = br.readLine()) != null)
		            lines.add(line);
		        br.close();
		       
		        // 创建子文件夹
		        File outPath = new File(outPathStr);
		        if (!outPath.exists()) {
		        	outPath.mkdirs();
		        }
		        
		        File savefile = new File(outPathStr+file.getName());
		        // 以outputEncode编码写出
		        out = new PrintStream(savefile, outEncode);
		        for (String s : lines)
		            out.println(s);
			} catch (Exception e) {
				System.out.println(file.toString() + "======= error");
			} finally {
		        out.flush();
		        out.close();
			}
	        System.out.println(file.toString() + " ---- OK");
	        
	    } else if (file.isDirectory()) {
	    	String dir = file.getName();
	        File[] files = file.listFiles();
	        if (files != null) {
	            for (File f : files) {
	            	convertEncode(f, outPathStr+"/"+dir+"/", inEncode, outEncode);
	            } 
	        }
	    }
	}
}
```


