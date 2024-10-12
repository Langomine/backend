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

from langomine.settings import OPEN_AI_WHISPERER_HOST
from api.models import Voice, Question
from api.serializer import VoiceSerializer, VoiceUploadSerializer, ProcessedVoiceSerializer, \
    QuestionSerializer
from rest_framework.decorators import action
from django.utils import timezone

class QuestionView(ViewSet):
    serializer_class = QuestionSerializer(many=True)

    @extend_schema(tags=['Question'])
    @action(methods=['get'], detail=True)
    def index(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
