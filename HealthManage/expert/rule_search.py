from experta import *

class SearchQuery(Fact):
    """使用者給予的搜尋參數"""
    pass

class SearchParamsRule(KnowledgeEngine):
    """
    依照參數給予相對應的結果
    """
    def __makeRespose(self,target):
        """console其找到的規則及結果，查看規則是否有正常運作"""
        print(f"找到結果：{target}")

    @Rule(
        SearchQuery(query="alcohol-free")
    )
    def alcohol_free(self):
         self.res = {
            "index":"object",
            "columns":"tags",
            "content":"non-alcoholic"
        }

    @Rule(
        SearchQuery(query = "low-calories")
    )
    def low_calories(self):
         self.res = {
            "index":"object",
            "columns":"tags",
            "content":"low-calories"
        }

    @Rule(
        SearchQuery(query = "low-protein")
    )
    def low_protein(self):
        self.res = {
            "index":"object",
            "columns":"tags",
            "content":"low-protein"
        }

    @Rule(
        SearchQuery(query = "low-sodium")
    )
    def low_sodium(self):
        self.res = {
            "index":"object",
            "columns":"tags",
            "content":"low-sodium"
        }

    @Rule(
        SearchQuery(query = "low-cholesterol")
    )
    def low_cholesterol(self):
        self.res = {
            "index":"object",
            "columns":"tags",
            "content":"low-cholesterol"
        }

    @Rule(
        SearchQuery(query = "high-protein")
    )
    def high_protein(self):
        """高蛋白"""
        self.res = {
            "index":"object",
            "columns":"tags",
            "content":"high-protein"
        }


    @Rule(
        SearchQuery(query = "gluten-free")
    )
    def gluten_free(self):
         self.res = {
            "index":"object",
            "columns":"tags",
            "content":"gluten-free"
        }

    @Rule()
    def else_rule(self):
        # 在所有其他規則都不符合時執行的動作
        self.res=None
        self.__makeRespose("無")