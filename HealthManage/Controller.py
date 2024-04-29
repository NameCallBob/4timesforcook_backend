from Member.models import Health , Prefer , HealthTarget
class Manage:
    """健康管理"""
    def analyze(self,Member_ob):
        """
        分析目前使用者狀況
        Member_ob => uid
        """
        try:
            User_health = Health.objects.getr(uid=Member_ob)
            User_prefer = Prefer.objects.get(uid=Member_ob)
            User_weight = int(User_health.weight)
            User_height = int(User_health.height)
            bmi = self.__bmi(weight=User_weight,height=User_height)
            from HealthManage.expert.run import ruleResult
            target = ruleResult.main(
                type_expert=1,
                data=bmi
            )
            from Member.models import HealthTarget
            from datetime import datetime
            from dateutil.relativedelta import relativedelta
            # 建立
            HealthTarget(
                uid = Member_ob,
                calories_intake = target['calories']*User_weight,
                water_intake = target['water']*User_weight,
                exercise_duration = target['exercise'],
                end_time = datetime.now().date() + relativedelta(months=2)
            ).save()
            return 1
        except Health.DoesNotExist:
            return 0
        except Exception as e :
            print(e)

    def __bmi(self,weight,height):
        """輸出BMI結果"""
        bmi = round(weight / (height ** 2),2)
        return bmi

    def __info(self):
        """輸出使用者營養資訊"""
        pass


class Begin:
    """初始化"""

class Recommand:
    """推薦"""

    def __get(self,):
        pass

class Notice:
    """郵件通知"""

class System:
    """健康系統"""