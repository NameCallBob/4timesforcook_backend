#  --coding:utf8--**
import pandas as pd
from recipe.models import Recipe_At , Recipe_Ob
import os
class DataBase:
    def __init__(self) -> None:
        """在物件生成時，做什麼事情"""
        pass

    def resource(self):
        """
        資料預處理後結果
        """
        current = os.getcwd()
        try:
            d1 = pd.read_csv(os.path.join(current,"recipe/data/RAW_recipes.csv"))
            d2 = pd.read_csv(os.path.join(current,"recipe/data/Food Ingredients and Recipe Dataset with Image Name Mapping.csv"))
        except FileNotFoundError:
            """only跑該檔案"""
            try:
                d1 = pd.read_csv(os.path.join(current,"RAW_recipes.csv"))
                d2 = pd.read_csv(os.path.join(current,"Food Ingredients and Recipe Dataset with Image Name Mapping.csv"))
            except FileNotFoundError:
                r = os.path.join(current,"recipe/data")
                raise FileNotFoundError(f"請確認是否有食譜檔案在資料夾中，路徑為下{r}")

        return d1 , d2

    def info(self):
        """
        Food Ingredients and Recipe Dataset with Image Name Mapping.csv
        """
        data = pd.read_csv("./Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
        print("-"*50)
        print("資料表:Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
        print(f"本資料集大小為{data.shape}")
        print(f"其欄位:{data.columns.tolist()}")
        print("第一筆資料如下")
        print(data.head(1))

        """
        表格結構：
        ----------
        Unnamed: 0： 可能是索引列，不包含實際的資訊。
        Title： 食譜標題。
        Ingredients： 食材清單。
        Instructions： 食譜製作步驟。
        Image_Name： 食譜相關圖片的檔名。
        Cleaned_Ingredients： 已經清理過的食材資訊。
        資料內容：
        ----------
        Title 和 Image_Name： 提供了食譜的名稱和相應的圖片檔名。
        Ingredients 和 Cleaned_Ingredients： 分別提供了原始和清理過的食材資訊。
        Instructions： 包含了製作食譜的步驟。
        使用性質：
        ----------
        可以通過標題快速查找特定食譜。
        食材和步驟的資訊可以用於系統的呈現和查詢功能。
        潛在改進：
        ----------
        可能需要進一步的資料清理，確保資訊的一致性和完整性。
        如果需要支援多語言，可能需要擴充語言支援。
        """
        print("-"*50)

        print("資料表:Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
        data1 = pd.read_csv("/Users/apple/Desktop/Code/Project/KBQA_Bert__RecipeRecommendations/backend/Meibuy/backend/recipe/data/RAW_recipes.csv")
        print(f"本資料集大小為{data1.shape}")
        print(f"其欄位:{data1.columns.tolist()}")
        print("第一筆資料如下")
        print(data1.head(1))

        print("-"*50)

    def know_value(self):
        """
        得取欄位的值
        tags、ingredients、minutes

        Processing Threads: 100%|██████████| 3/3 [02:27<00:00, 49.15s/it]
        為處理時間!
        """
        from threading import Thread ; from tqdm import tqdm
        t1 = Thread(target=self.find_unqiue_value,args=("tags",))
        t2 = Thread(target=self.find_unqiue_value,args=("ingredients",))
        t3 = Thread(target=self.find_unqiue_value,args=("minutes",))
        threads = [t1, t2, t3]
        # 使用 tqdm 顯示進度條
        with tqdm(total=len(threads), desc="Processing Threads") as pbar:
            for t in threads:
                t.start()

            for t in threads:
                t.join()
                pbar.update(1)

        # 將檔案一進行
    def find_unqiue_value(self,index):
        """找欄位的單一值"""
        import json , ast
        r1, r2 = self.resource()
        value = []
        if index == "minutes":
            for i , row in r1.iterrows():
                value.append(row[index])
                value = set(value)
                value = list(value)
        else:

            for i,row in r1.iterrows():
                try:
                    if row[index] is not None and row[index] != "":
                        tmp = row[index]
                        tmp_r = value.copy()
                        if tmp is not None:
                            tmp_r.extend(ast.literal_eval(tmp))
                        tmp_r = set(tmp_r)
                        value = list(tmp_r)
                    else:
                        print(f"食譜ID:{row['id']}，其{index}為None或空字串")
                except json.JSONDecodeError as e :
                    print(f"json讀取失敗，該值為{row[index]}，其食譜ID為{row['id']}，{e}")
                    raise SystemError("出錯，終止")
                except Exception as e:
                    raise(e)
                    continue

        print("找尋完成!")
        print("-"*50)
        print(f"欄位{index}的值如下")
        print(value[0:5])
        print("END")
        print("_"*50)
        file_name = f"{index}_U.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(str(value))
        print("DONE")
        return value

    def for_ing(self):
        """
        警告:此為測試程式

        用於輸出出現次數前200的食材
        """
        with open("./ingredients_U.txt", 'r', encoding='utf-8') as file:
            a = file.read()
            import ast
            import pandas as pd
            a = ast.literal_eval(a)
            res = []
            for i in a:
                r = i.split(" ")
                res.extend(r)
            res = pd.DataFrame(res)
            res.value_counts()[0:200].to_csv("ing_200.csv",index=True)








class Trans_db(DataBase):
    """將原資料進行轉換"""
    def trans(self):
        """將原資料庫資料進行轉換!"""
        d1 , d2 = super().resource()
        data = d1
        # print(d1)
        from threading import Thread
        t1 = Thread(target=self.__toObject,args=(data,))
        t2 = Thread(target=self.__toAttribute,args=(data,))
        t1.start() ; t2.start()
        print("處理結束已將資料存於資料庫")
    def __toObject(self, data):
        for index, row in data.iterrows():
            Recipe_Ob.objects.create(
                rid=row['id'],
                name=row['name'],
                tags=row['tags'],
                steps=row['steps'],
                description=row['description'],
                ingredients=row['ingredients']
            ).save()
        print('O_complete')

    def __toAttribute(self, data):
        for index, row in data.iterrows():
            Recipe_At.objects.create(
                rid=row['id'],
                minutes=row['minutes'],
                nutrition=row['nutrition'],
                n_steps=row['n_steps'],
                n_ingredients=row['n_ingredients']
            ).save()
        print("A_complete")

if __name__ == "__main__":
    # DataBase().info()
    # Trans_db().trans()
    DataBase().know_value()
    DataBase().for_ing()
