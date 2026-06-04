from django.contrib import admin
from .models import transaction
from .models import user

admin.site.register(transaction)
admin.site.register(user)