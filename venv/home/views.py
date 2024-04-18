from json.decoder import JSONDecoder
from django import template
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
import datetime
from .models import Contact, Seller, Cathome, Books, Review
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, CustomerForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.template import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, request
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#for_smtp
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template, render_to_string
from io import BytesIO
from django.http import HttpResponse
from xhtml2pdf import pisa
import os
from random import randint
import pdfkit
import datetime

#Search
from django.db.models import Q

#Rating
from django.urls import reverse


# Create your views here.
def index(request):
    category = request.GET.get('category')
    if category == None:
        books = Books.objects.all()
    else:
        books = Books.objects.filter(category__name=category)
    categories = Cathome.objects.all()

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']


    context = {'categories':categories, 'books':books, 'cartItems':cartItems}

    return render(request, 'index.html', context)

def about(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status
    return render(request, 'about.html', {'cartItems': cartItems})      

@login_required(login_url='/sign_in')
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        anyfile = request.FILES.get('anyfile')
        contact = Contact(name=name, email=email, phone=phone, desc=desc, anyfile=anyfile, date=datetime.datetime.today())
        contact.save()
        success(request)

    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    return render(request, 'contact.html', {'cartItems': cartItems})

def logoutUser(request):
    logout(request)
    return redirect('home')

def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR Password is incorrect')

    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            users = get_user_model()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data['email']
            p = Customer(user=users.objects.get(username=username), name=username,email=email, date_created=datetime.datetime.now())
            p.save()
            messages.success(request, 'Account was created for ' + username)
            return redirect('sign_in')

    context = {'form': form}

    return render(request, 'sign_in.html', context)

def viewBook(request, pk):
    book = Books.objects.get(id=pk)

    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    #Review
    if request.method == "POST":
        product = Books.objects.get(id=pk)
        name = request.user
        email = request.POST.get('email')
        desc = request.POST.get('desc')

        review = Review.objects.create(
            product=product,
            name=request.user,
            email=email,
            desc=desc,
            date=datetime.datetime.today(),
            time=datetime.datetime.today()
        )
        
        return redirect('book', pk=pk)

    reviews = Review.objects.filter(product=book)
    page = request.GET.get('page', 1)

    paginator = Paginator(reviews, 3)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'book.html', {"book":book,"users":users, "reviews":reviews, 'cartItems':cartItems})

@login_required(login_url='/sign_in')
def liked_video(request, id):
    user=request.user
    Like=False
    if request.method=="POST":
        book_id=request.POST['book_id']
        get_book=get_object_or_404(Books, id=book_id)
        if user in get_book.likes.all():
            get_book.likes.remove(user)
            Like=False
        else:
            get_book.likes.add(user)
            Like=True
        data={
            "liked":Like,
            "likes_count":get_book.likes.all().count()
        }
        return JsonResponse(data, safe=False)
    return redirect(reverse("book", args=[str(id)]))

@login_required(login_url='/sign_in')
def dislike_video(request, id):
    user=request.user
    Dislikes=False
    if request.method == "POST":
        book_id=request.POST['book_id']
        print("printing ajax id", book_id)
        watch=get_object_or_404(Books, id=book_id)
        if user in watch.dislikes.all():
            watch.dislikes.remove(user)
            Dislikes=False
        else:
            if user in watch.likes.all():
                watch.likes.remove(user)
            watch.dislikes.add(user)
            watch.save()
            Dislikes=True
        data={
            "disliked":Dislikes,
            'dislike_count':watch.dislikes.all().count()
        }
        return JsonResponse(data, safe=False)
    return redirect(reverse("book", args=[str(id)]))

#Changes made by MANISH
@login_required(login_url='/sign_in')
def sell(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    categories = Cathome.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        author = request.POST.get('author')
        phone = request.POST.get('phone')
        if request.POST.get('category'):
            savevalue=Seller()
            savevalue.category=request.POST.get('category')
            cate=savevalue.category
        
        category_new = request.POST.get('category_new')
        price = request.POST.get('price')
        desc = request.POST.get('desc')
        img = request.FILES.get('img')
        pdf = request.FILES.get('pdf')

        if cate != 'none':
            category = Cathome.objects.get(id=cate)
        elif category_new != '':
            category, created = Cathome.objects.get_or_create(name=category_new)
        else:
            category = None

        book = Books.objects.create(
            category=category,
            description=desc,
            image=img,
            name=name,
            price=price,
            pdf=pdf,
            author=author,
            date=datetime.datetime.today()
        )

        seller = Seller(name=name, author=author, phone=phone, category=cate, price=price, desc=desc, img=img, date=datetime.datetime.today())
        seller.save()

        return redirect('home')

    context = {'categories':categories, 'cartItems':cartItems}
    return render(request, 'sell.html', context)


@login_required(login_url='/sign_in')
def cart(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'cart.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    product = Books.objects.get(id=productId)
    print(product)
    order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    print(order)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    print(orderItem)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    print(orderItem.quantity)

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item is added", safe=False)

@login_required(login_url='/sign_in')
def checkout(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'checkout.html', context)

def proccessOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    order, created = Order.objects.get_or_create(customer=request.user, complete=False)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        
        ShippingAddress.objects.create(
            customer=request.user,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            country=data['shipping']['country'],
        )

    if order.shipping == True:
        z = str(data['shipping']['zipcode'])
        statecode = z[-2:]
        invoiceno = randint(1000000000, 9999999999)
        m = str(randint(1000, 9999))
        n = str(randint(1000, 9999))
        o = str(randint(1000, 9999))
        billingid = m + "-"+ n +"-" + o
        success(request, order, data, total, statecode, invoiceno, billingid)                     

    return JsonResponse('Payment Complete', safe=False)

def privacypolicy(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status
    return render(request, 'privacypolicy.html', {'cartItems':cartItems})

def terms(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status
    return render(request, 'terms.html', {'cartItems':cartItems})

def disclaimer(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status
    return render(request, 'disclaimer.html', {'cartItems':cartItems})

def misc(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    return render(request, 'misc.html', {'cartItems':cartItems})

def search(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    srh = request.GET.get('query')
    price_from = request.GET.get('price_from', 0)
    price_to = request.GET.get('price_to', 9999)
    sorting = request.GET.get('sorting', '-date')
    if not srh:
        srh=''
    books = Books.objects.filter(price__gte=price_from).filter(price__lte=price_to).filter(Q(name__icontains=srh) | Q(author__icontains=srh))

    context = {
        'books': books.order_by(sorting),
        'search':srh,
        'price_from': price_from,
        'price_to': price_to,
        'sorting': sorting,
        'cartItems':cartItems,
        }

    return render(request, 'search.html', context)

def success(request, order, data, total, statecode, invoiceno, billingid):
    orderItem = OrderItem.objects.filter(order=order)
    datetoday = datetime.date.today()
    template = get_template('email_temp.html').render({'name':request.user})
    data={
        'order': order,
        'transaction_id' : order.transaction_id,
        'total': total,
        'customer' :request.user,
        'address': data['shipping']['address'],
        'city': data['shipping']['city'],
        'state': data['shipping']['state'],
        'zipcode': data['shipping']['zipcode'],
        'country': data['shipping']['country'],
        'statecode': statecode,
        'invoiceno': invoiceno,
        'billingid': billingid,
        'datetoday': datetime.date.today(),
        'orderItem': orderItem,
    }
    html  = get_template('invoice.html').render(data)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    pdf = result.getvalue()
    filename = 'Invoice_' + str(invoiceno) + '.pdf'

    email = EmailMessage(
            'Thanks for purchasing books from Books Treasury!',
            template,
            settings.EMAIL_HOST_USER,
            [request.user.email],
            )
            
    email.content_subtype = "html"
    email.attach(filename, pdf, 'application/pdf')
    email.send(fail_silently=False)

    return JsonResponse('E-mail Sent', safe=False)

@login_required(login_url='/sign_in')
def orders(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    orders = Order.objects.filter(customer = request.user)
    orderItems = OrderItem.objects.filter(order__in=orders)

    total_orders = orders.count()
    delivered = orders.filter(complete='True').count()
    pending = orders.filter(complete='False').count()

    print('ORDERS:', orders)
    print(orderItems)

    context = {'orders':orders, 'orderItems':orderItems, 'total_orders':total_orders, 'delivered':delivered,'pending':pending, 'cartItems':cartItems}

    return render(request, 'orders.html', context)

def accountsetting(request):
    #for cart update status
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        item = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    #for cart update status

    form = CustomerForm(instance=request.user.customer)

    if request.method =='POST':
        form = CustomerForm(request.POST, request.FILES,  instance=request.user.customer)
        if form.is_valid():
            form.save()
    
    return render(request, 'account_setting.html',{'form':form, 'cartItems':cartItems})

#Assets for Crosscheck

def emailtemp(request):
    return render(request, 'email_temp.html')

def invoice(request):
    return render(request, 'invoice.html')

def dark(request):
    return render(request, 'darkmode.html', {'username':request.user})