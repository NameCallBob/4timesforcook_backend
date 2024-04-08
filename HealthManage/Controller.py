from Member.models import Health , Prefer , HealthTarget
class Manage:
    """健康管理"""
    def analyze(Member_ob):
        """
        分析目前使用者狀況
        Member_ob => uid
        """
        try:
            chronic = Health.objects.filter(uid=Member_ob)
            prefer = Prefer.objects.filter(uid=Member_ob)
            
            
        except Health.DoesNotExist:
            return 0 
        except Exception as e :
            print(e)

    def __bmi(weight,height):
        """輸出BMI結果"""
        bmi = round(weight / (height ** 2),2)
        lim = [18.5,24,27,30,35]
        label = ['過輕','標準','過重','輕度肥胖','中度肥胖']
        num = 0 
        for i in lim:
            if bmi < i:
                return label[num]
            num += 1 
        return '重度肥胖'

    def __info():
        """輸出使用者營養資訊"""
        


class Begin:
    """初始化"""

class Recommand:
    """推薦"""
    
    def __get(self,)

class Notice:
    """郵件通知"""

class System:
    """健康系統"""