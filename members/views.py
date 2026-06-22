from django.shortcuts import render, redirect, get_object_or_404
from .models import transaction, user
from django.db.models import Sum, Count
import calendar
from datetime import datetime, date
import json
from django.http import HttpResponse # for http runing 
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,  Paragraph,Spacer)# for create pdf table text design space 
from reportlab.lib import colors    # table color
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import HRFlowable #for horizontal line
from reportlab.lib.pagesizes import letter

from openpyxl import Workbook
current = date.today()

def home(request):
    base_query = transaction.objects.all()
    data = base_query.order_by('-date')[:2]
    get_name = user.objects.all()
    now = datetime.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    Transactions = transaction.objects.filter(date__year=year, date__month=month, transaction_type='expanses')
    graph_query = Transactions.values('date').annotate(total_daily=Sum('amount')).order_by('date')
    
    graph_labels = [] 
    graph_data = []
   
    for entry in graph_query:
        formated_date = entry['date'].strftime('%d %b')
        graph_labels.append(formated_date)
        graph_data.append(float(entry['total_daily']))

    highest_day = "No Data"
    highest_amount = 0
    lowest_day = "No Data"
    lowest_amount = float('inf') 

    if graph_query:
        for entry in graph_query:
            current_amount = float(entry['total_daily'])
            current_date = entry['date'].strftime('%d %b') 

            if current_amount > highest_amount:
                highest_amount = current_amount
                highest_day = current_date

            if current_amount < lowest_amount:
                lowest_amount = current_amount
                lowest_day = current_date

        if lowest_amount == float('inf'):
            lowest_amount = 0
    else:
        lowest_amount = 0

    category_data = transaction.objects.filter(transaction_type='expanses').values('category').annotate(total=Sum('amount'), total_entries=Count('id')).order_by('-total')
    
    pie_labels = []
    pie_data = []
    for item in category_data:
        pie_labels.append(item['category'])
        pie_data.append(float(item['total']))

    totalex = total_expanses()
    totalin = total_income()
    netbalance = totalin - totalex
    
    # 1. Calculate health safely
    if totalin > 0:
        health = (netbalance / totalin) * 100
    else:
        health = 0
        
    # 2. These lines must move back to the left so they run NO MATTER WHAT
    expanses_count = base_query.filter(transaction_type="expanses").aggregate(Count('id'))['id__count'] or 0
    income_count = base_query.filter(transaction_type="income").aggregate(Count('id'))['id__count'] or 0

    return render(request, 'index.html', context={
        "current": current, "data": data, "user": get_name, 
        'graph_labels': json.dumps(graph_labels), 'graph_data': json.dumps(graph_data),
        'highest_day': highest_day, 'highest_amount': highest_amount,
        'lowest_day': lowest_day, 'lowest_amount': lowest_amount,
        'pie_labels': json.dumps(pie_labels), 'pie_data': json.dumps(pie_data),
        'category_data': category_data, 'totalexpanseamount': totalex, 
        "countexpanses": expanses_count, 'countincome': income_count,
        'totalincome': totalin, 'netbalance': netbalance, 'finacialhelath': health
    })

def addtransaction(request):
    error = None
    if request.method == "POST":
        title = request.POST.get("title")
        transaction_type = request.POST.get("transaction_type")
        category = request.POST.get("category")
        mode=request.POST.get("mode")
        amount = request.POST.get("amount")
        input_date = request.POST.get("date")
        note = request.POST.get("note")
        if not category or category == "" or category == "Select Category":
            error = 'Please select a valid category.'
        else:
            transaction.objects.create(
                title=title,
                transaction_type=transaction_type,
                category=category,
                mode=mode,
                amount=amount,
                date=input_date,
                note=note
            )
            return redirect('addtransaction')
        
    transaction_type = request.GET.get("type")
    data = transaction.objects.all().order_by("-date")

    today_expnases = transaction.objects.filter(transaction_type='expanses', date=date.today())

    if today_expnases.exists():
        # Fixed missing closing parenthesis at the end of .aggregate(...)
        todayamount = today_expnases.aggregate(total=Sum('amount'))['total']
    else:
        todayamount = 0 
    
    excount = transaction.objects.filter(transaction_type='expanses', date=date.today()).count()
    
    today_income = transaction.objects.filter(transaction_type='income', date=date.today())

    if today_income.exists():
        # Fixed missing closing parenthesis at the end of .aggregate(...)
        todayiamount = today_income.aggregate(total=Sum('amount'))['total']
    else:
        todayiamount = 0
    
    icount= transaction.objects.filter(transaction_type='income', date=date.today()).count()
    
    get_name = user.objects.all()
    
    if transaction_type:
        data = data.filter(transaction_type=transaction_type)

    cash=transaction.objects.filter(transaction_type='expanses', mode='Cash').aggregate(Sum('amount'))['amount__sum'] or 0
    cashcount=transaction.objects.filter(transaction_type='expanses',mode='Cash').count()


    bank=transaction.objects.filter(transaction_type='expanses',mode='Bank').aggregate(Sum('amount'))['amount__sum'] or 0
    bankcount=transaction.objects.filter(transaction_type='expanses',mode='Bank').count()
   
    return render(request, 'addexpanses.html', context={
        "data": data,
        'tamount': todayamount,
        'iamount':todayiamount,
        "user": get_name,
        "ec":excount,
        "ic":icount,
        'cash':cash,
        'cashc':cashcount,
        'bank':bank,
        'bankc':bankcount,
        'error': error,
        "current": current,
    })


def total_expanses():
    total = transaction.objects.filter(transaction_type='expanses').aggregate(Sum('amount'))['amount__sum'] or 0
    return total

def total_income():
    total = transaction.objects.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    return total

def highexpanses():
    highest_expanse = transaction.objects.filter(transaction_type='expanses').order_by("-amount").first()
    return highest_expanse


def Montlytracaction(request):
    totalex = total_expanses()
    high_expanses = highexpanses()
    category_data = transaction.objects.filter(transaction_type='expanses').values('category').annotate(total=Sum('amount'), total_entries=Count('id')).order_by('-total')
    topcategory = transaction.objects.filter(transaction_type='expanses').values('category').annotate(total=Sum('amount')).order_by('-total').first()
    get_name = user.objects.all()
    
    for i in category_data:
        if totalex and totalex > 0:
            i['percentage'] = round((i["total"] / totalex) * 100, 1)
        else:
            i['percentage'] = 0

    now = datetime.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    monthlyexpanse=transaction.objects.filter(date__year=year,date__month=month,transaction_type='expanses')
    monthlyincome=transaction.objects.filter(date__year=year,date__month=month,transaction_type='income')

    monthly_expenses_count = monthlyexpanse.count()
    monthly_income_count = monthlyincome.count()

    monthly_total_expense = monthlyexpanse.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_total_income = monthlyincome.aggregate(Sum('amount'))['amount__sum'] or 0
   
    userdata = user.objects.first()
    if userdata and userdata.salary:
        print(userdata.salary)  # Safe to print now!
        budget_limit = int(int(userdata.salary) * 0.21)
    else:
        budget_limit = 4000

    if budget_limit > 0:
        budget_percentage = round((monthly_total_expense / budget_limit) * 100, 1)
    else:
        budget_percentage = 0

    net_balance = monthly_total_income - monthly_total_expense





    Transactions = transaction.objects.filter(date__year=year, date__month=month, transaction_type='expanses')
    daily_spending = {}
    spending_query = Transactions.values('date__day').annotate(total_day_amount=Sum('amount'))

    for entry in spending_query:
        day_num = entry['date__day']
        daily_spending[day_num] = float(entry['total_day_amount'])

    cal = calendar.Calendar(firstweekday=6)
    raw_weeks = cal.monthdayscalendar(year, month)
    
    combined_matrix = []
    for week in raw_weeks:
        week_data = []
        for day in week:
            if day == 0:
                spending_amount = 0
            else:
                spending_amount = daily_spending.get(day, 0)
            day_info = {'number': day, 'spending': spending_amount}
            week_data.append(day_info)
        combined_matrix.append(week_data)

    return render(request, 'month.html', context={
        "current": current, "highex": high_expanses, 'category_data': category_data, 
        "topcategory": topcategory, "user": get_name, "current": now, 
        'combined_matrix': combined_matrix, 'current_year': year,
        'current_month_num': month, 'current_month_name': calendar.month_name[month],
        'monthly_expense': monthly_total_expense,
        'monthly_expense_count': monthly_expenses_count,
        'monthly_income': monthly_total_income,
        'monthly_income_count': monthly_income_count,
        'budget_limit': budget_limit,
        'budget_percentage': budget_percentage,
        'net_balance': net_balance,
    })

def profile(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        salary = request.POST.get("salary")
        input_date = request.POST.get("date")
        user.objects.create(
            name=name,
            email=email,
            salary=salary,
            date=input_date
        )
        return redirect("profile")
        
    userdata = user.objects.first()
    income = total_income()
    expanses = total_expanses()
    total = transaction.objects.aggregate(Count('id'))['id__count'] or 0
         
    return render(request, 'profile.html', context={
        "current": current, "user": userdata, "tincome": income, 
        'texpanses': expanses, "total": total
    })

def edit_data(request, id):
    data = get_object_or_404(transaction, id=id)
    if request.method == 'POST':
        data.title = request.POST.get('title')
        data.category = request.POST.get('category')
        data.mode=request.POST.get('mode')
        data.amount = request.POST.get('amount')
        data.date = request.POST.get('date')
        data.note = request.POST.get('note')
        data.transaction_type = request.POST.get('transaction_type')
        data.save()
        return redirect('addtransaction')

    return render(request, 'addexpanses.html', context={"data": data})

def delete_data(request, id):
    data = transaction.objects.get(id=id)
    data.delete()
    return redirect('addtransaction')
    
def print_transactions(request):
    data = transaction.objects.all().order_by('-date')
    return render(request,'print.html',context={'data': data})

def exportpdf(request):
    response = HttpResponse(content_type='application/pdf') #this say it is pdf file
    response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'
    
    doc = SimpleDocTemplate(
    response,
    pagesize=letter,
    rightMargin=20,
    leftMargin=20,
    topMargin=20,
    bottomMargin=20
)
    elements=[]
    styles = getSampleStyleSheet()
    title = Paragraph("Expense Flow Tracker Report",styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable())
    elements.append(Spacer(1, 12))
    data = [[
    'Sr No',
    'Title',
    'Category',
    'Mode',
    'Type',
    'Amount',
    'Date'
]]
    queryset = transaction.objects.all()
    for index, i in enumerate(queryset, start=1):
        data.append([
            index,
            i.title,
            i.category,
            i.mode,
            i.transaction_type,
            f"₹ {i.amount}",
            str(i.date)
        ])
    table = Table(data,colWidths=[40,120,100,80,80,90])
    table.setStyle(TableStyle([

    ('BACKGROUND', (0,0), (-1,0), colors.green),

    ('TEXTCOLOR', (0,0), (-1,0), colors.white),

    ('GRID', (0,0), (-1,-1), 1, colors.black),

    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

    ('BOTTOMPADDING', (0,0), (-1,0), 12),

    ('BACKGROUND', (0,1), (-1,-1), colors.beige),

    ('FONTSIZE', (0,0), (-1,-1), 10),

    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

]))
    elements.append(table)# BUILD PDF
    doc.build(elements)

    return response
def export_excel(request):

    # CREATE WORKBOOK
    wb = Workbook()

    # ACTIVE SHEET
    ws = wb.active

    # SHEET TITLE
    ws.title = "Expense Report"

    # HEADER
    ws.append([
        'Sr No',
        'Title',
        'Category',
        'Mode',
        'Type',
        'Amount',
        'Date'
    ])

    # DATABASE DATA
    queryset = transaction.objects.all()

    for index, i in enumerate(queryset, start=1):

        ws.append([
            index,
            i.title,
            i.category,
            i.mode,
            i.transaction_type,
            float(i.amount),
            str(i.date)
        ])

    # RESPONSE
    response = HttpResponse(
        content_type='application/ms-excel'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="expense_report.xlsx"'

    # SAVE FILE
    wb.save(response)

    return response
