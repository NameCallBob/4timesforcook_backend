from django.shortcuts import render
from rest_framework import viewsets, permissions

from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.response import Response
# model
from Record.models import Record_Search, Record_Output
from recipe.models import Recipe_Ob
# Serializer
from recipe.serializer import RecipeSerializer
# Record
from Record.views import record_


class DefaultRunViewsets(viewsets.ModelViewSet):
    """初始化使用"""
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def setting(self, request):
        """進行初步資料庫設定"""
        from recipe.data.data_use import Trans_db
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
        """食譜 範例"""
        ob = Recipe_Ob.objects.all()[:3]
        res = RecipeSerializer(ob, many=True)
        return Response(status=200, data=res.data)

    @action(methods=['post'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def get(self, request):
        """給予前端食譜資料"""
        from answer import frontend_error
        try:
            sentence = request.data['sentence']
        except KeyError:
            frontend_error.KeyError()
        from deep_translator import GoogleTranslator
        trans_sentence = GoogleTranslator(source="zh-TW",target="english").translate(sentence)
        trans_sentence = "Can you recommend a recipe for a comforting lentil soup?"
        label = self.__modelPredict(trans_sentence)
        return Response(status=200, data={"sentence": trans_sentence, "label": label})
        # params = [request.data.get("sentence", ""), request.data.get("time", ""), request.data.get("tags", ""), request.data.get("health_choice", ""),]

    @action(methods=['get'], authentication_classes=[], detail=False)
    def get_id(self, request):
        """透過食譜ID得取食譜資訊"""
        recipe_id = request.GET['rid']
        recipe_ob = Recipe_Ob.objects.filter(rid=recipe_id)
        if recipe_ob.count() == 1:
            res = RecipeSerializer(recipe_ob, many=True)
            return Response(status=200, data=res.data)
        else:
            return Response(status=404, data="無資料")

    def __modelPredict(self, sentence) -> list:
        """利用訓練好的Bert模型"""
        from recipe.BertModel.dataset import align_word_ids, ids_to_labels, tokenizer
        from recipe.BertModel.model import BertModel
        import torch
        import os
        model_path = os.path.join(os.getcwd(),"recipe","BertModel","model.pth")
        model = BertModel()
        model.load_state_dict(torch.load(model_path))
        model.eval()

        use_cuda = torch.cuda.is_available()
        device = torch.device("cuda" if use_cuda else "cpu")

        if use_cuda:
            model = model.cuda()
        else:
            print("USE CPU PREDICT")

        text = tokenizer(sentence, padding='max_length',
                         max_length=128, truncation=True, return_tensors="pt")

        mask = text['attention_mask'].to(device)
        input_id = text['input_ids'].to(device)
        label_ids = torch.Tensor(align_word_ids(sentence)).unsqueeze(0).to(device)

        logits = model(input_id, mask, None)
        logits_clean = logits[0][label_ids != -100]

        predictions = logits_clean.argmax(dim=1).tolist()
        prediction_label = [ids_to_labels[i] for i in predictions]

        return prediction_label


    def __searchDB(self,request,sentence,query = None):
        """
        依照模型給予的參數進行搜尋
        sentence -> User input
        model_query -> BertModel's predicted Tag
        """
        from recipe.data.KBQA_run import DB_search

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