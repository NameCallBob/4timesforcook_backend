
from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
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
    # JWT：以 refresh token 換發新的 3 小時 access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # OpenAPI schema 與 Swagger 文件
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns += router.urls
