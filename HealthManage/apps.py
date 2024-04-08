from django.apps import AppConfig


class HealthmanageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'HealthManage'

class ExpertSystem:
    """此專家系統將依據慢性病以及BMI，輸出推薦他的營養指數"""
    def __init__(self):
        from os import getcwd ; import json
        with open(getcwd()+"/HealthManage/prevent_way/BMI.json", 'r') as f:
            self.rules = json.load(f)

    def getUserTarget(self,UserInfo,bmi):
        """得取資料"""
        data = self.rules['BMI']
        res = []
        # 建議卡路里攝取量
        res.append(int(UserInfo['weight'])*data['base_calories'])
        # 建議水分攝取量
        res.append(data['water'])
        # 建議運動量
        res.append(data['exercise'])
        return res
    
    def getRecipeQuery(self):
        """依照慢性病取得食譜的搜尋資料"""
        pass
        
    