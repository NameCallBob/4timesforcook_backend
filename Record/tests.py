"""知識測驗 (Record app) 的核心邏輯測試。

涵蓋：題庫輸出不外洩答案、計分規則、以及錯誤輸入不應噴 500。
"""
import pytest
from rest_framework.test import APIClient

from Record.models import Category, Question, Record_Score, Record_Answer

QUESTION_URL = "/Test/question/"
CHECK_URL = "/Test/check/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def quiz():
    """四題題庫，正解依序為 A(1)、B(2)、C(3)、D(4)。"""
    cate = Category.objects.create(name="營養知識")
    questions = []
    for qid, right in enumerate([1, 2, 3, 4], start=1):
        questions.append(Question.objects.create(
            qid=qid,
            cate=cate,
            content=f"第 {qid} 題",
            option1="選項1", option2="選項2",
            option3="選項3", option4="選項4",
            difficulty=1,
            right_answer=right,
        ))
    return questions


def payload(answers, is_post_test=False):
    """answers: {qid: "A"} -> API 需要的作答清單。"""
    return [{"qid": qid, "answer": ans, "is_post_test": is_post_test}
            for qid, ans in answers.items()]


# ---------------------------------------------------------------------------
# 題庫輸出
# ---------------------------------------------------------------------------

class TestQuestionListing:
    def test_question_list_is_public(self, client, quiz):
        resp = client.get(QUESTION_URL)
        assert resp.status_code == 200
        assert len(resp.data) == 4

    def test_question_list_does_not_leak_right_answer(self, client, quiz):
        """題庫是公開端點，絕不可把正解一起吐出去。"""
        resp = client.get(QUESTION_URL)
        for item in resp.data:
            assert "right_answer" not in item
            assert "difficulty" not in item
            assert {"qid", "content", "option1"} <= set(item)


# ---------------------------------------------------------------------------
# 計分邏輯
# ---------------------------------------------------------------------------

class TestScoring:
    def test_all_correct_scores_100(self, client, quiz):
        resp = client.post(CHECK_URL,
                           payload({1: "A", 2: "B", 3: "C", 4: "D"}),
                           format="json")
        assert resp.status_code == 200
        assert resp.data["score"] == 100
        assert resp.data["wrong_question"] == []

    def test_one_wrong_of_four_scores_75(self, client, quiz):
        """滿分 100，四題每題權重 100 // 4 = 25。"""
        resp = client.post(CHECK_URL,
                           payload({1: "A", 2: "B", 3: "C", 4: "A"}),
                           format="json")
        assert resp.status_code == 200
        assert resp.data["score"] == 75
        assert resp.data["wrong_question"] == [4]

    def test_all_wrong_scores_zero(self, client, quiz):
        resp = client.post(CHECK_URL,
                           payload({1: "B", 2: "C", 3: "D", 4: "A"}),
                           format="json")
        assert resp.status_code == 200
        assert resp.data["score"] == 0
        assert sorted(resp.data["wrong_question"]) == [1, 2, 3, 4]

    def test_single_question_is_all_or_nothing(self, client, quiz):
        wrong = client.post(CHECK_URL, payload({1: "D"}), format="json")
        right = client.post(CHECK_URL, payload({1: "A"}), format="json")
        assert wrong.data["score"] == 0
        assert right.data["score"] == 100


# ---------------------------------------------------------------------------
# 輸入防護：壞資料要回 4xx，不能變成 500
# ---------------------------------------------------------------------------

class TestInputGuards:
    def test_empty_body_returns_400(self, client, quiz):
        resp = client.post(CHECK_URL, [], format="json")
        assert resp.status_code == 400

    def test_unknown_qid_returns_400_not_500(self, client, quiz):
        resp = client.post(CHECK_URL, payload({99999: "A"}), format="json")
        assert resp.status_code == 400

    def test_missing_answer_key_returns_400(self, client, quiz):
        resp = client.post(CHECK_URL,
                           [{"qid": 1, "is_post_test": False}],
                           format="json")
        assert resp.status_code == 400

    def test_non_integer_qid_returns_400(self, client, quiz):
        resp = client.post(CHECK_URL,
                           [{"qid": "not-a-number", "answer": "A",
                             "is_post_test": False}],
                           format="json")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 內部題庫維護端點需管理員權限
# ---------------------------------------------------------------------------

class TestQuestionModels:
    def test_score_and_answer_models_link_together(self, quiz):
        """作答紀錄的資料模型關聯正確（背景寫入所依賴的結構）。"""
        score = Record_Score.objects.create(answer_id=1, score=75,
                                            is_post_test=False)
        Record_Answer.objects.create(answer_id=score, qid=quiz[0],
                                     answer=1, is_post_test=False)
        assert Record_Answer.objects.filter(answer_id=score).count() == 1
        assert Record_Answer.objects.get(answer_id=score).qid.qid == 1
