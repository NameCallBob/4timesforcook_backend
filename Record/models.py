from django.db import models


class Record_Search(models.Model):
    """用於儲存使用者提出查詢的紀錄"""
    # 自動增量的索引欄位
    index = models.AutoField(primary_key=True, unique=True, editable=False)
    ip_address = models.TextField(null=True)
    recordId = models.TextField(null=True)
    searchText = models.TextField(null=True)
    searchEngText = models.TextField(null=True)


class Record_DataChange(models.Model):
    """用於儲存會員的變更紀錄"""
    index = models.AutoField(primary_key=True, unique=True, editable=False)
    ip_address = models.TextField()
    change_date = models.DateTimeField(auto_now_add=True)  # 輸出日期，自動記錄當前時間
    user_id = models.TextField()
    change_type = models.CharField(max_length=50)  # 變更類型，例如新增、修改、刪除
    change_description = models.TextField()  # 變更描述


class Record_Output(models.Model):
    """輸出紀錄"""
    index = models.AutoField(primary_key=True, unique=True, editable=False)
    recordId = models.TextField()
    recipeId = models.TextField()
    output_date = models.DateTimeField(auto_now_add=True)  # 輸出日期，自動記錄當前時間


class Category(models.Model):
    name = models.TextField("問題類別名稱")

    def __str__(self) -> str:
        return self.name


class Question(models.Model):
    """題目資訊"""
    ANSWER = {
        1: "A", 2: "B", 3: "C", 4: "D"
    }
    DIFF = {
        1: "easy", 2: "normal", 3: "hard"
    }
    qid = models.IntegerField("題目編號", primary_key=True)
    cate = models.ForeignKey(Category, on_delete=models.CASCADE)
    content = models.TextField("題目")
    option1 = models.TextField("選項1", null=True)
    option2 = models.TextField("選項2", null=True)
    option3 = models.TextField("選項3", null=True)
    option4 = models.TextField("選項4", null=True)
    difficulty = models.IntegerField("難度", choices=DIFF)
    right_answer = models.IntegerField("正確答案", choices=ANSWER)

    def __str__(self):
        return self.content

class Record_Score(models.Model):
    """記錄使用者分數"""
    answer_id = models.IntegerField("作答者ID")
    score = models.IntegerField("分數")
    is_post_test = models.BooleanField("是否為後側")

class Record_Answer(models.Model):
    """記錄使用者回答"""
    ANSWER = {
        1: "A", 2: "B", 3: "C", 4: "D"
    }
    answer_id = models.ForeignKey(Record_Score, on_delete=models.CASCADE)
    qid = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.IntegerField(choices=ANSWER)
    is_post_test = models.BooleanField("是否為後側", default=False)

    def __str__(self) -> str:
        return f"回答人{self.answer_id},題目id{self.qid}"


class Record_CheckIn(models.Model):
    """使用者打卡機制"""

    qid = models.ForeignKey(Question, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, blank=True)
