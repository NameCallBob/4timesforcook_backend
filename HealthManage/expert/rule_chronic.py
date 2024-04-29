from experta import *


class SymptonFact(Fact):
    """症狀（慢性病）"""
    pass

class ChronicRecipeParmasRules(KnowledgeEngine):
    """
    依照慢性病給予其食譜的參數
    """
    def __makeRespose(self,target):
        """console其找到的規則及結果，查看規則是否有正常運作"""
        print(f"找到結果：{target}")

    @Rule(SymptonFact(
            name=P(
                lambda x : len(
                    set(["hypertension","diabetes","heart disease","chronic lung disease"]) & set(x)
                    ) >= 1
    )))
    def DASHdiet(self):
        """
        DASH飲食的六大原則：

        1.主食選擇全穀雜糧類：建議選用未精製、含麩皮的全穀類或根莖類（例如糙米、燕麥），取代精製過的白飯、白麵製品，以獲得豐富的膳食纖維。
        2.大量蔬菜、適量水果：攝取豐富的鎂、鉀離子，特別是深綠色蔬菜如菠菜、空心菜等。
        3.選擇低脂奶類：攝取豐富的鈣質，例如低脂優格、起司、優酪乳。
        4.蛋白質以白肉為主：選擇魚肉、雞、鴨等家禽類，或是黃豆、毛豆等植物性蛋白質，減少攝取紅肉和內臟。
        5.吃堅果、用好油：攝取不飽和脂肪酸，例如腰果、核桃，並使用橄欖油、沙拉油等植物油。
        """

        self.__makeRespose("DASH飲食")
        self.res = {
            "tags":["hypertension","diabetes","heart disease","chronic lung disease","health"],
            "ingredients":[
                'oats','brown rice','low fat milk','fish','chicken','nut','olive oil'
                ]
        }


    def mediterranean_diet(self):
        """地中海飲食"""
        self.__makeRespose("地中海飲食")
        self.res = {
            "tags":["health"],
            "ingredients":[
                'Brown rice', 'oats', 'wheat', 'barley', 'rye', #主食
                'Spinach', 'carrots', 'beetroot', 'broccoli', 'kale', 'tomatoes', #蔬菜
                'Basil','rosemary', 'ginger', 'garlic', 'chilli', #香料
                'Almonds', 'walnuts', 'sesame seeds', 'flax seeds', 'chia seeds', #堅果和種子
                'Black beans', 'mung beans', 'red beans', 'tofu', 'soy mil' #豆類
                ]
        }