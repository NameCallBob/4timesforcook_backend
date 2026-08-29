import logging
from threading import Thread

from django.db import connection
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.response import Response

from Record.serializer import Question_output_Serializer, AnswerSerializer
from Record.models import Record_Answer, Question
from Record.models import Record_Output, Record_Search, Record_DataChange , Record_Score
import answer

logger = logging.getLogger(__name__)


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
            logger.info("查詢紀錄建立成功 recordId=%s", output_rId)
            return 1

        except Exception:
            logger.exception("查詢紀錄建立失敗")
            return

    def create_Member_record(ip, user_id, type):
        """記錄會員資料修改紀錄"""
        type_list = ["change", "delete", "disable", "forgot"]
        if type not in type_list:
            logger.warning(
                "type not found, got %s, expected one of %s", type, type_list)
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

                except Exception:
                    logger.exception("Record 儲存失敗")
                    return 0
        logger.warning("create_Member_record 未匹配到任何變更類型: %s", type)
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
        if not request.data:
            return Response(status=400, data="未提供任何作答資料")
        for i in request.data:
            serializer = AnswerSerializer(data=i, many=False)
            if not serializer.is_valid():
                return answer.frontend_error.FormatError(serializer.errors)
        # 跑邏輯
        try:
            score, wrong_qus = self.__caculate(request.data)
        except Question.DoesNotExist:
            # 前端送了不存在的題號，屬於輸入錯誤而非系統錯誤
            return Response(status=400, data="作答資料含有不存在的題號(qid)")
        except Exception as e:
            logger.exception("quiz check failed")
            return answer.backend_error.accident(e)
        return Response(status=200, data={"score": score, "wrong_question": wrong_qus})

    # 選項字母與資料庫中 right_answer 整數的對照表
    ANSWER_MAP = {"A": 1, "B": 2, "C": 3, "D": 4}

    def __caculate(self, data: list):
        """計算分數，回傳 (分數, 答錯的題號清單)。

        題號不存在時丟出 Question.DoesNotExist，由呼叫端轉成 400。
        """
        score = 100
        wrong = 100 // len(data)
        wrong_qus = []
        for i in data:
            # 用 get() 讓不存在的題號直接丟 DoesNotExist，而不是 IndexError -> 500
            ob = Question.objects.get(qid=i['qid'])
            if ob.right_answer == self.ANSWER_MAP[i['answer']]:
                continue
            score = score - wrong
            wrong_qus.append(i['qid'])
        # 作答紀錄非即時需求，放到背景執行緒避免拖慢回應
        Thread(target=self.__save_UserAnswer, args=(data, score), daemon=True).start()

        return score, wrong_qus

    def __save_UserAnswer(self,data,score):
        """儲存使用者之作答紀錄（背景執行緒）。

        背景執行緒中的例外不會傳回前端，因此在這裡收斂並記錄，
        同時關閉本執行緒自己開出來的 DB 連線避免連線洩漏。
        """
        try:
            answer_id = Record_Score.objects.all().count()+1
            score_ob = Record_Score.objects.create(
                answer_id = answer_id,
                score = score,
                is_post_test =data[0]['is_post_test'],
            )
            for i in data:
                Record_Answer.objects.create(
                    answer_id = score_ob,
                    qid = Question.objects.get(qid=(int(i['qid']))),
                    answer = self.ANSWER_MAP[i['answer']],
                    is_post_test=i['is_post_test'],
                )
        except Exception:
            logger.exception("儲存使用者作答紀錄失敗")
        finally:
            connection.close()

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
