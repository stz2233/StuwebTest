from django.db import models

# 班级信息
class Grades(models.Model):
    objects = None
    id = models.AutoField('记录ID',primary_key=True)
    name = models.CharField('班级名称',max_length=50,null=False)
    address = models.CharField('班级位置',max_length=50,null=False)
    class Meta:
        db_table = 'grades' #表名

#学生信息
class Students(models.Model):
    id = models.CharField('学生学号',primary_key=True,null=False,max_length=20)
    name = models.CharField('学生姓名',max_length=30,null=False)
    gender = models.CharField('学生性别',max_length=2,null=False)
    age = models.IntegerField('学生年龄',null=False)
    intoTime=models.CharField('入学时间',db_column="into_time",null=False,max_length=19) #数据库的字段名称为into_time,而python的变量名称为intoTime
    grade = models.ForeignKey(Grades,db_column='grade_id',null=False,on_delete=models.CASCADE)
    class Meta:
        db_table = 'students'
