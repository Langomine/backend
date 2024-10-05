import datetime

import requests
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.viewsets import ViewSet

from langomine.settings import OPEN_AI_WHISPERER_HOST
from api.models import Voice
from api.serializer import VoiceSerializer, VoiceUploadSerializer, VoiceCreatedSerializer, VoiceShowSerializer
from rest_framework.decorators import action
from django.utils import timezone

class VoiceView(ViewSet):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @swagger_auto_schema(
        method='get',
        tags=['Voice'],
        responses={
            200: VoiceSerializer,
            404: 'Voice not found',
        }
    )
    @action(methods=['get'], detail=True)
    def show(self, request, uuid):
        try:
            voice = Voice.objects.filter(deleted_at__isnull=True).get(pk=uuid)
            serializer = VoiceShowSerializer(voice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Voice.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        method='post',
        request_body=VoiceUploadSerializer,
        tags=['Voice'],
        responses={200: openapi.Response('response description', VoiceSerializer)}
    )
    @action(methods=['post'], detail=True)
    def store(self, request, format=None):
        whisper = requests.post(
            url=OPEN_AI_WHISPERER_HOST + '/asr',
            params={
                "encode": "true",
                "task": "transcribe",
                "word_timestamps": "true",
                "output": "json"
            },
            files={
                "audio_file": request.FILES['file']
            },
        ).json()

        voice = Voice(
            duration_s=(datetime.timedelta(seconds=whisper['segments'][0]['end']) - datetime.timedelta(seconds=whisper['segments'][0]['start'])).seconds,
            file=request.FILES['file'],
            language=whisper['language'],
            text=whisper['text'],
            words=whisper['segments'][0]['words'],
        )
        voice.save()
        return Response(VoiceCreatedSerializer(voice).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='delete',
        tags=['Voice'],
        responses={
            204: openapi.Response("No content"),
            404: 'Voice not found'
        }
    )
    @action(methods=['delete'], detail=True)
    def destroy(self, request, uuid):
        try:
            voice = Voice.objects.filter(deleted_at__isnull=True).get(pk=uuid)
            voice.file = None
            voice.deleted_at = timezone.now()
            voice.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Voice.DoesNotExist:
            raise Http404
