from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self,account,password,uid,**extra_fields):
        """建立一般使用者"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        user = self.model(uid=uid,account=account, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,account,password,uid='None',**extra_fields):
        """建立管理員或特別權限者"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(("Superuser must have is_superuser=True."))
        return self.create_user(account, password,uid, **extra_fields)

class MemberP(AbstractBaseUser , PermissionsMixin):
    uid = models.CharField("uid", max_length=50,primary_key=True)
    account = models.CharField("帳號", max_length=50 ,null=False,unique=True)
    password = models.CharField("密碼",max_length=100,null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_superuser = models.BooleanField(default=False) # a superuser
    last_login = models.DateTimeField(auto_now=True,null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "account"
    REQUIRED_FIELDS = ['password','uid']
    objects = CustomUserManager()
    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return f"會員編號為{self.uid}"

from datetime import date
class Member(models.Model):
    """儲存會員資料"""
    uid = models.ForeignKey(MemberP,on_delete=models.CASCADE,unique=True,default="ErrorID")
    name = models.TextField(null=False)
    birth = models.DateField(default="2003-06-25")
    email = models.TextField(null=False)
    gender = models.TextField(null=False,default="male")
    job = models.TextField(null=False,default="None")
    join_date = models.DateField(default = date.today)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"會員{self.name}"


class Health(models.Model):
    """會員健康資料"""
    EXCERCISE_TIMES = {
        5:"Everyday",4:"5 times or more",3:"3-4 times",2:"1-2 times",1:"never"
    }
    EXCERCISE_STRONG = {
        4:"high",3:"medium",2:"low",1:"None"
    }
    EXCERCISE_TIME = {
        3:"LongTime",2:"ShortTime",1:"None"
    }
    uid = models.ForeignKey(MemberP,on_delete=models.CASCADE,unique=True)
    height = models.FloatField("身高",default=160)
    weight = models.FloatField("體重",default=60)
    mental = models.TextField("心理因素",null=True)
    exercise_intensity = models.IntegerField("運動強度",null=True,choices=EXCERCISE_STRONG,default=1)
    excercise_frequency = models.IntegerField("運動頻率（週）",null=True,choices=EXCERCISE_TIMES,default=1)
    excercise_time = models.IntegerField("運動時間",null=True,choices=EXCERCISE_TIME,default=1)
    allergen = models.TextField("過敏原",null=True)
    disease = models.TextField("慢性病",null=True)
    
    

class Prefer(models.Model):
    """會員飲食偏好"""
    uid = models.ForeignKey(MemberP,on_delete=models.CASCADE,unique=True)
    target = models.TextField("飲食目標",null=False)
    restrict = models.TextField("飲食限制")
    prefer = models.TextField("飲食偏好")
    Nut_need = models.TextField("營養需求")
    update_time = models.DateTimeField(auto_now=True)

