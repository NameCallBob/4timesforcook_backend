from django.contrib import admin
from Record.models import Record_Answer,Question,Category
# Register your models here.


admin.register(Category)
admin.register(Question)
admin.register(Record_Answer)
