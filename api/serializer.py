from rest_framework import serializers
from .models import Voice

class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'

class VoiceUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
