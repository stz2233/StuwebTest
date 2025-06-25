from django.urls import path

import app.views

urlpatterns = [
    path('', app.views.toWelcomeView),
    path('grades/page', app.views.toPageGradeInfos),
    path('grades/add/view', app.views.toPageGradeView),
    path('grades/add/form', app.views.addGradeForm),
    path('grades/upd/view', app.views.toUpdGradeView),
    path('grades/upd/form', app.views.updGradeForm),
    path('grades/del/form', app.views.delGradeForm),
    path('students/page', app.views.getPageStudentInfos),
    path('students/add/view', app.views.toAddStudentView),
    path('students/add/form', app.views.addStudentForm),
    path('students/upd/view', app.views.toUpdateStudentView),
    path('students/upd/form', app.views.updStudentForm),
    path('students/del/form', app.views.delStudentForm),

]
