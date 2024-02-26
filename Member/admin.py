from django.contrib import admin

# Register your models here.
from Member.models import Member,MemberP,Health

admin.site.register(MemberP)
admin.site.register(Member)
admin.site.register(Health)