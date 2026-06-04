from django.db import models

class transaction(models.Model):
    transaction_type=(
    ('income','Income'),
    ('expanses','Expanses')
    )
    title = models.CharField(max_length=100)
    transaction_type = models.CharField( max_length=10,choices=transaction_type)
    category = models.CharField(max_length=100)
    mode=models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True,null=True)
def __str__(self):
        return self.title
    
class user(models.Model):
    name=models.CharField(max_length=255)
    email=models.EmailField(unique=True)
    salary=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField()
   
   
   
def __str__(self):
        return self.name
    