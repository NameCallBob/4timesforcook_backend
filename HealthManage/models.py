from django.db import models
from Member.models import Member

class daily_water(models.Model):
    """記錄使用者每日水分攝取"""
    uid = models.ForeignKey("使用者ID",Member,on_delete=models.CASCADE)
    time = models.DateTimeField("輸入時間")
    water = models.IntegerField("水分攝取",auto_now_add=True)
    
class daily_calories(models.Model):
    """記錄使用者每日卡路里"""
    TYPE_FOOD = {
        "balence":1,
        "TooOil":2,
        "":3,
        "TooVege":4,
        "":5,
        "":6,
    }
    uid = models.ForeignKey("使用者ID",Member,on_delete=models.CASCADE)
    time = models.DateTimeField("輸入時間")
    type = models.IntegerField("攝取型",choices=TYPE_FOOD)
    water = models.IntegerField("卡路里攝取",auto_now_add=True)

class daily_exercise(models.Model):
    """記錄使用者運動量"""
    EXCERCISE_STRONG = {
        3:"high",2:"medium",1:"low",
    }
    uid = models.ForeignKey("使用者ID",Member,on_delete=models.CASCADE)
    time = models.DateTimeField("輸入時間")
    strong = models.IntegerField("運動強度",choices=EXCERCISE_STRONG)
    water = models.IntegerField("運動時間",auto_now_add=True)
