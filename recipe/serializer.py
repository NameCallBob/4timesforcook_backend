from rest_framework import serializers
from recipe.models import Recipe_Ob,Recipe_At

class Recipe_AtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe_At
        fields = ['minutes', 'nutrition', 'n_steps', 'n_ingredients']

class RecipeSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()
    class Meta:
        model = Recipe_Ob
        fields = "__all__"

    def get_attributes(self, obj):
        # 在這裡取得 Recipe_At 的屬性，你可以根據實際需求進行過濾
        recipe_at_instance = Recipe_At.objects.get(rid=obj.rid)
        attributes_serializer = Recipe_AtSerializer(recipe_at_instance)
        return attributes_serializer.data