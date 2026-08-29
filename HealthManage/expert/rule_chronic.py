"""慢性病規則：依使用者症狀給出建議的食譜查詢參數。

原以 experta 撰寫，因該套件已無法在 Python 3.10+ 執行而改為純 Python。

DASH 飲食六大原則（命中高血壓／糖尿病／心臟病／慢性肺病時採用）：
    1. 主食選擇未精製全穀雜糧類（糙米、燕麥）。
    2. 大量蔬菜、適量水果，攝取鎂與鉀。
    3. 選擇低脂奶類補充鈣質。
    4. 蛋白質以白肉與植物性蛋白為主，減少紅肉與內臟。
    5. 吃堅果、用好油（橄欖油等不飽和脂肪酸）。
"""

DASH_TRIGGERS = {"hypertension", "diabetes", "heart disease",
                 "chronic lung disease"}

DASH_DIET = {
    "tags": ["hypertension", "diabetes", "heart disease",
             "chronic lung disease", "health"],
    "ingredients": ['oats', 'brown rice', 'low fat milk', 'fish',
                    'chicken', 'nut', 'olive oil'],
}

MEDITERRANEAN_DIET = {
    "tags": ["health"],
    "ingredients": [
        'Brown rice', 'oats', 'wheat', 'barley', 'rye',                     # 主食
        'Spinach', 'carrots', 'beetroot', 'broccoli', 'kale', 'tomatoes',   # 蔬菜
        'Basil', 'rosemary', 'ginger', 'garlic', 'chilli',                  # 香料
        'Almonds', 'walnuts', 'sesame seeds', 'flax seeds', 'chia seeds',   # 堅果種子
        'Black beans', 'mung beans', 'red beans', 'tofu', 'soy milk',       # 豆類
    ],
}


def diet_for_symptoms(symptoms) -> dict:
    """命中任一慢性病 -> DASH 飲食；否則回傳地中海飲食（一般健康取向）。"""
    if symptoms and DASH_TRIGGERS & set(symptoms):
        return dict(DASH_DIET)
    return dict(MEDITERRANEAN_DIET)
