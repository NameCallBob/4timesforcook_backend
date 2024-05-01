from Record.serializer import Question_output_Serializer, AnswerSerializer
from Record.models import Record_Answer, Question
from threading import Thread
from django.shortcuts import render
from Record.models import Record_Output, Record_Search, Record_DataChange , Record_Score
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.response import Response
import answer


class record_:

    def create_record(self,ip, search,search_Eng, res):
        """
        記錄使用者輸入輸出內容
        @ip -> 使用者IP
        @search -> 中文輸入
        @search_Eng -> 翻譯為英文
        @res -> 最後的結果
        """
        output_rId = "TEST{0:05d}".format(
            Record_Search.objects.all().count()+1)
        try:

            Record_Search(
                recordId=output_rId,
                ip_address=ip,
                searchText=search,
                searchEngText = search_Eng
            ).save()
            Record_Output(
                recordId=output_rId,
                recipeId=res,
            ).save()
            print("紀錄成功")
            return 1

        except Exception as e:
            print(e)
            return

    def create_Member_record(ip, user_id, type):
        """記錄會員資料修改紀錄"""
        type_list = ["change", "delete", "disable", "forgot"]
        if type not in type_list:
            print(
                f"type not found , your input is {type},you can use [change,delete,disable,forgot]")
            return 0

        descriptio_list = [
            "修改資料",
            "刪除帳號",
            "停用帳號",
            "密碼忘記,重新設置"
        ]

        for i in range(0, 3):
            if type_list[i] == type:
                description = descriptio_list[i]
                try:
                    Record_DataChange(
                        ip_address=ip,
                        user_id=user_id,
                        change_type=type,
                        change_description=description,
                    ).save()
                    return 1

                except Exception as e:
                    print(f"Record儲存失敗！{e}")
                    return 0
        print("出現意外問題")
        return 0


class TestViewsets(viewsets.ViewSet):
    """測驗使用"""

    @action(methods=['get'], detail=False, permission_classes=[permissions.AllowAny], authentication_classes=[])
    def question(self, request):
        """問題"""
        try:
            data = Question.objects.all()
            data = Question_output_Serializer(data, many=True)
            return Response(data=data.data, status=200)
        except Exception as e:
            return answer.backend_error.accident(e)

    @action(methods=['post'], detail=False, permission_classes=[permissions.AllowAny], authentication_classes=[])
    def check(self, request):
        """確認正確"""
        for i in request.data:
            print(i)
            serializer = AnswerSerializer(data=i, many=False)
            if not serializer.is_valid():
                return answer.frontend_error.FormatError(serializer.errors)
        # 跑邏輯
        try:
            score, wrong_qus = self.__caculate(request.data)
            return Response(status=200, data={"score": score, "wrong_question": wrong_qus})
        except Exception as e:
                return Response(status=500, data=answer.backend_error.accident(e))

    def __caculate(self, data: list) -> int:
        """計算分數"""
        score = 100
        wrong = 100 // len(data)
        answer = {"A": 1, "B": 2, "C": 3, "D": 4}
        wrong_qus = []
        for i in data:
            ob = Question.objects.filter(qid=i['qid'])
            if ob[0].right_answer == answer[i['answer']]:
                continue
            else:
                score = score - wrong
                wrong_qus.append(i['qid'])
        t1 = Thread(target=self.__save_UserAnswer,args=(data,score)) ; t1.start()

        return score, wrong_qus

    def __save_UserAnswer(self,data,score):
        """儲存使用者之作答紀錄"""
        answer = {"A": 1, "B": 2, "C": 3, "D": 4}
        answer_id = Record_Score.objects.all().count()+1
        Record_Score(
            answer_id = answer_id,
            score = score,
            is_post_test =data[0]['is_post_test'],
        ).save()
        for i in data:
            Record_Answer(
                answer_id = Record_Score.objects.get(answer_id=answer_id),
                qid = Question.objects.get(qid=(int(i['qid']))),
                answer = answer[i['answer']],
                is_post_test=i['is_post_test'],
            ).save()

class QuestionViewsets(viewsets.ViewSet):
    """內部用於問題"""

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAdminUser])
    def all(self, request):
        ob = Question.objects.all()
        serializer = Question_output_Serializer(ob, many=True)
        return Response(status=200, data=serializer.data)

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAdminUser])
    def new(self, requset):
        return Response(status=404, data="尚未開放")
