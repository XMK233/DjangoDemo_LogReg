# coding=utf-8
from django.shortcuts import render

from django.shortcuts import render, render_to_response
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import auth
from models import User

import pdb
import time

class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput())
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    email = forms.EmailField(label='电子邮件')


class UserFormLogin(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    checkcode = forms.CharField(label='验证码')

def check_code(request):
    import io
    import check_code as CheckCode
    stream = io.BytesIO()
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")
    request.session['checkcode'] = code
    return HttpResponse(stream.getvalue(), "png")

def login(request):
    if request.method == "POST":
        uf = UserFormLogin(request.POST)
        if uf.is_valid():
            # 获取表单信息
            input_code = request.session['checkcode'].upper()
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            checkcode = uf.cleaned_data['checkcode'].upper()

            if input_code == checkcode:

                userResult = User.objects.filter(username=username, password=password)
                # pdb.set_trace()
                if (len(userResult) > 0):
                    response = render_to_response('Success.html',
                                                  {'operation': "登录", 'username': username},
                                                  context_instance=RequestContext(request))
                    response.set_cookie('username',username,60)
                    return response
                else:
                    #return HttpResponse("该用户不存在")
                    return render_to_response('register.html',
                                              {"errors": "该用户不存在"},
                                              context_instance=RequestContext(request))
            else:
                return render_to_response('register.html',
                                          {"errors": "请输入验证码"},
                                          context_instance=RequestContext(request))
    else:
        uf = UserFormLogin()


    return render_to_response("userlogin.html", {'uf': uf}, context_instance=RequestContext(request))


def register(request):
    if request.method == "POST":
        uf = UserForm(request.POST)
        if uf.is_valid():
            # 获取表单信息
            username = uf.cleaned_data['username']
            # pdb.set_trace()
            # try:
            filterResult = User.objects.filter(username=username)
            if len(filterResult) > 0:
                return render_to_response('register.html',
                                          {"errors": "用户名已存在"},
                                          context_instance=RequestContext(request))
            else:
                password1 = uf.cleaned_data['password1']
                password2 = uf.cleaned_data['password2']
                errors = []
                if (password2 != password1):
                    errors.append("两次输入的密码不一致!")
                    return render_to_response('register.html',
                                              {'errors': errors},
                                              context_instance=RequestContext(request))
                    # return HttpResponse('两次输入的密码不一致!,请重新输入密码')
                password = password2
                email = uf.cleaned_data['email']
                # 将表单写入数据库
                user = User.objects.create(username=username, password=password1, email=email)
                # user = User(username=username,password=password,email=email)
                user.save()
                #pdb.set_trace()
                # 返回注册成功页面
                return render_to_response('success.html',
                                          {'username': username, 'operation': "注册"},
                                          context_instance=RequestContext(request))
    else:
        uf = UserForm()

    return render_to_response('register.html', {'uf': uf}, context_instance=RequestContext(request))

def logout(request):
    nm = request.COOKIES.get('username')
    response = render_to_response('Success.html',
                                  {'operation': "退出", 'username': nm},
                                  context_instance=RequestContext(request))
    #清理cookie里保存username
    response.delete_cookie('username')
    return response