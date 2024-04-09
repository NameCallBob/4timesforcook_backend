# inner
# from recipe.data.data_use import DataBase
from recipe.models import Recipe_At , Recipe_Ob
# django
from django.db.models import Q

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
            if d_ob.get("ingredient"):
                queryA &= Q(ingredients__icontains=d_ob['ingredient'])
            if d_ob.get("tags"):
                queryA &= Q(tags__icontains=d_ob['tags'])

        # 屬性條件判斷
        if data.get("Attribute"):
            d_at = data['Attribute']
            if d_at.get('minutes'):
                queryB &= Q(minutes__lte=d_at['minutes'])
            if d_at.get("nutrition"):
                queryB &= Q(nutrition__lte=d_at['nutrition'])
            if d_at.get("n_steps"):
                queryB &= Q(n_steps__lte=d_at['n_steps'])
            if d_at.get("n_ingredients"):
                queryB &= Q(n_ingredients__lte=d_at['n_ingredients'])

        return queryA , queryB

    def run(self,data):
        try:
            querysetA , querysetB = self.__query_set(data)

            # 實體搜尋
            resultsA = Recipe_Ob.objects.filter(querysetA)

            # 屬性搜尋
            resultsB = Recipe_At.objects.filter(querysetB)

            # 合併結果
            final_results = resultsA.filter(rid__in=resultsB.values('rid'))

            # 按照分數排序
            final_results = final_results[0:5]
            res_id = [result.id for result in final_results]

            return res_id
        except Exception as e :
            print(f"KBQA輸出出現問題，問題如下:{e}")
            return 0

