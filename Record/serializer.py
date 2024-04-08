from rest_framework import serializers
from Record.models import Question, Record_Answer


class Question_output_Serializer(serializers.ModelSerializer):
    """問題專用序列化"""
    class Meta:
        model = Question
        fields = ['qid', 'content', 'option1', 'option2', 'option3', 'option4']


class QuestionSerializer(serializers.Serializer):
    cate = serializers.CharField(max_length=30)
    content = serializers.CharField(max_length=150)
    option1 = serializers.CharField(max_length=50)
    option2 = serializers.CharField(max_length=50)
    option3 = serializers.CharField(max_length=50)
    option4 = serializers.CharField(max_length=50)
    difficulty = serializers.CharField(max_length=20)
    right_answer = serializers.CharField(max_length=1)

    def create(self, validated_data):
        try:
            qid = "Q{0:05d}".format(Question.objects.all().count())
            print(f"編號：{qid}")
            Question.objects.create(
                qid=qid,
                cate=validated_data['cate'],
                content=validated_data['content'],
                option1=validated_data['option1']
            )
            return super().create(validated_data)
        except serializers.ValidationError:
            raise serializers.ValidationError(e)


class AnswerSerializer(serializers.Serializer):
    """使用者答覆序列化"""
    qid = serializers.IntegerField()
    answer = serializers.CharField(max_length=1)
    is_post_test = serializers.BooleanField()

    def create(self, validated_data):
        try:
            answer_id = len(Record_Answer.objects.values_list(
                'answer_id', flat=True).distinct())+1
            for i in validated_data:
                i['answer_id'] = answer_id
                Record_Answer.objects.create(i).save()
            return True
        except Exception as e:
            raise serializers.ValidationError(e)
