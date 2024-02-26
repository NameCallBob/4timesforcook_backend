from rest_framework import serializers
from Record.models import Question,Record_Answer

class Question_output_Serializer(serializers.ModelSerializer):
    """問題專用序列化"""
    class meta:
        model = Question
        fields = ["qid","content","option","difficulty"]

class AnswerSerializer(serializers.Serializer):
    """使用者答覆序列化"""
    qid = serializers.IntegerField()
    answer = serializers.CharField(max_length=1)
    is_post_test = serializers.BooleanField()

    def create(self, validated_data):
        try:
            answer_id = len(Record_Answer.objects.values_list('answer_id', flat=True).distinct())+1
            for i in validated_data:
                    i['answer_id'] = answer_id
                    Record_Answer.objects.create(i).save()
            return True
        except Exception as e :
            raise serializers.ValidationError(e)
