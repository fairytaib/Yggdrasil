from django.contrib import admin
from .models import Person, FamilyTree, FamilyRelation
# Register your models here.

admin.site.register(FamilyTree)
admin.site.register(Person)
admin.site.register(FamilyRelation)
