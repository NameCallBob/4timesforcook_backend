"""規則系統（BMI 目標／慢性病飲食／搜尋參數）與健康目標建立的測試。

這些規則原本以 experta 撰寫，在 Python 3.10+ 已無法載入；改為純 Python 後
以下測試把每條規則的邊界值固定下來。
"""
import pytest

from HealthManage.Controller import Manage
from HealthManage.expert.rule_chronic import DASH_DIET, MEDITERRANEAN_DIET
from HealthManage.expert.run import ruleResult
from Member.models import Health, HealthTarget, Member, MemberP


# ---------------------------------------------------------------------------
# BMI 分級
# ---------------------------------------------------------------------------

class TestBMIRules:
    @pytest.mark.parametrize("bmi,calories", [
        (17.0, 35),    # 過輕
        (18.5, 30),    # 標準（下邊界）
        (23.99, 30),   # 標準（上邊界）
        (24.0, 45),    # 過重（下邊界）
        (26.9, 45),
        (27.0, 40),    # 輕度肥胖
        (30.0, 35),    # 中度肥胖
        (40.0, 35),    # 重度肥胖
    ])
    def test_bmi_maps_to_calorie_coefficient(self, bmi, calories):
        assert ruleResult().main(type_expert=1, data=bmi)["calories"] == calories

    def test_result_is_a_copy_not_shared_state(self):
        first = ruleResult().main(type_expert=1, data=21.0)
        first["calories"] = 999
        second = ruleResult().main(type_expert=1, data=21.0)
        assert second["calories"] == 30


# ---------------------------------------------------------------------------
# 慢性病飲食
# ---------------------------------------------------------------------------

class TestChronicRules:
    def test_chronic_disease_maps_to_dash_diet(self):
        res = ruleResult().main(type_expert=2, data=["diabetes"])
        assert res["ingredients"] == DASH_DIET["ingredients"]

    def test_no_chronic_disease_falls_back_to_mediterranean(self):
        res = ruleResult().main(type_expert=2, data=["none"])
        assert res["ingredients"] == MEDITERRANEAN_DIET["ingredients"]

    def test_symptom_list_stored_as_string_is_parsed(self):
        """資料庫以 "['hypertension']" 這種字串保存 list。"""
        res = ruleResult().main(type_expert=2, data="['hypertension']")
        assert res["ingredients"] == DASH_DIET["ingredients"]

    def test_malformed_string_does_not_execute_code(self):
        """literal_eval 失敗時只是保留原字串，不得執行任意程式碼。"""
        res = ruleResult().main(type_expert=2, data="__import__('os')")
        assert res["ingredients"] == MEDITERRANEAN_DIET["ingredients"]


# ---------------------------------------------------------------------------
# 搜尋參數
# ---------------------------------------------------------------------------

class TestSearchRules:
    def test_known_tag_is_translated(self):
        assert ruleResult().main(type_expert=3, data="alcohol-free") == {
            "index": "object", "columns": "tags", "content": "non-alcoholic"}

    def test_unknown_tag_returns_none(self):
        assert ruleResult().main(type_expert=3, data="deep-fried") is None

    def test_unknown_expert_type_raises(self):
        with pytest.raises(KeyError):
            ruleResult().main(type_expert=99, data=None)


# ---------------------------------------------------------------------------
# 由身高體重推導健康目標
# ---------------------------------------------------------------------------

@pytest.fixture
def member_with_health():
    mp = MemberP.objects.create_user(account="bmi_user", password="Xq7vplmZ29t",
                                     uid="B000001")
    Member.objects.create(uid=mp, name="bmi_user", email="bmi@example.com",
                          gender="female", job="none")
    Health.objects.create(uid=mp, height=165, weight=55)
    return mp


class TestHealthTargetCreation:
    def test_analyze_creates_target_from_height_in_cm(self, member_with_health):
        """身高以公分儲存，換算成公尺後 BMI 約 20.2 -> 標準（係數 30）。"""
        assert Manage().analyze(member_with_health) == 1

        target = HealthTarget.objects.get(uid__uid=member_with_health.uid)
        assert target.calories_intake == round(30 * 55)
        assert target.water_intake == round(30 * 55)
        assert target.exercise_duration == 1000

    def test_analyze_is_idempotent(self, member_with_health):
        Manage().analyze(member_with_health)
        Manage().analyze(member_with_health)
        assert HealthTarget.objects.filter(
            uid__uid=member_with_health.uid).count() == 1

    def test_analyze_without_health_data_returns_zero(self):
        mp = MemberP.objects.create_user(account="no_health",
                                         password="Xq7vplmZ29t", uid="B000002")
        Member.objects.create(uid=mp, name="no_health", email="n@example.com",
                              gender="male", job="none")
        assert Manage().analyze(mp) == 0
        assert not HealthTarget.objects.filter(uid__uid=mp.uid).exists()
