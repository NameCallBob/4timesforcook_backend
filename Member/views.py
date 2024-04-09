
from rest_framework.decorators import action ,permission_classes ,authentication_classes
from rest_framework import viewsets, permissions
from rest_framework.response import Response
# check
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# inner
from Record.views import record_
from Member.models import Member, MemberP
from Member.serializer import MemberPrivateSerializer, MemberSerializer, HealthSerializer, PreferSerializer , ForgotPasswordSerializer
# model
from django.db import transaction
import answer



class MemberViewset(viewsets.ModelViewSet):
    """會員viewset"""
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

<<<<<<< HEAD
    @action(methods=['post'], detail=False ,authentication_classes=[])
=======
    @action(methods=['post'], detail=False ,authentication_classes=[permissions.AllowAny])
>>>>>>> 4fb6132b440573c7d93c50e4eca66ea6abe7f5e3
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

    @action(methods=['post'], detail=False)
    def forgot_password(self, request):
        """忘記密碼"""
        forgot_serializer = ForgotPasswordSerializer(data=request.data)
        if forgot_serializer.is_valid():
            if forgot_serializer.change(data=request.data):
                return Response(status=200,data="ok")
            else:
                return Response(status=404,data={"code":1001})
        else:
            return Response(data=f"資料格式錯誤，錯誤訊息:{forgot_serializer.errors}，請依照錯誤訊息進行修正", status=400)