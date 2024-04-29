from django.db import models

# Create your models here.
"""
KBQA -> 實體與屬性定義：

實體：食材、食譜、烹飪方法等。
屬性：食材的營養價值、食譜的難度、烹飪時間等。

"""

class Recipe_Ob(models.Model):
    """(英文)用於儲存KBQA食譜＿實體＿資訊"""

    rid = models.CharField(max_length = 50)
    name = models.TextField()
    tags = models.TextField()
    steps = models.TextField()
    description = models.TextField()
    ingredients = models.TextField()

class Chinese_Ob(models.Model):
    """(中文)用於儲存KBQA食譜＿實體＿資訊"""

    rid = models.CharField(max_length = 50)
    name = models.TextField()
    tags = models.TextField()
    steps = models.TextField()
    description = models.TextField()
    ingredients = models.TextField()


class Recipe_At(models.Model):
    """用於儲存KBQA食譜＿屬性＿資訊"""

    rid = models.CharField(max_length = 50)
    minutes = models.IntegerField()
    calories = models.FloatField(default=0) #卡路里
    fat = models.FloatField(default=0) #脂肪
    sugar = models.FloatField(default=0) #糖
    sodium = models.FloatField(default=0) #鈉
    protein = models.FloatField(default=0) #蛋白質
    saturated_fat = models.FloatField(default=0) #飽和脂肪
    carbohydrates = models.FloatField(default=0) #碳水化合物
    # nutrition = models.TextField()
    n_steps = models.IntegerField()
    n_ingredients = models.IntegerField()
