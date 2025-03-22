from django.contrib import admin
from .models import Person, FamilyTree
# Register your models here.

admin.site.register(FamilyTree)
admin.site.register(Person)
