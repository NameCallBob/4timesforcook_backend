"""規則系統的統一進入點。

三組規則（飲食目標／慢性病飲食／搜尋參數）各自是純 Python 函式，
這裡保留原本 ``ruleResult().main(type_expert, data)`` 的呼叫介面。
"""
import ast
import logging

from HealthManage.expert.rule_chronic import diet_for_symptoms
from HealthManage.expert.rule_search import params_for_query
from HealthManage.expert.rule_target import classify_bmi, target_for_bmi

logger = logging.getLogger(__name__)

HEALTH_TARGET = 1
CHRONIC_DIET = 2
SEARCH_PARAMS = 3


class ruleResult:
    """規則引擎的門面（facade）。"""

    def __Health(self, bmi):
        """取得飲食目標之結果"""
        bmi = float(bmi)
        logger.debug("BMI %s 分類為 %s", bmi, classify_bmi(bmi))
        return target_for_bmi(bmi)

    def __Chronic(self, symptom):
        """取得慢性病飲食之結果"""
        return diet_for_symptoms(symptom)

    def __Search(self, query):
        """取得使用者查詢參數的結果"""
        return params_for_query(query)

    def main(self, type_expert, data):
        """
        主要跑規則的函式
        @type_expert -> 使用哪一組規則（1 飲食目標 / 2 慢性病飲食 / 3 搜尋參數）
        @data -> 規則所需的參數
        """
        if type_expert == SEARCH_PARAMS:
            # 搜尋參數本身就是字串標籤，不可解析
            return self.__Search(query=data)

        if isinstance(data, str):
            # 資料庫以字串形式保存 list（例如 "['diabetes']"），還原成 Python 物件。
            # 使用 literal_eval 而非 eval，避免執行任意程式碼。
            try:
                data = ast.literal_eval(data)
            except (ValueError, SyntaxError):
                pass

        if type_expert == HEALTH_TARGET:
            return self.__Health(bmi=data)
        if type_expert == CHRONIC_DIET:
            return self.__Chronic(symptom=data)
        raise KeyError(
            "type輸入未知參數，目前開放 1（使用者飲食目標）、2（慢性病食譜參數）、"
            f"3（搜尋參數）。您輸入之參數：{type_expert}")
