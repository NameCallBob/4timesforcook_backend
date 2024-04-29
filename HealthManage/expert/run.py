
class ruleResult:
    def __Health(self,bmi):
        """取得Health之結果"""
        from HealthManage.expert.rule_target import HealthyTargetRules,BMI
        engine = HealthyTargetRules()
        engine.reset()
        engine.declare(BMI(bmi=bmi))
        engine.run()
        return engine.res

    def __Chronic(self,symptom:list):
        """取得慢性病之結果"""
        from HealthManage.expert.rule_chronic import ChronicRecipeParmasRules , SymptonFact
        engine = ChronicRecipeParmasRules()
        engine.reset()
        engine.declare(SymptonFact(name = symptom))
        engine.run()

        return engine.res

    def main(self,type_expert,data):
        """Main function"""
        if type(data) == type("123"):
            data = eval(data)

        if type_expert == 1 :
            # User Healthy Target
            return self.__Health(bmi=data)
        elif type_expert == 2:
            # Recipe Chroic Params
            return self.__Chronic(symptom=data)
        else:
            raise KeyError(f"type輸入未知參數，目前開放 1（使用者飲食目標）,2(慢性病食譜參數)．您輸入之參數：{type_expert}")






if __name__ == "__main__":
    print("Test start!")
    res = ruleResult().main(
        type_expert=2,
        data=[]
    )
    print(res)
