from django.db import models
from Member.models import Member

class daily_water(models.Model):
    """記錄使用者每日水分攝取"""
    uid = models.ForeignKey(Member,on_delete=models.CASCADE)
    time = models.DateTimeField("輸入時間",auto_now_add=True)
    water = models.IntegerField("水分攝取")

class daily_calories(models.Model):
    """記錄使用者每日卡路里"""
    TYPE_FOOD = {
        0:"None",
        1:"balence",
        2:"TooOil",
        3:"TooMuchRice",
        4:"lotsVege",
    }
    uid = models.ForeignKey(Member,on_delete=models.CASCADE)
    time = models.DateTimeField("輸入時間",auto_now_add=True)
    type = models.IntegerField("攝取型",choices=TYPE_FOOD)
    calories = models.IntegerField("卡路里攝取")

class daily_exercise(models.Model):
    """記錄使用者運動量"""
    EXCERCISE_STRONG = {
        3:"high",2:"medium",1:"low",
    }
    uid = models.ForeignKey(Member,on_delete=models.CASCADE)
    time = models.DateTimeField("輸入時間",auto_now_add=True)
    strong = models.IntegerField("運動強度",choices=EXCERCISE_STRONG)
    sport_time = models.IntegerField("運動時間")