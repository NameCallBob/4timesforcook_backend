# django
from django.db.models import Q
from recipe.models import Recipe_At , Recipe_Ob

class DB_search:

    def __query_set(self,data:dict):
        """搜尋參數設置"""
        # 實體參數
        queryA = Q()
        # 屬性參數
        queryB = Q()

        # 實體條件判斷
        if data.get("object"):
            d_ob  = data['object']
            if d_ob.get("name"):
                queryA &= Q(name__icontains=d_ob['name'])
            if d_ob.get("ingredients"):
                queryA &= Q(ingredients__icontains=d_ob['ingredients'])
            if d_ob.get("tags"):
                queryA &= Q(tags__icontains=d_ob['tags'])

        # 屬性條件判斷
        if data.get("Attribute"):
            d_at = data['Attribute']
            if d_at.get('minutes'):
                queryB &= Q(minutes__lte=d_at['minutes'])
            # if d_at.get("nutrition"):
            #     queryB &= Q(nutrition__lte=d_at['nutrition'])
            # 營養數值
            if d_at.get("calories"):
                queryB &= Q(calories__lte=d_at['calories'])
            if d_at.get("fat"):
                queryB &= Q(fat__lte=d_at['fat'])
            if d_at.get("sugar"):
                queryB &= Q(sugar__lte=d_at['sugar'])
            if d_at.get("sodium"):
                queryB &= Q(sodium__lte=d_at['sodium'])
            if d_at.get("protein"):
               queryB &= Q(protein__lte=d_at['protein'])
            if d_at.get("saturated_fat"):
                queryB &= Q(saturated_fat__lte=d_at['saturated_fat'])
            if d_at.get("carbohydrates"):
                queryB &= Q(carbohydrates__lte=d_at['carbohydrates'])
            # 食譜步驟數量
            if d_at.get("n_steps"):
                queryB &= Q(n_steps__lte=d_at['n_steps'])
            if d_at.get("n_ingredients"):
                queryB &= Q(n_ingredients__lte=d_at['n_ingredients'])

        return queryA , queryB

    def __type(self,sentence:str,labels:list):
        """
        將label轉為query
        """
        labels_to_columns = {
        "num": 1,
        "B-ING":"ingredients","B-DIS":"tags","B-NUT":"nutrition",
        "B-ALG":"allergen","B-STP":"step","B-TME":7,
        "B-UDO":"udo","B-TAG":"tags",
        "I-ING":"ingredients","I-TAG":"tags"
        }

        labels_key = labels_to_columns.keys()
        words = sentence.split()
        clean_labels = set([x for x in labels if x != 'O']);
        clean_labels = list(clean_labels)
        print(clean_labels)
        # 若模型有判斷出實體
        if len(clean_labels) == 0:
            # 無實體，隨機給予
            return 0
        else:
            # 有實體
            res={
                "object":{},
                "Attribute":{}
                 }
            # 多實體判別(B、I)
            if ['B-TAG','I-TAG'] in clean_labels:
                res['object']['tags'] = self.__process_sentence(1,words,labels)
            if ['B-ING','I-ING'] in clean_labels:
                res['object']['ingredients'] = self.__process_sentence(0,words,labels)
            # 其他單一實體判別(B)

            # 找到特定標籤的位置
            def find_tag_indices(tags, target_tag):
                return [i for i, tag in enumerate(tags) if tag == target_tag]

            # 找到特定標籤對應的單詞
            def find_tag_words(words, tags, target_tag):
                tag_indices = find_tag_indices(tags, target_tag)
                return [words[i] for i in tag_indices]

            # 要找的標籤列表
            target_tags = [x for x in labels if x not in ['I-TAG','I-ING']]

            for target_tag in target_tags:
                # 找到特定標籤的位置
                tag_indices = find_tag_indices(labels, target_tag)
                # 找到特定標籤對應的單詞
                tag_words = find_tag_words(words, labels, target_tag)
                res["object"][labels_to_columns[target_tag]] = tag_words

            print(res)
            return res

    def __process_sentence(self,type:int,words, entities) -> list:
            """
            判別是否有B、I的實體
            @type -> 實體標記的類型
            @words -> 句子拆分後的單字
            @entities -> 實體標記
            """
            sentence = []
            check = [["B-ING","I-ING"],['B-TAG',"I-TAG"]]
            for word, entity in zip(words, entities):
                if entity == check[type][0]:
                    sentence.append(word)
                elif entity == check[type][1] and sentence:
                    sentence[-1] += ' ' + word
                else:
                    sentence.append('O')
            sentence = set(sentence);sentence=list(sentence)
            return sentence

    def __process_UserQuery(self,data,user_query):
        """
        處理使用給予的條件式判斷
        @data -> 先前處理的使用者參數
        @user_query -> 使用者輸入的參數
        """
        if user_query == []:
            # 如果使用者沒有輸入任何參數，直接回傳原本的參數
            return data
        data_object = data['object'] ; data_attr = data['Attribute']
        # 前端的制定的參數
        # 食譜標籤
        tags = [
            # 料理風格
            "japanese","chinese","korean","spain","italian","'german","mexico"
        ]
        time = [
            # 做飯時間
            "15-minutes-or-less","30-minutes-or-less","60-minutes-or-less",
        ]
        # 健康選擇
        health = [
        'alcohol-free','low-calorie','low-protein',
        'high-protein','gluten-free''low-sodium','low-cholesterol'
        ]
        for i in user_query:
            # 食譜標籤
            if i in tags:
                if i not in data_object['tags']:
                    data_object['tags'].append(i)
            # 食譜時間
            elif i in time:
                data_attr['minutes'] = int(i[0:2])
            elif i == "time-to-make":
                data_attr['minutes_up'] = 60
            # 健康因素
            elif i in health :
                pass

    def run(self,sentence,labels,user_query):
        """
        sentence -> 以翻譯過的句子
        labels -> 模型預測的label
        user_query -> 使用者點選的條件式
        """
        try:
            # 如果有翻譯英文，代表模型有預測，從中拿取參數
            data={
                "object":{},
                "Attribute":{}
                 }
            if sentence != "":
                data = self.__type(sentence,labels)

            data = self.__process_UserQuery(data,user_query)

            querysetA , querysetB = self.__query_set(data)

            # 實體搜尋
            resultsA = Recipe_Ob.objects.filter(querysetA)

            # 屬性搜尋
            resultsB = Recipe_At.objects.filter(querysetB)

            # 合併結果
            final_results = resultsA.filter(rid__in=resultsB.values('rid'))

            # 按照分數排序
            final_results = final_results[0:3]
            res_id = [result.rid for result in final_results]

            if res_id == []:
                res_id = [47366,67547,23850]
            return res_id

        except Exception as e :
            print(f"KBQA輸出出現問題，問題如下:{e}")
