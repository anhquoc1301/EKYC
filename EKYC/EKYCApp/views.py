from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect

from .forms import UserForm
from .models import Deal, User, InputCoin, OutputCoin, BetDeal
import random
from django.views import View
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
import schedule
import time
import requests
import os
from django.conf import settings
from django.core.mail import send_mail
from .decorators import admin_only, verify_only
# from .check import checkSum
# Create your views here.


def send_mail_after_registration(email):
    subject = 'Tài khoản của bạn cần xác thực'
    host = settings.HOST
    message = f'Nhấn vào đường link này để xác thực: https://{host}/verify_mail/{email}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list, fail_silently=True)

# def test(request, pk):
#     profile_obj = User.objects.filter(email=pk).first()
#     if profile_obj:
#         if profile_obj.is_active_mail:
#             messages.success(request, 'Bạn đã xác thực tài khoản này rồi')
#             return redirect('')
#         profile_obj.is_active_mail = True
#         profile_obj.save()
#         messages.success(request, 'Tài khoản của bạn đã xác thực.')
#         return redirect('app1:login')
#     else:
#         return redirect('app1:login')

def verify_mail(request, pk):
    profile_obj = User.objects.filter(email=pk).first()
    if profile_obj:
        if profile_obj.is_active_mail:
            messages.success(request, 'Bạn đã xác thực tài khoản này rồi')
            return redirect('')
        profile_obj.is_active_mail = True
        profile_obj.save()
        messages.success(request, 'Tài khoản của bạn đã xác thực.')
        return redirect('app1:login')
    else:
        return redirect('app1:login')


class register(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'dangky/dangky.html')
        else:
            return redirect('app1:home')

    def post(self, request):
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            email = request.POST.get('email')
            phone = None
            if request.POST.get('phone'):
                phone = int(request.POST.get('phone'))
            code = random.randint(100000000, 999999999)
            while User.objects.filter(code=code).exists():
                code = random.randint(100000000, 999999999)
            if User.objects.filter(username=username).exists():
                messages.warning(request, 'Tên đăng nhập trùng!')
                return redirect('app1:register')
            if password == password2:
                ur = User.objects.create_user(
                    username=username, password=password, email=email, phone=phone)
                ur.code = code
                ur.coin = 10000000
                ur.total_deal = 0
                ur.bonuscoin = 0
                ur.save()
                send_mail_after_registration(email=email)
                messages.success(
                    request, 'Đăng ký thành công!Vui long xac thuc email')
                return redirect('app1:login')
            else:
                messages.warning(request, 'Mật khẩu không khớp!')
                return redirect('app1:register')


class login(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'dangnhap/dangnhap.html')
        else:
            return redirect('app1:home')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if user is not None:
                if user.is_active_mail == True:
                    my_user = authenticate(
                        request, username=username, password=password)
                    if my_user is None:
                        messages.error(request, 'Sai tài khoản hoặc mật khẩu!')
                        return redirect('app1:login')
                    else:
                        auth.login(request, my_user)
                        return redirect('app1:dashboard')
                else:
                    messages.error(request, 'Tai khoan chua duoc xac thuc!')
                    return redirect('app1:login')
            else:
                messages.error(request, 'User khong ton tai!')
                return redirect('app1:login')
        except:
            messages.error(request, 'User khong ton tai!')
            return redirect('app1:login')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('app1:login')

@login_required
@verify_only
def inputcoin(request):
    if request.method == "POST":
        try:
            prime = int(request.POST.get('prime'))
            ip = InputCoin.objects.create(coin_deal=prime, user=request.user.code)
            ur = User.objects.get(id=request.user.id)
            ur.coin = ur.coin+prime
            ur.save()
            ip.save()
            messages.success(request, 'Nạp tiền thành công!')
            return redirect('app1:inputcoin')
        except:
            messages.error(request, 'Nạp tiền that bai!')
            return redirect('app1:inputcoin')
    return render(request, 'naptien.html')

@login_required
@verify_only
def outputcoin(request):
    if request.method == "POST":
        try:
            prime = int(request.POST.get('prime'))
            ur = User.objects.get(id=request.user.id)
            if ur.coin >= prime:
                ur.coin -= prime
                ur.save()
                ip = OutputCoin.objects.create(
                    coin_deal=prime, user=request.user.code)
                ip.save()
                messages.success(request, 'Rút tiền thành công!')
                return redirect('app1:outputcoin')
            else:
                messages.warning(request, 'Rút tiền thất bại!')
                return redirect('app1:outputcoin')
        except:
            messages.warning(request, 'Co loi xay ra, vui long thu lai!')
            return redirect('app1:outputcoin')
    return render(request, 'ruttien.html')

@login_required
@verify_only
def deal(request):
    if request.method == "POST":
        try:
            prime = int(request.POST.get('prime'))
            unto = int(request.POST.get('unto'))
            ur = User.objects.get(id=request.user.id)
            to = User.objects.get(code=unto)
            if ur.coin >= prime:
                ur.coin -= prime
                to.coin += prime
                to.save()
                ur.save()
                ip = Deal.objects.create(
                    coin_deal=prime, unto=unto, user=request.user.code)
                ip.save()
                messages.success(request, 'Chuyển khoản thành công!')
                return redirect('app1:deal')
            else:
                messages.warning(request, 'Chuyển khoản thất bại!')
                return redirect('app1:deal')
        except:
            messages.warning(request, 'Co loi xay ra, vui long thu lai!')
            return redirect('app1:deal')
    return render(request, 'chuyentien.html')


@login_required
def editpassword(request):
    ur = User.objects.get(id=request.user.id)
    if request.method == "POST":
        if ur.check_password(request.POST['password']):
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 == password2:
                ur.set_password(password2)
                ur.save()
                messages.success(request, 'Đổi mật khẩu thành công!')
                ur2 = authenticate(username=ur.username, password=password2)
                auth.login(request, ur2)
                return redirect('app1:home')
            else:
                messages.warning('Mật khẩu không khớp!')
                return redirect('app1:editpassword')
        else:
            messages.error(request, 'Nhap sai mat khau')
    # return render(request, 'editpassword.html')


@login_required
def viewcoin(request):
    ur = User.objects.get(id=request.user.id)
    return render(request, 'viewcoin.html', {'form': ur})


def checkSum(code):
    sum = 0
    a = []
    ur = User.objects.all()
    for i in ur:
        if i.referrer_temporary == code:
            a.append(i.code)
    for i in a:
        for j in ur:
            if i == j.code:
                sum += j.total_deal+checkSum(i)
    return sum


def autocheck():
    ur = User.objects.all()
    for i in ur:
        k = 0
        total = checkSum(i.code)
        for j in ur:
            if j.referrer_temporary == i.code and j.total_deal >= 500:
                k += 1
        if i.level < 1:
            if k >= 3 and i.total_deal >= 500 and total >= 20000:
                i.level = 1
                i.bonus = 0.7/100
                i.save()
                for j in ur:
                    if j.referrer == i.code and i.level >= j.level:
                        j.referrer_temporary = i.code
                        j.save()
        if i.level < 2:
            if k >= 5 and i.total_deal >= 1000 and total >= 100000:
                i.level = 2
                i.bonus = 0.8 / 100
                i.save()
                for j in ur:
                    if j.referrer == i.code and i.level >= j.level:
                        j.referrer_temporary = i.code
                        j.save()
        if i.level < 3:
            if k >= 10 and i.total_deal >= 5000 and total >= 500000:
                i.level = 3
                i.bonus = 0.9 / 100
                i.save()
                for j in ur:
                    if j.referrer == i.code and i.level >= j.level:
                        j.referrer_temporary = i.code
                        j.save()
        if i.level < 4:
            if k >= 15 and i.total_deal >= 10000 and total >= 3500000:
                i.level = 4
                i.bonus = 1 / 100
                i.save()
                for j in ur:
                    if j.referrer == i.code and i.level >= j.level:
                        j.referrer_temporary = i.code
                        j.save()
        if i.level < 5:
            h = 0
            for j in ur:
                if j.referrer_temporary == i.code and j.total_deal >= 1000:
                    h += 1
            if h >= 20 and i.total_deal >= 20000 and total >= 10000000:
                i.level = 5
                i.bonus = 1.2 / 100
                i.save()
                for j in ur:
                    if j.referrer == i.code and i.level >= j.level:
                        j.referrer_temporary = i.code
                        j.save()

    for i in ur:
        if i.referrer_temporary is not None:
            a = i.referrer_temporary
            dad = User.objects.get(code=a)
            if i.level <= dad.level:
                i.referrer_temporary = dad.code
            if i.level > dad.level:
                if dad.referrer_temporary is not None:
                    b = dad.referrer_temporary
                    k = 1
                    while k == 1:
                        dadn = User.objects.get(code=b)
                        if i.level > dadn.level:
                            if dadn.referrer_temporary is not None:
                                b = dadn.referrer_temporary
                            else:
                                i.referrer_temporary = None
                                k = 2
                        else:
                            i.referrer_temporary = dadn.code
                            k = 2

                else:
                    i.referrer_temporary = None

    for h in ur:
        h.bonuscoin = 0
        h.save()

def check():
    a = []
    ur = User.objects.all()
    for i in ur:
        a.append(i)
    a.reverse()
    for i in a:
        print(i.create_at)

@login_required
def historyoutput(request):
    ur = OutputCoin.objects.filter(user=request.user.code)
    context = {'form': ur}
    return render(request, 'history/historyoutput.html', context)


@login_required
def historyinput(request):
    ur = InputCoin.objects.filter(user=request.user.code)
    context = {'form': ur}
    return render(request, 'history/historyinput.html', context)


@login_required
def historydeal(request):
    ur = Deal.objects.filter(user=request.user.code)
    context = {'form': ur}
    return render(request, 'app.mail.html', context)


@login_required
def historybet(request):
    ur = BetDeal.objects.filter(user=request.user.code)
    context = {'form': ur}
    return render(request, 'history/historybet.html', context)


@login_required
def historyreceive(request):
    ur = Deal.objects.filter(unto=request.user.code)
    context = {'form': ur}
    return render(request, 'history/historyreceive.html', context)


@login_required
def listchild(request):
    if request.user.username == 'admin':
        return redirect('app1:onlyadmin')
    us = User.objects.get(code=request.user.code)
    b = float(int(us.bonuscoin*10)/10)
    ur = User.objects.all()
    total = checkSum(request.user.code)
    a = []
    for i in ur:
        if i.referrer_temporary == request.user.code:
            a.append(i)
    context = {'form': a, 'total': total, 'bonus': b, 'us': us}
    return render(request, 'home/home.html', context)


@login_required
def listf(request, pk):
    us = User.objects.get(code=request.user.code)
    b = float(int(us.bonuscoin*10)/10)
    ur = User.objects.all()
    total = checkSum(request.user.code)
    us = User.objects.get(code=pk)
    a = []
    for i in ur:
        if i.referrer_temporary == us.code:
            a.append(i)
    context = {'form': a, 'total': total, 'bonus': b}
    return render(request, 'viewf.html', context)


@login_required
def bet_view(request):
    if request.method == 'POST':
        prime = int(request.POST.get('prime'))
        ur = User.objects.get(id=request.user.id)
        if ur.coin >= prime:
            betdeal = BetDeal.objects.create(coin_deal=prime, user=ur.code)
            betdeal.save()
            ur.total_deal += int(prime)
            ur.coin = ur.coin-int(prime)
            ur.save()
            messages.success(request, 'Cược thành công!')
            return redirect('app1:bet_view')
        else:
            messages.warning(request, 'Cược thất bại!')
            return redirect('app1:bet_view')
    return render(request, 'bet/bet.html')


@login_required
@admin_only
def onlyadmin(request):
    try:
        ur = User.objects.all()
        total = 0
        bonus = 0
        lv0 = lv1 = lv2 = lv3 = lv4 = lv5 = 0
        for i in ur:
            total += i.total_deal
            bonus += i.bonuscoin
        bonus = float(int(bonus * 10) / 10)
        for i in ur:
            if i.level == 0:
                lv0 += 1
            if i.level == 1:
                lv1 += 1
            if i.level == 2:
                lv2 += 1
            if i.level == 3:
                lv3 += 1
            if i.level == 4:
                lv4 += 1
            if i.level == 5:
                lv5 += 1
        context = {'total': total, 'bonus': bonus, 'lv0': lv0,
                'lv1': lv1, 'lv2': lv2, 'lv3': lv3, 'lv4': lv4, 'lv5': lv5}
        return render(request, 'onlyadmin.html', context)
    except:
        return HttpResponse('Admin view!')


@login_required
def resetweek(request):
    ur = User.objects.all()
    if request.method == "POST":
        for i in ur:
            i.coin += i.bonuscoin
            i.total_deal = 0
            i.bonus = 0
            i.level = 0
            i.bonuscoin = 0
            i.referrer_temporary = i.referrer
            i.save()
        messages.success(request, 'Reset lại thành công')
        return redirect('app1:onlyadmin')
    return render(request, 'resetweek.html')

@login_required
def upload_card_id(request):
    if request.method == "POST":
        user=User.objects.get(id=request.user.id)
        card_id = request.FILES['card_id']
        if card_id:
            user.card_id=card_id
    
            baseUrl = "https://api.smartbot.vn"
            url_auth = f"{baseUrl}/auth"
            payload_auth = {"api_key": "ef3dd558-1cd0-4f32-ab2d-c0f6706de114"}
            headers_auth = {}
            response_auth = requests.request(
                "POST", url_auth, headers=headers_auth, data=payload_auth)
            response_auth=response_auth.json()
            access_token = response_auth['access_token']
            url=f"{baseUrl}/ocr/id"
            payload={}
            files=[
            ('frontImg',('resize_image_card.jpg',card_id,'image/jpeg')),
            ]
            headers={
            "Authorization":f"Bearer {access_token}"
            }
            response=requests.request("POST",url,headers=headers,data=payload,files=files)
            if response:
                response=response.json()
                user.card_number=response['data']['id_number']
                user.fullname=response['data']['name']
                print(response['data']['name'])
                user.birthday=response['data']['dob']
                user.address=response['data']['residence']
                user.save()
                return redirect('app1:app_user_detail')
            else:
                messages.error(request, 'Anh khong hop le, vui long chon anh khac')
    return render(request, 'app.user.html')

@login_required
def app_user_detail(request):
    user=User.objects.get(id=request.user.id)
    if user:
        context={'name': user.fullname, 'birthday': user.birthday, 'address': user.address, 'card_number': user.card_number}
    else:
        messages.error('user not exist')
    return render(request, 'app.user.detail.html', context)

@login_required
def verify(request):
    if request.method == "POST":
        user=User.objects.get(id=request.user.id)
        image_card = user.card_id
        image_live = request.FILES['image_live']
        baseUrl = "https://api.smartbot.vn"
        url_auth = f"{baseUrl}/auth"
        payload_auth = {"api_key": "ef3dd558-1cd0-4f32-ab2d-c0f6706de114"}
        headers_auth = {}
        response_auth = requests.request(
            "POST", url_auth, headers=headers_auth, data=payload_auth)
        response_auth=response_auth.json()
        access_token = response_auth['access_token']
        url_verify = f"{baseUrl}/cloudekyc/faceid/verification"
        payload_verify = {}
        files_verify = [
            ('image_card',(str(image_card.name) ,image_card,'image/jpeg')),
            ('image_live',(str(image_live.name) ,image_live,'image/jpeg')),
            ]
        headers_verify = {
            'Authorization': f'Bearer {access_token}'
        }
        response_verify = requests.request(
            "POST",url_verify, headers=headers_verify, data=payload_verify, files=files_verify)
        response_verify=response_verify.json()
        print(response_verify)
        if response_verify['verify_result'] == 1 or response_verify['verify_result'] == 2:
            user.is_verified=True
            user.save()
            messages.success(request, 'Verify thanh cong')
        return redirect('app1:verify_result')
    return render(request, 'app.mail.detail.html')

@login_required
def verify_result(request):
    user=User.objects.get(id=request.user.id)
    result=user.is_verified
    return render(request, 'result.html', {'result': result})

def test(request):
    return render(request, 'app.user.detail.html')
    
@login_required
def dashboard(request):
    user = User.objects.get(id=request.user.id)
    context={'is_verified': user.is_verified, 'fullname': user.fullname, 'coin': user.coin, 'code': user.code}
    return render(request, 'dashboard.html', context)

@login_required
def promotion(request):
    return render(request, 'app.calendar.html')

@login_required
def message(request):
    user=User.objects.get(id=request.user.id)
    context={
        'name': user.fullname,
        'card_number': user.code
    }
    return render(request, 'app.message.html', context)