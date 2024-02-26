from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
# Create your views here.
# model
from Record.models import Record_Search , Record_Output
from recipe.models import Recipe_Ob
# Serializer
from recipe.serializer import RecipeSerializer
# Record
from Record.views import record_
class DefaultRunViewsets(viewsets.ModelViewSet):
    """初始化使用"""
    @action(methods=['get'] , detail=False)
    def setting(self,request):
        """進行初步資料庫設定"""
        from recipe.data.data_use import Trans_db
        data_db = Trans_db()
        # run
        try:
            data_db.trans()
            print("初始化成功！")
            return(Response(status=200,data="資料初始化成功！"))
        except Exception as e:
            print("初始化出現問題")
            print(f"其問題如：{e}")
            return(Response(status=500,data=f"{e}"))

class RecipeViewsets(viewsets.ModelViewSet):
    """食譜相關"""
    serializer_class = RecipeSerializer
    queryset = Recipe_Ob.objects.all()
    @action(methods=['post'] , detail=False)
    def get(self,request):
        """給予前端食譜資料"""
        test_data = {
        "object":{
            "name":"pizza",
        },
        "Attribute":{
            "minutes":30
        }
        }

    
        
        list_id = DB_search().run(test_data)
        if list_id != 0 and type(list_id) == list :
            """執行成功"""
            res = Recipe_Ob.objects.filter(rid__in=list_id)
            record_().create_record(search="我想吃pizza並想花30分鐘煮或烤!",res=str(list_id))
            res = RecipeSerializer(res , many=True)
            return Response(status=200,data=res.data)
        else:
            print(list_id)
            return Response(status=500,data="出問題摟，請洽系統管理員")

   