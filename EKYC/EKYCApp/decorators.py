from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages

def admin_only(view_func):
    def function(request, *args, **kwargs):
        user=request.user.username
        if user=='admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("Chức năng này chỉ dành cho Admin!")
    return function

def verify_only(view_func):
    def function(request, *args, **kwargs):
        is_verified=request.user.is_verified
        if is_verified==True:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request,'ban can xac thuc tai khoan')
            return redirect('app1:dashboard')
    return function