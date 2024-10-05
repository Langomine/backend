import datetime

import requests
from django.db.models import Sum
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
from api.serializer import VoiceSerializer, VoiceUploadSerializer, VoiceCreatedSerializer, VoiceShowSerializer, \
    MainStatsSerializer
from rest_framework.decorators import action
from django.utils import timezone

class StatView(ViewSet):

    @swagger_auto_schema(
        method='get',
        tags=['Stat'],
        responses={
            status.HTTP_200_OK: openapi.Response('Main stats', MainStatsSerializer),
        },
    )
    @action(methods=['get'], detail=True)
    def show(self, request):
        stat = MainStatsSerializer(data={
            "total_duration_s": Voice.objects.filter(deleted_at__isnull=True).aggregate(Sum('duration_s'))['duration_s__sum'],
        })

        stat.is_valid(raise_exception=True)

        return Response(stat.data, status=status.HTTP_200_OK)
