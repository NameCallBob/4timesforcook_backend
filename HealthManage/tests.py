"""每日健康管理 (HealthManage app) 的核心邏輯測試。

涵蓋：端點需登入、輸入驗證、每日累計（水/卡路里/運動）與目標達成計算。
"""
import datetime

import pytest
from rest_framework.test import APIClient

from HealthManage.models import daily_water, daily_calories, daily_exercise
from Member.models import Member, MemberP, HealthTarget, InputRecord

PERSONAL_URL = "/HManage/Personal/"
WATER_URL = "/HManage/input_water/"
CALORIES_URL = "/HManage/input_calories/"
EXERCISE_URL = "/HManage/input_exercise/"
WEEK_URL = "/HManage/week_record/"

PASSWORD = "Xq7vplmZ29t"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def member():
    """一位已登入使用者 + 其健康目標。"""
    mp = MemberP.objects.create_user(account="hm_user", password=PASSWORD,
                                     uid="H000001")
    m = Member.objects.create(uid=mp, name="hm_user", email="hm@example.com",
                              gender="male", job="none")
    HealthTarget.objects.create(
        uid=m,
        calories_intake=2000,
        water_intake=3000,
        exercise_duration=300,
        end_time=datetime.date.today() + datetime.timedelta(days=30),
    )
    return mp


@pytest.fixture
def auth_client(client, member):
    client.force_authenticate(user=member)
    return client


# ---------------------------------------------------------------------------
# 權限：所有每日紀錄端點都必須登入
# ---------------------------------------------------------------------------

class TestAuthenticationRequired:
    @pytest.mark.parametrize("url,method", [
        (PERSONAL_URL, "get"),
        (WATER_URL, "post"),
        (CALORIES_URL, "post"),
        (EXERCISE_URL, "post"),
        (WEEK_URL, "get"),
    ])
    def test_anonymous_is_rejected(self, client, url, method):
        resp = getattr(client, method)(url, {}, format="json")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 輸入驗證：缺少必要欄位要回 400
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_water_requires_water_key(self, auth_client):
        resp = auth_client.post(WATER_URL, {"amount": 500}, format="json")
        assert resp.status_code == 400
        assert daily_water.objects.count() == 0

    def test_calories_requires_type_and_calories(self, auth_client):
        resp = auth_client.post(CALORIES_URL, {"calories": 500}, format="json")
        assert resp.status_code == 400
        assert daily_calories.objects.count() == 0

    def test_exercise_requires_strong_and_time(self, auth_client):
        resp = auth_client.post(EXERCISE_URL, {"strong": 2}, format="json")
        assert resp.status_code == 400
        assert daily_exercise.objects.count() == 0


# ---------------------------------------------------------------------------
# 寫入 + 當日累計
# ---------------------------------------------------------------------------

class TestDailyInput:
    def test_water_input_is_stored_and_accumulated(self, auth_client, member):
        assert auth_client.post(WATER_URL, {"water": 500},
                                format="json").status_code == 200
        assert auth_client.post(WATER_URL, {"water": 300},
                                format="json").status_code == 200

        assert daily_water.objects.count() == 2
        record = InputRecord.objects.get(uid__uid=member.uid)
        assert record.water_sum == 800

    def test_calories_input_is_accumulated(self, auth_client, member):
        auth_client.post(CALORIES_URL, {"type": 1, "calories": 600},
                         format="json")
        auth_client.post(CALORIES_URL, {"type": 2, "calories": 250},
                         format="json")

        record = InputRecord.objects.get(uid__uid=member.uid)
        assert record.calories_sum == 850

    def test_exercise_is_weighted_by_intensity(self, auth_client, member):
        """運動量 = 時間 x 強度權重，強度 1/2/3 分別為 2/5/7。"""
        auth_client.post(EXERCISE_URL, {"strong": 3, "sport_time": 30},
                         format="json")

        record = InputRecord.objects.get(uid__uid=member.uid)
        assert record.exercise_sum == 30 * 7

    def test_inputs_share_one_daily_record(self, auth_client, member):
        auth_client.post(WATER_URL, {"water": 500}, format="json")
        auth_client.post(CALORIES_URL, {"type": 1, "calories": 600},
                         format="json")
        auth_client.post(EXERCISE_URL, {"strong": 1, "sport_time": 10},
                         format="json")

        assert InputRecord.objects.filter(uid__uid=member.uid).count() == 1
        record = InputRecord.objects.get(uid__uid=member.uid)
        assert (record.water_sum, record.calories_sum, record.exercise_sum) \
            == (500, 600, 20)


# ---------------------------------------------------------------------------
# 統計輸出
# ---------------------------------------------------------------------------

class TestPersonalSummary:
    def test_summary_reports_targets_and_remaining(self, auth_client):
        auth_client.post(WATER_URL, {"water": 1200}, format="json")
        auth_client.post(CALORIES_URL, {"type": 1, "calories": 500},
                         format="json")
        auth_client.post(EXERCISE_URL, {"strong": 2, "sport_time": 20},
                         format="json")

        resp = auth_client.get(PERSONAL_URL)
        assert resp.status_code == 200
        record = resp.data["record"]

        assert record["water_target"] == 3000
        assert record["water_now"] == 1200
        assert record["water_remain"] == 1800

        assert record["calories_now"] == 500
        assert record["calories_remain"] == 1500

        # 強度 2 -> 權重 5，20 分鐘 => 100
        assert record["exercise_now"] == 100
        assert record["exercise_remain"] == 200

    def test_summary_with_no_input_returns_zero_progress(self, auth_client):
        resp = auth_client.get(PERSONAL_URL)
        assert resp.status_code == 200
        record = resp.data["record"]
        assert record["water_now"] == 0
        assert record["calories_now"] == 0
        assert record["exercise_now"] == 0
        # 一週七天皆為「未填寫」狀態
        assert set(resp.data["week"].values()) == {0}


class TestWeekRecord:
    def test_week_record_returns_this_week_entries(self, auth_client, member):
        auth_client.post(WATER_URL, {"water": 500}, format="json")

        resp = auth_client.get(WEEK_URL)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["water_sum"] == 500

    def test_week_record_excludes_other_members(self, auth_client):
        other_p = MemberP.objects.create_user(account="other_hm",
                                              password=PASSWORD, uid="H000002")
        other = Member.objects.create(uid=other_p, name="other",
                                      email="o@example.com", gender="male",
                                      job="none")
        InputRecord.objects.create(uid=other, date=datetime.date.today(),
                                   calories_sum=999, water_sum=999,
                                   exercise_sum=999, status=1)

        resp = auth_client.get(WEEK_URL)
        assert resp.status_code == 200
        assert resp.data == []


# ---------------------------------------------------------------------------
# 時區：今日區間必須以專案時區 (Asia/Taipei) 計算
# ---------------------------------------------------------------------------

class TestTimezoneBoundary:
    def test_early_morning_entry_counts_as_today(self, auth_client, member):
        """凌晨 00:30 (台北時間) 的紀錄仍屬於「今天」。

        若用 naive datetime 過濾，該筆會被當成 UTC 而落到昨天，導致漏算。
        """
        from django.utils import timezone

        auth_client.post(WATER_URL, {"water": 700}, format="json")
        row = daily_water.objects.get()
        row.time = timezone.make_aware(
            datetime.datetime.combine(timezone.localdate(),
                                      datetime.time(0, 30)))
        row.save()

        resp = auth_client.get(PERSONAL_URL)
        assert resp.status_code == 200
        assert resp.data["record"]["water_now"] == 700


class TestMissingHealthTarget:
    def test_personal_without_health_data_returns_404_not_500(self, client):
        """沒有身高體重就無法推導目標，必須回可理解的 404 而非 500。"""
        mp = MemberP.objects.create_user(account="no_target",
                                         password=PASSWORD, uid="H000003")
        Member.objects.create(uid=mp, name="no_target", email="nt@example.com",
                              gender="male", job="none")
        client.force_authenticate(user=mp)

        resp = client.get(PERSONAL_URL)
        assert resp.status_code == 404

    def test_personal_backfills_target_for_legacy_member(self, client):
        """舊會員有身高體重但沒有目標時，第一次查詢自動補建。"""
        from Member.models import Health

        mp = MemberP.objects.create_user(account="legacy",
                                         password=PASSWORD, uid="H000004")
        Member.objects.create(uid=mp, name="legacy", email="lg@example.com",
                              gender="female", job="none")
        Health.objects.create(uid=mp, height=170, weight=65)
        client.force_authenticate(user=mp)

        resp = client.get(PERSONAL_URL)
        assert resp.status_code == 200
        # BMI 約 22.5 -> 標準（係數 30）
        assert resp.data["record"]["calories_target"] == round(30 * 65)
