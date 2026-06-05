from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-transaction/', views.addtransaction, name='addtransaction'),
    path('monthly-transaction/', views.Montlytracaction, name='Montlytracaction'),
    path('profile/', views.profile, name='profile'),
    path('delete/<int:id>/',views.delete_data,name='delete_data'),
    path('edit/<int:id>/',views.edit_data,name='edit_data'),
    path('print_transactions', views.print_transactions, name='print_transactions'),
    path('export-pdf/',views.exportpdf,name='export_pdf'),
    path('export-excel/',views.export_excel,name='export_excel'),
   
]
