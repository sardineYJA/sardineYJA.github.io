---
layout: post
title: "Django models常见字段类型"
date: 2019-02-12
description: "介绍Django models常见字段类型"
tag: Web框架

---

# 常见字段
```
1. CharField
# 字符串字段, 用于较短的字符串.
# CharField 要求必须有一个参数 maxlength

2. IntegerField/PositiveIntegerField
# 用于保存一个整数/只能正整数

3. FloatField
# max_digits        总位数(不包括小数点和符号)
# decimal_places    小数位数

4. AutoField
# 系统会自动添加一个主键字段到你的 model.

5. BooleanField
# A true/false field. admin 用 checkbox 来表示此类字段.

6. TextField
# 一个容量很大的文本字段.

7. EmailField
# 带有检查Email合法性的 CharField,不接受 maxlength 参数.

8. DateField
# Argument     描述
# auto_now     当对象被保存时,自动将该字段的值设置为当前时间.
# auto_now_add 当对象首次被创建时,自动将该字段的值设置为当前时间.

9. DateTimeField
#  一个日期时间字段. 类似 DateField 支持同样的附加选项.

10. ImageField
# 类似 FileField, 不过要校验上传对象是否是一个合法图片.
# height_field和width_field,则图片将按提供的高度和宽度规格保存.

11. FileField
# 要求一个必须有的参数: upload_to, 一个用于保存上载文件的本地文件系统路径. 这个路径必须包含 strftime #formatting, 

12. URLField
# 保存 URL. 若verify_exists 参数为 True (默认), 给定的 URL 会预先检查是否存在(没有返回404响应).

13. IPAddressField
# 一个字符串形式的 IP 地址, (i.e. "24.124.1.30").
```


# 常见参数
```
1、null=True
数据库中字段可以为空

2、blank=True
django的 Admin 中添加数据时可允许空值

3、primary_key = False
主键，对AutoField设置主键后，就会代替原来的自增 id 列

4、auto_now 和 auto_now_add
auto_now   自动创建---无论添加或修改，都是当前操作的时间
auto_now_add  自动创建---永远是创建时的时间

5、choices
GENDER_CHOICE = (('M', 'Male'),('F', 'Female'),)
gender = models.CharField(max_length=2,choices = GENDER_CHOICE)

6、max_length        长度

7、default　　       默认值

8、verbose_name　　  Admin中字段的显示名称

9、name|db_column　　数据库中的字段名称

10、unique=True　　  不允许重复  

11、db_index = True　　数据库索引    

12、editable=True　　  在Admin里是否可编辑
  
13、error_messages=None　　错误提示  

14、auto_created=False　　 自动创建

15、help_text　　     在Admin中提示帮助信息

16、validators=[]    提示区间,例如电话号码范围

17、upload-to        文件上传目录
``` 

# 例子
```
name = models.CharField(max_length=128, verbose_name="姓名")
sex = models.IntegerField(choices=((1,'男'),(0,'女'),), verbose_name="性别", default=0)
email = models.EmailField(unique=True, verbose_name="Email")
created_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
href = models.URLField(verbose_name="链接")  # 默认长度200
is_nav = models.BooleanField(default=False, verbose_name="是否")
status = models.PositiveIntegerField(default=1, choices=(..), verbose_name="状态")
```

