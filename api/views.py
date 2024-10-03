import datetime

from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from rest_framework.response import Response
from rest_framework import status, views
from .models import Voice
from .serializer import VoiceSerializer, VoiceUploadSerializer
from rest_framework.decorators import action

class VoiceView(views.APIView):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    """
    Retrieve, update or delete a voice instance.
    """

    # def get_object(self, uuid):
    #     try:
    #         voice = Voice.objects.get(pk=uuid)
    #         return Response(VoiceSerializer(voice).data, status=status.HTTP_200_OK)
    #     except Voice.DoesNotExist:
    #         raise Http404

    # def get(self, request, pk, format=None):
    #     snippet = self.get_object(pk)
    #     serializer = SnippetSerializer(snippet)
    #     return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        request_body=VoiceUploadSerializer,
        tags=['Voice'],
        responses={200: openapi.Response('response description', VoiceSerializer)}
    )
    @action(methods=['post'], detail=True)
    def post(self, request, format=None):
        voice = Voice(
            duration=datetime.timedelta(seconds=30),
            file=request.FILES['file'],
        )
        voice.save()
        return Response(VoiceSerializer(voice).data, status=status.HTTP_201_CREATED)

    def delete(self, request, uuid, format=None):
        try:
            voice = Voice.objects.get(pk=uuid)
            voice.delete()
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
