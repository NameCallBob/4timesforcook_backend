"""飲食目標規則：依 BMI 給出每日建議攝取/運動基準。

原本以 experta 撰寫，但 experta（相依 frozendict 1.2）在 Python 3.10+
已無法載入（collections.Mapping 於 3.10 移除），整個模組形同無法執行。
規則本身只是一組區間對應，改以純 Python 實作，行為與原規則相同且可測試。

回傳值語意：
    calories / water 為「每公斤體重」的係數，由呼叫端乘上體重；
    exercise 為每週建議運動量（分鐘）。
"""

# (下界, 上界, 分類名稱, 結果)；上界為 None 代表無上限
BMI_RULES = [
    (None, 18.5, "過輕", {"calories": 35, "water": 30, "exercise": 1000}),
    (18.5, 24, "標準", {"calories": 30, "water": 30, "exercise": 1000}),
    (24, 27, "過重", {"calories": 45, "water": 30, "exercise": 1000}),
    (27, 30, "輕度肥胖", {"calories": 40, "water": 30, "exercise": 1000}),
    (30, 35, "中度肥胖", {"calories": 35, "water": 30, "exercise": 1000}),
    (35, None, "重度肥胖", {"calories": 35, "water": 30, "exercise": 1000}),
]


def classify_bmi(bmi: float) -> str:
    """回傳 BMI 對應的分類名稱。"""
    for low, high, label, _ in BMI_RULES:
        if (low is None or bmi >= low) and (high is None or bmi < high):
            return label
    raise ValueError(f"無法分類的 BMI：{bmi}")


def target_for_bmi(bmi: float) -> dict:
    """回傳 BMI 對應的每日目標係數。"""
    for low, high, _, result in BMI_RULES:
        if (low is None or bmi >= low) and (high is None or bmi < high):
            return dict(result)
    raise ValueError(f"無法分類的 BMI：{bmi}")
