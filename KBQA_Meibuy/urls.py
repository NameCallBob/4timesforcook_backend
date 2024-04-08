
from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter
from recipe.views import DefaultRunViewsets, RecipeViewsets
from Member.views import *
from Record.views import TestViewsets
from HealthManage.views import DailyViewsets

router = SimpleRouter()
# 建立新路徑
# 系統初始設定
router.register(
    r'Default', DefaultRunViewsets, basename="defaultsetting"
)
# 
router.register(
    r'Center', Member_use_Viewset, basename="loginorRegis"
)
# 會員相關
router.register(
    r'Member', MemberViewset, basename="MemberData"
)
# 測驗
router.register(
    r"Test", TestViewsets, basename="Question"
)
# 食譜相關
router.register(
    r"Recipe", RecipeViewsets, basename="RecipeOut"
)
router.register(
    r"HManage", DailyViewsets , basename="HealthDailyReocrd"
)
urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += router.urls
