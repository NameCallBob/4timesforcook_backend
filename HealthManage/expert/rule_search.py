"""搜尋參數規則：把前端的健康標籤轉成食譜查詢條件。

原以 experta 撰寫，因該套件已無法在 Python 3.10+ 執行而改為純 Python 對照表。
未知或空白的查詢回傳 None，由呼叫端決定如何處理。
"""

# 前端標籤 -> 資料庫 tags 欄位要比對的內容
TAG_QUERIES = {
    "alcohol-free": "non-alcoholic",
    "low-calories": "low-calories",
    "low-calorie": "low-calories",
    "low-protein": "low-protein",
    "high-protein": "high-protein",
    "low-sodium": "low-sodium",
    "low-cholesterol": "low-cholesterol",
    "gluten-free": "gluten-free",
}


def params_for_query(query):
    """回傳查詢條件 dict，查無對應時回傳 None。"""
    if not isinstance(query, str):
        return None
    content = TAG_QUERIES.get(query.strip().lower())
    if content is None:
        return None
    return {"index": "object", "columns": "tags", "content": content}
