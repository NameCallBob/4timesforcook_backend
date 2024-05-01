"""
與翻譯至資料庫其程式碼相同
"""
import pandas as pd
import os

class DataBase:
    """讀取Kaggle資料"""
    def resource(self):
        """
        資料預處理後結果
        """
        current = os.getcwd()
        try:
            # 依照本地進行設計
            d1 = pd.read_csv(os.path.join(current,"data","RAW_recipes.csv"))
            d2 = pd.read_csv(os.path.join(current,"data","Food Ingredients and Recipe Dataset with Image Name Mapping.csv"))
        except FileNotFoundError:
            # 依照django路徑設計
            try:
                d1 = pd.read_csv(os.path.join(current,"recipe/Sourcedata/data/RAW_recipes.csv"))
                d2 = pd.read_csv(os.path.join(current,"recipe/Sourcedata/data/Food Ingredients and Recipe Dataset with Image Name Mapping.csv"))
            except FileNotFoundError:
                # 請後端自己調整
                raise FileNotFoundError(f"請確認是否有食譜檔案在資料夾中，路徑為下{r}")

        return d1 , d2

def translate_to_chinese(type,text):
        """翻譯文字"""
        from deep_translator import GoogleTranslator
        import nltk
        if type in [1,3]:
            # 字比較少
            try:
                if text == "":
                    res="沒有文字介紹喔!"
                else:
                    res =GoogleTranslator(
                        source="english",target="zh-TW"
                        ).translate(text)

            except Exception as e :
                try:
                    res=""
                    x = nltk.tokenize.sent_tokenize(text)
                    for sentence in x :
                                try:
                                        tmp = GoogleTranslator(
                                            source="english",target="zh-TW"
                                            ).translate(sentence)
                                        res += tmp
                                except:
                                    res += ("字數過多，無法呈現")
                except:
                    res = "字數過多，無法呈現"
        else:
            # 字多採分割的方式翻譯
                res = []
                for i in eval(text):
                    # https://stackoverflow.com/questions/70673172/how-to-solve-text-must-be-a-valid-text-with-maximum-5000-character-otherwise-it
                    x = nltk.tokenize.sent_tokenize(i)
                    for sentence in x :
                            try:
                                res.append(
                                    GoogleTranslator(
                                        source="english",target="zh-TW"
                                        ).translate(sentence)
                                    )
                            except:
                                res.append("字數過多，無法呈現")
        return res

def nullCheck(data):
    """發現到有些資料會出現null的狀況，先進行判斷後再繼續"""
    if data == None or data == "":
        return  "no information！"
    return data


if __name__ == "__main__":
    """跑翻譯資料"""
    test = 0
    d1,d2 = DataBase().resource()
    # 翻成中文的必要資料
    rid = []
    name = []
    tags = []
    steps = []
    description =[]
    ingredients = []
    # 進度條
    from tqdm import tqdm
    num_all = int(d1.size//13) + 1
    progress_bar = tqdm(total=num_all, desc="進度", unit="任務")
    test = 0
    # pandas
    for index, row in d1.iterrows():
        rid.append(row['id'])
        name.append(nullCheck(translate_to_chinese(1,row['name'])))
        tags.append(nullCheck(translate_to_chinese(2,row['tags'])))
        steps.append(nullCheck(translate_to_chinese(4,row['steps'])))
        description.append(nullCheck(translate_to_chinese(3,row['description'])))
        ingredients.append(nullCheck(translate_to_chinese(6,row['ingredients'])))
        progress_bar.update(1)

    
    new_data = pd.DataFrame(
         {
              "id":rid,
              "name":name,
              "tags":tags,
              "steps":steps,
              "description":description,
              "ingredients":ingredients,
         }
    )
    new_data.to_csv("./res/trans_db.csv")
    progress_bar.update(1)
    progress_bar.close()
