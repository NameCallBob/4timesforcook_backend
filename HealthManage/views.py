from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.response import Response
from HealthManage.serializer import *
from Member.models import InputRecord , HealthTarget ; from Member.serializer import InputRecordSerializer

from HealthManage.models import *

class DailyViewsets(ViewSet):
    """記錄使用者每天攝取或運動量"""
    @action(methods=['get'],permission_classes = [IsAuthenticated] , detail=False)
    def Personal(self,request):
        """得取目前使用者的紀錄"""
        from Member.models import Member
        uid = Member.objects.get(uid=request.user.uid)
        serializer = UserDailyInfoSerializer([uid,1])
        res = self.__sumUserInputRecord(uid,serializer.data)
        return Response(data=res,status=200)
    @action(methods=['get'],permission_classes=[IsAuthenticated],detail=False)
    def recipe(self,request):
        from recipe.models import Recipe_Ob ; from recipe.serializer import RecipeSerializer
        # 隨機排序並取第一筆
        allob = Recipe_Ob.objects.all()
        random_object = allob.order_by('?').first()
        serializer = RecipeSerializer(random_object)
        return Response(status=200,data=serializer.data)

    @action(methods=['post'],permission_classes = [IsAuthenticated] , detail=False)
    def input_water(self,request):
        """使用者新增攝取水的紀錄"""
        uid = request.user.uid
        if not self.__check(request_data=request.data,needed_key=['water']):
            return Response(status=400,data="未依照要求傳輸特定檔案,key=>water")
        serializers = DailyWaterSerializer(data=request.data, partial=True)
        if serializers.is_valid():
            if serializers.create(uid,request.data):
                self.__addInputRecord(0,uid,request)
                return Response(status=200,data="ok")
            else:
                return Response(status=400,data=serializers.errors)
        else:
            return Response(status=400,data=serializers.errors)

    @action(methods=['post'],permission_classes = [IsAuthenticated] , detail=False)
    def input_calories(self,request):
        """使用者新增卡路里的紀錄"""
        uid = request.user.uid
        if not self.__check(request_data=request.data,needed_key=['type','calories']):
            return Response(status=400,data="未依照要求傳輸特定檔案,key=>type,calories")
        serializers = DailyCaloriesSerializer(data=request.data, partial=True)
        if serializers.is_valid():
            if serializers.create(uid,request.data):
                self.__addInputRecord(1,uid,request)
                return Response(status=200,data="ok")
            else:
                return Response(status=400,data=serializers.errors)
        else:
            return Response(status=400,data=serializers.errors)

    @action(methods=['post'],permission_classes = [IsAuthenticated] , detail=False)
    def input_exercise(self,request):
        """使用者新增運動的紀錄"""
        uid = request.user.uid
        if not self.__check(request_data=request.data,needed_key=['strong',"sport_time"]):
            return Response(status=400,data="未依照要求傳輸特定檔案,key=>strong,sport_time")
        serializers = DailyExerciseSerializer(data=request.data, partial=True)
        if serializers.is_valid():
            if serializers.create(uid,request.data):
                self.__addInputRecord(2,uid,request)
                return Response(status=200,data="ok")
            else:
                return Response(status=400,data=serializers.errors)
        else:
            return Response(status=400,data=serializers.errors)

    @action(methods=['get'],permission_classes = [IsAuthenticated] , detail=False)
    def week_record(self,request):
        """使用者的計算輸入狀況"""
        uid = request.user.uid
        # 使用函式取得一週的日期
        current_week_dates = self.__get_current_week_dates() ; week_dates=[]
        # 列印出一週的日期
        for date in current_week_dates:
            week_dates.append(date.strftime("%Y-%m-%d"))
        start_date = week_dates[0];end_date=week_dates[6]

        ob = InputRecord.objects.filter(time__range=(start_date,end_date),uid = uid)
        serializer = InputRecordSerializer(ob,many=True)
        return Response(data=serializer.data,status=200)


    def __check(self,request_data,needed_key):
        """檢查是否含有特定詞彙"""
        required_fields = needed_key
        missing_fields = [field for field in required_fields if field not in request_data]
        if len(missing_fields) == 0:
            return True
        else:
            return False

    def __sumUserInputRecord(self,uid,serializer_data):
        """加總目前使用者之填寫紀錄並與目標進行結合"""
        water = 0 ; calories = 0 ; exercise = 0
        if len(serializer_data['water_info']) != 0:
            for i in serializer_data['water_info']:
                water += int(i["water"])

        if len(serializer_data['calories_info']) != 0 :
            for i in serializer_data['calories_info']:
                calories += int(i['calories'])

        if len(serializer_data['exercise_info']) != 0 :
            for i in serializer_data['exercise_info']:
                tmp = {
                    1:2,
                    2:5,
                    3:7
                }
                exercise += (int(i['sport_time']) * tmp[i['strong']])

        ob = HealthTarget.objects.get(uid=uid)
        week_data = self.__get_current_week_dates(uid)
        return {
            "week":week_data,
            "record":{
                "water_target":ob.water_intake,
                'water_remain':ob.water_intake-water,
                'water_now':water,
                "calories_target":ob.calories_intake,
                'calories_remain':ob.calories_intake-calories,
                "calories_now":calories,
                "exercise_target":ob.exercise_duration,
                "exercise_remain":ob.exercise_duration-exercise,
                "exercise_now":exercise
            }
            }

    def __get_current_week_dates(self,uid_ob):
        """確認使用者的填寫紀錄"""
        from datetime import datetime,timedelta
        today = datetime.today()
        day_of_week = today.weekday()
        days_to_subtract = day_of_week
        start_of_week = today - timedelta(days=days_to_subtract)
        week_dates = []
        res = {}
        for i in range(7):
            week_dates.append(start_of_week + timedelta(days=i))
        data = InputRecord.objects.filter(date__range=(week_dates[0],week_dates[6]),uid=uid_ob)
        target = HealthTarget.objects.get(uid=uid_ob)
        if data.count() == 0 :
            for i in range(1,8):
                res[i] = 0
        else:
            length = 1
            for i in week_dates:
                tmp_ob = data.filter(date=i)
                if tmp_ob.count() == 1 :
                    if (\
                    # 使用者離目標差距小 -> 通過
                    (target.calories_intake-tmp_ob[0].calories_sum) < 500 and \
                    (target.water_intake - tmp_ob[0].water_sum) < 500 and  \
                    (target.exercise_duration - tmp_ob[0].exercise_sum < 300) \
                    ):
                        if tmp_ob[0].calories_sum < -200 :
                            res[length] = 3
                        else:
                            res[length] = 2
                    else:
                        res[length] = 2
                else:
                    res[length] = 1
                length += 1
        return res
    def __addInputRecord(self,type,uid,request):
        """新增或更改 使用者輸入"""
        try:
            from datetime import datetime
            today = datetime.today()
            uid = Member.objects.get(uid=uid)
            ob = InputRecord.objects.get(uid=uid,date=today)
        except InputRecord.DoesNotExist:
            InputRecord.objects.create(
                        date=today,
                        calories_sum=0,
                        water_sum=0,
                        exercise_sum=0,
                        status=1,
                        uid = uid
            ).save()
        except Exception as e:
            return Response(status=400,data=e)
        finally:
            ob = InputRecord.objects.get(uid=uid,date=today)
            if type == 0 :
                ob.water_sum = ob.water_sum + int(request.data['water'])
            elif type == 1 :
                ob.calories_sum = ob.calories_sum + int(request.data['calories'])
            elif type == 2 :
                d = {1:2,2:5,3:7}
                strong = d[request.data['strong']]
                ob.exercise_sum = ob.exercise_sum + int(strong*request.data['sport_time'])
            ob.save()
            return Response(status=200,data="ok")



