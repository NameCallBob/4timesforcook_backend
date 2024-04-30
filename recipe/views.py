from django.shortcuts import render
from rest_framework import viewsets, permissions

from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.response import Response
# model
from Record.models import Record_Search, Record_Output
from recipe.models import Recipe_Ob,Chinese_Ob
# Serializer
from recipe.serializer import RecipeSerializer , ChineseRecipeSerializer
# Record
from Record.views import record_


class DefaultRunViewsets(viewsets.ModelViewSet):
    """初始化使用"""
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def setting(self, request):
        """進行初步資料庫設定"""
        from recipe.Sourcedata.data_use import Trans_db
        data_db = Trans_db()
        # run
        try:
            data_db.trans()
            print("初始化成功！")
            return (Response(status=200, data="資料初始化成功！"))
        except Exception as e:
            print("初始化出現問題")
            print(f"其問題如：{e}")
            return (Response(status=500, data=f"{e}"))


class RecipeViewsets(viewsets.ModelViewSet):
    """食譜相關"""
    serializer_class = RecipeSerializer
    queryset = Recipe_Ob.objects.all()

    @action(methods=['get'], detail=False, permission_classes=[permissions.AllowAny], authentication_classes=[])
    def example_output(self, request):
        """食譜 範例輸出"""
        ob = Chinese_Ob.objects.all()[:3]
        res = ChineseRecipeSerializer(ob, many=True)
        # from deep_translator import GoogleTranslator
        # trans_sentence = GoogleTranslator(source="english",target="zh-TW").translate(res.data)
        return Response(status=200, data=res.data)

    @action(methods=['post'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def get(self, request):
        """給予前端食譜資料"""
        from answer import frontend_error
        try:
            sentence = request.data['sentence']
            object = request.data['object']
            attribute = request.data['attribute']
        except KeyError:
            frontend_error.KeyError()
        from deep_translator import GoogleTranslator
        trans_sentence = GoogleTranslator(source="zh-TW",target="english").translate(sentence)
        # 翻譯
        from recipe.BertModel.main import modelPredict

        label = modelPredict(trans_sentence)
        from recipe.DB_query import DB_search
        rid = DB_search().run(trans_sentence,label)
        ob = Chinese_Ob.objects.filter(rid__in=rid)
        serializer = ChineseRecipeSerializer(ob,many=True)
        return Response(status=200, data=serializer.data)
        # params = [request.data.get("sentence", ""), request.data.get("time", ""), request.data.get("tags", ""), request.data.get("health_choice", ""),]

    @action(methods=['get'], authentication_classes=[],permission_classes=[], detail=False)
    def get_id(self, request):
        """透過食譜ID得取食譜資訊"""
        try:
            recipe_id = request.GET['rid']
        except:
            return Response(status=400,data="請確認是否符合GET的參數傳遞方式")
        recipe_ob = Recipe_Ob.objects.filter(rid=recipe_id)
        if recipe_ob.count() == 1:
            res = RecipeSerializer(recipe_ob, many=True)
            # print(res.data)
            return Response(status=200, data=res.data)
        else:
            return Response(status=404, data="無資料")

    def __searchDB(self,request,sentence,query = None):
        """
        依照模型給予的參數進行搜尋
        sentence -> User input
        model_query -> BertModel's predicted Tag
        """
        from recipe.DB_query import DB_search

        list_id = DB_search().run(query)
        if list_id != 0 and type(list_id) == list:
            """執行成功"""
            res = Recipe_Ob.objects.filter(rid__in=list_id)
            record_().create_record(search=request.data.get("sentence", "僅使用條件判斷"), res=str(list_id),ip = request.META['REMOTE_ADDR'])
            res = RecipeSerializer(res, many=True)
            return Response(status=200, data=res.data)
        else:
            print(list_id)
            return Response(status=500, data="出問題摟，請洽系統管理員")