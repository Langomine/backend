import datetime

from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.viewsets import ViewSet

from .models import Voice
from .serializer import VoiceSerializer, VoiceUploadSerializer
from rest_framework.decorators import action
from django.utils import timezone

class VoiceView(ViewSet):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    """
    Retrieve, update or delete a voice instance.
    """

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
            serializer = VoiceSerializer(voice)
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
        voice = Voice(
            duration=datetime.timedelta(seconds=30),
            file=request.FILES['file'],
        )
        voice.save()
        return Response(VoiceSerializer(voice).data, status=status.HTTP_201_CREATED)

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




# @swagger_auto_schema(
#     method='post',
#     request_body=VoiceSerializer,
#     tags=['Voice'],
#     responses={200: openapi.Response('response description', VoiceSerializer)}
# )
#@action(detail=True, methods=['post'], parser_classes=(MultiPartParser, FileUploadParser))
