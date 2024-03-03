from Member.models import Health
class Manage:
    """健康管理"""
    def analyze(Member_ob):
        """分析目前使用者狀況"""
        try:
            chronic = Health.objects.filter(uid=Member_ob)
            
        except Health.DoesNotExist:
            return 0 
        except Exception as e :
            print(e)
            
        
class Begin:
    """初始化"""

class Recommand:
    """推薦"""

class Notice:
    """郵件通知"""

class System:
    """健康系統"""