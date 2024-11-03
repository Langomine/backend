import datetime
import json
from pathlib import Path
import dateutil.parser
from dateutil.parser import ParserError
from django.core.files import File
import responses
from unittest.mock import patch, MagicMock

from api.models import Voice
from api.tests.test_setup import TestSetUp
from django.utils import timezone
from api.services.llm_analyser import ModelType

from langomine.settings import OPEN_AI_WHISPERER_HOST


class TestVoiceViews(TestSetUp):
    def setUp(self):
        super().setUp()
        self.mock_llm_response = {
            "fluency_and_coherence": {
                "band_score": 7.0,
                "strengths": ["Good flow"],
                "areas_for_improvement": ["Pausing"],
                "detailed_feedback": "Good overall fluency"
            },
            "overall_assessment": {
                "band_score": 6.5,
                "key_strengths": ["strength1"],
                "priority_improvements": ["improvement1"],
                "summary": "Good overall performance"
            },
            "model_used": "gpt-4o"  # Added this field to match actual response
        }

    def test_can_get_voice(self):
        voice = Voice(
            duration_s=30,
            file=File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb")),
        )

        voice.save()

        res = self.client.get(path=f"/api/voices/{voice.uuid}/", content_type='application/json')

        self.assertEqual(200, res.status_code)

        self.assertEqual(f"{voice.uuid}", res.data['uuid'])
        self.assertEqual(30, res.data['duration_s'])
        self.assertEqual(voice.text, res.data['text'])
        self.assertEqual(voice.language, res.data['language'])
        self.assertEqual(f"{res.data['created_at']}", res.data['created_at'])

    def test_can_not_get_deleted_voice(self):
        voice = Voice(
            duration_s=30,
            file=None,
            deleted_at=timezone.now(),
        )

        voice.save()

        res = self.client.get(path=f"/api/voices/{voice.uuid}/", content_type='application/json')

        self.assertEqual(404, res.status_code)

    @responses.activate
    @patch('api.services.llm_analyser.OpenAI')
    def test_can_submit_voice_with_country_and_analysis(self, mock_openai_class):
        # Setup LLM mock
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        # Set the content directly instead of function_call.arguments
        mock_choice.message.content = json.dumps(self.mock_llm_response)
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        # Mock Whisper response
        responses.add(
            method=responses.POST,
            url=OPEN_AI_WHISPERER_HOST + '/asr',
            json=json.loads('{"text": " Hi there!", "segments": [{"id": 0, "seek": 0, "start": 0.0, "end": 0.54, "text": " Hi there!", "tokens": [50364, 2421, 456, 0, 50414], "temperature": 0.0, "avg_logprob": -0.6894392967224121, "compression_ratio": 0.5294117647058824, "no_speech_prob": 0.08031938970088959, "words": [{"word": " Hi", "start": 0.0, "end": 0.32, "probability": 0.5562068223953247}, {"word": " there!", "start": 0.32, "end": 0.54, "probability": 0.9154007434844971}]}], "language": "en"}'),
            status=200
        )

        headers = {'HTTP_CF_IPCOUNTRY': 'FR'}
        res = self.client.post(
            path="/api/voices/",
            data={'file': File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb"))},
            **headers
        )

        voice = Voice.objects.first()

        self.assertEqual(201, res.status_code)
        self.assertEqual('FR', voice.request_country)
        self.assertEqual(self.mock_llm_response, voice.analysed)

        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], ModelType.GPT4O.value)

    def test_can_delete_voice(self):
        voice = Voice(
            duration_s=30,
            file=File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb")),
        )

        voice.save()

        res = self.client.delete(path=f"/api/voices/{voice.uuid}/")

        self.assertEqual(204, res.status_code)

        voice = Voice.objects.first()

        self.assertFalse(bool(voice.file))
        self.assertIsNotNone(voice.deleted_at)
        self.assertIsNone(voice.text)
        self.assertIsNone(voice.words)
