"""
與翻譯至資料庫其程式碼相同
"""
import pandas as pd
import os
from deep_translator import GoogleTranslator
import nltk

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
            except FileNotFoundError as r :
                # 請後端自己調整
                raise FileNotFoundError(f"請確認是否有食譜檔案在資料夾中，路徑為下{r}")

        return d1 , d2

def translatelotWord(text):
    """大量文本翻譯_拆解"""

    if type(text) == list:
        # 型態為矩陣去做翻譯
        res=[]
        for i in text:
            x = nltk.tokenize.sent_tokenize(i)
            for sentence in x :
                try:
                    tmp = GoogleTranslator(
                    source="english",target="zh-TW"
                    ).translate(sentence)
                    res.append(tmp)
                except Exception as e:
                    print(e)
                    res.append("字數過多，無法呈現")
        return res

    elif type(text) == str:
        # 型態為名字去做翻譯
        tmp = GoogleTranslator(
            source="english",target="zh-TW"
        ).translate(text)
        return tmp



def translate_to_chinese(type,text):
        """翻譯文字"""
        if type == 1 or type == 3:
            # 字比較少
            try:
                if text == "" or text == "nan":
                    return "沒有文字介紹喔!"
                else:
                    return GoogleTranslator(
                        source="english",target="zh-TW"
                    ).translate(text)
            except Exception as e :
                print(f"訊息出錯{e}")
                return translatelotWord(text)
        else:
            tmp = []
            for i in eval(text):
                tmp.append(translatelotWord(i))
            return tmp

def nullCheck(data):
    """發現到有些資料會出現null的狀況，先進行判斷後再繼續"""
    if data == None or data == "":
        return  "no information!"
    return data

def oneThread(d1,file_num):
    #  僅使用單一執行跑翻譯
    #  測試次數(確認是否正常運作)
    test = 0
    # 翻成中文的必要資料
    rid = []
    name = []
    tags = []
    steps = []
    description =[]
    ingredients = []
    # 進度條
    from tqdm import tqdm
    num_all = int(d1.shape[0]) + 1
    progress_bar = tqdm(total=num_all, desc=f"第{file_num}個執行緒進度", unit="筆")

    # pandas
    for index, row in d1.iterrows():
        trans_name = nullCheck(translate_to_chinese(1,row['name']))
        trans_tags = nullCheck(translate_to_chinese(2,row['tags']))
        trans_step = nullCheck(translate_to_chinese(4,row['steps']))
        trans_des = nullCheck(translate_to_chinese(3,row['description']))
        trans_ing = nullCheck(translate_to_chinese(6,row['ingredients']))

        rid.append(row['id'])
        name.append(trans_name)
        tags.append(trans_tags)
        steps.append(trans_step)
        description.append(trans_des)
        ingredients.append(trans_ing)

        progress_bar.update(1)
        if test == 10:
            break




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

    current = os.getcwd()
    new_data.to_csv(os.path.join(current,"recipe","Sourcedata","translate_res",f"trans_db{file_num}.csv"))
    progress_bar.update(1)
    progress_bar.close()



def datasplit():
    d1,d2 = DataBase().resource()
    chunk_size = d1.shape[0]//50
    data_num = [0]
    for i in range(1,51):
        if i == 50 :
            data_num.append(d1.shape[0])
        else:
            data_num.append(chunk_size*i)

    chunks = []
    for i in range(len(data_num)-1):
         chunks.append(d1.iloc[data_num[i]:data_num[i+1]])
    return chunks

def multiThread():
    """
    發現單一執行，跑的速度會處理到20天

    因此將要翻譯的檔案分為20份進行翻譯及處理
    """
    data = datasplit()
    # 使用多執行緒進行翻譯
    import threading
    threads = []
    for i in range(len(data)):
        thread = threading.Thread(target=oneThread, args=(data[i],i,))
        thread.start()
        threads.append(thread)
    for i in threads:
        i.join()




if __name__ == "__main__":
    """跑翻譯資料"""
    multiThread()
