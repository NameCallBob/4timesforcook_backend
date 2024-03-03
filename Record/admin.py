from django.contrib import admin
from Record.models import Record_Answer,Question,Category
# Register your models here.


admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Record_Answer)
