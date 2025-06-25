from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect

from app import models


# 打开系统首页
def toWelcomeView(request):
    return render(request,'welcome.html')  #渲染欢迎页面

def toPageGradeInfos(request):
    pageIndex = request.GET.get('pageIndex',1)
    pageSize = request.GET.get('pageSize',10)
    data=models.Grades.objects.all()#获取所有的页面
    page=Paginator(data,pageSize)
    resl=[]
    for item in page.page(pageIndex):
        resl.append({
            'id': item.id,
            'name': item.name,
            'address': item.address,
        })
    return render(request,'grades/data.html',{'pageIndex':int(pageIndex),
        'pageSize':int(pageSize),'count':page.count,'data':resl,'pageTotal':page.page(pageIndex).paginator.num_pages})

#跳转班级添加页面
def toPageGradeView(request):
    return render(request,'grades/add.html')

#添加班级信息
def addGradeForm(request):
    models.Grades.objects.create(name=request.POST['name'],address=request.POST['address'])
    return redirect('/grades/page')

#跳转班级修改页面
def toUpdGradeView(request):
    info=models.Grades.objects.get(id=request.GET['id'])
    return render(request,'grades/upd.html',{'info':info})

#添加修改班级信息函数
def updGradeForm(request):
    models.Grades.objects.filter(id=request.POST['id']).update(name=request.POST['name'],address=request.POST['address'])
    return redirect('/grades/page')


#删除班级信息
def delGradeForm(request):
    models.Grades.objects.filter(id=request.GET['id']).delete()
    return redirect('/grades/page')

#分页查询学生信息
def getPageStudentInfos(request):
    pageIndex = request.GET.get('pageIndex', 1)
    pageSize = request.GET.get('pageSize', 5)
    data=models.Students.objects.all()#获取所有的页面
    page=Paginator(data,pageSize)
    resl=[]
    for item in page.page(pageIndex):
        resl.append({
            'id': item.id,
            'name': item.name,
            'gender': item.gender,
            'age': item.age,
            'intoTime': item.intoTime,
            'gradeId': item.grade.id,
            'gradeName': item.grade.name,
        })
    return render(request,'students/data.html',{'pageIndex':int(pageIndex),
                                                'pageSize':int(pageSize),'count':page.count,'data':resl,
                                                'pageTotal':page.page(pageIndex).paginator.num_pages})



#跳转学生信息添加界面
def toAddStudentView(request):
    grades=models.Grades.objects.all()
    return render(request,'students/add.html',{'grades':grades})

#添加学生信息
def addStudentForm(request):
    models.Students.objects.create(
        name=request.POST['name'],
        gender=request.POST['gender'],
        age=request.POST['age'],
        intoTime=request.POST['intoTime'],
        grade=models.Grades.objects.get(pk=request.POST['gradeId']))
    return redirect('/students/page')

#跳转学生信息修改界面
def toUpdateStudentView(request):
    grades=models.Grades.objects.all()
    info=models.Students.objects.get(id=request.GET['id'])
    return render(request,'students/upd.html',{'info':info,'grades':grades})

#修改学生信息
def updStudentForm(request):
    models.Students.objects.filter(id=request.POST['id']).update(
        name=request.POST['name'],
        gender=request.POST['gender'],
        age=request.POST['age'],
        intoTime=request.POST['intoTime'],
        grade=models.Grades.objects.get(pk=request.POST['gradeId'])
    )
    return redirect('/students/page')

#删除学生信息
def delStudentForm(request):
    models.Students.objects.filter(id=request.GET['id']).delete()
    return redirect('/students/page')

