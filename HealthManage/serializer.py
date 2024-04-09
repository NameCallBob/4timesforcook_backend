from rest_framework import serializers
from .models import daily_water, daily_calories, daily_exercise
from Member.models import Member
class DailyWaterSerializer(serializers.ModelSerializer):
    """使用者水序列化"""
    class Meta:
        model = daily_water
        fields = '__all__'
        
    # def validate(self,data):
    #     """
    #     內部方法，用於檢查是否提供了 water 屬性
    #     """
    #     errors = {}
    #     water = data.get('water',None)

    #     if water is None:
    #         errors['water'] = ["請提供水分攝取量"]

    #     if errors:
    #         raise serializers.ValidationError(errors)    
        
    def create(self,uid, validated_data):
        try:
            uid = Member.objects.get(uid=uid)
            daily_water.objects.create(
                uid=uid ,
                water = validated_data['water']
            ).save()
            return True
        except Member.DoesNotExist:
            return "User not found:D"
        except serializers.ValidationError as e:
            print(e)
            return e 
    
class DailyCaloriesSerializer(serializers.ModelSerializer):
    """卡路里序列化"""
    class Meta:
        model = daily_calories
        fields = '__all__'
    
    def create(self,uid, validated_data):
        try:
            uid = Member.objects.get(uid=uid)
            daily_calories.objects.create(
                uid = uid ,
                type = validated_data['type'],
                calories = validated_data['calories']
            ).save()
            return True
        except Member.DoesNotExist:
            return "User not found:D"
        except serializers.ValidationError as e:
            raise e    
        except Exception as e:
            raise f"發生意外問題，請洽後端，問題：{e}"
class DailyExerciseSerializer(serializers.ModelSerializer):
    """使用者運動序列化"""
    class Meta:
        model = daily_exercise
        fields = '__all__'
   
    def create(self,uid, validated_data):
        """新增"""
        try:
            uid = Member.objects.get(uid=uid)
            daily_exercise.objects.create(
                uid = uid ,
                strong = validated_data['strong'],
                sport_time = validated_data['sport_time']
            ).save()
            return True
        except Member.DoesNotExist:
            raise serializers.ValidationError("User not found:D")
        except Exception as e:
            raise serializers.ValidationError(f"發生意外問題，請洽後端，問題：{e}")
             
class UserDailyInfoSerializer(serializers.Serializer):
    """用於統整輸出使用者健康資訊"""
    water_info = serializers.SerializerMethodField()
    calories_info = serializers.SerializerMethodField()
    exercise_info = serializers.SerializerMethodField()

    def get_water_info(self, obj):
        user_id = obj[0] ; status=obj[1]
        ob = daily_water.objects
        water_data = self.__status(ob,status,user_id)
        serializer = DailyWaterSerializer(water_data, many=True)
        # print(serializer.data)
        return serializer.data

    def get_calories_info(self, obj):
        user_id = obj[0] ; status=obj[1]
        ob = daily_calories.objects
        calories_data = self.__status(ob,status,user_id)
        serializer = DailyCaloriesSerializer(calories_data, many=True)
        return serializer.data

    def get_exercise_info(self, obj):
        user_id = obj[0] ; status=obj[1]
        ob = daily_exercise.objects
        exercise_data = self.__status(ob,status,user_id)
        serializer = DailyExerciseSerializer(exercise_data, many=True)
        return serializer.data

    def __status(self,filter_ob,status,uid):
        """依照狀況給予參數"""
        from datetime import datetime , timedelta
        if status == 1:
            # now
            now_date = datetime.now().date()
            return filter_ob.filter(time__range=(now_date, now_date+timedelta(days=1)),uid = uid)

        elif status == 2:
            # week
            pass
            
            
        elif status == 3:
            # month
            pass

        elif status == 4:
            # year
            pass

        elif status == 5 :
            # all 
            return filter_ob.filter(uid=uid)

        else:
            raise serializers.ValidationError("query is not accepted or None")
