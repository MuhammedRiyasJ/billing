from django.shortcuts import render
from datetime import datetime, date, timedelta
import calendar
from products.models import Product
from sales.models import Sale,SaleProduct
from purchases.models import Purchase,PurchaseProduct
from vendors.models import Vendor
from django.db.models import Sum
from app.functions import get_current_shop
from decimal import Decimal
from django.http import HttpResponse
import xlsxwriter
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
from django.conf import settings
from io import BytesIO
from users.models import Profile
from expense.models import Expense


@login_required
@check_group(['admin','staff'])
def view_sale_report(request):

     #get current shop
    current_shop = get_current_shop(request)

    user_profile = Profile.objects.get(user=request.user)

    from_date = request.GET.get('from_date',False)
    to_date = request.GET.get('to_date',False)

    #filter by date
    if from_date and to_date:
       start_date = datetime.strptime(from_date, '%d-%m-%Y')
       end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    elif from_date and not to_date:
        start_date = datetime.strptime(from_date, '%d-%m-%Y')
        end_date =  datetime.today()

    elif not from_date and to_date:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    else:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date =  datetime.today()

    day_count = (end_date-start_date).days + 1
    
    total_sales = Sale.objects.filter(shop=current_shop,is_deleted=False,date__range=[start_date,end_date])

    if user_profile.tax_only:
        total_income = SaleProduct.objects.filter(sale__in=total_sales,is_deleted=False,product__untaxed=False).aggregate(Sum('total_amount'))['total_amount__sum']
    else:
        total_income = SaleProduct.objects.filter(sale__in=total_sales,is_deleted=False).aggregate(Sum('total_amount'))['total_amount__sum']

    total_income = total_income if total_income else 0.00

    report =[]
    for date in (start_date+timedelta(days=days) for days in range(day_count)):
        day_sales = Sale.objects.filter(shop=current_shop,is_deleted=False,date=date)

        if user_profile.tax_only:
            income = SaleProduct.objects.filter(sale__in=day_sales,is_deleted=False,product__untaxed=False).aggregate(Sum('total_amount'))['total_amount__sum']
        else:
            income = SaleProduct.objects.filter(sale__in=day_sales,is_deleted=False).aggregate(Sum('total_amount'))['total_amount__sum']
        income = income if income else '0.00'

        report.append([datetime.strftime(date,'%d-%m-%Y'),str(income)])


    request.session[str(current_shop)+'_report'] = report
    request.session[str(current_shop)+'_total_report'] = [str(total_income)]

    total_expense = Expense.objects.filter(shop=current_shop,is_deleted=False,date__range=[start_date,end_date]).aggregate(Sum('amount'))['amount__sum']

    total_expense = total_expense if total_expense else 0.00

    request.session[str(current_shop)+'_total_expense'] = [str(total_expense)]

    context = {
        'title' : "Sales Report",
        'report' : report,
        'start_date':start_date,
        'end_date': end_date,
        'total_income':total_income,
        'total_expense' : total_expense,
        "reports_active":"active"
    }
    return render(request,'reports/view_sale_report.html',context) 

@login_required
@check_group(['admin','staff'])
def print_sale_report(request):
    
     #get current shop
    current_shop = get_current_shop(request)

    try:
        #getting report from session variable
        report = request.session[str(current_shop)+'_report']
        total_report = request.session[str(current_shop)+'_total_report']

        #delete session
        del request.session[str(current_shop)+'_report']
        del request.session[str(current_shop)+'_total_report']

    except:
        report = None
        total_report = None

    context = {
        "title" : "Sales Report",
        'report' : report,
        'total_report' : total_report,

  
    }
    return render(request,'reports/print_sale_report.html',context)


@login_required
@check_group(['admin'])
def view_purchase_report(request):

     #get current shop
    current_shop = get_current_shop(request)

    #get current user profile
    user_profile = Profile.objects.get(user=request.user)

    from_date = request.GET.get('from_date',False)
    to_date = request.GET.get('to_date',False)

    #filter by date
    if from_date and to_date:
       start_date = datetime.strptime(from_date, '%d-%m-%Y')
       end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    elif from_date and not to_date:
        start_date = datetime.strptime(from_date, '%d-%m-%Y')
        end_date =  datetime.today()

    elif not from_date and to_date:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    else:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date =  datetime.today()

    day_count = (end_date-start_date).days + 1

    total_purchases = Purchase.objects.filter(shop=current_shop,is_deleted=False,date__range=[start_date,end_date])

    if user_profile.tax_only:
        total_purchase_expense = PurchaseProduct.objects.filter(purchase__in=total_purchases,is_deleted=False,product__untaxed=False).aggregate(Sum('total_amount'))['total_amount__sum']
    else:
        total_purchase_expense = PurchaseProduct.objects.filter(purchase__in=total_purchases,is_deleted=False).aggregate(Sum('total_amount'))['total_amount__sum']

    total_purchase_expense = total_purchase_expense if total_purchase_expense else 0.00

    report =[]
    for date in (start_date+timedelta(days=days) for days in range(day_count)):

        day_purchases = Purchase.objects.filter(shop=current_shop,is_deleted=False,date=date)

        if user_profile.tax_only:
            purchase_expense = PurchaseProduct.objects.filter(purchase__in=day_purchases,is_deleted=False,product__untaxed=False).aggregate(Sum('total_amount'))['total_amount__sum']
        else:
            purchase_expense = PurchaseProduct.objects.filter(purchase__in=day_purchases,is_deleted=False).aggregate(Sum('total_amount'))['total_amount__sum']

        purchase_expense =purchase_expense if purchase_expense else '0.00'

        report.append([datetime.strftime(date,'%d-%m-%Y'),str(purchase_expense)])


    request.session[str(current_shop)+'_report'] = report
    request.session[str(current_shop)+'_total_report'] = [str(total_purchase_expense)]

    context = {
        'title' : "Purchase Report",
        'report' : report,
        'start_date':start_date,
        'end_date': end_date,
        'total_purchase_expense':total_purchase_expense,
        "reports_active":"active"
    }
    return render(request,'reports/view_purchase_report.html',context) 

@login_required
@check_group(['admin'])
def print_purchase_report(request):
    
     #get current shop
    current_shop = get_current_shop(request)

    try:
        #getting report from session variable
        report = request.session[str(current_shop)+'_report']
        total_report = request.session[str(current_shop)+'_total_report']

        #delete session
        del request.session[str(current_shop)+'_report']
        del request.session[str(current_shop)+'_total_report']

    except:
        report = None
        total_report = None

    context = {
        "title" : "Purchase Report",
        'report' : report,
        'total_report' : total_report,

  
    }
    return render(request,'reports/print_purchase_report.html',context)


@login_required
@check_group(['admin'])
def view_vat(request):

    #get current shop
    current_shop = get_current_shop(request)


    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

   #filter by date
    if from_date and to_date:
       start_date = datetime.strptime(from_date, '%d-%m-%Y')
       end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    elif from_date and not to_date:
        start_date = datetime.strptime(from_date, '%d-%m-%Y')
        end_date =  datetime.today()

    elif not from_date and to_date:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    else:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date =  datetime.today()

    sales = Sale.objects.filter(shop=current_shop,is_deleted=False,date__range=[start_date,end_date]).order_by('date_added')
    sales_report =[]
    total_sales_tax = Decimal('0.00')

    for sale in sales:
        products = SaleProduct.objects.filter(sale=sale,is_deleted=False,product__untaxed=False)
        total_sale_tax = products.aggregate(Sum('tax_amount'))['tax_amount__sum']
        total_untaxed_amount = products.aggregate(Sum('amount'))['amount__sum']

        if sale.customer:
            tin = sale.customer.tin
            customer_name = sale.customer.name
            customer_address = sale.customer.details
        else:
            tin = None
            customer_name = None
            customer_address = None
        
        if products.exists():
            sale_report = [sale.sale_id,datetime.strftime(sale.date,'%d-%m-%Y'),tin,customer_name,customer_address,str(round(total_untaxed_amount, 2)),str(round(total_sale_tax, 2))]
            total_sales_tax = total_sales_tax + total_sale_tax

        if sales.exists() and products.exists():
            sales_report.append(sale_report)

    purchases = Purchase.objects.filter(shop=current_shop,is_deleted=False,date__range=[start_date,end_date]).order_by('date_added')
    purchases_report =[]
    total_purchases_tax = Decimal('0.00')

    for purchase in purchases:
        products = PurchaseProduct.objects.filter(purchase=purchase,is_deleted=False,product__untaxed=False)
        total_purchase_tax = products.aggregate(Sum('tax_amount'))['tax_amount__sum']
        total_untaxed_amount = products.aggregate(Sum('amount'))['amount__sum']
        
        if purchase.vendor:
            tin = purchase.vendor.tin
            vendor_name = purchase.vendor.name
            vendor_address = purchase.vendor.address
        else:
            tin = None
            vendor_name = None
            vendor_address = None

        if products.exists():
            purchase_report = [purchase.purchase_id,datetime.strftime(purchase.date,'%d-%m-%Y'),tin,vendor_name,vendor_address,str(round(total_untaxed_amount, 2)),str(round(total_purchase_tax, 2))]
            total_purchases_tax = total_purchases_tax + total_purchase_tax

        if purchases.exists() and products.exists():
            purchases_report.append(purchase_report)

    request.session[str(current_shop)+'_sales_report'] = sales_report
    request.session[str(current_shop)+'_total_sales_tax'] = str(round(total_sales_tax,2))
    request.session[str(current_shop)+'_purchases_report'] = purchases_report
    request.session[str(current_shop)+'_total_purchases_tax'] = str(round(total_purchases_tax,2))

    context = {
        "sales_report": sales_report,
        "total_sales_tax":total_sales_tax,
        "purchases_report":purchases_report,
        "total_purchases_tax":total_purchases_tax,
        "start_date":start_date,
        "end_date": end_date,
        "title" : "VAT Report",
        "reports_active":"active"
    }
    return render(request,'reports/view_vat.html',context)

@login_required
@check_group(['admin'])
def print_vat(request):

    #get current shop
    current_shop = get_current_shop(request)

    try:
        sales_report = request.session[str(current_shop)+'_sales_report']
        purchases_report = request.session[str(current_shop)+'_purchases_report']
        total_sales_tax = request.session[str(current_shop)+'_total_sales_tax']
        total_purchases_tax = request.session[str(current_shop)+'_total_purchases_tax']

    except:
        sales_report = None
        purchases_report = None

    context = {
        "title" : "Print VAT",
        "sales_report": sales_report,
        "purchases_report":purchases_report,
        "total_sales_tax":total_sales_tax,
        "total_purchases_tax":total_purchases_tax,
  
    }
    return render(request,'reports/print_vat.html',context)


@login_required
@check_group(['admin'])
def export_xlsx(request):

    #get current shop
    current_shop = get_current_shop(request)

    try:
        sales_report = request.session[str(current_shop)+'_sales_report']
        purchases_report = request.session[str(current_shop)+'_purchases_report']
        total_sales_tax = request.session[str(current_shop)+'_total_sales_tax']
        total_purchases_tax = request.session[str(current_shop)+'_total_purchases_tax']

    except:
        sales_report = None
        purchases_report = None

    buffer = BytesIO()

    workbook = xlsxwriter.Workbook(buffer)
    bold_small_pink= workbook.add_format({'font_size':10,'bold': True,'bg_color':'#FFB6F1','font_name':'arial','right':1})
    small_arial = workbook.add_format({'font_size':10,'font_name':'arial'})

    worksheet = workbook.add_worksheet('Purchases')
    worksheet.set_column(0,2,15)
    worksheet.set_column(3,4,25)
    worksheet.set_column(5,7,15)
    worksheet.set_row(0,40)
    worksheet.write(0,0, "Invoice No\n(Mandatory)",bold_small_pink)
    worksheet.write(0,1, "Invoice Date\n(DD-MM-YYYY)\n(Mandatory)",bold_small_pink)
    worksheet.write(0,2, "Seller Registration No\n(Mandatory)",bold_small_pink)
    worksheet.write(0,3, "Seller Dealer Name\n(Mandatory for Unregistered)",bold_small_pink)
    worksheet.write(0,4, "Seller Dealer Address\n(Mandatory for Unregistered)",bold_small_pink)
    worksheet.write(0,5, "Value of Goods\n(Mandatory)",bold_small_pink)
    worksheet.write(0,6, "Vat Amount Paid\n(Mandatory)",bold_small_pink)
    worksheet.write(0,7, "Cess Amount\n(Mandatory)",bold_small_pink)

    row = 1
    
    for invoice_no,invoice_date,tin,vendor,address,value_of_goods,vat_amount in purchases_report:
        worksheet.write(row,0, invoice_no,small_arial)
        worksheet.write(row,1, invoice_date,small_arial)
        worksheet.write(row,2, tin,small_arial)
        worksheet.write(row,3, vendor,small_arial)
        worksheet.write(row,4, address,small_arial)
        worksheet.write(row,5, value_of_goods,small_arial)
        worksheet.write(row,6, vat_amount,small_arial)
        row = row +1


    worksheet1 = workbook.add_worksheet('Sales')
    worksheet1.set_column(0,2,15)
    worksheet1.set_column(3,4,25)
    worksheet1.set_column(5,7,15)
    worksheet1.set_row(0,40)
    worksheet1.write(0,0, "Invoice No\n(Mandatory)",bold_small_pink)
    worksheet1.write(0,1, "Invoice Date\n(DD-MM-YYYY)\n(Mandatory)",bold_small_pink)
    worksheet1.write(0,2, "Buyer Registration No\n(Mandatory)",bold_small_pink)
    worksheet1.write(0,3, "Buyer Dealer Name\n(Mandatory for Unregistered)",bold_small_pink)
    worksheet1.write(0,4, "Buyer Dealer Address\n(Mandatory for Unregistered)",bold_small_pink)
    worksheet1.write(0,5, "Value of Goods\n(Mandatory)",bold_small_pink)
    worksheet1.write(0,6, "Vat Amount Paid\n(Mandatory)",bold_small_pink)
    worksheet1.write(0,7, "Cess Amount\n(Mandatory)",bold_small_pink)

    row = 1
    
    for invoice_no,invoice_date,tin,customer,address,value_of_goods,vat_amount in sales_report:
        worksheet1.write(row,0, invoice_no,small_arial)
        worksheet1.write(row,1, invoice_date,small_arial)
        worksheet1.write(row,2, tin,small_arial)
        worksheet1.write(row,3, customer,small_arial)
        worksheet1.write(row,4, address,small_arial)
        worksheet1.write(row,5, value_of_goods,small_arial)
        worksheet1.write(row,6, vat_amount,small_arial)
        row = row + 1

    workbook.close()

    xlsx = buffer.getvalue()
    buffer.close()

    response = HttpResponse(xlsx,content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="'+str(current_shop)+'_purchase_sale.xlsx"'

    return response


@login_required
@check_group(['admin'])
def view_excel_report(request):

    #get current shop
    current_shop = get_current_shop(request)


    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

   #filter by date
    if from_date and to_date:
       start_date = datetime.strptime(from_date, '%d-%m-%Y')
       end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    elif from_date and not to_date:
        start_date = datetime.strptime(from_date, '%d-%m-%Y')
        end_date =  datetime.today()

    elif not from_date and to_date:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date = datetime.strptime(to_date, '%d-%m-%Y').replace(hour=23,minute=59,second=59,microsecond=999999)

    else:
        start_date = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_date =  datetime.today()

    request.session[str(current_shop)+'_start_date'] = datetime.strftime(start_date,'%d-%m-%Y')
    request.session[str(current_shop)+'_end_date'] = datetime.strftime(end_date,'%d-%m-%Y')

    context = {
        
        "start_date":start_date,
        "end_date": end_date,
        "title" : "Excel Report",
    }
    return render(request,'reports/view_excel_report.html',context)


@login_required
@check_group(['admin','staff'])
def export_excel(request):

    #get current shop
    current_shop = get_current_shop(request)
    
    start_date = request.session[str(current_shop)+'_start_date']
    end_date = request.session[str(current_shop)+'_end_date']
    start_date_str = datetime.strptime(start_date,'%d-%m-%Y')
    end_date_str = datetime.strptime(end_date,'%d-%m-%Y')
    buffer = BytesIO()

    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet('Purchases')
    format = workbook.add_format()
    bold = workbook.add_format({'bold': True,'bg_color': '#5BCF64'})
    center = workbook.add_format()
    center.set_align('center')
    center.set_align('vcenter')

    format.set_bg_color('#6FACFC')
    format.set_align('center')
    format.set_align('vcenter')
    format.set_border(2)
    worksheet.set_row(0, 25)
    worksheet.set_column('A:S', 10)
    
    worksheet.write(0,0, 'Invoice No',format)
    worksheet.write(0,1, 'Invoice Date',format)
    worksheet.write(0,2, 'Vendor',format)
    worksheet.write(0,3, 'GSTIN',format)
    worksheet.write(0,4, 'State',format)
    worksheet.write(0,5, 'State Code',format)
    worksheet.write(0,6, 'Product',format)
    worksheet.write(0,7, 'HSN code',format)
    worksheet.write(0,8, 'Unit Cost',format)
    worksheet.write(0,9, 'Quantity',format)
    worksheet.write(0,10, 'Discount',format)
    worksheet.write(0,11, 'Taxable Value',format)
    worksheet.write(0,12, 'CGST%',format)
    worksheet.write(0,13, 'CGST',format)
    worksheet.write(0,14, 'SGST%',format)
    worksheet.write(0,15, 'SGST',format)
    worksheet.write(0,16, 'Totoal GST',format)
    worksheet.write(0,17, 'Grand Total',format)

    row = 1

    purchases = Purchase.objects.filter(is_deleted=False,date__range=[start_date_str,end_date_str]).order_by('purchase_id')
    starting_row = 1
    merged_row = 0
    for purchase in purchases:
        purchase_products = PurchaseProduct.objects.filter(is_deleted=False,purchase=purchase)
        total_gst = PurchaseProduct.objects.filter(is_deleted=False,purchase=purchase).aggregate(Sum('tax_amount'))['tax_amount__sum']
        total_net_amount = PurchaseProduct.objects.filter(is_deleted=False,purchase=purchase).aggregate(Sum('amount'))['amount__sum']
        final_total = PurchaseProduct.objects.filter(is_deleted=False,purchase=purchase).aggregate(Sum('total_amount'))['total_amount__sum']

        row_count = purchase_products.count()
        
        for purchase_product in purchase_products:
            product = purchase_product.product
            unit_cost = purchase_product.unit_cost
            cgst = purchase_product.input_gst/2
            cgst_amount = purchase_product.tax_amount/2
            quantity = purchase_product.quantity
            tax_amount = purchase_product.tax_amount
            amount = purchase_product.amount
            offer = purchase_product.offer
            total_amount = purchase_product.total_amount
            worksheet.write(row,6, product.name)
            worksheet.write(row,7, product.hsn_code)
            worksheet.write(row,8, unit_cost)
            worksheet.write(row,9, quantity)
            worksheet.write(row,10, offer)
            worksheet.write(row,11, amount)
            worksheet.write(row+1,11, total_net_amount ,bold)
            worksheet.write(row,12, cgst)
            worksheet.write(row,13, cgst_amount)
            worksheet.write(row,14, cgst)
            worksheet.write(row,15, cgst_amount)
            worksheet.write(row,16, tax_amount)
            worksheet.write(row+1,16, total_gst , bold)
            worksheet.write(row,17, total_amount)
            worksheet.write(row+1,17, final_total , bold)
            row = row +1
        merged_row = merged_row + row_count +1
        worksheet.merge_range(starting_row,0,merged_row,0, purchase.purchase_id,center)
        worksheet.merge_range(starting_row,1,merged_row,1, datetime.strftime(purchase.date,'%d-%m-%Y'),center)
        if purchase.vendor:
            
            worksheet.merge_range(starting_row,2,merged_row,2, purchase.vendor.name,center)
            worksheet.merge_range(starting_row,3,merged_row,3, purchase.vendor.gstin,center)
            worksheet.merge_range(starting_row,4,merged_row,4, purchase.vendor.state,center)
            worksheet.merge_range(starting_row,5,merged_row,5, purchase.vendor.get_state_display(),center) 
        else:
            worksheet.merge_range(starting_row,2,merged_row,2, "")
            worksheet.merge_range(starting_row,3,merged_row,3, "")
            worksheet.merge_range(starting_row,4,merged_row,4, "")
            worksheet.merge_range(starting_row,5,merged_row,5, "")
        starting_row =merged_row + 1
            
        row = row +1 

    worksheet1 = workbook.add_worksheet('Sales')
    
    worksheet1.set_row(0, 25)
    worksheet1.set_column('A:S', 10)
    worksheet1.write(0,0, 'Sale Id',format)
    worksheet1.write(0,1, 'Sale Date',format)
    worksheet1.write(0,2, 'Customer',format)
    worksheet1.write(0,3, 'Details',format)
    worksheet1.write(0,4, 'GSTIN',format)
    worksheet1.write(0,5, 'State',format)
    worksheet1.write(0,6, 'State Code',format)
    worksheet1.write(0,7, 'Product',format)
    worksheet1.write(0,8, 'HSN code',format)
    worksheet1.write(0,9, 'Unit Price',format)
    worksheet1.write(0,10, 'Quantity',format)
    worksheet1.write(0,11, 'Discount',format)
    worksheet1.write(0,12, 'Taxable Value',format)
    worksheet1.write(0,13, 'CGST%',format)
    worksheet1.write(0,14, 'CGST',format)
    worksheet1.write(0,15, 'SGST%',format)
    worksheet1.write(0,16, 'SGST',format)
    worksheet1.write(0,17, 'Total GST',format)
    worksheet1.write(0,18, 'Grant Total',format)

    row = 1
    starting_row = 1
    merged_row = 0
    sales = Sale.objects.filter(is_deleted=False,date__range=[start_date_str,end_date_str]).order_by('sale_id')
    for sale in sales:
        
        sale_products = SaleProduct.objects.filter(is_deleted=False,sale=sale)
        total_gst = SaleProduct.objects.filter(is_deleted=False,sale=sale).aggregate(Sum('tax_amount'))['tax_amount__sum']
        total = SaleProduct.objects.filter(is_deleted=False,sale=sale).aggregate(Sum('total_amount'))['total_amount__sum']
        total_net_amount = SaleProduct.objects.filter(is_deleted=False,sale=sale).aggregate(Sum('amount'))['amount__sum']
        
        row_count = sale_products.count()
        for sale_product in sale_products:
            product = sale_product.product
            unit_price = sale_product.unit_price
            output_gst = sale_product.output_gst
            quantity = sale_product.quantity
            tax_amount = sale_product.tax_amount
            amount = sale_product.amount
            offer = sale_product.offer
            cgst = sale_product.output_gst/2
            cgst_amount = sale_product.tax_amount/2
            total_amount = sale_product.total_amount
            worksheet1.write(row,7, product.name)
            worksheet1.write(row,8, product.hsn_code)
            worksheet1.write(row,9, unit_price)
            worksheet1.write(row,10, quantity)
            worksheet1.write(row,11, offer)
            worksheet1.write(row,12, amount)
            worksheet1.write(row+1,12, total_net_amount , bold)
            worksheet1.write(row,13, cgst)
            worksheet1.write(row,14, cgst_amount)
            worksheet1.write(row,15, cgst)
            worksheet1.write(row,16, cgst_amount)
            worksheet1.write(row,17, tax_amount)
            worksheet1.write(row+1,17, total_gst , bold)
            worksheet1.write(row,18, total_amount)
            worksheet1.write(row+1,18, total, bold)
            row = row +1
        merged_row = merged_row + row_count +1
        worksheet1.merge_range(starting_row,0,merged_row,0, sale.sale_id,center)
        worksheet1.merge_range(starting_row,1,merged_row,1, datetime.strftime(sale.date,'%d-%m-%Y'),center)
        if sale.customer:
            worksheet1.merge_range(starting_row,2,merged_row,2, sale.customer.name,center)
            worksheet1.merge_range(starting_row,3,merged_row,3, sale.customer.details,center)
            worksheet1.merge_range(starting_row,4,merged_row,4, sale.customer.gstin,center)
            worksheet1.merge_range(starting_row,5,merged_row,5, sale.customer.state,center)
            worksheet1.merge_range(starting_row,6,merged_row,6, sale.customer.get_state_display(),center)
        else:
            worksheet1.merge_range(starting_row,2,merged_row,2, "")
            worksheet1.merge_range(starting_row,3,merged_row,3, "")
            worksheet1.merge_range(starting_row,4,merged_row,4, "")
            worksheet1.merge_range(starting_row,5,merged_row,5, "")
            worksheet1.merge_range(starting_row,6,merged_row,6, "")
        starting_row =merged_row + 1
        row = row +1
    

    workbook.close()
    xlsx = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(xlsx,content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="'+str(current_shop)+'_purchase_sale.xlsx"'

    return response