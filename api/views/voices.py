import datetime

import requests
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.viewsets import ViewSet

from api.services.llm_analyser import LlmAnalyser
from langomine.settings import OPEN_AI_WHISPERER_HOST
from api.models import Voice
from api.serializer import VoiceSerializer, VoiceUploadSerializer, ProcessedVoiceSerializer
from rest_framework.decorators import action
from django.utils import timezone

class VoiceView(ViewSet):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @extend_schema(
        tags=['Voice'],
        responses={
            200: ProcessedVoiceSerializer,
            404: OpenApiResponse(description='Not found')
        }
    )
    @action(methods=['get'], detail=True)
    def show(self, request, uuid):
        try:
            voice = Voice.objects.filter(deleted_at__isnull=True).get(pk=uuid)
            serializer = ProcessedVoiceSerializer(voice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Voice.DoesNotExist:
            raise Http404

    @extend_schema(
        request=VoiceUploadSerializer,
        tags=['Voice'],
        responses={200: ProcessedVoiceSerializer}
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

        country = request.headers.get('CF-IPCountry', '')

        analyser = LlmAnalyser(
            voice_content=whisper['segments'][0],
            country_code=country
        )

        analysed = analyser.analyze()

        voice = Voice(
            duration_s=(datetime.timedelta(seconds=whisper['segments'][0]['end']) - datetime.timedelta(seconds=whisper['segments'][0]['start'])).seconds,
            file=request.FILES['file'],
            language=whisper['language'],
            text=whisper['text'],
            words=whisper['segments'][0]['words'],
            request_country=country,
            analysed=analysed
        )
        voice.save()
        return Response(ProcessedVoiceSerializer(voice).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Voice'],
        responses={
            204: OpenApiResponse(description='Item deleted'),
            404: OpenApiResponse(description='Not found')
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
