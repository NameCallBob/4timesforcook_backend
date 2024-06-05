from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from Member.models import Member, MemberP, Health, Prefer

class MemberPrivateSerializer(serializers.Serializer):
    """登入註冊序列化"""
    # MemberP Data
    account = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    # Member Data
    def create(self, validated_data):
        try:
            if 1 == MemberP.objects.filter(account=validated_data['account']).count():
                return [False, "已註冊過", None]
            uid = "U{0:06d}".format(MemberP.objects.all().count()+2)
            from django.contrib.auth.hashers import make_password
            ob = MemberP.objects.create(
                uid=uid,
                account=validated_data['account'],
                password=make_password(validated_data['password']),
            )
            ob.save()
            return [True, "創立成功", uid]
        except Exception as e:
            print(e)
            return [False, f"請確認註冊資料是否有誤,{e}", None]



class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name', 'birth', 'email', 'gender','job']

    def validate(self, data):
        existing_member = Member.objects.filter(email=data['email']).first()
        if existing_member:
            raise serializers.ValidationError("該電子郵件地址已被註冊。")
        return data

    def create(self, uid, validated_data):
        # 建立新的會員物件
        try:
            return Member.objects.create(uid=uid, **validated_data)
        except Exception as e:
            raise serializers.ValidationError(e)

    def update(self, instance, validated_data):
        # 更新現有的會員物件
        instance.name = validated_data.get('name', instance.name)
        instance.birth = validated_data.get('birth', instance.birth)
        instance.email = validated_data.get('email', instance.email)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.job =validated_data.get('job', instance.job)
        instance.save()
        return True


class HealthSerializer(serializers.Serializer):
    """健康資料序列化"""

    height = serializers.IntegerField()
    weight = serializers.IntegerField()
    mental = serializers.ListField()
    allergen = serializers.ListField()
    exercise_intensity = serializers.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(4)
    ])
    excercise_frequency = serializers.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    excercise_time = serializers.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(3)
    ])
    disease = serializers.ListField()

    def create(self, uid, validated_data):
        try:
            ob = Health.objects.create(
                uid=uid,
                **validated_data
            )
            return ob

        except Exception as e:
            raise serializers.ValidationError(e)


class  PreferSerializer(serializers.Serializer):
    target = serializers.ListField(allow_null=False)
    restrict = serializers.ListField()
    prefer = serializers.ListField()
    Nut_need = serializers.ListField()

    def create(self, uid, validated_data):
        try:
            ob = Prefer.objects.create(
                uid=uid,
                **validated_data
            )
            return ob

        except Exception as e:
            raise serializers.ValidationError(e)


class ForgotPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    birth = serializers.DateField()
    def change(self,data):
        ob = Member.objects.filter(email = data['email'],birth=data['birth'])
        if ob.count() == 1:
            try:
                from django.contrib.auth.hashers import make_password
                new_password = make_password(data['password'])
                uid = ob[0].uid.uid
                ob = MemberP.objects.get(uid=uid)
                ob.password = new_password
                ob.save()
                return True

            except Exception as e :
                raise serializers.ValidationError(e)
                return False
        else:
            return False

from Member.models import InputRecord
class InputRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputRecord
        fields = ['date','calories_sum','water_sum','exercise_sum','status']
