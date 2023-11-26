from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from store.models import Order,Orderitem
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from xhtml2pdf.default import DEFAULT_FONT
from reportlab.lib.pagesizes import letter  # Import the desired page size
from reportlab.lib.units import cm  # Import units (e.g., cm for margins)



# ...START- FUNCTION OF ORDER PAGE ,IN THIS PAGE ORDER HISTORY DISPLAYED...
def index(request):
    '''FUNCTION OF ORDER PAGE ,IN THIS PAGE ORDER HISTORY DISPLAYED'''
    orders = Order.objects.filter(user=request.user)
    orders = reversed(orders)
    context = {'orders':orders}
    return render(request,'store/orders/index.html',context)
# ...END- FUNCTION OF ORDER PAGE ,IN THIS PAGE ORDER HISTORY DISPLAYED...




# ...START- FUNCTION OF DETAILES OF EACH ORDER...
def vieworder(request,t_no):
    '''DETAILES OF EACH ORDER'''
    order = Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
    orderitems = Orderitem.objects.filter(order=order).select_related('product')
    context = {
        'order':order,
        'orderitems':orderitems
        }
    return render(request,'store/orders/view.html',context)
# ...END- FUNCTION OF DETAILES OF EACH ORDER...




# ...START- FUNCTION OF INVOICE...
def invoice(request,t_no):
    '''INVOICE'''
    order = Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
    orderitems = Orderitem.objects.filter(order=order).select_related('product')
    context = {
        'order':order,
        'orderitems':orderitems
        }
    return render(request,'store/orders/invoice.html',context)
# ...END- FUNCTION OF INVOICE...




# ...START- FUNCTION OF GENERATION OF PDF...
def invoice_pdf(template_source, context_dict={}):
    template = get_template(template_source)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, encoding="utf-8", pagesize="A4", pagebreaks=False)
    if not pdf.err:
        response = HttpResponse(content_type="application/pdf")
        # response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        response.write(result.getvalue())
        return response
    return HttpResponse("PDF generation failed", content_type="text/plain")

# CONTEXT PASSING IN GENERATED PDF
def generate_pdf(request,t_no):
    '''GENERATION OF PDF'''
    # order = Order.objects.filter(user=request.user).first()
    order = Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
    orderitems = Orderitem.objects.filter(order=order)
    
    context = {
        'order': order,
        'orderitems': orderitems,
    }
    
    pdf = invoice_pdf("store/orders/invoice_pdf.html", context)
    return pdf
# ...START- FUNCTION OF GENERATION OF PDF...
    

        
        
        
        
                                                                                                                       