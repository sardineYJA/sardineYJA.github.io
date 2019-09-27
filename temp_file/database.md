



外部临时表：

通过CREATE TEMPORARY TABLE 创建的临时表，这种临时表称为外部临时表。这种临时表只对当前用户可见，当前会话结束的时候，该临时表会自动关闭。这种临时表的命名与非临时表可以同名（同名后非临时表将对当前会话不可见，直到临时表被删除）。

 
内部临时表：

内部临时表是一种特殊轻量级的临时表，用来进行性能优化。这种临时表会被MySQL自动创建并用来存储某些操作的中间结果。这些操作可能包括在优化阶段或者执行阶段。这种内部表对用户来说是不可见的，但是通过EXPLAIN或者SHOW STATUS可以查看MYSQL是否使用了内部临时表用来帮助完成某个操作。

 

 delete和trucate的区别：

truncate table wp_comments;
delete * from wp_comments;
其中truncate操作中的table可以省略，delete操作中的 * 可以省略。这两者都是将wp_comments表中数据清空，不过也是有区别的，如下：

truncate是整体删除（速度较快）， delete是逐条删除（速度较慢）。
truncate不写服务器log，delete写服务器log，也就是truncate效率比delete高的原因。
truncate不激活trigger(触发器)，但是会重置Identity（标识列、自增字段），相当于自增列会被置为初始值，又重新从1开始记录，而不是接着原来的ID数。而delete删除以后，Identity依旧是接着被删除的最近的那一条记录ID加1后进行记录。
程度从强到弱

1、drop  table tb 
      删除表的结构和数据，没有办法找回
2、truncate (table) tb
      删除表中的所有记录，表结构还在，不写日志，无法找回删除的记录，速度快，不能与where一起使用
3、delete from tb (where)
      一行一行地删除所有记录，表结构还在，写日志，可以恢复的，速度慢。
 
区别：truncate和delete的区别
         1、事务：truncate是不可以rollback的，但是delete是可以rollback的；
              原因：truncate删除整表数据(ddl语句,隐式提交)，delete是一行一行的删除，可以rollback
         2、效果：truncate删除后将重新水平线和索引(id从零开始) ,delete不会删除索引    
         3、 truncate 不能触发任何Delete触发器。
         4、delete 删除可以返回行数



# 参考

https://www.cnblogs.com/domi22/p/8538628.html

