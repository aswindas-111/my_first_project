from django.contrib import admin
from . models import *
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from rangefilter.filter import DateRangeFilter
from django.utils.safestring import mark_safe

# REPORT LAB LIBRARIES FOR GENERATING PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import PageTemplate, BaseDocTemplate, Frame, Table, Paragraph
from reportlab.platypus.tables import TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Sum
from django.db.models.functions import Coalesce
# FOR EXCEL REPORT
import xlsxwriter

#  FOR IMPORT/EXPORT FUNCTIONALITY
from import_export.admin import ImportExportModelAdmin


'''FUNCTION OF GENERATING PDF IN ADMIN SIDE'''
def generate_pdf(modeladmin, request, queryset, fields_to_include):
    model_name = modeladmin.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'

    # Creation of landscape A4-sized PDF document
    doc = BaseDocTemplate(response, pagesize=landscape(letter))

    # Creation of PageTemplate with a single Frame
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
    template = PageTemplate(frames=[frame])

    # Adding the PageTemplate to the document
    doc.addPageTemplates([template])

    elements = []
    
    title_style = getSampleStyleSheet()['Title']
    title =Paragraph("Report", style=title_style)
    elements.append(title)

    data = [['S.No'] + [modeladmin.model._meta.get_field(field_name).verbose_name for field_name in fields_to_include]]

    for index, obj in enumerate(queryset.order_by('id'), start=1):
        data_row = [str(index)] + [str(getattr(obj, field_name)) for field_name in fields_to_include]
        data.append(data_row)

    # Defining custom styles for table borders
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Background color for the header row
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Text color for the header row
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Border for all cells
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle vertical alignment for all cells
    ])

    table = Table(data)
    table.setStyle(table_style)

    elements.append(table)

    doc.build(elements)
    return response

generate_pdf.short_description = "Download selected items as PDF."


'''FUNCTION OF GENERATING EXCEL REPORT IN ADMIN SIDE'''
def download_excel(modeladmin, request, queryset):
    model_name = modeladmin.model.__name__
    response = HttpResponse(content_type='application/vnd.openxmlformats-officdocument.spreadsheettml.sheet')
    response['Content-Disposition'] = f'attachment; filename={model_name}.xlsx'

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    headers = [field.verbose_name for field in modeladmin.model._meta.fields]

    # Adding  header for the serial number column
    headers.insert(0, 'Serial Number')

    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    for row_num, obj in enumerate(queryset, 1):
        for col_num, field in enumerate(modeladmin.model._meta.fields):
            value = str(getattr(obj, field.name))
            worksheet.write(row_num, col_num + 1, value)  # +1 to skip the serial number column

        # Adding the serial number to the first column
        worksheet.write(row_num, 0, row_num)

    workbook.close()
    return response

download_excel.short_description = "Download selected items as Excel."



'''FUNCTION OF GENERATING SALES REPORT WITH TOP PRODUCTS AND TOTAL INCOME'''
def generate_sales_report_with_top_products(modeladmin, request, queryset):
    model_name = modeladmin.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}_sales_report.pdf'

    # Creation of landscape A4-sized PDF document
    doc = BaseDocTemplate(response, pagesize=landscape(letter))

    # Creation of PageTemplate with a single Frame
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
    template = PageTemplate(frames=[frame])

    # Adding the PageTemplate to the document
    doc.addPageTemplates([template])

    elements = []

    title_style = getSampleStyleSheet()['Title']
    title = Paragraph("Sales Report with Top Products", style=title_style)
    elements.append(title)

    # Retrieve the top-selling products
    top_selling_products = queryset.values('product__name').annotate(
        total_quantity_sold=Coalesce(Sum('quantity'), 0),
        total_amount_sold=ExpressionWrapper(
            F('price') * F('total_quantity_sold'),
            output_field=FloatField()  # Use FloatField for the total amount
        )
    ).order_by('-total_quantity_sold')[:10]  # Change 10 to the desired number of top products

    # Create a table to display the top-selling products
    top_products_data = [['Product', 'Quantity Sold', 'Total Amount']]
    for product in top_selling_products:
        top_products_data.append([
            product['product__name'],
            product['total_quantity_sold'],
            'RS {:.2f}'.format(product['total_amount_sold'])  # Format total amount as currency
        ])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Background color for the header row
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Text color for the header row
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Border for all cells
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle vertical alignment for all cells
    ])

    # Add column alignment for the "Total Amount" column
    table_style.add('ALIGN', (-1, 0), (-1, -1), 'RIGHT')

    top_products_table = Table(top_products_data)
    top_products_table.setStyle(table_style)

    elements.append(top_products_table)

    doc.build(elements)
    return response

generate_sales_report_with_top_products.short_description = "Download Sales Report with Top Products"




'''CATEGORY ADMIN'''
class CategoryAdmin(ImportExportModelAdmin):
    search_fields = Category.searchablefields
    
    def download_selected_pdf(self, request, queryset):
        # Defining the fields that want to include in the PDF
        fields_to_include = ['id', 'name']
        return generate_pdf(self, request, queryset, fields_to_include)
    
    actions = [download_selected_pdf, download_excel]
    
    
'''PRODUCTS ADMIN'''
class ProductAdmin(ImportExportModelAdmin):
    search_fields = Product.searchablefields
    list_display = ['name','language','author','category','view_image']
    list_per_page = 10
    list_filter = ['category','language','author','trending']
    
    def view_image(self, obj):
        if obj.product_image:
            return mark_safe('<a href="{}" target="_blank"><img src="{}" width="50" height="50" /></a>'.format(obj.product_image.url, obj.product_image.url))
        else:
            return "No Image"

    view_image.short_description = 'View Image'
    
    def download_selected_pdf(self, request, queryset):
        # FIELDS THAT INCLUDES IN PDF
        fields_to_include = ['id', 'name','language','author','quantity']
        return generate_pdf(self, request, queryset, fields_to_include)

    actions = [download_selected_pdf, download_excel]
    
'''ORDER ADMIN'''
orderstatuses = (
        ('Pending','Pending'),
        ('Out for shipping','Out for shipping'),
        ('Completed','Completed'),
    )

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['user','fname','lname','email','phone','address','city','state','country','pincode','total_price','payment_mode','payment_id','tracking_no']
    search_fields = Order.searchablefields
    list_display = ['fname','lname','email','state','country','payment_mode','get_status_display','created_at']
    list_per_page = 10
    list_filter = (
        ('created_at', DateRangeFilter),# Adding DateRangeFilter for 'created_at' field
        'fname',
        'lname',
        'state',
        'created_at'
    )
    # METHOD TO DISPLAY STATUS
    def get_status_display(self, obj):
        return dict(orderstatuses).get(obj.status, obj.status)
    get_status_display.short_description = 'Status'
    
    
    # METHOD TO DISPLAY FIELDS IN PDF 
    def download_selected_pdf(self, request, queryset):
        # Defining the fields that include in the PDF
        fields_to_include = ['id', 'fname','lname','phone','address','state','payment_mode','payment_id']
        return generate_pdf(self, request, queryset, fields_to_include)

    actions = [download_selected_pdf, download_excel]
    
    
'''ORDER ITEMS ADMIN'''
class OrderitemAdmin(admin.ModelAdmin):
    readonly_fields = ['order','product','price','quantity']
    list_display = ['order','product','price']
    list_per_page = 10
    list_filter = (
        ('order__created_at', DateRangeFilter),# Adding DateRangeFilter for 'created_at' field
        'order__fname',
        'order__lname',
        'order__state',
        'order__created_at'
    )
    search_fields = Orderitem.searchablefields
    
    
    def download_selected_pdf(self, request, queryset):
        # Defining the fields that include in the PDF
        fields_to_include = ['id', 'order','product','price','quantity']
        return generate_pdf(self, request, queryset, fields_to_include)

    actions = [download_selected_pdf, download_excel, generate_sales_report_with_top_products]

'''USERS [ FOR THIS, FIRST UNREGISTER THE INBUILT USER AND THEN CREATE AND REGISTER CUSTOMUSERADMIN ]'''
class CustomUserAdmin(UserAdmin):
    readonly_fields = ['username']
    list_per_page = 10
    
    
    def download_selected_pdf(self, request, queryset):
        # Define the fields you want to include in the PDF
        fields_to_include = ['id', 'username', 'first_name', 'last_name', 'email']
        return generate_pdf(self, request, queryset, fields_to_include)

    actions = [download_selected_pdf, download_excel]
    
'''AUTHOR ADMIN'''
class AuthorAdmin(ImportExportModelAdmin):
    pass

'''TESTIMONIAL/QUOTES'''
class TestimonialAdmin(ImportExportModelAdmin):
    pass


admin.site.unregister(User)

'''Register your models here.'''
admin.site.register(User, CustomUserAdmin)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Cart)
admin.site.register(Order,OrderAdmin)
admin.site.register(Orderitem,OrderitemAdmin)
admin.site.register(Profile)
admin.site.register(Banner)
admin.site.register(Category_slider)
admin.site.register(Author,AuthorAdmin)
admin.site.register(Testimonial,TestimonialAdmin)
admin.site.register(Coupon)




