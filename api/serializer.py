from rest_framework import serializers
from .models import Voice

class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'

class VoiceCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = ['uuid']

class VoiceShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = ['uuid', 'duration', 'text', 'file', 'language', 'created_at']

class VoiceUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
