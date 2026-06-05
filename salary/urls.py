"""
URL configuration for salary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse  # <-- 1. Added this import

# 2. Added this function to output the exact JSON format Chrome wants
def manifest_view(request):
    data = {
        "short_name": "ExpenseFlow",
        "name": "Expense Flow Tracker",
        "icons": [
            {
                "src": "https://expansesflow.onrender.com/static/images/logo.png",
                "type": "image/png",
                "sizes": "192x192"
            },
            {
                "src": "https://expansesflow.onrender.com/static/images/logo.png",
                "type": "image/png",
                "sizes": "512x512"
            }
        ],
        "start_url": "/",
        "background_color": "#002119",
        "display": "standalone",
        "theme_color": "#002119"
    }
    return JsonResponse(data)

urlpatterns = [
    path('', include('members.urls')),
    path('manifest.json', manifest_view),
    path('admin/', admin.site.urls),
    
]
