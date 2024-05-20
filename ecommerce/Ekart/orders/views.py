from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from coupon.models import Coupon
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template.loader import get_template



def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        transaction_id = body['transID'],
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
           
           
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
       
        

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
def cancel_order(request,order_id):
    order = Order.objects.get(id = order_id, user=request.user )

    order.status = 'Cancelled'
    order.save()
    return redirect('my_orders')

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse


def cash_on_delivery(request):
    order_number = request.POST.get('order_number')
    
    try:
        order = get_object_or_404(Order, user=request.user, is_ordered=False, order_number=order_number)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    payment_method = "Cash On Delivery"
    amount_paid = order.order_total

    if order.coupon:
        amount_paid -= order.coupon.discount_price

    payment_status = "NOT PAID"
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    payment = Payment.objects.create(
        user=request.user,
        payment_method=payment_method,
        amount_paid=amount_paid,
        status=payment_status
    )

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
        )
        for variation in item.variations.all():
            order_product.variations.add(variation)

        item.product.stock -= item.quantity
        item.product.save()

    CartItem.objects.filter(user=request.user).delete()

    mail_subject = 'Order Placed'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email

    try:
        send_mail = EmailMessage(mail_subject, message, to=[to_email])
        send_mail.send()
    except Exception as e:
        print("Email sending failed:", str(e))

    ordered_products = OrderProduct.objects.filter(order=order)

    subtotal = sum(op.product_price * op.quantity for op in ordered_products)
    grand_total = order.order_total

    if order.coupon:
        grand_total -= order.coupon.discount_price

    context = {
        'order': order,
        #'ordered_products': ordered_products,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'transID': payment.transaction_id,
        'payment': payment,
        'subtotal': subtotal,
        'grand_total': grand_total
    }

    return render(request, 'orders/cod_complete.html', context)

from io import BytesIO
from xhtml2pdf import pisa


def render_to_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    response = BytesIO()
    
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")),
        response,
        pagesize='letter'  # Set the page size to letter (8.5 x 11 inches)
    )
    
    if not pdf.err: #type:ignore
        response.seek(0)
        return response
    return None


def cod_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    discount = 0
    if order.coupon:
        discount  = order.coupon.discount_price
    ordered_products = OrderProduct.objects.filter(order_id=order.id) #type:ignore
    subtotal = 0
   
    for item in ordered_products:
        subtotal += item.product_price * item.quantity

    context = {
        'order': order,
        'order_number': order.order_number,
        'transID': "N.A",
        'ordered_products': ordered_products,
        'subtotal': subtotal,
        'status': "NOT COMPLETED",
        'discount': discount,
        'grand_total': order.order_total -discount
    }

    template_path = 'orders/invoice.html'  # Replace with the path to your HTML template
    pdf_response = render_to_pdf(template_path, context)

    if pdf_response:
        response = HttpResponse(pdf_response.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{order.order_number}.pdf'
        return response

    # Handle the case where PDF generation fails
    return HttpResponse('PDF generation failed', status=500)


def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    discount = 0
    if order.coupon:
        discount  = order.coupon.discount_price
    ordered_products = OrderProduct.objects.filter(order_id=order.id) #type:ignore
    payment = Payment.objects.get(transaction_id=order.payment.transaction_id) #type:ignore
    subtotal = 0
   
    for item in ordered_products:
        subtotal += item.product_price * item.quantity

    context = {
        'order': order,
        'order_number': order.order_number,
        'transID': payment.transaction_id,
        'ordered_products': ordered_products,
        'subtotal': subtotal,
        'status': payment.status,
        'discount': discount,
        'grand_total': order.order_total
    }

    template_path = 'orders/invoice.html'  # Replace with the path to your HTML template
    pdf_response = render_to_pdf(template_path, context)

    if pdf_response:
        response = HttpResponse(pdf_response.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{order.order_number}.pdf'
        return response