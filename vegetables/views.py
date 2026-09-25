from csv import excel
from http.client import responses
from django.http import HttpRequest, HttpResponse
from django.template.context_processors import request
from django.shortcuts import render, redirect,get_object_or_404
from. models import *
from vegetablestore.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db.models import Sum




@never_cache
def index(request):
    if 'sid' not in request.session:
        return redirect('/login/')
    pro = vegetables.objects.all()
    return render(request, 'index.html',{'pro':pro})

def account(request):
    if request.method == "POST":
        if useracc.objects.filter(name=request.POST['name']).exists():
            return HttpResponse('username already exists')
        else:
            data = useracc(name=request.POST.get('name'),
                           age=request.POST.get('age'),
                           place=request.POST.get('place'),
                           phone=request.POST.get('phone'),
                           email=request.POST.get('email'),
                           password=request.POST.get('password'))
            data.save()
    return render(request, 'useracc.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def delabout(request):
    return render(request, 'delaboutus.html')

def product(request):
    veg = vegetables.objects.all()
    return render(request, 'products.html', {'veg': veg})

def login(request):
    if request.method == "POST":
        user = request.POST.get('username')
        pas = request.POST.get('password')

        try:
            st = useracc.objects.get(name=user)

            if pas == st.password:
                request.session['sid'] = st.name
                request.session.modified = True
                return redirect('index')
            else:
                return HttpResponse('incorrect password')

        except useracc.DoesNotExist:
            return HttpResponse('user does not exist')

    return render(request, 'login.html')
            
def home(request):
    return render(request, 'home.html')

def carts(request,id):
    username = request.session.get('sid')
    if not username:
        return redirect('/login/')  # redirect if not logged in

    user = get_object_or_404(useracc, name=username)
    product = get_object_or_404(vegetables, id=id)

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    cart_item.quantity = (cart_item.quantity or 0) + 1
    cart_item.save()

    return redirect('cart_page')

def cart_page(request):
    username = request.session.get('sid')
    if not username:
        return redirect('/login/')  # if not logged in

    user = get_object_or_404(useracc, name=username)

    # get all items in that user's cart
    cart_items = Cart.objects.filter(user=user)

    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    price = 0
    for mult in cart_items:
        price += mult.product.price * mult.quantity

    return render(request, 'cart.html', {'cart_items': cart_items, 'price': price})

def dele_item(request,id):
    item = get_object_or_404(Cart, id=id)
    item.delete()
    messages.success(request, "Item removed from cart successfully!")
    return redirect('cart_page')

def payments(request):
    total_price = request.GET.get('total', 0)
    username = request.session.get('sid')
    if not username:
        return redirect('/login/')
    user = get_object_or_404(useracc, name=username)

    if request.method == "POST":
        data = Payment(user=user,
                       name=user.name,
                       email=user.email,
                       address=user.place,
                       payment=request.POST.get('payment_method'),
                       totalprice=request.POST.get('total_amount'),)
        data.save()
        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            vdata=PaidItem(payment=data,
                           product=item.product,
                           quantity=item.quantity,
                           product_name=item.product.name,  # Store product name
                           product_price=item.product.price,  # Store product price
                           product_image=item.product.image
                           )
            vdata.save()
        subject = 'payment sucess'
        message =(
            f'Dear {data.name}\n\n\n'
            f'Your order successfully done\n'
            f'Your total price is ${data.totalprice}\n'
        )
        send = [data.email]
        from_email = EMAIL_HOST_USER
        send_mail(subject, message, from_email, send)

        return redirect('order_history')

    return render(request, 'payment.html',{'total_price': total_price,'user': user})

def order_history(request):
    username = request.session.get('sid')
    user = get_object_or_404(useracc, name=username)

    payments = Payment.objects.filter(user=user).prefetch_related('items__product').order_by('-id')

    return render(request, 'orderhistory.html', {'payments': payments })

def userlogout(request):
    request.session.flush()
    return redirect('/login/')

def dellogout(request):
    request.session.flush()
    return redirect('/dellogin/')

def delveracc(request):
    if request.method == "POST":
        if Delivery.objects.filter(name=request.POST['name']).exists():
            return HttpResponse('username already exists')
        else:
            data = Delivery(name=request.POST.get('name'),
                            age=request.POST.get('age'),
                            place=request.POST.get('place'),
                            phone=request.POST.get('phone'),
                            email=request.POST.get('email'),
                            password=request.POST.get('password'))
            data.save()
    return render(request,'deliveracc.html')

def dellogin(request):
    if request.method == "POST":
        user = request.POST.get("username")
        passw = request.POST.get("password")
        try:
            st = Delivery.objects.get(name=user)
            if passw == st.password:
                request.session['did'] = st.id
                request.session['dname'] = st.name
                return redirect('delindex')
            else:
                return HttpResponse('password does not exist')
        except Delivery.DoesNotExist:
            return HttpResponse('username does not exist')
    return render(request,'delvlogin.html')

def deliveryindex(request):
    return render(request,'deliveryindex.html')

def delorder(request):
    payments = Payment.objects.select_related('user').prefetch_related('items__product')
    return render(request, 'delorder.html', {'payments': payments})

def delorderhistory(request,id):
    deliver_id = request.session.get('did')
    if not deliver_id:
        return redirect('/dellogin/')

    order = Payment.objects.get(id=id)
    if order.deliver is None:
        order.deliver_id = deliver_id
        order.save()

    return redirect('delorder')

def delorderview(request):
    deliver_id = request.session.get('did')
    if not deliver_id:
        return redirect('/dellogin/')
    payments = Payment.objects.filter(deliver_id=deliver_id).select_related('user').prefetch_related('items__product').order_by('-id')

    return render(request, 'deliveryorders.html', {'payments': payments})

def oderproduct(request,id):
    deliver_id = request.session.get('did')
    if not deliver_id:
        return redirect('/dellogin/')
    order = Payment.objects.select_related('user').prefetch_related('items__product').get(id=id, deliver_id=deliver_id)
    return render(request, 'orderproduct.html', {'order': order})

def mark_out(request, id):
    if request.method == "POST":
        payment = get_object_or_404(Payment, id=id)
        payment.status = "Out for Delivery"
        payment.save()
    return redirect('order')

def mark_delivered(request, id):
    if request.method == "POST":
        payment = get_object_or_404(Payment, id=id)
        payment.status = "Delivered"
        payment.save()
    return redirect('order')

def cancelled(request, id):
    if request.method == "POST":
        payment = get_object_or_404(Payment, id=id)
        payment.status = "Cancelled"
        payment.save()
        return redirect('order_history')

def userupdate(request):
    username = request.session.get('sid')
    if not username:
        return redirect('/login/')

    user = get_object_or_404(useracc, name=username)

    if request.method == "POST":
        new_name = request.POST.get('name')

        if useracc.objects.filter(name=new_name).exclude(id=user.id).exists():
            return HttpResponse('Username already exists')

        user.name = new_name
        user.age = request.POST.get('age')
        user.place = request.POST.get('place')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.password = request.POST.get('password')
        user.save()

        request.session['sid'] = new_name

        return redirect('/uprofile/?success=true')
    return render(request, 'userprofile.html', {'data': user})

def userdelete(request):
    username = request.session.get('sid')
    if not username:
        return redirect('/login/')
    user = get_object_or_404(useracc,name=username)
    user.delete()
    request.session.flush()
    return redirect('home')

def deliveryupdate(request):
    username = request.session.get('dname')
    if not username:
        return redirect('/dellogin/')

    user = get_object_or_404(Delivery,name=username)

    if request.method == "POST":
        newname = request.POST.get('name')

        if Delivery.objects.filter(name=newname).exclude(id=user.id).exists():
            return HttpResponse('Username already exists')

        user.name = newname
        user.age = request.POST.get('age')
        user.place = request.POST.get('place')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.password = request.POST.get('password')
        user.save()

        request.session['dname'] = newname

        return redirect('/delprofile/?success=true')
    return render(request, 'deliveryprofile.html', {'data': user})

def deliverydelete(request):
    username = request.session.get('dname')
    if not username:
        return redirect('/dellogin/')
    user = get_object_or_404(Delivery,name=username)
    user.delete()
    request.session.flush()
    return redirect('home')

def userfeedback(request):
    username = request.session.get('sid')
    if not username:
        return redirect('/login/')
    user = get_object_or_404(useracc, name=username)
    if request.method == "POST":
        data = feedback(user=user,
                        message=request.POST.get('message'))
        data.save()
        messages.success(request, "✅ Feedback submitted successfully!")
        return redirect('feedback')
    feed = feedback.objects.filter(user=user).order_by('-id')
    return render(request, 'userfeedback.html', {'user': user, 'feed': feed})

def admin(request):
    username = request.session.get('anameid')
    if not username:
        return redirect('/adminlogin/')
    user = get_object_or_404(admins,name=username)
    use = useracc.objects.count()
    total = Payment.objects.exclude(status='Cancelled').aggregate(total=Sum('totalprice'))['total']
    pay = Payment.objects.count()
    can = Payment.objects.filter(status='Cancelled').count()
    veg = vegetables.objects.count()
    dele = Delivery.objects.count()
    return render(request, 'admin.html',{'user': user, 'use': use, 'total': total, 'pay': pay, 'veg':veg, 'dele': dele,'can':can})

def adminpro(request):
    veg = vegetables.objects.all()
    if request.method == "POST":
        data = vegetables(name=request.POST.get('pname'),
                          image=request.FILES.get('pimage'),
                          price=request.POST.get('pprice'), )
        data.save()
        return redirect('adminpro')
    return render(request, 'adminproduct.html', {'veg': veg,})

def delproduct(request,id):
    pro = get_object_or_404(vegetables,id=id)
    pro.delete()
    return redirect('adminpro')

def editproduct(request,id):
    pro = vegetables.objects.get(id=id)
    if request.method == "POST":
        pro.name=request.POST.get('pname')
        if request.FILES.get('pimage'):
            pro.image = request.FILES['pimage']

        pro.price=request.POST.get('pprice')
        pro.save()
        return redirect('adminpro')
    return render(request, 'editproduct.html', {'pro': pro})

def adminuser(request):
    user = useracc.objects.all().order_by('-id')
    return render(request, 'adminuser.html', {'user': user})

def admindelivery(request):
    dell = Delivery.objects.all().order_by('-id')
    return render(request, 'admindelivery.html', {'dell': dell})

def adminfeedback(request):
    feed = feedback.objects.all().order_by('-id')
    return render(request, 'adminfeedback.html', {'feed': feed})

def adminorders(request):
    payments = Payment.objects.prefetch_related('items').all()
    return render(request, "adminorders.html", {"payments": payments})

def adminlogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            st=admins.objects.get(name=username)
            if st.password == password:
                request.session['aid'] = st.id
                request.session['anameid'] = st.name
                return redirect('admins')
            else:
                return HttpResponse('password does not exist')
        except admins.DoesNotExist:
            return HttpResponse('username does not exist')
    return render(request, 'adminlogin.html')



