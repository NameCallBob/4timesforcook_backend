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

    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def setting_chinese(self,request):
        from recipe.Sourcedata.ob_trans import multiThread
        multiThread()
        return (Response(status=200,data="running"))


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
        # 檢查變數是否上傳正常
        try:
            sentence = request.data.get("sentence",'')
            user_query = request.data.get('user_query','')
            UserIP = request.META['REMOTE_ADDAR']
        except KeyError:
            frontend_error.KeyError()
        # 先判斷使用者是否有傳任何東西
        if sentence=='' and user_query == '':
            return Response(status=400,data="使用者沒有輸入任何參數")
        # 利用套件翻譯
        if sentence != '':
            from deep_translator import GoogleTranslator
            trans_sentence = GoogleTranslator(source="zh-TW",target="english").translate(sentence)
            # 模型實體標記
            from recipe.BertModel.main import modelPredict
            label = modelPredict(trans_sentence)
        else:
            trans_sentence = "" ; label=[]
        # 依照實體去做參數設定
        data = self.__searchDB(
            UserIP=self.get_client_ip(request),
            sentence=sentence,
            trans_sentence=trans_sentence,
            user_query = user_query,
            label = label
        )
        return Response(status=200, data=data)

    @action(methods=['get'], authentication_classes=[],permission_classes=[], detail=False)
    def get_id(self, request):
        """透過食譜ID得取食譜資訊"""
        try:
            recipe_id = request.GET['rid']
        except:
            return Response(status=400,data="請確認是否符合GET的參數傳遞方式")
        recipe_ob = Chinese_Ob.objects.filter(rid=recipe_id)
        if recipe_ob.count()  == 1:
            # 由於先前在新增食譜時未將重複食譜刪除，故先以這處理此問題
            res = ChineseRecipeSerializer(recipe_ob, many=True)
            # print(res.data)
            return Response(status=200, data=res.data)
        else:
            return Response(status=404, data="無資料")

    def __searchDB(self,UserIP,sentence,trans_sentence,user_query,label):
        """
        依照模型給予的參數進行搜尋
        @sentence -> User input
        @trans_sentence -> 翻譯為英文的句子
        @user_query -> 使用者的條件判斷參數
        @labels -> BertModel's predicted Tag
        """
        from recipe.DB_query import DB_search

        list_id = DB_search().run(trans_sentence,label,user_query)

        if list_id != 0 and type(list_id) == list:
            """執行成功"""
            ob = Chinese_Ob.objects.filter(rid__in=list_id)
            if sentence == '':
                sentence="僅使用條件判斷";trans_sentence="None"
            record_().create_record(
                search=sentence,
                search_Eng=trans_sentence,
                res=str(list_id),
                ip = UserIP
            )
            res = ChineseRecipeSerializer(ob, many=True)
            return res.data
        else:
            print("list_id無任何輸出")
            return 0
    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip