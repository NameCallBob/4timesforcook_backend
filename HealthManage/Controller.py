"""健康管理的商業邏輯：由會員的身高體重推導出每日飲食/運動目標。"""
import logging
from datetime import date, timedelta

from Member.models import Health, HealthTarget, Member, Prefer

logger = logging.getLogger(__name__)

# 目標的有效期間（約兩個月）
TARGET_DURATION_DAYS = 60


class Manage:
    """健康管理"""

    def analyze(self, member_p):
        """依照使用者的身高體重建立（或更新）每日健康目標。

        @member_p -> MemberP 物件（登入帳號）
        回傳 1 表示建立成功，0 表示缺少必要資料。
        """
        try:
            user_health = Health.objects.get(uid=member_p)
            member = Member.objects.get(uid=member_p)
        except (Health.DoesNotExist, Member.DoesNotExist):
            logger.warning("無法建立健康目標，缺少 Health/Member 資料：%s", member_p)
            return 0

        weight = float(user_health.weight)
        height = float(user_health.height)
        if weight <= 0 or height <= 0:
            logger.warning("身高或體重不合理，跳過健康目標建立：%s", member_p)
            return 0

        bmi = self.__bmi(weight=weight, height=height)
        from HealthManage.expert.run import ruleResult
        target = ruleResult().main(type_expert=1, data=bmi)

        HealthTarget.objects.update_or_create(
            uid=member,
            defaults=dict(
                calories_intake=round(target['calories'] * weight),
                water_intake=round(target['water'] * weight),
                exercise_duration=target['exercise'],
                end_time=date.today() + timedelta(days=TARGET_DURATION_DAYS),
            ),
        )
        return 1

    def __bmi(self, weight, height):
        """計算 BMI。

        身高以公分儲存，BMI 公式需要公尺，先換算再平方；
        原本直接用公分平方會讓所有人的 BMI 都趨近 0 而永遠被判為「過輕」。
        """
        height_m = height / 100
        return round(weight / (height_m ** 2), 2)

    def recommend_diet(self, member_p):
        """依使用者的慢性病資料，給出建議的食譜查詢參數。"""
        try:
            user_health = Health.objects.get(uid=member_p)
        except Health.DoesNotExist:
            return None
        from HealthManage.expert.run import ruleResult
        return ruleResult().main(type_expert=2, data=user_health.disease)
