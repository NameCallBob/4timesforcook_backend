from experta import *

class BMI(Fact):
    pass

class HealthyTargetRules(KnowledgeEngine):
    """
    飲食目標建制，主要依照BMI進行設計
    """
    def __makeRespose(self,target):
        print(f"找到結果：{target}")

    @Rule(BMI(bmi=P(lambda x: x < 18.5)))
    def underweight(self):
        """過輕"""
        self.__makeRespose("過輕")
        self.res =  (
            {"calories":35,"water":30,"exercise":1000}
        )

    @Rule(BMI(bmi=P(lambda x: 18.5 <= x < 24)))
    def standard(self):
        self.__makeRespose("標準")
        self.res = (
            {"calories":30,"water":30,"exercise":1000}
        )
    @Rule(BMI(bmi=P(lambda x: 24 <= x < 27)))
    def overweight(self):
        self.__makeRespose("過重")
        self.res = (
            {"calories":45,"water":30,"exercise":1000}
        )

    @Rule(BMI(bmi=P(lambda x: 27 <= x < 30)))
    def mildlyObese(self):
        self.__makeRespose("輕度肥胖")
        self.res = (
            {"calories":40,"water":30,"exercise":1000}
        )
    @Rule(BMI(bmi=P(lambda x: 30 <= x < 35)))
    def moderatelyObese(self):
        self.__makeRespose("中度肥胖")
        self.res = (
            {"calories":35,"water":30,"exercise":1000}
        )
    @Rule(BMI(bmi=P(lambda x: x >= 35)))
    def severelyObese(self):
        self.__makeRespose("重度肥胖")
        self.res = (
            {"calories":35,"water":30,"exercise":1000}
        )
    