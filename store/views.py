from django.shortcuts import render,redirect, get_object_or_404 
from django.http import HttpResponse 
from .models.product import Product 
from .models.category import Category 
from .models.cart import Cart
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.urls import reverse
import jwt
from django.contrib.auth.models import User





# Create your views here.


def mysignup(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')
        username = email.split('@')[0]


        if User.objects.filter(email=email).exists():  # Agar email already exist karti hai  
                return render(request, 'signup.html', {'mes': 'User already exists'})  # Error message dikhao  


        user = User()
        user.username = username
        user.set_password(password)
        user.is_active = True # Important for activation

        

        try:
            user.save()

            # ✅ Activation Email Send Karna  
            enc = jwt.encode(payload={'encid': str(user.pk)}, key='secret', algorithm='HS256')  # JWT token generate kiya  
            link = request.scheme + '://' + request.META['HTTP_HOST'] + '/activate/' + str(enc) + '/'  # Activation link banaya  

            # ✅ Email bhejne ka code  
            em = EmailMessage('Activation link', 'Thanks for registration!\n Click here to activate your account' + link, 'areebsd06@gmail.com', [email])  
            em.send()  # Email bhej diya  

            return render(request, 'signup.html', {'mes': 'User created successfully. Check your email for activation link.'})  # Success message dikhaya  

        except Exception as e:  # Agar koi error aaye toh exception handle karo  
            return render(request, 'signup.html', {'mes': 'Error: ' + str(e)})  # Error message dikhao  

        

    return render(request, "signup.html")




def mylogin(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')
        username = email.split("@")[0]  # assuming you saved username like this during signup
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Django’s built-in login
            request.session['username'] = username  # ✅ Save email in session
            return redirect('home')  # Replace 'home' with the name of your homepage url pattern
        else:
            return render(request, 'login.html', {'mes': 'Wrong credentials'})
    
    return render(request, 'login.html')


from django.db.models import Q

@login_required(login_url='login')
def home(request):
    category = Category.all_categories()
    
    # Get user name
    name = ""
    if request.user.is_authenticated:
        name = request.user.first_name or request.user.username
    
    # Get search query and category filter
    search_query = request.GET.get('search', '').strip()
    categoryID = request.GET.get('category')
    
    # Start with all products
    products = Product.objects.all()
    
    # Apply search filter - searches in name, description, and category
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Apply category filter
    if categoryID:
        products = products.filter(category_id=categoryID)
    
    data = {
        'product': products,
        'category': category,
        'name': name,
        'user': request.user,
        'search_query': search_query,
        'selected_category': categoryID
    }
    
    return render(request, 'home.html', data)





def activate(request, id):
    dec = jwt.decode(id, key='secret', algorithms=['HS256'])  # JWT token decode kiya  
    us = User.objects.get(pk=int(dec['encid']))  # Database me user ko find kiya jo is ID se match kare  
    us.is_active = True  # User ko active kar diya  
    us.save()  # Database me save kar diya  
    return redirect(reverse('login'))  # Login page par redirect kar diya 



def mylogout(request):
    if request.session.has_key('username'):
        del request.session['username']
    return redirect('login')



def productdetail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    name = ""
    if request.user.is_authenticated:
        name = request.user.first_name or request.user.username

    username = request.session.get('username')
    in_cart = False
    if username:
        in_cart = Cart.objects.filter(username=username, product=product).exists()

    context = {
        'product': product,
        'in_cart': in_cart,
        'name': name,
    }
    return render(request, 'productdetail.html', context)



def add_to_cart(request):
    if request.method == "POST":
        username = request.session.get('username')
        if not username:
            return redirect('login')

        product_id = request.POST.get('prod_id')
        product = get_object_or_404(Product, id=product_id)

        existing = Cart.objects.filter(username=username, product=product).first()
        if existing:
            existing.quantity += 1
            existing.save()
        else:
            Cart.objects.create(
                username=username,
                product=product,
                # Remove these lines:
                # image=product.image,
                price=product.price,
                quantity=1
            )

        return redirect('product-detail', pk=product.id)
    else:
        return redirect('home')

    

#go to cart wala

@login_required
def view_cart(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    cart_items = Cart.objects.filter(username=username)

    # Add subtotal to each cart item manually
    for item in cart_items:
        item.subtotal = item.price * item.quantity

    total_price = sum(item.subtotal for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })




from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product

@require_POST
def increase_quantity(request):
    username = request.session.get('username')
    product_id = request.POST.get('product_id')
    cart_item = Cart.objects.filter(username=username, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@require_POST
def decrease_quantity(request):
    username = request.session.get('username')
    product_id = request.POST.get('product_id')
    cart_item = Cart.objects.filter(username=username, product_id=product_id).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('view_cart')



@require_POST
def remove_from_cart(request):
    username = request.session.get('username')
    product_id = request.POST.get('product_id')
    Cart.objects.filter(username=username, product_id=product_id).delete()

    return redirect('view_cart')



# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import Cart, Order, OrderItem  # Adjust imports based on your models
import json

def process_checkout(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        gmail = request.POST.get('gmail')
        address = request.POST.get('address')
        payment_method = request.POST.get('paymentMethod', 'cod')
        
        # Validate required fields
        if not all([name, gmail, address]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('view_cart')
        
        # Get user's cart items
        try:
            # Assuming you have a Cart model with user session
            username = request.session.get('username')
            if not username:
                messages.error(request, 'Please login to proceed with checkout.')
                return redirect('login')
            
            # Get cart items for the user
            cart_items = Cart.objects.filter(username=username)
            
            if not cart_items.exists():
                messages.error(request, 'Your cart is empty.')
                return redirect('view_cart')
            
            # Calculate total price
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            
            # Create order record (you'll need to create Order model)
            order = Order.objects.create(
                username=username,
                customer_name=name,
                customer_email=gmail,
                customer_address=address,
                payment_method=payment_method,
                total_amount=total_price,
                status='pending'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear the cart after successful order
            cart_items.delete()
            
            # Send confirmation email (optional)
            try:
                send_confirmation_email(name, gmail, order)
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            # Success message
            messages.success(request, f'Order placed successfully! Order ID: {order.id}')
            
            # Redirect to order confirmation page
            return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'An error occurred while processing your order: {str(e)}')
            return redirect('view_cart')
    
    # If GET request, redirect to cart
    return redirect('view_cart')

def send_confirmation_email(name, email, order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - Zaidi Mart (Order #{order.id})'
    message = f"""
    Dear {name},
    
    Thank you for your order! Here are your order details:
    
    Order ID: {order.id}
    Total Amount: Rs {order.total_amount}
    Payment Method: {order.get_payment_method_display()}
    Delivery Address: {order.customer_address}
    
    We will process your order and deliver it to your address soon.
    
    Thank you for shopping with Zaidi Mart!
    
    Best regards,
    Zaidi Mart Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def order_confirmation(request, order_id):
    """Display order confirmation page"""
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'order_confirmation.html', context)
    
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('view_cart')
    
