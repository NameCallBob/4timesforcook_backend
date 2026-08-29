"""建立一組展示用資料，讓任何人 clone 之後就能直接把 API 跑起來看。

用法::

    python manage.py migrate
    python manage.py seed_demo
    python manage.py runserver

接著開啟 http://127.0.0.1:8000/api/docs/ 操作 API，
或直接看 http://127.0.0.1:8000/Test/question/ 的公開題庫。

資料皆為虛構的展示資料，不含任何真實使用者資訊。
"""
import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

DEMO_ACCOUNT = "demo"
DEMO_PASSWORD = "Demo!4time2024"
DEMO_UID = "DEMO0001"

QUESTIONS = [
    (1, "下列何者為每日建議飲水量的常見估算方式？",
     "體重(公斤) x 30 毫升", "固定 1000 毫升", "只在口渴時喝", "每天 5 公升", 1),
    (2, "下列哪一種烹調方式通常含油量最低？",
     "清蒸", "油炸", "熱炒", "焗烤", 1),
    (3, "關於「剩食」，下列敘述何者正確？",
     "外觀不佳的蔬果多半仍可安全食用", "剩食一定已經腐敗",
     "剩食不可再利用", "剩食僅指過期食品", 1),
    (4, "想增加膳食纖維攝取，下列何者最有幫助？",
     "全穀類與蔬果", "含糖飲料", "精緻白麵包", "加工肉品", 1),
    (5, "運動後補充蛋白質的主要目的是？",
     "協助肌肉修復與生長", "立即降低體重", "取代所有正餐", "增加體脂肪", 1),
]


class Command(BaseCommand):
    help = "建立展示用的題庫、示範會員與每日健康紀錄（不含真實資料）"

    @transaction.atomic
    def handle(self, *args, **options):
        from HealthManage.models import daily_calories, daily_exercise, daily_water
        from Member.models import (Health, HealthTarget, Member, MemberP,
                                   InputRecord, Prefer)
        from Record.models import Category, Question

        cate, _ = Category.objects.get_or_create(name="營養知識")
        for qid, content, o1, o2, o3, o4, right in QUESTIONS:
            Question.objects.update_or_create(
                qid=qid,
                defaults=dict(cate=cate, content=content, option1=o1,
                              option2=o2, option3=o3, option4=o4,
                              difficulty=1, right_answer=right),
            )
        self.stdout.write(f"題庫：{Question.objects.count()} 題")

        member_p = MemberP.objects.filter(account=DEMO_ACCOUNT).first()
        if member_p is None:
            member_p = MemberP.objects.create_user(
                account=DEMO_ACCOUNT, password=DEMO_PASSWORD, uid=DEMO_UID)
        else:
            member_p.set_password(DEMO_PASSWORD)
            member_p.save()

        member, _ = Member.objects.get_or_create(
            uid=member_p,
            defaults=dict(name="示範帳號", email="demo@example.com",
                          gender="female", job="engineer"),
        )
        Health.objects.get_or_create(
            uid=member_p,
            defaults=dict(height=165, weight=58, mental="['none']",
                          allergen="['none']", disease="['none']",
                          exercise_intensity=2, excercise_frequency=3,
                          excercise_time=2),
        )
        Prefer.objects.get_or_create(
            uid=member_p,
            defaults=dict(target="['loseWeight']", restrict="['vegetarian']",
                          prefer="['chinese']", Nut_need="['highFiber']"),
        )
        HealthTarget.objects.update_or_create(
            uid=member,
            defaults=dict(calories_intake=2000, water_intake=3000,
                          exercise_duration=300,
                          end_time=datetime.date.today() + datetime.timedelta(days=90)),
        )

        today = datetime.date.today()
        daily_water.objects.filter(uid=member).delete()
        daily_calories.objects.filter(uid=member).delete()
        daily_exercise.objects.filter(uid=member).delete()
        daily_water.objects.create(uid=member, water=1200)
        daily_calories.objects.create(uid=member, type=1, calories=680)
        daily_exercise.objects.create(uid=member, strong=2, sport_time=25)

        for offset in range(0, 4):
            InputRecord.objects.update_or_create(
                uid=member, date=today - datetime.timedelta(days=offset),
                defaults=dict(calories_sum=1800 - offset * 120,
                              water_sum=2600 - offset * 200,
                              exercise_sum=260 - offset * 30, status=1),
            )

        self.stdout.write(self.style.SUCCESS(
            f"完成！示範帳號 account={DEMO_ACCOUNT} password={DEMO_PASSWORD}"))
        self.stdout.write("開啟 http://127.0.0.1:8000/api/docs/ 即可操作 API。")
