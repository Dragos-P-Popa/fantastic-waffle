from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    story_cat = serializers.CharField(source='get_category_display')
    story_region = serializers.CharField(source='get_region_display')
    story_date = serializers.DateField(source='date')
    story_details = serializers.CharField(source='details')
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"

    class Meta:
        model = Article
        fields = ["key", "headline", "story_cat", "story_region", "author", "story_date", "story_details"]