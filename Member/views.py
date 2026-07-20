
import logging

from rest_framework.decorators import action ,permission_classes ,authentication_classes
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
# check
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken
# inner
from Record.views import record_
from Member.models import Member, MemberP
from Member.serializer import (
    MemberPrivateSerializer, MemberSerializer, HealthSerializer, PreferSerializer,
    RequestPasswordResetSerializer, ResetPasswordSerializer,
)
# model
from django.db import transaction
import answer

logger = logging.getLogger(__name__)


class PasswordResetThrottle(SimpleRateThrottle):
    """套用 settings 中 'password_reset' 節流速率（預設 5/hour），以來源 IP 為識別。"""
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }



class MemberViewset(viewsets.GenericViewSet):
    """會員 viewset。

    僅暴露 scoped 的 'info' (GET) 與 'change' (POST) 兩個自訂動作，
    皆以 request.user 為範圍。刻意不使用 ModelViewSet，以避免暴露
    針對全體會員的 list/retrieve/update/destroy CRUD（IDOR）。
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=False)
    def info(self, request):
        """輸出會員個人資料"""
        try:
            account = request.user.account
            uid = MemberP.objects.get(account = account)
            data = Member.objects.filter(uid = uid)
            serializer = MemberSerializer(data, many=False)
            return Response(status=200, data=serializer.data)
        except Member.DoesNotExist:
            return Response(status=404, data="?")
        except Exception as e:
            return answer.backend_error.accident(e)

    @action(methods=['post'], detail=False)
    def change(self, request):
        """修改會員資料"""
        account = request.user.account
        try:
            ob = MemberP.objects.get(account = account)
        except MemberP.DoesNotExist:
            return Response(status=404,data="?")

        serializer = MemberSerializer(request.data, many=False)
        if serializer.is_valid():
            ok = serializer.update(
                instance=ob ,
                validated_data=request.data
            )
            if ok :
                return Response(status=200,data="ok")
            else:
                return Response(status=400,data="輸入資料錯誤")
        else:
            return answer.frontend_error.FormatError(serializer.errors)



class Member_use_Viewset(viewsets.ViewSet):
    """會員登入註冊"""
    permission_classes = [permissions.AllowAny]

    @action(methods=['post'], detail=False ,authentication_classes=[])
    def login(self, request):
        """登入"""
        account = request.data.get('account')
        password = request.data.get('password')
        user = authenticate(account=account, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'message': "OK", 'token': str(refresh.access_token)}, status=200)
        else:
            return Response({'error': 'account or password Not Correctly'}, status=400)

    @action(methods=['post'], detail=False ,authentication_classes=[])
    def register(self, request):
        """註冊"""
        try:
            Private_serializer = MemberPrivateSerializer(
                data=request.data['Private'])
            Member_serializer = MemberSerializer(data=request.data['Member'])
            Health_serializer = HealthSerializer(data=request.data['Health'])
            Prefer_serializer = PreferSerializer(data=request.data['Prefer'])
        except KeyError:
            return answer.frontend_error.KeyError()
        try:
            # 判斷資料是否有誤
            if not Private_serializer.is_valid():
                return Response(data="傳送格式出錯或資料有誤，錯誤訊息:{0}，請依照錯誤訊息進行修正".format(Private_serializer.errors), status=400)
            if not Member_serializer.is_valid():
                return Response(data="傳送格式出錯或資料有誤，錯誤訊息:{0}，請依照錯誤訊息進行修正".format(Member_serializer.errors), status=400)
            if not Health_serializer.is_valid():
                return Response(data="傳送格式出錯或資料有誤，錯誤訊息:{0}，請依照錯誤訊息進行修正".format(Health_serializer.errors), status=400)
            if not Prefer_serializer.is_valid():
                return Response(data="傳送格式出錯或資料有誤，錯誤訊息:{0}，請依照錯誤訊息進行修正".format(Prefer_serializer.errors), status=400)
        except Exception as e:
            return (Response(status=500, data=f"出現意外問題，請洽系統管理員，ErrorMessage:{e}，或前端失誤"))
        # do!
        try:
            with transaction.atomic():
                deal_res = Private_serializer.create(request.data['Private'])
                status = deal_res[0]
                message = deal_res[1]
                uid = MemberP.objects.get(uid=deal_res[2])

                if status:
                    if not Member_serializer.create(uid=uid, validated_data=request.data['Member']):
                        return Response(data=f"會員資料建立失敗，錯誤訊息:{Member_serializer.errors}，請依照錯誤訊息進行修正", status=400)
                    else:
                        if not Health_serializer.create(uid=uid, validated_data=request.data['Health']):
                            return Response(data=f"健康資料建立失敗，錯誤訊息:{Health_serializer.errors}，請依照錯誤訊息進行修正", status=400)
                        else:
                            if not Prefer_serializer.create(uid=uid, validated_data=request.data['Prefer']):
                                return Response(data=f"偏好資料建立失敗，錯誤訊息:{Health_serializer.errors}，請依照錯誤訊息進行修正", status=400)
                            else:
                                return Response(status=200, data="OK")
                else:
                    if message == "已註冊過":
                        return Response(status=201, data=message)
                    else:
                        return Response(status=400, data=message)
        except Exception as e:
            transaction.rollback()
            return Response(status=500, data=f"出現意外問題，請洽系統管理員，ErrorMessage:{e}，或前端失誤")
        else:
            transaction.commit()

    @action(methods=['post'], detail=False, authentication_classes=[],
            permission_classes=[permissions.AllowAny],
            throttle_classes=[PasswordResetThrottle])
    def request_password_reset(self, request):
        """請求密碼重設連結。

        無論該 email 是否存在，皆回傳相同的通用訊息，避免帳號列舉。
        若帳號存在，會產生 default_token_generator 的 token 與 base64 編碼的 uid，
        並記錄於 log。此為 portfolio/demo 用途（無郵件伺服器）：僅在 DEBUG 時
        將 uid/token 一併回傳以便測試。
        TODO: 正式環境改用 send_mail() 寄送含 uid/token 的重設連結，
              且切勿於 API 回應中回傳 token。
        """
        serializer = RequestPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=400, data=f"資料格式錯誤，錯誤訊息:{serializer.errors}，請依照錯誤訊息進行修正")

        email = serializer.validated_data['email']
        generic = {"message": "若該電子郵件已註冊，系統將寄送密碼重設連結。"}

        member = Member.objects.filter(email=email).select_related('uid').first()
        if member is not None:
            user = member.uid
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            logger.info(
                "Password reset requested account=%s uid=%s token=%s",
                user.account, uidb64, token,
            )
            if settings.DEBUG:
                data = dict(generic)
                data.update({"uid": uidb64, "token": token})
                return Response(status=200, data=data)

        return Response(status=200, data=generic)

    @action(methods=['post'], detail=False, authentication_classes=[],
            permission_classes=[permissions.AllowAny],
            throttle_classes=[PasswordResetThrottle])
    def reset_password(self, request):
        """透過 uid + token 重設密碼。

        需提供 uid、token 與新密碼；以 default_token_generator 驗證 token，
        並強制套用 Django 密碼驗證器後才更新密碼。
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=400, data=f"資料格式錯誤，錯誤訊息:{serializer.errors}，請依照錯誤訊息進行修正")

        uidb64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = MemberP.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MemberP.DoesNotExist):
            return Response(status=400, data={"code": 1001, "message": "重設連結無效或已過期。"})

        if not default_token_generator.check_token(user, token):
            return Response(status=400, data={"code": 1001, "message": "重設連結無效或已過期。"})

        try:
            validate_password(new_password, user)
        except DjangoValidationError as e:
            return Response(status=400, data={"code": 1002, "message": list(e.messages)})

        user.set_password(new_password)
        user.save()
        return Response(status=200, data={"message": "密碼已成功重設。"})