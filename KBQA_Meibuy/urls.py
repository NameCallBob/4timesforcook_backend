
from django.contrib import admin
from django.urls import path
from rest_framework.routers import  SimpleRouter
from recipe.views import DefaultRunViewsets
from Member.views import *


router = SimpleRouter()
# 建立新路徑
router.register(
    r'Default',DefaultRunViewsets,basename="defaultsetting"
)
router.register(
    r'Center',Member_use_Viewset,basename="loginorRegis"
)
router.register(
    r'Member',MemberViewset,basename="MemberData"
)
# router.register(
#     r""
# )

urlpatterns = [
    path('admin/', admin.site.urls),    
]

urlpatterns += router.urls