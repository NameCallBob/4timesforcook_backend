from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.response import Response
from HealthManage.serializer import *

from HealthManage.models import *

class DailyViewsets(ViewSet):
    """記錄使用者每天攝取或運動量"""
    @action(methods=['get'],permission_classes = [IsAuthenticated] , detail=False)
    def Personal(self,request):
        """得取目前使用者的紀錄"""
        from Member.models import Member
        uid = Member.objects.get(uid=request.user.uid)
        serializer = UserDailyInfoSerializer([uid,1])
        res = self.__sum(uid,serializer.data)
        return Response(data=res,status=200)

    @action(methods=['post'],permission_classes = [IsAuthenticated] , detail=False)
    def input_water(self,request):
        """使用者新增攝取水的紀錄"""
        uid = request.user.uid
        if not self.__check(request_data=request.data,needed_key=['water']):
            return Response(status=400,data="未依照要求傳輸特定檔案,key=>water")

        serializers = DailyWaterSerializer(data=request.data, partial=True)
        if serializers.is_valid():
            if serializers.create(uid,request.data):
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
                return Response(status=200,data="ok")
            else:
                return Response(status=400,data=serializers.errors)
        else:
            return Response(status=400,data=serializers.errors)

    @action(methods=['get'],permission_classes = [IsAuthenticated] , detail=False) 
    def week_record(self,request):
        """使用者的計算輸入狀況"""
        # 使用函式取得一週的日期
        current_week_dates = self.__get_current_week_dates() ; week_date=[]
        # 列印出一週的日期
        for date in current_week_dates:
            week_date.append(date.strftime("%Y-%m-%d"))
        pass


    def __check(self,request_data,needed_key):
        """檢查是否含有特定詞彙"""
        required_fields = needed_key  
        missing_fields = [field for field in required_fields if field not in request_data]
        if len(missing_fields) == 0:
            return True
        else:
            return False
        
    def __sum(self,uid,serializer_data):
        """加總目前使用者之填寫紀錄並與目標進行結合"""
        water = 0 ; calories = 0 ; exercise = 0 
        print(serializer_data)
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
        from Member.models import HealthTarget
        ob = HealthTarget.objects.get(uid=uid)
        
        return {
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
    
    def __get_current_week_dates():
        from datetime import datetime,timedelta
        # 取得當天日期
        today = datetime.today()
        # 找出當天是一週的第幾天 (0 表示星期一，1 表示星期二，以此類推)
        day_of_week = today.weekday()
        # 計算當天與一週的第一天的差距
        days_to_subtract = day_of_week
        # 計算一週的第一天
        start_of_week = today - timedelta(days=days_to_subtract)
        # 建立一個空的列表來存放一週的日期
        week_dates = []
        # 透過迴圈取得整個週期的日期
        for i in range(7):
            # 將當天加入列表
            week_dates.append(start_of_week + timedelta(days=i))
        # 回傳一週的日期列表
        return week_dates