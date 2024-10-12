from rest_framework import serializers
from .models import Voice, Question


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'

class ProcessedVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = ['uuid', 'duration_s', 'text', 'file', 'language', 'created_at']

class VoiceUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class MainStatsSerializer(serializers.Serializer):
    # total_count = serializers.IntegerField()
    total_duration_s = serializers.IntegerField()

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'